---
name: git-internals-master
description: Master skill for reading .git/ directory structure, walking commit graphs, extracting blobs/trees/diffs using libgit2 / git2-rs. Use whenever working on Stageira's core engine: parsing commits, extracting author data, walking history, reading file diffs from the .git/objects/ folder. Triggers on \"read commits\", \"parse .git\", \"walk history\", \"extract diffs\", \"libgit2\", \"git2-rs\", or any work in the scanner.py / objects.rs / src/ core.
---


# Git Internals Master

The core of Stageira. This skill covers everything needed to replace the GitHub API with direct `.git/` directory parsing — the foundational capability that makes Stageira offline-first.

## Why This Matters

Every git repo has a `.git/` folder. It contains 100% of the history. No GitHub API needed.

```
.git/
├── objects/   ← All commits, trees, blobs (content-addressed by SHA)
├── refs/      ← Branch and tag pointers → SHA lookups
├── logs/      ← Reflog: who moved what ref when
├── COMMIT_EDITMSG
└── HEAD       ← Current branch pointer
```

## Key Data Types

| Git Object | What It Is | Stageira Use |
|-----------|-----------|-------------|
| **Blob** | File content at a point in time | File diffs, churn |
| **Tree** | Directory snapshot | File path resolution |
| **Commit** | Pointer to tree + metadata | Author, timestamp, message |
| **Tag** | Named pointer to commit | Release boundary detection |

## git2-rs Patterns (Rust)

### Open a repository

```rust
use git2::Repository;

let repo = Repository::open("/path/to/repo")?;
```

### Walk commit history

```rust
let mut revwalk = repo.revwalk()?;
revwalk.push_head()?;
revwalk.set_sorting(git2::Sort::TIME)?;

for oid in revwalk {
    let oid = oid?;
    let commit = repo.find_commit(oid)?;
    let author = commit.author();
    let timestamp = commit.time().seconds();
    // process...
}
```

### Extract file diffs from a commit

```rust
fn get_diff_stats(repo: &Repository, commit: &git2::Commit) -> Result<Vec<DiffStat>> {
    let tree = commit.tree()?;
    let parent_tree = commit.parent(0).ok().and_then(|p| p.tree().ok());

    let diff = repo.diff_tree_to_tree(
        parent_tree.as_ref(),
        Some(&tree),
        None,
    )?;

    let stats = diff.stats()?;
    // files_changed, insertions, deletions
}
```

## GitPython Patterns (Python analytics layer)

### Open and walk commits

```python
import git

repo = git.Repo("/path/to/repo")
for commit in repo.iter_commits("HEAD", max_count=1000):
    author = commit.author.name
    timestamp = commit.committed_datetime
    files = list(commit.stats.files.keys())
```

### Extract per-file stats

```python
for commit in repo.iter_commits():
    for filename, stat in commit.stats.files.items():
        insertions = stat["insertions"]
        deletions = stat["deletions"]
        lines = stat["lines"]
```

## Implementation Files

- `src/scanner.py` — entry point, opens repo, yields `CommitRecord` objects
- `src/objects.py` — dataclasses for Blob, Tree, Commit, DiffStat
- `src/exporter.py` — converts records to JSON/CSV

## CommitRecord Schema

```python
@dataclass
class CommitRecord:
    sha: str
    author_name: str
    author_email: str
    timestamp: datetime
    files_changed: list[str]
    insertions: int
    deletions: int
    message: str
```

## Performance Notes

- For repos with 100K+ commits: use `--first-parent` traversal to skip merge commits
- Batch commits into chunks of 1,000 before writing to Polars DataFrame
- Cache file path → SHA mappings to avoid re-walking trees

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `git2::Error: repository not found` | Bad path | Check `.git/` exists |
| `BorrowError` on commit parent | Root commit has no parent | Guard with `commit.parent_count() > 0` |
| Slow on large repos | Reading every tree | Use `--diff-filter` to skip unmodified files |

## Quick Start

```bash
cd 01-core-systems/git-internals-master
pip install -r requirements.txt
./run.sh analyze /path/to/your/repo
```
