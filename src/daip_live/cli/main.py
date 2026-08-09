"""
CLI module for the DAIP-LIVE system.

This module provides command-line interfaces for the enhanced debate system and other features.
It follows the module-first design principle and integrates with the container system.
"""  # noqa: E501

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

# Patch click.termui before typer imports it (fix for click 8.x compatibility)
try:
    import shutil

    import click.termui

    # get_terminal_size was removed from click.termui in click 8.x
    if not hasattr(click.termui, "get_terminal_size"):
        click.termui.get_terminal_size = shutil.get_terminal_size
except ImportError:
    pass

import typer

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.table import Table

from daip_live.agent_engine.enhanced_intent_recognizer import (
    EnhancedIntentRecognizer,
    Intent,
)
from daip_live.container import Container
from daip_live.core.models import (
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
    ErrorEvent,
    FinalResponseEvent,
    ThoughtEvent,
    TodoItem,
    TokenUsageEvent,
)
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.tui_modular import DAIP_TUI

# Create CLI app
app = typer.Typer()

# Container for dependency injection
container = Container()


@app.command()
def run():
    """启动DAIP-TUI界面"""
    try:
        tui = DAIP_TUI()
        tui.run()
    except ImportError:
        pass


# Create debate sub-app
debate_app = typer.Typer()
app.add_typer(debate_app, name="debate", help="辩论相关命令")


@debate_app.command("start")
def debate_start(
    topic: str = typer.Argument(..., help="辩论主题"),
    roles: str = typer.Option(
        "pro_arguer,con_arguer", help="参与辩论的角色，用逗号分隔"
    ),
    rounds: int = typer.Option(1, help="辩论轮次"),
):
    """开始辩论"""

    async def run_debate_async():
        console = Console()
        role_list = [r.strip() for r in roles.split(",") if r.strip()]

        # 真实辩论管理器（容器装配：角色模型映射 + 模型可用性检查）
        debate_manager = container.enhanced_debate_manager()
        debate_history_tracker = container.debate_history_tracker()

        console.print(f"[bold]Starting debate on topic:[/bold] {topic}")
        console.print(f"[bold]Roles:[/bold] {roles}")
        console.print(f"[bold]Rounds:[/bold] {rounds}")

        # Generate session ID for debate tracking
        session_id = f"debate_{int(time.time())}"

        # Track debate in history at start
        start_event = DebateStartEvent(
            topic=topic, roles=role_list, rounds=rounds, session_id=session_id
        )
        await debate_history_tracker.start_tracking(start_event)

        # Run debate and capture events
        async for event in debate_manager.run_debate(topic, role_list, rounds):
            if isinstance(event, DebateStartEvent):
                console.print("🎮 Debate started!")
                # Show model assignments
                summary = debate_manager.get_debate_model_summary(role_list)
                if "model_assignments" in summary:
                    console.print("Model assignments:")
                    for role_name, config in summary.get(
                        "model_assignments", {}
                    ).items():
                        console.print(
                            f"  {role_name} → {config.get('model', 'unknown')}"
                        )

            elif isinstance(event, DebateRoundStartEvent):
                console.print(f"\n🔄 [bold]Round {event.round_number}[/bold] started")
            elif isinstance(event, DebateTurnCompleteEvent):
                console.print(f"🗣️ [bold]{event.participant}[/bold] speaking...")
                console.print(f"💬 {event.content_preview}")
            elif isinstance(event, TokenUsageEvent):
                console.print(
                    f"📈 Tokens: {event.usage_info.get('total_tokens', 'N/A')}"
                )
            elif isinstance(event, ThoughtEvent):
                console.print(f"💭 {event.content}")
            elif isinstance(event, DebateCompleteEvent):
                console.print("✅ Debate completed!")
                if event.summary:
                    console.print(f"📝 {event.summary}")

    try:
        asyncio.run(run_debate_async())
    except Exception:
        pass


