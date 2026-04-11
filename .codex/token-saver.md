---
name: token-saver
description: Slash token usage by 10-20x when analyzing, summarizing, or navigating the Stageira codebase. Use this skill immediately whenever the user asks to "understand the codebase", "read this project", "what does X do", "map the architecture", "find where Y is implemented", or before any large-scale refactor or feature addition. Also use proactively when you're about to read more than 5 files in a row — stop, use this skill first.
---


# Token Saver — Efficient Codebase Navigation

Reading files blindly burns tokens. This skill gives you a systematic protocol to understand 95% of a codebase by reading ≤15% of it.

## Core Rule

**Never read files linearly.** Always build a map first, then read strategically.

## The 4-Step Protocol

### Step 1: Scan (30 seconds, ~200 tokens)

Run a structural scan without reading any file content:

```bash
find . -type f \( -name "*.rs" -o -name "*.py" -o -name "*.toml" -o -name "*.sh" \) \
  | grep -v target | grep -v __pycache__ | grep -v ".git" \
  | sort
```

### Step 2: Classify Files by Role

Before reading, assign each file to a tier:

| Tier | Read When | Examples |
|------|-----------|---------|
| **ROOT** (always) | Immediately | `main.rs`, `lib.rs`, `Cargo.toml`, `SKILL.md` |
| **CORE** (read next) | After root | `scanner.py`, `analytics.py`, `objects.rs` |
| **SUPPORT** (conditional) | If needed | `exporter.py`, `config.py`, `run.sh` |
| **LEAF** (skip) | Almost never | `tests/`, `docs/`, lock files |

### Step 3: Build the Summary Tree

After reading ROOT + CORE files, produce a map like:

```
stageira/
├── [ROOT] src/main.rs          → CLI entry, dispatches subcommands
├── [CORE] src/scanner.py       → Walks .git/ with GitPython
├── [CORE] src/analytics.py     → Computes churn, bus factor via Polars
├── [SUPPORT] src/exporter.py   → JSON/CSV serialization
└── [LEAF] tests/               → unit tests (skip unless debugging)
```

### Step 4: Answer from the Map

- Point to specific files + line numbers
- Never quote entire functions — summarize in 1-2 sentences
- Offer: "Want me to dive deeper into [module]?"

## Token Budget Targets

| Phase | Goal | Budget |
|-------|------|--------|
| Scan | File list only | 200 tokens |
| Root files | Entry points | 1,000 tokens |
| Core files | Business logic | 3,000 tokens |
| Summary | Connect the dots | 1,000 tokens |
| **Total** | | **~5,200 tokens** |

vs. reading 20 files verbatim: ~50,000 tokens

## Compression Rules

1. **Summarize, never quote** — "scanner.py reads commits via `git2::Repository::open()`" not 50 lines of code
2. **Point, don't paste** — "bus_factor.py line 42" not the whole function
3. **Skip boilerplate** — imports, type aliases, docstrings with no logic
4. **Batch similar files** — "churn.py and temporal_coupling.py both use the same Polars groupby pattern"
5. **Stop when you have enough** — if you can answer the question, stop reading

## Stageira-Specific Entry Points

Always start with these for the Stageira project:

1. `Cargo.toml` — dependency map and feature flags
2. `src/main.rs` or `src/lib.rs` — CLI structure
3. The SKILL.md of the relevant module
4. `run.sh` — how to execute

## When to Break This Rule

- User explicitly says "show me the full file"
- Debugging a subtle bug that needs exact code
- Reviewing a PR (intentionally reading everything)
