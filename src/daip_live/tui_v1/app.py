"""
DAIP-LIVE newP6 TUI Application

This is the main TUI application that integrates newP6 componentized architecture
with the existing DAIP system infrastructure.

Features:
- Component-based architecture using newP6 components
- Integration with DAIP services (executor, session manager, etc.)
- Event-driven communication between components
- Real-time status monitoring and display
- Command processing and history
"""

import asyncio
from typing import Any, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header

# Import DAIP services
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.config import ConfigManager

# Import DAIP event models
from daip_live.core.models import (
    AgentEvent,
    ErrorEvent,
    FinalResponseEvent,
    ModelMetricsEvent,
    PermissionRequestEvent,
    ThoughtEvent,
    TokenUsageEvent,
)
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager

# Import newP6 components
from daip_live.tui_v1.components.base import TUIComponent
from daip_live.tui_v1.components.display_area import DisplayAreaComponent
from daip_live.tui_v1.components.input_area import InputAreaComponent
from daip_live.tui_v1.components.layout import LayoutComponent
from daip_live.tui_v1.components.navigation import NavigationComponent
from daip_live.tui_v1.components.status_bar import StatusBarComponent


class DAIPScreen(Screen):
    """Main screen for DAIP-LIVE TUI application."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #header {
        height: 3;
        background: $primary;
        color: $text;
    }

    #main-layout {
        height: 1fr;
    }

    #navigation {
        height: 3;
        background: $secondary;
    }

    #input-area {
        height: 3;
        background: $surface;
    }

    #status-bar {
        height: 3;
        background: $panel;
    }
    """

    def __init__(self, daip_services: dict[str, Any]) -> None:
        """Initialize screen with DAIP services."""
        super().__init__()
        self.daip_services = daip_services
        self.components: dict[str, TUIComponent] = {}

    def compose(self: "DAIPScreen") -> ComposeResult:
        """Compose the screen layout using newP6 components."""
        # Header
        yield Header("DAIP-LIVE Agent Engine V1 - newP6 Architecture", id="header")

        # Main layout container
        main_layout = LayoutComponent(
            component_id="main_layout", layout_type="vertical"
        )

        # Navigation component
        navigation = NavigationComponent(component_id="navigation", show_menu=True)

        # Content display area
        display_area = DisplayAreaComponent(
            component_id="main_log",  # Maintain backwards compatibility
            auto_scroll=True,
            max_lines=1000,
        )

        # Input area
        input_area = InputAreaComponent(
            component_id="user_input",  # Maintain backwards compatibility
            placeholder="Enter command or ask for help...",
            auto_complete=True,
        )

        # Status bar
        status_bar = StatusBarComponent(
            component_id="status_bar",  # Maintain backwards compatibility
            show_progress=True,
            show_time=True,
            show_system_info=True,
        )

        # Store component references
        self.components.update(
            {
                "main_layout": main_layout,
                "navigation": navigation,
                "display_area": display_area,
                "input_area": input_area,
                "status_bar": status_bar,
            }
        )

        # Compose the layout
        yield main_layout.render()
        yield navigation.render()
        yield display_area.render()
        yield input_area.render()
        yield status_bar.render()
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        # Initialize component state
        await self._initialize_components()

        # Set up DAIP service integrations
        await self._setup_daip_integrations()

        # Start background monitoring
        await self._start_monitoring()

        # Initialize skill system and load existing skills after services are set up
        await self._initialize_skills()

    async def _initialize_components(self) -> None:
        """Initialize all newP6 components."""
        for component in self.components.values():
            await component.mount()

        # Set up navigation menu items
        navigation = self.components["navigation"]
        navigation.add_menu_item({"label": "Agent Control", "action": "agent_control"})
        navigation.add_menu_item(
            {"label": "Knowledge Base", "action": "knowledge_manage"}
        )
        navigation.add_menu_item(
            {"label": "Session History", "action": "session_history"}
        )
        navigation.add_menu_item({"label": "Debate System", "action": "debate_system"})
        navigation.add_menu_item(
            {"label": "Skills Management", "action": "skills_manage"}
        )

        # Set up input area with DAIP commands
        input_area = self.components["input_area"]

        def daip_command_suggestions(input_text: str) -> list:
            """Provide DAIP command suggestions."""
            commands = [
                "help",
                "status",
                "quit",
                "clear",
                "agent list",
                "agent switch <name>",
                "session list",
                "session show <id>",
                "knowledge sync",
                "knowledge search <query>",
                "debate start <topic>",
                "debate list",
                "model list",
                "model status",
                "/skill",
                "/ppt",
                "/survey",
            ]
            return [cmd for cmd in commands if cmd.startswith(input_text.lower())]

        input_area.set_suggestions_callback(daip_command_suggestions)

    async def _initialize_skills(self) -> None:
        """Initialize skill system and load existing skills."""
        skill_manager = self.daip_services.get("skill_manager")
        if skill_manager:
            # Load any existing Claude skills from the claude_skills directory
            try:
                loaded_count = skill_manager.load_claude_skills_from_directory(
                    "./claude_skills"
                )
                display_area = self.components["display_area"]
                if loaded_count > 0:
                    display_area.write(
                        f"🔄 已从 ./claude_skills 加载 {loaded_count} 个Claude技能"
                    )
                else:
                    display_area.write(
                        "📁 未找到本地Claude技能，可在需要时从GitHub下载"
                    )
            except Exception:
                pass

    async def _setup_daip_integrations(self) -> None:
        """Set up integration with DAIP services."""
        # Connect display area to DAIP executor events
        display_area = self.components["display_area"]
        executor = self.daip_services.get("executor")

        if executor:
            # Subscribe to executor events
            self._setup_executor_listeners(executor, display_area)

        # Connect status bar to system monitoring
        status_bar = self.components["status_bar"]
        await self._setup_status_monitoring(status_bar)

        # Connect input area to command processing
        input_area = self.components["input_area"]
        await self._setup_command_processing(input_area)

    def _setup_executor_listeners(
        self, executor: AgentExecutor, display_area: DisplayAreaComponent
    ) -> None:
        """Set up event listeners for the agent executor."""
        # This would integrate with DAIP's event system
        # For now, we'll simulate the event handling
        pass

    async def _setup_status_monitoring(self, status_bar: StatusBarComponent) -> None:
        """Set up system status monitoring."""

        # Simulate system metrics updates
        async def update_system_status():
            while True:
                # Update system info (mock implementation)
                system_info = {
                    "cpu_percent": 45.0,
                    "memory_percent": 60.0,
                    "active_agents": 1,
                }
                status_bar.update_system_info(system_info)
                status_bar.update_time()
                await asyncio.sleep(5)  # Update every 5 seconds

        asyncio.create_task(update_system_status())

    async def _setup_command_processing(self, input_area: InputAreaComponent) -> None:
        """Set up command processing for input area."""
        # Get the skill manager and Claude integration service from DAIP services
        skill_manager = self.daip_services.get("skill_manager")
        claude_integration_service = self.daip_services.get(
            "claude_integration_service"
        )

        if skill_manager is None:
            # If not provided in daip_services, create a default one
            from daip_live.skills.manager import SkillManager

            skill_manager = SkillManager()
            self.daip_services["skill_manager"] = skill_manager

        if claude_integration_service is None:
            # Initialize Claude integration service if not provided
            from daip_live.skills.enhanced_integration import (
                EnhancedClaudeSkillsManager,
            )

            claude_integration_service = EnhancedClaudeSkillsManager(skill_manager)
            self.daip_services["claude_integration_service"] = (
                claude_integration_service
            )

        # Setup command processing system
        from daip_live.tui_v1.command.command_processor import setup_command_processing

        self.command_processor = setup_command_processing(
            self,  # Pass self as the tui_app parameter
            skill_manager,
            claude_integration_service,
        )

        # Set up event handling for user input
        async def handle_user_input(event):
            """Handle user input from input area."""
            user_input = input_area.get_input_text()
            if user_input.strip():
                # Try to process as a command first
                result = self.command_processor.process_command(user_input)

                if result:  # If command was processed
                    # Display the command result
                    display_area = self.components["display_area"]
                    display_area.write(result)
                    input_area.clear_input()
                else:
                    # If not a recognized command, it might be a natural language query
                    # This would be handled by the intent recognition system
                    display_area = self.components["display_area"]
                    display_area.write(f"🤔 检测到非命令输入: {user_input}")
                    display_area.write("💡 提示: 输入 /help 查看可用命令")
                    input_area.clear_input()

        # Add callback to input area's submit event
        # This is a simplified implementation - in a real app, you'd connect to actual events  # noqa: E501
        pass

    async def _start_monitoring(self) -> None:
        """Start background monitoring tasks."""
        display_area = self.components["display_area"]
        status_bar = self.components["status_bar"]

        # Display welcome message
        display_area.write("🚀 DAIP-LIVE Agent Engine V1 Started")
        display_area.write("🎭 newP6 Component Architecture Active")
        display_area.write("💡 Type 'help' for available commands")
        display_area.write("─" * 50)

        status_bar.set_status("System Ready")

    def handle_daip_event(self, event: Any) -> None:
        """Handle events from DAIP services."""
        display_area = self.components["display_area"]
        status_bar = self.components["status_bar"]

        # Process different event types
        if isinstance(event, ThoughtEvent):
            display_area.write(f"🤔 {event.content}")
        elif isinstance(event, AgentEvent):
            display_area.write(f"🤖 {event.content}")
        elif isinstance(event, ErrorEvent):
            display_area.write(f"❌ Error: {event.error_message}")
            status_bar.set_error_status(event.error_message)
        elif isinstance(event, FinalResponseEvent):
            display_area.write(f"✅ {event.content}")
            status_bar.set_success_status("Task Completed")
        elif isinstance(event, TokenUsageEvent):
            status_bar.indicate_activity("Processing tokens...")
        elif isinstance(event, ModelMetricsEvent):
            # Update status with model performance metrics
            pass
        elif isinstance(event, PermissionRequestEvent):
            display_area.write(f"🔐 Permission requested: {event.permission_type}")

        # Auto-scroll to bottom for new events
        display_area.scroll_to_bottom()


