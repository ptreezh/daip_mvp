"""Main entry point for running the DAIP-LIVE application.
This script ensures the correct Python path is set and launches the Typer CLI.
"""
import asyncio
import datetime
import logging
import os
import pathlib
import re
import sys
from typing import Any, Optional

# Add the project root to the Python path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from prompt_toolkit import Application
from prompt_toolkit.filters import Condition, has_focus
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from rich.console import Console

from src.composition import create_application_dependencies
from src.models import (
    ClearScreenEvent,
    DebateConfig,
    DebateEndEvent,
    DebateEvent,
    DebateStartEvent,
    ErrorEvent,
    NewTurnEvent,
    TechLogEvent,
    UserInterventionCommand,
)

# --- Global Configurations ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console = Console()

# --- Communication Queues ---
to_protocol_queue: asyncio.Queue = asyncio.Queue()
from_protocol_queue: asyncio.Queue = asyncio.Queue()

# --- Global State ---
deps: Optional[dict[str, Any]] = None
show_verbose_logs: bool = False

# --- TUI Application Components ---
output_area = TextArea(
    text="Welcome to DAIP-LIVE Interactive Debate!\n",
    read_only=True,
    scrollbar=True,
    wrap_lines=True,
)
input_area = TextArea(
    multiline=False,
    wrap_lines=False,
    prompt="Your input: ",
)
class _TUIState:
    input_visible = False
_tui_state = _TUIState()
input_container = ConditionalContainer(
    content=input_area,
    filter=Condition(lambda: _tui_state.input_visible)
)
toolbar = Window(
    height=1,
    content=FormattedTextControl("[i] Intervene | [v] Toggle Verbose | [Ctrl+S] Save | [Ctrl+L] Clear | [q] / [Ctrl+C] Quit"),
    style="class:toolbar",
)
root_container = HSplit([output_area, input_container, toolbar])
layout = Layout(root_container)

# --- Core Functions ---

async def ui_renderer(app_instance: Application, queue: asyncio.Queue):
    """Renders events from the debate engine to the TUI."""
    global show_verbose_logs, deps
    while True:
        event: DebateEvent = await queue.get()
        if isinstance(event, ClearScreenEvent):
            output_area.text = "Screen cleared.\n"
        elif isinstance(event, DebateStartEvent):
            output_area.text += f"--- Debate Started ---\nTopic: {event.config.topic}\nRoles: {', '.join(event.config.roles)}\n\n"
        elif isinstance(event, NewTurnEvent):
            role = deps["role_manager"].get_role_by_id(event.turn.role_id)
            role_name = role.name if role else event.turn.role_id
            output_area.text += f"[{role_name}]: {event.turn.opinion}\n\n"
        elif isinstance(event, TechLogEvent):
            if show_verbose_logs:
                source_details = event.source
                if event.module and event.function:
                    source_details = f"{event.source} ({event.module}.{event.function})"
                output_area.text += f"[VERBOSE] {source_details}: {event.message}\n"
        elif isinstance(event, DebateEndEvent):
            output_area.text += f"\n--- Debate Ended ---\nConsensus: {event.result.consensus_outcome}\nSynthesis: {event.result.synthesis}\n"
            app_instance.invalidate()
            break
        elif isinstance(event, ErrorEvent):
            output_area.text += f"\n[ERROR] {event.error_message}\nDetails: {event.details}\n"
            app_instance.invalidate()
            break
        app_instance.invalidate()
        queue.task_done()

