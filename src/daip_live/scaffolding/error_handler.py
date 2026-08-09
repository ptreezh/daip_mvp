"""
错误处理器
遵循SOLID原则，提供统一的错误处理、重试和恢复机制
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

from .models import (
    ConfigurationError,
    FileOperationError,
    GenerationError,
    NetworkError,
    TimeoutError,
    ValidationError,
)


class ErrorSeverity(Enum):
    """错误严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __lt__(self, other):
        """支持比较操作"""
        if self.__class__ is other.__class__:
            order = [
                ErrorSeverity.LOW,
                ErrorSeverity.MEDIUM,
                ErrorSeverity.HIGH,
                ErrorSeverity.CRITICAL,
            ]
            return order.index(self) < order.index(other)
        return NotImplemented


class ErrorCategory(Enum):
    """错误类别"""

    VALIDATION = "validation"
    FILE_OPERATION = "file_operation"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    GENERATION = "generation"
    TIMEOUT = "timeout"
    SYSTEM = "system"
    USER_INPUT = "user_input"

    @classmethod
    def from_exception(cls, exception: Exception) -> "ErrorCategory":
        """根据异常类型获取错误类别"""
        exception_type_map = {
            ValidationError: cls.VALIDATION,
            GenerationError: cls.GENERATION,
            FileOperationError: cls.FILE_OPERATION,
            NetworkError: cls.NETWORK,
            TimeoutError: cls.TIMEOUT,
            ConfigurationError: cls.CONFIGURATION,
        }

        for exception_type, category in exception_type_map.items():
            if isinstance(exception, exception_type):
                return category

        # 默认为系统错误
        return cls.SYSTEM


