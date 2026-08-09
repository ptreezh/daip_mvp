"""
Wiki CLI命令
遵循TDD原则 - 基于测试需求实现
"""

import builtins
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...core.models import ProviderConfig
from ...model_provider.provider import LiteLLMProvider
from ...wiki.manager import WikiManager
from ..utils.error_handler import ErrorHandler
from ..utils.performance_monitor import PerformanceMonitor

# Create the wiki command app
app = typer.Typer(
    name="wiki",
    help="Manage wiki pages in the DAIP-LIVE system",
    rich_markup_mode="rich",
)

# Create instances
console = Console()
error_handler = ErrorHandler()


@app.command()
def create(
    title: str = typer.Argument(..., help="Wiki page title"),
    content: str = typer.Option(
        "", "--content", "-c", help="Initial content for the page"
    ),
    tags: Optional[str] = typer.Option(
        None, "--tags", "-t", help="Comma-separated tags for the page"
    ),
):
    """Create a new wiki page"""

    @error_handler.handle_command_errors(command_name="wiki create")
    async def _create_wiki_page():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("wiki_create"):
            console.print(f"[bold blue]📝 Creating wiki page: {title}[/bold blue]")

            try:
                # Load config from YAML or use defaults
                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    wiki_dir = config_data.get("wiki", {}).get("directory", "wiki/")
                else:
                    wiki_dir = "wiki/"

                # Create configuration
                wiki_path = Path(wiki_dir)
                wiki_path.mkdir(parents=True, exist_ok=True)

                # Initialize database manager and providers
                try:
                    from daip_live.p4_role_manager_tools.role_model_manager import (
                        RoleModelManager,
                    )
                    from daip_live.persistence.database import DatabaseManager

                    DatabaseManager(":memory:")  # Using in-memory for CLI

                    # Create roles directory if it doesn't exist
                    roles_path = Path("roles")
                    roles_path.mkdir(exist_ok=True)

                    role_model_manager = RoleModelManager(
                        roles_dir_path=str(roles_path)
                    )
                    provider_config = ProviderConfig(
                        model="mock-model", provider="mock"
                    )
                    model_provider = LiteLLMProvider(provider_config)
                except Exception:
                    # Fallback for initial implementation
                    role_model_manager = None
                    model_provider = None

                wiki_manager = WikiManager(
                    wiki_root=wiki_path,
                    role_model_manager=role_model_manager,
                    model_provider=model_provider,
                )

                # Process tags
                tag_list = None
                if tags:
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

                # Process content to handle escaped characters that may have been passed from CLI  # noqa: E501
                content_to_use = content
                if content_to_use:
                    # On Windows command line, when user types \\n, it becomes literal \\n in the parameter  # noqa: E501
                    # We need to convert these literal escape sequences to actual characters  # noqa: E501
                    content_to_use = (
                        content_to_use.replace("\\\\n", "\n")
                        .replace("\\\\t", "\t")
                        .replace("\\\\r", "\r")
                    )
                    # Also handle single escape sequences that might occur
                    content_to_use = (
                        content_to_use.replace("\\n", "\n")
                        .replace("\\t", "\t")
                        .replace("\\r", "\r")
                    )

                if not content_to_use:
                    content_to_use = f"# {title}\n\n开始协同创建关于 {title} 的维基页面...\n\n创建时间: {Path.home()}\n"  # noqa: E501

                # Create the wiki page
                page = wiki_manager.create_page(
                    title=title, content=content_to_use, tags=tag_list
                )

                console.print(
                    f"[green]✅ Wiki page '{page.title}' created successfully![/green]"
                )
                console.print(f"[dim]Location: {page.file_path}[/dim]")

                if tag_list:
                    console.print(f"[dim]Tags: {', '.join(tag_list)}[/dim]")

            except Exception as e:
                console.print(f"[red]❌ Error creating wiki page: {str(e)}[/red]")
                raise

    # Run the async function
    import asyncio

    asyncio.run(_create_wiki_page())


