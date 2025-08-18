"""@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : main.py
@Description: Main CLI entry point for DAIP-LIVE system.
"""

import asyncio
import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

# Initialize console for rich output
console = Console() # Added this line

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import settings
from src.config import settings
from src.config import settings
from src.cli.commands import check_system_health # Moved import to top

# New imports for core services
from src.application.personal_assistant_router import PersonalAssistantRouter
from src.core_services.user_profile_service import UserProfileService
from src.core_services.intent_analysis_service import BasicIntentAnalysisService
from src.core_services.role_manager import RoleManager
from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.memory_agent import MemAgent
from src.core_services.real_llm_context_optimizer import RealLLMClient, IntelligentContextOptimizer
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.core_services.task_manager import TaskManager
from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.workflow_engine import WorkflowEngine

# Initialize core services (order matters due to dependencies)
# Note: Some services might have their own dependencies that need to be initialized first.
# This is a simplified instantiation for CLI purposes.
user_profile_service = UserProfileService()
intent_analysis_service = BasicIntentAnalysisService(user_profile_service=user_profile_service)

role_manager = RoleManager()

# EnhancedSSKGManager needs a path for persistence
enhanced_sskg_manager = EnhancedSSKGManager(graph_path=Path("data/sskg_graph.graphml"), vector_store_path=Path("data/sskg_vector_store"))
mem_agent = MemAgent(sskg_manager=enhanced_sskg_manager)

# RealLLMClient and IntelligentContextOptimizer are instantiated internally by IntegratedLLMManager
# We pass the necessary dependencies to IntegratedLLMManager
integrated_llm_manager = IntegratedLLMManager() # This will initialize its own context_optimizer, role_manager, mem_agent

task_manager = TaskManager()

primitive_registry = PrimitiveRegistry()
workflow_engine = WorkflowEngine(primitive_registry=primitive_registry)

# Initialize PersonalAssistantRouter
personal_assistant_router = PersonalAssistantRouter(
    intent_analysis_service=intent_analysis_service,
    llm_manager=integrated_llm_manager,
    workflow_engine=workflow_engine,
    task_manager=task_manager
)

def version_callback(value: bool):
    if value:
        print(f"DAIP-LIVE CLI Version: {settings.version}")
        raise typer.Exit()

# Initialize CLI app and console
app = typer.Typer(
    name="daip-cli",
    help="DAIP-LIVE CLI - Dynamic AI-driven Project-execution LIVE system",
    add_completion=False,
)

@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the CLI version and exit.",
    )
):
    # This function will be called before any command.
    # The 'version' option is handled by its callback.
    pass

# Create a Typer application for the 'pa' command group (Personal Assistant)
pa_app = typer.Typer(
    name="pa",
    help="Commands for interacting with the Personal Assistant.",
    add_completion=False,
)
app.add_typer(pa_app, name="pa")

# Add Personal Assistant commands
@pa_app.command("chat")
def pa_chat(query: str = typer.Argument(..., help="The query for the Personal Assistant.")):
    """Interact with the personal assistant."""
    asyncio.run(personal_assistant_router.process_query(query))

@pa_app.command("status")
def pa_status(task_id: str = typer.Argument(..., help="The ID of the task to check status for.")):
    """Check the status of a complex task."""
    asyncio.run(personal_assistant_router.get_task_status(task_id))

@pa_app.command("logs")
def pa_logs(limit: int = typer.Option(10, "--limit", "-l", help="Number of log entries to retrieve.")):
    """View recent log entries from the personal assistant."""
    asyncio.run(personal_assistant_router.get_logs(limit))


# New imports for core services
from src.application.personal_assistant_router import PersonalAssistantRouter
from src.core_services.user_profile_service import UserProfileService
from src.core_services.intent_analysis_service import BasicIntentAnalysisService
from src.core_services.role_manager import RoleManager
from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.memory_agent import MemAgent
from src.core_services.real_llm_context_optimizer import RealLLMClient, IntelligentContextOptimizer
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.core_services.task_manager import TaskManager
from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.workflow_engine import WorkflowEngine

