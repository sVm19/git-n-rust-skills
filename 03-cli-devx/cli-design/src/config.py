"""
config.py — Stageira configuration loader using TOML + Pydantic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class AlertConfig(BaseModel):
    code_churn_threshold: float = 0.7
    bus_factor_min: int = 3
    notify: str = "none"
    webhook_url: str = ""


class MetricsConfig(BaseModel):
    churn: bool = True
    bus_factor: bool = True
    temporal_coupling: bool = True
    contributor_stats: bool = True
    commit_frequency: bool = True


class ThresholdsConfig(BaseModel):
    churn_top_n: int = 50
    temporal_coupling_min_support: int = 3


class OutputConfig(BaseModel):
    format: str = "json"
    out: Optional[str] = None


class RepoConfig(BaseModel):
    path: str = "."
    window_days: int = 30


class StageiraConfig(BaseModel):
    repo: RepoConfig = RepoConfig()
    output: OutputConfig = OutputConfig()
    metrics: MetricsConfig = MetricsConfig()
    thresholds: ThresholdsConfig = ThresholdsConfig()
    alerts: AlertConfig = AlertConfig()


def load_config(path: Path = Path("stageira.toml")) -> StageiraConfig:
    """Load configuration from TOML file, or return defaults if not found."""
    if not path.exists():
        return StageiraConfig()
    
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # pip install tomli
        except ImportError:
            return StageiraConfig()
    
    with open(path, "rb") as f:
        data = tomllib.load(f)
    
    return StageiraConfig(**data)
