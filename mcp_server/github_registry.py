"""
github_registry.py — SkillRegistry backed by GitHub instead of local filesystem.

Same interface as SkillRegistry (skill_registry.py) so server.py works identically
in both local and GitHub mode.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from .github_fetcher import GitHubFetcher, RemoteSkillFile


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except Exception:
        meta = {}
    body = content[match.end():].strip()
    return meta, body


class GitHubSkillEntry:
    """A skill loaded from GitHub. Same interface as SkillEntry."""

    def __init__(self, remote: RemoteSkillFile):
        self.remote = remote
        content = remote.content or ""
        meta, self._body = parse_frontmatter(content)

        # Path structure: "00-productivity-meta/token-saver/SKILL.md"
        parts = Path(remote.path).parts
        self.category = parts[0] if len(parts) >= 2 else "uncategorized"
        self.skill_folder = parts[1] if len(parts) >= 3 else parts[0]

        self.name = meta.get("name", self.skill_folder)
        self.description = meta.get("description", "No description.")
        self.compatibility = meta.get("compatibility", "")
        self.path = remote.path  # str, not Path (it's remote)

    @property
    def short_description(self) -> str:
        return self.description.split(".")[0].strip()

    def load_body(self) -> str:
        return self._body


class GitHubSkillRegistry:
    """
    Skill registry backed by a GitHub repository.
    Fetches all SKILL.md files on first access, then caches locally.
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
        self.source_label = f"github.com/{owner}/{repo}@{branch}"

        self._fetcher = GitHubFetcher(
            owner=owner,
            repo=repo,
            branch=branch,
            cache_dir=cache_dir,
            token=token,
        )
        self._skills: list[GitHubSkillEntry] = []
        self.reload()

    def reload(self) -> int:
        """Re-fetch from GitHub. Returns skill count."""
        remote_files = self._fetcher.fetch_all_skills(force_refresh=True)
        self._skills = []
        for rf in remote_files:
            try:
                self._skills.append(GitHubSkillEntry(rf))
            except Exception as e:
                print(f"[github-registry] Warning: could not parse {rf.path}: {e}")
        return len(self._skills)

    @property
    def skills(self) -> list[GitHubSkillEntry]:
        return self._skills

    def find_by_name(self, name: str) -> Optional[GitHubSkillEntry]:
        name_lower = name.lower().strip()
        for s in self._skills:
            if s.name.lower() == name_lower or s.skill_folder.lower() == name_lower:
                return s
        return None

    def search(self, query: str, max_results: int = 5) -> list[GitHubSkillEntry]:
        tokens = query.lower().split()
        scored = []
        for skill in self._skills:
            haystack = f"{skill.name} {skill.description} {skill.category}".lower()
            score = sum(1 for t in tokens if t in haystack)
            if score > 0:
                scored.append((score, skill))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:max_results]]

    def by_category(self) -> dict[str, list]:
        result: dict[str, list] = {}
        for skill in self._skills:
            result.setdefault(skill.category, []).append(skill)
        return result

    def summary_list(self) -> list[dict]:
        return [
            {
                "name": s.name,
                "category": s.category,
                "folder": s.skill_folder,
                "description": s.short_description,
                "compatibility": s.compatibility,
            }
            for s in self._skills
        ]
