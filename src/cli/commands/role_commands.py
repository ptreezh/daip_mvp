"""
Role management commands for the DAIP CLI.
"""
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime

from src.core_services.role_manager import RoleManager, Role
from src.debate_system.debate_state_manager import DebateStateManager
from src.debate_system.debate_flow_definition import DebateParticipant, ParticipantRole

# Initialize console for rich output
console = Console()

# Create role management app
role_app = typer.Typer(help="Role management commands for DAIP-LIVE.")

@role_app.command("create")
def create_role(
    name: str = typer.Argument(..., help="Name of the new role"),
    description: str = typer.Option(..., "--description", help="Role description"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags")
):
    """Create a new AI role with specified attributes."""
    if not name or len(name.strip()) < 3:
        console.print("[red]Error: Role name must be at least 3 characters long and cannot be empty.[/red]")
        raise typer.Exit(code=1)

    try:
        role_manager = RoleManager()
        role_data = {
            "name": name,
            "description": description,
            "tags": [tag.strip() for tag in tags.split(",")] if tags else []
        }
        success = role_manager.create_role(role_data)
        if success:
            console.print(f"✅ Role '{name}' created successfully.")
        else:
            console.print(f"❌ Failed to create role '{name}'.")
            raise typer.Exit(code=1)
            
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)

@role_app.command("manage")
def manage_role(
    role_id: str = typer.Argument(..., help="ID of the role to manage"),
    update_description: Optional[str] = typer.Option(None, "--update-description", help="New description")
):
    """Update role attributes."""
    if update_description is not None and not update_description.strip():
        console.print("[red]Error: Description cannot be empty.[/red]")
        raise typer.Exit(code=1)

    try:
        role_manager = RoleManager()
        update_data = {}
        if update_description:
            update_data["description"] = update_description
        
        success = role_manager.update_role(role_id, update_data)
        if success:
            console.print(f"✅ Role '{role_id}' updated successfully")
        else:
            console.print(f"❌ Failed to update role '{role_id}'.")
            raise typer.Exit(code=1)
            
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)

@role_app.command("invite")
def invite_role(
    role_id: str = typer.Argument(..., help="The ID of the role to invite."),
    debate_id: str = typer.Option(..., "--debate-id", help="The ID of the debate to invite the role to.")
):
    """
    Invite a role to participate in a debate.
    """
    try:
        role_manager = RoleManager()
        debate_manager = DebateStateManager() # Corrected class name

        # 1. Validate Role ID
        role = role_manager.get_role_by_id(role_id)
        if not role:
            console.print(f"[red]Error: Role with ID '{role_id}' not found.[/red]")
            raise typer.Exit(code=1)

        # 2. Validate Debate ID
        # Note: DebateStateManager methods are async, but for CLI we run them synchronously.
        # This is a simplification for the CLI context.
        session = debate_manager.storage.load_session(debate_id) # Using sync storage method for simplicity
        if not session:
            console.print(f"[red]Error: Debate with ID '{debate_id}' not found.[/red]")
            raise typer.Exit(code=1)

        # 3. Check for duplicate invitations
        if any(p.participant_id == role.id for p in session.participants):
            console.print(f"[red]Error: Role '{role.name}' is already a participant in debate '{debate_id}'.[/red]")
            raise typer.Exit(code=1)

        # 4. Create DebateParticipant object and add it
        participant = DebateParticipant(
            participant_id=role.id,
            name=role.name,
            role=ParticipantRole.OBSERVER # Assign a default role
        )
        
        # Using sync storage method for simplicity
        session.participants.append(participant)
        success = debate_manager.storage.save_session(session)

        if success:
            console.print(f"[green]Successfully invited role '{role.name}' ({role.id}) to debate '{debate_id}'[/green]")
        else:
            console.print(f"[red]Error: Failed to invite role '{role.name}' to debate '{debate_id}'.[/red]")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)


@role_app.command("match")
def match_roles(
    task_description: str = typer.Argument(..., help="Description of the task to match roles for"),
    task_type: str = typer.Option("general", "--task-type", help="Type of task (general, debate, wiki_creation, analysis, creative)"),
    limit: int = typer.Option(5, "--limit", help="Maximum number of roles to return")
):
    """
    Match roles to a task based on expertise and capabilities.
    """
    try:
        role_manager = RoleManager()
        
        console.print(f"[bold blue]🔍 Matching roles to task: '{task_description}'[/bold blue]")
        console.print(f"[dim]Task type: {task_type}, Limit: {limit}[/dim]")
        
        # Get matched roles
        matched_roles = role_manager.match_roles_to_task(task_description, task_type, limit)
        
        if not matched_roles:
            console.print("[yellow]No roles found that match the task description.[/yellow]")
            console.print("[dim]Try using different keywords or a more general task description.[/dim]")
            return
        
        # Display results in a table
        table = Table(title=f"Top {len(matched_roles)} Role Matches")
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Role Name", style="magenta")
        table.add_column("Relevance", style="green")
        table.add_column("Domain", style="yellow")
        table.add_column("Match Reasons", style="dim")
        
        for i, match in enumerate(matched_roles, 1):
            role = match["role"]
            relevance_score = match["relevance_score"]
            match_reasons = match["match_reasons"]
            
            # Extract domain from role
            domain = role_manager._extract_domain_from_role(role)
            
            # Format relevance score
            relevance_str = f"{relevance_score:.2f}"
            if relevance_score >= 0.8:
                relevance_str = f"🟢 {relevance_str}"
            elif relevance_score >= 0.6:
                relevance_str = f"🟡 {relevance_str}"
            else:
                relevance_str = f"🔴 {relevance_str}"
            
            # Format match reasons (truncate if too long)
            reasons_str = ", ".join(match_reasons[:2])  # Show top 2 reasons
            if len(match_reasons) > 2:
                reasons_str += f" (+{len(match_reasons)-2} more)"
            
            table.add_row(
                str(i),
                role.name,
                relevance_str,
                domain.title(),
                reasons_str
            )
        
        console.print(table)
        
        # Show domain statistics
        stats = role_manager.get_domain_statistics()
        console.print(f"\n[dim]Domain Statistics: {stats['total_roles']} total roles across {len(stats['domains'])} domains[/dim]")
        
        # Show top domains
        top_domains = sorted(stats['domains'].items(), key=lambda x: x[1], reverse=True)[:5]
        domain_str = ", ".join([f"{domain} ({count})" for domain, count in top_domains])
        console.print(f"[dim]Top domains: {domain_str}[/dim]")
        
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        logger.error(f"Error matching roles: {e}")
        raise typer.Exit(code=1)


