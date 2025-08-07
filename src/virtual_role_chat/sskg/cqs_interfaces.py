#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 18:00:00
@Author  : DAIP-LIVE Team
@File    : cqs_interfaces.py
@Description:
    SSKG CQS (Command Query Separation) 接口定义
    
    严格实现CQS原则：
    - Query: 无副作用的读操作，专注高性能
    - Command: 有副作用的写操作，专注一致性
    - 完全分离的接口设计，避免混合操作
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# 类型变量定义
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class QueryResultStatus(Enum):
    """查询结果状态"""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ERROR = "error"
    TIMEOUT = "timeout"

class CommandResultStatus(Enum):
    """命令执行状态"""
    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"

@dataclass
class QueryResult(Generic[T]):
    """查询结果封装"""
    status: QueryResultStatus
    data: Optional[T] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommandResult:
    """命令执行结果封装"""
    status: CommandResultStatus
    command_id: str
    affected_entities: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    transaction_id: Optional[str] = None
    events_generated: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuerySpec:
    """查询规范"""
    query_id: str
    query_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    pagination: Optional[Dict[str, Any]] = None
    sort_criteria: Optional[List[Dict[str, str]]] = None
    include_metadata: bool = False
    cache_policy: str = "default"  # none, default, aggressive

@dataclass
class CommandSpec:
    """命令规范"""
    command_id: str
    command_type: str
    target_entity_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    expected_version: Optional[int] = None  # 乐观锁版本
    transaction_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)
    timeout_ms: int = 5000

# ============= Query Interfaces (查询接口) =============

class IQueryHandler(ABC, Generic[T]):
    """查询处理器接口 - 所有查询操作必须无副作用"""
    
    @abstractmethod
    async def handle_query(self, query_spec: QuerySpec) -> QueryResult[T]:
        """
        处理查询请求
        
        重要约束：
        1. 绝对不能有任何副作用
        2. 不能修改任何状态
        3. 可以使用缓存优化性能
        4. 必须是幂等的
        """
        pass
    
    @abstractmethod
    def can_handle(self, query_type: str) -> bool:
        """检查是否能处理指定类型的查询"""
        pass

class IReadOnlyRepository(ABC, Generic[K, V]):
    """只读仓储接口 - 专注于高性能读取"""
    
    @abstractmethod
    async def get_by_id(self, entity_id: K) -> QueryResult[V]:
        """根据ID获取实体"""
        pass
    
    @abstractmethod
    async def get_by_criteria(self, criteria: Dict[str, Any]) -> QueryResult[List[V]]:
        """根据条件查询实体列表"""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: K) -> QueryResult[bool]:
        """检查实体是否存在"""
        pass
    
    @abstractmethod
    async def count(self, criteria: Dict[str, Any]) -> QueryResult[int]:
        """统计符合条件的实体数量"""
        pass
    
    @abstractmethod
    async def get_related(self, entity_id: K, relation_type: str) -> QueryResult[List[V]]:
        """获取相关实体"""
        pass

