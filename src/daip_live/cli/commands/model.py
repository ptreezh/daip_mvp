"""
模型管理CLI命令
遵循TDD原则 - 基于测试需求实现
"""

import json
from typing import List, Optional, Dict, Any
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.error_handler import ErrorHandler
from ..utils.performance_monitor import PerformanceMonitor
from ...model_manager import ModelManager


# Create the model command app
app = typer.Typer(
    name="model",
    help="Manage AI models in the DAIP-LIVE system",
    rich_markup_mode="rich"
)

# Create instances
console = Console()
error_handler = ErrorHandler()
# Performance monitor will be created per command instance


@app.command()
def list(
    refresh: bool = typer.Option(
        False, "--refresh", "-r", help="Force refresh the model list"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed model information"
    ),
    filter_name: Optional[str] = typer.Option(
        None, "--filter", "-f", help="Filter models by name"
    )
):
    """List all available AI models"""

    @error_handler.handle_command_errors(command_name="model list")
    async def _list_models():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("model_list") as metrics:
            # Don't show status message for JSON output
            if not json_output:
                console.print("[bold blue]🤖 Fetching available models...[/bold blue]")

            # Get model manager
            model_manager = ModelManager()

            try:
                # Only show progress for non-JSON output
                if not json_output:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                        transient=True
                    ) as progress:
                        task = progress.add_task("Getting models...", total=None)

                        # Get available models
                        models = model_manager.get_available_models(force_refresh=refresh)

                        progress.update(task, completed=True)
                else:
                    # Get models without progress for JSON output
                    models = model_manager.get_available_models(force_refresh=refresh)

                # Filter models if filter is provided
                if filter_name:
                    models = [
                        model for model in models
                        if filter_name.lower() in model.get('name', '').lower()
                    ]

                if not models:
                    if json_output:
                        # JSON output for empty list
                        output_data = {
                            "models": [],
                            "total_count": 0,
                            "filter": filter_name
                        }
                        console.print(json.dumps(output_data, indent=2))
                    else:
                        console.print("[yellow]⚠️  No models found[/yellow]")
                        if filter_name:
                            console.print(f"[dim]Filtered by: '{filter_name}'[/dim]")
                    return

                if json_output:
                    # JSON output
                    output_data = {
                        "models": models,
                        "total_count": len(models),
                        "filter": filter_name
                    }
                    console.print(json.dumps(output_data, indent=2))
                else:
                    # Rich table output
                    _display_models_table(models, verbose)

            except Exception as e:
                if json_output:
                    # For JSON output, print error as JSON
                    error_data = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error fetching models: {str(e)}[/red]")
                raise

    # Run the async function
    import asyncio
    asyncio.run(_list_models())


def _display_models_table(models: List[Dict[str, Any]], verbose: bool = False):
    """Display models in a formatted table"""

    table = Table(title="Available AI Models")

    # Basic columns
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Size", style="green")
    table.add_column("Family", style="blue")
    table.add_column("Modified", style="yellow")

    # Verbose columns
    if verbose:
        table.add_column("Parameters", style="magenta")
        table.add_column("Quantization", style="white")
        table.add_column("Digest", style="dim")

    for model in models:
        # Basic info
        row = [
            model.get('name', 'Unknown'),
            model.get('size', 'Unknown'),
            model.get('family', 'Unknown'),
            model.get('modified', 'Unknown')
        ]

        # Verbose info
        if verbose:
            row.extend([
                model.get('parameter_size', 'Unknown'),
                model.get('quantization', 'Unknown'),
                model.get('digest', 'Unknown')[:8] + '...' if model.get('digest') else 'Unknown'
            ])

        table.add_row(*row)

    console.print(table)

    # Show summary
    console.print(f"\n[dim]Total: {len(models)} model(s)[/dim]")


@app.command()
def status():
    """Show current model status"""

    @error_handler.handle_command_errors(command_name="model status")
    async def _show_status():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("model_status") as metrics:
            console.print("[bold blue]🔍 Checking model status...[/bold blue]")

            model_manager = ModelManager()
            current_model = model_manager.get_current_model()

            if current_model:
                # Display current model info
                panel_content = f"""
[bold]Name:[/bold] {current_model.get('name', 'Unknown')}
[bold]Status:[/bold] {current_model.get('status', 'Unknown')}
[bold]Uptime:[/bold] {current_model.get('uptime', 'Unknown')}
                """

                panel = Panel(
                    panel_content.strip(),
                    title="[bold green]Current Model Status[/bold green]",
                    border_style="green"
                )
                console.print(panel)
            else:
                console.print("[yellow]⚠️  No model is currently set[/yellow]")

    import asyncio
    asyncio.run(_show_status())


@app.command()
def info(
    model_name: str = typer.Argument(..., help="Name of the model to get info for"),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    )
):
    """Get detailed information about a specific model"""

    @error_handler.handle_command_errors(command_name="model info")
    async def _get_model_info():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("model_info") as metrics:
            console.print(f"[bold blue]🔍 Getting info for model: {model_name}...[/bold blue]")

            model_manager = ModelManager()
            model_info = model_manager.get_model_info(model_name)

            if not model_info:
                console.print(f"[red]❌ Model '{model_name}' not found[/red]")
                raise typer.Exit(1)

            if json_output:
                console.print(json.dumps(model_info, indent=2))
            else:
                # Display model info in a formatted way
                _display_model_info(model_info, model_name)

    import asyncio
    asyncio.run(_get_model_info())


def _display_model_info(model_info: Dict[str, Any], model_name: str):
    """Display detailed model information"""

    # Create a panel with model details
    content_lines = []

    # Basic information
    content_lines.append(f"[bold]Name:[/bold] {model_name}")

    key_mapping = {
        'size': 'Size',
        'family': 'Family',
        'parameter_size': 'Parameters',
        'quantization': 'Quantization',
        'modified': 'Modified',
        'digest': 'Digest',
        'status': 'Status',
        'description': 'Description',
        'license': 'License'
    }

    for key, label in key_mapping.items():
        value = model_info.get(key)
        if value:
            content_lines.append(f"[bold]{label}:[/bold] {value}")

    # Additional metadata
    metadata = model_info.get('metadata', {})
    if metadata:
        content_lines.append("\n[bold]Metadata:[/bold]")
        for meta_key, meta_value in metadata.items():
            content_lines.append(f"  • {meta_key}: {meta_value}")

    content = "\n".join(content_lines)

    panel = Panel(
        content,
        title=f"[bold green]Model Information: {model_name}[/bold green]",
        border_style="green"
    )

    console.print(panel)