# Initialize core services (order matters due to dependencies)
# Note: Some services might have their own dependencies that need to be initialized first.
# This is a simplified instantiation for CLI purposes.
user_profile_service = UserProfileService()
intent_analysis_service = BasicIntentAnalysisService(user_profile_service=user_profile_service)

role_manager = RoleManager()

# EnhancedSSKGManager needs a path for persistence
enhanced_sskg_manager = EnhancedSSKGManager(graph_path=Path("data/sskg_graph.graphml"), vector_store_path=Path("data/sskg_vector_store"))
mem_agent = MemAgent(sskg_manager=enhanced_sskg_manager)

# RealLLMClient and IntelligentContextOptimizer are instantiated internally by IntegratedLLMManager
# We pass the necessary dependencies to IntegratedLLMManager
integrated_llm_manager = IntegratedLLMManager() # This will initialize its own context_optimizer, role_manager, mem_agent

task_manager = TaskManager()

primitive_registry = PrimitiveRegistry()
workflow_engine = WorkflowEngine(primitive_registry=primitive_registry)

# Initialize PersonalAssistantRouter
personal_assistant_router = PersonalAssistantRouter(
    intent_analysis_service=intent_analysis_service,
    llm_manager=integrated_llm_manager,
    workflow_engine=workflow_engine,
    task_manager=task_manager
)

def version_callback(value: bool):
    if value:
        print(f"DAIP-LIVE CLI Version: {settings.version}")
        raise typer.Exit()

# Initialize CLI app and console
app = typer.Typer(
    name="daip-cli",
    help="DAIP-LIVE CLI - Dynamic AI-driven Project-execution LIVE system",
    add_completion=False,
)

@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the CLI version and exit.",
    )
):
    # This function will be called before any command.
    # The 'version' option is handled by its callback.
    pass

# Create a Typer application for the 'pa' command group (Personal Assistant)
pa_app = typer.Typer(
    name="pa",
    help="Commands for interacting with the Personal Assistant.",
    add_completion=False,
)
app.add_typer(pa_app, name="pa")

# Add Personal Assistant commands
@pa_app.command("chat")
def pa_chat(query: str = typer.Argument(..., help="The query for the Personal Assistant.")):
    """Interact with the personal assistant."""
    asyncio.run(personal_assistant_router.process_query(query))

@pa_app.command("status")
def pa_status(task_id: str = typer.Argument(..., help="The ID of the task to check status for.")):
    """Check the status of a complex task."""
    asyncio.run(personal_assistant_router.get_task_status(task_id))

@pa_app.command("logs")
def pa_logs(limit: int = typer.Option(10, "--limit", "-l", help="Number of log entries to retrieve.")):
    """View recent log entries from the personal assistant."""
    asyncio.run(personal_assistant_router.get_logs(limit))


# New imports for core services
from src.application.personal_assistant_router import PersonalAssistantRouter
from src.core_services.user_profile_service import UserProfileService
from src.core_services.intent_analysis_service import BasicIntentAnalysisService
from src.core_services.role_manager import RoleManager
from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.memory_agent import MemAgent
from src.core_services.real_llm_context_optimizer import RealLLMClient, IntelligentContextOptimizer
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.core_services.task_manager import TaskManager
from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.workflow_engine import WorkflowEngine

# Initialize core services (order matters due to dependencies)
# Note: Some services might have their own dependencies that need to be initialized first.
# This is a simplified instantiation for CLI purposes.
user_profile_service = UserProfileService()
intent_analysis_service = BasicIntentAnalysisService(user_profile_service=user_profile_service)

role_manager = RoleManager()

# EnhancedSSKGManager needs a path for persistence
enhanced_sskg_manager = EnhancedSSKGManager(graph_path=Path("data/sskg_graph.graphml"), vector_store_path=Path("data/sskg_vector_store"))
mem_agent = MemAgent(sskg_manager=enhanced_sskg_manager)

