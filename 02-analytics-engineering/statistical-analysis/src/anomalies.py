"""
anomalies.py — Outlier and anomaly detection for Stageira commit metrics.
"""

from __future__ import annotations

import polars as pl


def detect_commit_anomalies(
    df: pl.DataFrame,
    period: str = "1w",
    z_threshold: float = 2.5,
) -> pl.DataFrame:
    """
    Flag time periods where commit count is statistically unusual.
    
    Uses Z-score: (value - mean) / std
    
    Args:
        df: Commits DataFrame
        period: Time bucket size ("1w", "1mo", "1d")
        z_threshold: Number of standard deviations to flag (2.5 = ~1% false positive rate)
    
    Returns:
        DataFrame: [period, commit_count, z_score, is_anomaly]
    """
    weekly = (
        df.with_columns(pl.col("timestamp").dt.truncate(period).alias("period"))
        .group_by("period")
        .agg(pl.len().alias("commit_count"))
        .sort("period")
    )
    
    mean = weekly["commit_count"].mean() or 0.0
    std = weekly["commit_count"].std() or 1.0
    
    return weekly.with_columns([
        ((pl.col("commit_count") - mean) / std).alias("z_score"),
        (((pl.col("commit_count") - mean) / std).abs() > z_threshold).alias("is_anomaly"),
    ])


def detect_churn_spikes(
    churn_df: pl.DataFrame,
    rolling_window: int = 4,
    spike_multiplier: float = 2.0,
) -> pl.DataFrame:
    """
    Detect files whose churn score spikes beyond X times the rolling average.
    
    A spike indicates an active refactor or high-risk turbulence period.
    """
    return churn_df.with_columns([
        pl.col("churn_score")
          .rolling_mean(window_size=rolling_window)
          .alias("rolling_churn_avg"),
    ]).with_columns([
        (pl.col("churn_score") > pl.col("rolling_churn_avg") * spike_multiplier)
          .alias("is_spike"),
    ])
