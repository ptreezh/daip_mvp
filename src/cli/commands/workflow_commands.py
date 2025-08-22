"""
Workflow management commands for the DAIP CLI.
"""

import json
import asyncio
import typer
from rich.console import Console
from rich.table import Table

from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.workflow_engine import WorkflowEngine

# Initialize console for rich output
console = Console()

# Create workflow management app
workflow_app = typer.Typer(help="Workflow and primitive management commands.")

@workflow_app.command("list")
def list_workflows():
    """
    List all available workflows (institutional primitives).
    """
    try:
        registry = PrimitiveRegistry()
        primitives = registry.list_primitives()

        if not primitives:
            console.print("[yellow]No workflows (primitives) are currently registered.[/yellow]")
            return

        table = Table(title="Available Workflows (Primitives)")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Type", style="magenta")

        for primitive_info in primitives:
            table.add_row(
                primitive_info.name,
                primitive_info.description,
                primitive_info.type
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)

@workflow_app.command("create")
def create_workflow(
    definition_file: typer.FileText = typer.Option(
        ..., 
        "--definition-file", 
        help="Path to the workflow definition JSON file.",
        exists=True, 
        file_okay=True, 
        dir_okay=False, 
        readable=True
    )
):
    """
    Create and register a new workflow from a definition file.
    """
    try:
        # Parse the JSON file
        try:
            workflow_def = json.load(definition_file)
        except json.JSONDecodeError:
            console.print("[red]Error: Invalid JSON in definition file.[/red]")
            raise typer.Exit(code=1)

        registry = PrimitiveRegistry()

        # Validate the workflow definition
        try:
            registry.validate_primitive(workflow_def)
        except ValueError as e:
            console.print(f"[red]Workflow validation failed: {e}[/red]")
            raise typer.Exit(code=1)

        # Register the workflow
        success = registry.register_primitive(workflow_def)

        if success:
            workflow_name = workflow_def.get("name", "Unknown")
            console.print(f"[green]Successfully validated and registered workflow '{workflow_name}'[/green]")
        else:
            console.print("[red]Error: Failed to register workflow.[/red]")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)

@workflow_app.command("execute")
def execute_workflow(
    name: str = typer.Argument(..., help="The name of the workflow to execute."),
    params: str = typer.Option("{}", "--params", help="JSON string of parameters for the workflow.")
):
    """
    Execute a workflow.
    """
    try:
        # Parse parameters
        try:
            workflow_params = json.loads(params)
        except json.JSONDecodeError:
            console.print("[red]Error: Invalid JSON format for --params.[/red]")
            raise typer.Exit(code=1)

        registry = PrimitiveRegistry()
        workflow_def = registry.get_primitive(name)

        if not workflow_def:
            console.print(f"[red]Error: Workflow '{name}' not found.[/red]")
            raise typer.Exit(code=1)

        # Run the async execution
        async def main():
            engine = WorkflowEngine(registry)
            execution_id = await engine.execute_workflow(workflow_def, workflow_params)
            return execution_id

        execution_id = asyncio.run(main())

        if execution_id:
            console.print(f"[green]Workflow '{name}' started successfully.[/green]")
            console.print(f"[green]Execution ID: {execution_id}[/green]")
        else:
            console.print(f"[red]Error: Failed to start workflow '{name}'.[/red]")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)
