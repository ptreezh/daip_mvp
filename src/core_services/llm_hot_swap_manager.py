#!/usr/bin/env python3
"""@Time    : 2025-08-03 17:00:00
@Author  : DAIP-LIVE Team
@File    : llm_hot_swap_manager.py
@Description:
    LLM热插拔管理器
    
    核心特性：
    - 无缝LLM切换，不影响虚拟专家记忆和历史上下文
    - 状态迁移和兼容性处理
    - 性能监控和自动回退
    - 多LLM并行支持和负载均衡
    - 上下文格式适配和转换
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from src.core_services.integrated_llm_manager import IntegratedLLMManager, RoleContext
from src.core_services.memory_agent import MemAgent
from src.core_services.role_manager import RoleManager
from src.kernel.llm_interface import LLMConfig, LLMInterface

logger = logging.getLogger(__name__)

class LLMStatus(Enum):
    """LLM状态"""
    ACTIVE = "active"
    STANDBY = "standby"
    SWITCHING = "switching"
    FAILED = "failed"
    TESTING = "testing"

class SwapStrategy(Enum):
    """切换策略"""
    IMMEDIATE = "immediate"      # 立即切换
    GRACEFUL = "graceful"       # 优雅切换
    GRADUAL = "gradual"         # 渐进切换
    ROLLBACK = "rollback"       # 回滚切换

@dataclass
class LLMInstance:
    """LLM实例"""
    instance_id: str
    config: LLMConfig
    interface: LLMInterface
    status: LLMStatus = LLMStatus.STANDBY
    performance_metrics: dict[str, float] = field(default_factory=dict)
    error_count: int = 0
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    active_contexts: dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextMigrationRecord:
    """上下文迁移记录"""
    migration_id: str
    source_llm: str
    target_llm: str
    role_contexts: list[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    migration_data: dict[str, Any] = field(default_factory=dict)
    rollback_data: Optional[dict[str, Any]] = None

@dataclass
class SwapConfiguration:
    """切换配置"""
    strategy: SwapStrategy = SwapStrategy.GRACEFUL
    timeout_seconds: int = 300
    preserve_history: bool = True
    preserve_memory: bool = True
    preserve_role_state: bool = True
    validation_required: bool = True
    auto_rollback: bool = True
    parallel_validation: bool = False

class LLMHotSwapManager:
    """LLM热插拔管理器"""
    
    def __init__(self, 
                 mem_agent: MemAgent,
                 role_manager: RoleManager,
                 integrated_llm_manager: IntegratedLLMManager):
        
        # 核心组件
        self.mem_agent = mem_agent
        self.role_manager = role_manager
        self.integrated_llm_manager = integrated_llm_manager
        
        # LLM实例管理
        self.llm_instances: dict[str, LLMInstance] = {}
        self.active_llm_id: Optional[str] = None
        self.standby_llm_ids: list[str] = []
        
        # 上下文保持
        self.role_contexts: dict[str, RoleContext] = {}
        self.context_snapshots: dict[str, dict[str, Any]] = {}
        
        # 迁移管理
        self.migration_records: list[ContextMigrationRecord] = []
        self.active_migrations: dict[str, ContextMigrationRecord] = {}
        
        # 性能监控
        self.performance_tracker = LLMPerformanceTracker()
        
        # 兼容性适配器
        self.compatibility_adapters: dict[str, "LLMCompatibilityAdapter"] = {}
        
        # 配置
        self.swap_config = SwapConfiguration()
        
        # 初始化
        self._initialize_hot_swap_system()
    
    def _initialize_hot_swap_system(self):
        """初始化热插拔系统"""
        # 启动后台监控任务
        asyncio.create_task(self._health_monitoring_loop())
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._context_backup_loop())
        
        # 注册兼容性适配器
        self._register_compatibility_adapters()
        
        logger.info("LLM热插拔管理器初始化完成")
    
    async def register_llm(self, 
                          config: LLMConfig,
                          instance_id: Optional[str] = None,
                          set_as_active: bool = False) -> str:
        """注册LLM实例"""
        if instance_id is None:
            instance_id = f"llm_{config.provider}_{config.model}_{uuid.uuid4().hex[:8]}"
        
        try:
            # 创建LLM接口
            from src.kernel.llm_interface import LLMFactory
            interface = LLMFactory.create_llm(config)
            
            # 创建LLM实例
            instance = LLMInstance(
                instance_id=instance_id,
                config=config,
                interface=interface,
                status=LLMStatus.TESTING
            )
            
            # 健康检查
            health_check = await self._perform_health_check(instance)
            if not health_check["healthy"]:
                raise Exception(f"LLM健康检查失败: {health_check['error']}")
            
            # 兼容性测试
            compatibility = await self._test_compatibility(instance)
            if not compatibility["compatible"]:
                logger.warning(f"LLM兼容性问题: {compatibility['issues']}")
            
            # 注册实例
            instance.status = LLMStatus.STANDBY
            self.llm_instances[instance_id] = instance
            self.standby_llm_ids.append(instance_id)
            
            # 如果没有活跃LLM或设置为活跃，则激活
            if self.active_llm_id is None or set_as_active:
                await self.set_active_llm(instance_id)
            
            logger.info(f"LLM实例注册成功: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"LLM实例注册失败: {e}")
            raise
    
    async def hot_swap_llm(self, 
                          target_llm_id: str,
                          strategy: SwapStrategy = SwapStrategy.GRACEFUL,
                          config: Optional[SwapConfiguration] = None) -> dict[str, Any]:
        """热插拔LLM"""
        if config:
            self.swap_config = config
        
        # 验证目标LLM
        if target_llm_id not in self.llm_instances:
            raise ValueError(f"目标LLM不存在: {target_llm_id}")
        
        source_llm_id = self.active_llm_id
        target_instance = self.llm_instances[target_llm_id]
        
        # 创建迁移记录
        migration_id = str(uuid.uuid4())
        migration_record = ContextMigrationRecord(
            migration_id=migration_id,
            source_llm=source_llm_id or "none",
            target_llm=target_llm_id,
            role_contexts=list(self.role_contexts.keys()),
            start_time=datetime.now()
        )
        
        self.active_migrations[migration_id] = migration_record
        
        try:
            # 1. 预迁移验证
            await self._pre_migration_validation(target_instance, migration_record)
            
            # 2. 备份当前状态
            backup_data = await self._backup_current_state(source_llm_id, migration_record)
            migration_record.rollback_data = backup_data
            
            # 3. 根据策略执行切换
            if strategy == SwapStrategy.IMMEDIATE:
                swap_result = await self._immediate_swap(target_llm_id, migration_record)
            elif strategy == SwapStrategy.GRACEFUL:
                swap_result = await self._graceful_swap(target_llm_id, migration_record)
            elif strategy == SwapStrategy.GRADUAL:
                swap_result = await self._gradual_swap(target_llm_id, migration_record)
            else:
                raise ValueError(f"不支持的切换策略: {strategy}")
            
            # 4. 迁移上下文和状态
            migration_result = await self._migrate_contexts_and_state(
                source_llm_id, target_llm_id, migration_record
            )
            
            # 5. 验证迁移结果
            validation_result = await self._validate_migration(target_llm_id, migration_record)
            
            if validation_result["valid"]:
                # 6. 提交切换
                await self._commit_swap(target_llm_id, migration_record)
                migration_record.success = True
                
                result = {
                    "success": True,
                    "migration_id": migration_id,
                    "source_llm": source_llm_id,
                    "target_llm": target_llm_id,
                    "strategy": strategy.value,
                    "contexts_migrated": len(migration_record.role_contexts),
                    "migration_time": (datetime.now() - migration_record.start_time).total_seconds(),
                    "validation_passed": True
                }
            else:
                # 验证失败，执行回滚
                if self.swap_config.auto_rollback:
                    await self._rollback_swap(migration_record)
                    result = {
                        "success": False,
                        "migration_id": migration_id,
                        "error": "迁移验证失败，已回滚",
                        "validation_errors": validation_result["errors"],
                        "rollback_performed": True
                    }
                else:
                    raise Exception(f"迁移验证失败: {validation_result['errors']}")
            
        except Exception as e:
            logger.error(f"热插拔失败: {e}")
            
            # 自动回滚
            if self.swap_config.auto_rollback and migration_record.rollback_data:
                try:
                    await self._rollback_swap(migration_record)
                    result = {
                        "success": False,
                        "migration_id": migration_id,
                        "error": str(e),
                        "rollback_performed": True
                    }
                except Exception as rollback_error:
                    logger.error(f"回滚失败: {rollback_error}")
                    result = {
                        "success": False,
                        "migration_id": migration_id,
                        "error": str(e),
                        "rollback_error": str(rollback_error),
                        "system_state": "inconsistent"
                    }
            else:
                result = {
                    "success": False,
                    "migration_id": migration_id,
                    "error": str(e),
                    "rollback_performed": False
                }
        
        finally:
            # 清理迁移记录
            migration_record.end_time = datetime.now()
            self.migration_records.append(migration_record)
            self.active_migrations.pop(migration_id, None)
        
        return result
    
    async def _migrate_contexts_and_state(self, 
                                         source_llm_id: Optional[str],
                                         target_llm_id: str, 
                                         migration_record: ContextMigrationRecord) -> dict[str, Any]:
        """迁移上下文和状态"""
        target_instance = self.llm_instances[target_llm_id]
        
        # 1. 迁移角色上下文
        role_migration_results = {}
        for role_id, role_context in self.role_contexts.items():
            try:
                # 适配上下文格式
                adapted_context = await self._adapt_context_format(
                    role_context, target_instance.config
                )
                
                # 迁移对话历史
                migrated_history = await self._migrate_conversation_history(
                    role_context.conversation_history, target_instance
                )
                
                # 迁移记忆上下文
                migrated_memory = await self._migrate_memory_context(
                    role_context.memory_context, target_instance
                )
                
                # 更新角色上下文
                role_context.conversation_history = migrated_history
                role_context.memory_context = migrated_memory
                
                role_migration_results[role_id] = {
                    "success": True,
                    "history_items": len(migrated_history),
                    "memory_items": len(migrated_memory)
                }
                
            except Exception as e:
                logger.error(f"角色 {role_id} 上下文迁移失败: {e}")
                role_migration_results[role_id] = {
                    "success": False,
                    "error": str(e)
                }
        
        # 2. 迁移全局状态
        global_state_migration = await self._migrate_global_state(
            source_llm_id, target_llm_id
        )
        
        # 3. 更新集成LLM管理器
        await self._update_integrated_llm_manager(target_instance)
        
        migration_result = {
            "role_migrations": role_migration_results,
            "global_state_migration": global_state_migration,
            "successful_roles": len([r for r in role_migration_results.values() if r["success"]]),
            "failed_roles": len([r for r in role_migration_results.values() if not r["success"]])
        }
        
        migration_record.migration_data = migration_result
        return migration_result
    
    async def _adapt_context_format(self, 
                                   role_context: RoleContext,
                                   target_config: LLMConfig) -> RoleContext:
        """适配上下文格式"""
        # 获取目标LLM的兼容性适配器
        adapter_key = f"{target_config.provider}_{target_config.model}"
        adapter = self.compatibility_adapters.get(adapter_key)
        
        if adapter:
            # 使用适配器转换格式
            adapted_context = await adapter.adapt_role_context(role_context, target_config)
        else:
            # 使用默认适配逻辑
            adapted_context = await self._default_context_adaptation(role_context, target_config)
        
        return adapted_context
    
    async def _migrate_conversation_history(self, 
                                           history: list[dict[str, Any]],
                                           target_instance: LLMInstance) -> list[dict[str, Any]]:
        """迁移对话历史"""
        migrated_history = []
        
        for message in history:
            try:
                # 转换消息格式
                adapted_message = await self._adapt_message_format(
                    message, target_instance.config
                )
                
                # 验证消息兼容性
                if await self._validate_message_compatibility(adapted_message, target_instance):
                    migrated_history.append(adapted_message)
                else:
                    logger.warning(f"消息格式不兼容，跳过: {message.get('id', 'unknown')}")
                    
            except Exception as e:
                logger.error(f"消息迁移失败: {e}")
                continue
        
        return migrated_history
    
    async def _migrate_memory_context(self, 
                                     memory_context: dict[str, Any],
                                     target_instance: LLMInstance) -> dict[str, Any]:
        """迁移记忆上下文"""
        migrated_memory = {}
        
        for key, value in memory_context.items():
            try:
                # 检查记忆项是否需要格式转换
                if await self._memory_needs_adaptation(key, value, target_instance.config):
                    adapted_value = await self._adapt_memory_value(key, value, target_instance.config)
                    migrated_memory[key] = adapted_value
                else:
                    migrated_memory[key] = value
                    
            except Exception as e:
                logger.error(f"记忆项 {key} 迁移失败: {e}")
                continue
        
        return migrated_memory
    
    async def preserve_virtual_expert_continuity(self, 
                                                migration_id: str,
                                                role_id: str) -> dict[str, Any]:
        """保持虚拟专家连续性"""
        migration_record = self.active_migrations.get(migration_id)
        if not migration_record:
            return {"error": "迁移记录不存在"}
        
        role_context = self.role_contexts.get(role_id)
        if not role_context:
            return {"error": "角色上下文不存在"}
        
        # 1. 创建专家状态快照
        expert_snapshot = await self._create_expert_snapshot(role_context)
        
        # 2. 保存专家记忆到持久存储
        memory_preservation = await self._preserve_expert_memory(role_id, expert_snapshot)
        
        # 3. 维护专家个性特征
        personality_preservation = await self._preserve_expert_personality(role_id, expert_snapshot)
        
        # 4. 保持交互历史完整性
        history_integrity = await self._maintain_interaction_history_integrity(role_id)
        
        # 5. 确保角色定义一致性
        role_consistency = await self._ensure_role_definition_consistency(role_id)
        
        return {
            "role_id": role_id,
            "expert_snapshot": expert_snapshot,
            "memory_preservation": memory_preservation,
            "personality_preservation": personality_preservation,
            "history_integrity": history_integrity,
            "role_consistency": role_consistency,
            "continuity_score": self._calculate_continuity_score(
                memory_preservation, personality_preservation, history_integrity, role_consistency
            )
        }
    
    async def _create_expert_snapshot(self, role_context: RoleContext) -> dict[str, Any]:
        """创建专家快照"""
        return {
            "role_id": role_context.role_id,
            "role_name": role_context.role_name,
            "role_definition": role_context.role_definition.copy(),
            "conversation_summary": await self._summarize_conversation_history(
                role_context.conversation_history
            ),
            "key_memories": await self._extract_key_memories(role_context.memory_context),
            "interaction_patterns": await self._analyze_interaction_patterns(role_context),
            "expertise_domains": await self._extract_expertise_domains(role_context),
            "communication_style": await self._analyze_communication_style(role_context),
            "current_task_context": role_context.current_task,
            "performance_metrics": {
                "interaction_count": role_context.interaction_count,
                "last_interaction": role_context.last_interaction.isoformat() if role_context.last_interaction else None
            },
            "snapshot_timestamp": datetime.now().isoformat()
        }
    
    async def get_swap_status(self) -> dict[str, Any]:
        """获取切换状态"""
        return {
            "active_llm": self.active_llm_id,
            "available_llms": list(self.llm_instances.keys()),
            "standby_llms": self.standby_llm_ids,
            "active_migrations": len(self.active_migrations),
            "migration_history": len(self.migration_records),
            "llm_health": {
                llm_id: {
                    "status": instance.status.value,
                    "error_count": instance.error_count,
                    "last_used": instance.last_used.isoformat() if instance.last_used else None,
                    "performance": instance.performance_metrics
                }
                for llm_id, instance in self.llm_instances.items()
            },
            "context_preservation": {
                "role_contexts": len(self.role_contexts),
                "context_snapshots": len(self.context_snapshots),
                "memory_consistency": await self._check_memory_consistency()
            }
        }
    
    async def _health_monitoring_loop(self):
        """健康监控循环"""
        while True:
            try:
                for llm_id, instance in self.llm_instances.items():
                    health = await self._perform_health_check(instance)
                    if not health["healthy"]:
                        await self._handle_llm_failure(llm_id, health["error"])
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"健康监控循环错误: {e}")
                await asyncio.sleep(300)
    
    async def _performance_monitoring_loop(self):
        """性能监控循环"""
        while True:
            try:
                await self.performance_tracker.collect_metrics(self.llm_instances)
                await self.performance_tracker.analyze_performance()
                await asyncio.sleep(300)  # 每5分钟收集一次
                
            except Exception as e:
                logger.error(f"性能监控循环错误: {e}")
                await asyncio.sleep(600)
    
    def _calculate_continuity_score(self, 
                                   memory_preservation: dict[str, Any],
                                   personality_preservation: dict[str, Any],
                                   history_integrity: dict[str, Any],
                                   role_consistency: dict[str, Any]) -> float:
        """计算连续性评分"""
        memory_score = memory_preservation.get("preservation_rate", 0)
        personality_score = personality_preservation.get("consistency_score", 0)
        history_score = history_integrity.get("integrity_score", 0)
        role_score = role_consistency.get("consistency_score", 0)
        
        # 加权平均
        continuity_score = (
            memory_score * 0.3 +
            personality_score * 0.25 +
            history_score * 0.25 +
            role_score * 0.2
        )
        
        return continuity_score

class LLMCompatibilityAdapter(ABC):
    """LLM兼容性适配器抽象基类"""
    
    @abstractmethod
    async def adapt_role_context(self, 
                               role_context: RoleContext,
                               target_config: LLMConfig) -> RoleContext:
        """适配角色上下文"""
        pass
    
    @abstractmethod
    async def adapt_message_format(self, 
                                 message: dict[str, Any],
                                 target_config: LLMConfig) -> dict[str, Any]:
        """适配消息格式"""
        pass

class LLMPerformanceTracker:
    """LLM性能追踪器"""
    
    def __init__(self):
        self.metrics_history = {}
        self.performance_trends = {}
    
    async def collect_metrics(self, llm_instances: dict[str, LLMInstance]):
        """收集性能指标"""
        for llm_id, instance in llm_instances.items():
            if llm_id not in self.metrics_history:
                self.metrics_history[llm_id] = []
            
            # 收集当前指标
            current_metrics = {
                "timestamp": datetime.now().isoformat(),
                "response_time": instance.performance_metrics.get("avg_response_time", 0),
                "error_rate": instance.error_count,
                "active_contexts": len(instance.active_contexts),
                "status": instance.status.value
            }
            
            self.metrics_history[llm_id].append(current_metrics)
            
            # 保持历史记录大小
            if len(self.metrics_history[llm_id]) > 1440:  # 24小时的分钟数
                self.metrics_history[llm_id] = self.metrics_history[llm_id][-720:]  # 保留12小时
    
    async def analyze_performance(self):
        """分析性能趋势"""
        for llm_id, history in self.metrics_history.items():
            if len(history) < 2:
                continue
            
            # 计算趋势
            recent_metrics = history[-10:]  # 最近10个数据点
            
            avg_response_time = sum(m["response_time"] for m in recent_metrics) / len(recent_metrics)
            error_trend = sum(m["error_rate"] for m in recent_metrics[-5:]) - sum(m["error_rate"] for m in recent_metrics[:5])
            
            self.performance_trends[llm_id] = {
                "avg_response_time": avg_response_time,
                "error_trend": error_trend,
                "stability_score": self._calculate_stability_score(recent_metrics)
            }
    
    def _calculate_stability_score(self, metrics: list[dict[str, Any]]) -> float:
        """计算稳定性评分"""
        if len(metrics) < 2:
            return 1.0
        
        response_times = [m["response_time"] for m in metrics]
        variance = sum((x - sum(response_times)/len(response_times))**2 for x in response_times) / len(response_times)
        
        # 方差越小，稳定性越高
        stability_score = max(0, 1 - (variance / 1000))  # 假设1秒的方差对应0分
        return stability_score

# 创建全局实例函数
def create_llm_hot_swap_manager(mem_agent: MemAgent, 
                               role_manager: RoleManager,
                               integrated_llm_manager: IntegratedLLMManager) -> LLMHotSwapManager:
    """创建LLM热插拔管理器实例"""
    return LLMHotSwapManager(mem_agent, role_manager, integrated_llm_manager)