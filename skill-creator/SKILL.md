---
name: skill-creator
description: Create, scaffold, and improve skill files for the Stageira git analytics project. Use this skill whenever the user wants to add a new skill, generate boilerplate for a skill folder, write a SKILL.md, create a run.sh, requirements.txt, or src/ file for any module in git-n-rust-skills/. Also triggers when the user says "create skill", "scaffold skill", "new skill for X", or "add skill file".
---

# Skill Creator — Stageira Edition

Use this skill to create new skills for the Stageira project, covering everything from Git internals to Go-To-Market templates.

## Skill Anatomy

Every skill lives in a folder with this structure:

```
<category>/<skill-name>/
├── SKILL.md          ← Required. YAML frontmatter + instructions
├── run.sh            ← Universal entry point (bash)
├── requirements.txt  ← Python deps (if Python skill)
├── setup.py          ← Package setup (if distributable)
├── src/
│   ├── __init__.py
│   └── *.py          ← Implementation files
├── tests/
│   └── test_*.py
└── docs/
    └── QUICK_START.md
```

## SKILL.md Template

```markdown
---
name: <skill-id>
description: <one-line trigger description — when to use + what it does>
compatibility: Python 3.10+, Rust 1.75+ (only if relevant)
---

# <Skill Title>

Brief description of what this skill does and why it matters for Stageira.

## When to Use

- Trigger phrases or contexts
- Example user requests

## Quick Start

```bash
./run.sh <command> [options]
```

## Core Concepts

Key ideas this skill implements.

## Implementation Steps

1. Step one
2. Step two
3. Step three

## Output Format

What the skill produces (JSON schema, file paths, etc.)

## Error Handling

Common errors and how to fix them.
```

## Category Map

| Folder | Domain |
|--------|--------|
| `00-productivity-meta/` | AI dev workflow speedups |
| `01-core-systems/` | Git + Rust + Polars foundation |
| `02-analytics-engineering/` | Metrics algorithms |
| `03-cli-devx/` | CLI UX + config |
| `04-system-integration/` | CI/CD + file export |
| `05-performance/` | Speed + memory |
| `06-enterprise-security/` | Offline-first + compliance |
| `07-testing-reliability/` | Tests + fuzzing |
| `08-devops-release/` | Publishing + distribution |
| `09-product-monetization/` | Pricing + tiers |
| `10-go-to-market/` | Marketing + outreach |
| `11-project-management/` | GitHub Issues + workflow |

## Skill Creation Checklist

- [ ] SKILL.md with frontmatter + body
- [ ] run.sh entry point (executable)
- [ ] requirements.txt (pin versions)
- [ ] src/__init__.py
- [ ] At least one implementation file in src/
- [ ] tests/test_<skill>.py skeleton
- [ ] docs/QUICK_START.md