@app.command()
def list(
    limit: int = typer.Option(
        20, "--limit", "-l", help="Maximum number of pages to show"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
):
    """List all wiki pages"""

    @error_handler.handle_command_errors(command_name="wiki list")
    async def _list_wiki_pages():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("wiki_list"):
            if not json_output:
                console.print("[bold blue]📋 Listing wiki pages...[/bold blue]")

            try:
                # Load config from YAML or use defaults
                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    wiki_dir = config_data.get("wiki", {}).get("directory", "wiki/")
                else:
                    wiki_dir = "wiki/"

                # Create configuration
                wiki_path = Path(wiki_dir)
                if not wiki_path.exists():
                    if json_output:
                        console.print(json.dumps({"pages": [], "total": 0}))
                    else:
                        console.print(
                            "[yellow]⚠️  No wiki directory exists yet[/yellow]"
                        )
                        console.print(
                            "[dim]Create a page with 'daip wiki create' first[/dim]"
                        )
                    return

                # Initialize database manager and providers
                try:
                    from daip_live.p4_role_manager_tools.role_model_manager import (
                        RoleModelManager,
                    )
                    from daip_live.persistence.database import DatabaseManager

                    DatabaseManager(":memory:")  # Using in-memory for CLI

                    # Create roles directory if it doesn't exist
                    roles_path = Path("roles")
                    roles_path.mkdir(exist_ok=True)

                    role_model_manager = RoleModelManager(
                        roles_dir_path=str(roles_path)
                    )
                    provider_config = ProviderConfig(
                        model="mock-model", provider="mock"
                    )
                    model_provider = LiteLLMProvider(provider_config)
                except Exception:
                    # Fallback for initial implementation
                    role_model_manager = None
                    model_provider = None

                wiki_manager = WikiManager(
                    wiki_root=wiki_path,
                    role_model_manager=role_model_manager,
                    model_provider=model_provider,
                )

                # Get all pages
                all_pages = wiki_manager.list_all_pages()

                if json_output:
                    pages_data = []
                    for page in all_pages[:limit]:
                        pages_data.append(
                            {
                                "title": page.title,
                                "file_path": str(page.file_path),
                                "created_at": page.created_at.isoformat(),
                                "modified_at": page.modified_at.isoformat(),
                                "tags": page.tags,
                                "word_count": page.get_word_count(),
                            }
                        )

                    output_data = {
                        "pages": pages_data,
                        "total": len(all_pages),
                        "limit": limit,
                    }
                    console.print(json.dumps(output_data, indent=2, default=str))
                else:
                    # Display formatted list
                    _display_wiki_pages(all_pages[:limit], len(all_pages))

            except Exception as e:
                if json_output:
                    error_data = {"error": str(e), "error_type": type(e).__name__}
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error listing wiki pages: {str(e)}[/red]")
                raise

    import asyncio

    asyncio.run(_list_wiki_pages())


def _display_wiki_pages(pages: builtins.list, total_count: int):
    """Display wiki pages in a formatted table"""

    if not pages:
        console.print("[yellow]⚠️  No wiki pages found[/yellow]")
        return

    table = Table(title="Wiki Pages")
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Tags", style="yellow")
    table.add_column("Size", style="green", justify="right")
    table.add_column("Modified", style="dim")

    for page in pages:
        tags_str = ", ".join(page.tags) if page.tags else "None"
        size_str = f"{page.get_word_count()} words"
        modified_str = page.modified_at.strftime("%Y-%m-%d %H:%M")

        table.add_row(page.title, tags_str, size_str, modified_str)

    console.print(table)

    if total_count > len(pages):
        console.print(f"\n[dim]Showing {len(pages)} of {total_count} pages[/dim]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    by_content: bool = typer.Option(
        True, "--content", "-c", help="Search in content (default)"
    ),
    by_tag: bool = typer.Option(
        False, "--tag", "-t", help="Search by tag instead of content"
    ),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of results to return"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
):
    """Search wiki pages for content or tags"""

    @error_handler.handle_command_errors(command_name="wiki search")
    async def _search_wiki_pages():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("wiki_search"):
            if not json_output:
                console.print(
                    f"[bold blue]🔍 Searching wiki pages for: {query}[/bold blue]"
                )

            try:
                # Load config from YAML or use defaults
                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    wiki_dir = config_data.get("wiki", {}).get("directory", "wiki/")
                else:
                    wiki_dir = "wiki/"

                # Create configuration
                wiki_path = Path(wiki_dir)
                if not wiki_path.exists():
                    if json_output:
                        console.print(json.dumps({"results": [], "total": 0}))
                    else:
                        console.print(
                            "[yellow]⚠️  No wiki directory exists yet[/yellow]"
                        )
                        console.print(
                            "[dim]Create a page with 'daip wiki create' first[/dim]"
                        )
                    return

                # Initialize database manager and providers
                try:
                    from daip_live.p4_role_manager_tools.role_model_manager import (
                        RoleModelManager,
                    )
                    from daip_live.persistence.database import DatabaseManager

                    DatabaseManager(":memory:")  # Using in-memory for CLI

                    # Create roles directory if it doesn't exist
                    roles_path = Path("roles")
                    roles_path.mkdir(exist_ok=True)

                    role_model_manager = RoleModelManager(
                        roles_dir_path=str(roles_path)
                    )
                    provider_config = ProviderConfig(
                        model="mock-model", provider="mock"
                    )
                    model_provider = LiteLLMProvider(provider_config)
                except Exception:
                    # Fallback for initial implementation
                    role_model_manager = None
                    model_provider = None

                wiki_manager = WikiManager(
                    wiki_root=wiki_path,
                    role_model_manager=role_model_manager,
                    model_provider=model_provider,
                )

                # Perform search
                if by_tag:
                    results = wiki_manager.search_pages_by_tag(query)
                else:
                    results = wiki_manager.search_pages_by_content(query)

                if json_output:
                    results_data = []
                    for page in results[:limit]:
                        results_data.append(
                            {
                                "title": page.title,
                                "file_path": str(page.file_path),
                                "created_at": page.created_at.isoformat(),
                                "modified_at": page.modified_at.isoformat(),
                                "tags": page.tags,
                                "word_count": page.get_word_count(),
                            }
                        )

                    output_data = {
                        "query": query,
                        "results": results_data,
                        "total_found": len(results),
                        "limit": limit,
                        "search_type": "tag" if by_tag else "content",
                    }
                    console.print(json.dumps(output_data, indent=2, default=str))
                else:
                    # Display formatted search results
                    _display_search_results(
                        query, results[:limit], len(results), by_tag
                    )

            except Exception as e:
                if json_output:
                    error_data = {"error": str(e), "error_type": type(e).__name__}
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error searching wiki pages: {str(e)}[/red]")
                raise

    import asyncio

    asyncio.run(_search_wiki_pages())


