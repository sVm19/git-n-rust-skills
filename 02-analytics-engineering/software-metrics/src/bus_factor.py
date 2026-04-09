"""
bus_factor.py — Bus factor risk analysis for Stageira.

Bus factor = minimum authors whose departure would halt work on a file/module.
A bus factor of 1 = dangerous key-person risk.
"""

from __future__ import annotations

import polars as pl


def bus_factor(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate ownership % per author per file.
    
    Returns:
        DataFrame: [file, author, commit_count, ownership_pct]
        Sorted by file asc, ownership_pct desc.
    """
    file_ownership = (
        df.explode("files_changed")
        .drop_nulls("files_changed")
        .rename({"files_changed": "file"})
        .group_by(["file", "author"])
        .agg(pl.len().alias("commit_count"))
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


def bus_factor_score_per_file(ownership_df: pl.DataFrame) -> pl.DataFrame:
    """
    Compute a single bus factor score per file:
    Number of authors needed to cover 50%+ of commits.
    
    Args:
        ownership_df: Output of bus_factor()
    
    Returns:
        DataFrame: [file, bus_factor_score, top_author, top_author_pct]
    """
    rows = []
    for file, group in ownership_df.group_by("file"):
        sorted_group = group.sort("ownership_pct", descending=True)
        cumulative = 0.0
        count = 0
        for row in sorted_group.iter_rows(named=True):
            cumulative += row["ownership_pct"]
            count += 1
            if cumulative >= 0.5:
                break
        
        top_row = sorted_group.row(0, named=True)
        rows.append({
            "file": file[0] if isinstance(file, tuple) else file,
            "bus_factor_score": count,
            "top_author": top_row["author"],
            "top_author_pct": round(top_row["ownership_pct"], 3),
        })
    
    return (
        pl.DataFrame(rows)
        .sort("bus_factor_score")  # lowest bus factor = highest risk = first
    )


def risky_files(df: pl.DataFrame, threshold: int = 2) -> pl.DataFrame:
    """Return files with bus factor < threshold (high risk)."""
    ownership = bus_factor(df)
    scores = bus_factor_score_per_file(ownership)
    return scores.filter(pl.col("bus_factor_score") < threshold)
