"""工具执行监控与错误处理系统
提供全面的工具执行监控、性能统计、错误处理和恢复机制
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class ExecutionStatus(Enum):
    """执行状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ToolExecutionRecord:
    """工具执行记录"""

    execution_id: str
    tool_name: str
    arguments: dict[str, Any]
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    context: Optional[dict[str, Any]] = None


@dataclass
class ToolPerformanceStats:
    """工具性能统计"""

    tool_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    success_rate: float = 0.0
    error_types: dict[str, int] = None
    last_execution: Optional[datetime] = None

    def __post_init__(self):
        if self.error_types is None:
            self.error_types = defaultdict(int)


class ToolExecutionMonitor:
    """工具执行监控器

    功能：
    1. 执行时间监控和统计
    2. 错误捕获和分类
    3. 性能指标收集
    4. 自动重试机制
    5. 执行历史记录
    6. 异常恢复策略
    """

    def __init__(self, max_history_size: int = 1000, enable_auto_retry: bool = True):
        self.logger = logging.getLogger(__name__)
        self.max_history_size = max_history_size
        self.enable_auto_retry = enable_auto_retry

        # 执行记录存储
        self.execution_history = deque(maxlen=max_history_size)
        self.performance_stats = {}
        self.active_executions = {}

        # 配置参数
        self.default_timeout = 30.0  # 默认超时时间（秒）
        self.max_retry_count = 3  # 最大重试次数
        self.retry_delay = 1.0  # 重试延迟（秒）

        # 错误处理策略
        self.error_handlers = {
            "timeout": self._handle_timeout_error,
            "connection": self._handle_connection_error,
            "validation": self._handle_validation_error,
            "permission": self._handle_permission_error,
            "resource": self._handle_resource_error,
        }

        # 线程锁
        self._lock = threading.Lock()

    def execute_tool_with_monitoring(
        self,
        tool_name: str,
        tool_function: Callable,
        arguments: dict[str, Any],
        timeout: Optional[float] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """带监控的工具执行

        Args:
        ----
            tool_name: 工具名称
            tool_function: 工具函数
            arguments: 执行参数
            timeout: 超时时间
            context: 执行上下文

        Returns:
        -------
            执行结果

        """
        execution_id = f"{tool_name}_{int(time.time() * 1000)}"
        timeout = timeout or self.default_timeout

        # 创建执行记录
        record = ToolExecutionRecord(
            execution_id=execution_id,
            tool_name=tool_name,
            arguments=arguments.copy(),
            status=ExecutionStatus.PENDING,
            start_time=datetime.now(),
            context=context,
        )

        with self._lock:
            self.active_executions[execution_id] = record

        try:
            return self._execute_with_retry(record, tool_function, timeout)
        finally:
            with self._lock:
                if execution_id in self.active_executions:
                    del self.active_executions[execution_id]
                self.execution_history.append(record)
                self._update_performance_stats(record)

    def _execute_with_retry(
        self,
        record: ToolExecutionRecord,
        tool_function: Callable,
        timeout: float,
    ) -> dict[str, Any]:
        """带重试的执行逻辑"""
        last_error = None

        for attempt in range(self.max_retry_count + 1):
            record.retry_count = attempt
            record.status = ExecutionStatus.RUNNING
            record.start_time = datetime.now()

            try:
                # 执行工具函数
                start_time = time.time()
                result = self._execute_with_timeout(
                    tool_function,
                    record.arguments,
                    timeout,
                )
                end_time = time.time()

                # 记录成功执行
                record.end_time = datetime.now()
                record.duration = end_time - start_time
                record.result = result
                record.status = ExecutionStatus.SUCCESS

                self.logger.info(
                    f"工具 {record.tool_name} 执行成功 (耗时: {record.duration:.3f}s, 重试: {attempt})",
                )

                return {
                    "status": "success",
                    "result": result,
                    "execution_id": record.execution_id,
                    "duration": record.duration,
                    "retry_count": attempt,
                }

            except TimeoutError as e:
                last_error = e
                record.error_type = "timeout"
                record.error = str(e)
                record.status = ExecutionStatus.TIMEOUT
                self.logger.warning(
                    f"工具 {record.tool_name} 执行超时 (尝试 {attempt + 1}/{self.max_retry_count + 1})",
                )

            except Exception as e:
                last_error = e
                error_type = self._classify_error(e)
                record.error_type = error_type
                record.error = str(e)
                record.status = ExecutionStatus.FAILED

                self.logger.error(
                    f"工具 {record.tool_name} 执行失败 (尝试 {attempt + 1}/{self.max_retry_count + 1}): {e}",
                )

                # 检查是否应该重试
                if not self._should_retry(error_type, attempt):
                    break

            # 重试延迟
            if attempt < self.max_retry_count:
                time.sleep(self.retry_delay * (2**attempt))  # 指数退避

        # 所有重试都失败了
        record.end_time = datetime.now()
        record.status = ExecutionStatus.FAILED

        # 尝试错误恢复
        recovery_result = self._attempt_error_recovery(record, last_error)
        if recovery_result:
            return recovery_result

        return {
            "status": "error",
            "error": record.error,
            "error_type": record.error_type,
            "execution_id": record.execution_id,
            "retry_count": record.retry_count,
            "message": f"工具 {record.tool_name} 执行失败: {record.error}",
        }

    def _execute_with_timeout(
        self,
        tool_function: Callable,
        arguments: dict[str, Any],
        timeout: float,
    ) -> Any:
        """带超时的执行"""
        import platform

        # Windows系统不支持SIGALRM，使用线程超时
        if platform.system() == "Windows":
            import queue
            import threading

            result_queue = queue.Queue()
            exception_queue = queue.Queue()

            def target():
                try:
                    result = tool_function(**arguments)
                    result_queue.put(result)
                except Exception as e:
                    exception_queue.put(e)

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout)

            if thread.is_alive():
                # 超时了，但无法强制终止线程
                raise TimeoutError(f"工具执行超时 ({timeout}秒)")

            if not exception_queue.empty():
                raise exception_queue.get()

            if not result_queue.empty():
                return result_queue.get()

            raise RuntimeError("工具执行异常结束")

        else:
            # Unix系统使用信号
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"工具执行超时 ({timeout}秒)")

            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))

            try:
                result = tool_function(**arguments)
                return result
            finally:
                signal.alarm(0)  # 取消超时
                signal.signal(signal.SIGALRM, old_handler)

    def _classify_error(self, error: Exception) -> str:
        """错误分类"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        if "timeout" in error_str or "timeout" in error_type:
            return "timeout"
        elif (
            "connection" in error_str
            or "network" in error_str
            or "connectionerror" in error_type
            or "网络连接" in error_str
        ):
            return "connection"
        elif (
            "permission" in error_str
            or "access" in error_str
            or "forbidden" in error_str
        ):
            return "permission"
        elif (
            "validation" in error_str or "invalid" in error_str or "format" in error_str
        ):
            return "validation"
        elif "memory" in error_str or "resource" in error_str or "limit" in error_str:
            return "resource"
        else:
            return "unknown"

    def _should_retry(self, error_type: str, attempt: int) -> bool:
        """判断是否应该重试"""
        if not self.enable_auto_retry:
            return False

        if attempt >= self.max_retry_count:
            return False

        # 某些错误类型不应该重试
        non_retryable_errors = {"permission", "validation"}
        if error_type in non_retryable_errors:
            return False

        return True

    def _attempt_error_recovery(
        self,
        record: ToolExecutionRecord,
        error: Exception,
    ) -> Optional[dict[str, Any]]:
        """尝试错误恢复"""
        error_type = record.error_type

        if error_type in self.error_handlers:
            try:
                recovery_result = self.error_handlers[error_type](record, error)
                if recovery_result:
                    self.logger.info(f"工具 {record.tool_name} 错误恢复成功")
                    return recovery_result
            except Exception as e:
                self.logger.error(f"错误恢复失败: {e}")

        return None

    def _handle_timeout_error(
        self,
        record: ToolExecutionRecord,
        error: Exception,
    ) -> Optional[dict[str, Any]]:
        """处理超时错误"""
        # 可以尝试使用更简单的参数重新执行
        return None

    def _handle_connection_error(
        self,
        record: ToolExecutionRecord,
        error: Exception,
    ) -> Optional[dict[str, Any]]:
        """处理连接错误"""
        # 可以尝试重新建立连接
        return None

    def _handle_validation_error(
        self,
        record: ToolExecutionRecord,
        error: Exception,
    ) -> Optional[dict[str, Any]]:
        """处理验证错误"""
        # 可以尝试修正参数格式
        return None

    def _handle_permission_error(
        self,
        record: ToolExecutionRecord,
        error: Exception,
    ) -> Optional[dict[str, Any]]:
        """处理权限错误"""
        # 可以尝试使用备用方法
        return None

    def _handle_resource_error(
        self,
        record: ToolExecutionRecord,
        error: Exception,
    ) -> Optional[dict[str, Any]]:
        """处理资源错误"""
        # 可以尝试清理资源后重试
        return None

    def _update_performance_stats(self, record: ToolExecutionRecord):
        """更新性能统计"""
        tool_name = record.tool_name

        if tool_name not in self.performance_stats:
            self.performance_stats[tool_name] = ToolPerformanceStats(
                tool_name=tool_name,
            )

        stats = self.performance_stats[tool_name]
        stats.total_executions += 1
        stats.last_execution = record.end_time or record.start_time

        if record.status == ExecutionStatus.SUCCESS:
            stats.successful_executions += 1
            if record.duration:
                stats.total_duration += record.duration
                stats.min_duration = min(stats.min_duration, record.duration)
                stats.max_duration = max(stats.max_duration, record.duration)
                stats.avg_duration = stats.total_duration / stats.successful_executions
        else:
            stats.failed_executions += 1
            if record.error_type:
                stats.error_types[record.error_type] += 1

        stats.success_rate = stats.successful_executions / stats.total_executions

    def get_performance_report(self, tool_name: Optional[str] = None) -> dict[str, Any]:
        """获取性能报告"""
        if tool_name:
            if tool_name in self.performance_stats:
                return asdict(self.performance_stats[tool_name])
            else:
                return {"error": f"未找到工具 {tool_name} 的统计信息"}

        return {
            "total_tools": len(self.performance_stats),
            "total_executions": sum(
                stats.total_executions for stats in self.performance_stats.values()
            ),
            "overall_success_rate": sum(
                stats.successful_executions for stats in self.performance_stats.values()
            )
            / max(
                sum(
                    stats.total_executions for stats in self.performance_stats.values()
                ),
                1,
            ),
            "tools": {
                name: asdict(stats) for name, stats in self.performance_stats.items()
            },
        }

    def get_recent_executions(
        self,
        limit: int = 10,
        tool_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """获取最近的执行记录"""
        records = list(self.execution_history)

        if tool_name:
            records = [r for r in records if r.tool_name == tool_name]

        # 按时间倒序排列
        records.sort(key=lambda x: x.start_time, reverse=True)

        return [asdict(record) for record in records[:limit]]

    def clear_history(self, older_than_days: int = 7):
        """清理历史记录"""
        cutoff_time = datetime.now() - timedelta(days=older_than_days)

        with self._lock:
            # 过滤掉过期的记录
            filtered_history = deque(maxlen=self.max_history_size)
            for record in self.execution_history:
                if record.start_time > cutoff_time:
                    filtered_history.append(record)

            self.execution_history = filtered_history

        self.logger.info(f"清理了 {older_than_days} 天前的执行记录")

    def export_performance_data(self, filepath: str):
        """导出性能数据"""
        data = {
            "export_time": datetime.now().isoformat(),
            "performance_stats": self.get_performance_report(),
            "recent_executions": self.get_recent_executions(limit=100),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        self.logger.info(f"性能数据已导出到: {filepath}")