def create_key_bindings() -> KeyBindingsBase:
    """Creates the key bindings for the TUI application."""
    kb = KeyBindings()
    @kb.add("c-c")
    @kb.add("q")
    def _quit(event): event.app.exit()
    @kb.add("v", filter=~has_focus(input_area))
    def _(event):
        global show_verbose_logs
        show_verbose_logs = not show_verbose_logs
        status = "enabled" if show_verbose_logs else "disabled"
        output_area.text += f"\n[System] Verbose logs {status}.\n"
        event.app.invalidate()
    @kb.add("c-l")
    async def _(event): await from_protocol_queue.put(ClearScreenEvent())
    @kb.add("c-s")
    def _(event):
        try:
            transcript_dir = pathlib.Path("transcripts")
            transcript_dir.mkdir(exist_ok=True)
            topic_match = re.search(r"Topic: (.*)\n", str(output_area.text))
            topic = topic_match.group(1) if topic_match else "untitled-debate"
            safe_topic = re.sub(r'[\\/*?:"<>|]', "", topic).replace(" ", "_").lower()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}_{safe_topic}.txt"
            filepath = transcript_dir / filename
            filepath.write_text(str(output_area.text), encoding="utf-8")
            output_area.text += f"\n[System] Transcript saved to {filepath}\n"
        except OSError as e:
            output_area.text += f"\n[System] Error saving transcript: {e}\n"
        event.app.invalidate()
    @kb.add("i")
    def _(event):
        _tui_state.input_visible = True
        toolbar.content = FormattedTextControl("Enter your intervention and press Enter to submit.")
        event.app.layout.focus(input_area)
        event.app.invalidate()
    @kb.add("enter", filter=has_focus(input_area))
    async def _(event):
        user_text = event.app.current_buffer.text
        if user_text:
            await to_protocol_queue.put(UserInterventionCommand(content=user_text))
            output_area.text += f"\n[You (Intervention)]: {user_text}\n"
        event.app.current_buffer.reset()
        _tui_state.input_visible = False
        toolbar.content = FormattedTextControl("[i] Intervene | [v] Toggle Verbose | [Ctrl+S] Save | [Ctrl+L] Clear | [q] / [Ctrl+C] Quit")
        event.app.layout.focus(output_area)
        event.app.invalidate()
    return kb

async def run_application_logic(config: DebateConfig):
    """Gathers and runs all concurrent tasks."""
    kb = create_key_bindings()
    tui_app = Application(layout=layout, key_bindings=kb, full_screen=True, mouse_support=True)
    protocol = deps["debate_protocol"]
    engine_task = asyncio.create_task(protocol.run(config))
    renderer_task = asyncio.create_task(ui_renderer(tui_app, from_protocol_queue))
    async def input_handler():
        while True:
            command = await to_protocol_queue.get()
            if isinstance(command, UserInterventionCommand):
                await protocol.handle_command(command)
            to_protocol_queue.task_done()
    input_handler_task = asyncio.create_task(input_handler())
    await tui_app.run_async()
    for task in [engine_task, renderer_task, input_handler_task]:
        task.cancel()
    try:
        await asyncio.gather(engine_task, renderer_task, input_handler_task)
    except asyncio.CancelledError:
        pass

def _get_topic_from_user(llm_interface) -> str:
    """Interactive prompt to get the debate topic."""
    console.print("\n[bold cyan]Step 1: Define the Debate Topic[/bold cyan]")
    choice = console.input("Do you want to (1) enter the topic directly, or (2) have the AI extract it from a prompt? [bold](1/2)[/bold]: ")
    while True:
        if choice == "1":
            return console.input("Please enter the debate topic: ")
        elif choice == "2":
            console.print("Please provide the text for the AI to extract a topic from. End with a blank line.")
            prompt_lines = [line for line in iter(console.input, "")]
            user_prompt = "\n".join(prompt_lines)
            if not user_prompt:
                console.print("[yellow]Prompt is empty. Please try again.[/yellow]")
                continue
            system_prompt = "You are an expert at summarizing and identifying the core debate topic from a given text. Extract a concise, clear, and neutral debate topic. Respond with only the topic itself."
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            with console.status("[bold green]AI is analyzing the text...[/bold green]"):
                extracted_topic = asyncio.run(llm_interface.generate(messages)).get("content", "").strip()
            console.print(f"Extracted Topic: [bold magenta]{extracted_topic}[/bold magenta]")
            if console.input("Is this topic satisfactory? (y/n): ").lower() == 'y':
                return extracted_topic
            else:
                console.print("Let's try again.")
                choice = console.input("Do you want to (1) enter the topic directly, or (2) provide a new prompt? [bold](1/2)[/bold]: ")
        else:
            choice = console.input("[red]Invalid choice.[/red] Please enter '1' or '2': ")

