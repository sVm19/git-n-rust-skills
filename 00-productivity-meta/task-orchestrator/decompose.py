#!/usr/bin/env python3
"""
decompose.py — Generates a structured task breakdown file from a requirement.

Usage:
    python decompose.py "Add temporal coupling to analyze command"
    python decompose.py --req-file requirement.txt --out tasks.md

Output: A markdown file with the Requirement Autopsy + Task List template
pre-filled with project context from the git-n-rust-skills directory.
The AI agent then fills in the blanks.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

THIS_DIR = Path(__file__).parent
PROJECT_ROOT = THIS_DIR.parent.parent  # c:\rust-git-skills\

TEMPLATE = """\
# Task Decomposition: {title}

> Generated: {timestamp}
> Source requirement: {req_source}

---

## Requirement

```
{requirement}
```

---

## Phase 1 — Requirement Autopsy

> ⚠️ Complete this FULLY before writing any task.

**What is explicitly stated:**
- [ ] 
- [ ] 

**What is implied but not stated:**
- [ ] 
- [ ] 

**What is unknown / needs to be looked up:**
- [ ] 
- [ ] 

**Files that will be touched (verify these exist first):**
{file_suggestions}

**Files that must NOT be touched:**
- [ ] 

**Definition of done:**
- [ ] 

**Hallucination risks:**
- [ ] Agent might invent a function that doesn't exist in ___
- [ ] Agent might assume a module is imported when it isn't

---

## Phase 2 — Task List

**Total tasks:** N  
**Ordered by:** data flow dependency

| # | Task | Type | Output | Depends On |
|---|------|------|--------|-----------|
| 1 | Read & map existing code | discover | API signatures | — |
| 2 | | implement | | Task 1 |
| 3 | | implement | | Task 2 |
| 4 | | test | | Task 3 |
| 5 | End-to-end verification | verify | | Task 4 |

---

## Phase 3 — Agent Task Prompts

{task_prompts}

---

## Sequencing Checklist

- [ ] Task 1 is read-only (no writes)
- [ ] Each task has exactly one output
- [ ] No task references a function not verified in a prior task
- [ ] Every task has a `VERIFY SUCCESS BY` step
- [ ] `DO NOT` section covers the most likely hallucination
- [ ] Final task is a full end-to-end verification
"""

TASK_PROMPT_TEMPLATE = """\
### Task {n} of N: <Title>

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT TASK [{n} of N]: <Task Title>

CONTEXT (read these first):
  - <file path> — <why>

WHAT YOU KNOW FOR CERTAIN:
  - <fact from codebase>

YOUR ONE JOB:
  <single precise action>

EXACT EXPECTED OUTPUT:
  - File: <path>
  - Change: <what changes>

DO NOT:
  - Do not create files not listed above
  - Do not call unverified functions
  - Do not modify <protected file>

VERIFY SUCCESS BY:
  1. <run this command>
  2. <check this output>

HAND OFF TO TASK [{next_n}]:
  Produce: <what next task needs>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

"""

SKILL_FILE_DIRS = [
    "01-core-systems",
    "02-analytics-engineering",
    "03-cli-devx",
    "04-system-integration",
    "05-performance",
]


def find_relevant_files(requirement: str) -> list[str]:
    """Heuristic: find SKILL.md and src/*.py files related to keywords."""
    keywords = requirement.lower().split()
    matches = []

    for pattern in ["**/*.py", "**/SKILL.md"]:
        for f in PROJECT_ROOT.glob(pattern):
            if any(k in f.name.lower() or k in str(f.parent).lower() for k in keywords):
                try:
                    rel = f.relative_to(PROJECT_ROOT)
                    matches.append(str(rel))
                except ValueError:
                    pass

    # Always include the most relevant core files
    always_include = [
        "01-core-systems/git-internals-master/src/scanner.py",
        "01-core-systems/data-processing-polars/src/analytics.py",
    ]
    for f in always_include:
        if f not in matches and (PROJECT_ROOT / f).exists():
            matches.append(f)

    return matches[:10]  # cap to avoid overwhelming


def build_task_prompts(n_tasks: int = 5) -> str:
    prompts = []
    for i in range(1, n_tasks + 1):
        next_n = i + 1 if i < n_tasks else "END"
        prompts.append(TASK_PROMPT_TEMPLATE.format(n=i, next_n=next_n))
    return "\n".join(prompts)


def main():
    parser = argparse.ArgumentParser(description="Decompose a requirement into agent tasks")
    parser.add_argument("requirement", nargs="?", help="Requirement text")
    parser.add_argument("--req-file", help="Read requirement from file")
    parser.add_argument("--out", help="Output markdown file (default: stdout)")
    parser.add_argument("--tasks", type=int, default=5, help="Number of task slots to create")
    args = parser.parse_args()

    # Read requirement
    if args.req_file:
        requirement = Path(args.req_file).read_text(encoding="utf-8").strip()
        req_source = args.req_file
    elif args.requirement:
        requirement = args.requirement.strip()
        req_source = "command line"
    else:
        print("Usage: python decompose.py 'your requirement here'")
        sys.exit(1)

    # Generate title
    title = requirement[:80] + ("..." if len(requirement) > 80 else "")

    # Find relevant files
    relevant = find_relevant_files(requirement)
    file_suggestions = "\n".join(f"- [ ] `{f}`" for f in relevant) or "- [ ] (identify manually)"

    # Build content
    content = TEMPLATE.format(
        title=title,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        req_source=req_source,
        requirement=requirement,
        file_suggestions=file_suggestions,
        task_prompts=build_task_prompts(args.tasks),
    )

    # Output
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(content, encoding="utf-8")
        print(f"✅ Task breakdown written to: {out_path}")
    else:
        print(content)


if __name__ == "__main__":
    main()
