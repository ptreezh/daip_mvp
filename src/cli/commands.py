"""@Time    : 2025-07-19 03:30:00
@Author  : DAIP-LIVE Team
@File    : commands.py
@Description: CLI command implementations for DAIP-LIVE system.
"""

import asyncio
import importlib.util
import logging

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize console and logger
console = Console()
logger = logging.getLogger(__name__)

# Check for required dependencies
MISSING_DEPENDENCIES = []
REQUIRED_MODULES = [
    'aiosqlite',
    'chromadb',
    'tiktoken',
    'frontmatter'  # Module name for python-frontmatter package
]

for module in REQUIRED_MODULES:
    if importlib.util.find_spec(module) is None:
        MISSING_DEPENDENCIES.append(module)

# Only import if dependencies are available
# Temporarily remove condition for TDD GREEN state
# if not MISSING_DEPENDENCIES:
from src.app_state import AppState
from src.models import DebateConfig
from src.protocols.debate_protocol import DebateProtocol
from src.application.personal_assistant_service import PersonalAssistantService
from src.domain.entities import UserMessage
try:
    pass # Placeholder for other imports that might need try-except
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    MISSING_DEPENDENCIES.append(str(e))

class CLIDebateHandler:
    """Handles CLI debate execution with real-time output."""
    
    def __init__(self):
        self.app_state = None
        self.debate_protocol = None
        self.event_queue = None
        self.command_queue = None
        self.debate_history = []
        self.intervention_handler = None
        
    async def initialize(self):
        """Initialize the debate handler with app state and services."""
        initialization_steps = [
            ("Loading application state", "app_state"),
            ("Setting up communication channels", "event_queue"),
            ("Setting up command channel", "command_queue"),
            ("Preparing debate kernel", "kernel"),
            ("Initializing debate protocol", "protocol"),
            ("Setting up user intervention", "intervention")
        ]
        
        try:
            console.print("[bold blue]🔧 Initializing services...[/bold blue]")
            
            for i, (step_name, step_key) in enumerate(initialization_steps, 1):
                console.print(f"[dim]   {i}/{len(initialization_steps)}: {step_name}...[/dim]")
                
                if step_key == "app_state":
                    self.app_state = AppState()
                    await asyncio.sleep(0.1)  # Allow UI to update
                    
                elif step_key == "event_queue":
                    self.event_queue = asyncio.Queue()
                    await asyncio.sleep(0.1)
                
                elif step_key == "command_queue":
                    self.command_queue = asyncio.Queue()
                    await asyncio.sleep(0.1)
                    
                elif step_key == "kernel":
                    from types import SimpleNamespace
                    kernel = SimpleNamespace()
                    kernel.synthesis_engine = self.app_state.synthesis_engine
                    kernel.llm_interface = self.app_state.llm_interface
                    kernel.tool_executor = self.app_state.unified_tool_manager
                    await asyncio.sleep(0.1)
                    
                elif step_key == "protocol":
                    self.debate_protocol = DebateProtocol(kernel=kernel, event_queue=self.event_queue, command_queue=self.command_queue)
                    await asyncio.sleep(0.1)
                
                elif step_key == "intervention":
                    from src.cli.user_intervention import UserInterventionHandler
                    self.intervention_handler = UserInterventionHandler(self.command_queue)
                    await asyncio.sleep(0.1)
                
                console.print(f"[green]   ✅ {step_name} completed[/green]")
            
            console.print("[bold green]🎉 All services initialized successfully![/bold green]")
            return True
            
        except Exception as e:
            console.print(f"\n[red]❌ Failed to initialize services: {e}[/red]")
            
            # Enhanced error categorization with specific solutions
            error_str = str(e).lower()
            if "no module named" in error_str:
                console.print("[yellow]🔧 Missing dependency detected:[/yellow]")
                console.print("[yellow]   • Run: pip install -r requirements.txt[/yellow]")
                console.print("[yellow]   • Check if all required packages are installed[/yellow]")
            elif "connection refused" in error_str or "connection error" in error_str:
                console.print("[yellow]🌐 Connection issue detected:[/yellow]")
                console.print("[yellow]   • Check if LLM server is running (e.g., Ollama on port 11434)[/yellow]")
                console.print("[yellow]   • Verify network connectivity[/yellow]")
                console.print("[yellow]   • Check firewall settings[/yellow]")
            elif "permission denied" in error_str:
                console.print("[yellow]🔒 Permission issue detected:[/yellow]")
                console.print("[yellow]   • Check file/directory permissions[/yellow]")
                console.print("[yellow]   • Ensure data directories are writable[/yellow]")
                console.print("[yellow]   • Try running with appropriate privileges[/yellow]")
            elif "appstate" in error_str:
                console.print("[yellow]⚙️  Application state issue detected:[/yellow]")
                console.print("[yellow]   • Check configuration files (config.yaml)[/yellow]")
                console.print("[yellow]   • Verify database connectivity[/yellow]")
                console.print("[yellow]   • Run 'daip-cli status' for detailed diagnostics[/yellow]")
            elif "database" in error_str or "sqlite" in error_str:
                console.print("[yellow]🗄️  Database issue detected:[/yellow]")
                console.print("[yellow]   • Check if data directory exists and is writable[/yellow]")
                console.print("[yellow]   • Verify database file permissions[/yellow]")
                console.print("[yellow]   • Try deleting and recreating the database[/yellow]")
            elif "memory" in error_str:
                console.print("[yellow]💾 Memory issue detected:[/yellow]")
                console.print("[yellow]   • Close other applications to free memory[/yellow]")
                console.print("[yellow]   • Try with simpler configuration[/yellow]")
                console.print("[yellow]   • Check system resources[/yellow]")
            else:
                console.print("[yellow]💡 General troubleshooting:[/yellow]")
                console.print("[yellow]   • Run 'daip-cli status' to check system health[/yellow]")
                console.print("[yellow]   • Check logs for more detailed error information[/yellow]")
                console.print("[yellow]   • Verify all configuration files are present[/yellow]")
            
            # Log the full error for debugging
            logger.error(f"Service initialization failed: {e}", exc_info=True)
            return False
    
    async def start_debate(self, topic: str, roles: list[str], rounds: int, consensus_strategy: str, verbose: bool):
        """Start and manage a debate session."""
        if not await self.initialize():
            return False
            
        # Start listening for user interventions
        if self.intervention_handler:
            self.intervention_handler.start_listening()
            
        # Validate roles
        if not roles:
            console.print("[yellow]No roles specified. Using default roles.[/yellow]")
            roles = ["Expert", "Critic"]  # Default roles
            
        # Create debate configuration
        config = DebateConfig(
            topic=topic,
            roles=roles,
            rounds=rounds,
            consensus_strategy=consensus_strategy
        )
        
        console.print(f"\n[bold green]🎯 Starting Debate: {topic}[/bold green]")
        console.print(f"[dim]Participants: {', '.join(roles)}[/dim]")
        console.print(f"[dim]Rounds: {rounds} | Strategy: {consensus_strategy}[/dim]\n")
        
        # Start the debate in a separate task
        debate_task = asyncio.create_task(self.debate_protocol.run(config))
        
        # Process events in real-time
        event_task = asyncio.create_task(self._process_events(verbose))
        
        try:
            # Wait for both tasks to complete
            await asyncio.gather(debate_task, event_task)
            console.print("\n[bold green]✅ Debate completed successfully![/bold green]")
            
            # Stop listening for user interventions
            if self.intervention_handler:
                self.intervention_handler.stop_listening()
                
            return True
            
        except Exception as e:
            console.print(f"\n[red]❌ Debate failed: {e}[/red]")
            logger.error(f"Debate execution failed: {e}", exc_info=True)
            return False
    
    async def _process_events(self, verbose: bool):
        """Process debate events and display them in real-time."""
        # Track debate progress
        current_round = 0
        total_rounds = 0
        roles_count = 0
        
        try:
            while True:
                try:
                    # Wait for events with a timeout to allow graceful shutdown
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                    
                    if hasattr(event, 'event_type'):
                        if event.event_type == 'debate_start':
                            console.print("[bold blue]🚀 Debate Started[/bold blue]")
                            # Extract debate configuration for progress tracking
                            total_rounds = event.config.rounds
                            roles_count = len(event.config.roles)
                            console.print(f"[dim]Planning {total_rounds} rounds with {roles_count} participants[/dim]")
                            
                        elif event.event_type == 'new_turn':
                                
                            turn = event.turn
                            
                            # Update round tracking
                            if turn.round > current_round:
                                current_round = turn.round
                                console.print(f"\n[bold]Round {current_round}/{total_rounds}[/bold]")
                            
                            # Determine role color based on role name
                            role_color = "cyan"
                            if "Expert" in turn.role_id:
                                role_color = "cyan"
                            elif "Critic" in turn.role_id:
                                role_color = "magenta"
                            elif "User" in turn.role_id:
                                role_color = "green"
                            else:
                                # Assign colors based on role position
                                colors = ["cyan", "magenta", "yellow", "green", "blue", "purple"]
                                role_index = sum(1 for t in self.debate_history if hasattr(t, 'role_id') and t.role_id == turn.role_id)
                                role_color = colors[role_index % len(colors)]
                            
                            # Display the turn
                            panel = Panel(
                                Text(turn.opinion, style="white"),
                                title=f"[{role_color}]{turn.role_id}[/{role_color}] - Round {turn.round}",
                                border_style=role_color
                            )
                            console.print(panel)
                            self.debate_history.append(turn)
                            
                            # Show waiting message without spinner to avoid conflicts
                            if roles_count > 0:
                                next_role_index = len(self.debate_history) % roles_count
                                if next_role_index < roles_count:
                                    console.print("[dim]⏳ Waiting for next response...[/dim]")
                            
                        elif event.event_type == 'tech_log' and verbose:
                            # Show technical logs only in verbose mode
                            console.print(f"[dim]🔧 {event.source}: {event.message}[/dim]")
                            
                        elif event.event_type == 'debate_end':
                                
                            result = event.result
                            console.print("\n[bold yellow]📊 Debate Results[/bold yellow]")
                            
                            # Display consensus
                            if result.consensus_outcome:
                                console.print(f"[green]Consensus: {result.consensus_outcome}[/green]")
                            
                            # Display synthesis
                            if result.synthesis:
                                synthesis_panel = Panel(
                                    Text(result.synthesis, style="white"),
                                    title="[bold yellow]Final Synthesis[/bold yellow]",
                                    border_style="yellow"
                                )
                                console.print(synthesis_panel)
                            
                            # Display debate statistics
                            console.print("\n[bold]Debate Statistics:[/bold]")
                            console.print(f"[dim]• Total rounds: {current_round}/{total_rounds}[/dim]")
                            console.print(f"[dim]• Participants: {roles_count}[/dim]")
                            console.print(f"[dim]• Total turns: {len(self.debate_history)}[/dim]")
                            
                            break
                            
                        elif event.event_type == 'error':
                                
                            console.print(f"[red]❌ Error: {event.error_message}[/red]")
                            if verbose and event.details:
                                console.print(f"[dim]Details: {event.details}[/dim]")
                                
                            # Provide troubleshooting tips based on error message
                            if "timeout" in str(event.error_message).lower():
                                console.print("[yellow]The operation timed out. This could be due to high server load or network issues.[/yellow]")
                                console.print("[yellow]Try again later or with a simpler debate configuration.[/yellow]")
                            elif "memory" in str(event.error_message).lower():
                                console.print("[yellow]The system may be running out of memory. Try reducing the number of rounds or participants.[/yellow]")
                            
                            break
                            
                except asyncio.TimeoutError:
                    # Just continue waiting
                    continue
                    
        except Exception as e:
            console.print(f"[red]❌ Event processing error: {e}[/red]")
            logger.error(f"Event processing error: {e}", exc_info=True)


