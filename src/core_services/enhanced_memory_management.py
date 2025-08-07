#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 16:30:00
@Author  : DAIP-LIVE Team
@File    : enhanced_memory_management.py
@Description:
    V0.3.3 记忆管理系统深度集成
    
    基于现有MemAgent进行深度集成和优化：
    - 用户偏好学习的准确性和适应性提升
    - 长对话的上下文保持和智能截断机制
    - 跨会话连贯性：用户重新进入系统时的记忆恢复和连接
    - 个性化引擎：基于用户行为的个性化推荐和适配
    - 隐私保护：用户数据的本地存储和隐私保护机制
"""

import asyncio
import logging
import json
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# 延迟加载的机器学习库
_numpy = None
_sklearn_kmeans = None
_sklearn_tfidf = None
_sklearn_cosine = None

def _get_numpy():
    global _numpy
    if _numpy is None:
        try:
            import numpy as np
            _numpy = np
        except ImportError:
            raise ImportError("numpy is required for memory management")
    return _numpy

def _get_sklearn_kmeans():
    global _sklearn_kmeans
    if _sklearn_kmeans is None:
        try:
            from sklearn.cluster import KMeans
            _sklearn_kmeans = KMeans
        except ImportError:
            raise ImportError("sklearn.cluster is required for memory management")
    return _sklearn_kmeans

def _get_sklearn_tfidf():
    global _sklearn_tfidf
    if _sklearn_tfidf is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            _sklearn_tfidf = TfidfVectorizer
        except ImportError:
            raise ImportError("sklearn.feature_extraction.text is required for memory management")
    return _sklearn_tfidf

def _get_sklearn_cosine():
    global _sklearn_cosine
    if _sklearn_cosine is None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            _sklearn_cosine = cosine_similarity
        except ImportError:
            raise ImportError("sklearn.metrics.pairwise is required for memory management")
    return _sklearn_cosine

# 导入现有组件
from src.core_services.memory_agent import MemAgent, Memory, MemoryType
from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager

logger = logging.getLogger(__name__)

class LearningSignal(Enum):
    """学习信号类型"""
    POSITIVE_FEEDBACK = "positive_feedback"
    NEGATIVE_FEEDBACK = "negative_feedback"
    PREFERENCE_CHANGE = "preference_change"
    BEHAVIOR_PATTERN = "behavior_pattern"
    CONTEXT_SWITCH = "context_switch"
    SESSION_END = "session_end"

class PersonalizationLevel(Enum):
    """个性化级别"""
    BASIC = "basic"         # 基础个性化
    ADAPTIVE = "adaptive"   # 自适应个性化
    PREDICTIVE = "predictive"  # 预测性个性化
    PROACTIVE = "proactive"    # 主动性个性化

@dataclass
class UserBehaviorPattern:
    """用户行为模式"""
    user_id: str
    session_patterns: Dict[str, Any] = field(default_factory=dict)
    preference_patterns: Dict[str, Any] = field(default_factory=dict)
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    temporal_patterns: Dict[str, Any] = field(default_factory=dict)
    context_patterns: Dict[str, Any] = field(default_factory=dict)
    learning_velocity: float = 0.5
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ContextWindow:
    """上下文窗口"""
    window_id: str
    content: List[Dict[str, Any]]
    start_time: datetime
    end_time: Optional[datetime] = None
    importance_score: float = 0.0
    summary: Optional[str] = None
    key_entities: List[str] = field(default_factory=list)
    emotions: Dict[str, float] = field(default_factory=dict)
    compressed: bool = False

@dataclass
class PersonalizationProfile:
    """个性化档案"""
    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    learned_patterns: Dict[str, Any] = field(default_factory=dict)
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    personalization_level: PersonalizationLevel = PersonalizationLevel.BASIC
    trust_score: float = 0.5
    privacy_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class EnhancedMemoryManager:
    """增强的记忆管理器"""
    
    def __init__(self, 
                 mem_agent: MemAgent,
                 sskg_manager: EnhancedSSKGManager,
                 max_context_length: int = 8000,
                 learning_rate: float = 0.1):
        
        # 核心组件
        self.mem_agent = mem_agent
        self.sskg_manager = sskg_manager
        
        # 配置参数
        self.max_context_length = max_context_length
        self.learning_rate = learning_rate
        
        # 用户行为分析
        self.user_patterns: Dict[str, UserBehaviorPattern] = {}
        self.personalization_profiles: Dict[str, PersonalizationProfile] = {}
        
        # 上下文管理
        self.context_windows: Dict[str, List[ContextWindow]] = {}
        self.active_contexts: Dict[str, str] = {}  # user_id -> active_window_id
        
        # 学习系统
        self.learning_signals: List[Tuple[str, LearningSignal, Dict[str, Any]]] = []
        self.adaptation_engine = AdaptationEngine(self)
        
        # 隐私保护
        self.privacy_manager = PrivacyManager()
        
        # 性能监控
        self.performance_metrics = {
            "context_compression_ratio": [],
            "retrieval_accuracy": [],
            "adaptation_speed": [],
            "user_satisfaction": []
        }
        
        # 初始化
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化组件"""
        # 启动后台任务
        asyncio.create_task(self._background_learning_loop())
        asyncio.create_task(self._context_maintenance_loop())
        asyncio.create_task(self._personalization_update_loop())
        
        logger.info("增强记忆管理器初始化完成")
    
    async def _background_learning_loop(self):
        """后台学习循环"""
        while True:
            try:
                await self._process_learning_signals()
                await self._update_user_patterns()
                await self._optimize_memory_organization()
                await asyncio.sleep(60)  # 每分钟执行一次
            except Exception as e:
                logger.error(f"后台学习循环错误: {e}")
                await asyncio.sleep(300)  # 出错时延长等待
    
    async def _context_maintenance_loop(self):
        """上下文维护循环"""
        while True:
            try:
                await self._compress_old_contexts()
                await self._cleanup_inactive_contexts()
                await self._update_context_importance()
                await asyncio.sleep(300)  # 每5分钟执行一次
            except Exception as e:
                logger.error(f"上下文维护循环错误: {e}")
                await asyncio.sleep(600)
    
    async def _personalization_update_loop(self):
        """个性化更新循环"""
        while True:
            try:
                await self._update_personalization_profiles()
                await self._generate_proactive_recommendations()
                await self._evaluate_adaptation_effectiveness()
                await asyncio.sleep(1800)  # 每30分钟执行一次
            except Exception as e:
                logger.error(f"个性化更新循环错误: {e}")
                await asyncio.sleep(3600)
    
    async def enhanced_memory_store(self, 
                                   user_id: str,
                                   content: str,
                                   memory_type: MemoryType = MemoryType.EPISODIC,
                                   context: Optional[Dict[str, Any]] = None,
                                   importance_hints: Optional[List[str]] = None) -> str:
        """增强的记忆存储"""
        
        # 1. 计算动态重要性
        importance = await self._calculate_dynamic_importance(
            user_id, content, memory_type, context, importance_hints
        )
        
        # 2. 提取上下文信息
        extracted_context = await self._extract_context_information(content, context)
        
        # 3. 个性化处理
        personalized_content = await self._personalize_memory_content(
            user_id, content, extracted_context
        )
        
        # 4. 创建增强记忆
        memory = Memory(
            id=str(uuid.uuid4()),
            content=personalized_content,
            memory_type=memory_type,
            source_id=user_id,
            importance=importance,
            recency=1.0,
            metadata={
                **extracted_context,
                "original_content": content,
                "personalization_applied": True,
                "context_window": self.active_contexts.get(user_id)
            }
        )
        
        # 5. 存储到MemAgent
        await self.mem_agent.store_memory(memory)
        
        # 6. 更新上下文窗口
        await self._update_context_window(user_id, content, memory.id)
        
        # 7. 触发学习信号
        await self._emit_learning_signal(
            user_id, 
            LearningSignal.BEHAVIOR_PATTERN,
            {"action": "memory_store", "memory_type": memory_type.value, "importance": importance}
        )
        
        logger.info(f"增强记忆存储完成: {memory.id}")
        return memory.id
    
    async def intelligent_memory_retrieve(self,
                                         user_id: str,
                                         query: str,
                                         max_memories: int = 10,
                                         context_aware: bool = True,
                                         personalized: bool = True) -> List[Memory]:
        """智能记忆检索"""
        
        # 1. 分析查询意图
        query_analysis = await self._analyze_query_intent(user_id, query)
        
        # 2. 构建个性化查询
        if personalized:
            enhanced_query = await self._enhance_query_with_personalization(
                user_id, query, query_analysis
            )
        else:
            enhanced_query = query
        
        # 3. 基础记忆检索
        base_memories = await self.mem_agent.retrieve_memories(
            enhanced_query, max_memories * 2
        )
        
        # 4. 上下文感知过滤
        if context_aware:
            context_filtered = await self._apply_context_filtering(
                user_id, base_memories, query_analysis
            )
        else:
            context_filtered = base_memories
        
        # 5. 个性化重排序
        if personalized:
            reranked_memories = await self._personalized_rerank(
                user_id, context_filtered, query_analysis
            )
        else:
            reranked_memories = context_filtered
        
        # 6. 应用多样性和新颖性
        final_memories = await self._apply_diversity_and_novelty(
            reranked_memories, max_memories
        )
        
        # 7. 更新访问记录
        for memory in final_memories:
            memory.last_accessed = datetime.now()
            memory.access_count += 1
        
        # 8. 记录检索行为
        await self._record_retrieval_behavior(user_id, query, final_memories)
        
        logger.info(f"智能记忆检索完成: 返回 {len(final_memories)} 条记忆")
        return final_memories
    
    async def adaptive_context_management(self, 
                                         user_id: str,
                                         new_content: str,
                                         force_compression: bool = False) -> Dict[str, Any]:
        """自适应上下文管理"""
        
        # 1. 获取当前上下文窗口
        current_window = await self._get_current_context_window(user_id)
        
        # 2. 检查是否需要压缩
        needs_compression = (
            force_compression or
            self._calculate_context_length(current_window) > self.max_context_length or
            await self._should_start_new_context(user_id, new_content, current_window)
        )
        
        if needs_compression:
            # 3. 智能压缩当前上下文
            compression_result = await self._intelligent_context_compression(
                user_id, current_window
            )
            
            # 4. 创建新的上下文窗口
            new_window = await self._create_new_context_window(user_id, new_content)
            
            result = {
                "action": "compression_and_new_window",
                "compressed_window": compression_result,
                "new_window": new_window,
                "compression_ratio": compression_result.get("compression_ratio", 0),
                "preserved_entities": compression_result.get("key_entities", [])
            }
        else:
            # 5. 扩展当前上下文
            await self._extend_current_context(current_window, new_content)
            
            result = {
                "action": "context_extension",
                "window_id": current_window.window_id,
                "current_length": self._calculate_context_length(current_window),
                "utilization": self._calculate_context_length(current_window) / self.max_context_length
            }
        
        # 6. 更新性能指标
        self._update_context_metrics(result)
        
        return result
    
    async def cross_session_continuity(self, user_id: str) -> Dict[str, Any]:
        """跨会话连贯性管理"""
        
        # 1. 检索用户历史会话
        historical_sessions = await self._retrieve_historical_sessions(user_id)
        
        # 2. 分析会话间的连贯性
        continuity_analysis = await self._analyze_session_continuity(
            user_id, historical_sessions
        )
        
        # 3. 识别未完成的对话线程
        unfinished_threads = await self._identify_unfinished_threads(
            historical_sessions
        )
        
        # 4. 提取跨会话的上下文
        cross_session_context = await self._extract_cross_session_context(
            user_id, historical_sessions
        )
        
        # 5. 生成会话恢复建议
        recovery_suggestions = await self._generate_session_recovery_suggestions(
            user_id, unfinished_threads, cross_session_context
        )
        
        # 6. 创建连贯性记忆
        continuity_memory = await self._create_continuity_memory(
            user_id, cross_session_context, recovery_suggestions
        )
        
        return {
            "continuity_score": continuity_analysis.get("score", 0),
            "unfinished_threads": unfinished_threads,
            "cross_session_context": cross_session_context,
            "recovery_suggestions": recovery_suggestions,
            "continuity_memory_id": continuity_memory,
            "session_connection_strength": continuity_analysis.get("connection_strength", 0)
        }
    
    async def personalized_recommendation_engine(self, user_id: str) -> Dict[str, Any]:
        """个性化推荐引擎"""
        
        # 1. 获取用户个性化档案
        profile = await self._get_personalization_profile(user_id)
        
        # 2. 分析当前会话状态
        session_state = await self._analyze_current_session_state(user_id)
        
        # 3. 预测用户需求
        predicted_needs = await self._predict_user_needs(user_id, profile, session_state)
        
        # 4. 生成个性化建议
        recommendations = await self._generate_personalized_recommendations(
            user_id, predicted_needs, profile
        )
        
        # 5. 计算推荐置信度
        confidence_scores = await self._calculate_recommendation_confidence(
            recommendations, profile
        )
        
        # 6. 应用多样性和新颖性过滤
        final_recommendations = await self._apply_recommendation_filters(
            recommendations, confidence_scores
        )
        
        return {
            "recommendations": final_recommendations,
            "confidence_scores": confidence_scores,
            "predicted_needs": predicted_needs,
            "personalization_level": profile.personalization_level.value,
            "adaptation_suggestions": await self._get_adaptation_suggestions(user_id)
        }
    
    async def privacy_aware_processing(self, 
                                      user_id: str,
                                      data: Dict[str, Any],
                                      operation: str) -> Dict[str, Any]:
        """隐私感知处理"""
        
        # 1. 检查隐私设置
        privacy_settings = await self._get_user_privacy_settings(user_id)
        
        # 2. 数据脱敏处理
        anonymized_data = await self.privacy_manager.anonymize_data(
            data, privacy_settings
        )
        
        # 3. 本地化处理
        if privacy_settings.get("local_only", False):
            processing_result = await self._local_processing(
                anonymized_data, operation
            )
        else:
            processing_result = await self._standard_processing(
                anonymized_data, operation
            )
        
        # 4. 应用数据保留策略
        await self._apply_data_retention_policy(user_id, processing_result)
        
        # 5. 记录隐私审计日志
        await self._log_privacy_audit(user_id, operation, privacy_settings)
        
        return {
            "result": processing_result,
            "privacy_level": privacy_settings.get("level", "standard"),
            "data_anonymized": True,
            "local_processing": privacy_settings.get("local_only", False)
        }
    
    # ===== 内部辅助方法 =====
    
    async def _calculate_dynamic_importance(self, 
                                           user_id: str,
                                           content: str,
                                           memory_type: MemoryType,
                                           context: Optional[Dict[str, Any]],
                                           hints: Optional[List[str]]) -> float:
        """计算动态重要性"""
        base_importance = 0.5
        
        # 基于内容长度
        length_factor = min(len(content) / 1000, 1.0) * 0.2
        
        # 基于记忆类型
        type_factors = {
            MemoryType.EPISODIC: 0.3,
            MemoryType.SEMANTIC: 0.4,
            MemoryType.PROCEDURAL: 0.3,
            MemoryType.META: 0.2
        }
        type_factor = type_factors.get(memory_type, 0.3)
        
        # 基于用户个性化
        user_factor = await self._get_user_importance_bias(user_id, content)
        
        # 基于上下文
        context_factor = await self._calculate_context_importance(context) if context else 0
        
        # 基于提示
        hint_factor = len(hints) * 0.1 if hints else 0
        
        importance = min(
            base_importance + length_factor + type_factor + user_factor + context_factor + hint_factor,
            1.0
        )
        
        return importance
    
    async def _extract_context_information(self, 
                                          content: str,
                                          context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """提取上下文信息"""
        extracted = {
            "entities": await self._extract_named_entities(content),
            "emotions": await self._analyze_emotional_content(content),
            "topics": await self._extract_topic_keywords(content),
            "intent": await self._classify_intent(content),
            "complexity": await self._calculate_content_complexity(content)
        }
        
        if context:
            extracted.update(context)
        
        return extracted
    
    async def _personalize_memory_content(self,
                                         user_id: str,
                                         content: str,
                                         context: Dict[str, Any]) -> str:
        """个性化记忆内容"""
        profile = await self._get_personalization_profile(user_id)
        
        # 基于用户偏好调整内容表示
        if profile.preferences.get("detailed_memory", False):
            # 添加详细上下文
            personalized = f"{content}\n[Context: {context.get('topics', [])}]"
        else:
            # 保持简洁
            personalized = content
        
        # 添加个性化标签
        if profile.preferences.get("add_tags", True):
            tags = context.get("topics", [])[:3]
            if tags:
                personalized += f"\n[Tags: {', '.join(tags)}]"
        
        return personalized
    
    async def _emit_learning_signal(self,
                                   user_id: str,
                                   signal_type: LearningSignal,
                                   data: Dict[str, Any]):
        """发出学习信号"""
        signal = (user_id, signal_type, {
            **data,
            "timestamp": datetime.now().isoformat()
        })
        
        self.learning_signals.append(signal)
        
        # 保持信号队列大小
        if len(self.learning_signals) > 1000:
            self.learning_signals = self.learning_signals[-500:]
    
    async def _process_learning_signals(self):
        """处理学习信号"""
        if not self.learning_signals:
            return
        
        # 按用户分组处理信号
        user_signals = {}
        for user_id, signal_type, data in self.learning_signals:
            if user_id not in user_signals:
                user_signals[user_id] = []
            user_signals[user_id].append((signal_type, data))
        
        # 为每个用户更新学习模式
        for user_id, signals in user_signals.items():
            await self._update_user_learning_pattern(user_id, signals)
        
        # 清空已处理的信号
        self.learning_signals.clear()
    
    def get_memory_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取记忆统计信息"""
        stats = {
            "total_memories": 0,
            "memory_type_distribution": {},
            "average_importance": 0,
            "context_windows": 0,
            "personalization_level": "basic",
            "learning_signals_processed": len(self.learning_signals),
            "performance_metrics": self.performance_metrics
        }
        
        if user_id:
            # 用户特定统计
            user_pattern = self.user_patterns.get(user_id)
            profile = self.personalization_profiles.get(user_id)
            
            if user_pattern:
                stats.update({
                    "user_confidence_score": user_pattern.confidence_score,
                    "learning_velocity": user_pattern.learning_velocity,
                    "session_patterns": len(user_pattern.session_patterns)
                })
            
            if profile:
                stats.update({
                    "personalization_level": profile.personalization_level.value,
                    "trust_score": profile.trust_score,
                    "adaptations_count": len(profile.adaptation_history)
                })
        
        return stats

class AdaptationEngine:
    """自适应引擎"""
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.adaptation_history = {}
        self.learning_models = {}
    
    async def adapt_to_user_behavior(self, 
                                    user_id: str,
                                    behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据用户行为进行自适应"""
        
        # 分析行为模式
        patterns = await self._analyze_behavior_patterns(user_id, behavior_data)
        
        # 更新学习模型
        await self._update_learning_model(user_id, patterns)
        
        # 生成适应策略
        adaptation_strategy = await self._generate_adaptation_strategy(user_id, patterns)
        
        # 应用适应
        adaptation_result = await self._apply_adaptation(user_id, adaptation_strategy)
        
        return adaptation_result
    
    async def _analyze_behavior_patterns(self, user_id: str, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析行为模式"""
        # 实现行为模式分析逻辑
        return {
            "interaction_frequency": behavior_data.get("interactions_per_session", 0),
            "preferred_memory_types": behavior_data.get("memory_type_usage", {}),
            "context_switching_rate": behavior_data.get("context_switches", 0),
            "feedback_patterns": behavior_data.get("feedback_ratio", 0.5)
        }
    
    async def _update_learning_model(self, user_id: str, patterns: Dict[str, Any]):
        """更新学习模型"""
        if user_id not in self.learning_models:
            self.learning_models[user_id] = {
                "preference_model": {},
                "behavior_model": {},
                "adaptation_model": {}
            }
        
        # 更新偏好模型
        self.learning_models[user_id]["preference_model"].update(patterns)
        
    async def _generate_adaptation_strategy(self, user_id: str, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """生成适应策略"""
        return {
            "memory_importance_weights": await self._calculate_importance_weights(patterns),
            "context_compression_threshold": await self._calculate_compression_threshold(patterns),
            "personalization_adjustments": await self._calculate_personalization_adjustments(patterns)
        }
    
    async def _apply_adaptation(self, user_id: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """应用适应策略"""
        # 实现适应策略应用逻辑
        return {
            "adaptations_applied": list(strategy.keys()),
            "adaptation_timestamp": datetime.now().isoformat(),
            "expected_improvement": 0.1
        }

class PrivacyManager:
    """隐私管理器"""
    
    def __init__(self):
        self.anonymization_rules = {}
        self.encryption_keys = {}
        
    async def anonymize_data(self, 
                            data: Dict[str, Any], 
                            privacy_settings: Dict[str, Any]) -> Dict[str, Any]:
        """数据匿名化"""
        anonymized = data.copy()
        
        # 基于隐私级别进行匿名化
        privacy_level = privacy_settings.get("level", "standard")
        
        if privacy_level == "high":
            # 高级别隐私保护
            anonymized = await self._high_level_anonymization(anonymized)
        elif privacy_level == "medium":
            # 中等级别隐私保护
            anonymized = await self._medium_level_anonymization(anonymized)
        
        return anonymized
    
    async def _high_level_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """高级别匿名化"""
        # 移除或hash所有可识别信息
        sensitive_fields = ["name", "email", "phone", "address", "id"]
        
        for field in sensitive_fields:
            if field in data:
                data[field] = self._hash_value(str(data[field]))
        
        return data
    
    async def _medium_level_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """中等级别匿名化"""
        # 部分匿名化
        if "email" in data:
            email = data["email"]
            if "@" in email:
                username, domain = email.split("@", 1)
                data["email"] = f"{username[:2]}***@{domain}"
        
        return data
    
    def _hash_value(self, value: str) -> str:
        """哈希值计算"""
        return hashlib.sha256(value.encode()).hexdigest()[:8]

# 全局实例
enhanced_memory_manager = None

def get_enhanced_memory_manager(mem_agent: MemAgent, sskg_manager: EnhancedSSKGManager) -> EnhancedMemoryManager:
    """获取增强记忆管理器实例"""
    global enhanced_memory_manager
    if enhanced_memory_manager is None:
        enhanced_memory_manager = EnhancedMemoryManager(mem_agent, sskg_manager)
    return enhanced_memory_manager