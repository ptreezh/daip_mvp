"""
Role management commands for the DAIP CLI.
"""

import typer
from rich.console import Console

from src.core_services.role_manager import RoleManager
from src.debate_system.debate_state_manager import DebateStateManager
from src.debate_system.debate_flow_definition import DebateParticipant, ParticipantRole

# Initialize console for rich output
console = Console()

# Create role management app
role_app = typer.Typer(help="Role management commands for DAIP-LIVE.")

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
