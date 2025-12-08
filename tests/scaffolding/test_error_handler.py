"""
测试错误处理器
遵循TDD原则：先写测试，再实现功能
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from daip_live.scaffolding.error_handler import (
    ErrorHandler,
    ErrorSeverity,
    ErrorCategory,
    ErrorContext,
    ErrorReport,
    RetryStrategy,
    ErrorRecoveryResult
)
from daip_live.scaffolding.models import (
    ValidationError,
    GenerationError,
    FileOperationError,
    NetworkError,
    TimeoutError,
    ConfigurationError
)


class TestErrorSeverity:
    """测试错误严重程度"""

    def test_error_severity_values(self):
        """测试错误严重程度枚举值"""
        # TC-1.5.1: 严重程度枚举测试
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_error_severity_comparison(self):
        """测试错误严重程度比较"""
        # TC-1.5.2: 严重程度比较测试
        assert ErrorSeverity.LOW < ErrorSeverity.MEDIUM
        assert ErrorSeverity.MEDIUM < ErrorSeverity.HIGH
        assert ErrorSeverity.HIGH < ErrorSeverity.CRITICAL

    def test_error_severity_ordering(self):
        """测试错误严重程度排序"""
        # TC-1.5.3: 严重程度排序测试
        severities = [ErrorSeverity.HIGH, ErrorSeverity.LOW, ErrorSeverity.CRITICAL, ErrorSeverity.MEDIUM]
        sorted_severities = sorted(severities)

        expected = [ErrorSeverity.LOW, ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
        assert sorted_severities == expected


class TestErrorCategory:
    """测试错误类别"""

    def test_error_category_values(self):
        """测试错误类别枚举值"""
        # TC-1.5.4: 错误类别枚举测试
        assert ErrorCategory.VALIDATION.value == "validation"
        assert ErrorCategory.FILE_OPERATION.value == "file_operation"
        assert ErrorCategory.NETWORK.value == "network"
        assert ErrorCategory.CONFIGURATION.value == "configuration"
        assert ErrorCategory.GENERATION.value == "generation"
        assert ErrorCategory.TIMEOUT.value == "timeout"
        assert ErrorCategory.SYSTEM.value == "system"
        assert ErrorCategory.USER_INPUT.value == "user_input"

    def test_error_category_from_exception(self):
        """测试从异常类型获取错误类别"""
        # TC-1.5.5: 异常类型映射测试
        assert ErrorCategory.from_exception(ValidationError("")) == ErrorCategory.VALIDATION
        assert ErrorCategory.from_exception(GenerationError("")) == ErrorCategory.GENERATION
        assert ErrorCategory.from_exception(FileOperationError("", "")) == ErrorCategory.FILE_OPERATION
        assert ErrorCategory.from_exception(NetworkError("")) == ErrorCategory.NETWORK
        assert ErrorCategory.from_exception(TimeoutError("")) == ErrorCategory.TIMEOUT
        assert ErrorCategory.from_exception(ConfigurationError("")) == ErrorCategory.CONFIGURATION

    def test_error_category_from_unknown_exception(self):
        """测试未知异常类型的处理"""
        # TC-1.5.6: 未知异常测试
        assert ErrorCategory.from_exception(ValueError("")) == ErrorCategory.SYSTEM
        assert ErrorCategory.from_exception(RuntimeError("")) == ErrorCategory.SYSTEM


class TestErrorContext:
    """测试错误上下文"""

    def test_error_context_creation(self):
        """测试错误上下文创建"""
        # TC-1.5.7: 上下文创建测试
        context = ErrorContext(
            operation="test_operation",
            component="test_component",
            user_id="test_user",
            session_id="test_session",
            additional_data={"key": "value"}
        )

        assert context.operation == "test_operation"
        assert context.component == "test_component"
        assert context.user_id == "test_user"
        assert context.session_id == "test_session"
        assert context.additional_data == {"key": "value"}
        assert isinstance(context.timestamp, datetime)

    def test_error_context_to_dict(self):
        """测试错误上下文转换为字典"""
        # TC-1.5.8: 上下文序列化测试
        context = ErrorContext(
            operation="test_op",
            component="test_comp",
            additional_data={"test": "data"}
        )

        context_dict = context.to_dict()

        assert context_dict["operation"] == "test_op"
        assert context_dict["component"] == "test_comp"
        assert context_dict["additional_data"] == {"test": "data"}
        assert "timestamp" in context_dict


class TestErrorReport:
    """测试错误报告"""

    def test_error_report_creation(self):
        """测试错误报告创建"""
        # TC-1.5.9: 错误报告创建测试
        error = ValueError("Test error")
        context = ErrorContext(operation="test", component="test_comp")

        report = ErrorReport(
            error=error,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            context=context,
            message="Custom error message"
        )

        assert report.error == error
        assert report.severity == ErrorSeverity.HIGH
        assert report.category == ErrorCategory.SYSTEM
        assert report.context == context
        assert report.message == "Custom error message"
        assert isinstance(report.timestamp, datetime)

    def test_error_report_auto_categorization(self):
        """测试自动分类错误"""
        # TC-1.5.10: 自动分类测试
        error = ValidationError("Test validation error")
        report = ErrorReport.from_exception(error, ErrorSeverity.MEDIUM)

        assert report.category == ErrorCategory.VALIDATION
        assert report.severity == ErrorSeverity.MEDIUM
        assert report.error == error

    def test_error_report_to_dict(self):
        """测试错误报告转换为字典"""
        # TC-1.5.11: 错误报告序列化测试
        error = ValueError("Test error")
        context = ErrorContext(operation="test", component="test_comp")
        report = ErrorReport(error=error, context=context)

        report_dict = report.to_dict()

        assert report_dict["error_type"] == "ValueError"
        assert report_dict["error_message"] == "Test error"
        assert report_dict["severity"] == "medium"
        assert report_dict["category"] == "system"
        assert "timestamp" in report_dict
        assert "context" in report_dict


class TestRetryStrategy:
    """测试重试策略"""

    def test_retry_strategy_creation(self):
        """测试重试策略创建"""
        # TC-1.5.12: 重试策略创建测试
        strategy = RetryStrategy(
            max_attempts=5,
            base_delay=1.0,
            max_delay=30.0,
            backoff_factor=2.0,
            jitter=True
        )

        assert strategy.max_attempts == 5
        assert strategy.base_delay == 1.0
        assert strategy.max_delay == 30.0
        assert strategy.backoff_factor == 2.0
        assert strategy.jitter == True

    def test_retry_strategy_default_values(self):
        """测试重试策略默认值"""
        # TC-1.5.13: 默认重试策略测试
        strategy = RetryStrategy()

        assert strategy.max_attempts == 3
        assert strategy.base_delay == 1.0
        assert strategy.max_delay == 60.0
        assert strategy.backoff_factor == 2.0
        assert strategy.jitter == True

    def test_retry_strategy_delay_calculation(self):
        """测试延迟时间计算"""
        # TC-1.5.14: 延迟计算测试
        strategy = RetryStrategy(
            base_delay=1.0,
            backoff_factor=2.0,
            max_delay=10.0,
            jitter=False
        )

        # 测试指数退避
        assert strategy.get_delay(1) == 1.0  # 第一次尝试
        assert strategy.get_delay(2) == 2.0  # 第二次尝试
        assert strategy.get_delay(3) == 4.0  # 第三次尝试
        assert strategy.get_delay(4) == 8.0  # 第四次尝试
        assert strategy.get_delay(5) == 10.0  # 超过最大延迟

    def test_retry_strategy_should_retry(self):
        """测试是否应该重试"""
        # TC-1.5.15: 重试条件测试
        strategy = RetryStrategy(max_attempts=3)

        assert strategy.should_retry(1) == True
        assert strategy.should_retry(2) == True
        assert strategy.should_retry(3) == True
        assert strategy.should_retry(4) == False

    def test_retry_strategy_with_jitter(self):
        """测试带抖动的延迟计算"""
        # TC-1.5.16: 抖动延迟测试
        strategy = RetryStrategy(
            base_delay=1.0,
            backoff_factor=2.0,
            jitter=True
        )

        delay1 = strategy.get_delay(1)
        delay2 = strategy.get_delay(1)

        # 由于抖动，两次计算的延迟应该不同
        assert delay1 != delay2
        # 延迟应该在合理范围内
        assert 0.9 <= delay1 <= 1.1  # ±10% 抖动
        assert 0.9 <= delay2 <= 1.1


class TestErrorHandler:
    """测试错误处理器"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.error_handler = ErrorHandler()

    def test_error_handler_creation(self):
        """测试错误处理器创建"""
        # TC-1.5.17: 错误处理器创建测试
        handler = ErrorHandler(max_history=100)

        assert handler.max_history == 100
        assert len(handler.error_history) == 0

    def test_error_handler_handle_error(self):
        """测试处理错误"""
        # TC-1.5.18: 错误处理测试
        error = ValueError("Test error")
        context = ErrorContext(operation="test", component="test_comp")

        report = self.error_handler.handle_error(
            error=error,
            context=context,
            severity=ErrorSeverity.MEDIUM
        )

        assert report.error == error
        assert report.severity == ErrorSeverity.MEDIUM
        assert report.context == context
        assert len(self.error_handler.error_history) == 1

    def test_error_handler_auto_categorization(self):
        """测试自动错误分类"""
        # TC-1.5.19: 自动分类测试
        error = ValidationError("Test validation error")

        report = self.error_handler.handle_error(error)

        assert report.category == ErrorCategory.VALIDATION

    def test_error_handler_custom_severity_mapping(self):
        """测试自定义严重程度映射"""
        # TC-1.5.20: 自定义严重程度测试
        # 配置自定义映射
        self.error_handler.configure_severity_mapping({
            ValueError: ErrorSeverity.LOW,
            RuntimeError: ErrorSeverity.HIGH
        })

        error1 = ValueError("Low error")
        error2 = RuntimeError("High error")

        report1 = self.error_handler.handle_error(error1)
        report2 = self.error_handler.handle_error(error2)

        assert report1.severity == ErrorSeverity.LOW
        assert report2.severity == ErrorSeverity.HIGH

    def test_error_handler_history_limit(self):
        """测试错误历史限制"""
        # TC-1.5.21: 历史限制测试
        handler = ErrorHandler(max_history=3)

        # 添加超过限制的错误
        for i in range(5):
            handler.handle_error(ValueError(f"Error {i}"))

        assert len(handler.error_history) == 3
        # 应该保留最近的3个错误
        assert handler.error_history[0].error.args[0] == "Error 2"
        assert handler.error_history[2].error.args[0] == "Error 4"

    def test_error_handler_get_errors_by_severity(self):
        """测试按严重程度获取错误"""
        # TC-1.5.22: 按严重程度过滤测试
        # 添加不同严重程度的错误
        self.error_handler.handle_error(ValueError("Low error"), severity=ErrorSeverity.LOW)
        self.error_handler.handle_error(ValueError("High error"), severity=ErrorSeverity.HIGH)
        self.error_handler.handle_error(ValueError("Medium error"), severity=ErrorSeverity.MEDIUM)

        high_errors = self.error_handler.get_errors_by_severity(ErrorSeverity.HIGH)
        medium_errors = self.error_handler.get_errors_by_severity(ErrorSeverity.MEDIUM)
        low_errors = self.error_handler.get_errors_by_severity(ErrorSeverity.LOW)

        assert len(high_errors) == 1
        assert len(medium_errors) == 1
        assert len(low_errors) == 1
        assert high_errors[0].error.args[0] == "High error"

    def test_error_handler_get_errors_by_category(self):
        """测试按类别获取错误"""
        # TC-1.5.23: 按类别过滤测试
        # 添加不同类别的错误
        self.error_handler.handle_error(ValidationError("Validation error"))
        self.error_handler.handle_error(FileOperationError("File error", ""))
        self.error_handler.handle_error(NetworkError("Network error"))

        validation_errors = self.error_handler.get_errors_by_category(ErrorCategory.VALIDATION)
        file_errors = self.error_handler.get_errors_by_category(ErrorCategory.FILE_OPERATION)
        network_errors = self.error_handler.get_errors_by_category(ErrorCategory.NETWORK)

        assert len(validation_errors) == 1
        assert len(file_errors) == 1
        assert len(network_errors) == 1

    def test_error_handler_clear_history(self):
        """测试清除错误历史"""
        # TC-1.5.24: 清除历史测试
        # 添加一些错误
        self.error_handler.handle_error(ValueError("Error 1"))
        self.error_handler.handle_error(ValueError("Error 2"))

        assert len(self.error_handler.error_history) == 2

        # 清除历史
        self.error_handler.clear_history()

        assert len(self.error_handler.error_history) == 0

    def test_error_handler_statistics(self):
        """测试错误统计"""
        # TC-1.5.25: 错误统计测试
        # 添加不同类型和严重程度的错误
        self.error_handler.handle_error(ValidationError("Error 1"), severity=ErrorSeverity.LOW)
        self.error_handler.handle_error(ValidationError("Error 2"), severity=ErrorSeverity.HIGH)
        self.error_handler.handle_error(FileOperationError("Error 3", ""))

        stats = self.error_handler.get_statistics()

        assert stats["total_errors"] == 3
        assert stats["by_severity"][ErrorSeverity.LOW.value] == 1
        assert stats["by_severity"][ErrorSeverity.HIGH.value] == 1
        assert stats["by_category"][ErrorCategory.VALIDATION.value] == 2
        assert stats["by_category"][ErrorCategory.FILE_OPERATION.value] == 1

    @pytest.mark.asyncio
    async def test_error_handler_retry_success(self):
        """测试重试成功"""
        # TC-1.5.26: 重试成功测试
        call_count = 0

        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await self.error_handler.retry_with_backoff(
            failing_function,
            RetryStrategy(max_attempts=3)
        )

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_error_handler_retry_failure(self):
        """测试重试最终失败"""
        # TC-1.5.27: 重试失败测试
        call_count = 0

        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError) as exc_info:
            await self.error_handler.retry_with_backoff(
                always_failing_function,
                RetryStrategy(max_attempts=3)
            )

        assert call_count == 3
        assert str(exc_info.value) == "Always fails"

    @pytest.mark.asyncio
    async def test_error_handler_retry_with_custom_strategy(self):
        """测试自定义重试策略"""
        # TC-1.5.28: 自定义重试策略测试
        call_count = 0
        delays = []

        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        # Mock asyncio.sleep to capture delays
        original_sleep = asyncio.sleep
        async def mock_sleep(delay):
            delays.append(delay)
            await original_sleep(0.01)  # 使用很短的延迟

        strategy = RetryStrategy(
            max_attempts=3,
            base_delay=0.1,
            backoff_factor=2.0,
            jitter=False
        )

        with patch('asyncio.sleep', side_effect=mock_sleep):
            result = await self.error_handler.retry_with_backoff(
                failing_function,
                strategy
            )

        assert result == "success"
        assert len(delays) == 2  # 重试两次
        assert delays[0] == 0.1
        assert delays[1] == 0.2

    @pytest.mark.asyncio
    async def test_error_handler_retry_with_condition(self):
        """测试条件重试"""
        # TC-1.5.29: 条件重试测试
        call_count = 0

        async def sometimes_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Retry this")
            raise RuntimeError("Don't retry this")

        # 只重试 ValueError
        def should_retry(exception):
            return isinstance(exception, ValueError)

        with pytest.raises(RuntimeError):
            await self.error_handler.retry_with_backoff(
                sometimes_failing_function,
                RetryStrategy(max_attempts=3),
                retry_condition=should_retry
            )

        assert call_count == 2  # 重试一次然后失败

    def test_error_recovery_result_creation(self):
        """测试错误恢复结果创建"""
        # TC-1.5.30: 恢复结果测试
        result = ErrorRecoveryResult(
            success=True,
            original_error=ValueError("Test error"),
            recovery_action="retry_with_backoff",
            attempts=3,
            total_delay=5.0,
            final_result="success"
        )

        assert result.success == True
        assert isinstance(result.original_error, ValueError)
        assert result.recovery_action == "retry_with_backoff"
        assert result.attempts == 3
        assert result.total_delay == 5.0
        assert result.final_result == "success"

    def test_error_handler_recovery_strategies(self):
        """测试错误恢复策略"""
        # TC-1.5.31: 恢复策略测试
        # 配置恢复策略
        self.error_handler.configure_recovery_strategy(
            ErrorCategory.NETWORK,
            retry_strategy=RetryStrategy(max_attempts=5),
            fallback_actions=["use_cache", "offline_mode"]
        )

        # 验证策略已配置
        network_strategy = self.error_handler.recovery_strategies[ErrorCategory.NETWORK]
        assert network_strategy.retry_strategy.max_attempts == 5
        assert "use_cache" in network_strategy.fallback_actions
        assert "offline_mode" in network_strategy.fallback_actions

    def test_error_handler_get_recovery_strategy(self):
        """测试获取恢复策略"""
        # TC-1.5.32: 获取恢复策略测试
        # 为网络错误配置策略
        self.error_handler.configure_recovery_strategy(
            ErrorCategory.NETWORK,
            retry_strategy=RetryStrategy(max_attempts=5)
        )

        # 获取网络错误的策略
        network_error = NetworkError("Connection failed")
        strategy = self.error_handler.get_recovery_strategy(network_error)

        assert strategy is not None
        assert strategy.retry_strategy.max_attempts == 5

        # 获取未配置策略的错误
        unknown_error = ValueError("Unknown error")
        strategy = self.error_handler.get_recovery_strategy(unknown_error)

        # 应该返回默认策略
        assert strategy is not None
        assert strategy.retry_strategy.max_attempts == 3


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])