class IQueryCache(ABC):
    """查询缓存接口"""
    
    @abstractmethod
    async def get(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        pass
    
    @abstractmethod
    async def set(self, cache_key: str, value: Any, ttl_seconds: int = 3600):
        """设置缓存数据"""
        pass
    
    @abstractmethod
    async def invalidate(self, cache_key: str):
        """使缓存失效"""
        pass
    
    @abstractmethod
    async def invalidate_pattern(self, pattern: str):
        """根据模式批量使缓存失效"""
        pass

class IQueryOptimizer(ABC):
    """查询优化器接口"""
    
    @abstractmethod
    async def optimize_query(self, query_spec: QuerySpec) -> QuerySpec:
        """优化查询规范"""
        pass
    
    @abstractmethod
    async def suggest_indexes(self, query_patterns: List[QuerySpec]) -> List[str]:
        """建议索引策略"""
        pass
    
    @abstractmethod
    async def analyze_performance(self, query_spec: QuerySpec) -> Dict[str, Any]:
        """分析查询性能"""
        pass

# ============= Command Interfaces (命令接口) =============

class ICommandHandler(ABC):
    """命令处理器接口 - 所有命令操作专注于数据一致性"""
    
    @abstractmethod
    async def handle_command(self, command_spec: CommandSpec) -> CommandResult:
        """
        处理命令请求
        
        重要约束：
        1. 必须保证事务性
        2. 必须进行业务验证
        3. 必须处理并发冲突
        4. 必须支持回滚
        """
        pass
    
    @abstractmethod
    def can_handle(self, command_type: str) -> bool:
        """检查是否能处理指定类型的命令"""
        pass
    
    @abstractmethod
    async def validate_command(self, command_spec: CommandSpec) -> List[str]:
        """验证命令的有效性，返回错误列表"""
        pass

class IWriteOnlyRepository(ABC, Generic[K, V]):
    """只写仓储接口 - 专注于数据一致性保证"""
    
    @abstractmethod
    async def create(self, entity: V) -> CommandResult:
        """创建新实体"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: K, updates: Dict[str, Any], expected_version: Optional[int] = None) -> CommandResult:
        """更新实体（支持乐观锁）"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: K, expected_version: Optional[int] = None) -> CommandResult:
        """删除实体"""
        pass
    
    @abstractmethod
    async def batch_operations(self, operations: List[Dict[str, Any]]) -> CommandResult:
        """批量操作"""
        pass

class ITransactionManager(ABC):
    """事务管理器接口"""
    
    @abstractmethod
    async def begin_transaction(self, isolation_level: str = "READ_COMMITTED") -> str:
        """开始事务，返回事务ID"""
        pass
    
    @abstractmethod
    async def commit_transaction(self, transaction_id: str) -> CommandResult:
        """提交事务"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self, transaction_id: str) -> CommandResult:
        """回滚事务"""
        pass
    
    @abstractmethod
    async def get_transaction_status(self, transaction_id: str) -> str:
        """获取事务状态"""
        pass

class IEventPublisher(ABC):
    """事件发布器接口"""
    
    @abstractmethod
    async def publish_event(self, event_type: str, event_data: Dict[str, Any], transaction_id: Optional[str] = None):
        """发布事件"""
        pass
    
    @abstractmethod
    async def publish_batch_events(self, events: List[Dict[str, Any]], transaction_id: Optional[str] = None):
        """批量发布事件"""
        pass

class IConflictDetector(ABC):
    """冲突检测器接口"""
    
    @abstractmethod
    async def detect_conflicts(self, command_spec: CommandSpec) -> List[str]:
        """检测潜在冲突"""
        pass
    
    @abstractmethod
    async def resolve_conflict(self, conflict_type: str, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """解决冲突"""
        pass

# ============= CQS Orchestration Interfaces (CQS编排接口) =============

class ICQSBus(ABC):
    """CQS总线接口 - 统一的查询和命令调度"""
    
    @abstractmethod
    async def execute_query(self, query_spec: QuerySpec) -> QueryResult[Any]:
        """执行查询"""
        pass
    
    @abstractmethod
    async def execute_command(self, command_spec: CommandSpec) -> CommandResult:
        """执行命令"""
        pass
    
    @abstractmethod
    def register_query_handler(self, query_type: str, handler: IQueryHandler):
        """注册查询处理器"""
        pass
    
    @abstractmethod
    def register_command_handler(self, command_type: str, handler: ICommandHandler):
        """注册命令处理器"""
        pass

class IProjectionManager(ABC):
    """投影管理器接口 - 管理查询端的数据投影"""
    
    @abstractmethod
    async def create_projection(self, projection_name: str, source_events: List[str]):
        """创建投影"""
        pass
    
    @abstractmethod
    async def update_projection(self, projection_name: str, event_data: Dict[str, Any]):
        """更新投影"""
        pass
    
    @abstractmethod
    async def rebuild_projection(self, projection_name: str):
        """重建投影"""
        pass
    
    @abstractmethod
    async def get_projection_status(self, projection_name: str) -> Dict[str, Any]:
        """获取投影状态"""
        pass

# ============= Monitoring and Diagnostics (监控和诊断) =============

class ICQSMetrics(ABC):
    """CQS指标接口"""
    
    @abstractmethod
    async def record_query_execution(self, query_type: str, execution_time_ms: float, cache_hit: bool):
        """记录查询执行指标"""
        pass
    
    @abstractmethod
    async def record_command_execution(self, command_type: str, execution_time_ms: float, success: bool):
        """记录命令执行指标"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        pass
    
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        pass

# ============= CQS Validation (CQS验证) =============

class CQSViolationError(Exception):
    """CQS原则违反错误"""
    pass

class CQSValidator:
    """CQS原则验证器"""
    
    @staticmethod
    def validate_query_handler(handler: IQueryHandler):
        """验证查询处理器是否符合CQS原则"""
        # 这里可以添加静态分析或运行时检查
        # 确保查询处理器没有副作用
        pass
    
    @staticmethod
    def validate_command_handler(handler: ICommandHandler):
        """验证命令处理器是否符合CQS原则"""
        # 这里可以添加事务性和一致性检查
        pass
    
    @staticmethod
    def validate_cqs_compliance(operation_type: str, has_side_effects: bool):
        """验证操作是否符合CQS原则"""
        if operation_type == "query" and has_side_effects:
            raise CQSViolationError("查询操作不能有副作用")
        
        if operation_type == "command" and not has_side_effects:
            logger.warning("命令操作通常应该有副作用")

# ============= 工厂接口 =============

class ICQSFactory(ABC):
    """CQS工厂接口"""
    
    @abstractmethod
    def create_query_handler(self, query_type: str) -> IQueryHandler:
        """创建查询处理器"""
        pass
    
    @abstractmethod
    def create_command_handler(self, command_type: str) -> ICommandHandler:
        """创建命令处理器"""
        pass
    
    @abstractmethod
    def create_cqs_bus(self) -> ICQSBus:
        """创建CQS总线"""
        pass
    
    @abstractmethod
    def create_transaction_manager(self) -> ITransactionManager:
        """创建事务管理器"""
        pass

# ============= 配置接口 =============

@dataclass
class CQSConfiguration:
    """CQS配置"""
    query_cache_enabled: bool = True
    query_cache_ttl_seconds: int = 3600
    command_timeout_ms: int = 30000
    transaction_isolation_level: str = "READ_COMMITTED"
    max_concurrent_queries: int = 100
    max_concurrent_commands: int = 50
    enable_query_optimization: bool = True
    enable_conflict_detection: bool = True
    enable_metrics: bool = True
    projection_update_mode: str = "async"  # sync, async, eventual

class ICQSConfigurationProvider(ABC):
    """CQS配置提供器接口"""
    
    @abstractmethod
    def get_configuration(self) -> CQSConfiguration:
        """获取CQS配置"""
        pass
    
    @abstractmethod
    def update_configuration(self, config: CQSConfiguration):
        """更新CQS配置"""
        pass