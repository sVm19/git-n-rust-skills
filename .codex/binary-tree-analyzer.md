---
name: binary-tree-analyzer
description: Read and analyze the Stageira project (or any uploaded codebase) using a binary tree divide-and-conquer traversal strategy, reducing token consumption by 10-20x. Use this whenever the user uploads a project folder, says "understand this codebase", "map out architecture", "find where X happens", or needs to locate specific functionality. Also triggers for refactoring, debugging, or generating docs for the Stageira project. Always use this before doing a large multi-file refactor.
---


# Binary Tree Code Analyzer

Analyze large codebases efficiently by treating files as a binary tree: read the "root" pivot files first, then divide into left (core logic) and right (utilities) subtrees.

## Mental Model

```
                    [ROOT]
                   main.rs / lib.rs
                  /               \
          [LEFT - CORE]       [RIGHT - SUPPORT]
          models, services     utils, config
         /           \         /           \
      [LEAF]       [LEAF]   [LEAF]       [LEAF]
      tests        docs     locks      build artifacts
```

Read order: ROOT → LEFT → RIGHT → specific LEAFs only if needed.

## 5-Step Protocol

### Step 1 — Scan the Tree (never read content yet)

```bash
find . -type f -not -path "./.git/*" -not -path "./target/*" \
  -not -path "./__pycache__/*" \
  | sort | head -100
```

Build this metadata map for each file:
- Path, estimated size
- Role: `root | core | service | util | config | test`
- Priority: 0 (root) → 5 (test/skip)

### Step 2 — Identify Pivot Files

**For Stageira specifically:**

| Priority | Files | Read Order |
|----------|-------|-----------|
| 0 — Root | `Cargo.toml`, `src/main.rs`, `src/lib.rs` | First |
| 1 — Core | `scanner.py`, `objects.py`, `analytics.py` | Second |
| 2 — Services | `churn.py`, `bus_factor.py`, `exporter.py` | Third |
| 3 — Support | `config.py`, `run.sh`, `*.toml` | Fourth |
| 4 — Test | `tests/`, `test_*.py` | On demand |

### Step 3 — Read Left Subtree (Core Business Logic)

Read in order of decreasing file size. For each file, extract:

```
FILE: src/scanner.py
PURPOSE: Walks .git/objects/ using GitPython to extract commits
KEY_EXPORTS: scan_repo(), CommitRecord, DiffStat
KEY_IMPORTS: git, polars
FEEDS_INTO: analytics.py, exporter.py
```

Budget: max 500-800 tokens per file summary.

### Step 4 — Read Right Subtree (Only If Needed)

Read config/utils only if:
- They were imported by core files you already read
- The user's question is specifically about configuration
- File is < 100 lines (cheap to read)

Otherwise: note as "available on demand."

### Step 5 — Deliver the Tree + Answer

Output format:

```
CODEBASE MAP: stageira/
==========================================
[ROOT] Cargo.toml          → Deps: git2, polars 0.35, clap 4.4
[ROOT] src/main.rs          → CLI dispatcher: analyze | compare | export

[CORE] src/scanner.py       → Reads .git/ history → Vec<CommitRecord>
[CORE] src/analytics.py     → Polars transforms → MetricsReport

[SERVICE] src/churn.py      → Code churn: file edit frequency per window
[SERVICE] src/bus_factor.py → Ownership entropy score per file

[SUPPORT] src/exporter.py   → Writes JSON/CSV from MetricsReport
[SUPPORT] config/stageira.toml → Alert thresholds, feature flags

[LEAF] tests/               → Skipped (not relevant to question)
==========================================
CRITICAL PATH: main.rs → scanner.py → analytics.py → exporter.py
```

Then answer the user's specific question with file + line references.

## Token Budget for Stageira

| Phase | Tokens |
|-------|--------|
| Scan (file list) | 300 |
| Root files (2-3) | 1,500 |
| Core files (4-6) | 3,000 |
| Service files (2-4) | 1,500 |
| Tree summary | 800 |
| **Total** | **~7,100** |

vs. reading all files: ~60,000+ tokens

## Stageira-Specific Patterns to Note

- **Data flow**: `.git/` → `scanner.py` → Polars DataFrame → `analytics.py` → JSON/CSV
- **No network calls anywhere** — everything is offline-first
- **Skill boundary**: each folder in `git-n-rust-skills/` is an independent skill unit
- **Entry point is always `run.sh`** in each skill folder

## build_tree.py — Automated Scanner

```bash
# Run to get file importance map
python skill-creator/build_tree.py /path/to/project
```

Output: JSON array sorted by importance, with category and line count.
Reference implementation in `skill-creator/generate_skill.py`.
