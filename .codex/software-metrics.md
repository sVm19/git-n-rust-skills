---
name: software-metrics
description: Implement and compute software engineering metrics for Stageira: code churn, bus factor, contribution distribution, temporal coupling, commit frequency trends. Use whenever working on metrics algorithms, adding a new metric, or explaining what a metric means to enterprise customers. Triggers on \"code churn\", \"bus factor\", \"temporal coupling\", \"contribution stats\", \"commit trends\", or \"metrics\" in the context of git analysis.
---


# Software Metrics Engineering

The analytics heart of Stageira. This skill covers what metrics to compute, why they matter to enterprise buyers, and how to implement them correctly.

## The Metrics Suite

### 1. Code Churn

**What**: How frequently each file is edited over time.
**Enterprise value**: Identifies unstable code — high churn = high bug risk.

```python
# churn.py
def code_churn(df: pl.DataFrame, window_days: int = 30) -> pl.DataFrame:
    cutoff = datetime.now() - timedelta(days=window_days)
    return (
        df.filter(pl.col("timestamp") >= cutoff)
        .explode("files_changed")
        .rename({"files_changed": "file"})
        .group_by("file")
        .agg(
            pl.len().alias("edit_count"),
            pl.col("insertions").sum().alias("lines_added"),
            pl.col("deletions").sum().alias("lines_removed"),
        )
        .with_columns(
            (pl.col("lines_added") + pl.col("lines_removed")).alias("churn_score")
        )
        .sort("churn_score", descending=True)
    )
```

**Threshold alert**: churn_score > `config.alerts.code_churn_threshold`

---

### 2. Bus Factor

**What**: Minimum number of contributors whose departure would stall a project area.
**Enterprise value**: Risk management — identifies single points of failure.

```python
# bus_factor.py
def bus_factor(df: pl.DataFrame) -> pl.DataFrame:
    file_ownership = (
        df.explode("files_changed")
        .group_by(["files_changed", "author"])
        .agg(pl.len().alias("commit_count"))
    )
    totals = (
        file_ownership.group_by("files_changed")
        .agg(pl.col("commit_count").sum().alias("total_commits"))
    )
    ownership = file_ownership.join(totals, on="files_changed").with_columns(
        (pl.col("commit_count") / pl.col("total_commits")).alias("ownership_pct")
    )
    # Bus factor = count of authors needed to reach 50% ownership
    def bus_factor_for_file(group):
        sorted_pct = group.sort("ownership_pct", descending=True)
        cumulative = 0
        for i, row in enumerate(sorted_pct.iter_rows(named=True)):
            cumulative += row["ownership_pct"]
            if cumulative >= 0.5:
                return i + 1
        return len(group)
    
    return ownership  # caller applies bus_factor_for_file per file group
```

**Alert**: bus_factor < `config.alerts.bus_factor_min` (default: 3)

---

### 3. Temporal Coupling

**What**: Files that change together frequently (strong coupling signal).
**Enterprise value**: Reveals hidden dependencies, informs refactoring.

```python
# temporal_coupling.py
def temporal_coupling(df: pl.DataFrame, min_support: int = 5) -> pl.DataFrame:
    pairs = (
        df.explode("files_changed").alias("a")
        .join(df.explode("files_changed").alias("b"), on="sha")
        .filter(pl.col("files_changed") < pl.col("files_changed_right"))
        .group_by(["files_changed", "files_changed_right"])
        .agg(pl.len().alias("co_changes"))
        .filter(pl.col("co_changes") >= min_support)
        .sort("co_changes", descending=True)
    )
    return pairs
```

---

### 4. Contribution Distribution

**What**: How evenly contributions are spread across the team.
**Enterprise value**: Identifies knowledge concentration and team health.

```python
# in analytics.py
def contribution_distribution(df: pl.DataFrame) -> pl.DataFrame:
    by_author = (
        df.group_by("author")
        .agg([
            pl.len().alias("commits"),
            pl.col("insertions").sum().alias("lines_added"),
        ])
        .with_columns(
            (pl.col("commits") / pl.col("commits").sum()).alias("commit_share"),
        )
        .sort("commits", descending=True)
    )
    return by_author
```

---

### 5. Commit Frequency Trends

**What**: Commit rate per week/month over time.
**Enterprise value**: Shows team velocity, release cadence, slowdowns.

```python
def commit_frequency(df: pl.DataFrame, freq: str = "1w") -> pl.DataFrame:
    return (
        df.with_columns(
            pl.col("timestamp").dt.truncate(freq).alias("period")
        )
        .group_by("period")
        .agg(pl.len().alias("commit_count"))
        .sort("period")
    )
```

## Metric Output Schema

```json
{
  "generated_at": "2024-01-15T10:30:00Z",
  "repo_path": "/path/to/repo",
  "window_days": 30,
  "metrics": {
    "churn": [
      {"file": "src/main.rs", "edit_count": 42, "churn_score": 380}
    ],
    "bus_factor": [
      {"file": "src/scanner.py", "bus_factor": 1, "top_author": "alice"}
    ],
    "temporal_coupling": [
      {"file_a": "src/a.rs", "file_b": "src/b.rs", "co_changes": 18}
    ],
    "contribution_distribution": [
      {"author": "alice", "commits": 120, "commit_share": 0.45}
    ],
    "commit_frequency": [
      {"period": "2024-01-08", "commit_count": 23}
    ]
  }
}
```

## Alert Integration

In `stageira.toml`:

```toml
[alerts]
code_churn_threshold = 0.7
bus_factor_min = 3
notify = "slack_webhook"
webhook_url = "https://hooks.slack.com/..."
```
