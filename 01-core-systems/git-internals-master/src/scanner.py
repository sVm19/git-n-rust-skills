"""
scanner.py — Core git repo scanner for Stageira.

Reads .git/ directly using GitPython (Python layer over libgit2).
No network calls. Works completely offline.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator

import git


@dataclass
class DiffStat:
    insertions: int
    deletions: int
    files_changed: list[str] = field(default_factory=list)


@dataclass
class CommitRecord:
    sha: str
    author_name: str
    author_email: str
    timestamp: datetime
    message: str
    files_changed: list[str]
    insertions: int
    deletions: int


def scan_repo(repo_path: str, max_commits: int = 100_000) -> list[CommitRecord]:
    """
    Walk the commit history of a git repository.
    
    Args:
        repo_path: Absolute path to the git repository root.
        max_commits: Maximum number of commits to scan. Default 100k.
    
    Returns:
        List of CommitRecord objects, newest first.
    
    Raises:
        git.exc.InvalidGitRepositoryError: If path is not a git repo.
        git.exc.NoSuchPathError: If path does not exist.
    """
    repo = git.Repo(repo_path)
    records: list[CommitRecord] = []

    for commit in repo.iter_commits("HEAD", max_count=max_commits):
        # Skip commits with no parent (root commit has no diff)
        if commit.parents:
            files = list(commit.stats.files.keys())
            total = commit.stats.total
            insertions = total.get("insertions", 0)
            deletions = total.get("deletions", 0)
        else:
            files = []
            insertions = 0
            deletions = 0

        records.append(CommitRecord(
            sha=commit.hexsha,
            author_name=commit.author.name or "",
            author_email=commit.author.email or "",
            timestamp=datetime.fromtimestamp(commit.committed_date),
            message=commit.message.strip()[:200],
            files_changed=files,
            insertions=insertions,
            deletions=deletions,
        ))

    return records


def iter_commits(repo_path: str, max_commits: int = 100_000) -> Iterator[CommitRecord]:
    """Generator version of scan_repo for streaming / memory-efficient use."""
    repo = git.Repo(repo_path)
    
    for commit in repo.iter_commits("HEAD", max_count=max_commits):
        if commit.parents:
            files = list(commit.stats.files.keys())
            total = commit.stats.total
        else:
            files = []
            total = {"insertions": 0, "deletions": 0}

        yield CommitRecord(
            sha=commit.hexsha,
            author_name=commit.author.name or "",
            author_email=commit.author.email or "",
            timestamp=datetime.fromtimestamp(commit.committed_date),
            message=commit.message.strip()[:200],
            files_changed=files,
            insertions=total.get("insertions", 0),
            deletions=total.get("deletions", 0),
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <repo-path>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Scanning: {path}")
    records = scan_repo(path, max_commits=1000)
    print(f"Found {len(records)} commits")
    if records:
        r = records[0]
        print(f"Latest: {r.sha[:8]} by {r.author_name} on {r.timestamp.date()}")
