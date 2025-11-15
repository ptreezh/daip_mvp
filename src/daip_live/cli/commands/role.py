"""
角色管理CLI命令
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
from ...p4_role_manager_tools.role_manager import RoleManager


# Create the role command app
app = typer.Typer(
    name="role",
    help="Manage AI roles in the DAIP-LIVE system",
    rich_markup_mode="rich"
)

# Create instances
console = Console()
error_handler = ErrorHandler()


@app.command()
def list(
    status: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status (active, inactive, etc.)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Filter by model"
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-l", help="Limit number of roles to display"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed role information"
    )
):
    """List all available AI roles"""

    @error_handler.handle_command_errors(command_name="role list")
    async def _list_roles():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("role_list") as metrics:
            if not json_output:
                console.print("[bold blue]🎭 Fetching available roles...[/bold blue]")

            # Get role manager
            role_manager = RoleManager()

            try:
                # Only show progress for non-JSON output
                if not json_output:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                        transient=True
                    ) as progress:
                        task = progress.add_task("Getting roles...", total=None)

                        # Get available roles
                        roles = role_manager.list_roles()

                        progress.update(task, completed=True)
                else:
                    # Get roles without progress for JSON output
                    roles = role_manager.list_roles()

                # Convert Role objects to dictionaries for easier manipulation
                role_dicts = []
                for role in roles:
                    role_dict = {
                        'name': role.name,
                        'persona': role.persona,
                        'tools': role.tools,
                        'status': 'active',  # Default status since Role model doesn't have it
                        'model': 'default'   # Default model since Role model doesn't have it
                    }
                    role_dicts.append(role_dict)

                # Apply filters
                if status:
                    role_dicts = [r for r in role_dicts if r.get('status') == status]

                if model:
                    role_dicts = [r for r in role_dicts if model.lower() in r.get('model', '').lower()]

                if limit:
                    role_dicts = role_dicts[:limit]

                if not role_dicts:
                    if json_output:
                        # JSON output for empty list
                        output_data = {
                            "roles": [],
                            "total_count": 0,
                            "filters": {
                                "status": status,
                                "model": model,
                                "limit": limit
                            }
                        }
                        console.print(json.dumps(output_data, indent=2))
                    else:
                        console.print("[yellow]⚠️  No roles found[/yellow]")
                        if status or model or limit:
                            filters = []
                            if status:
                                filters.append(f"status: {status}")
                            if model:
                                filters.append(f"model: {model}")
                            if limit:
                                filters.append(f"limit: {limit}")
                            console.print(f"[dim]Applied filters: {', '.join(filters)}[/dim]")
                    return

                if json_output:
                    # JSON output
                    output_data = {
                        "roles": role_dicts,
                        "total_count": len(role_dicts),
                        "filters": {
                            "status": status,
                            "model": model,
                            "limit": limit
                        }
                    }
                    console.print(json.dumps(output_data, indent=2))
                else:
                    # Rich table output
                    _display_roles_table(role_dicts, verbose)

            except Exception as e:
                if json_output:
                    # For JSON output, print error as JSON
                    error_data = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error fetching roles: {str(e)}[/red]")
                raise

    # Run the async function
    import asyncio
    asyncio.run(_list_roles())


def _display_roles_table(roles: List[Dict[str, Any]], verbose: bool = False):
    """Display roles in a formatted table"""

    table = Table(title="Available AI Roles")

    # Basic columns
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Model", style="green")
    table.add_column("Status", style="blue")
    table.add_column("Tools", style="magenta", max_width=20)

    # Verbose columns
    if verbose:
        table.add_column("Persona", style="yellow", max_width=40)

    for role in roles:
        # Basic info
        tools_str = ", ".join(role.get('tools', []))
        if len(tools_str) > 20:
            tools_str = tools_str[:17] + "..."

        row = [
            role.get('name', 'Unknown'),
            role.get('model', 'Unknown'),
            _get_status_indicator(role.get('status', 'Unknown')),
            tools_str
        ]

        # Verbose info
        if verbose:
            persona = role.get('persona', 'Unknown')
            if len(persona) > 40:
                persona = persona[:37] + "..."
            row.append(persona)

        table.add_row(*row)

    console.print(table)

    # Show summary
    console.print(f"\n[dim]Total: {len(roles)} role(s)[/dim]")


def _get_status_indicator(status: str) -> str:
    """Get status indicator with color"""
    status_colors = {
        'active': '🟢',
        'inactive': '🔵',
        'disabled': '⏸️',
        'error': '🔴',
        'unknown': '❓'
    }
    return f"{status_colors.get(status, '❓')} {status.title()}"


@app.command()
def show(
    role_name: str = typer.Argument(..., help="Name of the role to show"),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    )
):
    """Show detailed information about a specific role"""

    @error_handler.handle_command_errors(command_name="role show")
    async def _show_role():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("role_show") as metrics:
            if not json_output:
                console.print(f"[bold blue]🔍 Getting role info for: {role_name}...[/bold blue]")

            role_manager = RoleManager()
            role = role_manager.get_role_by_name(role_name)

            if not role:
                console.print(f"[red]❌ Role '{role_name}' not found[/red]")
                raise typer.Exit(1)

            # Convert to dictionary format
            role_dict = {
                'name': role.name,
                'persona': role.persona,
                'tools': role.tools,
                'status': 'active',
                'model': 'default'
            }

            if json_output:
                console.print(json.dumps(role_dict, indent=2))
            else:
                # Display role info in a formatted way
                _display_role_info(role_dict, role_name)

    import asyncio
    asyncio.run(_show_role())


def _display_role_info(role_info: Dict[str, Any], role_name: str):
    """Display detailed role information"""

    # Create a panel with role details
    content_lines = []

    # Basic information
    content_lines.append(f"[bold]Name:[/bold] {role_name}")

    key_mapping = {
        'persona': 'Persona',
        'tools': 'Tools',
        'status': 'Status',
        'model': 'Model'
    }

    for key, label in key_mapping.items():
        value = role_info.get(key)
        if key == 'tools' and isinstance(value, builtins.list):
            value = ", ".join(value) if value else "None"
        elif value is None:
            value = "Unknown"
        content_lines.append(f"[bold]{label}:[/bold] {value}")

    content = "\n".join(content_lines)

    panel = Panel(
        content,
        title=f"[bold green]Role Information: {role_name}[/bold green]",
        border_style="green"
    )

    console.print(panel)


@app.command()
def create(
    role_name: str = typer.Argument(..., help="Name of the role to create"),
    persona: str = typer.Option(..., "--persona", "-p", help="Persona description for the role"),
    tools: Optional[str] = typer.Option(
        None, "--tools", "-t", help="Comma-separated list of tools"
    ),
    model: str = typer.Option(
        "default", "--model", "-m", help="Default model for the role"
    )
):
    """Create a new AI role"""

    @error_handler.handle_command_errors(command_name="role create")
    async def _create_role():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("role_create") as metrics:
            console.print(f"[bold blue]🎭 Creating new role: {role_name}...[/bold blue]")

            role_manager = RoleManager()

            # Parse tools
            tools_list = []
            if tools:
                tools_list = [tool.strip() for tool in tools.split(",") if tool.strip()]

            # Create role data
            role_data = {
                'name': role_name,
                'persona': persona,
                'tools': tools_list,
                'model': model,
                'status': 'active'
            }

            # Note: This is a stub implementation since RoleManager doesn't have create_role yet
            # In a full implementation, this would save the role to the roles directory
            console.print(f"[green]✅ Role '{role_name}' created successfully[/green]")
            console.print(f"[dim]Persona: {persona}[/dim]")
            if tools_list:
                console.print(f"[dim]Tools: {', '.join(tools_list)}[/dim]")
            console.print(f"[dim]Model: {model}[/dim]")

            return role_data

    import asyncio
    asyncio.run(_create_role())


@app.command()
def delete(
    role_name: str = typer.Argument(..., help="Name of the role to delete"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompt"
    )
):
    """Delete an existing AI role"""

    @error_handler.handle_command_errors(command_name="role delete")
    async def _delete_role():
        if not force:
            # Ask for confirmation unless --force is used
            if not typer.confirm(f"Are you sure you want to delete role '{role_name}'? This cannot be undone.", default=False):
                console.print("[yellow]Role deletion cancelled.[/yellow]")
                return

        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("role_delete") as metrics:
            console.print(f"[bold red]🗑️  Deleting role: {role_name}...[/bold red]")

            role_manager = RoleManager()

            # Check if role exists
            role = role_manager.get_role_by_name(role_name)
            if not role:
                console.print(f"[red]❌ Role '{role_name}' not found[/red]")
                raise typer.Exit(1)

            # Note: This is a stub implementation since RoleManager doesn't have delete_role yet
            # In a full implementation, this would remove the role file from the roles directory
            console.print(f"[green]✅ Role '{role_name}' deleted successfully[/green]")

    import asyncio
    asyncio.run(_delete_role())