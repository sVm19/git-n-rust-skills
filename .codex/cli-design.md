---
name: cli-design
description: Design and implement production-grade Stageira CLI commands using Typer (Python) and Clap (Rust). Use whenever building or modifying the `analyze`, `compare`, or `export` commands, adding arguments, improving help text, or designing the UX of stageira's terminal interface. Triggers on "CLI command", "typer", "clap", "add argument", "stageira analyze", "stageira compare", "CLI UX", or "terminal output".
---


# CLI Design — Production-Grade Stageira Interface

The CLI is Stageira's primary customer touchpoint. It must be clear, fast, and CI/CD-friendly.

## Command Architecture

```
stageira
├── analyze   ← Core: run all metrics on a repo
├── compare   ← Historical: period-over-period diff
└── export    ← Output: write JSON/CSV to a file
```

## Typer Structure (Python prototype)

```python
# src/main.py
import typer
from rich.console import Console
from .commands import analyze, compare, export

app = typer.Typer(
    name="stageira",
    help="Local-first git repository analytics. No API access required.",
    no_args_is_help=True,
)
app.add_typer(analyze.app, name="analyze")
app.add_typer(compare.app, name="compare")
app.add_typer(export.app, name="export")

if __name__ == "__main__":
    app()
```

## analyze command

```python
# src/commands/analyze.py
import typer
from pathlib import Path
from rich.console import Console
from rich.progress import track

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def analyze(
    repo: Path = typer.Argument(
        default=Path("."),
        help="Path to git repository (default: current directory)",
        exists=True,
    ),
    window: int = typer.Option(
        30,
        "--window", "-w",
        help="Analysis window in days",
    ),
    output: str = typer.Option(
        "json",
        "--format", "-f",
        help="Output format: json | csv | table",
    ),
    out_file: Path = typer.Option(
        None,
        "--out", "-o",
        help="Write output to file (default: stdout)",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Suppress progress output (for CI/CD)",
    ),
):
    """Analyze a git repository and compute all metrics."""
    if not quiet:
        console.print(f"[bold cyan]stageira[/bold cyan] Analyzing: {repo}")
    
    # 1. Scan commits
    # 2. Compute metrics
    # 3. Export
```

## compare command

```python
# src/commands/compare.py
@app.callback(invoke_without_command=True)
def compare(
    repo: Path = typer.Argument(default=Path(".")),
    from_date: str = typer.Option(..., "--from", help="Start of period A (YYYY-MM-DD or YYYY-QN)"),
    to_date: str = typer.Option(..., "--to", help="Start of period B"),
):
    """Compare metrics between two time periods.
    
    Examples:
        stageira compare --from=2024-Q1 --to=2024-Q2
        stageira compare --from=2024-01-01 --to=2024-04-01
    """
```

## export command

```python
# src/commands/export.py
@app.command()
def to_json(repo: Path, output: Path):
    """Export metrics to JSON."""

@app.command()
def to_csv(repo: Path, output: Path):
    """Export metrics to CSV."""

@app.command()
def to_datadog(repo: Path, webhook: str):
    """Push metrics to Datadog via file-based integration."""
```

## TOML Config System

```python
# src/config.py
from pydantic import BaseModel
import tomllib
from pathlib import Path

class AlertConfig(BaseModel):
    code_churn_threshold: float = 0.7
    bus_factor_min: int = 3
    notify: str = "none"
    webhook_url: str = ""

class StageiraConfig(BaseModel):
    repo_path: str = "."
    window_days: int = 30
    alerts: AlertConfig = AlertConfig()

def load_config(path: Path = Path("stageira.toml")) -> StageiraConfig:
    if path.exists():
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return StageiraConfig(**data)
    return StageiraConfig()
```

## Default stageira.toml

```toml
# stageira.toml — Configuration for Stageira git analyzer

[repo]
path = "."
window_days = 30

[alerts]
code_churn_threshold = 0.7
bus_factor_min = 3
notify = "none"
# webhook_url = "https://hooks.slack.com/..."

[output]
format = "json"
```

## Rich Output Patterns

```python
# Beautiful terminal output without sacrificing CI compatibility
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def print_summary(metrics: dict):
    console.print(Panel.fit(
        f"[bold]Repo:[/bold] {metrics['repo']}\n"
        f"[bold]Commits analyzed:[/bold] {metrics['total_commits']}\n"
        f"[bold]Window:[/bold] {metrics['window_days']} days",
        title="[cyan]Stageira Analysis[/cyan]"
    ))
```

## CI/CD Compatibility Rules

1. Always support `--quiet` / `-q` for silent output
2. Exit code 0 = success, 1 = error, 2 = alert triggered
3. JSON output must be valid and parseable by `jq`
4. Never print color codes when stdout is not a TTY: Rich handles this automatically
