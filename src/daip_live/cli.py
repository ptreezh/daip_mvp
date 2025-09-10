import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.config import (
    config_manager,
    create_config_yaml_if_not_exists,
)
from daip_live.core.models import ProviderConfig
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.persistence.database import DatabaseManager

# Import the SessionManager
from daip_live.tui import DAIP_TUI
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.scaffolding.manager import ScaffoldingManager

app = typer.Typer()
session_app = typer.Typer()
debate_app = typer.Typer()
role_app = typer.Typer()
app.add_typer(session_app, name="session", help="Manage and review past sessions.")
app.add_typer(debate_app, name="debate", help="Run and manage multi-agent debates.")
app.add_typer(role_app, name="role", help="Manage AI roles.")

project_app = typer.Typer()
app.add_typer(project_app, name="project", help="Manage and scaffold new projects.")

console = Console()


@project_app.command(name="scaffold", help="Generates project structure from a description.")
def project_scaffold(
    description: Annotated[str, typer.Option(help="A detailed description of the project goal, team, and SOP.")] = "",
    from_file: Annotated[str, typer.Option(help="Path to a file containing the project description.")] = "",
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation and proceed with generation.")] = False,
):
    """Generates project roles and workflows from a natural language description."""
    console.print("[yellow]Scaffolding project...[/yellow]")

    if from_file:
        try:
            with open(from_file) as f:
                description = f.read()
        except FileNotFoundError:
            console.print(f"[bold red]Error: File not found at {from_file}[/bold red]")
            raise typer.Exit(code=1)

    if not description:
        console.print("[bold red]Error: Project description is empty. Use --description or --from-file.[/bold red]")
        raise typer.Exit(code=1)

    cfg = config_manager.get_config()
    model_provider = LiteLLMProvider(config=cfg.llm_provider)
    scaffolder = ScaffoldingManager(model_provider)

    console.print("[cyan]Generating project structure from description...[/cyan]")
    try:
        parsed_structure = asyncio.run(scaffolder.generate_structure(description))

        console.print("--- [bold green]Plan for File Creation[/bold green] ---")
        for item in parsed_structure:
            console.print(
                Panel(
                    Syntax(item['content'], "yaml", theme="monokai", line_numbers=True),
                    title=f"[bold cyan]File:[/bold cyan] {item['filename']}",
                    border_style="green",
                    expand=False
                )
            )

        if not yes:
            typer.confirm("Do you want to create these files?", abort=True)

        console.print("\n[bold green]Creating files...[/bold green]")
        try:
            for item in parsed_structure:
                file_path = Path(item['filename'])
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                # Write content to the file
                file_path.write_text(item['content'])
                console.print(f"  [green]âœ“ Created:[/green] {file_path}")
            console.print("\n[bold green]Scaffolding complete! âœ¨[/bold green]")
        except Exception as e:
            console.print(f"[bold red]An error occurred during file creation: {e}[/bold red]")

    except Exception as e:
        console.print(f"[bold red]An error occurred during generation: {e}[/bold red]")



@app.callback()
def callback():
    """
    DAIP-LIVE: Dynamic AI-driven Project-execution LIVE system
    """
    create_config_yaml_if_not_exists()
    # No longer need to explicitly load config here.

@app.command()
def run(
    goal: Annotated[str, typer.Argument(help="The goal for the agent to accomplish.")],
    role: Annotated[str, typer.Option(help="The role/persona for the agent.")] = "default",
):
    """
    Starts the interactive TUI session to accomplish a goal.
    """
    cfg = config_manager.get_config()
    db_manager = DatabaseManager(db_path=cfg.database.path)
    embed_provider_config = ProviderConfig(model=cfg.llm_provider.embedding_model)
    embed_provider = LiteLLMProvider(embed_provider_config)
    knowledge_config = {"knowledge_dir": cfg.knowledge_base.directory}
    knowledge_manager = KnowledgeManager(
        db_manager=db_manager,
        model_provider=embed_provider,
        config=knowledge_config
    )
    model_provider = LiteLLMProvider(config=cfg.llm_provider)
    tool_manager = ToolManager()
    session_manager = SessionManager() # No longer passing db_manager
    memory_service = MemoryService()

    agent_executor = AgentExecutor(
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=asyncio.Queue(),
    )

    # In run(), LiteLLMProvider is instantiated for the embedding model, but the main model provider is also needed.
    # We need to create a separate RoleManager for the TUI.
    role_manager = RoleManager()
    debate_manager = DebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        model_provider=model_provider
    )

    tui = DAIP_TUI(
        executor=agent_executor,
        goal=goal,
        session_manager=session_manager,
        role_manager=role_manager,
        knowledge_manager=knowledge_manager,
        debate_manager=debate_manager,
        model_provider=model_provider,
        db_manager=db_manager,
        config_manager=config_manager
    )
    tui.run()

@app.command(name="sync", help="Manually triggers the knowledge base sync process.")
def knowledge_sync():
    """
    Manually triggers the knowledge base sync process.
    """
    console.print("[green]Knowledge base sync started...[/green]")
    cfg = config_manager.get_config()
    db_manager = DatabaseManager(db_path=cfg.database.path)
    embed_provider_config = ProviderConfig(model=cfg.llm_provider.embedding_model)
    embed_provider = LiteLLMProvider(embed_provider_config)
    knowledge_config = {"knowledge_dir": cfg.knowledge_base.directory}
    knowledge_manager = KnowledgeManager(
        db_manager=db_manager,
        model_provider=embed_provider,
        config=knowledge_config
    )
    knowledge_manager.sync()
    console.print("[bold green]Knowledge base sync completed.[/bold green]")


