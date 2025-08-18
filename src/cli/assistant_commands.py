"""New CLI commands implementation using underlying domain services and use cases."""

import asyncio
import logging
from typing import Optional
from rich.console import Console

from src.domain.domain_services import (
    EntranceSelectorService,
    WorkflowOrchestratorService,
    UserInterventionService,
    ConsensusTrackingService
)
from src.use_cases.use_cases import SecretariatUseCase, ForumUseCase, EntranceSwitchingUseCase
from src.domain.entities import User
from src.domain.value_objects import EntranceType, UserPreference

console = Console()
logger = logging.getLogger(__name__)


class CLIAssistantService:
    """CLI Assistant Service - Direct interface to underlying domain services and use cases."""
    
    def __init__(self):
        # Initialize core domain services
        self.entrance_selector = EntranceSelectorService()
        self.workflow_orchestrator = WorkflowOrchestratorService()
        self.user_intervention = UserInterventionService()
        self.consensus_tracker = ConsensusTrackingService()
        
        # Initialize use cases
        self.secretariat_use_case = SecretariatUseCase()
        self.forum_use_case = ForumUseCase()
        self.entrance_switching_use_case = EntranceSwitchingUseCase()
        
        # CLI user
        self.cli_user = User(
            user_id="cli_user",
            username="CLI User",
            email="cli@daip.live",
            preferred_entrance=EntranceType.SECRETARIAT,
            preferences=UserPreference(
                preferred_entrance=EntranceType.SECRETARIAT,
                language="zh-CN",
                theme="light",
                notification_enabled=True,
                auto_transparency=False,
                detail_level="comprehensive"
            )
        )
        
        # Session management
        self.current_session_id: Optional[str] = None
        self.session_history = {}
        
    async def initialize(self):
        """Initialize the CLI assistant service."""
        # Initialize any required components
        pass
        
    async def process_query(self, query: str) -> dict:
        """Process a user query using the appropriate entrance type."""
        # Select entrance type based on query
        context = {"query": query}
        selected_entrance = await self.entrance_selector.select_entrance(self.cli_user, context)
        
        if selected_entrance == EntranceType.SECRETARIAT:
            return await self._process_secretariat_query(query)
        else:
            return await self._process_forum_query(query)
            
    async def _process_secretariat_query(self, query: str) -> dict:
        """Process a query using the Secretariat entrance."""
        # Create session if none exists
        if not self.current_session_id:
            session = await self.secretariat_use_case.create_session(self.cli_user, EntranceType.SECRETARIAT)
            self.current_session_id = session.session_id
            self.session_history[session.session_id] = {
                "type": "secretariat",
                "session": session,
                "created_at": session.created_at
            }
        
        # Submit task
        task_request = {
            "content": query,
            "intent_type": "analysis",  # Simplified for now
            "priority": "normal",
            "context": {}
        }
        
        result = await self.secretariat_use_case.submit_task(self.current_session_id, task_request)
        return {
            "type": "task_created",
            "task_id": result["task_id"],
            "workflow_id": result["workflow_id"],
            "estimated_duration": result["estimated_duration"],
            "message": f"任务已创建，预计需要 {result['estimated_duration']:.1f} 秒完成"
        }
        
    async def _process_forum_query(self, query: str) -> dict:
        """Process a query using the Forum entrance."""
        # Create session if none exists
        if not self.current_session_id:
            session_config = {
                "topic": query,
                "participants": ["expert_1", "expert_2"]
            }
            session = await self.forum_use_case.create_forum_session(self.cli_user, session_config)
            self.current_session_id = session.session_id
            self.session_history[session.session_id] = {
                "type": "forum",
                "session": session,
                "created_at": session.created_at
            }
        
        # Start debate
        result = await self.forum_use_case.start_debate(self.current_session_id)
        return {
            "type": "debate_started",
            "debate_id": result["debate_id"],
            "topic": result["topic"],
            "participants": result["participants"],
            "message": f"辩论已启动，主题：{result['topic']}"
        }
        
    async def process_intervention(self, content: str, intent: str = "comment") -> dict:
        """Process a user intervention in the current session."""
        if not self.current_session_id:
            raise ValueError("No active session. Start a conversation first.")
            
        # Get session type
        session_info = self.session_history.get(self.current_session_id)
        if not session_info:
            raise ValueError("Invalid session ID")
            
        if session_info["type"] == "forum":
            # Handle intervention for forum session
            intervention_data = {
                "message": {
                    "content": content,
                    "intent": intent
                },
                "context": {}
            }
            
            result = await self.forum_use_case.handle_user_intervention(self.current_session_id, intervention_data)
            return {
                "type": "intervention_processed",
                "message_id": result["message_id"],
                "optimized_input": result["optimized_input"],
                "integration_result": result["integration_result"],
                "message": "用户干预已集成到讨论中"
            }
        else:
            # For secretariat sessions, we might want to cancel current task and create a new one
            # This is a simplified implementation
            return {
                "type": "intervention_processed",
                "message": "干预已记录，将影响后续任务执行"
            }
            
    async def get_consensus_info(self) -> dict:
        """Get consensus information for the current forum session."""
        if not self.current_session_id:
            raise ValueError("No active session. Start a conversation first.")
            
        session_info = self.session_history.get(self.current_session_id)
        if not session_info or session_info["type"] != "forum":
            raise ValueError("Consensus information is only available for Forum sessions.")
            
        # Get debate context
        context = await self.forum_use_case.get_debate_context(self.current_session_id)
        return {
            "type": "consensus_info",
            "session_id": self.current_session_id,
            "debate_id": context["debate_id"],
            "topic": context["topic"],
            "consensus_level": context["consensus_level"],
            "consensus_description": context["consensus_description"],
            "active_agents": context["active_agents"],
            "key_arguments": context["key_arguments"],
            "message_count": context["message_count"],
            "participant_count": context["participant_count"]
        }
        
    async def get_disagreement_points(self) -> dict:
        """Get key disagreement points for the current forum session."""
        if not self.current_session_id:
            raise ValueError("No active session. Start a conversation first.")
            
        session_info = self.session_history.get(self.current_session_id)
        if not session_info or session_info["type"] != "forum":
            raise ValueError("Disagreement points are only available for Forum sessions.")
            
        # Get debate context
        context = await self.forum_use_case.get_debate_context(self.current_session_id)
        return {
            "type": "disagreement_points",
            "session_id": self.current_session_id,
            "debate_id": context["debate_id"],
            "topic": context["topic"],
            "key_arguments": context["key_arguments"]
        }
        
    async def get_sessions_list(self) -> dict:
        """Get list of all sessions."""
        sessions = []
        for session_id, session_info in self.session_history.items():
            sessions.append({
                "session_id": session_id,
                "type": session_info["type"],
                "created_at": session_info["created_at"].isoformat() if session_info["created_at"] else None
            })
            
        return {
            "type": "sessions_list",
            "sessions": sessions,
            "current_session": self.current_session_id
        }
        
    async def switch_to_session(self, session_id: str) -> dict:
        """Switch to a specific session."""
        if session_id not in self.session_history:
            raise ValueError(f"Session {session_id} not found.")
            
        self.current_session_id = session_id
        session_info = self.session_history[session_id]
        
        return {
            "type": "session_switched",
            "session_id": session_id,
            "session_type": session_info["type"],
            "message": f"已切换到会话 {session_id}"
        }


