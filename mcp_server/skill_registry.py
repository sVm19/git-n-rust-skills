"""
skill_registry.py — Scans all SKILL.md files in the git-n-rust-skills tree.

Parses YAML frontmatter (name, description, compatibility) and indexes them
so the MCP server can expose them to Claude instantly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class SkillEntry:
    name: str
    description: str
    category: str          # e.g. "01-core-systems"
    skill_folder: str      # e.g. "git-internals-master"
    path: Path             # absolute path to SKILL.md
    compatibility: str = ""
    body: Optional[str] = None   # loaded on demand

    @property
    def short_description(self) -> str:
        """First sentence of description — used in list_skills()."""
        return self.description.split(".")[0].strip()

    def load_body(self) -> str:
        """Read the full SKILL.md content (lazy)."""
        if self.body is None:
            self.body = self.path.read_text(encoding="utf-8")
        return self.body


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a SKILL.md file."""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content
    meta = yaml.safe_load(match.group(1)) or {}
    body = content[match.end():].strip()
    return meta, body


def scan_skills(root: Path) -> list[SkillEntry]:
    """
    Walk root directory tree and collect all SKILL.md files.

    Expects structure:
        <root>/<NN-category>/<skill-name>/SKILL.md
    """
    skills: list[SkillEntry] = []

    for skill_md in sorted(root.rglob("SKILL.md")):
        try:
            content = skill_md.read_text(encoding="utf-8")
            meta, _body = parse_frontmatter(content)

            # Derive category + skill_folder from path
            rel = skill_md.relative_to(root)
            parts = rel.parts  # e.g. ('01-core-systems', 'git-internals-master', 'SKILL.md')

            category = parts[0] if len(parts) >= 2 else "uncategorized"
            skill_folder = parts[1] if len(parts) >= 3 else parts[0]

            name = meta.get("name", skill_folder)
            description = meta.get("description", "No description available.")
            compatibility = meta.get("compatibility", "")

            skills.append(SkillEntry(
                name=name,
                description=description,
                category=category,
                skill_folder=skill_folder,
                path=skill_md,
                compatibility=compatibility,
            ))
        except Exception as e:
            # Never crash the server due to a malformed SKILL.md
            print(f"[skill-registry] Warning: could not parse {skill_md}: {e}")

    return skills


class SkillRegistry:
    """In-memory index of all skills. Thread-safe for reads."""

    def __init__(self, root: Path):
        self.root = root
        self._skills: list[SkillEntry] = []
        self.reload()

    def reload(self) -> int:
        """Rescan the directory tree. Returns count of skills found."""
        self._skills = scan_skills(self.root)
        return len(self._skills)

    @property
    def skills(self) -> list[SkillEntry]:
        return self._skills

    def find_by_name(self, name: str) -> Optional[SkillEntry]:
        """Case-insensitive lookup by skill name."""
        name_lower = name.lower().strip()
        for s in self._skills:
            if s.name.lower() == name_lower or s.skill_folder.lower() == name_lower:
                return s
        return None

    def search(self, query: str, max_results: int = 5) -> list[SkillEntry]:
        """Keyword search across name + description. Returns ranked results."""
        query_lower = query.lower()
        tokens = query_lower.split()

        scored: list[tuple[int, SkillEntry]] = []
        for skill in self._skills:
            haystack = f"{skill.name} {skill.description} {skill.category}".lower()
            score = sum(1 for t in tokens if t in haystack)
            if score > 0:
                scored.append((score, skill))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:max_results]]

    def by_category(self) -> dict[str, list[SkillEntry]]:
        """Group skills by category folder."""
        result: dict[str, list[SkillEntry]] = {}
        for skill in self._skills:
            result.setdefault(skill.category, []).append(skill)
        return result

    def summary_list(self) -> list[dict]:
        """Compact list for list_skills() tool — name + short description + category."""
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
