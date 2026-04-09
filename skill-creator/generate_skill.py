#!/usr/bin/env python3
"""
generate_skill.py — Bootstrap a new Stageira skill folder from a template.

Usage:
    python generate_skill.py <category-number> <skill-name>

Examples:
    python generate_skill.py 01-core-systems rust-ownership
    python generate_skill.py 03-cli-devx output-formatter
"""

import os
import sys
import textwrap
from pathlib import Path

CATEGORIES = {
    "00": "00-productivity-meta",
    "01": "01-core-systems",
    "02": "02-analytics-engineering",
    "03": "03-cli-devx",
    "04": "04-system-integration",
    "05": "05-performance",
    "06": "06-enterprise-security",
    "07": "07-testing-reliability",
    "08": "08-devops-release",
    "09": "09-product-monetization",
    "10": "10-go-to-market",
    "11": "11-project-management",
}

SKILL_MD_TEMPLATE = """\
---
name: {skill_name}
description: {skill_name} skill for Stageira. Use when working on {skill_name_human} functionality. Triggers on phrases like "{trigger_phrase}".
---

# {skill_name_title}

<!-- TODO: brief description of what this skill does and why it matters for Stageira -->

## When to Use

- <!-- example trigger scenario -->
- <!-- example user phrase -->

## Quick Start

```bash
./run.sh help
```

## Core Concepts

<!-- Key ideas this skill implements -->

## Implementation Steps

1. <!-- Step one -->
2. <!-- Step two -->
3. <!-- Step three -->

## Output Format

<!-- What the skill produces: JSON schema, CSV, CLI output, etc. -->

## Error Handling

<!-- Common errors and how to handle them -->
"""

RUN_SH_TEMPLATE = """\
#!/usr/bin/env bash
# run.sh — Entry point for {skill_name}
# Usage: ./run.sh <command> [options]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
SRC="$SCRIPT_DIR/src"

case "${{1:-help}}" in
  analyze)
    python "$SRC/main.py" analyze "${{@:2}}"
    ;;
  help|--help|-h)
    echo "Usage: ./run.sh [analyze|help]"
    ;;
  *)
    echo "Unknown command: $1"
    exit 1
    ;;
esac
"""

REQUIREMENTS_TEMPLATE = """\
# {skill_name} dependencies
# Pin versions for reproducibility
polars>=0.20.0
gitpython>=3.1.40
typer>=0.9.0
rich>=13.0.0
pydantic>=2.0.0
"""

INIT_TEMPLATE = '"""Stageira skill: {skill_name_human}."""\n'

MAIN_TEMPLATE = """\
"""
# {skill_name_human} — core implementation
# Part of the Stageira git analytics project

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def analyze(repo: str = typer.Argument(..., help="Path to git repository")):
    \"\"\"Analyze the git repository.\"\"\"
    console.print(f"[bold green]Analyzing[/bold green]: {{repo}}")
    # TODO: implement


if __name__ == "__main__":
    app()
"""

TEST_TEMPLATE = """\
\"\"\"Tests for {skill_name_human}.\"\"\"
import pytest


class Test{skill_name_title_camel}:
    def test_placeholder(self):
        # TODO: write real tests
        assert True
"""

QUICK_START_TEMPLATE = """\
# Quick Start — {skill_name_title}

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
./run.sh analyze /path/to/your/repo
```

## Output

<!-- describe output here -->
"""


def to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def to_camel(slug: str) -> str:
    return "".join(word.capitalize() for word in slug.split("-"))


def create_skill(category_dir: str, skill_name: str, base_dir: Path):
    skill_root = base_dir / category_dir / skill_name
    dirs = [
        skill_root,
        skill_root / "src",
        skill_root / "tests",
        skill_root / "docs",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    human = skill_name.replace("-", " ")
    title = to_title(skill_name)
    camel = to_camel(skill_name)
    trigger = f"{human.lower()}, {skill_name} analysis"

    files = {
        skill_root / "SKILL.md": SKILL_MD_TEMPLATE.format(
            skill_name=skill_name,
            skill_name_human=human,
            skill_name_title=title,
            trigger_phrase=trigger,
        ),
        skill_root / "run.sh": RUN_SH_TEMPLATE.format(skill_name=skill_name),
        skill_root / "requirements.txt": REQUIREMENTS_TEMPLATE.format(skill_name=skill_name),
        skill_root / "src" / "__init__.py": INIT_TEMPLATE.format(skill_name_human=human),
        skill_root / "src" / "main.py": MAIN_TEMPLATE.format(skill_name_human=human),
        skill_root / "tests" / f"test_{skill_name.replace('-','_')}.py": TEST_TEMPLATE.format(
            skill_name_human=human,
            skill_name_title_camel=camel,
        ),
        skill_root / "docs" / "QUICK_START.md": QUICK_START_TEMPLATE.format(
            skill_name_title=title
        ),
    }

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        print(f"  Created: {path.relative_to(base_dir)}")

    # Make run.sh executable on Unix
    (skill_root / "run.sh").chmod(0o755)

    print(f"\n✅ Skill '{skill_name}' created in {skill_root.relative_to(base_dir)}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    category_input = sys.argv[1]
    skill_name = sys.argv[2]

    # Accept both "01" and "01-core-systems"
    category_key = category_input.split("-")[0].zfill(2)
    if category_key in CATEGORIES:
        category_dir = CATEGORIES[category_key]
    elif category_input in CATEGORIES.values():
        category_dir = category_input
    else:
        print(f"Unknown category: {category_input}")
        print("Available:", list(CATEGORIES.values()))
        sys.exit(1)

    base_dir = Path(__file__).parent.parent
    create_skill(category_dir, skill_name, base_dir)


if __name__ == "__main__":
    main()
