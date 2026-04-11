---
name: data-processing-polars
description: Rust-first Polars DataFrames for Stageira's analytics engine. Use when computing churn, contributor stats, temporal patterns, or any aggregation on commit data. Triggers on "polars dataframe", "aggregate commits", "compute metrics", "churn calculation", "contributor stats", "temporal analysis", or any work in analytics.py / dataframe_ops.py.
---


# Data Processing with Polars

Polars is Stageira's analytics layer. It processes commit history data at DataFrame scale — much faster than pandas, and memory-efficient enough for monorepos.

> ⚠️ Polars Python API ≠ Polars Rust API. Most online examples are Python. Stageira uses Python Polars for analytics (the Rust binary handles git parsing).

## Key Philosophy

- Never iterate rows — always use expressions
- Lazy frames (`scan_*`) for large datasets
- Group-by + aggregation is the core pattern

## CommitRecord → Polars DataFrame

```python
import polars as pl
from datetime import datetime

# Build from scanner output
records = [...]  # list of CommitRecord dicts

df = pl.DataFrame({
    "sha": [r.sha for r in records],
    "author": [r.author_name for r in records],
    "email": [r.author_email for r in records],
    "timestamp": [r.timestamp for r in records],
    "files": [r.files_changed for r in records],
    "insertions": [r.insertions for r in records],
    "deletions": [r.deletions for r in records],
})

# Cast timestamp to proper type
df = df.with_columns(
    pl.col("timestamp").cast(pl.Datetime)
)
```

## Core Analytics Patterns

### Code Churn (file edit frequency)

```python
def compute_churn(df: pl.DataFrame, window_days: int = 30) -> pl.DataFrame:
    """Files edited most frequently in the last N days."""
    cutoff = datetime.now() - timedelta(days=window_days)
    
    return (
        df.filter(pl.col("timestamp") >= cutoff)
        .explode("files")           # unnest list column
        .group_by("files")
        .agg(pl.len().alias("edit_count"))
        .sort("edit_count", descending=True)
    )
```

### Bus Factor (contributor concentration)

```python
def compute_bus_factor(df: pl.DataFrame) -> pl.DataFrame:
    """Number of authors who own 50%+ of commits per file."""
    file_commits = (
        df.explode("files")
        .group_by(["files", "author"])
        .agg(pl.len().alias("commit_count"))
    )
    
    total_per_file = file_commits.group_by("files").agg(
        pl.col("commit_count").sum().alias("total")
    )
    
    return file_commits.join(total_per_file, on="files").with_columns(
        (pl.col("commit_count") / pl.col("total")).alias("ownership_ratio")
    )
```

### Temporal Coupling (files that change together)

```python
def compute_temporal_coupling(df: pl.DataFrame) -> pl.DataFrame:
    """File pairs that appear in the same commit frequently."""
    exploded = df.explode("files").select(["sha", "files"])
    
    # Self-join on sha to find co-occurring files
    coupled = exploded.join(exploded, on="sha", suffix="_partner")
    
    return (
        coupled.filter(pl.col("files") < pl.col("files_partner"))
        .group_by(["files", "files_partner"])
        .agg(pl.len().alias("co_change_count"))
        .sort("co_change_count", descending=True)
    )
```

### Contributor Stats

```python
def contributor_stats(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("author")
        .agg([
            pl.len().alias("total_commits"),
            pl.col("insertions").sum().alias("total_insertions"),
            pl.col("deletions").sum().alias("total_deletions"),
            pl.col("timestamp").min().alias("first_commit"),
            pl.col("timestamp").max().alias("last_commit"),
        ])
        .sort("total_commits", descending=True)
    )
```

## Lazy Evaluation (for large repos)

```python
# Use scan_csv / LazyFrame for repos with 100K+ commits
lazy = pl.scan_csv("commits.csv")

result = (
    lazy
    .filter(pl.col("insertions") > 0)
    .group_by("author")
    .agg(pl.len())
    .collect()  # Only materializes here
)
```

## Export to JSON / CSV

```python
# JSON
df.write_json("output.json", row_oriented=True)

# CSV
df.write_csv("output.csv")

# Pretty print for CLI
from rich.table import Table
from rich.console import Console

def print_table(df: pl.DataFrame, title: str):
    console = Console()
    table = Table(title=title, show_header=True)
    for col in df.columns:
        table.add_column(col)
    for row in df.iter_rows():
        table.add_row(*[str(v) for v in row])
    console.print(table)
```

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| `df.apply(lambda row: ...)` | Use `.map_elements()` only as last resort |
| Chaining `.to_pandas()` | Stay in Polars until final export |
| Exploding before filtering | Filter first → then explode (10x faster) |
| Ignoring null handling | Use `.drop_nulls()` or `.fill_null()` explicitly |
