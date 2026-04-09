"""
compare.py — `stageira compare` command.
"""

from datetime import datetime, date
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

QUARTER_MAP = {
    "Q1": (1, 3), "Q2": (4, 6), "Q3": (7, 9), "Q4": (10, 12)
}


def parse_period(s: str) -> tuple[datetime, datetime]:
    """
    Parse period string like '2024-Q1' or '2024-01-01'.
    Returns (start, end) as datetime.
    """
    if "Q" in s.upper():
        year_str, q_str = s.upper().split("-")
        year = int(year_str)
        start_month, end_month = QUARTER_MAP[q_str]
        start = datetime(year, start_month, 1)
        if end_month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, end_month + 1, 1)
        return (start, end)
    else:
        d = datetime.strptime(s, "%Y-%m-%d")
        return (d, d)


@app.callback(invoke_without_command=True)
def compare(
    repo: str = typer.Argument(default=".", help="Path to git repository"),
    from_period: str = typer.Option(..., "--from", help="Period A: YYYY-MM-DD or YYYY-QN"),
    to_period: str = typer.Option(..., "--to", help="Period B: YYYY-MM-DD or YYYY-QN"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
):
    """
    Compare metrics between two time periods.
    
    Examples:
    
        stageira compare --from=2024-Q1 --to=2024-Q2
        
        stageira compare --from=2024-01-01 --to=2024-04-01
    """
    a_start, a_end = parse_period(from_period)
    b_start, b_end = parse_period(to_period)
    
    if not quiet:
        console.print(f"Comparing [bold]{from_period}[/bold] → [bold]{to_period}[/bold]")
    
    # TODO: load df from repo, call trends.compare_periods(), display table
    console.print("[yellow]compare command: connect to analytics layer[/yellow]")
