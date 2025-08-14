#!/usr/bin/env python3
"""算法注册表 (Algorithm Registry)

提供统一的共识算法管理和注册功能。
负责算法的注册、发现、验证和健康检查。

核心功能：
1. 算法注册和注销
2. 算法发现和查询
3. 算法验证和健康检查
4. 元数据管理和存储
5. 动态配置支持

设计原则：
- 线程安全：支持并发注册和查询
- 动态管理：支持运行时注册和注销
- 健康监控：定期检查算法可用性
- 元数据驱动：基于元数据进行算法管理
"""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from consensus_algorithm_interface import AlgorithmCapabilities, ConsensusAlgorithm
from consensus_models import AlgorithmMetadata, AlgorithmType, ConsensusInput, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class AlgorithmInfo:
    """算法信息"""

    algorithm_id: str
    algorithm: ConsensusAlgorithm
    metadata: AlgorithmMetadata
    capabilities: AlgorithmCapabilities
    registered_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"  # healthy, unhealthy, unknown
    usage_count: int = 0
    last_used: Optional[datetime] = None
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegistryStats:
    """注册表统计信息"""

    total_algorithms: int = 0
    healthy_algorithms: int = 0
    unhealthy_algorithms: int = 0
    unknown_status_algorithms: int = 0
    total_usage_count: int = 0
    last_health_check: Optional[datetime] = None


