"""Enhanced TUI with command auto-completion and new features."""

import asyncio
import os
import re
import webbrowser
import subprocess
from pathlib import Path
from datetime import datetime
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
    TextArea,
)
from textual.css.query import NoMatches


from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import (
    AgentEvent,
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
    DebateTurnStartEvent,
    ErrorEvent,
    FinalResponseEvent,
    ModelMetricsEvent,
    PermissionRequestEvent,
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
    TokenUsageEvent,
)
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.model_manager import ModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.scaffolding.manager import ScaffoldingManager
from daip_live.wiki.manager import WikiManager
from daip_live.tui_logo import PersonalAILogo
from daip_live.selection_dialog import (
    SessionSelectionDialog,
    RoleSelectionDialog,
    ModelSelectionDialog
)
from daip_live.permissions.manager import PermissionManager, PermissionLevel


class CommandSelected(Message):
    """Posted when a command is selected from the autocomplete popup."""
    def __init__(self, command: str) -> None:
        super().__init__()
        self.command = command


async def run_agent_and_feed_tui(agent: AgentExecutor, tui: "DAIP_TUI", goal: str):
    """Runs the agent in non-interactive mode and posts its events to the TUI."""
    try:
        async for event in agent.run(goal=goal):
            tui.post_event(event)
        tui.post_event(FinalResponseEvent(content="Agent run finished."))
    except Exception as e:
        tui.post_event(ThoughtEvent(content=f"An error occurred: {e}"))