@debate_app.command("multimodel")
def debate_multimodel(
    topic: str = typer.Argument(..., help="辩论主题"),
    roles: str = typer.Option(
        "economist,laborer,policymaker", help="参与辩论的角色，用逗号分隔"
    ),
    rounds: int = typer.Option(1, help="辩论轮次"),
):
    """开始多模型辩论（每个角色使用不同模型）"""

    async def run_multimodel_debate_async():
        # Get components from container
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        role_model_manager = container.role_model_manager()
        model_provider = container.model_provider()
        debate_history_tracker = container.debate_history_tracker()

        # Create enhanced debate manager with history tracking
        debate_manager = EnhancedDebateManager(
            session_manager=session_manager,
            role_manager=role_manager,
            role_model_manager=role_model_manager,
            model_provider=model_provider,
            debate_history_tracker=debate_history_tracker,
            use_optimized_architecture=True,
        )

        console = Console()
        role_list = roles.split(",")
        console.print(f"[bold]Starting multi-model debate on topic:[/bold] {topic}")
        console.print(f"[bold]Roles:[/bold] {roles}")
        console.print(f"[bold]Rounds:[/bold] {rounds}")

        # Check for unavailable roles
        available_mappings = []
        unavailable_roles = []
        for role_name in role_list:
            role = role_manager.get_role_by_name(role_name.strip())
            if role:
                available_mappings.append(role_name.strip())
            else:
                unavailable_roles.append(role_name.strip())

        if unavailable_roles:
            console.print(
                "[yellow]Warning: Following roles not found in system, will use default model:[/yellow]"  # noqa: E501
            )
            for role in unavailable_roles:
                console.print(f"  - {role}")

        console.print("🤖 Multi-model debate started!")

        # Get debate model summary and show assignments
        summary = debate_manager.get_debate_model_summary(role_list)
        if "model_assignments" in summary:
            console.print("Model assignments:")
            for role_name, config in summary.get("model_assignments", {}).items():
                model_name = config.get("model", "unknown")
                console.print(f"  {role_name} → {model_name}")

        # Track debate in history
        start_event = DebateStartEvent(topic=topic, roles=role_list, rounds=rounds)
        await debate_history_tracker.start_tracking(start_event)

        # Run debate and capture events
        async for event in debate_manager.run_debate(topic, role_list, rounds):
            if isinstance(event, DebateStartEvent):
                console.print("🎮 Multi-model debate started!")
                # Show model assignments
                summary = debate_manager.get_debate_model_summary(role_list)
                if "model_assignments" in summary:
                    console.print("Model assignments:")
                    for role_name, config in summary.get(
                        "model_assignments", {}
                    ).items():
                        console.print(
                            f"  {role_name} uses {config.get('model', 'unknown')}"
                        )

            elif isinstance(event, DebateRoundStartEvent):
                console.print(f"\n🔄 [bold]Round {event.round_number}[/bold] started")
            elif isinstance(event, DebateTurnCompleteEvent):
                console.print(f"🗣️ [bold]{event.participant}[/bold] speaking...")
                console.print(f"📈 Tokens: {getattr(event, 'token_count', 'N/A')}")
                console.print(f"💬 Response from {event.content_preview}")
            elif isinstance(event, TokenUsageEvent):
                console.print(
                    f"📈 Tokens: {event.usage_info.get('total_tokens', 'N/A')}"
                )
            elif isinstance(event, ThoughtEvent):
                console.print(f"💭 {event.content}")
            elif isinstance(event, DebateCompleteEvent):
                console.print("✅ Multi-model debate completed!")

        return "multimodel_session"  # Return session ID

    asyncio.run(run_multimodel_debate_async())


