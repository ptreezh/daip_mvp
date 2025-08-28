# -*- coding: utf-8 -*- 
"""@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : main.py
@Description: Main CLI entry point for DAIP-LIVE system.
"""

import asyncio
import logging
import re
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

# Initialize console for rich output
console = Console() # Added this line

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import settings
from src.cli.commands.system_commands import check_system_health
from src.cli.commands.role_commands import role_app
from src.cli.commands.workflow_commands import workflow_app
from src.cli.chat_commands import app as chat_app
from src.cli.wiki_commands import app as wiki_app

# Service imports moved to src.cli.service_utils to avoid circular imports

from src.cli.service_utils import get_personal_assistant_router

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

def validate_input(text: str, min_length: int = 1, max_length: int = 1000, field_name: str = "input") -> str:
    """Validate input text with length and content checks."""
    if not text or not text.strip():
        raise typer.BadParameter(f"{field_name} cannot be empty")
    
    text = text.strip()
    if len(text) < min_length:
        raise typer.BadParameter(f"{field_name} must be at least {min_length} characters")
    if len(text) > max_length:
        raise typer.BadParameter(f"{field_name} must not exceed {max_length} characters")
    
    # Basic XSS prevention
    if re.search(r'<script|javascript:|data:', text, re.IGNORECASE):
        raise typer.BadParameter(f"{field_name} contains potentially unsafe content")
    
    return text

def validate_file_path(path: str, must_exist: bool = False) -> Path:
    """Validate file path for security and existence."""
    try:
        file_path = Path(path).resolve()
        
        # Prevent path traversal
        if ".." in str(file_path) or str(file_path).startswith("/"):
            raise typer.BadParameter("Invalid file path: path traversal detected")
        
        if must_exist and not file_path.exists():
            raise typer.BadParameter(f"File does not exist: {path}")
        
        return file_path
    except Exception as e:
        raise typer.BadParameter(f"Invalid file path: {e}") from e

# Add Personal Assistant commands
@pa_app.command("chat")
def pa_chat(query: str = typer.Argument(..., help="The query for the Personal Assistant.")):
    """Interact with the personal assistant."""
    try:
        validated_query = validate_input(query, min_length=2, max_length=5000, field_name="Query")
        router = get_personal_assistant_router()
        asyncio.run(router.process_query(validated_query))
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")
        raise typer.Exit(code=1) from e

@pa_app.command("status")
def pa_status(task_id: str = typer.Argument(..., help="The ID of the task to check status for.")):
    """Check the status of a complex task."""
    try:
        validated_task_id = validate_input(task_id, min_length=1, max_length=100, field_name="Task ID")
        router = get_personal_assistant_router()
        asyncio.run(router.get_task_status(validated_task_id))
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")
        raise typer.Exit(code=1) from e

@pa_app.command("logs")
def pa_logs(limit: int = typer.Option(10, "--limit", "-l", help="Number of log entries to retrieve.")):
    """View recent log entries from the personal assistant."""
    router = get_personal_assistant_router()
    asyncio.run(router.get_logs(limit))


# Create a Typer application for the 'debate' command group
debate_app = typer.Typer(
    name="debate",
    help="Commands for managing debates.",
    add_completion=False,
)
app.add_typer(debate_app, name="debate")
app.add_typer(role_app, name="roles")
app.add_typer(workflow_app, name="workflow")
app.add_typer(chat_app, name="chat")
app.add_typer(wiki_app, name="wiki")


# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@debate_app.command()
def start(
    topic: str = typer.Argument(..., help="The debate topic"),
    roles: Optional[list[str]] = typer.Option(None, "--role", "-r", help="AI roles to participate in the debate"),
    rounds: int = typer.Option(None, "--rounds", help="Number of debate rounds"),
    consensus_strategy: str = typer.Option(None, "--consensus", help="Consensus strategy to use"),
    verbose: bool = typer.Option(None, "--verbose", "-v", help="Enable verbose output"),
    save: bool = typer.Option(None, "--save", "-s", help="Save debate results to a file"),
    output: str = typer.Option(None, "--output", "-o", help="Output file for saved results"),
):
    """Start a new debate with specified topic and roles."""
    # Set default values
    if roles is None:
        roles = []
    if rounds is None:
        rounds = 3
    if consensus_strategy is None:
        consensus_strategy = "simple_majority_vote"
    if verbose is None:
        verbose = False
    if save is None:
        save = False
    if output is None:
        output = "debate_results.txt"
        
    from src.cli.debate_execution import run_debate_command
    
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
            output_path = validate_file_path(output)
            output_dir = output_path.parent
            if output_dir and not output_dir.exists():
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    validation_errors.append(f"Cannot create output directory: {output_dir} (permission denied)")
                except Exception as e:
                    validation_errors.append(f"Cannot create output directory: {e}")
        except Exception as e:
            validation_errors.append(str(e))
    
    # Display validation errors if any
    if validation_errors:
        console.print("[red]❌ Input validation failed:[/red]")
        for error in validation_errors:
            console.print(f"[red]   • {error}[/red]")
        console.print("\n[yellow]💡 Use 'daip-cli help' for usage examples")
        raise typer.Exit(1)
    
    # Show startup information
    console.print(f"[bold blue]🚀 Initializing debate: {topic}[/bold blue]")
    if verbose:
        console.print(f"[dim]Parameters: rounds={rounds}, consensus={consensus_strategy}, save={save}[/dim]")
    
    try:
        # Run the debate asynchronously with save parameters
        with console.status("[bold blue]Starting debate system...[/bold blue]", spinner="dots"):
            success = asyncio.run(
                run_debate_command(
                    topic=topic, 
                    roles=roles, 
                    rounds=rounds, 
                    consensus_strategy=consensus_strategy, 
                    verbose=verbose,
                    save_results=save,
                    output_file=output
                )
            )
        
        if not success:
            console.print("\n[red]❌ Debate failed to complete successfully.[/red]")
            console.print("[yellow]💡 Troubleshooting tips:[/yellow]")
            console.print("   • Run with --verbose flag for detailed error information")
            console.print("   • Check system status with 'daip-cli status'")
            console.print("   • Try with fewer rounds or simpler topic")
            raise typer.Exit(1)
        else:
            console.print("\n[bold green]🎉 Debate completed successfully![/bold green]")
            if save:
                console.print(f"[green]📁 Results saved to: {output}[/green]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⏸️  Debate interrupted by user.[/yellow]")
        console.print("[dim]💡 You can resume a similar debate by running the same command again.")
        raise typer.Exit(0) from None
    except asyncio.TimeoutError:
        console.print("\n[red]⏱️  Debate timed out.[/red]")
        console.print("[yellow]💡 The debate took too long to complete. Try:[/yellow]")
        console.print("   • Reducing the number of rounds")
        console.print("   • Using fewer participants")
        console.print("   • Checking your internet connection")
        raise typer.Exit(1)
    except MemoryError:
        console.print("\n[red]💾 System ran out of memory.[/red]")
        console.print("[yellow]💡 Try reducing the complexity:[/yellow]")
        console.print("   • Use fewer rounds (--rounds 2)")
        console.print("   • Use fewer roles")
        console.print("   • Close other applications")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        
        # Enhanced error categorization and suggestions
        error_str = str(e).lower()
        if "no module named" in error_str:
            console.print("[yellow]🔧 Missing dependency detected:[/yellow]")
            console.print("   • Run: pip install -r requirements.txt")
            console.print("   • Or: pip install daip-live")
        elif "connection refused" in error_str or "connection error" in error_str:
            console.print("[yellow]🌐 Connection issue detected:[/yellow]")
            console.print("   • Check if LLM server is running (e.g., Ollama)")
            console.print("   • Verify network connectivity")
            console.print("   • Check firewall settings")
        elif "permission denied" in error_str:
            console.print("[yellow]🔒 Permission issue detected:[/yellow]")
            console.print("   • Check file/directory permissions")
            console.print("   • Try running with appropriate privileges")
            console.print("   • Ensure output directory is writable")
        elif "config" in error_str or "settings" in error_str:
            console.print("[yellow]⚙️  Configuration issue detected:[/yellow]")
            console.print("   • Check config.yaml file")
            console.print("   • Run 'daip-cli status' to verify configuration")
            console.print("   • Ensure all required settings are present")
        else:
            console.print("[yellow]💡 General troubleshooting:[/yellow]")
            console.print("   • Run 'daip-cli status' to check system health")
            console.print("   • Try with --verbose flag for more details")
            console.print("   • Check the logs for more information")
        
        # Log the full error for debugging
        logger.error(f"CLI start command failed: {e}", exc_info=True)
        raise typer.Exit(1) from e