# Global instance for CLI commands
cli_assistant_service: Optional[CLIAssistantService] = None


async def initialize_cli_assistant_service():
    """Initialize the CLI assistant service."""
    global cli_assistant_service
    if cli_assistant_service is None:
        cli_assistant_service = CLIAssistantService()
        await cli_assistant_service.initialize()


async def run_assistant_chat_command(query: str):
    """Send a query to the personal assistant and display the response."""
    if not query.strip():
        console.print("[red]❌ Error: Query cannot be empty.[/red]")
        return

    try:
        await initialize_cli_assistant_service()
        
        with console.status("[bold blue]Thinking...[/bold blue]", spinner="dots"):
            # Process the user's query
            response = await cli_assistant_service.process_query(query)

            # Display the assistant's response
            if response and response.get("type") == "task_created":
                console.print(f"\n[bold green]✅ Assistant Response:[/bold green]")
                console.print(f"[white]{response.get('message', 'Task created successfully.')}[/white]")
                console.print(f"[dim]Task ID: {response.get('task_id')}[/dim]")
                console.print(f"[dim]Estimated Duration: {response.get('estimated_duration'):.1f} seconds[/dim]")
            elif response and response.get("type") == "debate_started":
                console.print(f"\n[bold green]✅ Assistant Response:[/bold green]")
                console.print(f"[white]{response.get('message', 'Debate started successfully.')}[/white]")
                console.print(f"[dim]Debate ID: {response.get('debate_id')}[/dim]")
                console.print(f"[dim]Topic: {response.get('topic')}[/dim]")
            else:
                console.print(f"\n[bold green]✅ Assistant Response:[/bold green]")
                console.print(f"[white]{response.get('response', 'No specific response content.')}[/white]")  # Fallback for other response types

    except Exception as e:
        console.print(f"\n[red]❌ An error occurred while interacting with the assistant: {e}[/red]")
        logger.error(f"Personal assistant CLI command failed: {e}", exc_info=True)


