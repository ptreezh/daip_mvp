"""
增强意图识别系统 - 错误处理与日志记录机制

实现全面的错误处理和详细的日志记录机制
确保系统在出现异常时能优雅降级并提供调试信息
"""

import logging
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional


@dataclass
class ErrorInfo:
    """错误信息数据类"""

    error_type: str
    error_message: str
    timestamp: datetime
    component: str
    session_id: Optional[str] = None
    original_input: Optional[str] = None
    traceback_info: Optional[str] = None


class IntentRecognitionErrorHandler:
    """
    意图识别错误处理器

    提供统一的错误处理机制，包括：
    1. 异常捕获和记录
    2. 优雅降级处理
    3. 错误恢复机制
    4. 错误统计和分析
    """

    def __init__(self, logger_name: str = "intent_recognition"):
        self.logger = logging.getLogger(logger_name)
        self.error_stats = {
            "total_errors": 0,
            "error_types": {},
            "recovery_attempts": 0,
            "successful_recoveries": 0,
        }

    def handle_error(
        self,
        error: Exception,
        component: str,
        session_id: Optional[str] = None,
        original_input: Optional[str] = None,
        fallback_result: Any = None,
    ) -> Any:
        """
        处理错误并返回降级结果

        Args:
            error: 发生的异常
            component: 出错的组件
            session_id: 会话ID
            original_input: 原始输入
            fallback_result: 降级结果

        Returns:
            降级结果或异常
        """
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            error_message=str(error),
            timestamp=datetime.now(),
            component=component,
            session_id=session_id,
            original_input=original_input,
            traceback_info=traceback.format_exc(),
        )

        self._log_error(error_info)
        self._update_error_stats(error_info)

        # 根据错误类型决定是否尝试恢复
        if self._should_attempt_recovery(error_info):
            return self._attempt_recovery(error_info, fallback_result)

        return fallback_result

    def _log_error(self, error_info: ErrorInfo):
        """记录错误信息"""
        error_msg = f"Error in {error_info.component}: {error_info.error_type} - {error_info.error_message}"  # noqa: E501

        if error_info.session_id:
            error_msg += f" (Session: {error_info.session_id})"

        if error_info.original_input:
            error_msg += f" (Input: '{error_info.original_input}')"

        self.logger.error(error_msg)

        # 详细错误信息（包含traceback）
        if error_info.traceback_info:
            self.logger.debug(
                f"Full traceback for {error_info.component} error:\n{error_info.traceback_info}"  # noqa: E501
            )

    def _update_error_stats(self, error_info: ErrorInfo):
        """更新错误统计"""
        self.error_stats["total_errors"] += 1

        # 统计错误类型
        error_type = error_info.error_type
        if error_type not in self.error_stats["error_types"]:
            self.error_stats["error_types"][error_type] = 0
        self.error_stats["error_types"][error_type] += 1

    def _should_attempt_recovery(self, error_info: ErrorInfo) -> bool:
        """判断是否应该尝试恢复"""
        # 某些错误类型不适合自动恢复
        unrecoverable_errors = ["KeyboardInterrupt", "SystemExit", "MemoryError"]
        return error_info.error_type not in unrecoverable_errors

    def _attempt_recovery(self, error_info: ErrorInfo, fallback_result: Any) -> Any:
        """尝试错误恢复"""
        self.error_stats["recovery_attempts"] += 1

        # 这里可以实现特定的恢复逻辑
        # 目前简单地返回降级结果
        self.error_stats["successful_recoveries"] += 1

        recovery_msg = f"Recovered from {error_info.error_type} in {error_info.component}, using fallback"  # noqa: E501
        if error_info.session_id:
            recovery_msg += f" (Session: {error_info.session_id})"

        self.logger.info(recovery_msg)

        return fallback_result

    def get_error_statistics(self) -> dict[str, Any]:
        """获取错误统计信息"""
        return self.error_stats.copy()

    def reset_statistics(self):
        """重置统计信息"""
        self.error_stats = {
            "total_errors": 0,
            "error_types": {},
            "recovery_attempts": 0,
            "successful_recoveries": 0,
        }


