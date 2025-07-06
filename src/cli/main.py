# -*- coding: utf-8 -*-
"""
@Time    : 2024-07-19 11:15:00
@Author  : DAIP-LIVE Team
@File    : main.py
@Description:
    The main entry point for the DAIP-LIVE Terminal User Interface (TUI).
    This module launches an interactive, full-screen application for debates.
"""
import asyncio
import logging
import pathlib
import datetime
import re
from typing import List, Optional, Dict, Any

import typer
from rich.console import Console

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.layout.containers import HSplit, Window, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.filters import has_focus, Condition
from prompt_toolkit.widgets import TextArea

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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = typer.Typer(name="daip", help="DAIP-LIVE: Dynamic AI Collaboration Platform")
console = Console()

# --- Communication Queues ---
to_protocol_queue: asyncio.Queue = asyncio.Queue()
from_protocol_queue: asyncio.Queue = asyncio.Queue()

async def ui_renderer(app_instance: Application, queue: asyncio.Queue):
    """Renders events from the debate engine to the TUI."""
    global show_verbose_logs
    while True:
        event: DebateEvent = await queue.get()

        if isinstance(event, ClearScreenEvent):
            output_area.text = "Screen cleared.\n"
        elif isinstance(event, DebateStartEvent):
            output_area.text += f"--- Debate Started ---\nTopic: {event.config.topic}\nRoles: {', '.join(event.config.roles)}\n\n"
        elif isinstance(event, NewTurnEvent):
            output_area.text += f"[{event.turn.role_id}]: {event.turn.opinion}\n\n"
        elif isinstance(event, TechLogEvent):
            if show_verbose_logs:
                source_details = event.source
                if event.module and event.function:
                    source_details = f"{event.source} ({event.module}.{event.function})"
                output_area.text += f"[VERBOSE] {source_details}: {event.message}\n"
        elif isinstance(event, DebateEndEvent):
            output_area.text += f"\n--- Debate Ended ---\n"
            output_area.text += f"Consensus: {event.result.consensus_outcome}\n"
            output_area.text += f"Synthesis: {event.result.synthesis}\n"
            app_instance.invalidate()  # Ensure final text is rendered
            break  # End the renderer
        elif isinstance(event, ErrorEvent):
            output_area.text += f"\n[ERROR] {event.error_message}\nDetails: {event.details}\n"
            app_instance.invalidate()  # Ensure final text is rendered
            break

        app_instance.invalidate()
        queue.task_done()

# --- TUI Application Components ---
# These are defined globally so they can be imported and used in tests.
show_verbose_logs: bool = False

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

# A mutable flag to control the visibility of the input container.
# Using a class or a list wrapper to ensure mutability across closures.
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


