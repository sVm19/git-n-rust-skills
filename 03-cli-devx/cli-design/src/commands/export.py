"""
export.py — `stageira export` command.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command("json")
def to_json(
    repo: Path = typer.Argument(default=Path("."), exists=True),
    output: Path = typer.Option(Path("stageira-report.json"), "--out", "-o"),
    window: int = typer.Option(30, "--window", "-w"),
):
    """Export metrics to JSON."""
    console.print(f"Exporting JSON → {output}")
    # TODO: call scanner + analytics + exporter


@app.command("csv")
def to_csv(
    repo: Path = typer.Argument(default=Path("."), exists=True),
    output: Path = typer.Option(Path("stageira-report.csv"), "--out", "-o"),
):
    """Export metrics to CSV."""
    console.print(f"Exporting CSV → {output}")


@app.command("datadog")
def to_datadog(
    repo: Path = typer.Argument(default=Path("."), exists=True),
    output: Path = typer.Option(Path("dd_metrics.json"), "--out", "-o"),
):
    """Export metrics in Datadog JSON format (for Datadog agent file intake)."""
    console.print(f"Exporting Datadog metrics → {output}")


@app.command("prometheus")
def to_prometheus(
    repo: Path = typer.Argument(default=Path("."), exists=True),
    output: Path = typer.Option(Path("metrics.txt"), "--out", "-o"),
):
    """Export metrics in Prometheus text format."""
    console.print(f"Exporting Prometheus metrics → {output}")
