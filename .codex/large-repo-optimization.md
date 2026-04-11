---
name: large-repo-optimization
description: Optimize Stageira's performance on massive git repos (100K+ commits, monorepos). Use when analyzing slow repositories, implementing parallel commit walking, lazy loading, streaming DataFrames, or hitting memory limits. Triggers on "large repo", "slow analysis", "monorepo", "100k commits", "out of memory", "parallel processing", "lazy loading", or "streaming".
---


# Large Repo Optimization

Stageira's target market includes monorepos with millions of commits. This skill covers the techniques to handle them without running out of memory or taking hours.

## Three Strategies

| Strategy | Best For | Trade-off |
|----------|----------|-----------|
| **Parallel processing** | CPU-bound commit parsing | Complexity, GIL issues |
| **Lazy loading** | Low-memory environments | Slower first access |
| **Streaming** | Extremely large outputs | Sequential only |

## Parallel Processing

```python
# src/parallel_processing.py
from multiprocessing import Pool, cpu_count
from git import Repo
import polars as pl

def process_chunk(args):
    """Worker: process a chunk of commit SHAs."""
    repo_path, sha_chunk = args
    repo = Repo(repo_path)  # open per-process (not picklable)
    
    records = []
    for sha in sha_chunk:
        commit = repo.commit(sha)
        records.append({
            "sha": sha,
            "author": commit.author.name,
            "timestamp": commit.committed_date,
            "insertions": commit.stats.total["insertions"],
            "deletions": commit.stats.total["deletions"],
        })
    return records

def parallel_scan(repo_path: str, max_commits: int = 100_000) -> pl.DataFrame:
    repo = Repo(repo_path)
    
    # Get all SHAs first (cheap)
    all_shas = [c.hexsha for c in repo.iter_commits("HEAD", max_count=max_commits)]
    
    # Split into chunks
    n_workers = max(1, cpu_count() - 1)
    chunk_size = max(100, len(all_shas) // n_workers)
    chunks = [all_shas[i:i+chunk_size] for i in range(0, len(all_shas), chunk_size)]
    
    # Process in parallel
    with Pool(n_workers) as pool:
        results = pool.map(process_chunk, [(repo_path, chunk) for chunk in chunks])
    
    # Flatten and build DataFrame
    all_records = [r for chunk in results for r in chunk]
    return pl.DataFrame(all_records)
```

## Lazy Loading (Polars LazyFrame)

```python
# src/lazy_loading.py
import polars as pl

def lazy_analyze(csv_path: str, window_days: int = 30) -> pl.DataFrame:
    """
    Scan a pre-exported CSV lazily — only materializes what's needed.
    Best for repeated analysis on the same large repo.
    """
    cutoff = pl.lit(window_days).cast(pl.Int32)
    
    return (
        pl.scan_csv(csv_path)
        .filter(
            pl.col("timestamp") >= pl.lit("2024-01-01")  # filter before load
        )
        .group_by("author")
        .agg(pl.len().alias("commits"))
        .sort("commits", descending=True)
        .collect()  # materializes here only
    )
```

## Streaming (for huge DataFrames)

```python
# src/streaming.py
import polars as pl

def stream_to_csv(repo_path: str, output_path: str, chunk_size: int = 5000):
    """
    Write commits to CSV in chunks — never holds all in memory at once.
    For repos with 500K+ commits.
    """
    from git import Repo
    import csv
    
    repo = Repo(repo_path)
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sha", "author", "timestamp", "insertions", "deletions"])
        writer.writeheader()
        
        chunk = []
        for commit in repo.iter_commits("HEAD"):
            chunk.append({
                "sha": commit.hexsha,
                "author": commit.author.name,
                "timestamp": commit.committed_date,
                "insertions": commit.stats.total["insertions"],
                "deletions": commit.stats.total["deletions"],
            })
            
            if len(chunk) >= chunk_size:
                writer.writerows(chunk)
                chunk = []
                f.flush()
        
        if chunk:
            writer.writerows(chunk)
```

## Performance Tips

| Technique | Speedup | When |
|-----------|---------|------|
| `--first-parent` traversal | 3-5x | Repos with heavy merging |
| Filter before explode | 10x | Churn/coupling queries |
| Pre-cache SHA → commit mapping | 2x | Multiple metrics on same repo |
| Skip binary files in diffs | 20%+ | Repos with assets |
| Use `git log --numstat` subprocess | 5x faster than gitpython diffs | Large repos |

## Rust Performance Target

From project-plan.md: analyze a 100K-commit repo in < 2 seconds.

```rust
// In Rust: prefer rayon for data parallelism
use rayon::prelude::*;

let all_commits: Vec<Commit> = revwalk.collect::<Vec<_>>();
let records: Vec<CommitRecord> = all_commits
    .par_iter()  // parallel iterator
    .filter_map(|oid| {
        let commit = repo.find_commit(*oid).ok()?;
        Some(CommitRecord::from_commit(&commit))
    })
    .collect();
```
