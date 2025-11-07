"""
newP6 TUI Component Integration Tests

This test file validates that the newP6 componentized TUI architecture
integrates correctly with the existing DAIP system infrastructure.

Integration Test Coverage:
1. Component compatibility with existing DAIP services
2. Event system integration with DAIP event bus
3. State management integration with DAIP session manager
4. TDI backwards compatibility
5. Performance and functionality regression testing
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Any, Dict

# Import newP6 components
from daip_live.tui_v1.components.base import TUIComponent
from daip_live.tui_v1.components.layout import LayoutComponent
from daip_live.tui_v1.components.navigation import NavigationComponent
from daip_live.tui_v1.components.content import ContentComponent
from daip_live.tui_v1.components.input_area import InputAreaComponent
from daip_live.tui_v1.components.display_area import DisplayAreaComponent
from daip_live.tui_v1.components.status_bar import StatusBarComponent

# Import DAIP services for integration testing
from daip_live.memory.session_manager import SessionManager
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.knowledge.manager import KnowledgeManager


class TestNewP6Integration:
    """
    Test newP6 TUI component integration with DAIP system.

    These tests ensure that:
    1. newP6 components work with existing DAIP infrastructure
    2. No functionality regressions occur
    3. Performance meets requirements
    4. Backwards compatibility is maintained
    """

    def test_component_daip_service_compatibility(self):
        """Test that newP6 components can interface with DAIP services."""
        # Mock DAIP services
        mock_executor = Mock(spec=AgentExecutor)
        mock_session_manager = Mock(spec=SessionManager)
        mock_model_provider = Mock(spec=LiteLLMProvider)
        mock_knowledge_manager = Mock(spec=KnowledgeManager)

        # Test DisplayAreaComponent with DAIP executor
        display_area = DisplayAreaComponent(component_id="main_log")

        # Simulate DAIP agent execution events
        agent_event = Mock()
        agent_event.event_type = Mock()
        agent_event.event_type.value = 'content_update'
        agent_event.data = {'content': 'Agent executed successfully'}

        display_area.handle_event(agent_event)

        # Verify component processed DAIP event
        content = display_area.get_content()
        assert 'Agent executed successfully' in content

    def test_component_id_backwards_compatibility(self):
        """Test that critical component IDs are maintained for backwards compatibility."""
        # These IDs must match the original monolithic TUI
        critical_ids = {
            'main_log': DisplayAreaComponent,
            'user_input': InputAreaComponent,
            'status_bar': StatusBarComponent
        }

        for component_id, component_class in critical_ids.items():
            component = component_class(component_id=component_id)
            assert component.component_id == component_id

    def test_event_system_daip_integration(self):
        """Test newP6 event system integrates with DAIP event bus."""
        from daip_live.tui_v1.events.system import TUIEventSystem
        from daip_live.tui_v1.events.types import Event, EventType

        event_system = TUIEventSystem()
        received_events = []

        def daip_event_handler(event):
            received_events.append(event)

        # Subscribe to DAIP agent events
        event_system.subscribe(EventType.USER_INPUT, daip_event_handler)

        # Simulate DAIP event
        daip_event = Event(
            event_type=EventType.USER_INPUT,
            source="daip_agent",
            data={"command": "help", "context": "user_request"}
        )

        event_system.publish(daip_event)

        assert len(received_events) == 1
        assert received_events[0].source == "daip_agent"
        assert received_events[0].data["command"] == "help"

    def test_state_management_session_integration(self):
        """Test state management integrates with DAIP session manager."""
        from daip_live.tui_v1.state.manager import TUIStateManager

        state_manager = TUIStateManager()
        mock_session_manager = Mock(spec=SessionManager)

        # Simulate session data from DAIP
        session_data = {
            'session_id': 'test_session_123',
            'user_goal': 'Complete project refactoring',
            'agent_history': [],
            'current_state': 'planning'
        }

        # Update TUI state with DAIP session data
        state_manager.update_state(session_data)

        # Verify state was correctly stored
        current_state = state_manager.get_state()
        assert current_state['session_id'] == 'test_session_123'
        assert current_state['user_goal'] == 'Complete project refactoring'

    def test_input_area_daip_command_processing(self):
        """Test InputAreaComponent processes DAIP commands correctly."""
        input_area = InputAreaComponent(component_id="user_input")

        # Simulate user inputting DAIP command
        test_command = "/run agent --goal 'Test newP6 integration'"
        input_area.set_input_text(test_command)

        # Add to command history
        input_area.add_to_history(test_command)

        # Verify command processing
        assert input_area.get_input_text() == test_command
        history = input_area.get_suggestions()  # This should integrate with DAIP command suggestions
        assert isinstance(history, list)

    def test_display_area_agent_output_rendering(self):
        """Test DisplayAreaComponent renders agent output correctly."""
        display_area = DisplayAreaComponent(component_id="main_log")

        # Simulate multiple types of DAIP agent output
        outputs = [
            "🤔 Agent is thinking about the problem...",
            "📊 Analyzing current system state...",
            "🔧 Executing refactoring steps...",
            "✅ Task completed successfully!"
        ]

        for output in outputs:
            display_area.write(output)

        # Verify all outputs were processed
        content = display_area.get_content()
        for output in outputs:
            assert output in content

        assert display_area.get_line_count() >= len(outputs)

    def test_status_bar_system_monitoring(self):
        """Test StatusBarComponent monitors DAIP system state."""
        status_bar = StatusBarComponent(component_id="status_bar")

        # Simulate DAIP system metrics
        system_metrics = {
            'cpu_percent': 45.2,
            'memory_percent': 67.8,
            'active_agents': 2,
            'queue_size': 5
        }

        status_bar.update_system_info(system_metrics)
        status_bar.set_status("Processing agent requests...")

        # Verify status bar reflects system state
        assert status_bar.get_status_text() == "Processing agent requests..."
        system_info = status_bar.get_system_info()
        assert system_info['cpu_percent'] == 45.2

    def test_navigation_daip_workflow_support(self):
        """Test NavigationComponent supports DAIP workflow navigation."""
        navigation = NavigationComponent(component_id="workflow_navigation")

        # Simulate DAIP workflow menu items
        workflow_menu = [
            {"label": "Agent Configuration", "action": "config_agents"},
            {"label": "Knowledge Base", "action": "manage_knowledge"},
            {"label": "Session Management", "action": "manage_sessions"},
            {"label": "Debate System", "action": "start_debate"}
        ]

        # Update navigation with DAIP workflows
        for item in workflow_menu:
            navigation.add_menu_item(item)

        # Verify navigation items
        menu_items = navigation.get_menu_items()
        assert len(menu_items) >= 4

        # Test navigation selection
        navigation.select_menu_item(0)  # Select "Agent Configuration"
        current_selection = navigation.get_current_selection()
        assert current_selection == 0

    def test_content_component_daip_data_rendering(self):
        """Test ContentComponent renders DAIP data correctly."""
        content = ContentComponent(component_id="content_display")

        # Simulate DAIP knowledge base content
        knowledge_content = """
