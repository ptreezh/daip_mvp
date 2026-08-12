"""
Unit tests for TUI background task management functionality.

Aligned with the current SimplifiedTUI implementation:
- on_unmount schedules cleanup() via asyncio.create_task (it does not cancel tasks)
- The active on_key delegates to _handle_system_keys (ctrl+e / ctrl+q exit
  confirmation, ESC exit output mode, input edit keys) and additionally
  handles ctrl+c / ctrl+a (copy). The former shadowing bug (a later on_key
  definition silently replacing the earlier one) was fixed on 2026-08-09 by
  merging both handlers into one dispatch.
- _handle_quit_command is async and delegates to action_quit
- _handle_compact_command replaces the removed _compress_session_context_async
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from daip_live.tui.simplified_main import SimplifiedTUI


class TestTUIBackgroundTaskManagement:
    """Test cases for TUI background task management functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch("daip_live.container.Container"):
            app = SimplifiedTUI()
            return app

    def test_background_tasks_set_initialized(self, tui_app):
        """Test that background tasks set is initialized."""
        # Assert
        assert hasattr(tui_app, "_background_tasks")
        assert isinstance(tui_app._background_tasks, set)

    @pytest.mark.asyncio
    async def test_on_unmount_schedules_cleanup(self, tui_app):
        """Test that unmounting the app schedules the async cleanup task."""
        # Setup - side_effect routes the coroutine to the real asyncio.create_task,
        # which executes the AsyncMock cleanup without a "never awaited" warning
        with patch.object(tui_app, "cleanup", new=AsyncMock()) as mock_cleanup:
            with patch(
                "asyncio.create_task", side_effect=asyncio.create_task
            ) as mock_create_task:
                # Execute
                tui_app.on_unmount()

                # Let the scheduled cleanup task run
                await asyncio.sleep(0)

                # Assert - cleanup was scheduled as a task and executed
                mock_create_task.assert_called_once()
                mock_cleanup.assert_awaited_once()

    def test_ctrl_e_shortcut_handled_by_on_key(self, tui_app):
        """ctrl+e 由 on_key 委托的系统快捷键处理触发退出确认（2026-08-09 修复 shadowing 后）。"""  # noqa: E501
        # Setup
        event = Mock()
        event.key = "ctrl+e"

        with patch.object(
            tui_app, "action_show_exit_confirmation"
        ) as mock_confirmation:
            # Execute
            tui_app.on_key(event)

            # Assert - 系统快捷键处理 ctrl+e，触发退出确认并阻止默认行为
            mock_confirmation.assert_called_once()
            event.prevent_default.assert_called_once()

    def test_ctrl_q_shortcut_handled_by_on_key(self, tui_app):
        """ctrl+q 由 on_key 委托的系统快捷键处理触发退出确认（2026-08-09 修复 shadowing 后）。"""  # noqa: E501
        # Setup
        event = Mock()
        event.key = "ctrl+q"

        with patch.object(
            tui_app, "action_show_exit_confirmation"
        ) as mock_confirmation:
            # Execute
            tui_app.on_key(event)

            # Assert - 系统快捷键处理 ctrl+q，触发退出确认并阻止默认行为
            mock_confirmation.assert_called_once()
            event.prevent_default.assert_called_once()

    @pytest.mark.asyncio
    async def test_ctrl_c_shortcut_copies_content(self, tui_app):
        """ctrl+c 由激活的 on_key 处理，触发复制（通过 asyncio.create_task 调度）。"""
        # Setup
        event = Mock()
        event.key = "ctrl+c"

        with patch.object(tui_app, "action_copy_text", new=AsyncMock()) as mock_copy:
            # Execute
            tui_app.on_key(event)
            await asyncio.sleep(0)  # 让调度出的复制任务执行

            # Assert
            mock_copy.assert_awaited_once()
            event.prevent_default.assert_called_once()

    @pytest.mark.asyncio
    async def test_ctrl_a_shortcut_copies_content(self, tui_app):
        """ctrl+a 由激活的 on_key 处理，触发复制（通过 asyncio.create_task 调度）。"""
        # Setup
        event = Mock()
        event.key = "ctrl+a"

        with patch.object(tui_app, "action_copy_text", new=AsyncMock()) as mock_copy:
            # Execute
            tui_app.on_key(event)
            await asyncio.sleep(0)  # 让调度出的复制任务执行

            # Assert
            mock_copy.assert_awaited_once()
            event.prevent_default.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_quit_command_async(self, tui_app):
        """Test that the quit command logs and delegates to action_quit."""
        # Setup - the implementation fires action_quit() without awaiting it,
        # so a plain Mock (not AsyncMock) avoids a never-awaited coroutine warning
        with patch.object(tui_app, "action_quit", new=Mock()) as mock_quit:
            with patch.object(tui_app, "_update_log_view") as mock_update_log:
                # Execute
                await tui_app._handle_quit_command("")

                # Assert
                mock_quit.assert_called_once()
                mock_update_log.assert_any_call(
                    "[bold yellow]👋 正在退出...[/bold yellow]"
                )

    @pytest.mark.asyncio
    async def test_handle_compact_command_with_session(self, tui_app):
        """Test that compacting a session with an active session reports success."""
        # Setup
        tui_app._current_session_id = "sess-1"
        # 构造真实压缩所需依赖
        session = MagicMock()
        session.history = [MagicMock() for _ in range(10)]
        session.compressed_history = None
        tui_app._session_manager = MagicMock()
        tui_app._session_manager.get_session.return_value = session
        tui_app._memory_service = AsyncMock()

        async def fake_compress(s):
            s.compressed_history = "压缩摘要内容"

        tui_app._memory_service.compress_history.side_effect = fake_compress

        with patch.object(tui_app, "_update_log_view") as mock_update_log:
            # Execute
            await tui_app._handle_compact_command("")

            # Assert
            tui_app._memory_service.compress_history.assert_awaited_once_with(session)
            tui_app._session_manager.save_session.assert_called_once_with(session)
            joined = " ".join(str(c[0][0]) for c in mock_update_log.call_args_list)
            assert "压缩完成" in joined
            assert "10 条历史" in joined

    @pytest.mark.asyncio
    async def test_handle_compact_command_without_session(self, tui_app):
        """Test that compacting without an active session shows a warning."""
        # Setup
        tui_app._current_session_id = None
        tui_app._session_manager = None

        with patch.object(tui_app, "_update_log_view") as mock_update_log:
            # Execute
            await tui_app._handle_compact_command("")

            # Assert
            mock_update_log.assert_any_call("[yellow]⚠️ 没有活动会话可以压缩[/yellow]")
            for call in mock_update_log.call_args_list:
                assert "✅ 会话压缩完成" not in call[0][0]
