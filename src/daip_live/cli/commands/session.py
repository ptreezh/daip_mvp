"""
会话管理CLI命令
遵循TDD原则 - 基于测试需求实现
"""

import json
import builtins
from typing import List, Optional, Dict, Any
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.error_handler import ErrorHandler
from ..utils.performance_monitor import PerformanceMonitor
from ...memory.session_manager import SessionManager
from ...persistence.database import DatabaseManager


# Create the session command app
app = typer.Typer(
    name="session",
    help="Manage conversation sessions in the DAIP-LIVE system",
    rich_markup_mode="rich"
)

# Create instances
console = Console()
error_handler = ErrorHandler()


@app.command()
def list(
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed session information"
    ),
    session_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by session type (debate, chat, workflow, etc.)"
    ),
    status: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status (active, completed, paused, etc.)"
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Limit number of sessions to display"
    )
):
    """List all conversation sessions"""

    @error_handler.handle_command_errors(command_name="session list")
    async def _list_sessions():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("session_list") as metrics:
            if not json_output:
                console.print("[bold blue]📋 Fetching conversation sessions...[/bold blue]")

            # Get database and session manager
            db_manager = DatabaseManager()
            session_manager = SessionManager(db_manager)

            try:
                if not json_output:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                        transient=True
                    ) as progress:
                        task = progress.add_task("Getting sessions...", total=None)

                        # Get all sessions
                        sessions = session_manager.list_sessions()

                        progress.update(task, completed=True)
                else:
                    # Get sessions without progress for JSON output
                    sessions = session_manager.list_sessions()

                # Apply filters
                if session_type:
                    sessions = [s for s in sessions if s.get('session_type') == session_type]

                if status:
                    sessions = [s for s in sessions if s.get('status') == status]

                if limit:
                    sessions = sessions[:limit]

                if not sessions:
                    if json_output:
                        # JSON output for empty list
                        output_data = {
                            "sessions": [],
                            "total_count": 0,
                            "filters": {
                                "type": session_type,
                                "status": status,
                                "limit": limit
                            }
                        }
                        console.print(json.dumps(output_data, indent=2))
                    else:
                        console.print("[yellow]⚠️  No sessions found[/yellow]")
                        if session_type or status or limit:
                            filters = []
                            if session_type:
                                filters.append(f"type: {session_type}")
                            if status:
                                filters.append(f"status: {status}")
                            if limit:
                                filters.append(f"limit: {limit}")
                            console.print(f"[dim]Applied filters: {', '.join(filters)}[/dim]")
                    return

                if json_output:
                    # JSON output
                    # Convert datetime objects to strings for JSON serialization
                    json_sessions = []
                    for session in sessions:
                        json_session = session.copy()
                        if 'created_at' in json_session:
                            json_session['created_at'] = json_session['created_at'].isoformat()
                        json_sessions.append(json_session)

                    output_data = {
                        "sessions": json_sessions,
                        "total_count": len(json_sessions),
                        "filters": {
                            "type": session_type,
                            "status": status,
                            "limit": limit
                        }
                    }
                    console.print(json.dumps(output_data, indent=2))
                else:
                    # Rich table output
                    _display_sessions_table(sessions, verbose)

            except Exception as e:
                if json_output:
                    # For JSON output, print error as JSON
                    error_data = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error fetching sessions: {str(e)}[/red]")
                raise

    # Run the async function
    import asyncio
    asyncio.run(_list_sessions())


def _display_sessions_table(sessions: List[Dict[str, Any]], verbose: bool = False):
    """Display sessions in a formatted table"""

    table = Table(title="Conversation Sessions")

    # Basic columns
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Type", style="green")
    table.add_column("Goal", style="blue", max_width=30)
    table.add_column("Status", style="yellow")
    table.add_column("Turns", style="magenta")
    table.add_column("Created", style="white")

    # Verbose columns
    if verbose:
        table.add_column("Participants", style="cyan")
        table.add_column("Updated", style="white")

    for session in sessions:
        # Basic info
        row = [
            session.get('id', 'Unknown')[:12],  # Truncate long IDs
            session.get('session_type', 'Unknown'),
            session.get('goal', 'Unknown')[:30],  # Truncate long goals
            _get_status_indicator(session.get('status', 'Unknown')),
            str(session.get('turn_count', 0)),
            _format_datetime(session.get('created_at'))
        ]

        # Verbose info
        if verbose:
            participants = session.get('participant_ids', [])
            participant_count = len(participants) if isinstance(participants, builtins.list) else 0
            row.extend([
                f"{participant_count} participants",
                _format_datetime(session.get('updated_at'))
            ])

        table.add_row(*row)

    console.print(table)

    # Show summary
    active_count = len([s for s in sessions if s.get('status') == 'active'])
    console.print(f"\n[dim]Total: {len(sessions)} session(s)")
    if active_count > 0:
        console.print(f"[dim]Active: {active_count}[/dim]")


def _get_status_indicator(status: str) -> str:
    """Get status indicator with color"""
    status_colors = {
        'active': '🟢',
        'completed': '🔵',
        'paused': '⏸️',
        'error': '🔴',
        'unknown': '❓'
    }
    return f"{status_colors.get(status, '❓')} {status.title()}"


def _format_datetime(dt_obj) -> str:
    """Format datetime object for display"""
    if not dt_obj:
        return "Unknown"

    if hasattr(dt_obj, 'strftime'):
        return dt_obj.strftime("%Y-%m-%d %H:%M")

    return str(dt_obj)


@app.command()
def clear(
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompt"
    )
):
    """Clear all conversation sessions"""

    @error_handler.handle_command_errors(command_name="session clear")
    async def _clear_sessions():
        if not force:
            # Ask for confirmation unless --force is used
            if not typer.confirm("Are you sure you want to clear all conversation sessions? This cannot be undone.", default=False):
                console.print("[yellow]Session clearing cancelled.[/yellow]")
                return

        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("session_clear") as metrics:
            console.print("[bold red]🗑️  Clearing all conversation sessions...[/bold red]")

            # Get database and session manager
            db_manager = DatabaseManager()
            session_manager = SessionManager(db_manager)

            try:
                # Clear all sessions
                cleared_count = session_manager.clear_all_sessions()

                if cleared_count == 0:
                    console.print("[yellow]ℹ️  No sessions to clear. Database is already empty.[/yellow]")
                else:
                    console.print(f"[green]✅ Successfully cleared {cleared_count} session(s)[/green]")
                    console.print(f"[dim]All conversation history has been removed.[/dim]")

            except Exception as e:
                console.print(f"[red]❌ Error clearing sessions: {str(e)}[/red]")
                raise

    # Run the async function
    import asyncio
    asyncio.run(_clear_sessions())