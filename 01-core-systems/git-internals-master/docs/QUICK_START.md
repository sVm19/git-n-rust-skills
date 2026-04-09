# Quick Start — Git Internals Master

The core Stageira engine. Reads `.git/` history without any network access.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
# Scan a local git repo
./run.sh analyze /path/to/your/repo

# Output: lists commit count and latest commit
```

## What it does

1. Opens `.git/` using GitPython (libgit2 bindings)
2. Walks commit history from HEAD
3. Extracts per-commit: SHA, author, timestamp, file diffs
4. Returns `list[CommitRecord]` for analytics layer

## Import in your code

```python
from src.scanner import scan_repo

records = scan_repo("/path/to/repo", max_commits=10_000)
print(f"Found {len(records)} commits")
print(f"Authors: {set(r.author_name for r in records)}")
```

## Feed to Polars

```python
import polars as pl

df = pl.DataFrame([r.__dict__ for r in records])
```

## Warnings

- `max_commits=100_000` is the safe default for < 2s performance
- Root commits (no parents) have `files_changed=[]` — this is expected
- Binary files appear in `files_changed` but insertions/deletions may be 0
