"""
github_fetcher.py — Fetch all SKILL.md files from a public GitHub repo.

Strategy:
  1. One GitHub API call → get full file tree (ALL paths in repo)
  2. Filter for SKILL.md files
  3. Fetch each one via raw.githubusercontent.com (no rate limits, no auth)
  4. Cache locally so the server works offline after first fetch

Rate limits:
  - GitHub tree API: 60 req/hour unauthenticated (we only call it once)
  - raw.githubusercontent.com: no rate limit for public repos
  - With GITHUB_TOKEN env var: 5000 req/hour for API
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ── Config ───────────────────────────────────────────────────────────────────

GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
CACHE_TTL_SECONDS = 3600  # 1 hour — refresh skills from GitHub hourly


@dataclass
class RemoteSkillFile:
    path: str           # e.g. "00-productivity-meta/token-saver/SKILL.md"
    raw_url: str        # direct content URL
    sha: str            # GitHub blob SHA (for cache invalidation)
    content: Optional[str] = None


class GitHubFetcher:
    """
    Fetches SKILL.md files from a GitHub repository.

    Usage:
        fetcher = GitHubFetcher("alice", "git-n-rust-skills", cache_dir=Path(".cache"))
        files = fetcher.fetch_all_skills()
        # files is a list of RemoteSkillFile with .content populated
    """

    def __init__(
        self,
        owner: str,
        repo: str,
        branch: str = "main",
        cache_dir: Optional[Path] = None,
        token: Optional[str] = None,
    ):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.cache_dir = cache_dir or Path.home() / ".cache" / "stageira-skills"
        self.token = token or os.environ.get("GITHUB_TOKEN")

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._tree_cache_file = self.cache_dir / f"{owner}_{repo}_tree.json"

    # ── Public API ────────────────────────────────────────────────────────────

    def fetch_all_skills(self, force_refresh: bool = False) -> list[RemoteSkillFile]:
        """
        Return all SKILL.md files with content populated.
        Uses cache unless force_refresh=True or cache is stale.
        """
        skill_files = self._get_skill_paths(force_refresh)
        result = []
        for sf in skill_files:
            content = self._fetch_content(sf)
            if content:
                sf.content = content
                result.append(sf)
        print(f"[github-fetcher] Loaded {len(result)} skills from {self.owner}/{self.repo}")
        return result

    def invalidate_cache(self):
        """Force next fetch to pull fresh data from GitHub."""
        if self._tree_cache_file.exists():
            self._tree_cache_file.unlink()
        print("[github-fetcher] Cache invalidated.")

    # ── Tree fetching ─────────────────────────────────────────────────────────

    def _get_skill_paths(self, force: bool = False) -> list[RemoteSkillFile]:
        """Get list of SKILL.md paths from GitHub (cached)."""
        if not force and self._tree_is_fresh():
            return self._load_tree_cache()

        print(f"[github-fetcher] Fetching file tree from GitHub: {self.owner}/{self.repo}...")
        url = f"{GITHUB_API}/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"

        try:
            data = self._api_get(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(
                    f"Repo not found: {self.owner}/{self.repo}. "
                    "Make sure the repo is public and the branch is correct."
                )
            raise

        skill_files = []
        for item in data.get("tree", []):
            path = item.get("path", "")
            if path.endswith("SKILL.md") and item.get("type") == "blob":
                raw_url = f"{RAW_BASE}/{self.owner}/{self.repo}/{self.branch}/{path}"
                skill_files.append(RemoteSkillFile(
                    path=path,
                    raw_url=raw_url,
                    sha=item.get("sha", ""),
                ))

        self._save_tree_cache(skill_files)
        print(f"[github-fetcher] Found {len(skill_files)} SKILL.md files")
        return skill_files

    # ── Content fetching (raw.githubusercontent.com — no rate limit) ──────────

    def _fetch_content(self, sf: RemoteSkillFile) -> Optional[str]:
        """Fetch SKILL.md content. Uses per-file cache keyed by SHA."""
        cache_key = hashlib.md5(sf.sha.encode()).hexdigest()[:12]
        cache_file = self.cache_dir / f"skill_{cache_key}.md"

        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8")

        try:
            req = urllib.request.Request(
                sf.raw_url,
                headers={"User-Agent": "stageira-skills-mcp/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
            cache_file.write_text(content, encoding="utf-8")
            return content
        except Exception as e:
            print(f"[github-fetcher] Warning: could not fetch {sf.path}: {e}")
            return None

    # ── Cache helpers ─────────────────────────────────────────────────────────

    def _tree_is_fresh(self) -> bool:
        if not self._tree_cache_file.exists():
            return False
        age = time.time() - self._tree_cache_file.stat().st_mtime
        return age < CACHE_TTL_SECONDS

    def _save_tree_cache(self, skills: list[RemoteSkillFile]):
        data = {
            "fetched_at": time.time(),
            "owner": self.owner,
            "repo": self.repo,
            "branch": self.branch,
            "skills": [
                {"path": s.path, "raw_url": s.raw_url, "sha": s.sha}
                for s in skills
            ],
        }
        self._tree_cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_tree_cache(self) -> list[RemoteSkillFile]:
        data = json.loads(self._tree_cache_file.read_text(encoding="utf-8"))
        return [
            RemoteSkillFile(path=s["path"], raw_url=s["raw_url"], sha=s["sha"])
            for s in data["skills"]
        ]

    # ── HTTP helper with optional auth ────────────────────────────────────────

    def _api_get(self, url: str) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "stageira-skills-mcp/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
