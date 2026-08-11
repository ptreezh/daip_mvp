"""
知识管理CLI命令
遵循TDD原则 - 基于测试需求实现
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ...core.models import KnowledgeBaseConfig, ProviderConfig
from ...knowledge.manager import KnowledgeManager
from ...persistence.database import DatabaseManager
from ..utils.error_handler import ErrorHandler
from ..utils.performance_monitor import PerformanceMonitor


def _execute_default_behavior(
    query: Optional[str] = None, sync: bool = False, search_opt: Optional[str] = None
):
    """
    执行默认行为：当没有子命令时
    """
    import asyncio

    # 决定执行哪个操作
    if query is not None or search_opt is not None:
        # 执行搜索
        search_query = query if query is not None else search_opt
        asyncio.run(_search_knowledge_default(search_query))
    elif sync is True:
        # 明确要求同步
        asyncio.run(_sync_knowledge_default())
    else:
        # 默认同步（没有参数或显式 sync=True）
        asyncio.run(_sync_knowledge_default())


def _build_knowledge_manager() -> tuple[KnowledgeManager, str]:
    """从 config.yaml 构造持久化 DB + 真实 embedding 的 KnowledgeManager（S4-1）。

    修复：此前 CLI 层用 :memory: DB + MockModelProvider，导致元数据永不落盘
    （knowledge_sources 恒为 0）且 sync 每次全量重摄入、搜索恒为空壳。
    """
    import os

    import yaml

    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        knowledge_dir = config_data.get("knowledge_base", {}).get("directory", "docs/")
        embedding_model = config_data.get("llm_provider", {}).get(
            "embedding_model", "ollama/nomic-embed-text"
        )
        db_path = config_data.get("database", {}).get("path", "daip_live.db")
    else:
        knowledge_dir = "docs/"
        embedding_model = "ollama/nomic-embed-text"
        db_path = "daip_live.db"

    # 测试隔离环境变量（S4-1/Phase2）：与 p7_gui 的 DAIP_DB_PATH 机制一致
    db_path = os.environ.get("DAIP_DB_PATH") or db_path
    knowledge_dir = os.environ.get("DAIP_KNOWLEDGE_DIR") or knowledge_dir

    knowledge_config = KnowledgeBaseConfig(directory=knowledge_dir)
    db_manager = DatabaseManager(db_path=db_path)
    # 延迟 import：避免模块级连带加载 litellm（CLI 冷启动优化 2026-08-10）
    from ...model_provider.provider import LiteLLMProvider

    provider_config = ProviderConfig(
        model=embedding_model,
        provider="ollama",
        embedding_model=embedding_model,
        base_url="http://localhost:11434",
    )
    model_provider = LiteLLMProvider(provider_config)
    return (
        KnowledgeManager(
            db_manager=db_manager,
            model_provider=model_provider,
            config=knowledge_config,
        ),
        db_path,
    )


# Create the knowledge command app
app = typer.Typer(
    name="knowledge",
    help="Manage knowledge base and document search in the DAIP-LIVE system",
    rich_markup_mode="rich",
)


@app.callback(invoke_without_command=True)
def _knowledge_root_callback(ctx: typer.Context):
    """根入口：无子命令时默认同步。

    注：Typer 不支持 `knowledge <query>` 裸参数（会被当作未知子命令名拒绝）；
    搜索请用显式子命令 `knowledge search <query>` 或 `knowledge auto <query>`。
    历史上此处曾尝试用 ctx.args 支持裸参数，但 Typer 在回调前即拒绝未知命令。
    """
    if ctx.invoked_subcommand is None:
        import asyncio

        asyncio.run(_sync_knowledge_default())


# Define a default command that can be called explicitly
@app.command("auto")
def auto_cmd(
    query: Optional[str] = typer.Argument(
        None,
        help="Search query. If provided, performs search. If not provided, syncs by default.",  # noqa: E501
    ),
    sync: bool = typer.Option(
        None,
        "--sync/--no-sync",
        help="Force sync operation (mutually exclusive with search)",
    ),
    search_opt: Optional[str] = typer.Option(
        None, "--search", "-s", help="Search query (alternative to positional argument)"
    ),
):
    """
    Default behavior for knowledge command (sync if no query, search if query)
    """
    _execute_default_behavior(query=query, sync=sync is True, search_opt=search_opt)


# Create an alias command for the default behavior
@app.command("default", hidden=True)
def default_cmd(
    query: Optional[str] = typer.Argument(
        None,
        help="Search query. If provided, performs search. If not provided, syncs by default.",  # noqa: E501
    ),
    sync: bool = typer.Option(
        None,
        "--sync/--no-sync",
        help="Force sync operation (mutually exclusive with search)",
    ),
    search_opt: Optional[str] = typer.Option(
        None, "--search", "-s", help="Search query (alternative to positional argument)"
    ),
):
    """
    Alias for auto command - provides the same default behavior
    """
    _execute_default_behavior(query=query, sync=sync is True, search_opt=search_opt)


# Create instances
console = Console()
error_handler = ErrorHandler()


async def _sync_knowledge_default():
    """默认同步函数"""
    perf_monitor = PerformanceMonitor()
    async with perf_monitor.measure_command("knowledge_sync"):
        console.print("[bold blue]📚 Synchronizing knowledge base...[/bold blue]")

        try:
            # 持久 DB + 真实 embedding（S4-1）
            knowledge_manager, _ = _build_knowledge_manager()

            # Actual sync (without dry_run or verbose for default)
            console.print(
                f"[dim]Scanning knowledge directory for changes: {knowledge_manager.config.directory}[/dim]"  # noqa: E501
            )

            # Run the actual sync
            sync_result = await knowledge_manager.sync_knowledge_base()

            # Rich output
            _display_sync_summary(sync_result, False)

        except Exception as e:
            console.print(f"[red]❌ Error syncing knowledge base: {str(e)}[/red]")
            raise


async def _search_knowledge_default(query: str):
    """默认搜索函数"""
    perf_monitor = PerformanceMonitor()
    async with perf_monitor.measure_command("knowledge_search"):
        console.print(
            f"[bold blue]🔍 Searching knowledge base for: {query}[/bold blue]"
        )

        try:
            # 真实检索（S4-2：删除空壳，接 KnowledgeManager.search）
            knowledge_manager, _ = _build_knowledge_manager()
            search_results = await knowledge_manager.search(query, top_k=10)

            # Display formatted search results
            _display_search_results(query, search_results, 10)

        except Exception as e:
            console.print(f"[red]❌ Error searching knowledge base: {str(e)}[/red]")
            raise


@app.command()
def sync(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show what would be synced without making changes",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output in JSON format"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed sync information"
    ),
):
    """Synchronize the knowledge base with document files"""

    @error_handler.handle_command_errors(command_name="knowledge sync")
    async def _sync_knowledge():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("knowledge_sync"):
            if not json_output:
                console.print(
                    "[bold blue]📚 Synchronizing knowledge base...[/bold blue]"
                )

            try:
                # 持久 DB + 真实 embedding（S4-1）
                knowledge_manager, _ = _build_knowledge_manager()

                if dry_run:
                    # Dry run mode - only show what would change
                    if not json_output:
                        console.print(
                            "[yellow]🔍 DRY RUN MODE - No changes will be made[/yellow]"
                        )
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            console=console,
                            transient=True,
                        ) as progress:
                            task = progress.add_task(
                                "Scanning for changes...", total=None
                            )

                            # Get changes without making actual changes
                            changes = knowledge_manager._scan_and_detect_changes()
                            progress.update(task, completed=True)

                        console.print("[dim]Files that would be processed:[/dim]")
                        for f in changes.added[:5]:  # Show first 5
                            console.print(f"  📄 [green]+ {f}[/green]")
                        if len(changes.added) > 5:
                            console.print(f"  ... and {len(changes.added) - 5} more")

                        for f in changes.updated[:5]:  # Show first 5
                            file_path, _ = f
                            console.print(f"  🔄 [yellow]~ {file_path}[/yellow]")
                        if len(changes.updated) > 5:
                            console.print(f"  ... and {len(changes.updated) - 5} more")

                        for f in changes.deleted[:5]:  # Show first 5
                            console.print(f"  🗑️  [red]- {f.file_path}[/red]")
                        if len(changes.deleted) > 5:
                            console.print(f"  ... and {len(changes.deleted) - 5} more")

                    # JSON output for dry run
                    dry_run_data = {
                        "dry_run": True,
                        "changes": {
                            "added": changes.added if hasattr(changes, "added") else [],
                            "updated": [f[0] for f in changes.updated]
                            if hasattr(changes, "updated")
                            else [],
                            "deleted": [f.file_path for f in changes.deleted]
                            if hasattr(changes, "deleted")
                            else [],
                            "unchanged": len(changes.unchanged)
                            if hasattr(changes, "unchanged")
                            else 0,
                        },
                        "summary": {
                            "total_changes": len(changes.added)
                            + len(changes.updated)
                            + len(changes.deleted)
                            if hasattr(changes, "added")
                            and hasattr(changes, "updated")
                            and hasattr(changes, "deleted")
                            else 0
                        },
                    }
                    console.print(json.dumps(dry_run_data, indent=2))
                    return

                # Actual sync
                if not json_output and verbose:
                    console.print(
                        f"[dim]Scanning knowledge directory for changes: {knowledge_manager.config.directory}[/dim]"  # noqa: E501
                    )

                # Run the actual sync
                sync_result = await knowledge_manager.sync_knowledge_base()

                if json_output:
                    # JSON output
                    output_data = {
                        "sync_complete": True,
                        "summary": sync_result,
                        "timestamp": "2025-11-13T11:45:00Z",
                    }
                    console.print(json.dumps(output_data, indent=2))
                else:
                    # Rich output
                    _display_sync_summary(sync_result, verbose)

            except Exception as e:
                if json_output:
                    error_data = {"error": str(e), "error_type": type(e).__name__}
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(
                        f"[red]❌ Error syncing knowledge base: {str(e)}[/red]"
                    )
                raise

    # Run the async function
    import asyncio

    asyncio.run(_sync_knowledge())


def _display_sync_summary(summary: dict[str, int], verbose: bool = False):
    """Display sync summary in formatted way"""

    total_changes = summary["added"] + summary["updated"] + summary["removed"]

    if total_changes == 0:
        console.print("[green]✅ Knowledge base is up to date[/green]")
        if summary["unchanged"] > 0:
            console.print(
                f"[dim]No changes needed. {summary['unchanged']} documents unchanged.[/dim]"  # noqa: E501
            )
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
    ),
):
    """Show knowledge base status and statistics"""

    @error_handler.handle_command_errors(command_name="knowledge status")
    async def _show_status():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("knowledge_status"):
            if not json_output:
                console.print(
                    "[bold blue]📊 Getting knowledge base status...[/bold blue]"
                )

            try:
                # 真实状态（S4-2：从持久 DB 与索引读取，替换 mock 硬编码）
                knowledge_manager, _ = _build_knowledge_manager()
                sources = knowledge_manager.db_manager.get_all_knowledge_sources()
                total_documents = len(sources)
                indexed_documents = (
                    knowledge_manager.faiss_index.ntotal
                    if knowledge_manager.faiss_index
                    else 0
                )
                pending_documents = max(0, total_documents - indexed_documents)
                total_size_mb = sum(
                    Path(s.file_path).stat().st_size
                    for s in sources
                    if Path(s.file_path).exists()
                ) / (1024 * 1024)

                if json_output:
                    status_data = {
                        "knowledge_base": {
                            "directory": knowledge_manager.config.directory,
                            "total_documents": total_documents,
                            "indexed_documents": indexed_documents,
                            "pending_documents": pending_documents,
                            "total_size_mb": total_size_mb,
                            "last_sync": None,
                        }
                    }
                    console.print(json.dumps(status_data, indent=2))
                else:
                    # Display formatted status
                    _display_knowledge_status(
                        directory=knowledge_manager.config.directory,
                        total_documents=total_documents,
                        indexed_documents=indexed_documents,
                        pending_documents=pending_documents,
                        total_size_mb=total_size_mb,
                    )

            except Exception as e:
                if json_output:
                    error_data = {"error": str(e), "error_type": type(e).__name__}
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(
                        f"[red]❌ Error getting knowledge status: {str(e)}[/red]"
                    )
                raise

    import asyncio

    asyncio.run(_show_status())


def _display_knowledge_status(
    directory: str,
    total_documents: int,
    indexed_documents: int,
    pending_documents: int,
    total_size_mb: float,
):
    """Display knowledge base status in formatted way"""

    # Create panel with status information
    content_lines = [
        f"[bold]Directory:[/bold] {directory}",
        f"[bold]Total Documents:[/bold] {total_documents}",
        f"[bold]Indexed Documents:[/bold] {indexed_documents}",
        f"[bold]Pending Documents:[/bold] {pending_documents}",
        f"[bold]Total Size:[/bold] {total_size_mb:.2f} MB",
    ]

    content = "\n".join(content_lines)

    panel = Panel(
        content,
        title="[bold green]Knowledge Base Status[/bold green]",
        border_style="green",
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
    ),
):
    """Search the knowledge base for documents matching the query"""

    @error_handler.handle_command_errors(command_name="knowledge search")
    async def _search_knowledge():
        perf_monitor = PerformanceMonitor()
        async with perf_monitor.measure_command("knowledge_search"):
            if not json_output:
                console.print(
                    f"[bold blue]🔍 Searching knowledge base for: {query}[/bold blue]"
                )

            try:
                # 真实检索（S4-2）
                knowledge_manager, _ = _build_knowledge_manager()
                search_results = await knowledge_manager.search(query, top_k=limit)

                if json_output:
                    search_data = {
                        "query": query,
                        "results": search_results,
                        "total_found": len(search_results),
                        "limit": limit,
                    }
                    console.print(json.dumps(search_data, indent=2))
                else:
                    # Display formatted search results
                    _display_search_results(query, search_results, limit)

            except Exception as e:
                if json_output:
                    error_data = {"error": str(e), "error_type": type(e).__name__}
                    console.print(json.dumps(error_data, indent=2))
                else:
                    console.print(
                        f"[red]❌ Error searching knowledge base: {str(e)}[/red]"
                    )
                raise

    import asyncio

    asyncio.run(_search_knowledge())


def _display_search_results(query: str, results: list[dict], limit: int):
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