def _get_roles_from_user(topic: str, role_manager, role_recommender) -> list[str]:
    """Interactive prompt to select or create roles."""
    console.print("\n[bold cyan]Step 2: Select Roles[/bold cyan]")
    with console.status("[bold green]AI is recommending roles...[/bold green]"):
        asyncio.run(role_recommender.build_index())
        recommended_roles = asyncio.run(role_recommender.recommend_roles(topic, top_k=5))
    if recommended_roles:
        console.print("Recommended roles based on your topic:")
        for i, role in enumerate(recommended_roles):
            console.print(f"  [bold]{i+1}. {role.name} ({role.id})[/bold]: {role.description}")
    else:
        console.print("[yellow]No roles could be recommended. Please add them manually.[/yellow]")
    selected_roles = []
    while True:
        console.print("\nEnter role numbers (e.g., '1,3'), '[bold]new[/bold]', '[bold]list[/bold]', or '[bold]done[/bold]'.")
        user_input = console.input("> ").lower()
        if user_input == 'done':
            if not selected_roles:
                console.print("[red]You must select at least one role.[/red]")
                continue
            return selected_roles
        elif user_input == 'list':
            console.print("\n[bold]All Available Roles:[/bold]")
            for role in role_manager.list_roles():
                console.print(f"  - [bold]{role.name} ({role.id})[/bold]")
        elif user_input == 'new':
            console.print("\n[bold]--- Create a New Role ---[/bold]")
            new_id = console.input("ID: ")
            new_name = console.input("Name: ")
            new_desc = console.input("Description: ")
            new_sys_prompt = console.input("System Prompt: ")
            new_caps = [c.strip() for c in console.input("Capabilities (comma-separated): ").split(',')]
            from src.core_services.role_manager import Role
            new_role = Role(id=new_id, name=new_name, description=new_desc, system_prompt=new_sys_prompt, capabilities=new_caps, tools=[])
            role_manager.save_role(new_role)
            console.print(f"[green]Role '{new_name}' created and added.[/green]")
            selected_roles.append(new_id)
        else:
            try:
                for index in [int(i.strip()) for i in user_input.split(',')]:
                    if 1 <= index <= len(recommended_roles):
                        role_id = recommended_roles[index-1].id
                        if role_id not in selected_roles:
                            selected_roles.append(role_id)
                            console.print(f"[green]Added: {recommended_roles[index-1].name}[/green]")
                        else:
                            console.print(f"[yellow]Already selected: {recommended_roles[index-1].name}[/yellow]")
                    else:
                        console.print(f"[red]Invalid number: {index}.[/red]")
                console.print(f"Current roles: [bold]{', '.join(selected_roles)}[/bold]")
            except ValueError:
                console.print("[red]Invalid input.[/red]")

def start():
    """Starts a new interactive, multi-role debate in a full-screen TUI."""
    global deps
    deps = create_application_dependencies(output_queue=from_protocol_queue)
    console.print("[bold green]Welcome to the DAIP-LIVE Interactive Debate Setup![/bold green]")
    topic = _get_topic_from_user(deps["llm_interface"])
    roles = _get_roles_from_user(topic, deps["role_manager"], deps["role_recommender_service"])
    try:
        rounds = int(console.input("\n[bold cyan]Step 3: Set Number of Rounds[/bold cyan] (default: 20): ") or "20")
    except ValueError:
        rounds = 20
    console.print("Available strategies: simple_majority_vote, weighted_vote")
    strategy = console.input("[bold cyan]Step 4: Select Consensus Strategy[/bold cyan] (default: simple_majority_vote): ") or "simple_majority_vote"
    console.print("\n[bold underline magenta]--- Debate Configuration Summary ---[/bold underline magenta]")
    console.print(f"[bold]Topic:[/bold] {topic}\n[bold]Roles:[/bold] {', '.join(roles)}\n[bold]Rounds:[/bold] {rounds}\n[bold]Consensus Strategy:[/bold] {strategy}")
    if console.input("\nReady to start? (y/n): ").lower() == 'y':
        config = DebateConfig(topic=topic, roles=roles, rounds=rounds, consensus_strategy=strategy)
        asyncio.run(run_application_logic(config))
    else:
        console.print("[red]Debate setup cancelled.[/red]")

if __name__ == "__main__":
    # Bypassing Typer to directly call the start function
    start()