def error_handler_decorator(
    error_handler: IntentRecognitionErrorHandler,
    component_name: str,
    fallback_result: Any = None,
):
    """
    错误处理装饰器

    Args:
        error_handler: 错误处理器实例
        component_name: 组件名称
        fallback_result: 降级结果
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 尝试从参数中提取session_id和input
                session_id = kwargs.get("session_id", "unknown")

                # 尝试从第一个参数（通常是self）和其他参数中查找输入
                original_input = "unknown"
                if (
                    args
                    and hasattr(args[0], "__class__")
                    and hasattr(args[0], "__dict__")
                ):
                    # 如果是类方法，可能在其他参数中有输入
                    for arg in args[1:]:
                        if (
                            isinstance(arg, str) and len(arg) < 200
                        ):  # 假设字符串参数是输入
                            original_input = arg
                            break
                elif "user_input" in kwargs:
                    original_input = kwargs["user_input"]

                return error_handler.handle_error(
                    e, component_name, session_id, original_input, fallback_result
                )

        return wrapper

    return decorator


class IntentRecognitionLogger:
    """
    意图识别专用日志记录器

    提供特定于意图识别的详细日志记录功能
    """

    def __init__(
        self, logger_name: str = "intent_recognition", log_level: int = logging.INFO
    ):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)

        # 如果还没有处理器，添加一个
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_intent_recognition_start(self, user_input: str, session_id: str):
        """记录意图识别开始"""
        self.logger.debug(
            f"Starting intent recognition for session {session_id}: '{user_input}'"
        )

    def log_intent_recognition_result(
        self,
        intent_name: str,
        confidence: float,
        session_id: str,
        processing_time: float = None,
    ):
        """记录意图识别结果"""
        time_info = (
            f" (time: {processing_time * 1000:.2f}ms)" if processing_time else ""
        )
        self.logger.debug(
            f"Intent recognition result for session {session_id}: {intent_name} (confidence: {confidence:.3f}){time_info}"  # noqa: E501
        )

    def log_context_info(self, session_id: str, context_summary: str):
        """记录上下文信息"""
        self.logger.debug(f"Context for session {session_id}: {context_summary}")

    def log_performance_warning(
        self, operation: str, duration: float, threshold: float, session_id: str = None
    ):
        """记录性能警告"""
        session_info = f" (session {session_id})" if session_id else ""
        self.logger.warning(
            f"Performance warning: {operation} took {duration * 1000:.2f}ms, exceeding threshold of {threshold * 1000:.2f}ms{session_info}"  # noqa: E501
        )

    def log_cache_operation(self, operation: str, hit_rate: float = None):
        """记录缓存操作"""
        if hit_rate is not None:
            self.logger.debug(f"Cache {operation}, hit rate: {hit_rate:.2%}")
        else:
            self.logger.debug(f"Cache {operation}")

    def log_config_change(self, config_changes: dict[str, Any]):
        """记录配置变更"""
        changes_str = ", ".join([f"{k}: {v}" for k, v in config_changes.items()])
        self.logger.info(f"Configuration changed: {changes_str}")


def setup_intent_recognition_logging(
    log_file: Optional[str] = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    设置意图识别专用日志记录

    Args:
        log_file: 日志文件路径
        console_level: 控制台日志级别
        file_level: 文件日志级别

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger("intent_recognition")
    logger.setLevel(min(console_level, file_level))

    # 避免重复添加处理器
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - IR - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件处理器（如果指定了文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"  # noqa: E501
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# 使用示例和测试函数
def example_usage():
    """错误处理和日志记录使用示例"""

    # 设置日志记录
    setup_intent_recognition_logging()
    logging.getLogger("intent_recognition")

    # 创建错误处理器
    error_handler = IntentRecognitionErrorHandler()

    # 创建日志记录器
    ir_logger = IntentRecognitionLogger()

    # 使用装饰器的示例函数
    @error_handler_decorator(
        error_handler, "example_component", fallback_result="fallback"
    )
    def example_function(session_id: str, user_input: str):
        # 模拟意图识别过程
        ir_logger.log_intent_recognition_start(user_input, session_id)

        # 模拟可能出错的操作
        if "error" in user_input.lower():
            raise ValueError("Simulated error for demonstration")

        # 正常处理
        result = {"intent": "example", "confidence": 0.9}
        ir_logger.log_intent_recognition_result("example", 0.9, session_id)
        return result

    # 测试正常情况
    example_function("session1", "normal input")

    # 测试错误情况
    example_function("session2", "input with error")

    # 显示错误统计


if __name__ == "__main__":
    example_usage()
