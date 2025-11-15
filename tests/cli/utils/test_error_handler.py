"""
测试统一错误处理装饰器
遵循TDD原则 - 先写测试，后写实现
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Any, Callable
import typer
from rich.console import Console


class TestErrorHandlerBasics:
    """测试错误处理器基础功能"""

    def test_error_handler_class_exists(self):
        """测试错误处理器类是否存在"""
        from daip_live.cli.utils.error_handler import ErrorHandler

        # Test instantiation
        handler = ErrorHandler()

        # Verify attributes
        assert hasattr(handler, 'console')
        assert isinstance(handler.console, Console)
        assert hasattr(handler, 'logger')
        assert hasattr(handler, 'error_stats')

        # Verify error stats structure
        assert 'total_errors' in handler.error_stats
        assert 'errors_by_category' in handler.error_stats
        assert 'errors_by_severity' in handler.error_stats

    def test_error_stats_initialization(self):
        """测试错误统计初始化"""
        from daip_live.cli.utils.error_handler import ErrorHandler

        handler = ErrorHandler()

        assert handler.error_stats['total_errors'] == 0
        assert handler.error_stats['errors_by_category'] == {}
        assert handler.error_stats['errors_by_severity'] == {}

    def test_record_error_stats(self):
        """测试错误统计记录"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError, ErrorSeverity

        handler = ErrorHandler()
        error = NetworkError("Test network error")

        # Record error stats
        handler._record_error_stats(error)

        # Verify stats updated
        assert handler.error_stats['total_errors'] == 1
        assert handler.error_stats['errors_by_category']['network'] == 1
        assert handler.error_stats['errors_by_severity']['high'] == 1

    def test_get_error_stats(self):
        """测试获取错误统计"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError, DatabaseError, ErrorSeverity

        handler = ErrorHandler()

        # Record some errors
        network_error = NetworkError("Network error")
        db_error = DatabaseError("Database error")

        handler._record_error_stats(network_error)
        handler._record_error_stats(db_error)

        stats = handler.get_error_stats()

        # Verify stats copy
        assert stats['total_errors'] == 2
        assert stats['errors_by_category']['network'] == 1
        assert stats['errors_by_category']['database'] == 1
        assert stats['errors_by_severity']['high'] == 2

        # Verify it's a copy (modifying shouldn't affect original)
        stats['total_errors'] = 999
        assert handler.error_stats['total_errors'] == 2

    def test_reset_error_stats(self):
        """测试重置错误统计"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError

        handler = ErrorHandler()
        error = NetworkError("Test error")
        handler._record_error_stats(error)

        # Reset stats
        handler.reset_error_stats()

        # Verify stats reset
        assert handler.error_stats['total_errors'] == 0
        assert handler.error_stats['errors_by_category'] == {}
        assert handler.error_stats['errors_by_severity'] == {}


class TestErrorHandlerDecorator:
    """测试错误处理装饰器功能"""

    def test_handle_command_errors_decorator_exists(self):
        """测试命令错误处理装饰器是否存在"""
        from daip_live.cli.utils.error_handler import ErrorHandler

        handler = ErrorHandler()

        # Verify decorator method exists
        assert hasattr(handler, 'handle_command_errors')
        assert callable(handler.handle_command_errors)

    def test_decorator_basic_functionality(self):
        """测试装饰器基本功能"""
        from daip_live.cli.utils.error_handler import ErrorHandler

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="test_command")
        async def test_function():
            return "success"

        # Test successful execution
        result = asyncio.run(test_function())
        assert result == "success"

    def test_decorator_with_cli_error_handling(self):
        """测试装饰器处理CLI错误"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="test_command")
        async def failing_function():
            raise NetworkError("Test network error")

        # Test error handling - should not raise exception
        with pytest.raises(typer.Exit):
            asyncio.run(failing_function())

        # Verify error was recorded
        assert handler.error_stats['total_errors'] == 1
        assert handler.error_stats['errors_by_category']['network'] == 1

    @patch('daip_live.cli.utils.error_handler.typer.Exit')
    def test_decorator_exit_code(self, mock_exit):
        """测试装饰器退出代码"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError

        handler = ErrorHandler()
        mock_exit.side_effect = SystemExit(1)

        @handler.handle_command_errors(command_name="test_command")
        async def failing_function():
            raise NetworkError("Test error")

        # Test that it exits with code 1
        with pytest.raises(SystemExit) as exc_info:
            asyncio.run(failing_function())

        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

    def test_decorator_with_original_exception(self):
        """测试装饰器处理原始异常"""
        from daip_live.cli.utils.error_handler import ErrorHandler

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="test_command")
        async def failing_function():
            raise ValueError("Original error")

        # Should handle generic exceptions
        with pytest.raises(typer.Exit):
            asyncio.run(failing_function())

        # Verify error was recorded
        assert handler.error_stats['total_errors'] == 1

    def test_decorator_reraise_option(self):
        """测试装饰器重新抛出选项"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="test_command", reraise=True)
        async def failing_function():
            raise NetworkError("Test error")

        # With reraise=True, should re-raise the original exception
        with pytest.raises(NetworkError):
            asyncio.run(failing_function())

    def test_decorator_show_traceback_option(self):
        """测试装饰器显示堆栈跟踪选项"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError

        handler = ErrorHandler()

        @handler.handle_command_errors(
            command_name="test_command",
            show_traceback=True,
            reraise=True  # Need to reraise to test traceback
        )
        async def failing_function():
            raise NetworkError("Test error")

        # This test mainly verifies the decorator accepts the parameter
        with pytest.raises(NetworkError):
            asyncio.run(failing_function())


