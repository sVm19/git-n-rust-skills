"""
dataframe_ops.py — Utility Polars operations for Stageira.

Helpers for building DataFrames from scanner output, type casting,
and common transformations used across analytics modules.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

import polars as pl

from ...git_internals_master.src.scanner import CommitRecord


def records_to_dataframe(records: Sequence[CommitRecord]) -> pl.DataFrame:
    """Convert a list of CommitRecords to a typed Polars DataFrame."""
    if not records:
        return pl.DataFrame(schema={
            "sha": pl.Utf8,
            "author": pl.Utf8,
            "email": pl.Utf8,
            "timestamp": pl.Datetime,
            "files_changed": pl.List(pl.Utf8),
            "insertions": pl.Int32,
            "deletions": pl.Int32,
            "message": pl.Utf8,
        })
    
    return pl.DataFrame({
        "sha": [r.sha for r in records],
        "author": [r.author_name for r in records],
        "email": [r.author_email for r in records],
        "timestamp": [r.timestamp for r in records],
        "files_changed": [r.files_changed for r in records],
        "insertions": [r.insertions for r in records],
        "deletions": [r.deletions for r in records],
        "message": [r.message for r in records],
    }).with_columns(
        pl.col("timestamp").cast(pl.Datetime),
        pl.col("insertions").cast(pl.Int32),
        pl.col("deletions").cast(pl.Int32),
    )


def filter_date_range(
    df: pl.DataFrame,
    start: datetime,
    end: datetime,
) -> pl.DataFrame:
    """Filter DataFrame to commits within [start, end]."""
    return df.filter(
        (pl.col("timestamp") >= start) & (pl.col("timestamp") <= end)
    )


def top_n(df: pl.DataFrame, column: str, n: int = 20) -> pl.DataFrame:
    """Return top N rows by column, descending."""
    return df.sort(column, descending=True).head(n)


def normalize_column(df: pl.DataFrame, column: str) -> pl.DataFrame:
    """Normalize a numeric column to [0, 1]."""
    col_min = df[column].min()
    col_max = df[column].max()
    if col_max == col_min:
        return df.with_columns(pl.lit(0.0).alias(f"{column}_normalized"))
    return df.with_columns(
        ((pl.col(column) - col_min) / (col_max - col_min)).alias(f"{column}_normalized")
    )
