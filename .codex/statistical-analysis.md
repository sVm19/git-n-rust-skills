---
name: statistical-analysis
description: Apply statistical methods to Stageira's git metrics: trend detection, time-series comparison (Q1 vs Q2), variance/anomaly detection. Use whenever the user wants to compare time periods, detect unusual spikes in commits, plot trends, or implement the \"historical comparison\" feature. Triggers on \"compare quarters\", \"trend detection\", \"anomaly\", \"statistical\", \"time series\", \"variance\", or \"Q1 vs Q2\".
---


# Statistical Analysis for Git Metrics

Brings data science methods to Stageira's commit history. Powers the "Historical Comparison" feature — one of the three game-changing additions in the project plan.

## Core Use Cases

1. **Time-period comparison**: Q1 vs Q2 commit velocity, churn, bus factor
2. **Trend detection**: Is code quality improving or degrading?
3. **Anomaly detection**: Unusual spikes (crunch periods, incidents)
4. **Forecasting**: Extrapolate current trends

## Time-Series Comparison (Q1 vs Q2)

```python
# trends.py
import polars as pl
from datetime import datetime

def compare_periods(
    df: pl.DataFrame,
    period_a: tuple[datetime, datetime],
    period_b: tuple[datetime, datetime],
    metric: str = "commit_count",
) -> dict:
    """Compare a metric between two time windows."""
    
    def period_stats(start, end):
        window = df.filter(
            (pl.col("timestamp") >= start) & (pl.col("timestamp") < end)
        )
        return {
            "total_commits": len(window),
            "unique_authors": window["author"].n_unique(),
            "avg_churn": window["insertions"].mean() + window["deletions"].mean(),
            "days": (end - start).days,
        }
    
    a = period_stats(*period_a)
    b = period_stats(*period_b)
    
    return {
        "period_a": a,
        "period_b": b,
        "commits_delta": b["total_commits"] - a["total_commits"],
        "commits_pct_change": (b["total_commits"] - a["total_commits"]) / max(a["total_commits"], 1) * 100,
        "summary": _narrative(a, b),
    }

def _narrative(a: dict, b: dict) -> str:
    delta_pct = (b["total_commits"] - a["total_commits"]) / max(a["total_commits"], 1) * 100
    direction = "improved" if delta_pct > 0 else "decreased"
    return f"Commit velocity {direction} by {abs(delta_pct):.1f}% between periods."
```

## Trend Detection (Rolling Average)

```python
def detect_trends(df: pl.DataFrame, window: str = "4w") -> pl.DataFrame:
    """Compute rolling average and slope for commit frequency."""
    weekly = (
        df.with_columns(pl.col("timestamp").dt.truncate("1w").alias("week"))
        .group_by("week")
        .agg(pl.len().alias("commits"))
        .sort("week")
    )
    
    # Rolling 4-week average
    return weekly.with_columns(
        pl.col("commits").rolling_mean(window_size=4).alias("rolling_avg"),
        pl.col("commits").diff().alias("week_over_week_delta"),
    )
```

## Anomaly Detection

```python
# anomalies.py
def detect_anomalies(df: pl.DataFrame, z_threshold: float = 2.5) -> pl.DataFrame:
    """Flag weeks with commit counts > z_threshold standard deviations from mean."""
    weekly = (
        df.with_columns(pl.col("timestamp").dt.truncate("1w").alias("week"))
        .group_by("week")
        .agg(pl.len().alias("commits"))
        .sort("week")
    )
    
    mean = weekly["commits"].mean()
    std = weekly["commits"].std()
    
    return weekly.with_columns(
        ((pl.col("commits") - mean) / std).alias("z_score"),
        (((pl.col("commits") - mean) / std).abs() > z_threshold).alias("is_anomaly"),
    )
```

## Output for CLI

```
$ stageira compare --from=2024-Q1 --to=2024-Q2

📊 Historical Comparison: Q1 2024 → Q2 2024
─────────────────────────────────────────
Commit velocity:    247 → 312  (+26.3%) ↑
Active authors:      12 → 15   (+25.0%) ↑
Avg code churn:    1.2k → 0.9k (-25.0%) ↓ (stabilizing)
Bus factor (min):    2  → 3    (+1)     ↑

Summary: "Your bus factor improved from 2 to 3 — less key-person risk."
⚠ Anomalies detected: week of 2024-05-13 had 3.1σ spike in commits.
```

## Integration with Stageira CLI

```python
# src/commands/compare.py
import typer
from ..statistical_analysis import compare_periods, detect_anomalies

app = typer.Typer()

@app.command()
def compare(
    repo: str = typer.Argument(...),
    from_date: str = typer.Option(..., "--from"),
    to_date: str = typer.Option(..., "--to"),
):
    """Compare metrics between two time periods."""
    # parse dates, load df, call compare_periods()
    ...
```