async def run_chat_agent_and_feed_tui(agent: AgentExecutor, tui: "DAIP_TUI", initial_goal: str):
    """Runs the agent in chat mode and posts its events to the TUI."""
    try:
        async for event in agent.chat_run(initial_goal=initial_goal):
            tui.post_event(event)
    except Exception as e:
        tui.post_event(ThoughtEvent(content=f"An error occurred in the agent's chat loop: {e}"))


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
            rich_log = RichLog(id="help-content")
            rich_log.write(self.help_text)
            yield rich_log
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
        full_suggestion = str(list_item.query_one(Label).renderable)
        # Remove help text if present (e.g., "/role view - Role management")
        command = full_suggestion.split(" - ", 1)[0]
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
    """A Textual app to interact with the 人格AI Agent."""

    BINDINGS = [
        Binding("shift_tab", "toggle_focus", "切换焦点"),
        Binding("ctrl+a", "select_all", "全选", show=False),
        Binding("ctrl+c", "copy_text", "复制", show=False),
        Binding("ctrl+e", "_handle_ctrl_e_exit", "退出应用", show=False),
        Binding("escape", "_handle_escape_key", "退出输出模式", show=False),
    ]

    def __init__(
        self,
        executor: AgentExecutor = None,
        session_manager: SessionManager = None,
        role_manager: RoleManager = None,
        knowledge_manager: KnowledgeManager = None,
        debate_manager: DebateManager = None,
        model_provider: LiteLLMProvider = None,
        db_manager: DatabaseManager = None,
        config_manager: Any = None,
        role_model_manager: RoleModelManager = None,
        enhanced_debate_manager: EnhancedDebateManager = None,
        goal: Optional[str] = None,
    ):
        super().__init__()
        
        # Import and initialize container if dependencies are not provided
        import os
        if any(dep is None for dep in [session_manager, role_manager, knowledge_manager]):
            from daip_live.container import Container
            container = Container()
            
            # Load configuration from YAML if it exists
            config_file = "config.yaml"
            if os.path.exists(config_file):
                try:
                    container.config.from_yaml(config_file)
                except Exception as e:
                    print(f"Warning: Could not load config from {config_file}: {e}")
            
            # Set minimal config if not already set
            if hasattr(container.config, 'database') and hasattr(container.config.database, 'path'):
                if container.config.database.path() is None:
                    container.config.database.path.from_value(":memory:")
            
            # Set required config values with proper default model
            if hasattr(container.config, 'llm_provider'):
                if container.config.llm_provider.default_model() is None:
                    container.config.llm_provider.default_model.from_value("ollama/llama3")
                if container.config.llm_provider.embedding_model() is None:
                    container.config.llm_provider.embedding_model.from_value("mock-embedding")
            
            if hasattr(container.config, 'role_manager') and hasattr(container.config.role_manager, 'roles_dir'):
                if container.config.role_manager.roles_dir() is None:
                    container.config.role_manager.roles_dir.from_value("roles")
            
            if hasattr(container.config, 'knowledge_base') and hasattr(container.config.knowledge_base, 'directory'):
                if container.config.knowledge_base.directory() is None:
                    container.config.knowledge_base.directory.from_value("knowledge")
            
            # Create directories if they don't exist
            import os
            roles_dir = container.config.role_manager.roles_dir() if hasattr(container.config, 'role_manager') else "roles"
            knowledge_dir = container.config.knowledge_base.directory() if hasattr(container.config, 'knowledge_base') else "knowledge"
            os.makedirs(roles_dir, exist_ok=True)
            os.makedirs(knowledge_dir, exist_ok=True)
            
            # Resolve dependencies from container
            self._executor = executor or container.agent_executor()
            self._session_manager = session_manager or container.session_manager()
            self._role_manager = role_manager or container.role_manager()
            self._knowledge_manager = knowledge_manager or container.knowledge_manager()
            self._debate_manager = debate_manager or container.debate_manager()
            self._model_provider = model_provider or container.model_provider()
            self._role_model_manager = role_model_manager or RoleModelManager()
            self._enhanced_debate_manager = enhanced_debate_manager or EnhancedDebateManager(
                self._session_manager, self._role_manager, self._role_model_manager, self._model_provider
            )
            self._db_manager = db_manager or container.db_manager()
            self._config_manager = config_manager or getattr(container, 'config_manager', None)
            self._model_manager = ModelManager()
            self._memory_service = MemoryService(model_provider=self._model_provider)
            self._tool_manager = ToolManager()
            self._permission_manager = PermissionManager()
            self._wiki_manager = WikiManager(
                wiki_root=Path.cwd() / "wiki",
                role_model_manager=self._role_model_manager,
                model_provider=self._model_provider
            )
        else:
            # Use provided dependencies
            self._executor = executor
            self._session_manager = session_manager
            self._role_manager = role_manager
            self._knowledge_manager = knowledge_manager
            self._debate_manager = debate_manager
            self._model_provider = model_provider
            self._role_model_manager = role_model_manager or RoleModelManager()
            self._enhanced_debate_manager = enhanced_debate_manager or EnhancedDebateManager(
                self._session_manager, self._role_manager, self._role_model_manager, self._model_provider
            )
            self._db_manager = db_manager
            self._config_manager = config_manager
            self._model_manager = ModelManager()
            self._memory_service = MemoryService(model_provider=self._model_provider) if model_provider else None
            self._tool_manager = ToolManager() if model_provider else None
            self._permission_manager = PermissionManager()
            self._wiki_manager = WikiManager(
                wiki_root=Path.cwd() / "wiki",
                role_model_manager=self._role_model_manager,
                model_provider=self._model_provider
            )
        
        self._goal = goal
        self._log_text_buffer: List[str] = []

        if self._executor is not None:
            self._executor.goal = self._goal
        self._current_session_id: Optional[str] = None
        self._session_stack: List[str] = []
        self._model_name = "llama3:8b"
        self._token_usage = (0, 8192)
        
        # Real-time tracking variables
        self._real_token_usage = (0, 8192)  # (used, total)
        self._model_metrics = {
            'request_count': 0,
            'total_latency': 0.0,
            'last_request_time': None
        }
        
        # Debate tracking variables
        self._current_debate = {
            'session_id': None,
            'topic': None,
            'current_round': 0,
            'total_rounds': 0,
            'current_participant': None,
            'is_active': False,
            'role_models': {},  # Track model for each role
            'participant_colors': {}  # Track color assignments for participants
        }

        # Current model tracking
        self._current_model = "default"  # Track current active model
        self._debate_active_models = {}  # Track models for active debate participants

        # Debate lifecycle events for testing
        self._debate_started_event = asyncio.Event()
        self._debate_completed_event = asyncio.Event()
        self._participant_events = {}  # participant -> asyncio.Event
        
        # System activity monitoring
        self._system_activity = {
            'events_processed': 0,
            'tools_executed': 0,
            'errors_encountered': 0,
            'session_start_time': None,
            'last_activity_time': None
        }
        self.focus_mode = FocusMode.INPUT
        
        # Input history for command recall
        self._input_history: List[str] = []
        self._history_index: int = -1  # -1 means current input, not browsing history
        self._current_input_before_history: str = ""  # Store input when starting history navigation
        
        # Double CTRL+E exit detection
        self._last_ctrl_e_time: float = 0
        self._exit_hint_shown: bool = False

        # Discover available commands
        self._available_commands = []
        for name in dir(self):
            if name.startswith("_handle_") and name.endswith("_command"):
                command_name = f"/{name.replace('_handle_', '').replace('_command', '')}"
                handler = getattr(self, name)
                help_text = (handler.__doc__ or "").strip().split('\n')[0]
                self._available_commands.append((command_name, help_text))
        
        # Load input history from file
        self._load_input_history()

        try:
            help_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "tui_commands_help.md")
            with open(help_file_path, encoding="utf-8") as f:
                self._help_text = f.read()
        except FileNotFoundError:
            self._help_text = "Help document not found."

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="main_log", classes="output-mode", highlight=True, markup=True, wrap=True)
        yield Input(placeholder="Enter command or message...", id="user_input")
        yield Static("Model: llama3:8b | Tokens: 0/8192 (0%) | Status: Idle | Focus: Input", id="status_bar")
        yield Footer()

    def action_toggle_focus(self) -> None:
        if self.focus_mode == FocusMode.INPUT:
            self.focus_mode = FocusMode.OUTPUT
            self.query_one("#main_log").focus()
            # Add visual feedback for focus
            self.query_one("#main_log").styles.border = ("heavy", "blue")
            self.query_one("#user_input").styles.border = ("solid", "grey")
        else:
            self.focus_mode = FocusMode.INPUT
            self.query_one("#user_input").focus()
            # Add visual feedback for focus
            self.query_one("#main_log").styles.border = ("solid", "grey")
            self.query_one("#user_input").styles.border = ("heavy", "blue")
        self._update_status_bar("Idle")
        # Force a refresh of the screen to ensure the focus change is visible
        self.refresh()

    def action_exit_output_mode(self) -> None:
        # Always switch to input mode, regardless of current mode
        self.focus_mode = FocusMode.INPUT
        try:
            self.query_one("#user_input").focus()
            # Add visual feedback for focus
            self.query_one("#main_log").styles.border = ("solid", "grey")
            self.query_one("#user_input").styles.border = ("heavy", "blue")
            self._update_status_bar("Idle")
            # Force a refresh of the screen to ensure the focus change is visible
            self.refresh()
        except Exception as e:
            print(f"Error in action_exit_output_mode: {e}")  # Debug

    def action_select_all(self) -> None:
        """Select all text in the output log (copy all to clipboard)."""
        all_text = "\n".join(self._log_text_buffer)
        try:
            pyperclip.copy(all_text)
            self._update_log_view("[bold green]> All text copied to clipboard.[/bold green]")
            self._update_log_view(f"[dim]> Text length: {len(all_text)} characters[/dim]")
        except Exception as e:
            self._update_log_view(f"[bold red]> Failed to copy: {e}[/bold red]")
            # Fallback: show last few lines for manual copy
            lines = self._log_text_buffer[-10:]  # Show last 10 lines
            self._update_log_view("[yellow]> Recent content (for manual copy):[/yellow]")
            for line in lines[-5:]:  # Show last 5 lines
                if line.strip():
                    self._update_log_view(f"[dim]{line}[/dim]")

    def action_copy_text(self) -> None:
        """Copy all text from the output log to the clipboard."""
        all_text = "\n".join(self._log_text_buffer)
        try:
            pyperclip.copy(all_text)
            # Let's also show a visual indication that text was copied
            self._update_log_view("[bold green]> All log content copied to clipboard.[/bold green]")
            self._update_log_view(f"[dim]> Text length: {len(all_text)} characters[/dim]")
        except Exception as e:
            self._update_log_view(f"[bold red]> Failed to copy to clipboard: {e}[/bold red]")
            # Fallback: show text content for manual copy
            self._update_log_view("[yellow]> Content (copy manually):[/yellow]")
            # Show recent lines that fit in terminal
            recent_lines = self._log_text_buffer[-15:]  # Last 15 lines
            for i, line in enumerate(recent_lines):
                if line.strip():
                    self._update_log_view(f"[dim]{line}[/dim]")
                if i >= 10:  # Limit to 10 lines to avoid spam
                    break

    def action__handle_ctrl_e_exit(self) -> None:
        """Action method for CTRL+E exit binding."""
        self._handle_ctrl_e_exit()

    def on_click(self, event) -> None:
        main_log = self.query_one("#main_log")
        # Use region check for more robust click detection in tests
        if main_log.region.contains(event.screen_x, event.screen_y):
            # Try to detect and handle link clicks
            if self._handle_link_click(event):
                return
            if self.focus_mode == FocusMode.INPUT:
                self.action_toggle_focus()

    def _handle_link_click(self, event) -> bool:
        """Handle link clicks in the output log.
        
        Args:
            event: The click event
            
        Returns:
            True if a link was clicked and handled, False otherwise
        """
        try:
            # Get the RichLog widget
            main_log = self.query_one("#main_log", RichLog)
            
            # Convert screen coordinates to widget coordinates
            widget_x = event.screen_x - main_log.region.x
            widget_y = event.screen_y - main_log.region.y
            
            # Get the text at the click position
            # This is a simplified approach - in a real implementation,
            # you'd need to parse the RichLog content more carefully
            log_content = "\n".join(self._log_text_buffer)
            
            # Find URLs in the log content with their positions
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            
            # Find all URLs with their start and end positions
            urls_with_positions = []
            for match in re.finditer(url_pattern, log_content):
                urls_with_positions.append({
                    'url': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
            
            if not urls_with_positions:
                return False
            
            # Calculate approximate line and character position
            # This is a simplified calculation - in a real implementation,
            # you'd need to get the exact text at the click position
            lines = log_content.split('\n')
            char_position = 0
            clicked_line = -1
            
            for i, line in enumerate(lines):
                line_start = char_position
                line_end = char_position + len(line)
                
                # Approximate the character position based on widget coordinates
                # This is a rough estimate - for precise detection, you'd need
                # to query the actual text at the click position from RichLog
                estimated_char_pos = line_start + (widget_x * 2)  # Rough estimate
                
                if line_start <= estimated_char_pos <= line_end:
                    clicked_line = i
                    break
                    
                char_position = line_end + 1  # +1 for the newline
            
            if clicked_line == -1:
                return False
            
            # Check if click is near any URL in the clicked line
            line_start = sum(len(lines[j]) + 1 for j in range(clicked_line))
            line_text = lines[clicked_line]
            
            for url_info in urls_with_positions:
                url_start = url_info['start']
                url_end = url_info['end']
                
                # Check if URL is in the clicked line
                if line_start <= url_start <= line_start + len(line_text):
                    # Calculate relative position within the line
                    relative_start = url_start - line_start
                    relative_end = url_end - line_start
                    
                    # Check if click is within URL bounds (with some tolerance)
                    click_char_pos = widget_x * 2  # Rough estimate
                    
                    if relative_start - 5 <= click_char_pos <= relative_end + 5:
                        url = url_info['url']
                        
                        # Add www. prefix if missing for http/https URLs
                        if url.startswith('www.') and not url.startswith('http'):
                            url = 'https://' + url
                        
                        # Check if it's an email address
                        if '@' in url and not url.startswith('mailto:'):
                            url = 'mailto:' + url
                        
                        try:
                            self._update_log_view(f"[bold blue]> 🌐 正在打开链接: {url}[/bold blue]")
                            
                            # Use appropriate method to open the URL
                            if url.startswith('mailto:'):
                                # Open email client
                                subprocess.run(['start', 'mailto:' + url[7:]], shell=True)
                            else:
                                # Open web browser
                                webbrowser.open(url)
                            
                            return True
                        except Exception as e:
                            try:
                                self._update_log_view(f"[bold red]> ❌ 无法打开链接: {e}[/bold red]")
                            except:
                                print(f"Cannot open link: {e}")
                            return False
            
            return False
            
        except Exception as e:
            print(f"Error handling link click: {e}")
            return False

    async def on_mount(self) -> None:
        self.query_one("#user_input").focus()
        
        # Set initial visual styles for focus feedback
        self.query_one("#main_log").styles.border = ("solid", "grey")
        self.query_one("#user_input").styles.border = ("heavy", "blue")
        print("Initial focus styles applied: input=heavy blue, log=solid grey")  # Debug

        # Display 人格AI logo on startup with animation
        try:
            await self._display_startup_logo()
        except Exception as e:
            # If logo display fails, show simple welcome message
            self._update_log_view("[bold green]Welcome to 人格AI! Ready for your command.[/bold green]")

        if self._goal is None:
            # This is a cold start, show welcome message
            self._update_log_view("[bold green]Welcome to 人格AI! Ready for your command.[/bold green]")
            self._update_status_bar("Ready")
        else:
            # A goal was provided. Display it and wait for user to press Enter or edit.
            self.query_one("#user_input").value = f"/pa {self._goal}"
            self._update_log_view(f"[bold green]Goal loaded. Press Enter to start or edit the command.[/bold green]")
            self._update_status_bar("Ready")

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_input = message.value.strip()
        if not user_input:  # Skip empty inputs
            return
            
        self.query_one("#user_input", Input).value = ""
        
        # Add to input history (skip duplicates and empty inputs)
        if user_input and (not self._input_history or self._input_history[-1] != user_input):
            self._input_history.append(user_input)
            # Keep only last 10 entries
            if len(self._input_history) > 10:
                self._input_history.pop(0)
        
        # Reset history navigation
        self._history_index = -1
        self._current_input_before_history = ""
        
        if user_input.startswith("/"):
            await self._handle_shortcut_command(user_input)
        else:
            # Check if we have an active chat session
            if hasattr(self._executor, 'user_input_queue') and self._executor.user_input_queue is not None:
                try:
                    self._executor.user_input_queue.put_nowait(user_input)
                    self._update_log_view(f"[bold blue]> You:[/bold blue] {user_input}")
                except Exception as e:
                    # Queue might be full or session broken
                    self._update_log_view(f"[bold red]> Error: Could not send message to session ({str(e)})[/bold red]")
                    self._start_new_chat_session(user_input)
            else:
                # No active agent session, create one automatically
                self._start_new_chat_session(user_input)

    def _get_autocomplete_suggestions(self, value: str) -> List[str]:
        """Gets autocomplete suggestions based on the input value."""
        parts = value.split(" ")
        trimmed_value = value.rstrip()
        
        # Debug: remove this after testing
        # print(f"DEBUG: value='{value}', parts={parts}, len={len(parts)}")

        # Case 1: Main command completion (only if exactly 1 part and not a known multi-part command)
        if len(parts) == 1 and value.startswith("/"):
            cmd = value.strip()
            # Don't show main command completion for commands that have subcommands
            known_multi_commands = {"/role", "/session", "/knowledge", "/project", "/debate", "/model", "/compact", "/doc", "/wiki", "/permission"}
            if cmd not in known_multi_commands or len(cmd) < len("/role"):  # Allow partial matches
                return [f"{cmd} - {help_text}" for cmd, help_text in self._available_commands if cmd.startswith(value)]

        # Case 2: /role command completions
        if parts[0] == "/role":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["list", "view"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/role {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/role {cmd}" for cmd in subcommands]
            
            elif len(parts) >= 3 and parts[1] == "view":
                # Suggest role names for /role view
                if len(parts) == 3 or (len(parts) == 4 and parts[3] == ""):
                    prefix = parts[2] if len(parts) >= 3 and parts[2] else ""
                    try:
                        roles = self._role_manager.list_roles()
                        role_names = [role.name for role in roles if role.name.startswith(prefix)]
                        return [f"/role view {name}" for name in role_names]
                    except:
                        return []

        # Case 3: /session command completions
        if parts[0] == "/session":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["list", "view", "clear", "reset"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/session {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/session {cmd}" for cmd in subcommands]
            
            elif len(parts) >= 3 and parts[1] == "view":
                # Suggest session IDs for /session view
                if len(parts) == 3 or (len(parts) == 4 and parts[3] == ""):
                    prefix = parts[2] if len(parts) >= 3 else ""
                    try:
                        sessions = self._session_manager.list_sessions()
                        session_ids = [s.session_id for s in sessions if s.session_id.startswith(prefix)]
                        return [f"/session view {sid}" for sid in session_ids]
                    except:
                        return []

        # Case 4: /knowledge command completions
        if parts[0] == "/knowledge":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["sync", "search"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/knowledge {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/knowledge {cmd}" for cmd in subcommands]

        # Case 5: /project command completions
        if parts[0] == "/project":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["scaffold"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/project {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/project {cmd}" for cmd in subcommands]
            
            elif len(parts) >= 3 and parts[1] == "scaffold":
                # Suggest options for /project scaffold
                if len(parts) == 3 or (len(parts) == 4 and parts[3] == ""):
                    options = ["--description", "--from-file", "--yes"]
                    prefix = parts[2] if len(parts) >= 3 else ""
                    option_suggestions = [f"/project scaffold {opt}" for opt in options if opt.startswith(prefix)]
                    return option_suggestions

        # Case 6: /debate command completions
        if parts[0] == "/debate":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["start"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/debate {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/debate {cmd}" for cmd in subcommands]
            
            elif len(parts) >= 3 and parts[1] == "start":
                # For /debate start, suggest options after topic
                if len(parts) >= 4:
                    # Suggest options like --roles and --rounds
                    if len(parts) == 4 or (len(parts) == 5 and parts[4] == ""):
                        options = ["--roles", "--rounds"]
                        prefix = parts[3] if len(parts) >= 4 else ""
                        # Reconstruct the base command with topic
                        topic_parts = parts[2:3]  # Get topic part
                        base_cmd = "/debate start " + " ".join(topic_parts)
                        option_suggestions = [f"{base_cmd} {option}" for option in options if option.startswith(prefix)]
                        return option_suggestions

        # Case 7: /model command completions - disabled, /model defaults to list
        if parts[0] == "/model":
            # No auto-completion for /model command
            return []

        # Case 8: /compact command completions
        if parts[0] == "/compact":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["current", "full", "aggressive"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/compact {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/compact {cmd}" for cmd in subcommands]

        # Case 9: /doc command completions
        if parts[0] == "/doc":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["search", "download", "list", "batch", "status", "report"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/doc {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/doc {cmd}" for cmd in subcommands]

            elif len(parts) >= 2 and parts[1] == "download":
                # For /doc download, suggest format options
                if len(parts) >= 4 and parts[3] == "--format":
                    if len(parts) == 4 or (len(parts) == 5 and parts[4] == ""):
                        formats = ["pdf", "docx", "html", "txt"]
                        prefix = parts[4] if len(parts) >= 5 else ""
                        format_suggestions = [f"/doc download {parts[2]} --format {fmt}" for fmt in formats if fmt.startswith(prefix)]
                        return format_suggestions
                elif len(parts) == 3 or (len(parts) == 4 and parts[4] == "--format"):
                    # Suggest --format option after arxiv_id
                    return [f"/doc download {parts[2]} --format"]

        # Case 10: /wiki command completions
        if parts[0] == "/wiki":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["create", "list", "search", "export", "delete", "import", "stats"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/wiki {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/wiki {cmd}" for cmd in subcommands]

            elif len(parts) >= 2 and parts[1] == "export":
                # For /wiki export, suggest format options
                if len(parts) == 3 or (len(parts) == 4 and parts[3] == ""):
                    formats = ["markdown", "html", "obsidian", "json"]
                    prefix = parts[2] if len(parts) >= 3 else ""
                    format_suggestions = [f"/wiki export {fmt}" for fmt in formats if fmt.startswith(prefix)]
                    return format_suggestions

        # Case 11: /permission command completions
        if parts[0] == "/permission":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                # Suggest subcommands
                subcommands = ["list", "grant", "revoke", "check", "reset"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/permission {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/permission {cmd}" for cmd in subcommands]

            elif len(parts) >= 2 and parts[1] in ["grant", "revoke", "check", "reset"]:
                # For /permission subcommands
                if parts[1] in ["grant", "revoke"]:
                    if len(parts) == 3 or (len(parts) == 4 and parts[3] == ""):
                        tools = ["gemini-cli", "playwright", "exa-search", "context7", "deepwiki", "paper-downloader", "format-converter"]
                        prefix = parts[2] if len(parts) >= 3 else ""
                        tool_suggestions = [f"/permission {parts[1]} {tool}" for tool in tools if tool.startswith(prefix)]
                        return tool_suggestions
                    elif parts[1] == "grant" and len(parts) >= 4:
                        # Suggest permission levels for grant command
                        if len(parts) == 4 or (len(parts) == 5 and parts[4] == ""):
                            levels = ["denied", "read_only", "basic", "advanced", "admin"]
                            prefix = parts[3] if len(parts) >= 4 else ""
                            level_suggestions = [f"/permission grant {parts[2]} {level}" for level in levels if level.startswith(prefix)]
                            return level_suggestions
                elif parts[1] in ["check"]:
                    if len(parts) == 3 or (len(parts) == 4 and parts[3] == ""):
                        tools = ["gemini-cli", "playwright", "exa-search", "context7", "deepwiki", "paper-downloader", "format-converter"]
                        prefix = parts[2] if len(parts) >= 3 else ""
                        tool_suggestions = [f"/permission check {tool}" for tool in tools if tool.startswith(prefix)]
                        return tool_suggestions

        return []



    def on_input_changed(self, message: Input.Changed) -> None:
        value = message.value
        
        # Reset history navigation when user starts typing
        if self._history_index != -1:
            self._history_index = -1
            self._current_input_before_history = ""
        
        suggestions = self._get_autocomplete_suggestions(value)
        existing_popup_query = self.query("#autocomplete-popup")

        if suggestions:
            # Always show popup for parameter suggestions (never auto-select parameters)
            parts = value.strip().split(" ")
            is_parameter_suggestion = len(parts) >= 2
            
            # Only auto-select for single command suggestions (not parameters)
            # But only when user is adding characters, not deleting
            if len(suggestions) == 1 and not is_parameter_suggestion:
                # Clean the suggestion by removing help text if present
                clean_suggestion = suggestions[0].split(" - ")[0]
                input_widget = self.query_one(Input)
                
                # Only auto-complete if the suggestion is longer than current input
                # This allows users to delete content without it being auto-completed back
                if len(clean_suggestion) > len(value):
                    # Replace only the part that matches what user was typing
                    # This prevents duplication when user has already typed some letters
                    if clean_suggestion.startswith(value):
                        input_widget.value = clean_suggestion
                    else:
                        # Fallback to original behavior
                        input_widget.value = clean_suggestion
                    
                    # Move cursor to end of the completed command
                    input_widget.action_end()
                    
                    # Remove any existing popup
                    if existing_popup_query:
                        existing_popup_query.first().remove()
                    return
            
            # Show popup for multiple suggestions or parameter suggestions
            if existing_popup_query:
                existing_popup_query.first().update_commands(suggestions)
            else:
                popup = AutocompletePopup(suggestions=suggestions, id="autocomplete-popup")
                self.mount(popup)
                popup.styles.offset = (self.query_one("#user_input").region.x, -3)
        # Assign distinct colors to debate participants for visual identification
        participant_colors = {}
        colors = [
            "cyan",      # Light blue
            "magenta",   # Purple
            "yellow",    # Yellow
            "green",     # Green
            "blue",      # Blue
            "bright_magenta",  # Bright purple
            "bright_cyan",     # Bright cyan
            "bright_yellow",   # Bright yellow
        ]
        
        for i, name in enumerate(participant_names):
            color = colors[i % len(colors)]  # Cycle through colors if more participants than colors
            participant_colors[name] = color
        
        return participant_colors


    def on_input_changed(self, message: Input.Changed) -> None:
        value = message.value
        
        # Reset history navigation when user starts typing
        if self._history_index != -1:
            self._history_index = -1
            self._current_input_before_history = ""
        
        suggestions = self._get_autocomplete_suggestions(value)
        existing_popup_query = self.query("#autocomplete-popup")

        if suggestions:
            # Always show popup for parameter suggestions (never auto-select parameters)
            parts = value.strip().split(" ")
            is_parameter_suggestion = len(parts) >= 2
            
            # Only auto-select for single command suggestions (not parameters)
            # But only when user is adding characters, not deleting
            if len(suggestions) == 1 and not is_parameter_suggestion:
                # Clean the suggestion by removing help text if present
                clean_suggestion = suggestions[0].split(" - ")[0]
                input_widget = self.query_one(Input)
                
                # Only auto-complete if the suggestion is longer than current input
                # This allows users to delete content without it being auto-completed back
                if len(clean_suggestion) > len(value):
                    # Replace only the part that matches what user was typing
                    # This prevents duplication when user has already typed some letters
                    if clean_suggestion.startswith(value):
                        input_widget.value = clean_suggestion
                    else:
                        # Fallback to original behavior
                        input_widget.value = clean_suggestion
                    
                    # Move cursor to end of the completed command
                    input_widget.action_end()
                    
                    # Remove any existing popup
                    if existing_popup_query:
                        existing_popup_query.first().remove()
                    return
            
            # Show popup for multiple suggestions or parameter suggestions
            if existing_popup_query:
                existing_popup_query.first().update_commands(suggestions)
        elif existing_popup_query:
            existing_popup_query.first().remove()

    def on_command_selected(self, message: CommandSelected) -> None:
        input_widget = self.query_one(Input)
        current_value = input_widget.value.strip()
        parts = current_value.split(" ")

        # Determine if this is a parameter completion
        current_suggestions = self._get_autocomplete_suggestions(current_value)
        is_parameter_completion = len(parts) >= 2 and current_suggestions

        if is_parameter_completion:
            # Parameter completion: replace the last part with the selection
            # For example: "/role view " + "assistant" -> "/role view assistant"
            # But we need to handle cases where the suggestion already includes the command
            if message.command.startswith(parts[0]):
                # Suggestion already includes the full command (e.g., "/role view assistant")
                new_value = message.command
            else:
                # Suggestion is just the parameter (e.g., "assistant")
                base_parts = parts[:-1]  # Keep all parts except the last (empty or partial)
                new_value = " ".join(base_parts) + " " + message.command
            input_widget.value = new_value
            # Move cursor to end of the completed parameter for user convenience
            input_widget.action_end()
        else:
            # Command completion: replace the whole input
            input_widget.value = message.command
            # Move cursor to end for user to continue typing
            input_widget.action_end()

        input_widget.focus()
        for popup in self.query("#autocomplete-popup"):
            popup.remove()

    def on_key(self, event: Keys) -> None:
        # Handle Shift+Tab key specifically
        if event.key == "shift+tab":
            self.action_toggle_focus()
            event.prevent_default()
            return  # Prevent further processing
        
        # Handle system-level keys first (should work regardless of focus)
        if event == Keys.ControlE:
            self._handle_ctrl_e_exit()
            event.prevent_default()
            return  # Prevent further processing
            
        if event == Keys.Escape:
            self._handle_escape_key()
            event.prevent_default()
            return  # Prevent further processing
            
        # Handle focus-specific key behavior
        if self.focus_mode == FocusMode.OUTPUT:
            # In output mode, only handle copy key
            if event == Keys.ControlC:
                self.action_copy_text()
                event.prevent_default()
                return
            elif event == Keys.ControlA:
                # In output mode, Ctrl+A should copy all text
                if self.focus_mode == FocusMode.OUTPUT:
                    self.action_select_all()
                event.prevent_default()
                return
            elif event.key == "escape":
                # Handle escape key specifically in output mode
                print(f"Escape key detected in OUTPUT mode, focus mode: {self.focus_mode}")  # Debug
                self._handle_escape_key()
                event.prevent_default()
                return
            else:
                # Ignore all other keys in output mode
                event.prevent_default()
                return
        
        # Handle input mode keys (let them pass through to the input widget)
        # This ensures normal typing, backspace, delete, etc. work correctly
        try:
            input_widget = self.query_one(Input)
        except NoMatches:
            # If Input widget not found, ignore the key event
            return
        
        popup_query = self.query("#autocomplete-popup")

        # Handle autocomplete popup navigation
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
            # For all other keys when popup is shown, let the input widget handle them
            # This ensures normal typing, backspace, delete, etc. work correctly
            return

        # Handle input history navigation (only when no popup is shown)
        if not popup_query and self._input_history:
            if event.key == "up":
                event.prevent_default()
                self._navigate_history(-1)  # Go to older history
                return
            if event.key == "down":
                event.prevent_default()
                self._navigate_history(1)   # Go to newer history
                return
                
        # For all other keys in input mode, let the input widget handle them normally
        # This ensures normal typing, backspace, delete, enter, etc. work correctly
        # We don't need to explicitly handle them here

    def _handle_escape_key(self) -> None:
        # Always switch to input mode when escape is pressed
        self.action_exit_output_mode()

    def _navigate_history(self, direction: int) -> None:
        """Navigate through input history.
        
        Args:
            direction: -1 for up (older), 1 for down (newer)
        """
        input_widget = self.query_one(Input)
        
        # If we're just starting history navigation, save current input
        if self._history_index == -1:
            self._current_input_before_history = input_widget.value
        
        # Calculate new index
        if direction == -1:  # Up key - older history
            if self._history_index == -1:
                # First up press - go to most recent history
                if self._input_history:
                    self._history_index = len(self._input_history) - 1
            else:
                # Continue to older history
                if self._history_index > 0:
                    self._history_index -= 1
                    
        elif direction == 1:  # Down key - newer history
            if self._history_index != -1:
                if self._history_index < len(self._input_history) - 1:
                    self._history_index += 1
                else:
                    # Reached the end, restore original input
                    self._history_index = -1
        
        # Update input field with selected history item
        if self._history_index == -1:
            input_widget.value = self._current_input_before_history
        else:
            input_widget.value = self._input_history[self._history_index]
        
        # Move cursor to end of input
        input_widget.action_end()

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
        """Personal assistant shortcut for interactive chat sessions."""
        if not args:
            self._update_log_view("[bold yellow]> Please enter your task goal:[/bold yellow]")
            self._update_log_view("[bold dim]> (Type your goal and press Enter to start the Personal Assistant)[/bold dim]")
            # Set input focus and clear for user input
            input_widget = self.query_one(Input)
            input_widget.value = "/pa "
            input_widget.focus()
            input_widget.action_end()
            return

        # Create a new executor instance for the session
        pa_executor = AgentExecutor(
            session_manager=self._session_manager,
            memory_service=MemoryService(model_provider=self._model_provider),
            knowledge_manager=self._knowledge_manager,
            model_provider=self._model_provider,
            tool_manager=ToolManager(),
            user_input_queue=asyncio.Queue(),
        )

        # Update the TUI's reference to the currently active executor
        self._executor = pa_executor

        # Run the agent in interactive chat mode
        agent_coro = run_chat_agent_and_feed_tui(pa_executor, self, args)
        self.run_worker(agent_coro)
        self._update_log_view(f"[bold green]> Personal Assistant started. You can now chat.[/bold green]")

    def _handle_role_command(self, args: str) -> None:
        """Role management commands (list, view)."""
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
                # Show role selection dialog
                roles = self._role_manager.list_roles()
                if not roles:
                    self._update_log_view("[bold yellow]> No roles found.[/bold yellow]")
                    return
                
                def on_role_selected(role):
                    self._safe_log_callback(lambda: (
                        f"Role Details: {role.name}\n"
                        f"  Persona: {role.persona}\n"
                        f"  Tools: {', '.join(role.tools) if role.tools else 'None'}"
                    ), "role", f"{role.name} - {role.persona}")
                
                self.push_screen(RoleSelectionDialog(roles, on_role_selected))
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
        """Knowledge base operations (sync, search)."""
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
        """Debate system commands (start with topic and options)."""
        args_list = args.split()
        if not args_list:
            self._update_log_view("[bold red]> Usage: /debate start <topic> [--roles <roles>] [--rounds <rounds>][/bold red]")
            return
        
        subcommand = args_list[0]
        remaining_args = " ".join(args_list[1:])
        
        if subcommand == "start":
            if not remaining_args.strip():
                self._update_log_view("[bold red]> Usage: /debate start <topic> [--roles <roles>] [--rounds <rounds>][/bold red]")
                return
            
            # Parse arguments (simple parsing)
            topic_parts = []
            roles = "pro_arguer,con_arguer"
            rounds = 3
            
            # Simple argument parsing
            remaining_parts = remaining_args.split()
            i = 0
            while i < len(remaining_parts):
                if remaining_parts[i] == "--roles" and i + 1 < len(remaining_parts):
                    roles = remaining_parts[i + 1]
                    i += 2
                elif remaining_parts[i] == "--rounds" and i + 1 < len(remaining_parts):
                    try:
                        rounds = int(remaining_parts[i + 1])
                        i += 2
                    except ValueError:
                        self._update_log_view("[bold red]> Invalid rounds value, must be a number[/bold red]")
                        return
                else:
                    topic_parts.append(remaining_parts[i])
                    i += 1
            
            topic = " ".join(topic_parts)
            
            self._update_log_view(f"[bold blue]> Starting debate on topic: {topic}[/bold blue]")
            self._update_log_view(f"[dim]> Roles: {roles}, Rounds: {rounds}[/dim]")
            
            # Start debate in background
            asyncio.create_task(self._start_debate(topic, roles, rounds))
        elif subcommand == "history":
            remaining_history_args = " ".join(args_list[1:])
            self._handle_debate_history_command(remaining_history_args)
        else:
            self._update_log_view(f"[bold red]> Unknown debate subcommand: {subcommand}[/bold red]")
            self._update_log_view("[bold yellow]> Available: start, history[/bold yellow]")

    async def _start_debate(self, topic: str, roles: str, rounds: int) -> None:
        """Start a debate asynchronously with multi-model support."""
        try:
            role_list = [r.strip() for r in roles.split(",")]

            # Initialize debate tracking
            self._current_debate.update({
                'topic': topic,
                'total_rounds': rounds,
                'current_round': 0,
                'current_participant': None,
                'is_active': True,
                'role_models': {}
            })

            # Get model mappings for all roles
            try:
                role_mappings = self._role_model_manager.get_debate_model_mappings(role_list)

                # Store role-model mappings
                for mapping in role_mappings:
                    self._current_debate['role_models'][mapping.role_name] = mapping.model_config.model_name
                    self._debate_active_models[mapping.role_name] = mapping.model_config.model_name

                # Log model assignments
                model_assignments = [f"{role}→{model}" for role, model in self._current_debate['role_models'].items()]
                self._update_log_view(f"[bold blue]🎯 Model assignments: {', '.join(model_assignments)}[/bold blue]")

                # Use enhanced debate manager with multi-model support
                async for event in self._enhanced_debate_manager.run_debate(topic, role_list, rounds):
                    self.post_event(event)

            except Exception as model_error:
                # Fall back to standard debate manager if enhanced features fail
                self._update_log_view(f"[yellow]Multi-model debate failed, using standard mode: {model_error}[/yellow]")
                async for event in self._debate_manager.run_debate(topic, role_list, rounds):
                    self.post_event(event)

        except Exception as e:
            self._update_log_view(f"[bold red]Debate error: {e}[/bold red]")
            self._current_debate['is_active'] = False
            self._debate_active_models.clear()
            self._update_current_model("default")

    def _handle_session_command(self, args: str) -> None:
        """Session management commands (list, view, clear, reset)."""
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
                # Show session selection dialog
                sessions = self._session_manager.list_sessions()
                if not sessions:
                    self._update_log_view("[bold yellow]> No sessions found.[/bold yellow]")
                    return
                
                def on_session_selected(session):
                    self._safe_log_callback(lambda: (
                        f"Session Details: {session.session_id}\n"
                        f"  Goal: {session.goal}\n"
                        f"  Status: {session.status.name}\n"
                        f"  Type: {session.session_type}\n"
                        f"  Participants: {', '.join(session.participant_ids)}\n"
                        f"  History: {len(session.history)} turns"
                    ), "session", f"{session.session_id} - {session.goal}")
                
                self.push_screen(SessionSelectionDialog(sessions, on_session_selected))
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
        elif subcommand == "clear":
            # Clear current session context and reset tokens
            self._clear_current_session_context()
        elif subcommand == "reset":
            # Reset token usage to zero
            self._reset_token_usage()
        else:
            self._update_log_view(f"[bold red]> Unknown subcommand for /session: {subcommand}. Try /session list, clear, or reset.[/bold red]")

    def _handle_model_command(self, args: str) -> None:
        """Model management commands - always show model list with selection."""
        # Always show model list with selection dialog, regardless of arguments
        self._handle_model_list()
    
    def _handle_model_list(self) -> None:
        """List available local models with interactive selection - default behavior for /model command."""
        self._update_log_view("[bold blue]> Scanning for local models...[/bold blue]")
        
        try:
            models = self._model_manager.get_available_models()
            if not models:
                self._update_log_view("[bold yellow]> No local models found.[/bold yellow]")
                self._update_log_view("[bold dim]> Make sure Ollama is installed and running.[/bold dim]")
                self._update_log_view("[bold dim]> Install models with: ollama pull <model_name>[/bold dim]")
                return
            
            # Show selection dialog instead of plain list
            def on_model_selected(model):
                model_name = model['name']
                provider = model['provider']
                
                # Start model switching process
                self._safe_log_callback(lambda: f"[bold blue]> Switching to model: {model_name}...[/bold blue]", "model", model_name)
                
                try:
                    success = self._model_manager.switch_model(model_name, provider)
                    if success:
                        # Update the current model provider in TUI
                        from daip_live.core.models import ProviderConfig
                        new_config = ProviderConfig(
                            model=f"{provider}/{model_name}",
                            embedding_model="mock-embedding"
                        )
                        self._model_provider = LiteLLMProvider(new_config)
                        
                        # Show success message
                        self._safe_log_callback(lambda: f"[bold green]> ✓ Successfully switched to model: {model_name}[/bold green]", "model", model_name)
                        self._safe_log_callback(lambda: "[bold dim]> Configuration updated. New model will be used for future requests.[/bold dim]", "model", model_name)
                    else:
                        self._safe_log_callback(lambda: f"[bold red]> Failed to switch to model: {model_name}[/bold red]", "model", model_name)
                except Exception as e:
                    self._safe_log_callback(lambda: f"[bold red]> Error switching model: {e}[/bold red]", "model", model_name)
            
            self.push_screen(ModelSelectionDialog(models, on_model_selected))
                
        except Exception as e:
            self._update_log_view(f"[bold red]> Error listing models: {e}[/bold red]")
    
    def _handle_model_switch(self, model_name: str) -> None:
        """Switch to a different model."""
        self._update_log_view(f"[bold blue]> Switching to model: {model_name}...[/bold blue]")
        
        try:
            # First, refresh the model list
            available_models = self._model_manager.get_available_models(force_refresh=True)
            
            # Check if model exists (try with ollama provider first)
            model_found = False
            provider = "ollama"
            
            for model in available_models:
                if model["name"] == model_name:
                    model_found = True
                    provider = model["provider"]
                    break
            
            if not model_found:
                self._update_log_view(f"[bold red]> Model '{model_name}' not found in available models.[/bold red]")
                self._update_log_view("[bold yellow]> Use /model list to see available models.[/bold yellow]")
                return
            
            # Switch the model
            success = self._model_manager.switch_model(model_name, provider)
            if success:
                # Update the current model provider in TUI
                from daip_live.core.models import ProviderConfig
                new_config = ProviderConfig(
                    model=f"{provider}/{model_name}",
                    embedding_model="mock-embedding"
                )
                self._model_provider = LiteLLMProvider(new_config)
                
                self._update_log_view(f"[bold green]> ✓ Successfully switched to model: {model_name}[/bold green]")
                self._update_log_view(f"[bold dim]> Configuration updated. New model will be used for future requests.[/bold dim]")
            else:
                self._update_log_view(f"[bold red]> Failed to switch to model: {model_name}[/bold red]")
                
        except Exception as e:
            self._update_log_view(f"[bold red]> Error switching model: {e}[/bold red]")
    
    

    def _handle_project_command(self, args: str) -> None:
        """Project scaffolding and management commands."""
        args_list = args.split()
        if not args_list:
            self._update_log_view("[bold red]> Usage: /project scaffold --description <desc> or --from-file <file>[/bold red]")
            return

        subcommand = args_list[0]
        remaining_args = " ".join(args_list[1:])

        if subcommand == "scaffold":
            self._handle_scaffold_command(remaining_args)
        else:
            self._update_log_view(f"[bold red]> Unknown project subcommand: {subcommand}[/bold red]")

    def _handle_scaffold_command(self, args: str) -> None:
        """Handle project scaffolding command."""
        import argparse
        import shlex

        # Parse arguments
        parser = argparse.ArgumentParser(description='Project scaffolding')
        parser.add_argument('--description', type=str, help='Project description')
        parser.add_argument('--from-file', type=str, help='Read description from file')
        parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')

        try:
            # Use shlex to properly handle quoted arguments
            parsed_args = parser.parse_args(shlex.split(args))
        except SystemExit:
            self._update_log_view("[bold red]> Invalid arguments. Use --description <desc> or --from-file <file>[/bold red]")
            return

        # Get description
        description = ""
        if parsed_args.from_file:
            try:
                with open(parsed_args.from_file, 'r', encoding='utf-8') as f:
                    description = f.read()
            except FileNotFoundError:
                self._update_log_view(f"[bold red]> File not found: {parsed_args.from_file}[/bold red]")
                return
            except Exception as e:
                self._update_log_view(f"[bold red]> Error reading file: {e}[/bold red]")
                return
        elif parsed_args.description:
            description = parsed_args.description
        else:
            self._update_log_view("[bold red]> Please provide either --description or --from-file[/bold red]")
            return

        # Start scaffolding process
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._execute_scaffolding(description, parsed_args.yes))
        except RuntimeError:
            # No running event loop, create a new one
            asyncio.run(self._execute_scaffolding(description, parsed_args.yes))

    async def _execute_scaffolding(self, description: str, skip_confirmation: bool = False) -> None:
        """Execute scaffolding process."""
        try:
            self._update_log_view("[bold blue]> 🚀 Starting project scaffolding...[/bold blue]")

            # Create scaffolding manager
            cfg = config_manager.get_config()
            model_provider = LiteLLMProvider(config=cfg.llm_provider)
            scaffolder = ScaffoldingManager(model_provider)

            self._update_log_view("[bold blue]> 📝 Generating project structure...[/bold blue]")

            # Generate structure
            generated_structure = await scaffolder.generate_structure(description)

            if not generated_structure:
                self._update_log_view("[bold red]> No structure generated. Please check your description.[/bold red]")
                return

            # Show preview
            self._update_log_view("[bold green]> ✅ Project structure generated successfully![/bold green]")
            self._update_log_view("[bold yellow]> 📋 Generated files:[/bold yellow]")

            for item in generated_structure:
                filename = item.get('filename', 'Unknown')
                self._update_log_view(f"[cyan]  - {filename}[/cyan]")

            if not skip_confirmation:
                self._update_log_view("[bold yellow]> ⚠️  Do you want to create these files? (Use --yes to skip confirmation)[/bold yellow]")
                self._update_log_view("[bold red]> ❌ Confirmation not yet implemented in TUI. Please use CLI for file creation.[/bold red]")
                return

            # Create files (if confirmation is skipped)
            self._update_log_view("[bold blue]> 📁 Creating files...[/bold blue]")

            created_files = []
            for item in generated_structure:
                filename = item.get('filename', '')
                content = item.get('content', '')

                if filename:
                    try:
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(filename), exist_ok=True)

                        # Write file
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(content)

                        created_files.append(filename)
                        self._update_log_view(f"[green]  ✓ Created {filename}[/green]")
                    except Exception as e:
                        self._update_log_view(f"[bold red]  ✗ Failed to create {filename}: {e}[/bold red]")

            self._update_log_view(f"[bold green]> 🎉 Scaffolding completed! Created {len(created_files)} files.[/bold green]")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ Scaffolding failed: {e}[/bold red]")

    def _handle_help_command(self, args: str) -> None:
        """Display help information."""
        self.push_screen(CommandHelpDialog(self._help_text))

    def _handle_init_command(self, args: str) -> None:
        """Initialize configuration."""
        self._update_log_view("[bold yellow]> Init command not yet implemented.")

    def _handle_run_command(self, args: str) -> None:
        """Run a goal with the agent."""
        if args.strip():
            self._update_log_view(f"[bold blue]> Starting agent with goal: {args}[/bold blue]")
            # Create new agent executor for this run
            from daip_live.agent_engine.executor import AgentExecutor

            session_manager = self._session_manager
            agent = AgentExecutor(
                session_manager=session_manager,
                memory_service=self._memory_service,
                knowledge_manager=self._knowledge_manager,
                model_provider=self._model_provider,
                tool_manager=self._tool_manager,
                user_input_queue=asyncio.Queue()
            )
            agent.goal = args.strip()
            
            # Run agent in background
            asyncio.create_task(run_agent_and_feed_tui(agent, self, args.strip()))
        else:
            self._update_log_view("[bold yellow]> Please enter your task goal:[/bold yellow]")
            self._update_log_view("[bold dim]> (Type your goal and press Enter to run the agent)[/bold dim]")
            # Set input focus and clear for user input
            input_widget = self.query_one(Input)
            input_widget.value = "/run "
            input_widget.focus()
            input_widget.action_end()

    def _handle_compact_command(self, args: str) -> None:
        """Manually compress session context to reduce token usage."""
        try:
            self._update_log_view("[bold blue]> 🔄 开始手动压缩上下文...[/bold blue]")

            if not self._current_session_id:
                # Create a default session for compression
                self._update_log_view("[bold blue]> 🔄 创建默认会话进行压缩...[/bold blue]")
                session = self._session_manager.create_session(
                    goal="Context Compression Session",
                    session_type="compression",
                    participant_ids=["user", "assistant"]
                )
                self._current_session_id = session.session_id

            session = self._session_manager.get_session(self._current_session_id)
            if not session:
                self._update_log_view(f"[bold red]> 会话 '{self._current_session_id}' 不存在[/bold red]")
                return

            # Check if there's enough history to compress
            history_count = len(session.history)
            if history_count == 0:
                self._update_log_view("[bold yellow]> ⚠️ 会话历史为空，无需压缩[/bold yellow]")
                return
            elif history_count <= 3:
                self._update_log_view("[bold yellow]> ⚠️ 会话历史较短({history_count}条记录)，跳过压缩[/bold yellow]")
                return

            # Get current token usage before compression
            used_tokens, total_tokens = self._real_token_usage
            current_percentage = (used_tokens / total_tokens) * 100 if total_tokens > 0 else 0

            self._update_log_view(f"[dim]> 压始状态: {used_tokens}/{total_tokens} tokens ({current_percentage:.1f}%)[/dim]")
            self._update_log_view(f"[dim]> 历史记录数: {history_count}[/dim]")

            # Perform compression using memory service if available
            if hasattr(self, '_memory_service') and self._memory_service:
                self._update_log_view("[bold blue]> 🔄 正在智能压缩上下文...[/bold blue]")

                # Run compression asynchronously
                loop = asyncio.get_running_loop()
                loop.create_task(self._compress_session_context_async(session))
            else:
                # Fallback: manual compression - keep recent entries
                self._update_log_view("[bold yellow]> 🔄 使用手动压缩方法...[/bold yellow]")

                # Keep last 5 entries or 25% of history, whichever is smaller
                keep_count = min(5, max(2, history_count // 4))
                original_count = len(session.history)

                session.history = session.history[-keep_count:]
                session.compressed_history = None

                if session.summary:
                    # Update summary to reflect compression
                    session.summary = f"会话已手动压缩 - 保留最近{keep_count}条记录 (共{original_count}条)"

                self._update_log_view(f"[bold green]> ✅ 手动压缩完成: 保留{keep_count}/{original_count}条记录[/bold green]")

                # Update token usage display
                self._update_status_bar("手动压缩完成")

        except Exception as e:
            self._update_log_view(f"[bold red]> 压缩过程中出错: {e}[/bold red]")

    def _handle_doc_command(self, args: str) -> None:
        """Paper download and management commands."""
        args_list = args.split()
        if not args_list:
            self._update_log_view("[bold red]> Usage: /doc [download|list|search] [options][/bold red]")
            return

        subcommand = args_list[0].lower()
        remaining_args = " ".join(args_list[1:])

        if subcommand == "download":
            self._handle_doc_download(remaining_args)
        elif subcommand == "list":
            self._handle_doc_list()
        elif subcommand == "search":
            self._handle_doc_search(remaining_args)
        else:
            self._update_log_view(f"[bold red]> Unknown doc subcommand: {subcommand}[/bold red]")
            self._update_log_view("[bold yellow]> Available: download, list, search[/bold yellow]")

    def _handle_doc_download(self, args: str) -> None:
        """Handle paper download command."""
        args_list = args.split()
        if not args_list:
            self._update_log_view("[bold red]> Usage: /doc download <query> [--max <number>] [--arxiv][/bold red]")
            return

        query = " ".join([arg for arg in args_list if not arg.startswith("--")])
        max_results = 5
        use_arxiv = False

        # Parse options
        i = 0
        while i < len(args_list):
            if args_list[i] == "--max" and i + 1 < len(args_list):
                try:
                    max_results = int(args_list[i + 1])
                    i += 2
                except ValueError:
                    self._update_log_view("[bold red]> Invalid max results value[/bold red]")
                    return
            elif args_list[i] == "--arxiv":
                use_arxiv = True
                i += 1
            else:
                i += 1

        self._update_log_view(f"[bold blue]> 📥 开始下载论文: '{query}'[/bold blue]")
        self._update_log_view(f"[dim]> 最大数量: {max_results}, 使用arXiv: {use_arxiv}[/dim]")

        # Import and use paper downloader
        try:
            from daip_live.doc.paper_downloader import PaperDownloader

            # Create download directory
            from pathlib import Path
            download_dir = Path.cwd() / "docs" / "papers"

            downloader = PaperDownloader(download_dir=download_dir)

            # Start download process
            loop = asyncio.get_running_loop()
            loop.create_task(self._execute_paper_download(downloader, query, max_results, use_arxiv))

        except ImportError:
            self._update_log_view("[bold red]> ❌ 论文下载功能不可用，缺少相关模块[/bold red]")
        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 下载失败: {e}[/bold red]")

    def _handle_doc_list(self) -> None:
        """List downloaded papers."""
        try:
            from pathlib import Path
            papers_dir = Path.cwd() / "docs" / "papers"

            if not papers_dir.exists():
                self._update_log_view("[bold yellow]> 📂 论文目录不存在: {papers_dir}[/bold yellow]")
                self._update_log_view("[dim]> 请先使用 /doc download 下载论文[/dim]")
                return

            # Find PDF and metadata files
            pdf_files = list(papers_dir.glob("*.pdf"))
            metadata_files = list(papers_dir.glob("*.json"))

            if not pdf_files:
                self._update_log_view("[bold yellow]> 📄 未找到已下载的论文[/bold yellow]")
                return

            self._update_log_view("[bold green]> 📚 已下载的论文:[/bold green]")

            for pdf_file in sorted(pdf_files):
                # Check if corresponding metadata exists
                metadata_file = pdf_file.with_suffix('.json')
                if metadata_file.exists():
                    try:
                        import json
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)

                        title = metadata.get('title', pdf_file.stem)
                        authors = metadata.get('authors', [])
                        authors_str = ", ".join(authors[:3])  # Show first 3 authors
                        if len(authors) > 3:
                            authors_str += f" et al. ({len(authors)} authors)"

                        self._update_log_view(f"[cyan]  📄 {title}[/cyan]")
                        self._update_log_view(f"[dim]     👥 {authors_str}[/dim]")
                        self._update_log_view(f"[dim]     📅 {pdf_file.name}[/dim]")

                    except Exception:
                        self._update_log_view(f"[cyan]  📄 {pdf_file.stem}[/cyan]")
                else:
                    self._update_log_view(f"[cyan]  📄 {pdf_file.stem}[/cyan]")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 列出论文时出错: {e}[/bold red]")

    def _handle_doc_search(self, args: str) -> None:
        """Search downloaded papers."""
        if not args.strip():
            self._update_log_view("[bold red]> Usage: /doc search <query>[/bold red]")
            return

        query = args.strip()
        self._update_log_view(f"[bold blue]> 🔍 搜索论文: '{query}'[/bold blue]")

        try:
            from pathlib import Path
            papers_dir = Path.cwd() / "docs" / "papers"

            if not papers_dir.exists():
                self._update_log_view("[bold yellow]> 📂 论文目录不存在，请先下载论文[/bold yellow]")
                return

            # Search in metadata files
            metadata_files = list(papers_dir.glob("*.json"))
            results = []

            for metadata_file in metadata_files:
                try:
                    import json
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    # Simple text search in title, abstract, and authors
                    search_text = f"{metadata.get('title', '')} {metadata.get('abstract', '')} {' '.join(metadata.get('authors', []))}".lower()
                    if query.lower() in search_text:
                        results.append(metadata)

                except Exception:
                    continue

            if not results:
                self._update_log_view("[bold yellow]> 🔍 未找到匹配的论文[/bold yellow]")
                return

            self._update_log_view(f"[bold green]> 🔍 找到 {len(results)} 个匹配结果:[/bold green]")

            for i, result in enumerate(results[:10], 1):  # Show top 10 results
                title = result.get('title', 'Unknown Title')
                authors = result.get('authors', [])
                authors_str = ", ".join(authors[:2])
                if len(authors) > 2:
                    authors_str += f" et al."

                self._update_log_view(f"[cyan]  {i}. {title}[/cyan]")
                self._update_log_view(f"[dim]     👥 {authors_str}[/dim]")

                # Show abstract preview
                abstract = result.get('abstract', 'No abstract available')
                if abstract != 'No abstract available':
                    preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
                    self._update_log_view(f"[dim]     📝 {preview}[/dim]")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 搜索论文时出错: {e}[/bold red]")

    async def _execute_paper_download(self, downloader, query: str, max_results: int, use_arxiv: bool) -> None:
        """Execute paper download process."""
        try:
            if use_arxiv:
                # Use arXiv API
                papers = downloader.search_arxiv(query, max_results=max_results)

                if not papers:
                    self._update_log_view("[bold yellow]> 🔍 未找到匹配的arXiv论文[/bold yellow]")
                    return

                self._update_log_view(f"[bold green]> 🎯 找到 {len(papers)} 篇arXiv论文，开始下载...[/bold green]")

                # Download papers
                for paper in papers:
                    self._update_log_view(f"[blue] 📥 下载: {paper.title[:50]}...[/blue]")
                    result = downloader.download_arxiv_paper(paper.arxiv_id)

                    if result.success:
                        self._update_log_view(f"[green]   ✓ 下载成功: {result.output_file}[/green]")
                    else:
                        self._update_log_view(f"[red]   ✗ 下载失败: {result.error_message}[/red]")
            else:
                self._update_log_view("[bold yellow]> ⚠️ 目前只支持arXiv下载，请使用 --arxiv 参数[/bold yellow]")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 下载过程出错: {e}[/bold red]")

    def _handle_wiki_command(self, args: str) -> None:
        """Wiki management commands."""
        args_list = args.split()
        if not args_list:
            self._update_log_view("[bold red]> Usage: /wiki [create|list|export] [options][/bold red]")
            return

        subcommand = args_list[0].lower()
        remaining_args = " ".join(args_list[1:])

        if subcommand == "create":
            self._handle_wiki_create(remaining_args)
        elif subcommand == "list":
            self._handle_wiki_list()
        elif subcommand == "export":
            self._handle_wiki_export(remaining_args)
        else:
            self._update_log_view(f"[bold red]> Unknown wiki subcommand: {subcommand}[/bold red]")
            self._update_log_view("[bold yellow]> Available: create, list, export[/bold yellow]")

    def _handle_debate_history_command(self, args: str) -> None:
        """Debate history commands."""
        args_list = args.split()
        if not args_list:
            # Show debate history selection dialog
            self._show_debate_history_list()
            return

        subcommand = args_list[0].lower()
        remaining_args = " ".join(args_list[1:])

        if subcommand == "list":
            self._show_debate_history_list()
        elif subcommand == "view":
            if len(args_list) < 2:
                self._update_log_view("[bold red]> Usage: /debate history view <session_id>[/bold red]")
                return
            session_id = args_list[1]
            self._show_debate_history(session_id)
        else:
            self._update_log_view(f"[bold red]> Unknown debate history subcommand: {subcommand}[/bold red]")
            self._update_log_view("[bold yellow]> Available: list, view[/bold yellow]")

    def _show_debate_history_list(self) -> None:
        """Show list of all debate sessions."""
        try:
            # Get debate history tracker from container
            from daip_live.container import Container
            container = Container()
            container.config.from_yaml("config.yaml")
            debate_history_tracker = container.debate_history_tracker()
            
            # Get all debate histories
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            histories = loop.run_until_complete(debate_history_tracker.get_all_histories())
            loop.close()
            
            if not histories:
                self._update_log_view("[bold yellow]> No debate histories found.[/bold yellow]")
                return

            self._update_log_view(f"[bold green]> 📚 Debate History Sessions ({len(histories)} found):[/bold green]")

            for i, history in enumerate(histories, 1):
                participants_str = ", ".join([p.name for p in history.participants])
                self._update_log_view(f"[cyan]  {i}. {history.session_id}[/cyan]")
                self._update_log_view(f"     [dim]Topic:[/dim] {history.topic}")
                self._update_log_view(f"     [dim]Status:[/dim] {history.status} | [dim]Rounds:[/dim] {history.total_rounds}")
                self._update_log_view(f"     [dim]Participants:[/dim] {participants_str}")
                self._update_log_view("")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ Error retrieving debate history list: {e}[/bold red]")

    def _show_debate_history(self, session_id: str) -> None:
        """Show specific debate history."""
        try:
            # Get debate history tracker from container
            from daip_live.container import Container
            container = Container()
            container.config.from_yaml("config.yaml")
            debate_history_tracker = container.debate_history_tracker()
            
            # Get specific debate history
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            history = loop.run_until_complete(debate_history_tracker.get_history(session_id))
            loop.close()
            
            if not history:
                self._update_log_view(f"[bold red]> No debate history found for session ID '{session_id}'.[/bold red]")
                return

            self._update_log_view(f"[bold blue]> 📖 Debate Session:[/bold blue] {history.session_id}")
            self._update_log_view(f"[bold]Topic:[/bold] {history.topic}")
            self._update_log_view(f"[bold]Status:[/bold] {history.status}")
            self._update_log_view(f"[bold]Total Rounds:[/bold] {history.total_rounds}")
            self._update_log_view("[bold]Participants:[/bold]")
            
            for p in history.participants:
                self._update_log_view(f"  [cyan]• {p.name}[/cyan] (Order: {p.turn_order})")
            
            self._update_log_view("--- [bold]Debate Transcript[/] ---")
            
            current_round = 0
            for turn in history.turns:
                if turn.round_number != current_round:
                    current_round = turn.round_number
                    self._update_log_view(f"\n[bold blue]Round {current_round}:[/bold blue]")
                
                # Add visual indicator for the speaker with color
                participant = next((p for p in history.participants if p.name == turn.participant_name), None)
                color = participant.color if participant else "white"
                self._update_log_view(f"[{color}][bold]{turn.participant_name}:[/bold] {turn.content}[/{color}]")
            
            if history.end_time:
                self._update_log_view(f"\n[bold]End Time:[/] {history.end_time}")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ Error retrieving debate history: {e}[/bold red]")

    def _handle_wiki_create(self, args: str) -> None:
        """Create a new wiki page."""
        args_list = args.split()
        if len(args_list) < 1:
            self._update_log_view("[bold red]> Usage: /wiki create <title> [--tags <tag1,tag2>][/bold red]")
            return

        title = args_list[0]
        tags = []

        # Parse tags option
        if "--tags" in args_list:
            tags_index = args_list.index("--tags")
            if tags_index + 1 < len(args_list):
                tags = [tag.strip() for tag in args_list[tags_index + 1].split(",")]

        self._update_log_view(f"[bold blue]> 📝 创建Wiki页面: '{title}'[/bold blue]")
        if tags:
            self._update_log_view(f"[dim]> 标签: {', '.join(tags)}[/dim]")

        try:
            manager = self._wiki_manager

            page = manager.create_page(title, f"# {title}\n\n开始编辑您的内容...", tags)

            self._update_log_view(f"[bold green]> ✅ Wiki页面创建成功: {page.file_path}[/bold green]")
            self._update_log_view(f"[dim]> 文件位置: {page.file_path}[/dim]")

        except ImportError:
            self._update_log_view("[bold red]> ❌ Wiki功能不可用，缺少相关模块[/bold red]")
        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 创建Wiki页面失败: {e}[/bold red]")

    def _handle_wiki_list(self) -> None:
        """List wiki pages."""
        try:
            manager = self._wiki_manager
            pages = manager.list_all_pages()

            if not pages:
                self._update_log_view("[bold yellow]> 📄 未找到Wiki页面[/bold yellow]")
                return

            self._update_log_view(f"[bold green]> 📚 Wiki页面列表 ({len(pages)} 个页面):[/bold green]")

            for page in pages:
                tags_str = ", ".join(page.tags) if page.tags else "无标签"
                modified = page.modified_at.strftime("%Y-%m-%d %H:%M")
                word_count = page.get_word_count()
                reading_time = page.get_reading_time()

                self._update_log_view(f"[cyan]  📄 {page.title}[/cyan]")
                self._update_log_view(f"[dim]     🏷️  标签: {tags_str}[/dim]")
                self._update_log_view(f"[dim]     📝 字数: {word_count} | 阅读时间: {reading_time}分钟[/dim]")
                self._update_log_view(f"[dim]     📅 修改时间: {modified}[/dim]")

        except ImportError:
            self._update_log_view("[bold red]> ❌ Wiki功能不可用，缺少相关模块[/bold red]")
        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 列出Wiki页面失败: {e}[/bold red]")

    def _handle_wiki_export(self, args: str) -> None:
        """Export wiki to different formats."""
        args_list = args.split()
        if len(args_list) < 1:
            self._update_log_view("[bold red]> Usage: /wiki export <format> [output_dir] [/bold red]")
            self._update_log_view("[bold yellow]> 支持格式: markdown, html, obsidian[/bold yellow]")
            return

        format_type = args_list[0].lower()
        output_dir = args_list[1] if len(args_list) > 1 else None

        if format_type not in ["markdown", "html", "obsidian"]:
            self._update_log_view(f"[bold red]> 不支持的格式: {format_type}[/bold red]")
            self._update_log_view("[bold yellow]> 支持格式: markdown, html, obsidian[/bold yellow]")
            return

        try:
            if not self._wiki_manager:
                self._update_log_view("[bold red]> Wiki Manager not initialized.[/bold red]")
                return

            manager = self._wiki_manager
            
            if output_dir:
                export_path = Path(output_dir)
            else:
                export_path = Path.cwd() / "wiki_export" / format_type

            self._update_log_view(f"[bold blue]> 📤 导出Wiki为 {format_type} 格式...[/bold blue]")
            self._update_log_view(f"[dim]> 导出目录: {export_path}[/dim]")

            from daip_live.wiki.knowledge_integration import WikiKnowledgeExporter
            exporter = WikiKnowledgeExporter(manager)

            if format_type == "markdown":
                success = exporter.export_to_markdown(export_path)
            elif format_type == "html":
                success = exporter.export_to_html(export_path)
            elif format_type == "obsidian":
                success = exporter.export_to_obsidian(export_path)

            if success:
                self._update_log_view(f"[bold green]> ✅ Wiki导出成功: {export_path}[/bold green]")
            else:
                self._update_log_view(f"[bold red]> ❌ Wiki导出失败[/bold red]")

        except ImportError:
            self._update_log_view("[bold red]> ❌ Wiki导出功能不可用，缺少相关模块[/bold red]")
        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ Wiki导出失败: {e}[/bold red]")

    def _handle_permission_command(self, args: str) -> None:
        """Permission management commands."""
        args_list = args.split()
        if not args_list:
            self._update_log_view("[bold red]> 用法: /permission [list|grant|revoke|check|reset] [参数][/bold red]")
            return

        subcommand = args_list[0].lower()
        remaining_args = " ".join(args_list[1:])

        if subcommand == "list":
            self._handle_permission_list()
        elif subcommand == "grant":
            self._handle_permission_grant(remaining_args)
        elif subcommand == "revoke":
            self._handle_permission_revoke(remaining_args)
        elif subcommand == "check":
            self._handle_permission_check(remaining_args)
        elif subcommand == "reset":
            self._handle_permission_reset(remaining_args)
        else:
            self._update_log_view(f"[bold red]> 未知的权限子命令: {subcommand}[/bold red]")
            self._update_log_view("[bold yellow]> 可用命令: list, grant, revoke, check, reset[/bold yellow]")

    def _handle_permission_list(self) -> None:
        """List current permission settings."""
        try:
            self._update_log_view("[bold green]> 🔐 权限管理系统状态:[/bold green]")

            # Get current user (simplified - use "default" user for now)
            current_user = "default"
            user_permissions = self._permission_manager.list_user_permissions(current_user)

            if not user_permissions:
                self._update_log_view("[yellow]> 当前用户没有特殊权限设置，使用默认权限[/yellow]")
                self._update_log_view("[dim]> 可以使用 /permission grant <tool> <level> 授予权限[/dim]")
            else:
                self._update_log_view(f"[cyan]> 用户 '{current_user}' 的特殊权限:[/cyan]")
                for tool_name, permission in user_permissions.items():
                    level_emoji = {
                        PermissionLevel.DENIED: "🚫",
                        PermissionLevel.READ_ONLY: "👁️",
                        PermissionLevel.BASIC: "✅",
                        PermissionLevel.ADVANCED: "🔧",
                        PermissionLevel.ADMIN: "👑"
                    }.get(permission.level, "❓")

                    usage_info = f" (使用 {permission.usage_count} 次)" if permission.usage_count > 0 else ""
                    self._update_log_view(f"  {level_emoji} {tool_name}: {permission.level.value}{usage_info}")

            # Show default permissions for reference
            self._update_log_view("[dim]---[/dim]")
            self._update_log_view("[cyan]> 默认权限级别:[/cyan]")
            default_perms = self._permission_manager.default_permissions
            for tool_name, level in default_perms.items():
                level_emoji = {
                    PermissionLevel.DENIED: "🚫",
                    PermissionLevel.READ_ONLY: "👁️",
                    PermissionLevel.BASIC: "✅",
                    PermissionLevel.ADVANCED: "🔧",
                    PermissionLevel.ADMIN: "👑"
                }.get(level, "❓")
                self._update_log_view(f"  {level_emoji} {tool_name}: {level.value}")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 获取权限信息失败: {e}[/bold red]")

    def _handle_permission_grant(self, args: str) -> None:
        """Grant permission to a tool."""
        args_list = args.strip().split()
        if len(args_list) < 2:
            self._update_log_view("[bold red]> 用法: /permission grant <tool_name> <level>[/bold red]")
            self._update_log_view("[yellow]> 权限级别: denied, read_only, basic, advanced, admin[/yellow]")
            self._update_log_view("[dim]> 示例: /permission grant gemini-cli advanced[/dim]")
            return

        tool_name = args_list[0]
        level_str = args_list[1].lower()

        # Parse permission level
        level_map = {
            "denied": PermissionLevel.DENIED,
            "read_only": PermissionLevel.READ_ONLY,
            "readonly": PermissionLevel.READ_ONLY,
            "basic": PermissionLevel.BASIC,
            "advanced": PermissionLevel.ADVANCED,
            "admin": PermissionLevel.ADMIN
        }

        if level_str not in level_map:
            self._update_log_view(f"[bold red]> 无效的权限级别: {level_str}[/bold red]")
            self._update_log_view("[yellow]> 有效级别: denied, read_only, basic, advanced, admin[/yellow]")
            return

        level = level_map[level_str]
        current_user = "default"  # Simplified user identification

        try:
            success = self._permission_manager.grant_permission(current_user, tool_name, level, "tui_user")
            if success:
                level_emoji = {
                    PermissionLevel.DENIED: "🚫",
                    PermissionLevel.READ_ONLY: "👁️",
                    PermissionLevel.BASIC: "✅",
                    PermissionLevel.ADVANCED: "🔧",
                    PermissionLevel.ADMIN: "👑"
                }.get(level, "❓")

                self._update_log_view(f"[bold green]> ✅ 权限已授予: {level_emoji} {tool_name} -> {level.value}[/bold green]")
                self._update_log_view(f"[dim]> 用户: {current_user}, 授予者: tui_user[/dim]")
            else:
                self._update_log_view(f"[bold red]> ❌ 授予权限失败: {tool_name}[/bold red]")
        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 授予权限时出错: {e}[/bold red]")

    def _handle_permission_revoke(self, tool_name: str) -> None:
        """Revoke permission from a tool."""
        if not tool_name.strip():
            self._update_log_view("[bold red]> 请指定工具名称[/bold red]")
            self._update_log_view("[dim]> 用法: /permission revoke <tool_name>[/dim]")
            return

        current_user = "default"  # Simplified user identification

        try:
            success = self._permission_manager.revoke_permission(current_user, tool_name.strip())
            if success:
                self._update_log_view(f"[bold green]> ✅ 权限已撤销: {tool_name.strip()}[/bold green]")
                self._update_log_view(f"[dim]> 用户: {current_user}[/dim]")
                self._update_log_view("[dim]> 现在将使用默认权限级别[/dim]")
            else:
                self._update_log_view(f"[bold yellow]> ⚠️ 用户没有 '{tool_name.strip()}' 的特殊权限[/bold yellow]")
                self._update_log_view("[dim]> 该工具已使用默认权限级别[/dim]")
        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 撤销权限时出错: {e}[/bold red]")

    def _handle_permission_check(self, tool_name: str) -> None:
        """Check permission level for a specific tool."""
        if not tool_name.strip():
            self._update_log_view("[bold red]> 请指定工具名称[/bold red]")
            self._update_log_view("[dim]> 用法: /permission check <tool_name>[/dim]")
            return

        current_user = "default"  # Simplified user identification

        try:
            level = self._permission_manager.check_permission(current_user, tool_name.strip())

            level_emoji = {
                PermissionLevel.DENIED: "🚫",
                PermissionLevel.READ_ONLY: "👁️",
                PermissionLevel.BASIC: "✅",
                PermissionLevel.ADVANCED: "🔧",
                PermissionLevel.ADMIN: "👑"
            }.get(level, "❓")

            level_desc = {
                PermissionLevel.DENIED: "拒绝访问 - 无法使用此工具",
                PermissionLevel.READ_ONLY: "只读权限 - 可以查看但不能执行",
                PermissionLevel.BASIC: "基础权限 - 可以使用基本功能",
                PermissionLevel.ADVANCED: "高级权限 - 可以使用所有功能",
                PermissionLevel.ADMIN: "管理员权限 - 完全控制"
            }

            self._update_log_view(f"[bold cyan]> 🔍 权限检查: {level_emoji} {tool_name.strip()}[/bold cyan]")
            self._update_log_view(f"[dim]> 权限级别: {level.value}[/dim]")
            self._update_log_view(f"[dim]> 说明: {level_desc.get(level, '未知级别')}[/dim]")

            # Show if this is a user-specific permission or default
            user_permissions = self._permission_manager.list_user_permissions(current_user)
            if tool_name.strip() in user_permissions:
                permission = user_permissions[tool_name.strip()]
                self._update_log_view(f"[dim]> 类型: 用户特定权限[/dim]")
                if permission.granted_by:
                    self._update_log_view(f"[dim]> 授予者: {permission.granted_by}[/dim]")
                if permission.granted_at:
                    self._update_log_view(f"[dim]> 授予时间: {permission.granted_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
            else:
                self._update_log_view(f"[dim]> 类型: 默认权限[/dim]")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 检查权限时出错: {e}[/bold red]")

    def _handle_permission_reset(self, args: str) -> None:
        """Reset user permissions."""
        args_list = args.strip().split()

        if args_list and args_list[0].lower() == "--all":
            # Reset all users (admin operation)
            try:
                all_users = self._permission_manager.list_all_users()
                if not all_users:
                    self._update_log_view("[yellow]> 没有用户权限需要重置[/yellow]")
                    return

                self._update_log_view(f"[bold blue]> 🔄 重置所有用户权限 ({len(all_users)} 个用户)...[/bold blue]")

                reset_count = 0
                for user_id in all_users:
                    if self._permission_manager.reset_user_permissions(user_id):
                        reset_count += 1

                self._update_log_view(f"[bold green]> ✅ 已重置 {reset_count} 个用户的权限[/bold green]")
                self._update_log_view("[dim]> 所有用户现在将使用默认权限级别[/dim]")

            except Exception as e:
                self._update_log_view(f"[bold red]> ❌ 重置所有权限时出错: {e}[/bold red]")
        else:
            # Reset current user
            current_user = "default"  # Simplified user identification

            try:
                success = self._permission_manager.reset_user_permissions(current_user)
                if success:
                    self._update_log_view(f"[bold green]> ✅ 已重置用户 '{current_user}' 的所有权限[/bold green]")
                    self._update_log_view("[dim]> 现在将使用默认权限级别[/dim]")
                else:
                    self._update_log_view(f"[bold yellow]> ⚠️ 用户 '{current_user}' 没有特殊权限需要重置[/bold yellow]")
            except Exception as e:
                self._update_log_view(f"[bold red]> ❌ 重置权限时出错: {e}[/bold red]")

            self._update_log_view("[dim]> 提示: 使用 /permission reset --all 重置所有用户权限[/dim]")

    def _handle_quit_command(self, args: str) -> None:
        """Exit the application and close TUI."""
        self.exit()

    def _handle_clear_command(self, args: str) -> None:
        """Clear the output area."""
        # 获取主输出区域并清空内容
        try:
            log_view = self.query_one("#main_log", RichLog)
            # RichLog没有直接的清空方法，我们创建一个新的实例
            # 先获取父容器
            container = log_view.parent
            if container:
                # 移除旧的RichLog
                log_view.remove()
                # 创建新的RichLog
                new_log_view = RichLog(id="main_log", classes="output-mode", highlight=True, markup=True, wrap=True)
                container.mount(new_log_view, before=container.query_one(Input))
                self._update_log_view("[dim]Output area cleared.[/dim]")
        except Exception as e:
            self._update_log_view(f"[bold red]> Error clearing output: {e}[/bold red]")

    def _handle_ctrl_e_exit(self) -> None:
        """Handle double CTRL+E exit sequence."""
        import time
        
        current_time = time.time()
        
        if current_time - self._last_ctrl_e_time <= 2.0:  # 2秒窗口内
            # 第二次CTRL+E，执行退出
            self.exit()
        else:
            # 第一次CTRL+E，显示提示
            self._last_ctrl_e_time = current_time
            self._exit_hint_shown = True
            self._update_status_bar("再次按 CTRL+E 退出应用")
            
            # 2秒后清除提示
            def clear_hint():
                if time.time() - self._last_ctrl_e_time > 2.0:
                    self._update_status_bar("Ready")
                    self._exit_hint_shown = False
            
            self.set_timer(2.0, clear_hint)

    def _start_new_chat_session(self, initial_message: str) -> None:
        """Start a new chat session with the given initial message."""
        self._update_log_view("[bold yellow]> Starting new chat session...[/bold yellow]")
        
        # Create a new executor instance for the session
        pa_executor = AgentExecutor(
            session_manager=self._session_manager,
            memory_service=MemoryService(model_provider=self._model_provider),
            knowledge_manager=self._knowledge_manager,
            model_provider=self._model_provider,
            tool_manager=ToolManager(),
            user_input_queue=asyncio.Queue(),
        )
        
        # Set the user input as the initial goal
        pa_executor.goal = initial_message
        
        # Update the TUI's reference to the currently active executor
        self._executor = pa_executor
        
        # Run the agent in interactive chat mode
        agent_coro = run_chat_agent_and_feed_tui(pa_executor, self, initial_message)
        self.run_worker(agent_coro)
        
        self._update_log_view(f"[bold blue]> You:[/bold blue] {initial_message}")
        self._update_log_view(f"[bold green]> Chat session started. You can now continue the conversation.[/bold green]")

    def _load_input_history(self) -> None:
        """Load input history from file."""
        try:
            from pathlib import Path
            history_file = Path.home() / ".daip" / "input_history.txt"
            
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    # 只保留最近的10条记录
                    self._input_history = lines[-10:] if lines else []
        except Exception as e:
            # 如果加载失败，使用空历史记录
            self._input_history = []

    def _save_input_history(self) -> None:
        """Save input history to file."""
        try:
            from pathlib import Path
            history_file = Path.home() / ".daip"
            history_file.mkdir(exist_ok=True)
            history_file = history_file / "input_history.txt"
            
            # 只保存最近的10条记录
            history_to_save = self._input_history[-10:] if self._input_history else []
            
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(history_to_save))
        except Exception as e:
            # 静默处理保存失败
            pass

    def _add_to_input_history(self, input_text: str) -> None:
        """Add input to history and save to file."""
        if not input_text.strip():
            return
        
        # 避免重复添加相同的内容
        if input_text in self._input_history:
            self._input_history.remove(input_text)
        
        # 添加到历史记录开头
        self._input_history.insert(0, input_text)
        
        # 限制为最近10条
        if len(self._input_history) > 10:
            self._input_history = self._input_history[:10]
        
        # 保存到文件
        self._save_input_history()

    def post_event(self, event: AgentEvent) -> None:
        self.call_later(self._post_event, event)
    
    def _update_system_activity(self, event: AgentEvent) -> None:
        """Update system activity monitoring based on event type."""
        import time
        
        # Initialize session start time if not set
        if self._system_activity['session_start_time'] is None:
            self._system_activity['session_start_time'] = time.time()
        
        # Update last activity time
        self._system_activity['last_activity_time'] = time.time()
        
        # Increment events processed
        self._system_activity['events_processed'] += 1
        
        # Track specific activity types
        if isinstance(event, ToolCallEvent):
            self._system_activity['tools_executed'] += 1
        elif isinstance(event, ErrorEvent):
            self._system_activity['errors_encountered'] += 1

    def _post_event(self, event: AgentEvent) -> None:
        # Update system activity monitoring
        self._update_system_activity(event)
        
        if isinstance(event, ThoughtEvent):
            # Hide internal thinking process from user, only show status
            # Don't display thinking content to user
            thinking_content = event.content
            if len(thinking_content) > 50:
                thinking_content = thinking_content[:47] + "..."

            # Show minimal status without revealing internal process
            status = "Processing..."
            self._update_status_bar(status)
            # Don't log thinking events to user display
            return
        elif isinstance(event, ToolCallEvent):
            # Hide detailed tool call information from user
            # Don't show specific tool names and arguments
            import time
            self._current_tool_start = time.time()

            # Show minimal progress indicator
            status = "Working on your request..."
            self._update_status_bar(status)
            # Don't log tool call details to user display
            return
        elif isinstance(event, ToolOutputEvent):
            # Hide tool output details from user unless there's an error
            if event.status == "success":
                # Don't show successful tool outputs to user
                import time
                if hasattr(self, '_current_tool_start'):
                    execution_time = time.time() - self._current_tool_start
                    self._update_status_bar("Ready")
                return
            else:
                # Only show error outputs
                status_color = "red"
                formatted_event = f"[bold red]> Error: {event.output}[/bold red]"
                import time
                if hasattr(self, '_current_tool_start'):
                    execution_time = time.time() - self._current_tool_start
                    self._update_status_bar(f"Error occurred")
                else:
                    self._update_status_bar("Error")
        elif isinstance(event, FinalResponseEvent):
            formatted_event = f"[bold white]> {event.content}[/bold white]"
            self._update_status_bar("Idle")
        elif isinstance(event, PermissionRequestEvent):
            self.push_screen(PermissionDialog(event.tool_name, event.args, self._handle_permission_response))
            formatted_event = f"[bold yellow]> Permission requested for tool: {event.tool_name}[/bold yellow]"
        elif isinstance(event, TokenUsageEvent):
            self.update_token_usage(event.usage_info)
            formatted_event = f"[cyan]> Token usage: {event.usage_info.get('total_tokens', 0)} tokens[/cyan]"
        elif isinstance(event, ModelMetricsEvent):
            self.update_model_metrics(event.latency)
            formatted_event = f"[cyan]> Model metrics: {event.request_count} requests, {event.latency:.2f}s latency[/cyan]"
        elif isinstance(event, DebateStartEvent):
            self._current_debate.update({
                'session_id': event.session_id,
                'topic': event.topic,
                'current_round': 0,
                'total_rounds': event.rounds,
                'current_participant': None,
                'is_active': True,
                'participant_colors': self._get_participant_colors(event.roles)
            })
            # Set debate started event for testing
            self._debate_started_event.set()

            # Reset debate completed event and participant events
            self._debate_completed_event.clear()
            self._participant_events.clear()

            formatted_event = f"[bold green]> 🎬 Debate started: {event.topic}[/bold green]"
            formatted_event += f"\n[cyan]> Participants: {', '.join(event.roles)}[/cyan]"
            formatted_event += f"\n[cyan]> Rounds: {event.rounds}[/cyan]"
        elif isinstance(event, DebateRoundStartEvent):
            self._current_debate['current_round'] = event.round_number
            formatted_event = f"[bold blue]> 🔄 Round {event.round_number}/{event.total_rounds} starting...[/bold blue]"
        elif isinstance(event, DebateTurnStartEvent):
            self._current_debate['current_participant'] = event.participant

            # Update current model when participant changes
            if self._current_debate['role_models']:
                participant_model = self._current_debate['role_models'].get(event.participant, self._model_name)
                self._update_current_model(participant_model)

            # Set participant event for testing
            if event.participant not in self._participant_events:
                self._participant_events[event.participant] = asyncio.Event()
            self._participant_events[event.participant].set()

            # Get participant-specific color for better visual identification
            participant_color = self._current_debate['participant_colors'].get(event.participant, 'yellow')
            formatted_event = f"[bold {participant_color}]> 🗣️  {event.participant} speaking (Round {event.round_number})...[/bold {participant_color}]"
        elif isinstance(event, DebateTurnCompleteEvent):
            # Show complete response with participant-specific coloring for better visual separation
            participant_color = self._current_debate['participant_colors'].get(event.participant, 'white')
            header_color = self._current_debate['participant_colors'].get(event.participant, 'green')
            
            formatted_event = f"[bold {header_color}]> ✅ {event.participant} finished (Round {event.round_number})[/bold {header_color}]"
            formatted_event += f"\n[bold {participant_color}]Response:[/bold {participant_color}]"
            formatted_event += f"\n[{participant_color}]{event.content_preview}[/{participant_color}]"
        elif isinstance(event, DebateCompleteEvent):
            self._current_debate['is_active'] = False
            self._current_debate['current_participant'] = None

            # Reset model display to default when debate completes
            self._update_current_model("default")

            # Set debate completed event for testing
            self._debate_completed_event.set()

            formatted_event = f"[bold magenta]> 🏁 Debate completed![/bold magenta]"
            formatted_event += f"\n[cyan]> Summary: {event.summary}[/cyan]"

            # Auto-save debate results
            self._save_debate_results(event)
        else:
            formatted_event = f"[grey]> {str(event)}[/grey]"
            self._update_status_bar("Idle")
        self._update_log_view(formatted_event)
    
    def update_token_usage(self, usage_info: dict) -> None:
        """Update real token usage from model provider calls."""
        if usage_info:
            if isinstance(usage_info, dict):
                prompt_tokens = usage_info.get('prompt_tokens', 0)
                completion_tokens = usage_info.get('completion_tokens', 0)
                total_tokens = usage_info.get('total_tokens', prompt_tokens + completion_tokens)

                # Update real token usage
                current_used, current_total = self._real_token_usage
                new_used = current_used + total_tokens
                self._real_token_usage = (new_used, max(current_total, new_used))

                # Check if token usage exceeds 80% and trigger compression
                usage_percentage = (new_used / max(current_total, 1)) * 100
                if usage_percentage >= 80:
                    self._handle_token_limit_exceeded(usage_percentage)

                # Update model metrics
                self._model_metrics['request_count'] += 1
    
    def update_model_metrics(self, latency: float) -> None:
        """Update model performance metrics."""
        import time
        self._model_metrics['total_latency'] += latency
        self._model_metrics['last_request_time'] = time.time()
    
    def get_enhanced_status_text(self, base_status: str) -> str:
        """Generate enhanced status text with real-time metrics."""
        import time
        
        used_tokens, total_tokens = self._real_token_usage
        percentage = int((used_tokens / total_tokens) * 100) if total_tokens > 0 else 0
        token_color = "green"
        if percentage > 80: token_color = "red"
        elif percentage > 60: token_color = "yellow"
        
        # Calculate average latency
        avg_latency = 0
        if self._model_metrics['request_count'] > 0:
            avg_latency = self._model_metrics['total_latency'] / self._model_metrics['request_count']
        
        # Calculate session duration
        session_duration = 0
        if self._system_activity['session_start_time']:
            session_duration = time.time() - self._system_activity['session_start_time']
        
        # Calculate activity rate (events per minute)
        events_per_minute = 0
        if session_duration > 0:
            events_per_minute = (self._system_activity['events_processed'] / session_duration) * 60
        
        focus_mode_text = "Input" if self.focus_mode == FocusMode.INPUT else "Output"
        
        # Build status text
        # Use current model for display, with special formatting for debate mode
        if self._current_debate['is_active'] and self._current_debate['current_participant']:
            current_role = self._current_debate['current_participant']
            role_model = self._current_debate['role_models'].get(current_role, self._model_name)
            model_display = f"{role_model} ({current_role})"
        else:
            model_display = self._current_model if self._current_model != "default" else self._model_name

        status_parts = [
            f"Model: {model_display}",
            f"Tokens: {used_tokens}/{total_tokens} ({percentage}%)",
            f"Requests: {self._model_metrics['request_count']}",
            f"Avg Latency: {avg_latency:.2f}s"
        ]
        
        # Add system activity metrics
        if self._system_activity['events_processed'] > 0:
            activity_info = (
                f"Events: {self._system_activity['events_processed']} "
                f"({events_per_minute:.1f}/min) | "
                f"Tools: {self._system_activity['tools_executed']}"
            )
            if self._system_activity['errors_encountered'] > 0:
                activity_info += f" | Errors: {self._system_activity['errors_encountered']}"
            status_parts.append(activity_info)
        
        # Add debate status if active
        if self._current_debate['is_active']:
            debate_info = (
                f"Debate: R{self._current_debate['current_round']}/"
                f"{self._current_debate['total_rounds']} - "
                f"{self._current_debate['current_participant'] or 'Starting'}"
            )
            status_parts.append(debate_info)
        
        status_parts.extend([
            f"Status: {base_status}",
            f"Focus: {focus_mode_text}"
        ])
        
        status_text = " | ".join(status_parts)
        return f"[{token_color}]{status_text}[/{token_color}]"

    def _update_current_model(self, model_name: str) -> None:
        """Update the current model display and status bar."""
        self._current_model = model_name
        self._model_name = model_name  # Also update the model_name for status bar
        # Update status bar to reflect model change
        current_status = "Idle" if not self._current_debate['is_active'] else "Debating"
        
        # Log model change
        try:
            self._update_log_view(f"[bold blue]> 🔄 Model switched to {model_name}[/bold blue]")
        except:
            print(f"Model switched to {model_name}")
        
        # Log model change in debates
        if self._current_debate['is_active'] and self._current_debate['current_participant']:
            try:
                self._update_log_view(f"[dim]🔄 Model switched to {model_name} for {self._current_debate['current_participant']}[/dim]")
            except:
                print(f"Model switched to {model_name} for {self._current_debate['current_participant']}")
        
        # Try to update status bar with error handling
        try:
            self._update_status_bar(current_status)
        except:
            pass  # Status bar update failed, but that's not critical

    def _update_status_bar(self, status: str) -> None:
        try:
            status_bar = self.query_one("#status_bar", Static)
            # Use enhanced status text with real-time metrics
            enhanced_text = self.get_enhanced_status_text(status)
            status_bar.update(enhanced_text)
        except Exception as e:
            # Fallback if status bar is not available
            print(f"Error updating status bar: {e}")
            # Try to log the status instead
            try:
                self._update_log_view(f"[dim]Status: {status}[/dim]")
            except:
                pass  # If even logging fails, just ignore

    def _handle_permission_response(self, allowed: bool) -> None:
        if hasattr(self._executor, 'permission_queue') and self._executor.permission_queue is not None:
            self._executor.permission_queue.put_nowait(allowed)
        self._update_log_view(f"[bold green]> Permission {'granted' if allowed else 'denied'}.[/bold green]")

    def clear_log(self) -> None:
        """Clears the log display and the internal text buffer."""
        self.query_one("#main_log", RichLog).clear()
        self._log_text_buffer.clear()

    def _safe_log_callback(self, message_func, item_type: str, fallback_info: str) -> None:
        """Safely update log view with error handling for selection callbacks.
        
        Args:
            message_func: Function that returns the message to log
            item_type: Type of item being processed ('session', 'role', 'model')
            fallback_info: Fallback information to print to console if logging fails
        """
        try:
            message = message_func()
            self._update_log_view(message)
        except Exception as e:
            print(f"Error in {item_type} selection callback: {e}")
            print(f"{item_type.capitalize()} details: {fallback_info}")

    async def _display_startup_logo(self) -> None:
        """Display 人格AI logo on startup with animation."""
        try:
            # Wait a bit for UI to fully initialize
            await asyncio.sleep(0.5)

            # Debug: Check if RichLog is available
            try:
                self.query_one("#main_log", RichLog)
                self._update_log_view("[dim]🎨 Displaying 人格AI logo...[/dim]")
            except Exception as log_error:
                print(f"RichLog not available: {log_error}")
                return

            # Create logo instance (automatically selects random variant)
            logo = PersonalAILogo()

            # Randomly select animation style
            import random
            animation_styles = ["typewriter", "gradient", "cyberpunk"]
            selected_style = random.choice(animation_styles)

            # Display animated logo with random style
            await logo.display_animated_tui(self._update_log_view, selected_style)

            # Add startup message
            self._update_log_view("[dim]===============================================[/dim]")
            self._update_log_view("[dim]           人格AI Initialized!           [/dim]")
            self._update_log_view("[dim]===============================================[/dim]")
            self._update_log_view("[dim]                                              [/dim]")

        except Exception as e:
            # If logo display fails, continue with normal startup
            print(f"Logo display error: {e}")
            try:
                self._update_log_view("[yellow]Logo display failed, continuing startup...[/yellow]")
            except:
                print("Critical: Cannot update log view")
            import traceback
            traceback.print_exc()

    def _update_log_view(self, text: str) -> None:
        try:
            self.query_one("#main_log", RichLog).write(text)
            self._log_text_buffer.append(Text.from_markup(text).plain)
        except Exception:
            # 如果main_log还不存在，暂时忽略这个错误
            # 这通常发生在TUI初始化期间
            pass

    def _highlight_code_and_json(self, text: str) -> str:
        try:
            parsed = yaml.safe_load(text)
            return Syntax(yaml.dump(parsed, indent=2), "yaml", theme="monokai", line_numbers=True)
        except (yaml.YAMLError, TypeError):
            return str(text)

    def _save_debate_results(self, event: DebateCompleteEvent, output_dir: Optional[Path] = None) -> None:
        """Save debate results to a specified directory, with full transcript."""
        try:
            session = self._session_manager.get_session(event.session_id)
            if not session:
                self._update_log_view(f"[bold red]> 无法找到会话 {event.session_id} 来保存报告。[/bold red]")
                return

            # Use explicit output_dir if provided, otherwise default to ./workout
            if output_dir is None:
                output_dir = Path(os.getcwd()) / "workout"
            
            output_dir.mkdir(exist_ok=True)

            # Sanitize topic for filename
            clean_topic = "".join(c for c in session.goal if c.isalnum() or c in (' ', '-', '_')).rstrip()
            date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"debate_{clean_topic}_{date_str}.md"
            file_path = output_dir / filename

            # Construct the full report
            report_parts = []
            report_parts.append("# 辩论结果报告")
            report_parts.append(f"\n**辩论主题**: {session.goal}")
            report_parts.append(f"**辩论时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_parts.append(f"**参与角色**: {', '.join(session.participant_ids)}")
            report_parts.append(f"**辩论轮数**: {self._current_debate.get('total_rounds', 'N/A')}")

            # Add Transcript Section
            if session.history:
                report_parts.append("\n## 辩论过程")
                for turn in session.history:
                    report_parts.append(f"\n**{turn.participant_id}:** {turn.content}")
            
            # Add Summary Section
            if session.summary:
                report_parts.append("\n## 辩论总结")
                report_parts.append(f"\n{session.summary}")

            report_parts.append("\n---")
            report_parts.append("*此报告由人格AI系统自动生成*")

            debate_content = "\n".join(report_parts)

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(debate_content)

            self._update_log_view(f"[bold green]> 💾 辩论报告已保存至: {file_path}[/bold green]")

        except Exception as e:
            self._update_log_view(f"[bold red]> ❌ 保存辩论报告失败: {e}[/bold red]")

    def _clear_current_session_context(self) -> None:
        """Clear current session context and reset token usage."""
        try:
            # Clear current session history
            if self._current_session_id:
                session = self._session_manager.get_session(self._current_session_id)
                if session:
                    # Clear history and compressed history
                    session.history = []
                    session.compressed_history = None
                    session.summary = None
                    self._update_log_view(f"[bold green]> ✅ 会话 '{self._current_session_id}' 上下文已清除[/bold green]")
                else:
                    self._update_log_view("[bold yellow]> ⚠️ 没有活动的会话[/bold yellow]")
            else:
                self._update_log_view("[bold yellow]> ⚠️ 没有活动的会话[/bold yellow]")

            # Also reset token usage
            self._reset_token_usage()

        except Exception as e:
            self._update_log_view(f"[bold red]> 清除会话上下文时出错: {e}[/bold red]")

    def _reset_token_usage(self) -> None:
        """Reset token usage counter to zero."""
        try:
            # Reset both token usage trackers
            self._token_usage = (0, 8192)
            self._real_token_usage = (0, 8192)

            # Reset model metrics
            self._model_metrics = {
                'request_count': 0,
                'total_latency': 0.0,
                'last_request_time': None
            }

            self._update_log_view("[bold green]> ✅ Token使用量已重置为 0[/bold green]")
            self._update_status_bar("Token使用量已重置")

        except Exception as e:
            self._update_log_view(f"[bold red]> 重置Token使用量时出错: {e}[/bold red]")

    def _handle_token_limit_exceeded(self, usage_percentage: float) -> None:
        """Handle token limit exceeded by triggering context compression at 80% threshold."""
        try:
            # Show warning message
            self._update_log_view(f"[bold yellow]> ⚠️ Token使用量已达到 {usage_percentage:.1f}%，触发自动压缩[/bold yellow]")

            # Try to compress current session context
            if not self._current_session_id:
                # Create a default session for auto compression
                self._update_log_view("[bold blue]> 🔄 创建会话进行自动压缩...[/bold blue]")
                session = self._session_manager.create_session(
                    goal="Auto Compression Session",
                    session_type="auto_compression",
                    participant_ids=["user", "assistant"]
                )
                self._current_session_id = session.session_id
            else:
                session = self._session_manager.get_session(self._current_session_id)

            if session and len(session.history) > 5:  # Lower threshold for compression
                # Use memory service to compress history
                if hasattr(self, '_memory_service') and self._memory_service:
                    self._update_log_view("[bold blue]> 🔄 正在智能压缩上下文...[/bold blue]")
                    asyncio.create_task(self._compress_session_context_async(session))
                else:
                    # Fallback: clear oldest history entries
                    session.history = session.history[-3:]  # Keep last 3 entries
                    session.compressed_history = None
                    self._update_log_view("[bold green]> ✅ 已手动清理历史记录[/bold green]")
            else:
                self._update_log_view("[bold blue]> 📝 会话历史较短，跳过压缩[/bold blue]")

            # Show compression complete message
            self._update_status_bar("80%压缩完成")

        except Exception as e:
            self._update_log_view(f"[bold red]> 处理80%Token压缩时出错: {e}[/bold red]")

    async def _compress_session_context_async(self, session) -> None:
        """Asynchronously compress session context using memory service."""
        try:
            await self._memory_service.compress_history(session)
            self._update_log_view("[bold green]> ✅ 上下文压缩完成[/bold green]")
        except Exception as e:
            self._update_log_view(f"[bold red]> 压缩上下文时出错: {e}[/bold red]")
            # Fallback: clear some history
            session.history = session.history[-5:]
            session.compressed_history = None
            self._update_log_view("[bold yellow]> ✅ 已手动清理历史记录[/bold green]")

    # Debate lifecycle wait methods for testing
    async def wait_debate_started(self, timeout: float = 30.0) -> None:
        """Wait for the debate to start."""
        try:
            await asyncio.wait_for(self._debate_started_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Debate did not start within {timeout} seconds")

    async def wait_debate_completed(self, timeout: float = 120.0) -> None:
        """Wait for the debate to complete."""
        try:
            await asyncio.wait_for(self._debate_completed_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Debate did not complete within {timeout} seconds")

    def _get_participant_colors(self, participant_names: list[str]) -> dict:
        """Get color assignments for debate participants."""
        colors = [
            "#87CEEB",  # Light blue
            "#FFB6C1",  # Light pink
            "#98FB98",  # Pale green
            "#DDA0DD",  # Plum
            "#F0E68C",  # Khaki
            "#FFA07A",  # Light salmon
            "#20B2AA",  # Light sea green
            "#9370DB",  # Medium purple
        ]
        
        participant_colors = {}
        for i, name in enumerate(participant_names):
            color = colors[i % len(colors)]  # Cycle through colors if more participants than colors
            participant_colors[name] = color
        
        return participant_colors

    async def wait_participant(self, participant: str, timeout: float = 60.0) -> None:
        """Wait for a specific participant to take their turn."""
        if participant not in self._participant_events:
            self._participant_events[participant] = asyncio.Event()

        try:
            await asyncio.wait_for(self._participant_events[participant].wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Participant {participant} did not speak within {timeout} seconds")
