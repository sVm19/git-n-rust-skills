"""
analytics.py — Core analytics for Stageira's data-processing-polars skill.

All functions take a Polars DataFrame of CommitRecords and return computed metrics.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import polars as pl


def compute_churn(
    df: pl.DataFrame,
    window_days: int = 30,
    cutoff: Optional[datetime] = None,
) -> pl.DataFrame:
    """
    Compute code churn: files edited most frequently in the last N days.
    
    Returns DataFrame with columns: [file, edit_count, lines_added, lines_removed, churn_score]
    """
    if cutoff is None:
        cutoff = datetime.now() - timedelta(days=window_days)
    
    return (
        df.filter(pl.col("timestamp") >= cutoff)
        .explode("files_changed")
        .rename({"files_changed": "file"})
        .drop_nulls("file")
        .filter(pl.col("file").str.len_chars() > 0)
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


def compute_bus_factor(df: pl.DataFrame) -> pl.DataFrame:
    """
    Compute bus factor: ownership percentage per author per file.
    
    Returns DataFrame: [file, author, commit_count, ownership_pct, cumulative_pct]
    """
    file_ownership = (
        df.explode("files_changed")
        .drop_nulls("files_changed")
        .group_by(["files_changed", "author"])
        .agg(pl.len().alias("commit_count"))
        .rename({"files_changed": "file"})
    )
    
    totals = (
        file_ownership
        .group_by("file")
        .agg(pl.col("commit_count").sum().alias("total_commits"))
    )
    
    return (
        file_ownership
        .join(totals, on="file")
        .with_columns(
            (pl.col("commit_count") / pl.col("total_commits")).alias("ownership_pct")
        )
        .sort(["file", "ownership_pct"], descending=[False, True])
    )


def compute_temporal_coupling(
    df: pl.DataFrame,
    min_co_changes: int = 3,
) -> pl.DataFrame:
    """
    Detect files that change together frequently.
    
    Returns DataFrame: [file_a, file_b, co_change_count]
    """
    exploded = df.select(["sha", "files_changed"]).explode("files_changed")
    
    coupled = (
        exploded.join(exploded, on="sha", suffix="_b")
        .filter(pl.col("files_changed") < pl.col("files_changed_b"))
        .group_by(["files_changed", "files_changed_b"])
        .agg(pl.len().alias("co_change_count"))
        .filter(pl.col("co_change_count") >= min_co_changes)
        .rename({"files_changed": "file_a", "files_changed_b": "file_b"})
        .sort("co_change_count", descending=True)
    )
    return coupled


def contributor_stats(df: pl.DataFrame) -> pl.DataFrame:
    """
    Aggregate stats per contributor.
    
    Returns: [author, total_commits, total_insertions, total_deletions, first_commit, last_commit, commit_share]
    """
    stats = (
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
    
    total = stats["total_commits"].sum()
    return stats.with_columns(
        (pl.col("total_commits") / total).alias("commit_share")
    )


def commit_frequency(df: pl.DataFrame, period: str = "1w") -> pl.DataFrame:
    """
    Commit count bucketed by time period.
    
    Args:
        period: Polars duration string, e.g. "1w", "1mo", "1d"
    
    Returns: [period, commit_count, rolling_4w_avg]
    """
    return (
        df.with_columns(
            pl.col("timestamp").dt.truncate(period).alias("period")
        )
        .group_by("period")
        .agg(pl.len().alias("commit_count"))
        .sort("period")
        .with_columns(
            pl.col("commit_count").rolling_mean(window_size=4).alias("rolling_avg")
        )
    )