class TestErrorFormatting:
    """测试错误格式化功能"""

    def test_get_suggestion_for_error(self):
        """测试根据错误类型获取建议"""
        from daip_live.cli.utils.error_handler import ErrorHandler, ErrorCategory

        handler = ErrorHandler()

        # Test network error suggestion
        network_suggestion = handler._get_suggestion_for_error(ErrorCategory.NETWORK)
        assert "internet connection" in network_suggestion.lower()

        # Test database error suggestion
        db_suggestion = handler._get_suggestion_for_error(ErrorCategory.DATABASE)
        assert "database" in db_suggestion.lower()

        # Test validation error suggestion
        validation_suggestion = handler._get_suggestion_for_error(ErrorCategory.VALIDATION)
        assert "input" in validation_suggestion.lower()

    def test_get_suggestion_for_unknown_error(self):
        """测试未知错误类型的建议"""
        from daip_live.cli.utils.error_handler import ErrorHandler, ErrorCategory

        handler = ErrorHandler()

        # Test with a valid category that doesn't have specific suggestions
        # We can use a mock approach instead of creating a new enum
        suggestion = handler._get_suggestion_for_error(ErrorCategory.BUSINESS)
        # Business errors might not have specific suggestions
        assert suggestion is None or isinstance(suggestion, str)


class TestAsyncErrorHandling:
    """测试异步错误处理"""

    @pytest.mark.asyncio
    async def test_async_command_success(self):
        """测试异步命令成功执行"""
        from daip_live.cli.utils.error_handler import ErrorHandler

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="async_test")
        async def async_success_function():
            await asyncio.sleep(0.01)  # Simulate async work
            return "async_success"

        result = await async_success_function()
        assert result == "async_success"

    @pytest.mark.asyncio
    async def test_async_command_error(self):
        """测试异步命令错误处理"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="async_test")
        async def async_failing_function():
            await asyncio.sleep(0.01)
            raise NetworkError("Async network error")

        with pytest.raises(typer.Exit):
            await async_failing_function()

        assert handler.error_stats['total_errors'] == 1

    @pytest.mark.asyncio
    async def test_async_command_with_timeout_simulation(self):
        """测试异步命令超时模拟"""
        from daip_live.cli.utils.error_handler import ErrorHandler

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="timeout_test")
        async def timeout_function():
            await asyncio.sleep(0.1)  # Simulate work
            return "completed"

        # Should complete successfully
        result = await timeout_function()
        assert result == "completed"


class TestErrorHandlerIntegration:
    """测试错误处理器集成功能"""

    def test_multiple_command_error_tracking(self):
        """测试多命令错误跟踪"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError, DatabaseError, ValidationError

        handler = ErrorHandler()

        @handler.handle_command_errors(command_name="command1")
        async def cmd1():
            raise NetworkError("Network error in cmd1")

        @handler.handle_command_errors(command_name="command2")
        async def cmd2():
            raise DatabaseError("Database error in cmd2")

        @handler.handle_command_errors(command_name="command3")
        async def cmd3():
            raise ValidationError("Validation error in cmd3")

        # Execute all commands
        for cmd in [cmd1, cmd2, cmd3]:
            with pytest.raises(typer.Exit):
                asyncio.run(cmd())

        # Verify all errors were recorded
        stats = handler.get_error_stats()
        assert stats['total_errors'] == 3
        assert stats['errors_by_category']['network'] == 1
        assert stats['errors_by_category']['database'] == 1
        assert stats['errors_by_category']['validation'] == 1

    def test_error_stats_persistence(self):
        """测试错误统计持久性"""
        from daip_live.cli.utils.error_handler import ErrorHandler, NetworkError

        handler = ErrorHandler()

        # Record some errors
        for i in range(5):
            error = NetworkError(f"Error {i}")
            handler._record_error_stats(error)

        # Get stats and verify
        stats = handler.get_error_stats()
        assert stats['total_errors'] == 5

        # Reset and verify
        handler.reset_error_stats()
        stats_after_reset = handler.get_error_stats()
        assert stats_after_reset['total_errors'] == 0