class AlgorithmRegistry:
    """算法注册表
    
    管理所有可用的共识算法，提供注册、发现、验证和健康检查功能。
    """

    def __init__(self,
                 health_check_interval: int = 300,  # 5分钟
                 max_health_check_workers: int = 5):
        self._algorithms: Dict[str, AlgorithmInfo] = {}
        self._lock = threading.RLock()
        self._health_check_interval = health_check_interval
        self._health_check_executor = ThreadPoolExecutor(max_workers=max_health_check_workers)
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._listeners: List[Callable[[str, str], None]] = []  # (event_type, algorithm_id)

        logger.info("AlgorithmRegistry initialized")

    def register(self,
                 algorithm_id: str,
                 algorithm: ConsensusAlgorithm,
                 metadata: Optional[AlgorithmMetadata] = None,
                 configuration: Optional[Dict[str, Any]] = None) -> bool:
        """注册算法
        
        Args:
            algorithm_id: 算法唯一标识
            algorithm: 算法实例
            metadata: 算法元数据（可选，会从算法获取）
            configuration: 算法配置（可选）
            
        Returns:
            是否注册成功

        """
        try:
            with self._lock:
                # 检查算法ID是否已存在
                if algorithm_id in self._algorithms:
                    logger.warning(f"Algorithm {algorithm_id} already registered, updating...")

                # 验证算法
                validation_result = self.validate_algorithm(algorithm)
                if not validation_result.is_valid:
                    logger.error(f"Algorithm validation failed for {algorithm_id}: {validation_result.errors}")
                    return False

                # 获取元数据和能力
                if metadata is None:
                    metadata = algorithm.get_metadata()
                capabilities = algorithm.get_capabilities()

                # 创建算法信息
                algorithm_info = AlgorithmInfo(
                    algorithm_id=algorithm_id,
                    algorithm=algorithm,
                    metadata=metadata,
                    capabilities=capabilities,
                    configuration=configuration or {}
                )

                # 注册算法
                self._algorithms[algorithm_id] = algorithm_info

                logger.info(f"Algorithm {algorithm_id} registered successfully")

                # 通知监听器
                self._notify_listeners("registered", algorithm_id)

                return True

        except Exception as e:
            logger.error(f"Failed to register algorithm {algorithm_id}: {str(e)}")
            return False

    def unregister(self, algorithm_id: str) -> bool:
        """注销算法
        
        Args:
            algorithm_id: 算法标识
            
        Returns:
            是否注销成功

        """
        try:
            with self._lock:
                if algorithm_id not in self._algorithms:
                    logger.warning(f"Algorithm {algorithm_id} not found for unregistration")
                    return False

                del self._algorithms[algorithm_id]
                logger.info(f"Algorithm {algorithm_id} unregistered successfully")

                # 通知监听器
                self._notify_listeners("unregistered", algorithm_id)

                return True

        except Exception as e:
            logger.error(f"Failed to unregister algorithm {algorithm_id}: {str(e)}")
            return False

    def get_algorithm(self, algorithm_id: str) -> Optional[ConsensusAlgorithm]:
        """获取算法实例
        
        Args:
            algorithm_id: 算法标识
            
        Returns:
            算法实例，如果不存在返回None

        """
        with self._lock:
            algorithm_info = self._algorithms.get(algorithm_id)
            if algorithm_info:
                # 更新使用统计
                algorithm_info.usage_count += 1
                algorithm_info.last_used = datetime.now()
                return algorithm_info.algorithm
            return None

    def get_algorithm_info(self, algorithm_id: str) -> Optional[AlgorithmInfo]:
        """获取算法详细信息
        
        Args:
            algorithm_id: 算法标识
            
        Returns:
            算法信息，如果不存在返回None

        """
        with self._lock:
            return self._algorithms.get(algorithm_id)

    def list_algorithms(self,
                       algorithm_type: Optional[AlgorithmType] = None,
                       health_status: Optional[str] = None) -> List[AlgorithmInfo]:
        """列出所有算法
        
        Args:
            algorithm_type: 过滤算法类型（可选）
            health_status: 过滤健康状态（可选）
            
        Returns:
            算法信息列表

        """
        with self._lock:
            algorithms = list(self._algorithms.values())

            # 按类型过滤
            if algorithm_type:
                algorithms = [
                    algo for algo in algorithms
                    if algo.metadata.algorithm_type == algorithm_type
                ]

            # 按健康状态过滤
            if health_status:
                algorithms = [
                    algo for algo in algorithms
                    if algo.health_status == health_status
                ]

            return algorithms

    def get_algorithm_ids(self) -> List[str]:
        """获取所有算法ID列表
        
        Returns:
            算法ID列表

        """
        with self._lock:
            return list(self._algorithms.keys())

    def validate_algorithm(self, algorithm: ConsensusAlgorithm) -> ValidationResult:
        """验证算法
        
        Args:
            algorithm: 待验证的算法
            
        Returns:
            验证结果

        """
        errors = []
        warnings = []

        try:
            # 检查必需方法
            required_methods = ['calculate', 'get_metadata', 'get_capabilities', 'validate_inputs']
            for method_name in required_methods:
                if not hasattr(algorithm, method_name):
                    errors.append(f"Missing required method: {method_name}")
                elif not callable(getattr(algorithm, method_name)):
                    errors.append(f"Method {method_name} is not callable")

            # 检查元数据
            try:
                metadata = algorithm.get_metadata()
                if not isinstance(metadata, AlgorithmMetadata):
                    errors.append("get_metadata() must return AlgorithmMetadata instance")
            except Exception as e:
                errors.append(f"get_metadata() failed: {str(e)}")

            # 检查能力
            try:
                capabilities = algorithm.get_capabilities()
                if not isinstance(capabilities, AlgorithmCapabilities):
                    errors.append("get_capabilities() must return AlgorithmCapabilities instance")
            except Exception as e:
                errors.append(f"get_capabilities() failed: {str(e)}")

            # 检查输入验证
            try:
                test_inputs = [
                    ConsensusInput(agent_id="test", position="test", confidence=0.5)
                ]
                validation_result = algorithm.validate_inputs(test_inputs)
                if not isinstance(validation_result, ValidationResult):
                    errors.append("validate_inputs() must return ValidationResult instance")
            except Exception as e:
                errors.append(f"validate_inputs() failed: {str(e)}")

        except Exception as e:
            errors.append(f"Algorithm validation failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def find_algorithms_by_capability(self,
                                    input_types: Optional[Set[str]] = None,
                                    min_participants: Optional[int] = None,
                                    max_participants: Optional[int] = None,
                                    requires_reasoning: Optional[bool] = None,
                                    requires_evidence: Optional[bool] = None) -> List[str]:
        """根据能力查找算法
        
        Args:
            input_types: 支持的输入类型
            min_participants: 最小参与者数量
            max_participants: 最大参与者数量
            requires_reasoning: 是否需要推理
            requires_evidence: 是否需要证据
            
        Returns:
            匹配的算法ID列表

        """
        matching_algorithms = []

        with self._lock:
            for algorithm_id, algorithm_info in self._algorithms.items():
                capabilities = algorithm_info.capabilities

                # 检查输入类型
                if input_types and not input_types.issubset(capabilities.supported_input_types):
                    continue

                # 检查参与者数量
                if min_participants and capabilities.min_participants > min_participants:
                    continue
                if max_participants and capabilities.max_participants and capabilities.max_participants < max_participants:
                    continue

                # 检查推理要求
                if requires_reasoning is not None and capabilities.requires_reasoning != requires_reasoning:
                    continue

                # 检查证据要求
                if requires_evidence is not None and capabilities.requires_evidence != requires_evidence:
                    continue

                matching_algorithms.append(algorithm_id)

        return matching_algorithms

    async def check_algorithm_health(self, algorithm_id: str) -> bool:
        """检查单个算法健康状态
        
        Args:
            algorithm_id: 算法标识
            
        Returns:
            是否健康

        """
        try:
            with self._lock:
                algorithm_info = self._algorithms.get(algorithm_id)
                if not algorithm_info:
                    return False

            # 执行健康检查
            algorithm = algorithm_info.algorithm

            # 基本健康检查：调用get_health_status方法
            try:
                health_status = algorithm.get_health_status()
                is_healthy = health_status.get("status") == "healthy"
            except Exception:
                # 如果没有健康检查方法，尝试基本功能测试
                is_healthy = await self._basic_health_check(algorithm)

            # 更新健康状态
            with self._lock:
                if algorithm_id in self._algorithms:
                    self._algorithms[algorithm_id].last_health_check = datetime.now()
                    self._algorithms[algorithm_id].health_status = "healthy" if is_healthy else "unhealthy"

            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for algorithm {algorithm_id}: {str(e)}")

            # 更新为不健康状态
            with self._lock:
                if algorithm_id in self._algorithms:
                    self._algorithms[algorithm_id].last_health_check = datetime.now()
                    self._algorithms[algorithm_id].health_status = "unhealthy"

            return False

    async def _basic_health_check(self, algorithm: ConsensusAlgorithm) -> bool:
        """基本健康检查
        
        Args:
            algorithm: 算法实例
            
        Returns:
            是否健康

        """
        try:
            # 测试基本方法调用
            metadata = algorithm.get_metadata()
            capabilities = algorithm.get_capabilities()

            # 测试输入验证
            test_inputs = [
                ConsensusInput(agent_id="health_check", position="test", confidence=0.5)
            ]
            validation_result = algorithm.validate_inputs(test_inputs)

            return (metadata is not None and
                   capabilities is not None and
                   validation_result is not None)

        except Exception:
            return False

    async def check_all_algorithms_health(self) -> Dict[str, bool]:
        """检查所有算法健康状态
        
        Returns:
            算法ID到健康状态的映射

        """
        algorithm_ids = self.get_algorithm_ids()
        health_results = {}

        # 并发检查所有算法
        tasks = []
        for algorithm_id in algorithm_ids:
            task = asyncio.create_task(self.check_algorithm_health(algorithm_id))
            tasks.append((algorithm_id, task))

        # 等待所有检查完成
        for algorithm_id, task in tasks:
            try:
                health_results[algorithm_id] = await task
            except Exception as e:
                logger.error(f"Health check task failed for {algorithm_id}: {str(e)}")
                health_results[algorithm_id] = False

        return health_results

    def get_healthy_algorithms(self) -> List[str]:
        """获取所有健康的算法ID
        
        Returns:
            健康算法ID列表（包括健康和未知状态的算法）

        """
        return [
            algorithm_id for algorithm_id, algorithm_info in self._algorithms.items()
            if algorithm_info.health_status in ["healthy", "unknown"]
        ]

    def get_registry_stats(self) -> RegistryStats:
        """获取注册表统计信息
        
        Returns:
            统计信息

        """
        with self._lock:
            stats = RegistryStats()
            stats.total_algorithms = len(self._algorithms)
            stats.total_usage_count = sum(info.usage_count for info in self._algorithms.values())

            # 统计健康状态
            for algorithm_info in self._algorithms.values():
                if algorithm_info.health_status == "healthy":
                    stats.healthy_algorithms += 1
                elif algorithm_info.health_status == "unhealthy":
                    stats.unhealthy_algorithms += 1
                else:
                    stats.unknown_status_algorithms += 1

            # 获取最近的健康检查时间
            health_check_times = [
                info.last_health_check for info in self._algorithms.values()
                if info.last_health_check
            ]
            if health_check_times:
                stats.last_health_check = max(health_check_times)

            return stats

    def add_listener(self, listener: Callable[[str, str], None]) -> None:
        """添加事件监听器
        
        Args:
            listener: 监听器函数，接收(event_type, algorithm_id)参数

        """
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[str, str], None]) -> None:
        """移除事件监听器
        
        Args:
            listener: 要移除的监听器函数

        """
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self, event_type: str, algorithm_id: str) -> None:
        """通知所有监听器
        
        Args:
            event_type: 事件类型
            algorithm_id: 算法ID

        """
        for listener in self._listeners:
            try:
                listener(event_type, algorithm_id)
            except Exception as e:
                logger.error(f"Listener notification failed: {str(e)}")

    async def start_health_monitoring(self) -> None:
        """启动健康监控"""
        if self._health_check_task and not self._health_check_task.done():
            logger.warning("Health monitoring already started")
            return

        self._shutdown_event.clear()
        self._health_check_task = asyncio.create_task(self._health_monitor_loop())
        logger.info("Health monitoring started")

    async def stop_health_monitoring(self) -> None:
        """停止健康监控"""
        self._shutdown_event.set()

        if self._health_check_task:
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        logger.info("Health monitoring stopped")

    async def _health_monitor_loop(self) -> None:
        """健康监控循环"""
        while not self._shutdown_event.is_set():
            try:
                await self.check_all_algorithms_health()
                logger.debug("Health check completed for all algorithms")

                # 等待下次检查
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self._health_check_interval
                    )
                except asyncio.TimeoutError:
                    continue  # 超时是正常的，继续下次检查

            except Exception as e:
                logger.error(f"Health monitor loop error: {str(e)}")
                await asyncio.sleep(60)  # 出错时等待1分钟再重试

    def shutdown(self) -> None:
        """关闭注册表"""
        # 停止健康监控
        if self._health_check_task:
            self._health_check_task.cancel()

        # 关闭线程池
        self._health_check_executor.shutdown(wait=True)

        logger.info("AlgorithmRegistry shutdown completed")

    def __len__(self) -> int:
        """返回注册的算法数量"""
        return len(self._algorithms)

    def __contains__(self, algorithm_id: str) -> bool:
        """检查算法是否已注册"""
        return algorithm_id in self._algorithms

    def __iter__(self):
        """迭代所有算法ID"""
        return iter(self._algorithms.keys())
