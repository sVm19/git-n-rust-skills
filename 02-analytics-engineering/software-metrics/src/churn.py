"""
churn.py — Code churn calculation for Stageira.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import polars as pl


def code_churn(
    df: pl.DataFrame,
    window_days: int = 30,
    top_n: int = 50,
    cutoff: Optional[datetime] = None,
) -> pl.DataFrame:
    """
    Calculate code churn: which files change most often?
    
    High churn = high bug risk. This is one of the most actionable metrics
    for enterprise engineering managers.
    
    Args:
        df: DataFrame with columns [sha, author, timestamp, files_changed, insertions, deletions]
        window_days: Look-back window in days
        top_n: Return only top N files by churn score
        cutoff: Override the window with an explicit datetime
    
    Returns:
        DataFrame: [file, edit_count, lines_added, lines_removed, churn_score]
    """
    if cutoff is None:
        cutoff = datetime.now() - timedelta(days=window_days)
    
    result = (
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
        .head(top_n)
    )
    return result


def churn_by_author(df: pl.DataFrame, window_days: int = 30) -> pl.DataFrame:
    """Which authors contribute most churn?"""
    cutoff = datetime.now() - timedelta(days=window_days)
    return (
        df.filter(pl.col("timestamp") >= cutoff)
        .group_by("author")
        .agg(
            pl.len().alias("commit_count"),
            pl.col("insertions").sum().alias("total_insertions"),
            pl.col("deletions").sum().alias("total_deletions"),
        )
        .with_columns(
            (pl.col("total_insertions") + pl.col("total_deletions")).alias("churn_score")
        )
        .sort("churn_score", descending=True)
    )