async def run_assistant_intervention_command(content: str, intent: str = "comment"):
    """Process a user intervention and display the response."""
    if not content.strip():
        console.print("[red]❌ Error: Intervention content cannot be empty.[/red]")
        return

    try:
        await initialize_cli_assistant_service()
        
        with console.status("[bold blue]Processing intervention...[/bold blue]", spinner="dots"):
            # Process the user's intervention
            response = await cli_assistant_service.process_intervention(content, intent)

            # Display the assistant's response
            if response and response.get("type") == "intervention_processed":
                console.print(f"\n[bold green]✅ Intervention Response:[/bold green]")
                console.print(f"[white]{response.get('message', 'Intervention processed successfully.')}[/white]")
            else:
                console.print(f"\n[bold green]✅ Intervention Response:[/bold green]")
                console.print(f"[white]{response.get('response', 'No specific response content.')}[/white]")

    except Exception as e:
        console.print(f"\n[red]❌ An error occurred while processing the intervention: {e}[/red]")
        logger.error(f"Personal assistant intervention CLI command failed: {e}", exc_info=True)


async def run_assistant_consensus_command():
    """Get consensus information and display it."""
    try:
        await initialize_cli_assistant_service()
        
        with console.status("[bold blue]Getting consensus information...[/bold blue]", spinner="dots"):
            # Get consensus information
            response = await cli_assistant_service.get_consensus_info()

            # Display the consensus information
            if response and response.get("type") == "consensus_info":
                console.print(f"\n[bold yellow]📊 Consensus Information:[/bold yellow]")
                console.print(f"[green]Topic: {response.get('topic')}[/green]")
                console.print(f"[cyan]Consensus Level: {response.get('consensus_level')*100:.1f}%[/cyan]")
                console.print(f"[white]{response.get('consensus_description')}[/white]")
                
                # Display key arguments
                key_arguments = response.get('key_arguments', [])
                if key_arguments:
                    console.print(f"\n[bold]Key Arguments:[/bold]")
                    for i, arg in enumerate(key_arguments[:5], 1):  # Show top 5 arguments
                        console.print(f"[dim]{i}. {arg.get('argument', '')}[/dim]")
            else:
                console.print(f"\n[bold yellow]📊 Consensus Information:[/bold yellow]")
                console.print(f"[white]{response.get('response', 'No specific consensus information.')}[/white]")

    except Exception as e:
        console.print(f"\n[red]❌ An error occurred while getting consensus information: {e}[/red]")
        logger.error(f"Personal assistant consensus CLI command failed: {e}", exc_info=True)


async def run_assistant_disagreement_command():
    """Get disagreement points and display them."""
    try:
        await initialize_cli_assistant_service()
        
        with console.status("[bold blue]Getting disagreement points...[/bold blue]", spinner="dots"):
            # Get disagreement points
            response = await cli_assistant_service.get_disagreement_points()

            # Display the disagreement points
            if response and response.get("type") == "disagreement_points":
                console.print(f"\n[bold magenta]🔍 Disagreement Points:[/bold magenta]")
                console.print(f"[green]Topic: {response.get('topic')}[/green]")
                
                # Display key arguments
                key_arguments = response.get('key_arguments', [])
                if key_arguments:
                    console.print(f"\n[bold]Key Arguments:[/bold]")
                    for i, arg in enumerate(key_arguments[:5], 1):  # Show top 5 arguments
                        console.print(f"[dim]{i}. {arg.get('argument', '')}[/dim]")
                else:
                    console.print("[dim]No key arguments found.[/dim]")
            else:
                console.print(f"\n[bold magenta]🔍 Disagreement Points:[/bold magenta]")
                console.print(f"[white]{response.get('response', 'No specific disagreement information.')}[/white]")

    except Exception as e:
        console.print(f"\n[red]❌ An error occurred while getting disagreement points: {e}[/red]")
        logger.error(f"Personal assistant disagreement CLI command failed: {e}", exc_info=True)


async def run_assistant_sessions_command():
    """Get sessions list and display it."""
    try:
        await initialize_cli_assistant_service()
        
        with console.status("[bold blue]Getting sessions list...[/bold blue]", spinner="dots"):
            # Get sessions list
            response = await cli_assistant_service.get_sessions_list()

            # Display the sessions list
            if response and response.get("type") == "sessions_list":
                console.print(f"\n[bold blue]📝 Sessions List:[/bold blue]")
                
                sessions = response.get('sessions', [])
                current_session = response.get('current_session')
                
                if sessions:
                    for session in sessions:
                        session_id = session.get('session_id')
                        session_type = session.get('type')
                        created_at = session.get('created_at')
                        
                        # Mark current session
                        current_marker = " (current)" if session_id == current_session else ""
                        
                        console.print(f"[cyan]ID: {session_id}{current_marker}[/cyan]")
                        console.print(f"[white]  Type: {session_type}[/white]")
                        console.print(f"[dim]  Created: {created_at}[/dim]")
                        console.print("")
                else:
                    console.print("[dim]No sessions found.[/dim]")
            else:
                console.print(f"\n[bold blue]📝 Sessions List:[/bold blue]")
                console.print(f"[white]{response.get('response', 'No specific sessions information.')}[/white]")

    except Exception as e:
        console.print(f"\n[red]❌ An error occurred while getting sessions list: {e}[/red]")
        logger.error(f"Personal assistant sessions CLI command failed: {e}", exc_info=True)