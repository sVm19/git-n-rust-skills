"""
objects.py — Git object dataclasses for Stageira.

Mirrors git's internal object model: blob, tree, commit.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class BlobObject:
    """A file at a specific revision (content-addressed by SHA)."""
    sha: str
    path: str
    size_bytes: int
    content: Optional[bytes] = None  # Only loaded on demand


@dataclass
class TreeObject:
    """A directory snapshot at a specific revision."""
    sha: str
    entries: list[BlobObject] = field(default_factory=list)


@dataclass
class CommitObject:
    """A commit with all metadata and associated tree."""
    sha: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    timestamp: datetime
    message: str
    parent_shas: list[str] = field(default_factory=list)
    tree: Optional[TreeObject] = None


@dataclass
class TagObject:
    """An annotated tag."""
    sha: str
    name: str
    target_sha: str
    message: str
    tagger_name: str
    timestamp: datetime