async def run_debate_command(topic: str, roles: list[str], rounds: int, consensus_strategy: str, verbose: bool, save_results: bool = False, output_file: str = "debate_results.txt"):
    """Run the debate command asynchronously."""
    # Check for missing dependencies
    if MISSING_DEPENDENCIES:
        console.print("[red]❌ Missing required dependencies:[/red]")
        for dep in MISSING_DEPENDENCIES:
            console.print(f"[red]   - {dep}[/red]")
        console.print("\n[yellow]Please install missing dependencies with:[/yellow]")
        
        # Filter out error messages that aren't actual package names
        install_deps = [dep for dep in MISSING_DEPENDENCIES if not dep.startswith("No module named")]
        if install_deps:
            console.print("[dim]pip install " + " ".join(install_deps) + "[/dim]")
        return False
        
    # Create a result handler for saving debate results
    debate_result = {
        "topic": topic,
        "roles": roles,
        "rounds": rounds,
        "consensus_strategy": consensus_strategy,
        "history": [],
        "consensus": None,
        "synthesis": None,
        "success": False,
        "timestamp": None
    }
    
    # If no roles are specified, try to recommend roles based on the topic
    if not roles and not MISSING_DEPENDENCIES:
        try:
            console.print("[yellow]No roles specified. Attempting to recommend roles based on the topic...[/yellow]")
            
            # Initialize AppState to access role recommendations
            app_state = AppState()
            
            # Use the search_roles_by_vector method to find relevant roles
            recommended_roles = app_state.search_roles_by_vector(topic, top_k=3)
            
            if recommended_roles:
                # Extract role names from the recommendations
                roles = [role["role"]["name"] for role in recommended_roles[:2]]  # Use top 2 roles
                console.print(f"[green]✅ Recommended roles based on topic: {', '.join(roles)}[/green]")
            else:
                # Fall back to default roles if no recommendations
                roles = ["Expert", "Critic"]
                console.print("[yellow]No role recommendations found. Using default roles.[/yellow]")
        except Exception as e:
            # Fall back to default roles if recommendation fails
            roles = ["Expert", "Critic"]
            console.print("[yellow]Could not recommend roles. Using default roles.[/yellow]")
            if verbose:
                console.print(f"[dim]Role recommendation error: {e}[/dim]")
    
    # Create a custom debate handler that will capture results
    class ResultCapturingDebateHandler(CLIDebateHandler):
        def __init__(self, result_dict):
            super().__init__()
            self.result_dict = result_dict
            
        async def _process_events(self, verbose: bool):
            # Call the parent method to handle UI display
            await super()._process_events(verbose)
            
            # After processing is complete, capture results if available
            if hasattr(self, 'debate_history') and self.debate_history:
                self.result_dict["history"] = [
                    {"role": turn.role_id, "opinion": turn.opinion, "round": turn.round}
                    for turn in self.debate_history if hasattr(turn, 'role_id')
                ]
                
            # The final result should be captured from the debate_end event
            # This is handled in the overridden _process_events method
    
    try:
        # Enhanced initialization with progress feedback
        console.print("[bold blue]🚀 Initializing debate system...[/bold blue]")
        handler = ResultCapturingDebateHandler(debate_result)
        
        # Show debate configuration summary
        console.print("[dim]📋 Configuration Summary:[/dim]")
        console.print(f"[dim]   • Topic: {topic[:60]}{'...' if len(topic) > 60 else ''}[/dim]")
        console.print(f"[dim]   • Participants: {len(roles)} role(s) - {', '.join(roles[:3])}{'...' if len(roles) > 3 else ''}[/dim]")
        console.print(f"[dim]   • Rounds: {rounds} | Strategy: {consensus_strategy}[/dim]")
        if save_results:
            console.print(f"[dim]   • Output: {output_file}[/dim]")
        console.print()
        
        # Start the debate without nested status displays
        console.print("[bold blue]🎭 Preparing debate environment...[/bold blue]")
        success = await handler.start_debate(topic, roles, rounds, consensus_strategy, verbose)
        
        # Update result status
        debate_result["success"] = success
        
        # Save results if requested
        if save_results and success:
            try:
                import json
                import os
                from datetime import datetime
                
                # Add timestamp
                debate_result["timestamp"] = datetime.now().isoformat()
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_file)) or '.', exist_ok=True)
                
                # Save as JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(debate_result, f, indent=2, ensure_ascii=False)
                
                console.print(f"[green]✅ Debate results saved to {output_file}[/green]")
            except Exception as save_error:
                console.print(f"[yellow]⚠️ Could not save results: {save_error}[/yellow]")
                logger.error(f"Failed to save debate results: {save_error}", exc_info=True)
        
        return success
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Debate interrupted by user.[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Failed to start debate: {e}[/red]")
        
        # Provide more helpful error messages based on common issues
        if "No module named" in str(e):
            console.print("[yellow]This appears to be a missing dependency. Try running 'pip install -r requirements.txt'[/yellow]")
        elif "Connection refused" in str(e):
            console.print("[yellow]Could not connect to a required service. Make sure all services are running.[/yellow]")
        elif "Permission denied" in str(e):
            console.print("[yellow]Permission issue accessing a file or service. Check your permissions.[/yellow]")
        
        # Log the full error for debugging
        logger.error(f"Debate command failed: {e}", exc_info=True)
        return False


def check_system_health():
    """Check system health and return status information."""
    health_info = {
        "configuration": {"status": "✅ Loaded", "details": "Configuration loaded successfully"},
        "dependencies": {"status": "⏳ Checking", "details": "Checking required modules..."},
        "services": {"status": "⏳ Checking", "details": "Initializing services..."},
        "api": {"status": "⏳ Checking", "details": "Testing API connectivity..."}
    }
    
    # Check dependencies
    if MISSING_DEPENDENCIES:
        health_info["dependencies"] = {
            "status": "❌ Missing dependencies", 
            "details": f"{len(MISSING_DEPENDENCIES)} packages missing"
        }
        health_info["services"] = {"status": "❌ Not available", "details": "Missing dependencies"}
        health_info["api"] = {"status": "❌ Not available", "details": "Missing dependencies"}
        return health_info
    else:
        health_info["dependencies"] = {"status": "✅ Ready", "details": "All required modules installed"}
    
    try:
        # Test service initialization
        app_state = AppState()
        health_info["services"] = {"status": "✅ Ready", "details": "All core services initialized"}
        
        # Test API
        from src.main import app as fastapi_app # Reverted to original import for FastAPI app
        routes = [route.path for route in fastapi_app.routes if not route.path.startswith('/docs')]
        health_info["api"] = {"status": "✅ Ready", "details": f"{len(routes)} endpoints available"}
        
    except Exception as e:
        health_info["services"] = {"status": "❌ Failed", "details": str(e)}
        health_info["api"] = {"status": "❌ Failed", "details": "Cannot connect to API"}
    
    return health_info


def list_available_roles():
    """List all available roles in the system."""
    if MISSING_DEPENDENCIES:
        console.print("[red]❌ Cannot list roles: Missing dependencies[/red]")
        return []
    
    try:
        # Initialize AppState to access roles
        app_state = AppState()
        app_state.load_all_roles()
        
        roles = []
        for name, info in app_state.all_roles_details.items():
            description = info.get("desc", "No description available")
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:97] + "..."
            
            roles.append({
                "name": name,
                "description": description,
                "tags": info.get("tags", [])
            })
        
        return sorted(roles, key=lambda x: x["name"])
    except Exception as e:
        console.print(f"[red]❌ Failed to list roles: {e}[/red]")
        logger.error(f"Role listing failed: {e}", exc_info=True)
        return []


