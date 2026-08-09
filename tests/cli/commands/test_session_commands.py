"""
测试会话管理命令
遵循TDD原则 - 先写测试，后写实现
"""

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from daip_live.core.models import AgentState, DialogueTurn, Session

# We'll import the actual command module once we create it
# from daip_live.cli.commands.session import app as session_app


@pytest.fixture(autouse=True)
def _isolate_config_manager(monkeypatch):
    """会话命令的 _get_db_manager 会读根目录 config.yaml（session.py:23-30），
    前置测试可能删除/修改该文件导致全量顺序敏感失败；统一 patch 为有效配置"""
    from daip_live.cli.commands import session as session_module

    mock_config = Mock()
    mock_config.model_dump.return_value = {"database": {"path": ":memory:"}}
    mock_config_manager = Mock()
    mock_config_manager.get_config.return_value = mock_config
    monkeypatch.setattr(session_module, "ConfigManager", lambda: mock_config_manager)


class TestSessionListCommand:
    """测试会话列表命令"""

    def test_session_list_command_exists(self):
        """测试会话列表命令是否存在"""
        # This will fail initially until we create the command
        from daip_live.cli.commands.session import app as session_app

        # Verify the app exists
        assert session_app is not None

    def test_session_list_help_text(self):
        """测试会话列表命令帮助文本"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()
        result = runner.invoke(session_app, ["--help"])

        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "sessions" in result.stdout.lower()

    def test_session_list_basic_functionality(self):
        """测试会话列表基本功能"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        # Mock the session manager and database
        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            # Setup database mock
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            # Setup session manager mock
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            # Mock return data (real contract: list of pydantic Session models)
            mock_sessions = [
                Session(
                    session_id="session-1",
                    goal="Discuss AI ethics",
                    session_type="debate",
                    participant_ids=["agent1", "agent2"],
                    status=AgentState.RUNNING,
                ),
                Session(
                    session_id="session-2",
                    goal="Plan project architecture",
                    session_type="workflow",
                    participant_ids=["agent3"],
                    status=AgentState.COMPLETED,
                ),
            ]
            mock_manager.list_sessions.return_value = mock_sessions

            result = runner.invoke(session_app, ["list"])

            assert result.exit_code == 0
            assert "session-1" in result.stdout
            assert "session-2" in result.stdout
            assert "Discuss AI" in result.stdout or "AI ethics" in result.stdout

    def test_session_list_empty_sessions(self):
        """测试空会话列表"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.list_sessions.return_value = []

            result = runner.invoke(session_app, ["list"])

            assert result.exit_code == 0
            assert (
                "No sessions" in result.stdout
                or "sessions found" in result.stdout.lower()
            )

    def test_session_list_with_json_output(self):
        """测试JSON格式输出"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            mock_sessions = [
                Session(
                    session_id="session-1",
                    goal="Test session",
                    session_type="chat",
                    participant_ids=[],
                    status=AgentState.RUNNING,
                )
            ]
            mock_manager.list_sessions.return_value = mock_sessions

            result = runner.invoke(session_app, ["list", "--json"])

            assert result.exit_code == 0
            # Verify JSON output
            import json

            output_data = json.loads(result.stdout)
            assert "sessions" in output_data
            assert len(output_data["sessions"]) == 1

    def test_session_list_with_filter_by_type(self):
        """测试按类型过滤会话"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            mock_sessions = [
                Session(
                    session_id="session-1",
                    session_type="debate",
                    goal="g1",
                    participant_ids=[],
                ),
                Session(
                    session_id="session-2",
                    session_type="workflow",
                    goal="g2",
                    participant_ids=[],
                ),
                Session(
                    session_id="session-3",
                    session_type="debate",
                    goal="g3",
                    participant_ids=[],
                ),
            ]
            mock_manager.list_sessions.return_value = mock_sessions

            result = runner.invoke(session_app, ["list", "--type", "debate"])

            assert result.exit_code == 0
            assert "session-1" in result.stdout
            assert "session-3" in result.stdout
            assert "session-2" not in result.stdout

    def test_session_list_with_filter_by_status(self):
        """测试按状态过滤会话"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            mock_sessions = [
                Session(
                    session_id="session-1",
                    status=AgentState.RUNNING,
                    session_type="chat",
                    goal="g1",
                    participant_ids=[],
                ),
                Session(
                    session_id="session-2",
                    status=AgentState.COMPLETED,
                    session_type="chat",
                    goal="g2",
                    participant_ids=[],
                ),
                Session(
                    session_id="session-3",
                    status=AgentState.IDLE,
                    session_type="chat",
                    goal="g3",
                    participant_ids=[],
                ),
            ]
            mock_manager.list_sessions.return_value = mock_sessions

            result = runner.invoke(session_app, ["list", "--status", "running"])

            assert result.exit_code == 0
            assert "session-1" in result.stdout
            assert "session-2" not in result.stdout
            assert "session-3" not in result.stdout

    def test_session_list_with_limit(self):
        """测试限制数量"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            mock_sessions = [
                Session(
                    session_id=f"session-{i}",
                    goal=f"Session {i}",
                    session_type="chat",
                    participant_ids=[],
                )
                for i in range(10)
            ]
            mock_manager.list_sessions.return_value = mock_sessions

            result = runner.invoke(session_app, ["list", "--limit", "5"])

            assert result.exit_code == 0
            assert (
                len([line for line in result.stdout.split("\n") if "session-" in line])
                <= 5
            )

    def test_session_list_with_verbose_output(self):
        """测试详细输出"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            from datetime import datetime, timezone

            datetime.now(timezone.utc)

            mock_sessions = [
                Session(
                    session_id="session-1",
                    goal="Detailed session",
                    session_type="debate",
                    participant_ids=["agent1", "agent2", "agent3"],
                    status=AgentState.RUNNING,
                    history=[
                        DialogueTurn(participant_id="agent1", content=f"turn {i}")
                        for i in range(15)
                    ],
                    summary="A comprehensive debate on AI topics",
                )
            ]
            mock_manager.list_sessions.return_value = mock_sessions

            result = runner.invoke(session_app, ["list", "--verbose"])

            assert result.exit_code == 0
            assert "3" in result.stdout or "participants" in result.stdout
            assert "15" in result.stdout
            assert "Detailed" in result.stdout or "session" in result.stdout

    def test_session_list_with_error_handling(self):
        """测试错误处理"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.list_sessions.side_effect = Exception(
                "Database connection failed"
            )

            result = runner.invoke(session_app, ["list"])

            # Should handle error gracefully
            assert result.exit_code != 0
            assert "error" in result.stdout.lower()

    def test_session_list_performance_monitoring_integration(self):
        """测试性能监控集成"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.list_sessions.return_value = []

            result = runner.invoke(session_app, ["list"])

            assert result.exit_code == 0
            # Command should work, performance monitoring is tested elsewhere


