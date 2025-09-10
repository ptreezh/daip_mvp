"""Enhanced TUI with command auto-completion and new features."""

import asyncio
import os
from enum import Enum
from typing import Any, List, Optional

import pyperclip
import yaml
from rich.syntax import Syntax
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.keys import Keys
from textual.message import Message
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    RichLog,
    Static,
)

from src.daip_live.agent_engine.executor import AgentExecutor
from src.daip_live.core.models import (
    AgentEvent,
    FinalResponseEvent,
    PermissionRequestEvent,
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
)
from src.daip_live.knowledge.manager import KnowledgeManager
from src.daip_live.memory.service import MemoryService
from src.daip_live.memory.session_manager import SessionManager
from src.daip_live.model_provider.provider import LiteLLMProvider
from src.daip_live.p4_role_manager_tools.role_manager import RoleManager
from src.daip_live.p4_role_manager_tools.tool_manager import ToolManager
from src.daip_live.p8_debate_system.manager import DebateManager
from src.daip_live.persistence.database import DatabaseManager


class CommandSelected(Message):
    """Posted when a command is selected from the autocomplete popup."""
    def __init__(self, command: str) -> None:
        super().__init__()
        self.command = command


async def run_agent_and_feed_tui(agent: AgentExecutor, tui: "DAIP_TUI", goal: str):
    """Runs the agent and posts its events to the TUI."""
    try:
        async for event in agent.run(goal=goal):
            tui.post_event(event)
        tui.post_event(FinalResponseEvent(content="Agent run finished."))
    except Exception as e:
        tui.post_event(ThoughtEvent(content=f"An error occurred: {e}"))