# RealLLMClient and IntelligentContextOptimizer are instantiated internally by IntegratedLLMManager
# We pass the necessary dependencies to IntegratedLLMManager
integrated_llm_manager = IntegratedLLMManager() # This will initialize its own context_optimizer, role_manager, mem_agent

task_manager = TaskManager()

primitive_registry = PrimitiveRegistry()
workflow_engine = WorkflowEngine(primitive_registry=primitive_registry)

# Initialize PersonalAssistantRouter
personal_assistant_router = PersonalAssistantRouter(
    intent_analysis_service=intent_analysis_service,
    llm_manager=integrated_llm_manager,
    workflow_engine=workflow_engine,
    task_manager=task_manager
)

def version_callback(value: bool):
    if value:
        print(f"DAIP-LIVE CLI Version: {settings.version}")
        raise typer.Exit()

# Initialize CLI app and console
app = typer.Typer(
    name="daip-cli",
    help="DAIP-LIVE CLI - Dynamic AI-driven Project-execution LIVE system",
    add_completion=False,
)

@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the CLI version and exit.",
    )
):
    # This function will be called before any command.
    # The 'version' option is handled by its callback.
    pass

# Create a Typer application for the 'pa' command group (Personal Assistant)
pa_app = typer.Typer(
    name="pa",
    help="Commands for interacting with the Personal Assistant.",
    add_completion=False,
)
app.add_typer(pa_app, name="pa")

# Add Personal Assistant commands
@pa_app.command("chat")
def pa_chat(query: str = typer.Argument(..., help="The query for the Personal Assistant.")):
    """Interact with the personal assistant."""
    asyncio.run(personal_assistant_router.process_query(query))

@pa_app.command("status")
def pa_status(task_id: str = typer.Argument(..., help="The ID of the task to check status for.")):
    """Check the status of a complex task."""
    asyncio.run(personal_assistant_router.get_task_status(task_id))

@pa_app.command("logs")
def pa_logs(limit: int = typer.Option(10, "--limit", "-l", help="Number of log entries to retrieve.")):
    """View recent log entries from the personal assistant."""
    asyncio.run(personal_assistant_router.get_logs(limit))


