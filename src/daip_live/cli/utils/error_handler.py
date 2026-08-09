"""
统一错误处理器
遵循TDD原则 - 基于测试需求实现
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional

import typer
from rich.console import Console

from .error_types import (
    CLIError,
    DatabaseError,  # noqa: F401  # re-export
    ErrorCategory,
    ErrorSeverity,
    NetworkError,  # noqa: F401  # re-export：调用方/测试依赖本模块导出这些异常
    ValidationError,  # noqa: F401  # re-export
)


class ErrorHandler:
    """统一错误处理器"""

    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
        }

    def handle_command_errors(
        self,
        command_name: Optional[str] = None,
        reraise: bool = False,
        show_traceback: bool = False,
    ):
        """命令错误处理装饰器"""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                cmd_name = command_name or func.__name__
                return await self._handle_error_async(
                    func, args, kwargs, cmd_name, reraise, show_traceback
                )

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                cmd_name = command_name or func.__name__
                return self._handle_error_sync(
                    func, args, kwargs, cmd_name, reraise, show_traceback
                )

            # 根据函数类型返回对应的包装器
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    async def _handle_error_async(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        command_name: str,
        reraise: bool,
        show_traceback: bool,
    ) -> Any:
        """异步错误处理"""
        try:
            return await func(*args, **kwargs)
        except CLIError as e:
            await self._process_cli_error(e, command_name, show_traceback)
            if reraise:
                raise
            raise typer.Exit(1)
        except Exception as e:
            await self._process_unexpected_error(e, command_name, show_traceback)
            if reraise:
                raise
            raise typer.Exit(1)

    def _handle_error_sync(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        command_name: str,
        reraise: bool,
        show_traceback: bool,
    ) -> Any:
        """同步错误处理"""
        try:
            return func(*args, **kwargs)
        except CLIError as e:
            # 对于同步函数，需要在事件循环中处理异步输出
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果已经在事件循环中，创建任务
                    loop.create_task(
                        self._process_cli_error(e, command_name, show_traceback)
                    )
                else:
                    # 如果没有运行的事件循环，运行新的事件循环
                    loop.run_until_complete(
                        self._process_cli_error(e, command_name, show_traceback)
                    )
            except RuntimeError:
                # 如果无法获取事件循环，使用同步处理
                self._process_cli_error_sync(e, command_name, show_traceback)

            if reraise:
                raise
            raise typer.Exit(1)
        except Exception as e:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(
                        self._process_unexpected_error(e, command_name, show_traceback)
                    )
                else:
                    loop.run_until_complete(
                        self._process_unexpected_error(e, command_name, show_traceback)
                    )
            except RuntimeError:
                self._process_unexpected_error_sync(e, command_name, show_traceback)

            if reraise:
                raise
            raise typer.Exit(1)

    async def _process_cli_error(
        self, error: CLIError, command_name: str, show_traceback: bool
    ):
        """处理CLI错误"""
        # 记录错误统计
        self._record_error_stats(error)

        # 日志记录
        self.logger.error(
            f"CLI Error in {command_name}: {error.message}",
            extra={"error_details": error.to_dict(), "command_name": command_name},
        )

        # 用户友好输出
        await self._display_error_to_user(error, show_traceback)

    def _process_cli_error_sync(
        self, error: CLIError, command_name: str, show_traceback: bool
    ):
        """同步处理CLI错误"""
        # 记录错误统计
        self._record_error_stats(error)

        # 日志记录
        self.logger.error(
            f"CLI Error in {command_name}: {error.message}",
            extra={"error_details": error.to_dict(), "command_name": command_name},
        )

        # 用户友好输出
        self._display_error_to_user_sync(error, show_traceback)

    async def _process_unexpected_error(
        self, error: Exception, command_name: str, show_traceback: bool
    ):
        """处理意外错误"""
        # 包装为CLI错误
        cli_error = CLIError(
            message=f"Unexpected error in {command_name}: {str(error)}",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            original_exception=error,
            details={"error_type": type(error).__name__, "command_name": command_name},
        )

        await self._process_cli_error(cli_error, command_name, show_traceback)

    def _process_unexpected_error_sync(
        self, error: Exception, command_name: str, show_traceback: bool
    ):
        """同步处理意外错误"""
        cli_error = CLIError(
            message=f"Unexpected error in {command_name}: {str(error)}",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            original_exception=error,
            details={"error_type": type(error).__name__, "command_name": command_name},
        )

        self._process_cli_error_sync(cli_error, command_name, show_traceback)

    async def _display_error_to_user(self, error: CLIError, show_traceback: bool):
        """向用户显示错误"""
        # 根据严重程度选择显示样式
        severity_styles = {
            "low": "yellow",
            "medium": "orange3",
            "high": "red",
            "critical": "bright_red",
        }

        style = severity_styles.get(error.severity.value, "red")

        # 显示主要错误信息
        self.console.print(f"❌ [{style}]Error:[/{style}] {error.message}")

        # 显示详细信息
        if error.details:
            self.console.print("\n[bold]Details:[/bold]")
            for key, value in error.details.items():
                self.console.print(f"  • {key}: {value}")

        # 显示建议
        suggestion = self._get_suggestion_for_error(error.category)
        if suggestion:
            self.console.print(f"\n💡 [dim]Suggestion:[/dim] {suggestion}")

        # 显示详细跟踪信息（如果启用）
        if show_traceback and error.original_exception:
            self.console.print("\n[dim]Detailed error information:[/dim]")
            import traceback

            traceback_str = "".join(
                traceback.format_exception(
                    type(error.original_exception),
                    error.original_exception,
                    error.original_exception.__traceback__,
                )
            )
            self.console.print(traceback_str, style="dim")

    def _display_error_to_user_sync(self, error: CLIError, show_traceback: bool):
        """同步向用户显示错误"""
        # 根据严重程度选择显示样式
        severity_styles = {
            "low": "yellow",
            "medium": "orange3",
            "high": "red",
            "critical": "bright_red",
        }

        style = severity_styles.get(error.severity.value, "red")

        # 显示主要错误信息
        self.console.print(f"❌ [{style}]Error:[/{style}] {error.message}")

        # 显示详细信息
        if error.details:
            self.console.print("\n[bold]Details:[/bold]")
            for key, value in error.details.items():
                self.console.print(f"  • {key}: {value}")

        # 显示建议
        suggestion = self._get_suggestion_for_error(error.category)
        if suggestion:
            self.console.print(f"\n💡 [dim]Suggestion:[/dim] {suggestion}")

        # 显示详细跟踪信息（如果启用）
        if show_traceback and error.original_exception:
            self.console.print("\n[dim]Detailed error information:[/dim]")
            import traceback

            traceback_str = "".join(
                traceback.format_exception(
                    type(error.original_exception),
                    error.original_exception,
                    error.original_exception.__traceback__,
                )
            )
            self.console.print(traceback_str, style="dim")

    def _get_suggestion_for_error(self, error_category: ErrorCategory) -> Optional[str]:
        """根据错误类型提供建议"""
        suggestions = {
            ErrorCategory.NETWORK: "Please check your internet connection and try again.",  # noqa: E501
            ErrorCategory.DATABASE: "Please check if the database is running and accessible.",  # noqa: E501
            ErrorCategory.VALIDATION: "Please check your input parameters and try again.",  # noqa: E501
            ErrorCategory.USER_INPUT: "Please check the command syntax and required arguments.",  # noqa: E501
        }

        return suggestions.get(error_category)

    def _record_error_stats(self, error: CLIError):
        """记录错误统计"""
        self.error_stats["total_errors"] += 1

        # 按类别统计
        category = error.category.value
        self.error_stats["errors_by_category"][category] = (
            self.error_stats["errors_by_category"].get(category, 0) + 1
        )

        # 按严重程度统计
        severity = error.severity.value
        self.error_stats["errors_by_severity"][severity] = (
            self.error_stats["errors_by_severity"].get(severity, 0) + 1
        )

    def get_error_stats(self) -> dict[str, Any]:
        """获取错误统计信息"""
        return self.error_stats.copy()

    def reset_error_stats(self):
        """重置错误统计"""
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
        }