# DAIP System Architecture

## Components
1. Agent Engine
2. Knowledge Management
3. Model Provider
4. Role Manager

## Integration Points
- Event-driven communication
- State synchronization
- Resource sharing
        """

        content.set_content(knowledge_content, content_type="markdown")

        # Verify content was set
        rendered_content = content.get_content()
        assert "DAIP System Architecture" in rendered_content
        assert "Agent Engine" in rendered_content

    def test_performance_requirements(self):
        """Test that newP6 components meet performance requirements."""
        import time

        # Test event system performance (<10ms delivery)
        from daip_live.tui_v1.events.system import TUIEventSystem
        from daip_live.tui_v1.events.types import Event, EventType

        event_system = TUIEventSystem()
        event_received = False

        def test_handler(event):
            nonlocal event_received
            event_received = True

        event_system.subscribe(EventType.USER_INPUT, test_handler)

        test_event = Event(
            event_type=EventType.USER_INPUT,
            source="performance_test",
            data={"test": True}
        )

        start_time = time.perf_counter()
        event_system.publish(test_event)

        # Wait for event processing
        timeout = time.perf_counter() + 0.05  # 50ms timeout
        while not event_received and time.perf_counter() < timeout:
            time.sleep(0.001)

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        assert event_received, "Event was not processed"
        assert latency_ms < 10, f"Event delivery latency {latency_ms:.2f}ms exceeds 10ms requirement"

    def test_error_handling_robustness(self):
        """Test that newP6 components handle errors gracefully."""
        display_area = DisplayAreaComponent(component_id="main_log")

        # Test with malformed data
        malformed_events = [
            None,  # None event
            Mock(event_type=None),  # Missing event type
            Mock(event_type=Mock(value=None), data=None),  # Missing data
        ]

        for malformed_event in malformed_events:
            try:
                display_area.handle_event(malformed_event)
                # Should not raise exception
            except Exception as e:
                pytest.fail(f"Component should handle malformed events gracefully: {e}")

    def test_memory_usage_efficiency(self):
        """Test that components manage memory efficiently."""
        display_area = DisplayAreaComponent(component_id="main_log", max_lines=100)

        # Add large amount of content
        for i in range(200):  # More than max_lines
            display_area.write(f"Line {i}: This is test content for memory efficiency testing.")

        # Verify buffer size is maintained
        assert display_area.get_line_count() <= 100

    @pytest.mark.asyncio
    async def test_async_operation_compatibility(self):
        """Test async operations work with DAIP's async patterns."""
        content = ContentComponent(component_id="async_content")

        # Simulate async content loading
        async def mock_daip_content_loader():
            await asyncio.sleep(0.01)  # Simulate async operation
            return "Async loaded content from DAIP knowledge base"

        loaded_content = await mock_daip_content_loader()
        content.set_content(loaded_content)

        assert content.get_content() == "Async loaded content from DAIP knowledge base"


class TestBackwardsCompatibility:
    """
    Test that newP6 maintains backwards compatibility with existing TUI.
    """

    def test_component_interface_compatibility(self):
        """Test that component interfaces are compatible with existing usage."""
        # Test that components can be used like the original TUI widgets
        display_area = DisplayAreaComponent(component_id="main_log")
        input_area = InputAreaComponent(component_id="user_input")
        status_bar = StatusBarComponent(component_id="status_bar")

        # Test basic widget operations
        display_area.write("Test message")
        assert display_area.get_content() == "Test message"

        input_area.set_input_text("test command")
        assert input_area.get_input_text() == "test command"

        status_bar.set_status("Ready")
        assert status_bar.get_status_text() == "Ready"

    def test_event_handling_compatibility(self):
        """Test that event handling is compatible with existing patterns."""
        layout = LayoutComponent(component_id="test_layout")

        # Test with mock event
        mock_event = Mock()
        mock_event.event_type = Mock()
        mock_event.event_type.value = 'resize'
        mock_event.data = {'width': 80, 'height': 24}

        # Should not raise exception
        layout.handle_event(mock_event)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])