def _display_search_results(
    query: str, results: builtins.list, total_count: int, by_tag: bool
):
    """Display search results in formatted table"""

    if not results:
        console.print("[yellow]⚠️  No results found for your query[/yellow]")
        console.print(
            f"[dim]Search: '{query}' ({'by tag' if by_tag else 'by content'})[/dim]"
        )
        return

    table = Table(
        title=f"Search Results for '{query}' ({'by tag' if by_tag else 'by content'})"
    )
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Tags", style="yellow", max_width=30)
    table.add_column("Size", style="green", justify="right")
    table.add_column("Modified", style="dim")

    for page in results:
        tags_str = ", ".join(page.tags) if page.tags else "None"
        size_str = f"{page.get_word_count()} words"
        modified_str = page.modified_at.strftime("%Y-%m-%d %H:%M")

        table.add_row(page.title, tags_str, size_str, modified_str)

    console.print(table)

    if total_count > len(results):
        console.print(f"\n[dim]Showing {len(results)} of {total_count} results[/dim]")


@app.command()
def show(
    title: str = typer.Argument(..., help="Wiki page title to show"),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
):
    """Show content of a specific wiki page"""

    @error_handler.handle_command_errors(command_name="wiki show")
    async def _show_wiki_page():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("wiki_show"):
            if not json_output:
                console.print(f"[bold blue]📖 Showing wiki page: {title}[/bold blue]")

            try:
                # Load config from YAML or use defaults
                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    wiki_dir = config_data.get("wiki", {}).get("directory", "wiki/")
                else:
                    wiki_dir = "wiki/"

                # Create configuration
                wiki_path = Path(wiki_dir)
                if not wiki_path.exists():
                    console.print("[yellow]⚠️  No wiki directory exists yet[/yellow]")
                    return

                # Initialize database manager and providers
                try:
                    from daip_live.p4_role_manager_tools.role_model_manager import (
                        RoleModelManager,
                    )
                    from daip_live.persistence.database import DatabaseManager

                    DatabaseManager(":memory:")  # Using in-memory for CLI

                    # Create roles directory if it doesn't exist
                    roles_path = Path("roles")
                    roles_path.mkdir(exist_ok=True)

                    role_model_manager = RoleModelManager(
                        roles_dir_path=str(roles_path)
                    )
                    provider_config = ProviderConfig(
                        model="mock-model", provider="mock"
                    )
                    model_provider = LiteLLMProvider(provider_config)
                except Exception:
                    # Fallback for initial implementation
                    role_model_manager = None
                    model_provider = None

                wiki_manager = WikiManager(
                    wiki_root=wiki_path,
                    role_model_manager=role_model_manager,
                    model_provider=model_provider,
                )

                # Get the specific page
                page = wiki_manager.get_page_by_title(title)

                if not page:
                    if json_output:
                        console.print(
                            json.dumps(
                                {
                                    "error": f"Page '{title}' not found",
                                    "page_exists": False,
                                }
                            )
                        )
                    else:
                        console.print(f"[red]❌ Page '{title}' not found[/red]")
                    return

                if json_output:
                    output_data = {
                        "title": page.title,
                        "content": page.content,
                        "file_path": str(page.file_path),
                        "created_at": page.created_at.isoformat(),
                        "modified_at": page.modified_at.isoformat(),
                        "tags": page.tags,
                        "word_count": page.get_word_count(),
                    }
                    console.print(json.dumps(output_data, indent=2, default=str))
                else:
                    # Display formatted page content
                    _display_wiki_page(page)

            except Exception as e:
                if json_output:
                    error_data = {"error": str(e), "error_type": type(e).__name__}
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error showing wiki page: {str(e)}[/red]")
                raise

    import asyncio

    asyncio.run(_show_wiki_page())