@dataclass
class ErrorContext:
    """错误上下文信息"""

    operation: Optional[str] = None
    component: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_data: Optional[dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "operation": self.operation,
            "component": self.component,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "additional_data": self.additional_data or {},
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ErrorReport:
    """错误报告"""

    error: Exception
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.SYSTEM
    context: Optional[ErrorContext] = None
    message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: Optional[str] = None

    def __post_init__(self):
        """后置处理"""
        if self.category == ErrorCategory.SYSTEM:
            self.category = ErrorCategory.from_exception(self.error)

        if self.message is None:
            self.message = str(self.error)

    @classmethod
    def from_exception(
        cls,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        message: Optional[str] = None,
    ) -> "ErrorReport":
        """从异常创建错误报告"""
        return cls(
            error=error,
            severity=severity,
            category=ErrorCategory.from_exception(error),
            context=context,
            message=message,
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "error_type": type(self.error).__name__,
            "error_message": str(self.error),
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.to_dict() if self.context else None,
            "stack_trace": self.stack_trace,
        }


@dataclass
class RetryStrategy:
    """重试策略"""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True

    def get_delay(self, attempt: int) -> float:
        """计算指定尝试次数的延迟时间"""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        delay = min(delay, self.max_delay)

        if self.jitter:
            # 添加 ±10% 的随机抖动
            jitter_factor = random.uniform(0.9, 1.1)
            delay *= jitter_factor

        return delay

    def should_retry(self, attempt: int) -> bool:
        """判断是否应该重试"""
        return attempt <= self.max_attempts


@dataclass
class RecoveryStrategy:
    """恢复策略"""

    retry_strategy: RetryStrategy = field(default_factory=RetryStrategy)
    fallback_actions: list[str] = field(default_factory=list)
    custom_handler: Optional[Callable] = None


@dataclass
class ErrorRecoveryResult:
    """错误恢复结果"""

    success: bool
    original_error: Exception
    recovery_action: str
    attempts: int
    total_delay: float
    final_result: Optional[Any] = None
    recovery_details: Optional[dict[str, Any]] = None


class ErrorHandler:
    """错误处理器

    遵循单一职责原则，专门负责错误处理、重试和恢复
    提供统一的错误处理接口和策略配置
    """

    def __init__(self, max_history: int = 1000):
        """初始化错误处理器

        Args:
            max_history: 最大错误历史记录数量
        """
        self.max_history = max_history
        self.error_history: list[ErrorReport] = []

        # 默认严重程度映射
        self.severity_mapping: dict[type[Exception], ErrorSeverity] = {
            ValidationError: ErrorSeverity.MEDIUM,
            ConfigurationError: ErrorSeverity.HIGH,
            NetworkError: ErrorSeverity.MEDIUM,
            TimeoutError: ErrorSeverity.HIGH,
            FileOperationError: ErrorSeverity.MEDIUM,
            GenerationError: ErrorSeverity.HIGH,
        }

        # 恢复策略
        self.recovery_strategies: dict[ErrorCategory, RecoveryStrategy] = {}

        # 配置默认恢复策略
        self._configure_default_recovery_strategies()

    def _configure_default_recovery_strategies(self) -> None:
        """配置默认恢复策略"""
        # 网络错误 - 更多的重试次数
        self.recovery_strategies[ErrorCategory.NETWORK] = RecoveryStrategy(
            retry_strategy=RetryStrategy(
                max_attempts=5, base_delay=2.0, backoff_factor=2.0
            ),
            fallback_actions=["use_cache", "offline_mode"],
        )

        # 超时错误 - 中等重试次数
        self.recovery_strategies[ErrorCategory.TIMEOUT] = RecoveryStrategy(
            retry_strategy=RetryStrategy(
                max_attempts=2, base_delay=5.0, backoff_factor=1.5
            ),
            fallback_actions=["increase_timeout", "alternative_endpoint"],
        )

        # 文件操作错误 - 较少重试次数
        self.recovery_strategies[ErrorCategory.FILE_OPERATION] = RecoveryStrategy(
            retry_strategy=RetryStrategy(
                max_attempts=2, base_delay=0.5, backoff_factor=1.0
            ),
            fallback_actions=["use_alternative_location", "skip_file"],
        )

    def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        severity: Optional[ErrorSeverity] = None,
        message: Optional[str] = None,
    ) -> ErrorReport:
        """处理错误并生成报告

        Args:
            error: 发生的错误
            context: 错误上下文
            severity: 错误严重程度，None表示自动判断
            message: 自定义错误消息

        Returns:
            ErrorReport: 错误报告
        """
        # 确定严重程度
        if severity is None:
            severity = self._determine_severity(error)

        # 创建错误报告
        report = ErrorReport(
            error=error,
            severity=severity,
            context=context,
            message=message,
            stack_trace=self._get_stack_trace(error),
        )

        # 添加到历史记录
        self._add_to_history(report)

        return report

    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """自动判断错误严重程度"""
        error_type = type(error)

        # 检查是否有自定义映射
        if error_type in self.severity_mapping:
            return self.severity_mapping[error_type]

        # 检查父类
        for mapped_type, severity in self.severity_mapping.items():
            if issubclass(error_type, mapped_type):
                return severity

        # 默认为中等严重程度
        return ErrorSeverity.MEDIUM

    def _get_stack_trace(self, error: Exception) -> Optional[str]:
        """获取错误堆栈跟踪"""
        try:
            import traceback

            return traceback.format_exc()
        except Exception:
            return None

    def _add_to_history(self, report: ErrorReport) -> None:
        """添加错误报告到历史记录"""
        self.error_history.append(report)

        # 保持历史记录在限制范围内
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history :]

    def configure_severity_mapping(
        self, mapping: dict[type[Exception], ErrorSeverity]
    ) -> None:
        """配置严重程度映射

        Args:
            mapping: 异常类型到严重程度的映射
        """
        self.severity_mapping.update(mapping)

    def configure_recovery_strategy(
        self,
        category: ErrorCategory,
        retry_strategy: Optional[RetryStrategy] = None,
        fallback_actions: Optional[list[str]] = None,
        custom_handler: Optional[Callable] = None,
    ) -> None:
        """配置恢复策略

        Args:
            category: 错误类别
            retry_strategy: 重试策略
            fallback_actions: 回退操作列表
            custom_handler: 自定义处理器
        """
        strategy = RecoveryStrategy(
            retry_strategy=retry_strategy or RetryStrategy(),
            fallback_actions=fallback_actions or [],
            custom_handler=custom_handler,
        )
        self.recovery_strategies[category] = strategy

    def get_recovery_strategy(self, error: Exception) -> RecoveryStrategy:
        """获取错误的恢复策略

        Args:
            error: 错误对象

        Returns:
            RecoveryStrategy: 恢复策略
        """
        category = ErrorCategory.from_exception(error)
        return self.recovery_strategies.get(category, RecoveryStrategy())

    async def retry_with_backoff(
        self,
        func: Callable,
        strategy: Optional[RetryStrategy] = None,
        retry_condition: Optional[Callable[[Exception], bool]] = None,
    ) -> Any:
        """使用指数退避重试函数

        Args:
            func: 要重试的函数（可以是协程函数或普通函数）
            strategy: 重试策略
            retry_condition: 重试条件函数，返回True表示应该重试

        Returns:
            Any: 函数执行结果

        Raises:
            Exception: 重试耗尽后的最后一个异常
        """
        if strategy is None:
            strategy = RetryStrategy()

        last_exception = None
        total_delay = 0.0

        for attempt in range(1, strategy.max_attempts + 1):
            try:
                # 调用函数
                if asyncio.iscoroutinefunction(func):
                    result = await func()
                else:
                    result = func()
                return result

            except Exception as e:
                last_exception = e

                # 检查是否应该重试
                if not strategy.should_retry(attempt):
                    break

                if retry_condition and not retry_condition(e):
                    break

                # 等待重试
                delay = strategy.get_delay(attempt)
                total_delay += delay
                await asyncio.sleep(delay)

        # 重试耗尽，抛出最后一个异常
        raise last_exception

    async def attempt_recovery(
        self, error: Exception, context: Optional[ErrorContext] = None
    ) -> ErrorRecoveryResult:
        """尝试从错误中恢复

        Args:
            error: 发生的错误
            context: 错误上下文

        Returns:
            ErrorRecoveryResult: 恢复结果
        """
        start_time = time.time()
        attempts = 0
        total_delay = 0.0

        try:
            # 获取恢复策略
            strategy = self.get_recovery_strategy(error)

            # 尝试重试
            async def retry_operation():
                nonlocal attempts
                attempts += 1
                raise error  # 重新抛出原始错误进行重试测试

            result = await self.retry_with_backoff(
                retry_operation, strategy.retry_strategy
            )

            total_delay = time.time() - start_time

            return ErrorRecoveryResult(
                success=True,
                original_error=error,
                recovery_action="retry_with_backoff",
                attempts=attempts,
                total_delay=total_delay,
                final_result=result,
            )

        except Exception:
            total_delay = time.time() - start_time

            # 尝试回退操作
            for action in strategy.fallback_actions:
                try:
                    # 这里可以扩展具体的回退操作实现
                    pass
                except Exception:
                    continue

            return ErrorRecoveryResult(
                success=False,
                original_error=error,
                recovery_action="retry_with_backoff",
                attempts=attempts,
                total_delay=total_delay,
                final_result=None,
                recovery_details={"fallback_attempts": len(strategy.fallback_actions)},
            )

    def get_errors_by_severity(self, severity: ErrorSeverity) -> list[ErrorReport]:
        """按严重程度获取错误

        Args:
            severity: 错误严重程度

        Returns:
            List[ErrorReport]: 匹配的错误报告列表
        """
        return [report for report in self.error_history if report.severity == severity]

    def get_errors_by_category(self, category: ErrorCategory) -> list[ErrorReport]:
        """按类别获取错误

        Args:
            category: 错误类别

        Returns:
            List[ErrorReport]: 匹配的错误报告列表
        """
        return [report for report in self.error_history if report.category == category]

    def get_errors_by_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> list[ErrorReport]:
        """按时间范围获取错误

        Args:
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            List[ErrorReport]: 时间范围内的错误报告列表
        """
        return [
            report
            for report in self.error_history
            if start_time <= report.timestamp <= end_time
        ]

    def get_statistics(self) -> dict[str, Any]:
        """获取错误统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.error_history:
            return {
                "total_errors": 0,
                "by_severity": {},
                "by_category": {},
                "recent_errors": [],
                "error_rate_24h": 0.0,
            }

        # 按严重程度统计
        by_severity = {}
        for severity in ErrorSeverity:
            count = len(self.get_errors_by_severity(severity))
            if count > 0:
                by_severity[severity.value] = count

        # 按类别统计
        by_category = {}
        for category in ErrorCategory:
            count = len(self.get_errors_by_category(category))
            if count > 0:
                by_category[category.value] = count

        # 最近24小时的错误率
        now = datetime.now()
        yesterday = now - timedelta(hours=24)
        recent_errors = self.get_errors_by_time_range(yesterday, now)
        error_rate_24h = len(recent_errors) / 24.0  # 每小时错误数

        # 最近的错误
        recent_errors = sorted(
            self.error_history, key=lambda x: x.timestamp, reverse=True
        )[:10]

        return {
            "total_errors": len(self.error_history),
            "by_severity": by_severity,
            "by_category": by_category,
            "recent_errors": [error.to_dict() for error in recent_errors],
            "error_rate_24h": error_rate_24h,
        }

    def clear_history(self) -> None:
        """清除错误历史记录"""
        self.error_history.clear()

    def export_error_logs(self, format: str = "json") -> str:
        """导出错误日志

        Args:
            format: 导出格式 ("json", "csv", "txt")

        Returns:
            str: 格式化的错误日志
        """
        if format.lower() == "json":
            import json

            return json.dumps(
                [report.to_dict() for report in self.error_history],
                indent=2,
                ensure_ascii=False,
            )

        elif format.lower() == "csv":
            import csv
            import io

            output = io.StringIO()
            if self.error_history:
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "timestamp",
                        "severity",
                        "category",
                        "error_type",
                        "error_message",
                    ],
                )
                writer.writeheader()
                for report in self.error_history:
                    writer.writerow(
                        {
                            "timestamp": report.timestamp.isoformat(),
                            "severity": report.severity.value,
                            "category": report.category.value,
                            "error_type": type(report.error).__name__,
                            "error_message": report.message,
                        }
                    )
            return output.getvalue()

        elif format.lower() == "txt":
            lines = []
            for report in self.error_history:
                lines.append(
                    f"[{report.timestamp}] {report.severity.value.upper()} {report.category.value}: {report.message}"  # noqa: E501
                )
                if report.context:
                    lines.append(
                        f"  Context: {report.context.operation} in {report.context.component}"  # noqa: E501
                    )
                lines.append("")
            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")
