"""
temporal_coupling.py — Detect files that frequently change together.

Temporal coupling is a hidden dependency signal. Files that change in the
same commit 80% of the time are tightly coupled — even if they look unrelated.
"""

from __future__ import annotations

import polars as pl


def temporal_coupling(
    df: pl.DataFrame,
    min_co_changes: int = 3,
    top_n: int = 50,
) -> pl.DataFrame:
    """
    Find file pairs that change together frequently.
    
    Args:
        df: Commits DataFrame with [sha, files_changed]
        min_co_changes: Minimum times two files must co-change to appear (noise filter)
        top_n: Maximum pairs to return
    
    Returns:
        DataFrame: [file_a, file_b, co_change_count, coupling_strength]
        coupling_strength = co_changes / total changes of the less-changed file
    """
    exploded = df.select(["sha", "files_changed"]).explode("files_changed").drop_nulls()
    
    # Self-join on sha to get file pairs per commit
    coupled = (
        exploded.join(exploded, on="sha", suffix="_b")
        .filter(pl.col("files_changed") < pl.col("files_changed_b"))  # deduplicate pairs
        .group_by(["files_changed", "files_changed_b"])
        .agg(pl.len().alias("co_change_count"))
        .filter(pl.col("co_change_count") >= min_co_changes)
        .rename({"files_changed": "file_a", "files_changed_b": "file_b"})
        .sort("co_change_count", descending=True)
        .head(top_n)
    )
    
    return coupled


def coupling_strength(df: pl.DataFrame, coupled: pl.DataFrame) -> pl.DataFrame:
    """
    Enrich temporal coupling with coupling strength ratio.
    
    coupling_strength = co_changes / min(total_a, total_b)
    A ratio near 1.0 means the files almost always change together.
    """
    file_commit_counts = (
        df.explode("files_changed")
        .drop_nulls()
        .group_by("files_changed")
        .agg(pl.len().alias("total_commits"))
        .rename({"files_changed": "file"})
    )
    
    return (
        coupled
        .join(file_commit_counts.rename({"file": "file_a", "total_commits": "total_a"}), on="file_a", how="left")
        .join(file_commit_counts.rename({"file": "file_b", "total_commits": "total_b"}), on="file_b", how="left")
        .with_columns(
            (pl.col("co_change_count") /
             pl.min_horizontal("total_a", "total_b")).alias("coupling_strength")
        )
        .sort("coupling_strength", descending=True)
    )