class TestSessionClearCommand:
    """测试会话清理命令"""

    def test_session_clear_command_exists(self):
        """测试会话清理命令是否存在"""
        from daip_live.cli.commands.session import app as session_app

        assert session_app is not None

    def test_session_clear_with_confirmation(self):
        """测试带确认的会话清理"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.clear_all_sessions.return_value = 3

            # Simulate user confirmation
            with patch("typer.confirm") as mock_confirm:
                mock_confirm.return_value = True

                result = runner.invoke(session_app, ["clear"])

                assert result.exit_code == 0
                mock_confirm.assert_called_once()
                mock_manager.clear_all_sessions.assert_called_once()

    def test_session_clear_without_confirmation(self):
        """测试无确认的会话清理"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.clear_all_sessions.return_value = 2

            result = runner.invoke(session_app, ["clear", "--force"])

            assert result.exit_code == 0
            mock_manager.clear_all_sessions.assert_called_once()

    def test_session_clear_cancelled(self):
        """测试取消清理"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            # Simulate user cancellation
            with patch("typer.confirm") as mock_confirm:
                mock_confirm.return_value = False

                result = runner.invoke(session_app, ["clear"])

                assert result.exit_code == 0
                mock_confirm.assert_called_once()
                mock_manager.clear_all_sessions.assert_not_called()

    def test_session_clear_empty_database(self):
        """测试清理空数据库"""
        from daip_live.cli.commands.session import app as session_app

        runner = CliRunner()

        with (
            patch("daip_live.cli.commands.session.DatabaseManager") as mock_db_class,
            patch(
                "daip_live.cli.commands.session.SessionManager"
            ) as mock_manager_class,
        ):
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.clear_all_sessions.return_value = 0

            with patch("typer.confirm") as mock_confirm:
                mock_confirm.return_value = True

                result = runner.invoke(session_app, ["clear"])

                assert result.exit_code == 0
                assert (
                    "No sessions to clear" in result.stdout
                    or "already empty" in result.stdout.lower()
                )
