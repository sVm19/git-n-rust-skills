"""
exporter.py — Export Stageira metrics to JSON and CSV.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl


def to_json(data: dict | list, output_path: Path, pretty: bool = True) -> Path:
    """Write dict/list to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2 if pretty else None, default=_json_default)
    
    return output_path


def dataframe_to_json(df: pl.DataFrame, output_path: Path) -> Path:
    """Write a Polars DataFrame as row-oriented JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_json(str(output_path), row_oriented=True)
    return output_path


def dataframe_to_csv(df: pl.DataFrame, output_path: Path) -> Path:
    """Write a Polars DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(str(output_path))
    return output_path


def metrics_report(
    repo_path: str,
    metrics: dict[str, pl.DataFrame],
    output_path: Path,
    window_days: int = 30,
) -> Path:
    """Write a full Stageira metrics report to JSON."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "repo_path": repo_path,
        "window_days": window_days,
        "metrics": {
            name: df.to_dicts() for name, df in metrics.items()
        },
    }
    return to_json(report, output_path)


def _json_default(obj: Any) -> Any:
    """JSON serializer for types not handled by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