class PermissionDialog(Screen):
    """A dialog for permission requests."""

    def __init__(self, tool_name: str, args: dict, callback) -> None:
        super().__init__()
        self.tool_name = tool_name
        self.args = args
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label(f"Tool '{self.tool_name}' requests permission to execute with args: {self.args}", id="permission-label")
            with Horizontal():
                yield Button("Allow", id="allow", variant="success")
                yield Button("Deny", id="deny", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "allow":
            self.callback(True)
        else:
            self.callback(False)
        self.app.pop_screen()


class CommandHelpDialog(Screen):
    """A dialog to show available commands."""

    def __init__(self, help_text: str) -> None:
        super().__init__()
        self.help_text = help_text

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("Available Commands:", id="help-label")
            yield RichLog(self.help_text, id="help-content")
            yield Button("Close", id="close", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()


class FocusMode(Enum):
    INPUT = "input"
    OUTPUT = "output"


class AutocompletePopup(Container):
    """A popup for command autocompletion."""

    def __init__(self, suggestions: List[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self.suggestions = suggestions

    def compose(self) -> ComposeResult:
        items = [ListItem(Label(s)) for s in self.suggestions]
        yield ListView(*items, id="autocomplete-list")

    def _accept_selection(self, list_item: ListItem) -> None:
        """Accepts the selected item and posts a message."""
        command = str(list_item.query_one(Label).renderable).split(" ", 1)[0]
        self.post_message(CommandSelected(command))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._accept_selection(event.item)

    def cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def accept_suggestion(self) -> None:
        list_view = self.query_one(ListView)
        if list_view.highlighted_child is not None:
            self._accept_selection(list_view.highlighted_child)

    def update_commands(self, new_suggestions: List[str]) -> None:
        list_view = self.query_one(ListView)
        list_view.clear()
        new_items = [ListItem(Label(s)) for s in new_suggestions]
        for item in new_items:
            list_view.append(item)


class DAIP_TUI(App):
    """A Textual app to interact with the DAIP Agent."""

    BINDINGS = [
        Binding("ctrl+tab", "toggle_focus", "切换焦点"),
        Binding("ctrl+a", "select_all", "全选", show=False),
        Binding("ctrl+c", "copy_text", "复制", show=False),
        Binding("escape", "exit_output_mode", "退出输出模式", show=False),
    ]

    def __init__(
        self,
        executor: AgentExecutor,
        goal: str,
        session_manager: SessionManager,
        role_manager: RoleManager,
        knowledge_manager: KnowledgeManager,
        debate_manager: DebateManager,
        model_provider: LiteLLMProvider,
        db_manager: DatabaseManager,
        config_manager: Any,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._executor = executor
        self._goal = goal
        self._session_manager = session_manager
        self._role_manager = role_manager
        self._knowledge_manager = knowledge_manager
        self._debate_manager = debate_manager
        self._model_provider = model_provider
        self._db_manager = db_manager
        self._config_manager = config_manager
        self._log_text_buffer: List[str] = []

        if self._executor is not None:
            self._executor.goal = goal
        self._current_session_id: Optional[str] = None
        self._session_stack: List[str] = []
        self._model_name = "llama3:8b"
        self._token_usage = (0, 8192)
        self.focus_mode = FocusMode.INPUT

        # Discover available commands
        self._available_commands = []
        for name in dir(self):
            if name.startswith("_handle_") and name.endswith("_command"):
                command_name = f"/{name.replace('_handle_', '').replace('_command', '')}"
                handler = getattr(self, name)
                help_text = (handler.__doc__ or "").strip().split('\n')[0]
                self._available_commands.append((command_name, help_text))

        try:
            help_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "tui_commands_help.md")
            with open(help_file_path, encoding="utf-8") as f:
                self._help_text = f.read()
        except FileNotFoundError:
            self._help_text = "Help document not found."

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="main_log", classes="output-mode", highlight=True, markup=True)
        yield Input(placeholder="Enter command or message...", id="user_input")
        yield Static("Model: llama3:8b | Tokens: 0/8192 (0%) | Status: Idle | Focus: Input", id="status_bar")
        yield Footer()

    def action_toggle_focus(self) -> None:
        if self.focus_mode == FocusMode.INPUT:
            self.focus_mode = FocusMode.OUTPUT
            self.query_one("#main_log").focus()
        else:
            self.focus_mode = FocusMode.INPUT
            self.query_one("#user_input").focus()
        self._update_status_bar("Idle")

    def action_exit_output_mode(self) -> None:
        if self.focus_mode == FocusMode.OUTPUT:
            self.focus_mode = FocusMode.INPUT
            self.query_one("#user_input").focus()
            self._update_status_bar("Idle")

    def action_select_all(self) -> None:
        """Select all text in the output log.
        Note: RichLog does not natively support select_all, so this
        is a no-op for now, but the binding is kept for user familiarity.
        The copy action will handle copying all text.
        """
        if self.focus_mode == FocusMode.OUTPUT:
            pass # RichLog does not support programmatic selection.

    def action_copy_text(self) -> None:
        """Copy all text from the output log to the clipboard."""
        if self.focus_mode == FocusMode.OUTPUT:
            all_text = "\n".join(self._log_text_buffer)
            pyperclip.copy(all_text)
            self._update_log_view("[bold green]> All log content copied to clipboard.[/bold green]")

    def on_click(self, event) -> None:
        main_log = self.query_one("#main_log")
        # Use region check for more robust click detection in tests
        if main_log.region.contains(event.screen_x, event.screen_y):
            if self.focus_mode == FocusMode.INPUT:
                self.action_toggle_focus()

    def on_mount(self) -> None:
        self.query_one("#user_input").focus()
        if self._goal is None:
            # This is a cold start, show welcome message
            self._update_log_view("[bold green]Welcome to DAIP-LIVE! Ready for your command.[/bold green]")
            self._update_status_bar("Ready")
        else:
            # A goal was provided, run the agent
            agent_coro = run_agent_and_feed_tui(self._executor, self, self._goal)
            self.run_worker(agent_coro)

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_input = message.value
        self.query_one("#user_input", Input).value = ""
        if user_input.startswith("/"):
            await self._handle_shortcut_command(user_input)
        else:
            if hasattr(self._executor, 'user_input_queue') and self._executor.user_input_queue is not None:
                self._executor.user_input_queue.put_nowait(user_input)
                self._update_log_view(f"[bold blue]> [/bold blue]User: {user_input}")
            else:
                self._update_log_view("[bold red]> [/bold red]Error: Agent not ready for input")

    def _get_autocomplete_suggestions(self, value: str) -> List[str]:
        """Gets autocomplete suggestions based on the input value."""
        parts = value.split(" ")

        # Case 1: Main command completion
        if len(parts) == 1 and value.startswith("/"):
            return [f"{cmd} - {help_text}" for cmd, help_text in self._available_commands if cmd.startswith(value)]

        # Case 2: Parameter completion for /role view
        if len(parts) == 3 and parts[0] == "/role" and parts[1] == "view" and parts[2] == "":
            roles = self._role_manager.list_roles()
            return [role.name for role in roles]

        # Case 3: Parameter completion for /session view
        if len(parts) == 3 and parts[0] == "/session" and parts[1] == "view" and parts[2] == "":
            sessions = self._session_manager.list_sessions()
            return [s.session_id for s in sessions]

        return []



    def on_input_changed(self, message: Input.Changed) -> None:
        value = message.value
        suggestions = self._get_autocomplete_suggestions(value)
        existing_popup_query = self.query("#autocomplete-popup")

        if suggestions:
            if existing_popup_query:
                existing_popup_query.first().update_commands(suggestions)
            else:
                popup = AutocompletePopup(suggestions=suggestions, id="autocomplete-popup")
                self.mount(popup)
                popup.styles.offset = (self.query_one("#user_input").region.x, -3)
        elif existing_popup_query:
            existing_popup_query.first().remove()

    def on_command_selected(self, message: CommandSelected) -> None:
        input_widget = self.query_one(Input)
        current_value = input_widget.value
        parts = current_value.strip().split(" ")

        # If we are completing a parameter, append the selection
        if len(parts) >= 2 and self._get_autocomplete_suggestions(current_value):
            new_value = " ".join(parts[:-1]) + " " + message.command
            input_widget.value = new_value
        else: # Otherwise, replace the whole command
            input_widget.value = message.command

        input_widget.focus()
        for popup in self.query("#autocomplete-popup"):
            popup.remove()

    def on_key(self, event: Keys) -> None:
        popup_query = self.query("#autocomplete-popup")

        if popup_query:
            popup = popup_query.first()
            if event.key == "up":
                event.prevent_default()
                popup.cursor_up()
                return
            if event.key == "down":
                event.prevent_default()
                popup.cursor_down()
                return
            if event.key in ("tab", "enter"):
                event.prevent_default()
                popup.accept_suggestion()
                return
            if event.key == "escape":
                popup.remove()
                event.prevent_default()
                return

        if event.key == "escape":
            self._handle_escape_key()

    def _handle_escape_key(self) -> None:
        if self.focus_mode == FocusMode.OUTPUT:
            self.action_exit_output_mode()

    async def _handle_shortcut_command(self, command: str) -> None:
        parts = command[1:].strip().split(" ", 1)
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        handler_name = f"_handle_{cmd}_command"
        handler = getattr(self, handler_name, lambda _: self._update_log_view(f"[bold red]> Unknown command: {cmd}"))

        if asyncio.iscoroutinefunction(handler):
            await handler(args)
        else:
            handler(args)

    def _handle_pa_command(self, args: str) -> None:
        if not args:
            self._update_log_view("[bold red]> Personal Assistant command requires a goal argument.")
            return
        self._session_stack.append(self._current_session_id) if self._current_session_id else None
        pa_session = self._session_manager.create_session(goal=args, session_type="chat", participant_ids=["user", "pa"])
        self._current_session_id = pa_session.session_id
        pa_executor = AgentExecutor(
            session_manager=self._session_manager,
            memory_service=MemoryService(),
            knowledge_manager=self._knowledge_manager,
            model_provider=self._model_provider,
            tool_manager=ToolManager(),
            user_input_queue=asyncio.Queue(),
        )
        agent_coro = run_agent_and_feed_tui(pa_executor, self, args)
        self.run_worker(agent_coro)
        self._update_log_view(f"[bold green]> Personal Assistant executing: {args}")

    def _handle_role_command(self, args: str) -> None:
        parts = args.strip().split(" ", 1)
        subcommand = parts[0].lower() if parts[0] else ""

        if subcommand == "list":
            roles = self._role_manager.list_roles()
            if not roles:
                self._update_log_view("[bold yellow]> No roles found.[/bold yellow]")
                return

            table_str = "Available Roles:\n"
            table_str += "- " + "\n- ".join([f"{role.name}: {role.persona}" for role in roles])
            self._update_log_view(f"[bold green]>{table_str}[/bold green]")
        elif subcommand == "view":
            if len(parts) < 2:
                self._update_log_view("[bold red]> Missing role name for /role view.[/bold red]")
                return
            role_name = parts[1]
            role = self._role_manager.get_role_by_name(role_name)
            if not role:
                self._update_log_view(f"[bold red]> Role '{role_name}' not found.[/bold red]")
                return

            details = (
                f"Role Details: {role.name}\n"
                f"  Persona: {role.persona}\n"
                f"  Tools: {', '.join(role.tools) if role.tools else 'None'}"
            )
            self._update_log_view(f"[bold green]>{details}[/bold green]")
        else:
            self._update_log_view(f"[bold red]> Unknown subcommand for /role: {subcommand}. Try /role list.[/bold red]")

    async def _handle_knowledge_command(self, args: str) -> None:
        parts = args.strip().split(" ", 1)
        subcommand = parts[0].lower() if parts and parts[0] else ""

        if subcommand == "sync":
            self._update_log_view("[bold yellow]> Starting knowledge base sync...[/bold yellow]")
            summary = await self._knowledge_manager.sync_knowledge_base()
            summary_str = ", ".join([f"{key.capitalize()}: {value}" for key, value in summary.items()])
            self._update_log_view(f"[bold green]> Knowledge base sync complete. {summary_str}[/bold green]")
        elif subcommand == "search":
            if len(parts) < 2:
                self._update_log_view("[bold red]> Missing query for /knowledge search.[/bold red]")
                return
            query = parts[1]
            self._update_log_view(f"[bold yellow]> Searching for: '{query}'...[/bold yellow]")
            results = await self._knowledge_manager.search(query)
            if not results:
                self._update_log_view("[bold yellow]> No results found.[/bold yellow]")
                return

            results_str = "Knowledge Search Results:\n"
            for res in results:
                results_str += f"- {res['file_path']} (Distance: {res['distance']:.4f})\n"
            self._update_log_view(f"[bold green]>{results_str}[/bold green]")
        else:
            self._update_log_view(f"[bold red]> Unknown subcommand for /knowledge: {subcommand}. Try /knowledge sync.[/bold red]")

    def _handle_debate_command(self, args: str) -> None:
        self._update_log_view("[bold yellow]> Debate commands not yet implemented.")

    def _handle_session_command(self, args: str) -> None:
        parts = args.strip().split(" ", 1)
        subcommand = parts[0].lower() if parts and parts[0] else "list" # Default to list

        if subcommand == "list":
            sessions = self._session_manager.list_sessions()
            if not sessions:
                self._update_log_view("[bold yellow]> No sessions found.[/bold yellow]")
                return

            table_str = "Available Sessions:\n"
            for s in sessions:
                table_str += f"- {s.session_id} | {s.status.name} | {s.goal}\n"
            self._update_log_view(f"[bold green]>{table_str}[/bold green]")
        elif subcommand == "view":
            if len(parts) < 2:
                self._update_log_view("[bold red]> Missing session ID for /session view.[/bold red]")
                return
            session_id = parts[1]
            session = self._session_manager.get_session(session_id)
            if not session:
                self._update_log_view(f"[bold red]> Session '{session_id}' not found.[/bold red]")
                return

            details = (
                f"Session Details: {session.session_id}\n"
                f"  Goal: {session.goal}\n"
                f"  Status: {session.status.name}\n"
                f"  Type: {session.session_type}\n"
                f"  Participants: {', '.join(session.participant_ids)}\n"
                f"  History: {len(session.history)} turns"
            )
            self._update_log_view(f"[bold green]>{details}[/bold green]")
        else:
            self._update_log_view(f"[bold red]> Unknown subcommand for /session: {subcommand}. Try /session list.[/bold red]")

    def _handle_model_command(self, args: str) -> None:
        self._update_log_view("[bold yellow]> Model commands not yet implemented.")

    def _handle_help_command(self, args: str) -> None:
        self.push_screen(CommandHelpDialog(self._help_text))

    def _handle_init_command(self, args: str) -> None:
        self._update_log_view("[bold yellow]> Init command not yet implemented.")

    def _handle_quit_command(self, args: str) -> None:
        """Exit the application."""
        self.exit()

    def post_event(self, event: AgentEvent) -> None:
        self.call_later(self._post_event, event)

    def _post_event(self, event: AgentEvent) -> None:
        if isinstance(event, ThoughtEvent):
            formatted_event = f"[italic grey]> {event.content}[/italic grey]"
            self._update_status_bar("Thinking...")
        elif isinstance(event, ToolCallEvent):
            formatted_event = f"[bold white]> [Tool Call] {event.tool_name}({event.args})[/bold white]"
            self._update_status_bar(f"Executing tool: {event.tool_name}")
        elif isinstance(event, ToolOutputEvent):
            status_color = "green" if event.status == "success" else "red"
            formatted_output = self._highlight_code_and_json(event.output)
            formatted_event = f"[bold {status_color}]> [Tool Output] {formatted_output}[/bold {status_color}]"
            self._update_status_bar("Idle")
        elif isinstance(event, FinalResponseEvent):
            formatted_event = f"[bold white]> {event.content}[/bold white]"
            self._update_status_bar("Idle")
        elif isinstance(event, PermissionRequestEvent):
            self.push_screen(PermissionDialog(event.tool_name, event.args, self._handle_permission_response))
            formatted_event = f"[bold yellow]> Permission requested for tool: {event.tool_name}[/bold yellow]"
        else:
            formatted_event = f"[grey]> {str(event)}[/grey]"
            self._update_status_bar("Idle")
        self._update_log_view(formatted_event)

    def _update_status_bar(self, status: str) -> None:
        status_bar = self.query_one("#status_bar", Static)
        used_tokens, total_tokens = self._token_usage
        percentage = int((used_tokens / total_tokens) * 100) if total_tokens > 0 else 0
        token_color = "green"
        if percentage > 80: token_color = "red"
        elif percentage > 60: token_color = "yellow"
        focus_mode_text = "Input" if self.focus_mode == FocusMode.INPUT else "Output"
        status_text = f"Model: {self._model_name} | Tokens: {used_tokens}/{total_tokens} ({percentage}%) | Status: {status} | Focus: {focus_mode_text}"
        status_bar.update(f"[{token_color}]{status_text}[/{token_color}]")

    def _handle_permission_response(self, allowed: bool) -> None:
        if hasattr(self._executor, 'permission_queue') and self._executor.permission_queue is not None:
            self._executor.permission_queue.put_nowait(allowed)
        self._update_log_view(f"[bold green]> Permission {'granted' if allowed else 'denied'}.[/bold green]")

    def clear_log(self) -> None:
        """Clears the log display and the internal text buffer."""
        self.query_one("#main_log", RichLog).clear()
        self._log_text_buffer.clear()

    def _update_log_view(self, text: str) -> None:
        self.query_one("#main_log", RichLog).write(text)
        self._log_text_buffer.append(Text.from_markup(text).plain)

    def _highlight_code_and_json(self, text: str) -> str:
        try:
            parsed = yaml.safe_load(text)
            return Syntax(yaml.dump(parsed, indent=2), "yaml", theme="monokai", line_numbers=True)
        except (yaml.YAMLError, TypeError):
            return str(text)