# Create a Typer application for the 'debate' command group
debate_app = typer.Typer(
    name="debate",
    help="Commands for managing debates.",
    add_completion=False,
)
app.add_typer(debate_app, name="debate")

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@debate_app.command()
def start(
    topic: str = typer.Argument(..., help="The debate topic"),
    roles: list[str] = typer.Option([], "--role", "-r", help="AI roles to participate in the debate"),
    rounds: int = typer.Option(3, "--rounds", help="Number of debate rounds"),
    consensus_strategy: str = typer.Option("simple_majority_vote", "--consensus", help="Consensus strategy to use"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    save: bool = typer.Option(False, "--save", "-s", help="Save debate results to a file"),
    output: str = typer.Option("debate_results.txt", "--output", "-o", help="Output file for saved results"),
):
    """Start a new debate with specified topic and roles."""
    from src.cli.commands import run_debate_command
    
    # Enhanced input validation with detailed feedback
    validation_errors = []
    
    if rounds < 1:
        validation_errors.append("Number of rounds must be at least 1")
    elif rounds > 20:
        validation_errors.append("Number of rounds cannot exceed 20 (to prevent excessive resource usage)")
        
    if len(topic.strip()) < 3:
        validation_errors.append("Debate topic must be at least 3 characters long")
    elif len(topic.strip()) > 500:
        validation_errors.append("Debate topic is too long (maximum 500 characters)")
    
    # Validate consensus strategy
    valid_strategies = ["simple_majority_vote", "weighted_vote", "consensus_building", "expert_judgment"]
    if consensus_strategy not in valid_strategies:
        validation_errors.append(f"Invalid consensus strategy. Valid options: {', '.join(valid_strategies)}")
    
    # Validate output file path if saving
    if save:
        try:
            import os
            output_dir = os.path.dirname(os.path.abspath(output))
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except PermissionError:
                    validation_errors.append(f"Cannot create output directory: {output_dir} (permission denied)")
                except Exception as e:
                    validation_errors.append(f"Cannot create output directory: {e}")
        except Exception as e:
            validation_errors.append(f"Invalid output file path: {e}")
    
    # Display validation errors if any
    if validation_errors:
        console.print("[red]❌ Input validation failed:[/red]")
        for error in validation_errors:
            console.print(f"[red]   • {error}[/red]")
        console.print("\n[yellow]💡 Use 'daip-cli help' for usage examples[/yellow]")
        raise typer.Exit(1)
    
    # Show startup information
    console.print(f"[bold blue]🚀 Initializing debate: {topic}[/bold blue]")
    if verbose:
        console.print(f"[dim]Parameters: rounds={rounds}, consensus={consensus_strategy}, save={save}[/dim]")
    
    try:
        # Run the debate asynchronously with save parameters
        with console.status("[bold blue]Starting debate system...[/bold blue]", spinner="dots"):
            success = asyncio.run(run_debate_command(
                topic=topic, 
                roles=roles, 
                rounds=rounds, 
                consensus_strategy=consensus_strategy, 
                verbose=verbose,
                save_results=save,
                output_file=output
            ))
        
        if not success:
            console.print("\n[red]❌ Debate failed to complete successfully.[/red]")
            console.print("[yellow]💡 Troubleshooting tips:[/yellow]")
            console.print("[yellow]   • Run with --verbose flag for detailed error information[/yellow]")
            console.print("[yellow]   • Check system status with 'daip-cli status'[/yellow]")
            console.print("[yellow]   • Try with fewer rounds or simpler topic[/yellow]")
            raise typer.Exit(1)
        else:
            console.print("\n[bold green]🎉 Debate completed successfully![/bold green]")
            if save:
                console.print(f"[green]📁 Results saved to: {output}[/green]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⏸️  Debate interrupted by user.[/yellow]")
        console.print("[dim]💡 You can resume a similar debate by running the same command again.[/dim]")
        raise typer.Exit(0)
    except asyncio.TimeoutError:
        console.print("\n[red]⏱️  Debate timed out.[/red]")
        console.print("[yellow]💡 The debate took too long to complete. Try:[/yellow]")
        console.print("[yellow]   • Reducing the number of rounds[/yellow]")
        console.print("[yellow]   • Using fewer participants[/yellow]")
        console.print("[yellow]   • Checking your internet connection[/yellow]")
        raise typer.Exit(1)
    except MemoryError:
        console.print("\n[red]💾 System ran out of memory.[/red]")
        console.print("[yellow]💡 Try reducing the complexity:[/yellow]")
        console.print("[yellow]   • Use fewer rounds (--rounds 2)[/yellow]")
        console.print("[yellow]   • Use fewer roles[/yellow]")
        console.print("[yellow]   • Close other applications[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        
        # Enhanced error categorization and suggestions
        error_str = str(e).lower()
        if "no module named" in error_str:
            console.print("[yellow]🔧 Missing dependency detected:[/yellow]")
            console.print("[yellow]   • Run: pip install -r requirements.txt[/yellow]")
            console.print("[yellow]   • Or: pip install daip-live[/yellow]")
        elif "connection refused" in error_str or "connection error" in error_str:
            console.print("[yellow]🌐 Connection issue detected:[/yellow]")
            console.print("[yellow]   • Check if LLM server is running (e.g., Ollama)[/yellow]")
            console.print("[yellow]   • Verify network connectivity[/yellow]")
            console.print("[yellow]   • Check firewall settings[/yellow]")
        elif "permission denied" in error_str:
            console.print("[yellow]🔒 Permission issue detected:[/yellow]")
            console.print("[yellow]   • Check file/directory permissions[/yellow]")
            console.print("[yellow]   • Try running with appropriate privileges[/yellow]")
            console.print("[yellow]   • Ensure output directory is writable[/yellow]")
        elif "config" in error_str or "settings" in error_str:
            console.print("[yellow]⚙️  Configuration issue detected:[/yellow]")
            console.print("[yellow]   • Check config.yaml file[/yellow]")
            console.print("[yellow]   • Run 'daip-cli status' to verify configuration[/yellow]")
            console.print("[yellow]   • Ensure all required settings are present[/yellow]")
        else:
            console.print("[yellow]💡 General troubleshooting:[/yellow]")
            console.print("[yellow]   • Run 'daip-cli status' to check system health[/yellow]")
            console.print("[yellow]   • Try with --verbose flag for more details[/yellow]")
            console.print("[yellow]   • Check the logs for more information[/yellow]")
        
        # Log the full error for debugging
        logger.error(f"CLI start command failed: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command()
def status():
    """Check the system status and configuration."""
    console.print("[bold blue]🔍 DAIP-LIVE System Status[/bold blue]")
    
    # Create status table
    table = Table(title="System Configuration")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")
    
    overall_health = True
    health_info = check_system_health()

    # Add rows to the table based on health_info
    for component, info in health_info.items():
        status_icon = "✅" if "✅" in info["status"] else ("⚠️" if "⚠️" in info["status"] else "❌")
        table.add_row(component.replace("_", " ").title(), info["status"], info["details"])
        if "❌" in info["status"] or "⚠️" in info["status"]:
            overall_health = False

    console.print(table)

    # Show overall health status
    if overall_health:
        console.print("\n[bold green]🎉 System Status: HEALTHY[/bold green]")
        console.print("[green]All components are working correctly![/green]")
    else:
        console.print("\n[bold yellow]⚠️  System Status: NEEDS ATTENTION[/bold yellow]")
        console.print("[yellow]Some components require configuration or repair.[/yellow]")

    # If there are missing dependencies, show them with enhanced feedback
    if "dependencies" in health_info and "❌" in health_info["dependencies"]["status"]:
        console.print("\n[bold red]🔧 Missing Dependencies:[/bold red]")
        # Assuming MISSING_DEPENDENCIES is still accessible or passed
        from src.cli.commands import MISSING_DEPENDENCIES
        for dep in MISSING_DEPENDENCIES:
            console.print(f"[red]   • {dep}[/red]")

        console.print("\n[yellow]💡 Installation Options:[/yellow]")
        install_deps = [dep for dep in MISSING_DEPENDENCIES if not dep.startswith("No module named") and "Error" not in dep]
        if install_deps:
            console.print(f"[dim]   pip install {' '.join(install_deps)}[/dim]")
        console.print("[dim]   pip install -r requirements.txt[/dim]")
        console.print("[dim]   pip install daip-live[/dim]")

    # Final recommendations
    console.print("\n[bold]💡 Next Steps:[/bold]")
    if overall_health:
        console.print("[green]   • System is ready! Try: daip-cli start 'Your debate topic'[/green]")
        console.print("[green]   • View available roles: daip-cli roles[/green]")
    else:
        console.print("[yellow]   • Fix missing dependencies first[/yellow]")
        console.print("[yellow]   • Check configuration files[/yellow]")
        console.print("[yellow]   • Run this status check again after fixes[/yellow]")


@app.command()
def roles():
    """List available roles for debates."""
    # Check if the system supports Unicode emojis
    try:
        "🎭".encode("gbk")
        # If we get here, gbk supports the emoji
        console.print("[bold blue]🎭 DAIP-LIVE Available Roles[/bold blue]")
    except UnicodeEncodeError:
        # Fallback for systems that don't support emojis
        console.print("[bold blue]DAIP-LIVE Available Roles[/bold blue]")
    
    try:
        with console.status("[dim]Loading available roles...[/dim]", spinner="dots"):
            from src.cli.commands import list_available_roles
            available_roles = list_available_roles()
        
        if not available_roles:
            console.print("[yellow]⚠️  No roles available or could not access role information.[/yellow]")
            console.print("\n[yellow]💡 Troubleshooting:[/yellow]")
            console.print("[yellow]   • Check system status: daip-cli status[/yellow]")
            console.print("[yellow]   • Verify roles directory exists[/yellow]")
            console.print("[yellow]   • Check for missing dependencies[/yellow]")
            return
        
        # Create a table to display roles
        table = Table(title=f"Available Roles ({len(available_roles)})")
        table.add_column("Role Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Tags", style="dim")
        
        # Add roles to the table with error handling for malformed role data
        valid_roles = 0
        for role in available_roles:
            try:
                name = role.get("name", "Unknown")
                description = role.get("description", "No description available")
                tags = role.get("tags", [])
                
                # Truncate long descriptions for better display
                if len(description) > 80:
                    description = description[:77] + "..."
                
                tags_str = ", ".join(tags) if tags else ""
                table.add_row(name, description, tags_str)
                valid_roles += 1
            except Exception as e:
                logger.warning(f"Skipping malformed role data: {e}")
                continue
        
        if valid_roles == 0:
            console.print("[red]❌ No valid roles found in the system.[/red]")
            console.print("[yellow]💡 This may indicate corrupted role files or configuration issues.[/yellow]")
            return
        
        console.print(table)
        
        # Show usage information
        # Check if the system supports Unicode emojis
        try:
            "\U0001f4cb".encode("gbk")
            # If we get here, gbk supports the emoji
            emoji = "\U0001f4cb"
        except UnicodeEncodeError:
            # Fallback for systems that don't support emojis
            emoji = ""
        
        console.print(f"\n[bold]{emoji} Role Usage:[/bold]")
        console.print("[dim]   Use role names with the --role option when starting a debate.[/dim]")
        console.print("[dim]   Example: daip-cli start 'Topic' --role 'Expert' --role 'Critic'[/dim]")
        
        # Show statistics
        if valid_roles != len(available_roles):
            skipped = len(available_roles) - valid_roles
            console.print(f"\n[yellow]⚠️  {skipped} role(s) skipped due to data issues.[/yellow]")
        
        # Show role categories if tags are available
        all_tags = set()
        for role in available_roles:
            if isinstance(role.get("tags"), list):
                all_tags.update(role["tags"])
        
        if all_tags:
            # Check if the system supports Unicode emojis
            try:
                "🏷️".encode("gbk")
                # If we get here, gbk supports the emoji
                category_emoji = "🏷️"
            except UnicodeEncodeError:
                # Fallback for systems that don't support emojis
                category_emoji = ""
            
            console.print(f"\n[bold]{category_emoji} Available Categories:[/bold]")
            sorted_tags = sorted(list(all_tags))
            console.print(f"[dim]   {', '.join(sorted_tags[:10])}{'...' if len(sorted_tags) > 10 else ''}[/dim]")
            
    except ImportError as e:
        console.print(f"[red]❌ Cannot import role listing functionality: {e}[/red]")
        console.print("[yellow]💡 This usually indicates missing dependencies.[/yellow]")
        console.print("[yellow]   • Run: pip install -r requirements.txt[/yellow]")
        console.print("[yellow]   • Check system status: daip-cli status[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Failed to list roles: {e}[/red]")
        console.print("[yellow]💡 Troubleshooting:[/yellow]")
        console.print("[yellow]   • Check system status: daip-cli status[/yellow]")
        console.print("[yellow]   • Verify role files are accessible[/yellow]")
        console.print("[yellow]   • Try running with verbose logging[/yellow]")
        logger.error(f"Role listing failed: {e}", exc_info=True)


@app.command()
def help():
    """Show detailed help and usage examples."""
    console.print("[bold blue]DAIP-LIVE CLI Help[/bold blue]")
    console.print()
    
    console.print("[bold]Available Commands:[/bold]")
    console.print("  [cyan]start[/cyan]   - Start a new debate")
    console.print("  [cyan]roles[/cyan]   - List available roles for debates")
    console.print("  [cyan]status[/cyan]  - Check system status")
    console.print("  [cyan]pa[/cyan]        - Commands for the Personal Assistant")
    console.print("  [cyan]intv[/cyan]    - Provide an intervention to the current session.")
    console.print("  [cyan]cons[/cyan]    - Get consensus information for the current session.")
    console.print("  [cyan]disag[/cyan]   - Get key disagreement points for the current session.")
    console.print("  [cyan]sess[/cyan]    - List all sessions.")
    console.print("  [cyan]help[/cyan]    - Show this help message")
    console.print()
    
    console.print("[bold]Usage Examples:[/bold]")
    console.print("  # Start a simple debate")
    console.print("  [dim]daip-cli start 'Should AI have rights?'[/dim]")
    console.print()
    console.print("  # Start a debate with specific roles")
    console.print("  [dim]daip-cli start 'Climate change solutions' --role 'Environmental Scientist' --role 'Economist'[/dim]")
    console.print()
    console.print("  # List available roles")
    console.print("  [dim]daip-cli roles[/dim]")
    console.print()
    console.print("  # Interact with the personal assistant")
    console.print("  [dim]daip-cli pa chat 'Summarize the latest AI research.'[/dim]")
    console.print()
    console.print("  # Check the status of a personal assistant task")
    console.print("  [dim]daip-cli pa status <task_id>[/dim]")
    console.print()
    console.print("  # View personal assistant logs")
    console.print("  [dim]daip-cli pa logs[/dim]")
    console.print()
    console.print("  # Start a longer debate with verbose output")
    console.print("  [dim]daip-cli start 'Future of work' --role 'Futurist' --role 'Labor Expert' --rounds 5 --verbose[/dim]")
    console.print()
    console.print("  # Check system status")
    console.print("  [dim]daip-cli status[/dim]")
    console.print()
    
    console.print("[bold]Tips:[/bold]")
    console.print("  • Use quotes around topics and role names that contain spaces")
    console.print("  • The --verbose flag shows detailed system operations")
    console.print("  • Multiple roles can be specified with multiple --role flags")
    console.print("  • Check 'daip-cli status' if you encounter issues")
    console.print("  • Use 'daip-cli roles' to see available roles for debates")





@app.command()
def intv(
    content: str = typer.Option(..., "--content", "-c", help="The content of the intervention."),
    intent: str = typer.Option("comment", "--intent", "-i", help="The intent of the intervention (comment, suggestion, correction, question).")
):
    """Provide an intervention to the current assistant session."""
    # This will need to interact with PersonalAssistantRouter or a dedicated service
    console.print(f"Intervention: {content} with intent: {intent}")
    # Placeholder for actual logic

@app.command()
def cons():
    """Get consensus information for the current session."""
    # This will need to interact with PersonalAssistantRouter or a dedicated service
    console.print("Getting consensus information...")
    # Placeholder for actual logic

@app.command()
def disag():
    """Get key disagreement points for the current session."""
    # This will need to interact with PersonalAssistantRouter or a dedicated service
    console.print("Getting disagreement points...")
    # Placeholder for actual logic

@app.command()
def sess():
    """List all sessions."""
    sessions = personal_assistant_router.get_session_list() # Removed asyncio.run()
    if not sessions:
        console.print("[yellow]No active sessions found.[/yellow]")
        return

    table = Table(title="Active Sessions")
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("User ID", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Last Activity", style="blue")

    for session_data in sessions:
        session_id = session_data.get("session_id", "N/A")
        user_id = session_data.get("user_id", "N/A")
        session_type = session_data.get("type", "N/A") # Assuming 'type' is available in session_data
        last_activity = session_data.get("last_activity", "N/A") # Assuming 'last_activity' is available

        table.add_row(session_id, user_id, session_type, last_activity)
    
    console.print(table)


from src.cli.interactive_cli import main_menu_loop, start_role_management

if __name__ == "__main__":
    # If no arguments are provided, run the interactive menu
    if len(sys.argv) == 1:
        main_menu_loop()
    else:
        app()