@debate_app.command("history")
def debate_history(
    session_id: Optional[str] = typer.Argument(None, help="特定辩论会话的ID"),
):
    """查看辩论历史记录"""

    async def get_history_async():
        debate_history_tracker = container.debate_history_tracker()

        if session_id:
            # Get specific debate history
            history = await debate_history_tracker.get_history(session_id)
            if history:
                console = Console()
                console.print(f"[bold]Debate Session:[/bold] {history.session_id}")
                console.print(f"[bold]Topic:[/bold] {history.topic}")
                console.print(f"[bold]Status:[/bold] {history.status}")
                console.print(f"[bold]Total Rounds:[/bold] {history.total_rounds}")
                console.print("[bold]Participants:[/bold]")
                for participant in history.participants:
                    console.print(
                        f"  - {participant.name} (Order: {participant.order})"
                    )

                console.print("[bold]--- Debate Transcript ---[/bold]")

                # Group turns by round
                turns_by_round = {}
                for turn in history.turns:
                    if turn.round_number not in turns_by_round:
                        turns_by_round[turn.round_number] = []
                    turns_by_round[turn.round_number].append(turn)

                for round_num in sorted(turns_by_round.keys()):
                    console.print(f"\n[b]Round {round_num}:[/b]")
                    for turn in turns_by_round[round_num]:
                        console.print(
                            f"[blue]{turn.participant}:[/blue] {turn.content}"
                        )

                console.print(f"[bold]End Time:[/bold] {history.end_time}")
            else:
                pass
        else:
            # Get all histories
            all_histories = await debate_history_tracker.get_all_histories()
            if all_histories:
                console = Console()
                table = Table(title="Debate History Sessions")
                table.add_column("Session ID", style="dim", width=35)
                table.add_column("Topic", min_width=15)
                table.add_column("Status", justify="center")
                table.add_column("Rounds", justify="right")
                table.add_column("Participants", justify="right")

                # Show up to 15 most recent debates
                histories_to_show = all_histories[:15]
                console.print(f"Found {len(all_histories)} debate history sessions:")

                for history in histories_to_show:
                    # Format topic with newlines
                    topic_lines = history.topic.split("\n")
                    topic_display = topic_lines[0]  # Take first line for display
                    if len(topic_lines) > 1:
                        topic_display += "..."

                    table.add_row(
                        history.session_id,
                        topic_display,
                        history.status,
                        str(history.total_rounds),
                        str(len(history.participants)),
                    )

                console.print(table)

                if len(all_histories) > 15:
                    pass
            else:
                pass

    asyncio.run(get_history_async())


# Create document tools sub-app
doc_app = typer.Typer()
app.add_typer(doc_app, name="doc", help="文档处理相关命令")


@doc_app.command("download")
def doc_download(
    topic: str = typer.Argument(..., help="论文主题或关键词"),
    source: str = typer.Option("arxiv", help="论文来源 (arxiv, pubmed, web)"),
):
    """下载学术论文"""

    async def run_download_async():
        from daip_live.doc.models.document_models import PaperSource
        from daip_live.doc.tools.paper_downloader import PaperDownloader

        console = Console()
        console.print(f"[bold]Downloading paper on topic:[/bold] {topic}")
        console.print(f"[bold]Source:[/bold] {source}")

        # Map string to enum
        source_enum = PaperSource.ARXIV
        if source.lower() == "pubmed":
            source_enum = PaperSource.PUBMED
        elif source.lower() == "web":
            source_enum = PaperSource.WEB

        downloader = PaperDownloader()
        result = await downloader.download_paper_by_topic(topic, source_enum)

        if result.success:
            console.print("✅ Paper downloaded successfully!")
            console.print(f"📁 File: {result.file_path}")
            if result.metadata:
                console.print(f"📑 Title: {result.metadata.title}")
                console.print(f"👥 Authors: {', '.join(result.metadata.authors)}")
        else:
            console.print(f"❌ Download failed: {result.error_message}")

    asyncio.run(run_download_async())


@doc_app.command("search")
def doc_search(
    query: str = typer.Argument(..., help="搜索关键词"),
    source: str = typer.Option("arxiv", help="搜索来源 (arxiv, pubmed, web)"),
    max_results: int = typer.Option(5, help="最大结果数"),
):
    """搜索学术论文"""

    async def run_search_async():
        from daip_live.doc.models.document_models import PaperSource
        from daip_live.doc.tools.paper_downloader import PaperDownloader

        console = Console()
        console.print(f"[bold]Searching papers for:[/bold] {query}")
        console.print(f"[bold]Source:[/bold] {source}")
        console.print(f"[bold]Max results:[/bold] {max_results}")

        # Map string to enum
        source_enum = PaperSource.ARXIV
        if source.lower() == "pubmed":
            source_enum = PaperSource.PUBMED
        elif source.lower() == "web":
            source_enum = PaperSource.WEB

        downloader = PaperDownloader()
        results = await downloader.search_papers(query, source_enum, max_results)

        if results:
            console.print(f"🔍 Found {len(results)} papers:")
            table = Table()
            table.add_column("Title", style="dim", min_width=20)
            table.add_column("Authors", min_width=15)
            table.add_column("Year", justify="right")

            for paper in results:
                year = paper.publication_date.year if paper.publication_date else "N/A"
                authors = ", ".join(paper.authors[:2])  # Show first 2 authors
                if len(paper.authors) > 2:
                    authors += " et al."

                table.add_row(paper.title, authors, str(year))

            console.print(table)
        else:
            console.print("No papers found for the query.")

    asyncio.run(run_search_async())