def _display_wiki_page(page):
    """Display a wiki page with formatted information"""

    # Create panel with page information
    info_lines = [
        f"[bold]Title:[/bold] {page.title}",
        f"[bold]File:[/bold] {page.file_path}",
        f"[bold]Created:[/bold] {page.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"[bold]Modified:[/bold] {page.modified_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"[bold]Size:[/bold] {page.get_word_count()} words, ~{page.get_reading_time()} min read",  # noqa: E501
    ]

    if page.tags:
        info_lines.append(f"[bold]Tags:[/bold] {', '.join(page.tags)}")

    info_content = "\n".join(info_lines)

    panel = Panel(
        info_content,
        title="[bold green]Page Information[/bold green]",
        border_style="green",
    )

    console.print(panel)

    console.print("\n[underline]Content:[/underline]")
    # Decode content if it's bytes to ensure proper encoding handling
    content_to_display = page.content
    if isinstance(content_to_display, bytes):
        content_to_display = content_to_display.decode("utf-8")
    # Process escape sequences for display in case they weren't handled during creation
    content_to_display = (
        content_to_display.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\r", "\r")
    )
    console.print(content_to_display)


@app.command()
def delete(
    title: str = typer.Argument(..., help="Wiki page title to delete"),
    confirm: bool = typer.Option(
        True, "--confirm/--no-confirm", "-y/-n", help="Confirm deletion"
    ),
):
    """Delete a wiki page"""

    @error_handler.handle_command_errors(command_name="wiki delete")
    async def _delete_wiki_page():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("wiki_delete"):
            console.print(f"[bold red]🗑️  Deleting wiki page: {title}[/bold red]")

            if confirm:
                confirm_input = input(
                    f"Are you sure you want to delete '{title}'? This cannot be undone. (y/N): "  # noqa: E501
                )
                if confirm_input.lower() != "y":
                    console.print("[yellow]❌ Deletion cancelled[/yellow]")
                    return

            try:
                # Load config from YAML or use defaults
                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    wiki_dir = config_data.get("wiki", {}).get("directory", "wiki/")
                else:
                    wiki_dir = "wiki/"

                # Create configuration
                wiki_path = Path(wiki_dir)
                if not wiki_path.exists():
                    console.print("[yellow]⚠️  No wiki directory exists yet[/yellow]")
                    return

                # Initialize database manager and providers
                try:
                    from daip_live.p4_role_manager_tools.role_model_manager import (
                        RoleModelManager,
                    )
                    from daip_live.persistence.database import DatabaseManager

                    DatabaseManager(":memory:")  # Using in-memory for CLI

                    # Create roles directory if it doesn't exist
                    roles_path = Path("roles")
                    roles_path.mkdir(exist_ok=True)

                    role_model_manager = RoleModelManager(
                        roles_dir_path=str(roles_path)
                    )
                    provider_config = ProviderConfig(
                        model="mock-model", provider="mock"
                    )
                    model_provider = LiteLLMProvider(provider_config)
                except Exception:
                    # Fallback for initial implementation
                    role_model_manager = None
                    model_provider = None

                wiki_manager = WikiManager(
                    wiki_root=wiki_path,
                    role_model_manager=role_model_manager,
                    model_provider=model_provider,
                )

                # Delete the page
                success = wiki_manager.delete_page(title)

                if success:
                    console.print(
                        f"[green]✅ Wiki page '{title}' deleted successfully![/green]"
                    )
                else:
                    console.print(f"[red]❌ Page '{title}' not found[/red]")

            except Exception as e:
                console.print(f"[red]❌ Error deleting wiki page: {str(e)}[/red]")
                raise

    import asyncio

    asyncio.run(_delete_wiki_page())


@app.command()
def stats(
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
):
    """Show wiki statistics"""

    @error_handler.handle_command_errors(command_name="wiki stats")
    async def _show_wiki_stats():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("wiki_stats"):
            if not json_output:
                console.print("[bold blue]📊 Getting wiki statistics...[/bold blue]")

            try:
                # Load config from YAML or use defaults
                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    wiki_dir = config_data.get("wiki", {}).get("directory", "wiki/")
                else:
                    wiki_dir = "wiki/"

                # Create configuration
                wiki_path = Path(wiki_dir)
                if not wiki_path.exists():
                    if json_output:
                        console.print(json.dumps({"stats": {}}))
                    else:
                        console.print(
                            "[yellow]⚠️  No wiki directory exists yet[/yellow]"
                        )
                        console.print(
                            "[dim]Create a page with 'daip wiki create' first[/dim]"
                        )
                    return

                # Initialize database manager and providers
                try:
                    from daip_live.p4_role_manager_tools.role_model_manager import (
                        RoleModelManager,
                    )
                    from daip_live.persistence.database import DatabaseManager

                    DatabaseManager(":memory:")  # Using in-memory for CLI

                    # Create roles directory if it doesn't exist
                    roles_path = Path("roles")
                    roles_path.mkdir(exist_ok=True)

                    role_model_manager = RoleModelManager(
                        roles_dir_path=str(roles_path)
                    )
                    provider_config = ProviderConfig(
                        model="mock-model", provider="mock"
                    )
                    model_provider = LiteLLMProvider(provider_config)
                except Exception:
                    # Fallback for initial implementation
                    role_model_manager = None
                    model_provider = None

                wiki_manager = WikiManager(
                    wiki_root=wiki_path,
                    role_model_manager=role_model_manager,
                    model_provider=model_provider,
                )

                # Get statistics
                stats = wiki_manager.get_statistics()

                if json_output:
                    stats_data = {
                        "total_pages": stats.total_pages,
                        "total_tags": stats.total_tags,
                        "total_words": stats.total_words,
                        "last_updated": stats.last_updated.isoformat(),
                        "most_used_tags": stats.most_used_tags,
                        "pages_by_reading_time": stats.pages_by_reading_time,
                    }
                    console.print(json.dumps(stats_data, indent=2, default=str))
                else:
                    # Display formatted statistics
                    _display_wiki_stats(stats)

            except Exception as e:
                if json_output:
                    error_data = {"error": str(e), "error_type": type(e).__name__}
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(f"[red]❌ Error getting wiki stats: {str(e)}[/red]")
                raise

    import asyncio

    asyncio.run(_show_wiki_stats())


def _display_wiki_stats(stats):
    """Display wiki statistics in a formatted panel"""

    # Create panel with stats information
    content_lines = [
        f"[bold]Total Pages:[/bold] {stats.total_pages}",
        f"[bold]Total Tags:[/bold] {stats.total_tags}",
        f"[bold]Total Words:[/bold] {stats.total_words:,}",
        f"[bold]Last Updated:[/bold] {stats.last_updated.strftime('%Y-%m-%d %H:%M:%S')}",  # noqa: E501
    ]

    # Add top tags if available
    if stats.most_used_tags:
        top_tags = ", ".join(
            [f"{tag}({count})" for tag, count in stats.most_used_tags[:5]]
        )
        content_lines.append(f"[bold]Top Tags:[/bold] {top_tags}")

    content = "\n".join(content_lines)

    panel = Panel(
        content, title="[bold green]Wiki Statistics[/bold green]", border_style="green"
    )

    console.print(panel)


@app.command()
def export(
    output_dir: str = typer.Argument(..., help="Directory to export wiki pages to"),
    format: str = typer.Option(
        "markdown", "--format", "-f", help="Export format (markdown or json)"
    ),
):
    """Export all wiki pages to a directory"""

    @error_handler.handle_command_errors(command_name="wiki export")
    async def _export_wiki_pages():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("wiki_export"):
            console.print(
                f"[bold blue]📤 Exporting wiki pages to: {output_dir}[/bold blue]"
            )
            console.print(f"[dim]Format: {format}[/dim]")

            try:
                # Load config from YAML or use defaults
                import yaml

                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path, encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    wiki_dir = config_data.get("wiki", {}).get("directory", "wiki/")
                else:
                    wiki_dir = "wiki/"

                # Create configuration
                wiki_path = Path(wiki_dir)
                if not wiki_path.exists():
                    console.print("[yellow]⚠️  No wiki directory exists yet[/yellow]")
                    return

                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)

                # Initialize database manager and providers
                try:
                    from daip_live.p4_role_manager_tools.role_model_manager import (
                        RoleModelManager,
                    )
                    from daip_live.persistence.database import DatabaseManager

                    DatabaseManager(":memory:")  # Using in-memory for CLI

                    # Create roles directory if it doesn't exist
                    roles_path = Path("roles")
                    roles_path.mkdir(exist_ok=True)

                    role_model_manager = RoleModelManager(
                        roles_dir_path=str(roles_path)
                    )
                    provider_config = ProviderConfig(
                        model="mock-model", provider="mock"
                    )
                    model_provider = LiteLLMProvider(provider_config)
                except Exception:
                    # Fallback for initial implementation
                    role_model_manager = None
                    model_provider = None

                wiki_manager = WikiManager(
                    wiki_root=wiki_path,
                    role_model_manager=role_model_manager,
                    model_provider=model_provider,
                )

                # Export pages
                wiki_manager.export_pages(output_path, format=format)

                console.print("[green]✅ Wiki pages exported successfully![/green]")
                console.print(
                    f"[dim]Format: {format}, Output: {output_path.absolute()}[/dim]"
                )

            except Exception as e:
                console.print(f"[red]❌ Error exporting wiki pages: {str(e)}[/red]")
                raise

    import asyncio

    asyncio.run(_export_wiki_pages())
