#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 12:30:00
@Author  : DAIP-LIVE Team
@File    : scenario_manager.py
@Description:
    V0.2.8 三场景集成和智能切换核心功能实现
    
    实现场景管理器，支持：
    - 学术研究、专家咨询、轻松讨论三场景统一管理
    - 智能场景推荐和无缝切换
    - 上下文保持和数据一致性
    - 个性化适配和用户偏好学习
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# 导入三个场景
from src.scenarios.academic_research_scenario import AcademicResearchScenario
from src.scenarios.expert_consultation_scenario import ExpertConsultationScenario
from src.scenarios.casual_discussion_scenario import CasualDiscussionScenario

# 导入核心服务
from src.core_services.memory_agent import MemAgent
from src.core_services.wiki_service import WikiService

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """场景类型枚举"""
    ACADEMIC_RESEARCH = "academic_research"
    EXPERT_CONSULTATION = "expert_consultation" 
    CASUAL_DISCUSSION = "casual_discussion"


@dataclass
class ScenarioContext:
    """场景上下文"""
    scenario_id: str
    scenario_type: ScenarioType
    topic: str
    user_preferences: Dict[str, Any]
    session_data: Dict[str, Any]
    created_at: str
    last_accessed: str
    is_active: bool = True


@dataclass
class ScenarioTransition:
    """场景转换记录"""
    transition_id: str
    from_scenario: Optional[ScenarioType]
    to_scenario: ScenarioType
    transition_reason: str
    context_preserved: bool
    user_intent: str
    timestamp: str


@dataclass
class UserProfile:
    """用户档案"""
    user_id: str
    preferences: Dict[str, Any]
    scenario_usage_stats: Dict[str, int]
    favorite_scenarios: List[ScenarioType]
    last_scenarios: List[ScenarioType]
    interaction_history: List[Dict[str, Any]]
    created_at: str
    updated_at: str


