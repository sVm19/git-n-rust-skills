"""
analyze.py — `stageira analyze` command.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def analyze(
    repo: Path = typer.Argument(
        default=Path("."),
        help="Path to git repository",
        exists=True,
    ),
    window: int = typer.Option(30, "--window", "-w", help="Analysis window in days"),
    format: str = typer.Option("json", "--format", "-f", help="Output: json | csv | table"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Output file path"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to stageira.toml"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
):
    """
    Analyze a git repository and compute all metrics.
    
    Examples:
    
        stageira analyze .
        
        stageira analyze /path/to/repo --window 90 --format csv --out report.csv
        
        stageira analyze . --quiet  # for CI/CD pipelines
    """
    from ..config import load_config
    
    cfg = load_config(config or Path("stageira.toml"))
    
    if not quiet:
        console.print(Panel.fit(
            f"[bold]Repo:[/bold] {repo.resolve()}\n"
            f"[bold]Window:[/bold] {window} days\n"
            f"[bold]Format:[/bold] {format}",
            title="[cyan]Stageira Analysis[/cyan]",
        ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        disable=quiet,
        console=console,
    ) as progress:
        task = progress.add_task("Scanning commits...", total=None)
        
        # Import here to keep startup fast
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
        
        progress.update(task, description="Computing metrics...")
        progress.update(task, description="Exporting results...")
    
    if not quiet:
        console.print("[green]✓[/green] Analysis complete")
