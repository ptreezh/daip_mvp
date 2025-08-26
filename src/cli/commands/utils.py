"""
Utility functions for CLI commands.
"""

from rich.console import Console
from rich.table import Table
from typing import List, Dict

console = Console()

def print_command_help(title: str, description: str, commands: List[Dict[str, str]]):
    """Prints a standardized help table for a command group."""
    console.print(f"\n[bold blue]{title}[/bold blue]")
    console.print(description)
    
    table = Table(title=f"{title} Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Example Usage", style="yellow")

    for command in commands:
        table.add_row(command["name"], command["description"], command["example"])

    console.print(table)

