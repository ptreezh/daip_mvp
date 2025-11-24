"""
CLI module for the DAIP-LIVE system.

This module provides command-line interfaces for the enhanced debate system and other features.
It follows the module-first design principle and integrates with the container system.
"""
import asyncio
import typer
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from daip_live.container import Container
from daip_live.core.models import (
    DebateStartEvent, DebateRoundStartEvent, DebateTurnCompleteEvent, 
    DebateCompleteEvent, TokenUsageEvent, ThoughtEvent, AgentEvent
)
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider  # Fixed import
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI
from daip_live.agent_engine.enhanced_intent_recognizer import Intent
from rich.console import Console
from rich.table import Table

# Create CLI app
app = typer.Typer()

# Container for dependency injection
container = Container()

# Global intent recognizer instance
intent_recognizer = None


@app.callback()
def initialize_app():
    """Initialize the CLI app and set up global components"""
    global intent_recognizer
    try:
        # Initialize the enhanced intent recognizer from container
        intent_recognizer = container.intent_recognizer()
        print("✅ CLI initialized with enhanced intent recognition")
    except Exception as e:
        print(f"⚠️ Warning: Failed to initialize intent recognizer: {e}")


@app.command()
def run():
    """启动DAIP-TUI界面"""
    try:
        tui = DAIP_TUI()
        tui.run()
    except ImportError as e:
        print(f"Error importing TUI: {e}")
        print("Make sure all dependencies are installed")


# Create debate sub-app
debate_app = typer.Typer()
app.add_typer(debate_app, name="debate", help="辩论相关命令")


@debate_app.command("start")
def debate_start(
    topic: str = typer.Argument(..., help="辩论主题"),
    roles: str = typer.Option("pro_arguer,con_arguer", help="参与辩论的角色，用逗号分隔"),
    rounds: int = typer.Option(1, help="辩论轮次")
):
    """开始辩论"""
    async def run_debate_async():
        # Get components from container
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        role_model_manager = container.role_model_manager()
        model_provider = container.model_provider()  # This should return LiteLLMProvider
        debate_history_tracker = container.debate_history_tracker()
        
        # Create debate manager with history tracker
        debate_manager = EnhancedDebateManager(
            session_manager=session_manager,
            role_manager=role_manager,
            role_model_manager=role_model_manager,
            model_provider=model_provider,
            debate_history_tracker=debate_history_tracker,  # Pass the history tracker
            use_optimized_architecture=True
        )
        
        console = Console()
        role_list = roles.split(",")
        console.print(f"[bold]Starting debate on topic:[/bold] {topic}")
        console.print(f"[bold]Roles:[/bold] {roles}")
        console.print(f"[bold]Rounds:[/bold] {rounds}")
        console.print("🤖 Debate started!")
        
        # Track debate in history at start
        start_event = DebateStartEvent(topic=topic, roles=role_list, rounds=rounds)
        await debate_history_tracker.start_tracking(start_event)
        
        # Run debate and capture events
        async for event in debate_manager.run_debate(topic, role_list, rounds):
            if isinstance(event, DebateStartEvent):
                console.print("🎮 Debate started!")
                # Show model assignments
                summary = debate_manager.get_debate_model_summary(role_list)
                if 'model_assignments' in summary:
                    console.print("Model assignments:")
                    for role_name, config in summary.get("model_assignments", {}).items():
                        console.print(f"  {role_name} → {config.get('model', 'unknown')}")
                        
            elif isinstance(event, DebateRoundStartEvent):
                console.print(f"\n🔄 [bold]Round {event.round_number}[/bold] started")
            elif isinstance(event, DebateTurnCompleteEvent):
                console.print(f"🗣️ [bold]{event.participant}[/bold] speaking...")
                console.print(f"💬 Response from {event.content_preview}")
                if hasattr(event, 'token_usage'):
                    console.print(f"📊 Tokens: {event.token_usage.get('total_tokens', 'N/A')}")
            elif isinstance(event, TokenUsageEvent):
                console.print(f"📈 Tokens: {event.usage_info.get('total_tokens', 'N/A')}")
            elif isinstance(event, ThoughtEvent):
                console.print(f"💭 {event.content}")
            elif isinstance(event, DebateCompleteEvent):
                console.print("✅ Debate completed!")
        
        return "session_created"  # Return session ID for tracking
    
    session_id = asyncio.run(run_debate_async())
    print(f"Session ID: {session_id}")