def create_key_bindings(
    output_area: TextArea,
    input_area: TextArea,
    input_container: ConditionalContainer,
    toolbar: Window,
) -> KeyBindingsBase:
    """Creates the key bindings for the TUI application."""
    kb = KeyBindings()

    @kb.add("c-c")
    @kb.add("q")
    def _quit(event):
        """Quit the application."""
        event.app.exit()

    @kb.add("v", filter=~has_focus(input_area))
    def _(event):
        """Toggle verbose technical logs."""
        global show_verbose_logs
        show_verbose_logs = not show_verbose_logs
        status = "enabled" if show_verbose_logs else "disabled"
        output_area.text += f"\n[System] Verbose logs {status}.\n"
        event.app.invalidate()

    @kb.add("c-l")
    async def _(event):
        """Clear the screen by sending a ClearScreenEvent."""
        # Use the from_protocol_queue as it's what the ui_renderer listens to.
        await from_protocol_queue.put(ClearScreenEvent())

    @kb.add("c-s")
    def _(event):
        """Save the current debate transcript to a file."""
        try:
            transcript_dir = pathlib.Path("transcripts")
            transcript_dir.mkdir(exist_ok=True)

            # Extract topic to use in the filename
            topic_match = re.search(r"Topic: (.*)\n", str(output_area.text))
            topic = topic_match.group(1) if topic_match else "untitled-debate"
            
            # Sanitize topic for filename
            safe_topic = re.sub(r'[\\/*?:"<>|]', "", topic).replace(" ", "_").lower()
            
            # Create a unique filename
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}_{safe_topic}.txt"
            filepath = transcript_dir / filename

            # Write content to file
            filepath.write_text(str(output_area.text), encoding="utf-8")

            # Notify user ONLY on success
            output_area.text += f"\n[System] Transcript saved to {filepath}\n"
            event.app.invalidate()
        except IOError as e:
            output_area.text += f"\n[System] Error saving transcript: {e}\n"
            event.app.invalidate()

    @kb.add("i")
    def _(event):
        """Handle user intervention by showing the input area."""
        # This handler modifies the shared TUI state to make the container visible
        _tui_state.input_visible = True
        toolbar.content = FormattedTextControl("Enter your intervention and press Enter to submit.")

        # Focus the input text area
        event.app.layout.focus(input_area)
        event.app.invalidate()

    @kb.add("enter", filter=has_focus(input_area))
    async def _(event):
        """Handle submission of the intervention text."""
        app = event.app
        buffer = event.app.current_buffer
        user_text = buffer.text
        
        if user_text:
            command = UserInterventionCommand(content=user_text)
            await to_protocol_queue.put(command)
            output_area.text += f"\n[You (Intervention)]: {user_text}\n"

        # Reset and hide the input area
        buffer.reset()
        _tui_state.input_visible = False
        toolbar.content = FormattedTextControl("[i] Intervene | [v] Toggle Verbose | [Ctrl+S] Save | [Ctrl+L] Clear | [q] / [Ctrl+C] Quit")

        # Return focus to the main output area
        app.layout.focus(output_area)
        app.invalidate()

    return kb

async def run_application(deps: Dict[str, Any], config: DebateConfig, output_queue: asyncio.Queue, input_queue: asyncio.Queue):
    """Gathers and runs all concurrent tasks."""
    # Pass components explicitly to make the function testable
    kb = create_key_bindings(output_area, input_area, input_container, toolbar)
    tui_app = Application(layout=layout, key_bindings=kb, full_screen=True, mouse_support=True)

    # --- Async Tasks ---
    protocol = deps["debate_protocol"]

    # Task to run the main debate protocol
    engine_task = asyncio.create_task(protocol.run(config))

    # Task to render UI events from the protocol
    renderer_task = asyncio.create_task(ui_renderer(tui_app, output_queue))

    # Task to handle user input commands and pass them to the protocol
    async def input_handler(input_q: asyncio.Queue, proto):
        while True:
            command = await input_q.get()
            if isinstance(command, UserInterventionCommand):
                await proto.handle_command(command)
            input_q.task_done()

    input_handler_task = asyncio.create_task(input_handler(input_queue, protocol))

    await tui_app.run_async()

    # Cleanup
    engine_task.cancel()
    renderer_task.cancel()
    input_handler_task.cancel() # Cancel the new input handler task
    try:
        await asyncio.gather(engine_task, renderer_task, input_handler_task) # Gather all tasks for cleanup
    except asyncio.CancelledError:
        pass # Expected on cleanup

@app.command("start")
def start_debate(
    topic: str = typer.Option(..., "--topic", "-t", help="The topic for the debate."),
    roles: Optional[List[str]] = typer.Option(None, "--roles", "-r", help="A list of role IDs to participate. Can be specified multiple times. If not provided, roles will be automatically recommended."),
    rounds: int = typer.Option(20, "--rounds", "-n", help="Number of full debate rounds."), # Increased rounds to 20
    consensus_strategy: str = typer.Option("simple_majority_vote", "--consensus", help="The consensus strategy tool to use."),
):
    """
    Starts a new interactive, multi-role debate in a full-screen TUI.
    """
    config = DebateConfig(
        topic=topic,
        roles=roles,
        rounds=rounds,
        consensus_strategy=consensus_strategy,
    )

    # Instantiate all services using the composition root
    # Note: We pass the output queue to the factory to inject it into the protocol
    deps = create_application_dependencies(output_queue=from_protocol_queue)
    asyncio.run(run_application(deps, config, from_protocol_queue, to_protocol_queue))


if __name__ == "__main__":
    app()