@role_app.command("stats")
def role_stats():
    """
    Show statistics about available roles and domains.
    """
    try:
        role_manager = RoleManager()
        
        console.print("[bold blue]📊 Role Domain Statistics[/bold blue]")
        
        # Get statistics
        stats = role_manager.get_domain_statistics()
        
        if "error" in stats:
            console.print(f"[red]Error getting statistics: {stats['error']}[/red]")
            raise typer.Exit(code=1)
        
        # Create summary table
        table = Table(title="Role Distribution Summary")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Roles", str(stats['total_roles']))
        table.add_row("Domains", str(len(stats['domains'])))
        table.add_row("Expertise Areas", str(len(stats['expertise_areas'])))
        table.add_row("Unique Capabilities", str(len(stats['capability_counts'])))
        table.add_row("Unique Tags", str(len(stats['tag_counts'])))
        
        console.print(table)
        
        # Show domain distribution
        console.print("\n[bold]Domain Distribution:[/bold]")
        
        domain_table = Table()
        domain_table.add_column("Domain", style="cyan", no_wrap=True)
        domain_table.add_column("Count", style="magenta")
        domain_table.add_column("Percentage", style="green")
        
        top_domains = sorted(stats['domains'].items(), key=lambda x: x[1], reverse=True)[:10]
        
        for domain, count in top_domains:
            percentage = (count / stats['total_roles']) * 100
            domain_table.add_row(domain.title(), str(count), f"{percentage:.1f}%")
        
        console.print(domain_table)
        
        # Show top expertise areas
        console.print("\n[bold]Top Expertise Areas:[/bold]")
        
        expertise_table = Table()
        expertise_table.add_column("Expertise Area", style="cyan", no_wrap=True)
        expertise_table.add_column("Count", style="magenta")
        
        top_expertise = sorted(stats['expertise_areas'].items(), key=lambda x: x[1], reverse=True)[:10]
        
        for expertise, count in top_expertise:
            expertise_table.add_row(expertise.title(), str(count))
        
        console.print(expertise_table)
        
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        logger.error(f"Error getting role stats: {e}")
        raise typer.Exit(code=1)

@role_app.command("list")
def list_roles():
    """List all available AI roles."""
    try:
        role_manager = RoleManager()
        roles = role_manager.list_roles()
        if not roles:
            console.print("[yellow]No roles available.[/yellow]")
            console.print("[bold]Troubleshooting:[/bold]")
            console.print("  - Ensure roles are defined in the `roles` directory.")
            console.print("  - Check file permissions for the `roles` directory.")
            return

        table = Table(title=f"DAIP-LIVE Available Roles ({len(roles)})")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Tags", style="blue")

        for role in roles:
            tags = ", ".join(role.tags) if role.tags else ""
            table.add_row(role.id, role.name, role.description, tags)

        console.print(table)

    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)

from src.cli.commands.utils import print_command_help

@role_app.command("help")
def roles_help():
    """Show detailed help for role management commands."""
    title = "Role Management Commands Help"
    description = "Manage AI roles within the DAIP-LIVE system."
    commands = [
        {"name": "list", "description": "List all available roles.", "example": "daip-cli roles list"},
        {"name": "create", "description": "Create a new role.", "example": "daip-cli roles create \"New Analyst\" --description \"A new analyst role.\" --tags \"analyst,finance\"" },
        {"name": "manage", "description": "Update an existing role.", "example": "daip-cli roles manage \"analyst\" --update-description \"An updated description.\""},
        {"name": "invite", "description": "Invite a role to a debate.", "example": "daip-cli roles invite \"analyst\" --debate-id \"debate_123\""},
        {"name": "match", "description": "Match roles to a task.", "example": "daip-cli roles match \"Analyze market trends for AI startups\""},
        {"name": "stats", "description": "Show role statistics.", "example": "daip-cli roles stats"},
        {"name": "help", "description": "Show this detailed help message.", "example": "daip-cli roles help"}
    ]
    print_command_help(title, description, commands)