@debate_app.command("multimodel")
def debate_multimodel(
    topic: str = typer.Argument(..., help="辩论主题"),
    roles: str = typer.Option("economist,laborer,policymaker", help="参与辩论的角色，用逗号分隔"),
    rounds: int = typer.Option(1, help="辩论轮次")
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
            use_optimized_architecture=True
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
            console.print(f"[yellow]Warning: Following roles not found in system, will use default model:[/yellow]")
            for role in unavailable_roles:
                console.print(f"  - {role}")
        
        console.print("🤖 Multi-model debate started!")
        
        # Get debate model summary and show assignments
        summary = debate_manager.get_debate_model_summary(role_list)
        if 'model_assignments' in summary:
            console.print("Model assignments:")
            for role_name, config in summary.get("model_assignments", {}).items():
                model_name = config.get('model', 'unknown')
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
                if 'model_assignments' in summary:
                    console.print("Model assignments:")
                    for role_name, config in summary.get("model_assignments", {}).items():
                        console.print(f"  {role_name} uses {config.get('model', 'unknown')}")
                        
            elif isinstance(event, DebateRoundStartEvent):
                console.print(f"\n🔄 [bold]Round {event.round_number}[/bold] started")
            elif isinstance(event, DebateTurnCompleteEvent):
                console.print(f"🗣️ [bold]{event.participant}[/bold] speaking...")
                console.print(f"📈 Tokens: {getattr(event, 'token_count', 'N/A')}")
                console.print(f"💬 Response from {event.content_preview}")
            elif isinstance(event, TokenUsageEvent):
                console.print(f"📈 Tokens: {event.usage_info.get('total_tokens', 'N/A')}")
            elif isinstance(event, ThoughtEvent):
                console.print(f"💭 {event.content}")
            elif isinstance(event, DebateCompleteEvent):
                console.print("✅ Multi-model debate completed!")
        
        return "multimodel_session"  # Return session ID
    
    session_id = asyncio.run(run_multimodel_debate_async())
    print(f"Session ID: {session_id}")


@debate_app.command("history")
def debate_history(session_id: Optional[str] = typer.Argument(None, help="特定辩论会话的ID")):
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
                console.print(f"[bold]Participants:[/bold]")
                for participant in history.participants:
                    console.print(f"  - {participant.name} (Order: {participant.order})")
                
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
                        console.print(f"[blue]{turn.participant}:[/blue] {turn.content}")
                
                console.print(f"[bold]End Time:[/bold] {history.end_time}")
            else:
                print(f"No debate found with session ID: {session_id}")
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
                    topic_lines = history.topic.split('\n')
                    topic_display = topic_lines[0]  # Take first line for display
                    if len(topic_lines) > 1:
                        topic_display += "..."
                    
                    table.add_row(
                        history.session_id,
                        topic_display,
                        history.status,
                        str(history.total_rounds),
                        str(len(history.participants))
                    )
                
                console.print(table)
                
                if len(all_histories) > 15:
                    print(f"... and {len(all_histories) - 15} more sessions")
            else:
                print("No debate histories found.")
    
    asyncio.run(get_history_async())


# Create document tools sub-app
doc_app = typer.Typer()
app.add_typer(doc_app, name="doc", help="文档处理相关命令")


@doc_app.command("download")
def doc_download(
    topic: str = typer.Argument(..., help="论文主题或关键词"),
    source: str = typer.Option("arxiv", help="论文来源 (arxiv, pubmed, web)")
):
    """下载学术论文"""
    async def run_download_async():
        from daip_live.doc.tools.paper_downloader import PaperDownloader
        from daip_live.doc.models.document_models import PaperSource
        
        console = Console()
        console.print(f"[bold]Downloading paper on topic:[/bold] {topic}")
        console.print(f"[bold]Source:[/bold] {source}")
        
        # Map string to enum
        source_enum = PaperSource.ARXIV
        if source.lower() == 'pubmed':
            source_enum = PaperSource.PUBMED
        elif source.lower() == 'web':
            source_enum = PaperSource.WEB
        
        downloader = PaperDownloader()
        result = await downloader.download_paper_by_topic(topic, source_enum)
        
        if result.success:
            console.print(f"✅ Paper downloaded successfully!")
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
    max_results: int = typer.Option(5, help="最大结果数")
):
    """搜索学术论文"""
    async def run_search_async():
        from daip_live.doc.tools.paper_downloader import PaperDownloader
        from daip_live.doc.models.document_models import PaperSource
        
        console = Console()
        console.print(f"[bold]Searching papers for:[/bold] {query}")
        console.print(f"[bold]Source:[/bold] {source}")
        console.print(f"[bold]Max results:[/bold] {max_results}")
        
        # Map string to enum
        source_enum = PaperSource.ARXIV
        if source.lower() == 'pubmed':
            source_enum = PaperSource.PUBMED
        elif source.lower() == 'web':
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
                authors = ', '.join(paper.authors[:2])  # Show first 2 authors
                if len(paper.authors) > 2:
                    authors += " et al."
                
                table.add_row(paper.title, authors, str(year))
            
            console.print(table)
        else:
            console.print("No papers found for the query.")
    
    asyncio.run(run_search_async())