@app.command("ask")
def process_natural_language(
    query: str = typer.Argument(..., help="Natural language query to process"),
):
    """Process natural language input and execute appropriate actions"""
    # Import the intent recognizer

    try:
        # Create intent recognizer
        intent_recognizer = EnhancedIntentRecognizer()

        # Recognize the intent from the natural language input
        intent = intent_recognizer.recognize_intent(query)

        if intent is None:
            return

        # Process based on the recognized intent
        if intent.name == "start_debate":
            _handle_debate_intent(intent)
        elif intent.name == "search_papers":
            _handle_search_papers_intent(intent)
        elif intent.name == "download_paper":
            _handle_download_paper_intent(intent)
        elif intent.name in ["chat", "question"]:
            asyncio.run(_handle_conversation_intent(intent))
        else:
            pass

    except Exception as e:
        # 不再静默吞错：向用户展示错误信息
        from rich.console import Console

        Console().print(f"[red]处理请求失败: {e}[/red]")


def _handle_debate_intent(intent: Intent):
    """Handle debate start intent"""
    topic = intent.parameters.get("topic", "General Discussion")
    roles = intent.parameters.get("roles")
    rounds = intent.parameters.get("rounds", 3)

    roles_str = "pro_arguer,con_arguer"
    if isinstance(roles, (list, tuple)):
        roles_str = ",".join(str(r) for r in roles)
    elif roles:
        roles_str = str(roles)

    # 复用真实 debate start 命令（容器装配的 EnhancedDebateManager + 真实 Ollama 生成）
    debate_start(topic=topic, roles=roles_str, rounds=int(rounds))


def _handle_search_papers_intent(intent: Intent):
    """Handle paper search intent"""
    query = intent.parameters.get("query", "")
    source = intent.parameters.get("source", "arxiv")
    max_results = intent.parameters.get("max_results", 5)

    if not query:
        return

    # 复用真实 doc search 命令（PaperDownloader.search_papers）
    doc_search(query=query, source=source, max_results=int(max_results))


def _handle_download_paper_intent(intent: Intent):
    """Handle paper download intent"""
    paper_id = intent.parameters.get("paper_id")
    source = intent.parameters.get("source", "arxiv")
    if not paper_id:
        return

    # 复用真实 doc download 命令（PaperDownloader 内部智能识别 arxiv ID / 主题）
    doc_download(topic=str(paper_id), source=source)


async def _handle_conversation_intent(intent: Intent):
    """Handle conversation intents"""
    question = intent.parameters.get("question", "")
    chat_content = intent.parameters.get("chat_content", "")

    prompt = question or chat_content
    if not prompt:
        return

    from rich.console import Console

    console = Console()
    agent = container.agent_executor()
    step_executor = agent.step_executor
    session = agent.session_manager.create_session(
        goal=prompt, session_type="chat", participant_ids=["agent", "user"]
    )
    current_task = TodoItem(
        id=0, description=prompt, status="pending", priority=1
    )
    answered = False
    async for event in step_executor.execute_step(current_task, session):
        if isinstance(event, FinalResponseEvent) and event.content:
            console.print(event.content)
            answered = True
        elif isinstance(event, ErrorEvent) and event.message:
            console.print(f"[red]错误: {event.message}[/red]")
            answered = True
    if not answered:
        console.print("[yellow]未能生成回答，请检查模型服务状态（Ollama 是否运行）。[/yellow]")  # noqa: E501


# Import commands
from .commands import knowledge, wiki  # noqa: E402
from .commands import model as model_commands  # noqa: E402
from .commands import role as role_commands  # noqa: E402
from .commands import session as session_commands  # noqa: E402

# Import intelligent role management commands
try:
    from .commands.role_intelligent import app as role_intelligent_app

    app.add_typer(
        role_intelligent_app,
        name="role-intel",
        help="Intelligent role management commands",
    )
except ImportError:
    pass

# Register the commands directly
app.add_typer(knowledge.app, name="knowledge", help="Knowledge management commands")
app.add_typer(wiki.app, name="wiki", help="Wiki management commands")

# Register the model/session/role command groups (full implementations that were never mounted)  # noqa: E501
app.add_typer(
    model_commands.app, name="model", help="Model provider management commands"
)
app.add_typer(session_commands.app, name="session", help="Session management commands")
app.add_typer(role_commands.app, name="role", help="Role management commands")


if __name__ == "__main__":
    app()
