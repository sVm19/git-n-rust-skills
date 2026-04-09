"""
main.py — Stageira CLI entry point.
"""

import typer
from rich.console import Console

from .commands import analyze, compare, export

app = typer.Typer(
    name="stageira",
    help="Local-first git repository analytics. No API access required.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

app.add_typer(analyze.app, name="analyze", help="Analyze a git repository")
app.add_typer(compare.app, name="compare", help="Compare two time periods")
app.add_typer(export.app, name="export", help="Export metrics to a file")


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit", is_eager=True
    ),
):
    if version:
        console.print("[bold cyan]stageira[/bold cyan] v0.1.0")
        raise typer.Exit()


if __name__ == "__main__":
    app()