# --- Session Commands ---

@session_app.command(name="list", help="Lists all recorded sessions.")
def session_list():
    # Create SessionManager instance (no longer needs db_manager)
    session_manager = SessionManager()

    sessions = session_manager.list_sessions()

    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    table = Table(title="Recorded Sessions")
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("Goal", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Start Time", style="blue")

    for s in sessions:
        table.add_row(s.session_id, s.goal, s.session_type, s.status.name, str(s.start_time))

    console.print(table)

@session_app.command(name="view", help="Displays the full dialogue for a specific session.")
def session_view(session_id: Annotated[str, typer.Argument(help="The ID of the session to view.")]):
    # Create SessionManager instance (no longer needs db_manager)
    session_manager = SessionManager()

    session = session_manager.get_session(session_id)

    if not session:
        console.print(f"[bold red]Session with ID '{session_id}' not found.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]Session ID:[/] {session.session_id}")
    console.print(f"[bold]Goal:[/] {session.goal}")
    console.print(f"[bold]Type:[/] {session.session_type}")
    console.print(f"[bold]Status:[/] {session.status.name}")
    console.print(f"[bold]Participants:[/] {', '.join(session.participant_ids)}")
    console.print("--- [bold]Dialogue History[/] ---")

    for turn in session.history:
        console.print(f"[cyan]{turn.participant_id}[/cyan] ([dim]{turn.timestamp}[/dim]):")
        console.print(f"> {turn.content}")

    if session.summary:
        console.print("--- [bold]Summary[/] ---")
        console.print(session.summary)


# --- Role Commands ---

@role_app.command(name="list", help="Lists all available roles.")
def role_list():
    """
    Lists all available roles.
    """
    role_manager = RoleManager()
    roles = role_manager._roles

    if not roles:
        console.print("[yellow]No roles found.[/yellow]")
        return

    table = Table(title="Available Roles")
    table.add_column("Role Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    for name, role in roles.items():
        table.add_row(name, role.persona[:50] + "..." if len(role.persona) > 50 else role.persona)

    console.print(table)

@role_app.command(name="view", help="Displays details of a specific role.")
def role_view(role_name: Annotated[str, typer.Argument(help="The name of the role to view.")]):
    """
    Displays details of a specific role.
    """
    role_manager = RoleManager()
    role = role_manager.get_role_by_name(role_name)

    if not role:
        console.print(f"[bold red]Role '{role_name}' not found.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]Role Name:[/] {role.name}")
    console.print(f"[bold]Persona:[/] {role.persona}")
    console.print(f"[bold]Tools:[/] {', '.join(role.tools) if role.tools else 'None'}")

# --- Debate Commands ---

@debate_app.command(name="start", help="Starts a new debate on a given topic.")
def debate_start(
    topic: Annotated[str, typer.Argument(help="The topic of the debate.")],
    roles: Annotated[str, typer.Option(help="Comma-separated list of role names for the debate.")] = "pro_arguer,con_arguer",
    rounds: Annotated[int, typer.Option(help="The number of rounds for the debate.")] = 2,
):
    cfg = config_manager.get_config()
    db_manager = DatabaseManager(db_path=cfg.database.path)
    session_manager = SessionManager() # No longer passing db_manager
    role_manager = RoleManager()
    model_provider = LiteLLMProvider(config=cfg.llm_provider)

    debate_manager = DebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        model_provider=model_provider
    )

    console.print(f"[bold green]Starting debate on topic:[/] {topic}")
    role_list = [r.strip() for r in roles.split(",")]
    final_session = asyncio.run(debate_manager.run_debate(topic, role_list, rounds))
    console.print(f"[bold green]Debate finished. Session ID:[/] {final_session.session_id}")
    console.print("--- [bold]Summary[/] ---")
    console.print(final_session.summary)


@app.command()
def pa(
    goal: Annotated[str, typer.Argument(help="The goal for the personal assistant to accomplish.")],
):
    """
    Personal assistant shortcut command to accomplish a goal.
    """
    run(goal=goal)


# --- Shortcut Commands ---

@app.command()
def _0(
    query: Annotated[str, typer.Argument(help="The query to search in the knowledge base.")] = "",
):
    """
    Knowledge base shortcut command.
    If no query is provided, syncs the knowledge base.
    If a query is provided, searches the knowledge base.
    """
    if query:
        console.print(f"[bold yellow]Searching knowledge base for:[/] {query}")
        # TODO: Implement knowledge base search functionality
    else:
        knowledge_sync()


@app.command()
def debate(
    topic: Annotated[str, typer.Argument(help="The topic of the debate.")],
    roles: Annotated[str, typer.Option(help="Comma-separated list of role names for the debate.")] = "pro_arguer,con_arguer",
    rounds: Annotated[int, typer.Option(help="The number of rounds for the debate.")] = 2,
):
    """
    Debate shortcut command.
    """
    debate_start(topic=topic, roles=roles, rounds=rounds)


@app.command()
def v(
    query: Annotated[str, typer.Argument(help="The query to search in session history.")] = "",
):
    """
    Session history shortcut command.
    If no query is provided, lists all sessions.
    If a query is provided, searches session history.
    """
    if query:
        console.print(f"[bold cyan]Searching sessions for:[/] {query}")
        # TODO: Implement session history search functionality
    else:
        session_list()


if __name__ == "__main__":
    app()
