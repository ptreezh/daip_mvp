# -*- coding: utf-8 -*-
"""@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : proposal_commands.py
@Description: Edit proposal management commands for the DAIP-LIVE CLI.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="Edit proposal management commands.")

@app.command(name="list")
def list_proposals():
    """List all pending edit proposals."""
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # List pending proposals
    try:
        proposals = wiki_service.list_pending_proposals()
        if proposals:
            typer.echo(f"Pending edit proposals ({len(proposals)}):")
            for proposal in proposals:
                typer.echo(f"  Entry: {proposal['entry_name']}")
                typer.echo(f"    Proposal ID: {proposal['proposal_id']}")
                typer.echo(f"    Author: {proposal['author']}")
                typer.echo(f"    Timestamp: {proposal['timestamp']}")
                typer.echo(f"    Summary: {proposal['change_summary']}")
                typer.echo()
        else:
            typer.echo("No pending edit proposals found.")
    except Exception as e:
        typer.echo(f"Error listing edit proposals: {e}")
        raise typer.Exit(1)


@app.command(name="reject")
def reject_proposal(
    entry_name: str = typer.Argument(..., help="The name of the wiki entry."),
    proposal_id: str = typer.Argument(..., help="The ID of the edit proposal to reject."),
):
    """Reject an edit proposal."""
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Reject the edit proposal
    try:
        success = wiki_service.reject(entry_name, proposal_id)
        if success:
            typer.echo(f"Successfully rejected proposal '{proposal_id}' for entry '{entry_name}'.")
        else:
            typer.echo(f"Failed to reject proposal '{proposal_id}' for entry '{entry_name}'.")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error rejecting edit proposal: {e}")
        raise typer.Exit(1)