@debate_app.command()
def export_to_wiki(
    debate_id: str = typer.Argument(..., help="The ID or topic of the debate to export"),
    title: str = typer.Option(None, "--title", "-t", help="Title for the wiki page (defaults to debate topic)"),
    format: str = typer.Option("markdown", "--format", "-f", help="Wiki format (markdown, html)"),
):
    """Export debate results to a wiki page."""
    from rich.console import Console
    console = Console()
    
    try:
        # Import the debate export functionality
        from src.cli.commands.debate_commands import export_debate_to_wiki
        
        # Generate default title if not provided
        if not title:
            title = f"Debate: {debate_id}"
        
        console.print(f"[bold blue]EXPORTING: Exporting debate '{debate_id}' to wiki...[/bold blue]")
        
        # Perform the export
        success = export_debate_to_wiki(
            debate_id=debate_id,
            wiki_title=title,
            format=format
        )
        
        if success:
            console.print(f"[green]SUCCESS: Debate successfully exported to wiki page: '{title}'")
        else:
            console.print("[red]ERROR: Failed to export debate to wiki")
            console.print("[yellow]TIP: Make sure the debate was completed and results were saved")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]ERROR: Error exporting debate to wiki: {e}[/red]")
        logger.error(f"Debate export to wiki failed: {e}", exc_info=True)
        raise typer.Exit(1) from e


@debate_app.command("view-disagreements")
def view_disagreements(
    debate_id: str = typer.Argument(..., help="The ID or topic of the debate to analyze"),
):
    """View key disagreement points in a debate."""
    from rich.console import Console
    console = Console()
    
    try:
        # Import the debate analysis functionality
        from src.cli.commands.debate_commands import view_debate_disagreements
        
        console.print(f"[bold blue]ANALYZING: Analyzing disagreements in debate '{debate_id}'...[/bold blue]")
        
        # Perform the analysis
        success = view_debate_disagreements(debate_id)
        
        if not success:
            console.print("[red]ERROR: Failed to analyze debate disagreements")
            console.print("[yellow]TIP: Make sure the debate was completed and results were saved")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]ERROR: Error analyzing debate disagreements: {e}[/red]")
        logger.error(f"Debate disagreement analysis failed: {e}", exc_info=True)
        raise typer.Exit(1) from e


@debate_app.command("select-consensus-algorithm")
def select_consensus_algorithm(
    debate_id: str = typer.Argument(..., help="The ID or topic of the debate"),
    algorithm_name: str = typer.Argument(..., help="Name of the consensus algorithm to use"),
):
    """Select or change the consensus algorithm for a debate."""
    from rich.console import Console
    console = Console()
    
    try:
        # Import the consensus algorithm selection functionality
        from src.cli.commands.debate_commands import select_consensus_algorithm
        
        console.print(f"[bold blue]UPDATING: Setting consensus algorithm for debate '{debate_id}' to '{algorithm_name}'...[/bold blue]")
        
        # Perform the selection
        success = select_consensus_algorithm(debate_id, algorithm_name)
        
        if not success:
            console.print("[red]ERROR: Failed to select consensus algorithm")
            console.print("[yellow]TIP: Valid algorithms are: simple_majority_vote, weighted_vote, consensus_building, expert_judgment")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]ERROR: Error selecting consensus algorithm: {e}[/red]")
        logger.error(f"Consensus algorithm selection failed: {e}", exc_info=True)
        raise typer.Exit(1) from e


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
        from src.cli.debate_execution import MISSING_DEPENDENCIES
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
        console.print("[yellow]   • Fix missing dependencies first")
        console.print("[yellow]   • Check configuration files")
        console.print("[yellow]   • Run this status check again after fixes")


@app.command()
def help():
    """Show detailed help and usage examples."""
    console.print("[bold blue]DAIP-LIVE CLI Help[/bold blue]")
    console.print()
    
    console.print("[bold]Available Commands:[/bold]")
    console.print("  [cyan]start[/cyan]   - Start a new debate")
    console.print("  [cyan]roles[/cyan]   - List available roles for debates")
    console.print("  [cyan]status[/cyan]  - Check system status")
    console.print("  [cyan]pa[/cyan]      - Commands for the Personal Assistant")
    console.print("  [cyan]debate[/cyan]  - Debate management commands")
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
    console.print("  # View debate disagreements")
    console.print("  [dim]daip-cli debate view-disagreements 'AI Ethics Debate'[/dim]")
    console.print()
    console.print("  # Select consensus algorithm for a debate")
    console.print("  [dim]daip-cli debate select-consensus-algorithm 'AI Ethics Debate' weighted_vote[/dim]")
    console.print()
    console.print("  # Export debate to wiki")
    console.print("  [dim]daip-cli debate export-to-wiki 'AI Ethics Debate' --title 'AI Ethics Analysis'[/dim]")
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
    router = get_personal_assistant_router()
    sessions = router.get_session_list() # Removed asyncio.run()
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


from src.cli.interactive_cli import main_menu_loop

if __name__ == "__main__":
    # If no arguments are provided, run the interactive menu
    if len(sys.argv) == 1:
        main_menu_loop()
    else:
        app()