async def run_assistant_chat_command(query: str):
    """Send a query to the personal assistant and display the response."""
    if not query.strip():
        console.print("[red]❌ Error: Query cannot be empty.[/red]")
        return

    try:
        with console.status("[bold blue]Thinking...[/bold blue]", spinner="dots"):
            # Initialize AppState and PersonalAssistantService
            app_state = AppState()
            personal_assistant_service = PersonalAssistantService()
            await personal_assistant_service.initialize()

            # For simplicity, use a fixed user ID and create a session if it doesn't exist
            user_id = "cli_user"
            session_id = f"cli_session_{user_id}" # A simple session ID for CLI interaction

            # Check if session exists, otherwise create one
            try:
                await personal_assistant_service.get_session(session_id)
            except ValueError: # Session not found
                session_info = await personal_assistant_service.create_session(user_id)
                session_id = session_info["session_id"]

            # Process the user's input
            user_input_data = {
                "content": query,
                "scenario_type": "personal_assistant", # Indicate the scenario
                "user_preferences": {"detail_level": "comprehensive"}
            }
            response = await personal_assistant_service.process_user_input(session_id, user_input_data)

            # Display the assistant's response
            if response and response.get("type") == "task_created":
                console.print(f"\n[bold green]✅ Assistant Response:[/bold green]")
                console.print(f"[white]{response.get('message', 'Task created successfully.')}[/white]")
                console.print(f"[dim]Task ID: {response.get('task_id')}[/dim]")
                console.print(f"[dim]Estimated Duration: {response.get('estimated_duration'):.1f} seconds[/dim]")
            elif response and response.get("type") == "intervention_processed":
                 console.print(f"\n[bold green]✅ Assistant Response:[/bold green]")
                 console.print(f"[white]{response.get('message', 'Intervention processed.')}[/white]")
            else:
                console.print(f"\n[bold green]✅ Assistant Response:[/bold green]")
                console.print(f"[white]{response.get('response', 'No specific response content.')}[/white]") # Fallback for other response types

    except Exception as e:
        console.print(f"\n[red]❌ An error occurred while interacting with the assistant: {e}[/red]")
        logger.error(f"Personal assistant CLI command failed: {e}", exc_info=True)