class DAIPNewP6App(App):
    """Main DAIP-LIVE application using newP6 architecture."""

    CSS = """
    App {
        background: $background;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+q", "quit", "Quit", show=False),
        Binding("f1", "help", "Help", show=True),
        Binding("ctrl+l", "clear", "Clear", show=True),
    ]

    def __init__(self, daip_services: dict[str, Any]) -> None:
        """Initialize app with DAIP services."""
        super().__init__()
        self.daip_services = daip_services
        self.title = "DAIP-LIVE - newP6 Architecture"

    def on_mount(self) -> None:
        """Initialize the application."""
        self.push_screen(DAIPScreen(self.daip_services))

    def action_clear(self) -> None:
        """Clear the display area."""
        screen = self.screen
        if hasattr(screen, "components"):
            display_area = screen.components.get("display_area")
            if display_area:
                display_area.clear()

    def action_help(self) -> None:
        """Show help information."""
        screen = self.screen
        if hasattr(screen, "components"):
            display_area = screen.components.get("display_area")
            if display_area:
                display_area.write("📖 DAIP-LIVE Help")
                display_area.write("─" * 30)
                display_area.write("Available commands:")
                display_area.write("  help     - Show this help")
                display_area.write("  status   - Show system status")
                display_area.write("  clear    - Clear display")
                display_area.write("  quit     - Exit application")
                display_area.write("  agent list - List available agents")
                display_area.write("  session list - Show session history")
                display_area.write("─" * 30)


def create_daip_newp6_app(
    executor: Optional[AgentExecutor] = None,
    session_manager: Optional[SessionManager] = None,
    knowledge_manager: Optional[KnowledgeManager] = None,
    model_provider: Optional[LiteLLMProvider] = None,
    role_manager: Optional[RoleManager] = None,
    debate_manager: Optional[DebateManager] = None,
    db_manager: Optional[DatabaseManager] = None,
    config_manager: Optional[ConfigManager] = None,
    **kwargs,
) -> DAIPNewP6App:
    """
    Create a DAIP-LIVE TUI application with newP6 architecture.

    Args:
        executor: Agent executor service
        session_manager: Session manager service
        knowledge_manager: Knowledge manager service
        model_provider: Model provider service
        role_manager: Role manager service
        debate_manager: Debate manager service
        db_manager: Database manager service
        config_manager: Configuration manager
        **kwargs: Additional services

    Returns:
        DAIPNewP6App: Configured TUI application
    """
    daip_services = {
        "executor": executor,
        "session_manager": session_manager,
        "knowledge_manager": knowledge_manager,
        "model_provider": model_provider,
        "role_manager": role_manager,
        "debate_manager": debate_manager,
        "db_manager": db_manager,
        "config_manager": config_manager,
        **kwargs,
    }

    return DAIPNewP6App(daip_services)