class ScenarioManager:
    """
    场景管理器 - V0.2.8核心功能实现
    
    负责三个场景的统一管理、智能切换和上下文保持：
    - 场景生命周期管理
    - 智能推荐引擎
    - 上下文传递和保持
    - 用户偏好学习
    """
    
    def __init__(self):
        """初始化场景管理器"""
        self.manager_id = str(uuid.uuid4())
        
        # 场景实例
        self.scenarios = {
            ScenarioType.ACADEMIC_RESEARCH: AcademicResearchScenario(),
            ScenarioType.EXPERT_CONSULTATION: ExpertConsultationScenario(),
            ScenarioType.CASUAL_DISCUSSION: CasualDiscussionScenario()
        }
        
        # 核心服务
        self.wiki_service = WikiService()
        
        # 初始化记忆代理
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            sskg_manager = EnhancedSSKGManager()
            self.memory_agent = MemAgent(sskg_manager)
        except Exception as e:
            logger.warning(f"MemAgent初始化失败，使用空实现: {e}")
            self.memory_agent = None
        
        # 管理器状态
        self.active_contexts = {}  # scenario_id -> ScenarioContext
        self.user_profiles = {}    # user_id -> UserProfile
        self.transition_history = []  # ScenarioTransition列表
        self.global_context_cache = {}  # 全局上下文缓存
        
        # 智能推荐配置
        self.recommendation_weights = {
            "topic_similarity": 0.3,
            "user_preference": 0.25,
            "usage_history": 0.2,
            "context_relevance": 0.15,
            "time_pattern": 0.1
        }
        
        logger.info(f"场景管理器初始化完成: {self.manager_id}")
    
    async def start_scenario(
        self,
        scenario_type: ScenarioType,
        topic: str,
        user_id: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """启动指定场景"""
        logger.info(f"启动场景: {scenario_type.value} - {topic}")
        
        try:
            # 1. 创建场景上下文
            scenario_context = await self._create_scenario_context(
                scenario_type, topic, user_id, user_preferences, context_data
            )
            
            # 2. 更新用户档案
            await self._update_user_profile(user_id, scenario_type, user_preferences)
            
            # 3. 执行场景
            scenario_result = await self._execute_scenario(scenario_context)
            
            # 4. 记录转换历史
            if hasattr(self, '_last_scenario'):
                await self._record_scenario_transition(
                    self._last_scenario, scenario_type, f"用户启动{scenario_type.value}", user_id
                )
            
            self._last_scenario = scenario_type
            
            # 5. 缓存上下文
            self.active_contexts[scenario_context.scenario_id] = scenario_context
            
            return {
                "success": True,
                "scenario_id": scenario_context.scenario_id,
                "scenario_type": scenario_type.value,
                "context": asdict(scenario_context),
                "result": scenario_result,
                "recommendations": await self._generate_follow_up_recommendations(scenario_context, scenario_result)
            }
            
        except Exception as e:
            logger.error(f"场景启动失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "scenario_type": scenario_type.value,
                "topic": topic
            }
    
    async def switch_scenario(
        self,
        from_scenario_id: str,
        to_scenario_type: ScenarioType,
        transition_reason: str,
        preserve_context: bool = True
    ) -> Dict[str, Any]:
        """场景切换"""
        logger.info(f"场景切换: {from_scenario_id} -> {to_scenario_type.value}")
        
        try:
            # 1. 获取源场景上下文
            from_context = self.active_contexts.get(from_scenario_id)
            if not from_context:
                return {
                    "success": False,
                    "error": "源场景上下文不存在",
                    "from_scenario_id": from_scenario_id
                }
            
            # 2. 提取可传递的上下文
            preserved_context = {}
            if preserve_context:
                preserved_context = await self._extract_transferable_context(from_context)
            
            # 3. 启动新场景
            new_scenario_result = await self.start_scenario(
                to_scenario_type,
                from_context.topic,  # 继承话题
                from_context.user_preferences.get("user_id", "anonymous"),
                from_context.user_preferences,
                preserved_context
            )
            
            # 4. 记录转换
            await self._record_scenario_transition(
                from_context.scenario_type, to_scenario_type, transition_reason,
                from_context.user_preferences.get("user_id", "anonymous")
            )
            
            # 5. 更新源场景状态
            from_context.is_active = False
            from_context.last_accessed = datetime.now().isoformat()
            
            return {
                "success": True,
                "transition_id": self.transition_history[-1].transition_id if self.transition_history else None,
                "from_scenario": asdict(from_context),
                "new_scenario": new_scenario_result,
                "context_preserved": preserve_context,
                "preserved_data": preserved_context
            }
            
        except Exception as e:
            logger.error(f"场景切换失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "from_scenario_id": from_scenario_id,
                "to_scenario_type": to_scenario_type.value
            }
    
    async def recommend_scenario(
        self,
        user_input: str,
        user_id: str,
        current_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """智能场景推荐"""
        logger.info(f"为用户 {user_id} 生成场景推荐")
        
        try:
            # 1. 分析用户输入
            input_analysis = await self._analyze_user_input(user_input)
            
            # 2. 获取用户档案
            user_profile = self.user_profiles.get(user_id, await self._create_default_user_profile(user_id))
            
            # 3. 计算场景匹配分数
            scenario_scores = {}
            for scenario_type in ScenarioType:
                score = await self._calculate_scenario_score(
                    scenario_type, input_analysis, user_profile, current_context
                )
                scenario_scores[scenario_type] = score
            
            # 4. 排序推荐
            sorted_scenarios = sorted(
                scenario_scores.items(), 
                key=lambda x: x[1]["total_score"], 
                reverse=True
            )
            
            # 5. 生成推荐结果
            recommendations = []
            for scenario_type, score_details in sorted_scenarios:
                recommendation = {
                    "scenario_type": scenario_type.value,
                    "confidence": score_details["total_score"],
                    "reasons": score_details["reasons"],
                    "suggested_config": await self._generate_scenario_config(scenario_type, input_analysis, user_profile)
                }
                recommendations.append(recommendation)
            
            return {
                "success": True,
                "user_input": user_input,
                "analysis": input_analysis,
                "recommendations": recommendations,
                "top_recommendation": recommendations[0] if recommendations else None
            }
            
        except Exception as e:
            logger.error(f"场景推荐失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_input": user_input
            }
    
    async def get_unified_interface_data(self, user_id: str) -> Dict[str, Any]:
        """获取统一界面数据"""
        try:
            user_profile = self.user_profiles.get(user_id, await self._create_default_user_profile(user_id))
            
            # 活跃场景
            active_scenarios = [
                context for context in self.active_contexts.values()
                if context.is_active and context.user_preferences.get("user_id") == user_id
            ]
            
            # 最近转换
            recent_transitions = [
                transition for transition in self.transition_history[-10:]
                if any(context.user_preferences.get("user_id") == user_id for context in self.active_contexts.values())
            ]
            
            # 统计信息
            usage_stats = user_profile.scenario_usage_stats
            total_usage = sum(usage_stats.values())
            
            return {
                "user_profile": asdict(user_profile),
                "active_scenarios": [asdict(context) for context in active_scenarios],
                "recent_transitions": [asdict(transition) for transition in recent_transitions],
                "usage_statistics": {
                    "total_sessions": total_usage,
                    "scenario_distribution": {
                        scenario.value: count for scenario, count in 
                        zip(ScenarioType, [usage_stats.get(s.value, 0) for s in ScenarioType])
                    },
                    "favorite_scenarios": [s.value for s in user_profile.favorite_scenarios]
                },
                "scenario_capabilities": await self._get_scenario_capabilities(),
                "interface_config": await self._generate_interface_config(user_profile)
            }
            
        except Exception as e:
            logger.error(f"获取统一界面数据失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_scenario_context(
        self,
        scenario_type: ScenarioType,
        topic: str,
        user_id: str,
        user_preferences: Optional[Dict[str, Any]],
        context_data: Optional[Dict[str, Any]]
    ) -> ScenarioContext:
        """创建场景上下文"""
        scenario_id = str(uuid.uuid4())
        
        if user_preferences is None:
            user_preferences = {}
        user_preferences["user_id"] = user_id
        
        return ScenarioContext(
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            topic=topic,
            user_preferences=user_preferences,
            session_data=context_data or {},
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        )
    
    async def _execute_scenario(self, context: ScenarioContext) -> Dict[str, Any]:
        """执行具体场景"""
        scenario = self.scenarios[context.scenario_type]
        
        if context.scenario_type == ScenarioType.ACADEMIC_RESEARCH:
            return await scenario.conduct_academic_research(
                research_topic=context.topic,
                research_config=context.session_data.get("config"),
                user_preferences=context.user_preferences
            )
        elif context.scenario_type == ScenarioType.EXPERT_CONSULTATION:
            return await scenario.start_expert_consultation(
                consultation_question=context.topic,
                user_preferences=context.user_preferences,
                config=context.session_data.get("config")
            )
        elif context.scenario_type == ScenarioType.CASUAL_DISCUSSION:
            return await scenario.start_casual_discussion(
                initial_topic=context.topic,
                user_preferences=context.user_preferences,
                config=context.session_data.get("config")
            )
        else:
            raise ValueError(f"不支持的场景类型: {context.scenario_type}")
    
    async def _update_user_profile(
        self,
        user_id: str,
        scenario_type: ScenarioType,
        user_preferences: Optional[Dict[str, Any]]
    ):
        """更新用户档案"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = await self._create_default_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        
        # 更新使用统计
        profile.scenario_usage_stats[scenario_type.value] = profile.scenario_usage_stats.get(scenario_type.value, 0) + 1
        
        # 更新最近使用场景
        if scenario_type not in profile.last_scenarios:
            profile.last_scenarios.insert(0, scenario_type)
        else:
            profile.last_scenarios.remove(scenario_type)
            profile.last_scenarios.insert(0, scenario_type)
        
        # 保持最近5个
        profile.last_scenarios = profile.last_scenarios[:5]
        
        # 更新偏好（如果提供）
        if user_preferences:
            for key, value in user_preferences.items():
                if key != "user_id":
                    profile.preferences[key] = value
        
        # 更新收藏场景（基于使用频率）
        usage_items = list(profile.scenario_usage_stats.items())
        usage_items.sort(key=lambda x: x[1], reverse=True)
        profile.favorite_scenarios = [ScenarioType(item[0]) for item, _ in zip(usage_items, range(3))]
        
        profile.updated_at = datetime.now().isoformat()
        
        # 存储到记忆系统
        if self.memory_agent:
            try:
                await self.memory_agent.store_interaction({
                    "type": "user_profile_update",
                    "user_id": user_id,
                    "scenario_type": scenario_type.value,
                    "profile": asdict(profile),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"用户档案存储失败: {e}")
    
    async def _create_default_user_profile(self, user_id: str) -> UserProfile:
        """创建默认用户档案"""
        return UserProfile(
            user_id=user_id,
            preferences={},
            scenario_usage_stats={},
            favorite_scenarios=[],
            last_scenarios=[],
            interaction_history=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    async def _record_scenario_transition(
        self,
        from_scenario: Optional[ScenarioType],
        to_scenario: ScenarioType,
        reason: str,
        user_id: str
    ):
        """记录场景转换"""
        transition = ScenarioTransition(
            transition_id=str(uuid.uuid4()),
            from_scenario=from_scenario,
            to_scenario=to_scenario,
            transition_reason=reason,
            context_preserved=True,  # 简化实现
            user_intent=reason,
            timestamp=datetime.now().isoformat()
        )
        
        self.transition_history.append(transition)
        
        # 保持历史记录大小
        if len(self.transition_history) > 1000:
            self.transition_history = self.transition_history[-500:]
        
        # 存储到记忆系统
        if self.memory_agent:
            try:
                await self.memory_agent.store_interaction({
                    "type": "scenario_transition",
                    "user_id": user_id,
                    "transition": asdict(transition),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"转换记录存储失败: {e}")
    
    async def _extract_transferable_context(self, from_context: ScenarioContext) -> Dict[str, Any]:
        """提取可传递的上下文"""
        transferable = {
            "original_topic": from_context.topic,
            "user_preferences": from_context.user_preferences.copy(),
            "previous_scenario": from_context.scenario_type.value,
            "session_metadata": {
                "started_at": from_context.created_at,
                "duration": (datetime.now() - datetime.fromisoformat(from_context.created_at)).total_seconds()
            }
        }
        
        # 场景特定的上下文提取
        if hasattr(from_context, 'session_data') and from_context.session_data:
            # 提取关键洞察或结论
            if "conclusions" in from_context.session_data:
                transferable["previous_conclusions"] = from_context.session_data["conclusions"]
            
            # 提取关键词和话题
            if "keywords" in from_context.session_data:
                transferable["keywords"] = from_context.session_data["keywords"]
        
        return transferable
    
    async def _analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """分析用户输入"""
        analysis = {
            "input_text": user_input,
            "length": len(user_input),
            "keywords": [],
            "intent_indicators": {},
            "complexity_level": "medium",
            "domain_hints": []
        }
        
        # 简单关键词提取
        words = user_input.lower().split()
        analysis["keywords"] = [word for word in words if len(word) > 3]
        
        # 意图指示器检测
        academic_indicators = ["研究", "分析", "学术", "论文", "报告", "深入", "理论", "文献"]
        expert_indicators = ["咨询", "建议", "专家", "决策", "选择", "方案", "评估", "对比"]
        casual_indicators = ["聊聊", "讨论", "分享", "看法", "想法", "轻松", "随便", "简单"]
        
        analysis["intent_indicators"] = {
            "academic": sum(1 for indicator in academic_indicators if indicator in user_input),
            "expert": sum(1 for indicator in expert_indicators if indicator in user_input),
            "casual": sum(1 for indicator in casual_indicators if indicator in user_input)
        }
        
        # 复杂度评估
        if len(user_input) > 200 or any(word in user_input for word in ["深入", "全面", "详细", "综合"]):
            analysis["complexity_level"] = "high"
        elif len(user_input) < 50 or any(word in user_input for word in ["简单", "快速", "简短"]):
            analysis["complexity_level"] = "low"
        
        return analysis
    
    async def _calculate_scenario_score(
        self,
        scenario_type: ScenarioType,
        input_analysis: Dict[str, Any],
        user_profile: UserProfile,
        current_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算场景匹配分数"""
        scores = {}
        reasons = []
        
        # 1. 话题相似性分数
        intent_match = input_analysis["intent_indicators"].get(scenario_type.value.split("_")[0], 0)
        if scenario_type == ScenarioType.ACADEMIC_RESEARCH:
            intent_match = input_analysis["intent_indicators"].get("academic", 0)
        elif scenario_type == ScenarioType.EXPERT_CONSULTATION:
            intent_match = input_analysis["intent_indicators"].get("expert", 0)
        elif scenario_type == ScenarioType.CASUAL_DISCUSSION:
            intent_match = input_analysis["intent_indicators"].get("casual", 0)
        
        topic_score = min(intent_match / 3.0, 1.0)  # 最多3个关键词匹配
        scores["topic_similarity"] = topic_score
        
        if topic_score > 0.5:
            reasons.append(f"输入内容与{scenario_type.value}高度匹配")
        
        # 2. 用户偏好分数
        usage_count = user_profile.scenario_usage_stats.get(scenario_type.value, 0)
        total_usage = sum(user_profile.scenario_usage_stats.values())
        preference_score = usage_count / max(total_usage, 1)
        scores["user_preference"] = preference_score
        
        if scenario_type in user_profile.favorite_scenarios:
            reasons.append("这是您常用的场景类型")
        
        # 3. 使用历史分数
        recent_usage = scenario_type in user_profile.last_scenarios[:3]
        history_score = 0.8 if recent_usage else 0.2
        scores["usage_history"] = history_score
        
        # 4. 上下文相关性分数
        context_score = 0.5  # 默认中等相关性
        if current_context:
            # 如果当前有活跃场景，计算相关性
            pass
        scores["context_relevance"] = context_score
        
        # 5. 时间模式分数（简化）
        time_score = 0.5  # 简化为固定值
        scores["time_pattern"] = time_score
        
        # 计算加权总分
        total_score = sum(
            scores[factor] * self.recommendation_weights[factor]
            for factor in self.recommendation_weights
        )
        
        return {
            "total_score": total_score,
            "component_scores": scores,
            "reasons": reasons
        }
    
    async def _generate_scenario_config(
        self,
        scenario_type: ScenarioType,
        input_analysis: Dict[str, Any],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """生成场景配置建议"""
        config = {}
        
        complexity = input_analysis["complexity_level"]
        
        if scenario_type == ScenarioType.ACADEMIC_RESEARCH:
            config = {
                "research_depth": "comprehensive" if complexity == "high" else "standard",
                "report_length": "detailed" if complexity == "high" else "summary",
                "include_citations": True,
                "perspective_count": 4 if complexity == "high" else 3
            }
        elif scenario_type == ScenarioType.EXPERT_CONSULTATION:
            config = {
                "expert_count": 4 if complexity == "high" else 3,
                "consultation_depth": "detailed" if complexity == "high" else "standard",
                "include_decision_framework": True,
                "provide_action_plan": True
            }
        elif scenario_type == ScenarioType.CASUAL_DISCUSSION:
            config = {
                "discussion_style": "relaxed",
                "humor_level": 0.7,
                "max_participants": 3,
                "social_elements": True
            }
        
        return config
    
    async def _generate_follow_up_recommendations(
        self,
        context: ScenarioContext,
        result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成后续推荐"""
        recommendations = []
        
        if result.get("success"):
            # 基于当前场景推荐其他场景
            current_type = context.scenario_type
            
            if current_type == ScenarioType.ACADEMIC_RESEARCH:
                recommendations.append({
                    "type": "scenario_switch",
                    "target_scenario": ScenarioType.EXPERT_CONSULTATION.value,
                    "reason": "获取该研究主题的专家实践建议",
                    "confidence": 0.7
                })
            elif current_type == ScenarioType.EXPERT_CONSULTATION:
                recommendations.append({
                    "type": "scenario_switch", 
                    "target_scenario": ScenarioType.CASUAL_DISCUSSION.value,
                    "reason": "轻松讨论相关话题和个人看法",
                    "confidence": 0.6
                })
            elif current_type == ScenarioType.CASUAL_DISCUSSION:
                recommendations.append({
                    "type": "scenario_switch",
                    "target_scenario": ScenarioType.ACADEMIC_RESEARCH.value,
                    "reason": "深入研究讨论中的有趣观点",
                    "confidence": 0.5
                })
        
        return recommendations
    
    async def _get_scenario_capabilities(self) -> Dict[str, Any]:
        """获取场景能力描述"""
        return {
            ScenarioType.ACADEMIC_RESEARCH.value: {
                "name": "学术研究",
                "description": "深度研究和万字级报告生成",
                "capabilities": ["多视角分析", "文献综合", "结构化报告", "学术严谨性"],
                "suitable_for": ["学术论文", "研究报告", "深度分析", "理论探讨"]
            },
            ScenarioType.EXPERT_CONSULTATION.value: {
                "name": "专家咨询",
                "description": "跨领域专家建议和决策支持",
                "capabilities": ["专家匹配", "权威建议", "决策框架", "行动方案"],
                "suitable_for": ["技术选型", "商业决策", "专业咨询", "方案对比"]
            },
            ScenarioType.CASUAL_DISCUSSION.value: {
                "name": "轻松讨论",
                "description": "自然愉快的话题探讨",
                "capabilities": ["自然对话", "话题转换", "社交互动", "氛围营造"],
                "suitable_for": ["日常话题", "兴趣分享", "轻松聊天", "观点交流"]
            }
        }
    
    async def _generate_interface_config(self, user_profile: UserProfile) -> Dict[str, Any]:
        """生成界面配置"""
        return {
            "default_scenario": user_profile.favorite_scenarios[0].value if user_profile.favorite_scenarios else ScenarioType.CASUAL_DISCUSSION.value,
            "show_recommendations": True,
            "enable_quick_switch": True,
            "display_usage_stats": len(user_profile.scenario_usage_stats) > 0,
            "preferred_themes": user_profile.preferences.get("ui_theme", "default"),
            "quick_access_scenarios": [s.value for s in user_profile.last_scenarios[:3]]
        }


# 便捷函数
async def create_scenario_manager() -> ScenarioManager:
    """创建场景管理器实例"""
    return ScenarioManager()


async def recommend_and_start_scenario(
    user_input: str,
    user_id: str,
    auto_start: bool = True
) -> Dict[str, Any]:
    """推荐并启动场景的便捷函数"""
    manager = ScenarioManager()
    
    # 获取推荐
    recommendation_result = await manager.recommend_scenario(user_input, user_id)
    
    if not recommendation_result.get("success"):
        return recommendation_result
    
    result = {
        "recommendation": recommendation_result,
        "auto_started": False
    }
    
    # 自动启动最佳推荐场景
    if auto_start and recommendation_result.get("top_recommendation"):
        top_rec = recommendation_result["top_recommendation"]
        
        if top_rec["confidence"] > 0.6:  # 置信度足够高
            scenario_type = ScenarioType(top_rec["scenario_type"])
            
            start_result = await manager.start_scenario(
                scenario_type=scenario_type,
                topic=user_input,
                user_id=user_id,
                user_preferences={"auto_start": True},
                context_data={"config": top_rec["suggested_config"]}
            )
            
            result["scenario_start"] = start_result
            result["auto_started"] = start_result.get("success", False)
    
    return result


# 使用示例
async def main():
    """测试场景管理器"""
    manager = ScenarioManager()
    
    # 测试场景推荐
    user_input = "我想深入研究AI在教育中的应用"
    user_id = "test_user"
    
    print("🔍 测试智能场景推荐...")
    recommendation = await manager.recommend_scenario(user_input, user_id)
    print(f"推荐结果: {recommendation.get('top_recommendation', {}).get('scenario_type')}")
    
    # 测试场景启动
    if recommendation.get("success") and recommendation.get("top_recommendation"):
        scenario_type = ScenarioType(recommendation["top_recommendation"]["scenario_type"])
        
        print(f"\n🚀 启动推荐场景: {scenario_type.value}")
        start_result = await manager.start_scenario(
            scenario_type=scenario_type,
            topic=user_input,
            user_id=user_id
        )
        
        if start_result.get("success"):
            print(f"✅ 场景启动成功: {start_result['scenario_id']}")
            
            # 测试场景切换
            print(f"\n🔄 测试场景切换...")
            switch_result = await manager.switch_scenario(
                from_scenario_id=start_result["scenario_id"],
                to_scenario_type=ScenarioType.CASUAL_DISCUSSION,
                transition_reason="用户希望轻松讨论"
            )
            
            if switch_result.get("success"):
                print("✅ 场景切换成功")
            else:
                print(f"❌ 场景切换失败: {switch_result.get('error')}")
        else:
            print(f"❌ 场景启动失败: {start_result.get('error')}")
    
    # 测试统一界面数据
    print(f"\n📊 获取统一界面数据...")
    interface_data = await manager.get_unified_interface_data(user_id)
    print(f"用户档案: {interface_data.get('user_profile', {}).get('scenario_usage_stats', {})}")


if __name__ == "__main__":
    asyncio.run(main())