"""
trends.py — Time-series trend analysis for Stageira's statistical module.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import polars as pl


def commit_frequency_trend(
    df: pl.DataFrame,
    period: str = "1w",
    rolling_window: int = 4,
) -> pl.DataFrame:
    """
    Weekly commit counts with rolling average and week-over-week delta.
    
    Returns: [period, commit_count, rolling_avg, wow_delta]
    """
    return (
        df.with_columns(
            pl.col("timestamp").dt.truncate(period).alias("period")
        )
        .group_by("period")
        .agg(pl.len().alias("commit_count"))
        .sort("period")
        .with_columns([
            pl.col("commit_count")
              .rolling_mean(window_size=rolling_window)
              .alias("rolling_avg"),
            pl.col("commit_count").diff().alias("wow_delta"),
        ])
    )


def compare_periods(
    df: pl.DataFrame,
    period_a_start: datetime,
    period_a_end: datetime,
    period_b_start: datetime,
    period_b_end: datetime,
) -> dict:
    """
    Compare metrics between two time windows.
    
    Returns a dict with stats for both periods and delta values.
    Powers `stageira compare --from=2024-Q1 --to=2024-Q2`.
    """
    def stats_for_window(start: datetime, end: datetime) -> dict:
        window = df.filter(
            (pl.col("timestamp") >= start) & (pl.col("timestamp") < end)
        )
        if len(window) == 0:
            return {"total_commits": 0, "unique_authors": 0, "avg_files_per_commit": 0.0}
        
        avg_files = (
            window.with_columns(pl.col("files_changed").list.len().alias("n_files"))
            ["n_files"].mean() or 0.0
        )
        
        return {
            "total_commits": len(window),
            "unique_authors": window["author"].n_unique(),
            "avg_files_per_commit": round(float(avg_files), 2),
            "total_insertions": int(window["insertions"].sum() or 0),
            "total_deletions": int(window["deletions"].sum() or 0),
        }
    
    a = stats_for_window(period_a_start, period_a_end)
    b = stats_for_window(period_b_start, period_b_end)
    
    def pct_change(old: float, new: float) -> Optional[float]:
        if old == 0:
            return None
        return round((new - old) / old * 100, 1)
    
    return {
        "period_a": {"start": period_a_start.isoformat(), "end": period_a_end.isoformat(), **a},
        "period_b": {"start": period_b_start.isoformat(), "end": period_b_end.isoformat(), **b},
        "delta": {
            "commits": b["total_commits"] - a["total_commits"],
            "commits_pct": pct_change(a["total_commits"], b["total_commits"]),
            "authors": b["unique_authors"] - a["unique_authors"],
        },
        "narrative": _narrative(a, b),
    }


def _narrative(a: dict, b: dict) -> str:
    delta = b["total_commits"] - a["total_commits"]
    pct = abs(delta) / max(a["total_commits"], 1) * 100
    direction = "increased" if delta > 0 else "decreased"
    return (
        f"Commit velocity {direction} by {pct:.1f}% between periods. "
        f"Active contributors: {a['unique_authors']} → {b['unique_authors']}."
    )
