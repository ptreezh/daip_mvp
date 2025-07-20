# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : main.py
@Description: Main CLI entry point for DAIP-LIVE system.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import settings

# Initialize CLI app and console
app = typer.Typer(
    name="daip-cli",
    help="DAIP-LIVE CLI - Dynamic AI-driven Project-execution LIVE system",
    add_completion=False,
)
console = Console()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@app.command()
def start(
    topic: str = typer.Argument(..., help="The debate topic"),
    roles: List[str] = typer.Option([], "--role", "-r", help="AI roles to participate in the debate"),
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
    
    # Check configuration
    try:
        config_status = "✅ Loaded"
        config_details = f"Log Level: {settings.log_level}"
        table.add_row("Configuration", config_status, config_details)
    except Exception as e:
        config_status = "❌ Failed"
        config_details = f"Error: {str(e)[:50]}..."
        table.add_row("Configuration", config_status, config_details, style="red")
        overall_health = False
    
    # Check LLM configuration
    try:
        if hasattr(settings, 'llm') and settings.llm.provider:
            llm_status = "✅ Configured"
            llm_details = f"Provider: {settings.llm.provider}"
            if hasattr(settings.llm, 'ollama') and hasattr(settings.llm.ollama, 'generation_model'):
                llm_details += f", Model: {settings.llm.ollama.generation_model}"
        else:
            llm_status = "⚠️  Not configured"
            llm_details = "No LLM provider configured"
            overall_health = False
        table.add_row("LLM Provider", llm_status, llm_details)
    except Exception as e:
        llm_status = "❌ Error"
        llm_details = f"Configuration error: {str(e)[:40]}..."
        table.add_row("LLM Provider", llm_status, llm_details, style="red")
        overall_health = False
    
    # Check vector store
    try:
        if hasattr(settings, 'vector_store') and hasattr(settings.vector_store, 'chroma_db_path'):
            vector_status = "✅ Configured"
            vector_details = f"Path: {settings.vector_store.chroma_db_path}"
        else:
            vector_status = "⚠️  Not configured"
            vector_details = "Vector store path not set"
        table.add_row("Vector Store", vector_status, vector_details)
    except Exception as e:
        vector_status = "❌ Error"
        vector_details = f"Configuration error: {str(e)[:40]}..."
        table.add_row("Vector Store", vector_status, vector_details, style="red")
        overall_health = False
    
    # Check dependencies
    try:
        from src.cli.commands import MISSING_DEPENDENCIES
        if MISSING_DEPENDENCIES:
            dep_status = "❌ Missing dependencies"
            dep_details = f"{len(MISSING_DEPENDENCIES)} packages missing"
            table.add_row("Dependencies", dep_status, dep_details, style="red")
            overall_health = False
        else:
            table.add_row("Dependencies", "✅ All installed", "Required packages found")
    except Exception as e:
        dep_status = "❌ Check failed"
        dep_details = f"Cannot verify dependencies: {str(e)[:30]}..."
        table.add_row("Dependencies", dep_status, dep_details, style="red")
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
    try:
        from src.cli.commands import MISSING_DEPENDENCIES
        if MISSING_DEPENDENCIES:
            console.print("\n[bold red]🔧 Missing Dependencies:[/bold red]")
            for dep in MISSING_DEPENDENCIES:
                console.print(f"[red]   • {dep}[/red]")
            
            console.print("\n[yellow]💡 Installation Options:[/yellow]")
            # Filter out error messages that aren't actual package names
            install_deps = [dep for dep in MISSING_DEPENDENCIES if not dep.startswith("No module named") and not "Error" in dep]
            if install_deps:
                console.print(f"[dim]   pip install {' '.join(install_deps)}[/dim]")
            console.print("[dim]   pip install -r requirements.txt[/dim]")
            console.print("[dim]   pip install daip-live[/dim]")
    except Exception as e:
        console.print(f"\n[red]❌ Could not check dependencies: {e}[/red]")
    
    # Enhanced API connectivity test
    console.print("\n[bold]🌐 API Connectivity Test[/bold]")
    try:
        with console.status("[dim]Testing API import...[/dim]", spinner="dots"):
            from src.main import app as fastapi_app
        console.print("[green]✅ FastAPI application can be imported[/green]")
        
        # Count available routes
        try:
            routes = [route.path for route in fastapi_app.routes if not route.path.startswith('/docs')]
            console.print(f"[green]✅ {len(routes)} API endpoints available[/green]")
            
            # Show some example endpoints
            if routes:
                example_routes = routes[:3]  # Show first 3 routes
                console.print(f"[dim]   Example endpoints: {', '.join(example_routes)}[/dim]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not enumerate routes: {e}[/yellow]")
            
    except ImportError as e:
        console.print(f"[red]❌ API import failed: {e}[/red]")
        console.print("[yellow]💡 This usually indicates missing dependencies or configuration issues.[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ API connectivity issue: {e}[/red]")
        console.print("[yellow]💡 Check your configuration and dependencies.[/yellow]")
    
    # Service initialization test
    console.print("\n[bold]🔧 Service Initialization Test[/bold]")
    try:
        with console.status("[dim]Testing service initialization...[/dim]", spinner="dots"):
            from src.cli.commands import check_system_health
            health_info = check_system_health()
        
        for component, info in health_info.items():
            status_icon = "✅" if "✅" in info["status"] else ("⚠️" if "⚠️" in info["status"] else "❌")
            console.print(f"{status_icon} {component.title()}: {info['details']}")
            
    except Exception as e:
        console.print(f"[red]❌ Service test failed: {e}[/red]")
        console.print("[yellow]💡 Run with verbose logging to see detailed error information.[/yellow]")
    
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
    console.print("[bold blue]🎭 DAIP-LIVE Available Roles[/bold blue]")
    
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
        console.print(f"\n[bold]📋 Role Usage:[/bold]")
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
            console.print(f"\n[bold]🏷️  Available Categories:[/bold]")
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


if __name__ == "__main__":
    app()