@app.command("ask")
def process_natural_language(
    query: str = typer.Argument(..., help="Natural language query to process")
):
    """Process natural language input and execute appropriate actions"""
    global intent_recognizer
    
    if intent_recognizer is None:
        print("❌ Intent recognizer not initialized")
        return
    
    try:
        # Recognize the intent from the natural language input
        intent = intent_recognizer.recognize_intent(query)
        
        if intent is None:
            print(f"❓ Sorry, I couldn't understand your request: '{query}'")
            print("💡 Try rephrasing or use specific commands like:")
            print("   - 'start debate about AI ethics'")
            print("   - 'search papers about machine learning'")
            print("   - 'download paper with ID 1234.5678'")
            return
        
        print(f"🎯 Recognized intent: {intent.name} (confidence: {intent.confidence:.2f})")
        
        # Process based on the recognized intent
        if intent.name == "start_debate":
            _handle_debate_intent(intent)
        elif intent.name == "search_papers":
            _handle_search_papers_intent(intent)
        elif intent.name == "download_paper":
            _handle_download_paper_intent(intent)
        elif intent.name == "view_debate_history":
            _handle_view_debate_history_intent(intent)
        elif intent.name == "view_specific_debate":
            _handle_view_specific_debate_intent(intent)
        elif intent.name in ["chat", "question"]:
            _handle_conversation_intent(intent)
        else:
            print(f"🚧 Intent '{intent.name}' recognized but not yet implemented")
            print(f"📝 Parameters: {intent.parameters}")
    
    except Exception as e:
        print(f"❌ Error processing natural language input: {e}")


def _handle_debate_intent(intent: Intent):
    """Handle debate start intent"""
    try:
        topic = intent.parameters.get("topic", "General Discussion")
        roles = intent.parameters.get("roles")
        rounds = intent.parameters.get("rounds", 3)
        
        print(f"🗣️ Starting debate on topic: {topic}")
        print(f"🎭 Roles: {roles or 'default'}")
        print(f"🔄 Rounds: {rounds}")
        
        # Call the existing debate start command
        debate_start(topic=topic, roles=roles or "pro_arguer,con_arguer", rounds=rounds)
        
    except Exception as e:
        print(f"❌ Error starting debate: {e}")


def _handle_search_papers_intent(intent: Intent):
    """Handle paper search intent"""
    try:
        query = intent.parameters.get("query", "")
        source = intent.parameters.get("source", "arxiv")
        max_results = intent.parameters.get("max_results", 5)  # Default to 5 to match CLI
        
        if not query:
            print("❌ No search query provided")
            return
            
        print(f"📚 Searching for papers about: {query}")
        print(f"🌐 Source: {source}")
        print(f"🔢 Max results: {max_results}")
        
        # Call the existing document search command
        doc_search(query=query, source=source, max_results=max_results)
        
    except Exception as e:
        print(f"❌ Error searching papers: {e}")


def _handle_download_paper_intent(intent: Intent):
    """Handle paper download intent"""
    try:
        paper_id = intent.parameters.get("paper_id")
        if not paper_id:
            print("❌ No paper ID provided for download")
            return
            
        print(f"📥 Downloading paper with ID: {paper_id}")
        
        # Call the existing document download command
        doc_download(topic=paper_id, source="arxiv")
        
    except Exception as e:
        print(f"❌ Error downloading paper: {e}")


def _handle_view_debate_history_intent(intent: Intent):
    """Handle debate history viewing intent"""
    try:
        session_id = intent.parameters.get("session_id")
        print(f"📜 Viewing debate history{' for session: ' + session_id if session_id else ''}")
        
        # Call the existing debate history command
        debate_history(session_id=session_id)
        
    except Exception as e:
        print(f"❌ Error viewing debate history: {e}")


def _handle_view_specific_debate_intent(intent: Intent):
    """Handle specific debate viewing intent"""
    try:
        session_id = intent.parameters.get("session_id")
        if not session_id:
            print("❌ No session ID provided")
            return
            
        print(f"🔍 Viewing specific debate session: {session_id}")
        
        # Call the existing debate history command with specific session
        debate_history(session_id=session_id)
        
    except Exception as e:
        print(f"❌ Error viewing specific debate: {e}")


def _handle_conversation_intent(intent: Intent):
    """Handle conversation/chat/question intent"""
    try:
        if intent.intent_type == IntentType.QUESTION:
            question = intent.parameters.get("question", "")
            print(f"🤔 Question: {question}")
            print("💡 For questions, please use the TUI interface for interactive responses")
        else:
            chat_content = intent.parameters.get("chat_content", "")
            print(f"💬 Chat: {chat_content}")
            print("👋 Hello! For chat interactions, please use the TUI interface")
            
    except Exception as e:
        print(f"❌ Error handling conversation: {e}")


if __name__ == "__main__":
    app()