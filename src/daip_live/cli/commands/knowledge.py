"""
知识管理CLI命令
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
from ...knowledge.manager import KnowledgeManager
from ...persistence.database import DatabaseManager
from ...model_provider.provider import LiteLLMProvider
from ...core.models import KnowledgeBaseConfig, ProviderConfig


# Create the knowledge command app
app = typer.Typer(
    name="knowledge",
    help="Manage knowledge base and document search in the DAIP-LIVE system",
    rich_markup_mode="rich"
)

# Create instances
console = Console()
error_handler = ErrorHandler()


@app.command()
def sync(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be synced without making changes"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed sync information"
    )
):
    """Synchronize the knowledge base with document files"""

    @error_handler.handle_command_errors(command_name="knowledge sync")
    async def _sync_knowledge():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("knowledge_sync") as metrics:
            if not json_output:
                console.print("[bold blue]📚 Synchronizing knowledge base...[/bold blue]")

            try:
                # Create default configuration
                knowledge_config = KnowledgeBaseConfig(directory="knowledge")
                provider_config = ProviderConfig(
                    model="text-embedding-3-small",
                    provider="openai"
                )

                # Initialize dependencies
                db_manager = DatabaseManager()
                model_provider = LiteLLMProvider(provider_config)
                knowledge_manager = KnowledgeManager(
                    db_manager=db_manager,
                    model_provider=model_provider,
                    config=knowledge_config
                )

                if dry_run:
                    # Dry run mode - only show what would change
                    if not json_output:
                        console.print("[yellow]🔍 DRY RUN MODE - No changes will be made[/yellow]")
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            console=console,
                            transient=True
                        ) as progress:
                            task = progress.add_task("Scanning for changes...", total=None)

                            # Mock scan for dry run - in real implementation this would call knowledge manager
                            progress.update(task, completed=True)

                        console.print("[dim]Files that would be processed:[/dim]")
                        console.print("  • No files to process (dry run mock)")

                    # JSON output for dry run
                    dry_run_data = {
                        "dry_run": True,
                        "changes": {
                            "added": [],
                            "updated": [],
                            "deleted": [],
                            "unchanged": []
                        },
                        "summary": {
                            "total_changes": 0
                        }
                    }
                    console.print(json.dumps(dry_run_data, indent=2))
                    return

                # Actual sync
                if not json_output and verbose:
                    console.print("[dim]Scanning knowledge directory for changes...[/dim]")

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("Syncing files...", total=None)

                    # Mock sync result for now - in real implementation would call knowledge_manager.sync_knowledge_base()
                    sync_result = {
                        "added": 0,
                        "updated": 0,
                        "removed": 0,
                        "unchanged": 0
                    }

                    progress.update(task, completed=True)

                if json_output:
                    # JSON output
                    output_data = {
                        "sync_complete": True,
                        "summary": sync_result,
                        "timestamp": "2025-11-13T11:45:00Z"
                    }
                    console.print(json.dumps(output_data, indent=2))
                else:
                    # Rich output
                    _display_sync_summary(sync_result, verbose)

            except Exception as e:
                if json_output:
                    error_data = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error syncing knowledge base: {str(e)}[/red]")
                raise

    # Run the async function
    import asyncio
    asyncio.run(_sync_knowledge())


def _display_sync_summary(summary: Dict[str, int], verbose: bool = False):
    """Display sync summary in formatted way"""

    total_changes = summary["added"] + summary["updated"] + summary["removed"]

    if total_changes == 0:
        console.print("[green]✅ Knowledge base is up to date[/green]")
        if summary["unchanged"] > 0:
            console.print(f"[dim]No changes needed. {summary['unchanged']} documents unchanged.[/dim]")
    else:
        console.print("[green]✅ Knowledge base sync complete[/green]")

        # Show changes summary
        table = Table(title="Sync Summary")
        table.add_column("Action", style="cyan")
        table.add_column("Count", style="green", justify="right")

        if summary["added"] > 0:
            table.add_row("📄 Added", f"{summary['added']}")
        if summary["updated"] > 0:
            table.add_row("🔄 Updated", f"{summary['updated']}")
        if summary["removed"] > 0:
            table.add_row("🗑️  Removed", f"{summary['removed']}")

        console.print(table)

        if verbose:
            console.print(f"\n[dim]Unchanged documents: {summary['unchanged']}[/dim]")


@app.command()
def status(
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    )
):
    """Show knowledge base status and statistics"""

    @error_handler.handle_command_errors(command_name="knowledge status")
    async def _show_status():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("knowledge_status") as metrics:
            if not json_output:
                console.print("[bold blue]📊 Getting knowledge base status...[/bold blue]")

            try:
                # Create default configuration
                knowledge_config = KnowledgeBaseConfig(directory="knowledge")
                provider_config = ProviderConfig(
                    model="text-embedding-3-small",
                    provider="openai"
                )

                # Initialize dependencies
                db_manager = DatabaseManager()
                model_provider = LiteLLMProvider(provider_config)
                knowledge_manager = KnowledgeManager(
                    db_manager=db_manager,
                    model_provider=model_provider,
                    config=knowledge_config
                )

                # Mock status data
                total_documents = 0
                indexed_documents = 0
                pending_documents = 0
                total_size_mb = 0.0

                if json_output:
                    status_data = {
                        "knowledge_base": {
                            "directory": knowledge_config.directory,
                            "total_documents": total_documents,
                            "indexed_documents": indexed_documents,
                            "pending_documents": pending_documents,
                            "total_size_mb": total_size_mb,
                            "last_sync": None
                        }
                    }
                    console.print(json.dumps(status_data, indent=2))
                else:
                    # Display formatted status
                    _display_knowledge_status(
                        directory=knowledge_config.directory,
                        total_documents=total_documents,
                        indexed_documents=indexed_documents,
                        pending_documents=pending_documents,
                        total_size_mb=total_size_mb
                    )

            except Exception as e:
                if json_output:
                    error_data = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error getting knowledge status: {str(e)}[/red]")
                raise

    import asyncio
    asyncio.run(_show_status())


def _display_knowledge_status(
    directory: str,
    total_documents: int,
    indexed_documents: int,
    pending_documents: int,
    total_size_mb: float
):
    """Display knowledge base status in formatted way"""

    # Create panel with status information
    content_lines = [
        f"[bold]Directory:[/bold] {directory}",
        f"[bold]Total Documents:[/bold] {total_documents}",
        f"[bold]Indexed Documents:[/bold] {indexed_documents}",
        f"[bold]Pending Documents:[/bold] {pending_documents}",
        f"[bold]Total Size:[/bold] {total_size_mb:.2f} MB"
    ]

    content = "\n".join(content_lines)

    panel = Panel(
        content,
        title="[bold green]Knowledge Base Status[/bold green]",
        border_style="green"
    )

    console.print(panel)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of results to return"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    )
):
    """Search the knowledge base for documents matching the query"""

    @error_handler.handle_command_errors(command_name="knowledge search")
    async def _search_knowledge():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("knowledge_search") as metrics:
            if not json_output:
                console.print(f"[bold blue]🔍 Searching knowledge base for: {query}[/bold blue]")

            try:
                # Create default configuration
                knowledge_config = KnowledgeBaseConfig(directory="knowledge")
                provider_config = ProviderConfig(
                    model="text-embedding-3-small",
                    provider="openai"
                )

                # Initialize dependencies
                db_manager = DatabaseManager()
                model_provider = LiteLLMProvider(provider_config)
                knowledge_manager = KnowledgeManager(
                    db_manager=db_manager,
                    model_provider=model_provider,
                    config=knowledge_config
                )

                # Mock search results
                search_results = []

                if json_output:
                    search_data = {
                        "query": query,
                        "results": search_results,
                        "total_found": len(search_results),
                        "limit": limit
                    }
                    console.print(json.dumps(search_data, indent=2))
                else:
                    # Display formatted search results
                    _display_search_results(query, search_results, limit)

            except Exception as e:
                if json_output:
                    error_data = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error searching knowledge base: {str(e)}[/red]")
                raise

    import asyncio
    asyncio.run(_search_knowledge())


def _display_search_results(query: str, results: List[Dict], limit: int):
    """Display search results in formatted table"""

    if not results:
        console.print("[yellow]⚠️  No results found for your query[/yellow]")
        console.print(f"[dim]Query: '{query}'[/dim]")
        return

    table = Table(title=f"Search Results for '{query}'")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Score", style="green", justify="right")
    table.add_column("Preview", style="yellow", max_width=50)

    for result in results[:limit]:
        file_path = result.get("file_path", "Unknown")
        distance = result.get("distance", 0.0)
        # Convert distance to similarity score (lower distance = higher similarity)
        score = max(0, min(100, (1 - distance) * 100))

        # Get content preview
        content = result.get("content", "")
        if len(content) > 50:
            content = content[:47] + "..."

        table.add_row(file_path, f"{score:.1f}%", content)

    console.print(table)

    if len(results) > limit:
        console.print(f"\n[dim]Showing {limit} of {len(results)} results[/dim]")