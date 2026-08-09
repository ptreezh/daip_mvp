"""
DAIP Status Bar Tests for newP6 TUI

This test suite implements TDD approach for real-time status bar functionality.
Tests are written first (RED), then implementation follows (GREEN), then refactoring.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import real implementations (will fail initially - RED phase)
from daip_live.tui_v1.status_bar.status_bar import StatusBar
from daip_live.tui_v1.status_bar.status_updater import StatusUpdater
from daip_live.tui_v1.status_bar.status_widget import StatusWidget

# RED TESTS - These will fail initially, driving implementation


class TestStatusBar:
    """Test main status bar functionality"""

    def test_status_bar_creation(self):
        """Test status bar creation"""
        # This will fail initially - driving need for StatusBar class
        status_bar = StatusBar()

        assert status_bar is not None
        assert hasattr(status_bar, "_widgets")
        assert hasattr(status_bar, "_updater")
        assert hasattr(status_bar, "_visible")
        assert status_bar._visible

    def test_status_bar_initialization(self):
        """Test status bar initialization with dependencies"""
        mock_event_system = Mock()
        mock_state_manager = Mock()
        mock_service_container = Mock()

        status_bar = StatusBar()
        status_bar.initialize(
            mock_event_system, mock_state_manager, mock_service_container
        )

        assert status_bar.event_system == mock_event_system
        assert status_bar.state_manager == mock_state_manager
        assert status_bar.service_container == mock_service_container
        assert status_bar._initialized

    def test_add_status_widget(self):
        """Test adding status widgets"""
        status_bar = StatusBar()
        mock_widget = Mock(spec=StatusWidget)
        mock_widget.name = "test_widget"

        status_bar.add_widget(mock_widget)

        assert len(status_bar._widgets) == 1
        assert "test_widget" in status_bar._widgets
        assert status_bar._widgets["test_widget"] == mock_widget

    def test_remove_status_widget(self):
        """Test removing status widgets"""
        status_bar = StatusBar()
        mock_widget = Mock(spec=StatusWidget)
        mock_widget.name = "test_widget"

        status_bar.add_widget(mock_widget)
        assert len(status_bar._widgets) == 1

        status_bar.remove_widget("test_widget")
        assert len(status_bar._widgets) == 0
        assert "test_widget" not in status_bar._widgets

    def test_get_widget(self):
        """Test retrieving status widgets"""
        status_bar = StatusBar()
        mock_widget = Mock(spec=StatusWidget)
        mock_widget.name = "test_widget"

        status_bar.add_widget(mock_widget)
        retrieved = status_bar.get_widget("test_widget")

        assert retrieved == mock_widget

    def test_get_nonexistent_widget(self):
        """Test retrieving non-existent widget returns None"""
        status_bar = StatusBar()

        result = status_bar.get_widget("nonexistent")
        assert result is None

    def test_status_bar_visibility(self):
        """Test status bar visibility control"""
        status_bar = StatusBar()

        # Default should be visible
        assert status_bar.is_visible()

        status_bar.hide()
        assert not status_bar.is_visible()

        status_bar.show()
        assert status_bar.is_visible()

    def test_refresh_status_bar(self):
        """Test refreshing all widgets"""
        status_bar = StatusBar()
        mock_widget1 = Mock(spec=StatusWidget)
        mock_widget2 = Mock(spec=StatusWidget)
        mock_widget1.name = "widget1"
        mock_widget2.name = "widget2"

        status_bar.add_widget(mock_widget1)
        status_bar.add_widget(mock_widget2)

        status_bar.refresh()

        mock_widget1.refresh.assert_called_once()
        mock_widget2.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_status_updates(self):
        """Test starting real-time status updates"""
        status_bar = StatusBar()
        mock_updater = Mock(spec=StatusUpdater)
        mock_updater.start = AsyncMock()
        mock_updater.is_running.return_value = False  # Mock that updater is not running
        status_bar._updater = mock_updater

        await status_bar.start_updates()

        mock_updater.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_status_updates(self):
        """Test stopping real-time status updates"""
        status_bar = StatusBar()
        mock_updater = Mock(spec=StatusUpdater)
        mock_updater.stop = AsyncMock()
        status_bar._updater = mock_updater

        await status_bar.stop_updates()

        mock_updater.stop.assert_called_once()

    def test_get_status_bar_content(self):
        """Test getting complete status bar content"""
        status_bar = StatusBar()
        mock_widget1 = Mock(spec=StatusWidget)
        mock_widget2 = Mock(spec=StatusWidget)
        mock_widget1.name = "model_status"
        mock_widget2.name = "session_info"
        mock_widget1.get_content.return_value = "GPT-4 Ready"
        mock_widget2.get_content.return_value = "Session: main"

        status_bar.add_widget(mock_widget1)
        status_bar.add_widget(mock_widget2)

        content = status_bar.get_content()

        assert "model_status" in content
        assert "session_info" in content
        assert content["model_status"] == "GPT-4 Ready"
        assert content["session_info"] == "Session: main"


class TestStatusWidget:
    """Test individual status widget functionality"""

    def test_status_widget_creation(self):
        """Test status widget creation"""
        # Create a concrete test widget
        from daip_live.tui_v1.status_bar.status_widget import StatusWidget

        class TestWidget(StatusWidget):
            async def refresh(self):
                pass

        widget = TestWidget("test_widget", "Test Widget")

        assert widget is not None
        assert widget.name == "test_widget"
        assert widget.label == "Test Widget"
        assert hasattr(widget, "_value")
        assert hasattr(widget, "_last_updated")

    def test_status_widget_update_value(self):
        """Test updating widget value"""
        from daip_live.tui_v1.status_bar.status_widget import StatusWidget

        class TestWidget(StatusWidget):
            async def refresh(self):
                pass

        widget = TestWidget("test_widget", "Test Widget")

        widget.update_value("new_value")

        assert widget._value == "new_value"
        assert widget._last_updated is not None

    def test_status_widget_get_content(self):
        """Test getting widget content"""
        from daip_live.tui_v1.status_bar.status_widget import StatusWidget

        class TestWidget(StatusWidget):
            async def refresh(self):
                pass

        widget = TestWidget("test_widget", "Test Widget")
        widget.update_value("test_value")

        content = widget.get_content()

        assert "test_value" in content
        assert "Test Widget" in content

    def test_status_widget_refresh(self):
        """Test refreshing widget"""
        from daip_live.tui_v1.status_bar.status_widget import StatusWidget

        class TestWidget(StatusWidget):
            def __init__(self, name, label):
                super().__init__(name, label)
                self.refreshed = False

            async def refresh(self):
                self.refreshed = True

        import asyncio

        widget = TestWidget("test_widget", "Test Widget")

        # Run the async refresh
        asyncio.run(widget.refresh())

        assert widget.refreshed

    def test_status_widget_auto_refresh(self):
        """Test widget auto-refresh configuration"""
        from daip_live.tui_v1.status_bar.status_widget import StatusWidget

        class TestWidget(StatusWidget):
            async def refresh(self):
                pass

        widget = TestWidget("test_widget", "Test Widget")

        # Default should not auto-refresh
        assert not widget.auto_refresh

        widget.enable_auto_refresh(1.0)  # 1 second interval
        assert widget.auto_refresh
        assert widget.refresh_interval == 1.0

        widget.disable_auto_refresh()
        assert not widget.auto_refresh


class TestModelStatusWidget:
    """Test model status specific widget"""

    @pytest.fixture
    def mock_model_service(self):
        service = Mock()
        service.get_current_model = AsyncMock(
            return_value={"name": "gpt-4o-mini", "status": "ready"}
        )
        return service

    @pytest.fixture
    def model_widget(self, mock_model_service):
        from daip_live.tui_v1.status_bar.model_widget import ModelStatusWidget

        return ModelStatusWidget(mock_model_service)

    def test_model_widget_creation(self, model_widget):
        """Test model status widget creation"""
        assert model_widget is not None
        assert model_widget.name == "model_status"
        assert model_widget.label == "Model"

    @pytest.mark.asyncio
    async def test_model_widget_refresh(self, model_widget):
        """Test model status widget refresh"""
        await model_widget.refresh()

        content = model_widget.get_content()
        assert "gpt-4o-mini" in content
        assert "ready" in content

    @pytest.mark.asyncio
    async def test_model_widget_no_service(self):
        """Test model widget without service"""
        from daip_live.tui_v1.status_bar.model_widget import ModelStatusWidget

        widget = ModelStatusWidget(None)

        await widget.refresh()

        content = widget.get_content()
        assert "No Model" in content


class TestSessionWidget:
    """Test session information widget"""

    @pytest.fixture
    def mock_session_service(self):
        service = Mock()
        service.get_current_session = AsyncMock(
            return_value={"id": "12345", "name": "main", "status": "active"}
        )
        return service

    @pytest.fixture
    def session_widget(self, mock_session_service):
        from daip_live.tui_v1.status_bar.session_widget import SessionWidget

        return SessionWidget(mock_session_service)

    def test_session_widget_creation(self, session_widget):
        """Test session widget creation"""
        assert session_widget is not None
        assert session_widget.name == "session_info"
        assert session_widget.label == "Session"

    @pytest.mark.asyncio
    async def test_session_widget_refresh(self, session_widget):
        """Test session widget refresh"""
        await session_widget.refresh()

        content = session_widget.get_content()
        assert "main" in content
        assert "active" in content

    @pytest.mark.asyncio
    async def test_session_widget_no_session(self):
        """Test session widget with no active session"""
        from daip_live.tui_v1.status_bar.session_widget import SessionWidget

        service = Mock()
        service.get_current_session = AsyncMock(return_value=None)
        widget = SessionWidget(service)

        await widget.refresh()

        content = widget.get_content()
        assert "No Active Session" in content


class TestStatusUpdater:
    """Test status update coordinator"""

    def test_status_updater_creation(self):
        """Test status updater creation"""
        # This will fail initially - driving need for StatusUpdater class
        updater = StatusUpdater()

        assert updater is not None
        assert hasattr(updater, "_status_bar")
        assert hasattr(updater, "_update_interval")
        assert hasattr(updater, "_running")

    def test_status_updater_initialization(self):
        """Test status updater initialization"""
        updater = StatusUpdater()
        mock_status_bar = Mock(spec=StatusBar)

        updater.initialize(mock_status_bar, 0.5)  # 0.5 second interval

        assert updater._status_bar == mock_status_bar
        assert updater._update_interval == 0.5
        assert not updater._running

    @pytest.mark.asyncio
    async def test_start_updater(self):
        """Test starting status updater"""
        updater = StatusUpdater()
        mock_status_bar = Mock(spec=StatusBar)
        updater.initialize(mock_status_bar, 0.1)

        # Start should not block
        start_task = asyncio.create_task(updater.start())

        # Give it a moment to start
        await asyncio.sleep(0.05)

        assert updater._running

        # Stop the updater
        await updater.stop()
        await start_task

    @pytest.mark.asyncio
    async def test_stop_updater(self):
        """Test stopping status updater"""
        updater = StatusUpdater()
        mock_status_bar = Mock(spec=StatusBar)
        updater.initialize(mock_status_bar, 0.1)

        await updater.start()
        assert updater._running

        await updater.stop()
        assert not updater._running

    @pytest.mark.asyncio
    async def test_update_cycle(self):
        """Test update cycle functionality"""
        updater = StatusUpdater()
        mock_status_bar = Mock(spec=StatusBar)
        mock_status_bar.refresh = Mock()
        updater.initialize(mock_status_bar, 0.05)  # Very fast for testing

        await updater.start()

        # Wait for at least one update cycle
        await asyncio.sleep(0.1)

        await updater.stop()

        # Should have called refresh at least once
        mock_status_bar.refresh.assert_called()


class TestConnectionStatusWidget:
    """Test connection status widget"""

    @pytest.fixture
    def connection_widget(self):
        from daip_live.tui_v1.status_bar.connection_widget import ConnectionStatusWidget

        return ConnectionStatusWidget()

    def test_connection_widget_creation(self, connection_widget):
        """Test connection widget creation"""
        assert connection_widget is not None
        assert connection_widget.name == "connection_status"
        assert connection_widget.label == "Connection"

    def test_connection_widget_update_status(self, connection_widget):
        """Test updating connection status"""
        connection_widget.update_status("connected", "API Connected")

        content = connection_widget.get_content()
        assert "connected" in content
        assert "API Connected" in content

    def test_connection_widget_offline(self, connection_widget):
        """Test connection widget offline status"""
        connection_widget.update_status("offline", "No Connection")

        content = connection_widget.get_content()
        assert "offline" in content
        assert "No Connection" in content


class TestSystemResourceWidget:
    """Test system resource monitoring widget"""

    @pytest.fixture
    def resource_widget(self):
        from daip_live.tui_v1.status_bar.resource_widget import SystemResourceWidget

        return SystemResourceWidget()

    def test_resource_widget_creation(self, resource_widget):
        """Test resource widget creation"""
        assert resource_widget is not None
        assert resource_widget.name == "system_resources"
        assert resource_widget.label == "Resources"

    @pytest.mark.asyncio
    async def test_resource_widget_refresh(self, resource_widget):
        """Test resource widget refresh"""
        # Mock psutil at the module level to handle import issues
        with (
            patch("daip_live.tui_v1.status_bar.resource_widget.psutil") as mock_psutil,
            patch("daip_live.tui_v1.status_bar.resource_widget.PSUTIL_AVAILABLE", True),
        ):
            mock_psutil.cpu_percent.return_value = 25.0
            mock_memory = Mock()
            mock_memory.percent = 60.0
            mock_memory.used = 8_589_934_592  # 8GB
            mock_memory.total = 16_000_000_000  # 16GB
            mock_psutil.virtual_memory.return_value = mock_memory

            await resource_widget.refresh()

            content = resource_widget.get_content()
            assert "CPU" in content
            assert "25.0%" in content
            assert "60.0%" in content

    @pytest.mark.asyncio
    async def test_resource_widget_no_psutil(self, resource_widget):
        """Test resource widget without psutil"""
        # 源码权威: 分支判断用模块级 PSUTIL_AVAILABLE（resource_widget.py:31），
        # 仅 patch psutil 变量不够，须同时 patch 该常量
        with (
            patch("daip_live.tui_v1.status_bar.resource_widget.psutil", None),
            patch(
                "daip_live.tui_v1.status_bar.resource_widget.PSUTIL_AVAILABLE", False
            ),
        ):
            await resource_widget.refresh()

            content = resource_widget.get_content()
            assert "N/A" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
