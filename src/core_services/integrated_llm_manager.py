#!/usr/bin/env python3
"""集成LLM管理器

为所有虚拟角色提供统一的、智能优化的LLM调用服务
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .memory_agent import MemAgent
from .real_llm_context_optimizer import IntelligentContextOptimizer, OptimizationResult
from .role_manager import RoleManager

logger = logging.getLogger(__name__)


@dataclass
class RoleContext:
    """角色上下文"""

    role_id: str
    role_name: str
    role_definition: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    memory_context: Dict[str, Any]
    current_task: Optional[str] = None
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None


@dataclass
class OptimizedLLMCall:
    """优化后的LLM调用"""

    role_id: str
    original_prompt: str
    optimized_prompt: str
    llm_response: str
    optimization_metrics: Dict[str, Any]
    call_timestamp: datetime
    tokens_used: int
    response_time: float


class IntegratedLLMManager:
    """集成LLM管理器"""

    def __init__(self):
        """初始化LLM管理器"""
        self.context_optimizer = IntelligentContextOptimizer()
        self.role_manager = RoleManager()
        self.memory_agent = MemAgent()

        # 角色上下文缓存
        self.role_contexts: Dict[str, RoleContext] = {}

        # 调用历史记录
        self.call_history: List[OptimizedLLMCall] = []

        # 性能统计
        self.performance_stats = {
            "total_calls": 0,
            "total_tokens_saved": 0,
            "total_time_saved": 0.0,
            "average_improvement": 0.0
        }

        logger.info("集成LLM管理器初始化完成")

    async def initialize(self):
        """初始化所有组件"""
        await self.context_optimizer.initialize()
        await self.role_manager.initialize()
        await self.memory_agent.initialize()

        # 加载所有角色的上下文
        await self._load_all_role_contexts()

        logger.info("集成LLM管理器组件初始化完成")

    async def call_llm_for_role(
        self,
        role_id: str,
        user_input: str,
        task_context: Optional[str] = None,
        additional_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """为特定角色调用LLM（带智能上下文优化）"""
        try:
            # 1. 获取或创建角色上下文
            role_context = await self._get_or_create_role_context(role_id)

            # 2. 更新角色交互历史
            await self._update_role_interaction(role_context, user_input, task_context)

            # 3. 构建角色专用的上下文信息
            role_specific_context = await self._build_role_specific_context(
                role_context, task_context, additional_context
            )

            # 4. 使用智能优化器优化上下文
            optimization_result = await self.context_optimizer.optimize_context_with_llm(
                user_query=user_input,
                conversation_history=role_context.conversation_history,
                available_context=role_specific_context,
                target_model="llama3:instruct"
            )

            # 5. 记录优化后的调用
            optimized_call = OptimizedLLMCall(
                role_id=role_id,
                original_prompt=optimization_result.original_context + f"\n\n用户输入: {user_input}",
                optimized_prompt=optimization_result.optimized_context + f"\n\n用户输入: {user_input}",
                llm_response=optimization_result.optimized_response.content,
                optimization_metrics=optimization_result.metrics,
                call_timestamp=datetime.now(),
                tokens_used=optimization_result.optimized_response.tokens_used,
                response_time=optimization_result.optimized_response.response_time
            )

            self.call_history.append(optimized_call)

            # 6. 更新性能统计
            await self._update_performance_stats(optimization_result)

            # 7. 更新角色记忆
            await self._update_role_memory(role_context, user_input, optimized_call.llm_response)

            # 8. 返回结果
            return {
                "role_id": role_id,
                "role_name": role_context.role_name,
                "response": optimized_call.llm_response,
                "optimization_applied": True,
                "optimization_metrics": {
                    "improvement_score": optimization_result.improvement_score,
                    "context_compression": optimization_result.metrics["context_compression_ratio"],
                    "tokens_saved": optimization_result.metrics["token_efficiency"]["token_savings"],
                    "time_saved": optimization_result.metrics["response_time"]["time_difference"]
                },
                "call_metadata": {
                    "tokens_used": optimized_call.tokens_used,
                    "response_time": optimized_call.response_time,
                    "timestamp": optimized_call.call_timestamp.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"角色 {role_id} LLM调用失败: {e}")

            # 降级到基础调用
            return await self._fallback_llm_call(role_id, user_input, task_context)

    async def call_llm_for_multi_role_debate(
        self,
        participating_roles: List[str],
        debate_topic: str,
        debate_context: Dict[str, Any],
        round_number: int = 1
    ) -> Dict[str, Any]:
        """多角色辩论的LLM调用（每个角色都使用优化）"""
        debate_results = {}

        for role_id in participating_roles:
            try:
                # 构建辩论专用上下文
                debate_specific_context = {
                    "debate_topic": debate_topic,
                    "debate_round": round_number,
                    "participating_roles": participating_roles,
                    "debate_history": debate_context.get("history", []),
                    "role_positions": debate_context.get("positions", {}),
                    "debate_rules": debate_context.get("rules", [])
                }

                # 为每个角色生成专门的辩论输入
                role_debate_input = f"在关于'{debate_topic}'的辩论中，请基于你的专业背景和认知框架提出你的观点和论证。这是第{round_number}轮辩论。"

                # 调用优化的LLM
                result = await self.call_llm_for_role(
                    role_id=role_id,
                    user_input=role_debate_input,
                    task_context=f"多角色辩论-{debate_topic}",
                    additional_context=debate_specific_context
                )

                debate_results[role_id] = result

            except Exception as e:
                logger.error(f"角色 {role_id} 辩论调用失败: {e}")
                debate_results[role_id] = {
                    "error": str(e),
                    "role_id": role_id
                }

        return {
            "debate_topic": debate_topic,
            "round_number": round_number,
            "participating_roles": participating_roles,
            "role_responses": debate_results,
            "debate_timestamp": datetime.now().isoformat(),
            "optimization_summary": await self._get_debate_optimization_summary(debate_results)
        }

    async def get_role_performance_analytics(self, role_id: str) -> Dict[str, Any]:
        """获取特定角色的性能分析"""
        role_calls = [call for call in self.call_history if call.role_id == role_id]

        if not role_calls:
            return {"error": f"角色 {role_id} 没有调用记录"}

        # 计算性能指标
        total_calls = len(role_calls)
        total_tokens_saved = sum(call.optimization_metrics["token_efficiency"]["token_savings"] for call in role_calls)
        total_time_saved = sum(call.optimization_metrics["response_time"]["time_difference"] for call in role_calls)
        avg_improvement = sum(call.optimization_metrics.get("improvement_score", 0) for call in role_calls) / total_calls

        # 最近调用趋势
        recent_calls = sorted(role_calls, key=lambda x: x.call_timestamp)[-10:]
        recent_improvement_trend = [call.optimization_metrics.get("improvement_score", 0) for call in recent_calls]

        return {
            "role_id": role_id,
            "performance_summary": {
                "total_calls": total_calls,
                "total_tokens_saved": total_tokens_saved,
                "total_time_saved": total_time_saved,
                "average_improvement": avg_improvement,
                "optimization_success_rate": sum(1 for call in role_calls if call.optimization_metrics.get("improvement_score", 0) > 0) / total_calls
            },
            "recent_trend": {
                "recent_calls_count": len(recent_calls),
                "recent_improvement_scores": recent_improvement_trend,
                "trend_direction": "improving" if len(recent_improvement_trend) > 1 and recent_improvement_trend[-1] > recent_improvement_trend[0] else "stable"
            },
            "context_optimization_stats": {
                "avg_context_compression": sum(call.optimization_metrics["context_compression_ratio"] for call in role_calls) / total_calls,
                "avg_tokens_per_call": sum(call.tokens_used for call in role_calls) / total_calls,
                "avg_response_time": sum(call.response_time for call in role_calls) / total_calls
            }
        }

    async def get_system_wide_analytics(self) -> Dict[str, Any]:
        """获取系统级性能分析"""
        if not self.call_history:
            return {"error": "没有调用记录"}

        # 按角色统计
        role_stats = {}
        for call in self.call_history:
            if call.role_id not in role_stats:
                role_stats[call.role_id] = {
                    "call_count": 0,
                    "tokens_saved": 0,
                    "time_saved": 0.0,
                    "improvement_scores": []
                }

            stats = role_stats[call.role_id]
            stats["call_count"] += 1
            stats["tokens_saved"] += call.optimization_metrics["token_efficiency"]["token_savings"]
            stats["time_saved"] += call.optimization_metrics["response_time"]["time_difference"]
            stats["improvement_scores"].append(call.optimization_metrics.get("improvement_score", 0))

        # 计算每个角色的平均表现
        for role_id, stats in role_stats.items():
            stats["avg_improvement"] = sum(stats["improvement_scores"]) / len(stats["improvement_scores"])

        # 系统整体统计
        total_calls = len(self.call_history)
        total_tokens_saved = sum(call.optimization_metrics["token_efficiency"]["token_savings"] for call in self.call_history)
        total_time_saved = sum(call.optimization_metrics["response_time"]["time_difference"] for call in self.call_history)
        avg_system_improvement = sum(call.optimization_metrics.get("improvement_score", 0) for call in self.call_history) / total_calls

        return {
            "system_summary": {
                "total_calls": total_calls,
                "active_roles": len(role_stats),
                "total_tokens_saved": total_tokens_saved,
                "total_time_saved": total_time_saved,
                "average_improvement": avg_system_improvement,
                "optimization_success_rate": sum(1 for call in self.call_history if call.optimization_metrics.get("improvement_score", 0) > 0) / total_calls
            },
            "role_performance": {
                role_id: {
                    "call_count": stats["call_count"],
                    "avg_improvement": stats["avg_improvement"],
                    "tokens_saved": stats["tokens_saved"],
                    "time_saved": stats["time_saved"]
                }
                for role_id, stats in role_stats.items()
            },
            "top_performing_roles": sorted(
                [(role_id, stats["avg_improvement"]) for role_id, stats in role_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "optimization_effectiveness": "高效" if avg_system_improvement > 0.3 else "有效" if avg_system_improvement > 0.1 else "基本有效"
        }

    async def _get_or_create_role_context(self, role_id: str) -> RoleContext:
        """获取或创建角色上下文"""
        if role_id not in self.role_contexts:
            # 从角色管理器获取角色定义
            role_definition = await self.role_manager.get_role_definition(role_id)

            if not role_definition:
                raise ValueError(f"角色 {role_id} 不存在")

            # 创建新的角色上下文
            self.role_contexts[role_id] = RoleContext(
                role_id=role_id,
                role_name=role_definition.get("name", role_id),
                role_definition=role_definition,
                conversation_history=[],
                memory_context={},
                interaction_count=0
            )

        return self.role_contexts[role_id]

    async def _update_role_interaction(
        self,
        role_context: RoleContext,
        user_input: str,
        task_context: Optional[str]
    ):
        """更新角色交互历史"""
        interaction = {
            "type": "user_input",
            "content": user_input,
            "task_context": task_context,
            "timestamp": datetime.now().isoformat()
        }

        role_context.conversation_history.append(interaction)
        role_context.interaction_count += 1
        role_context.last_interaction = datetime.now()
        role_context.current_task = task_context

        # 保持历史记录在合理范围内
        if len(role_context.conversation_history) > 20:
            role_context.conversation_history = role_context.conversation_history[-15:]

    async def _build_role_specific_context(
        self,
        role_context: RoleContext,
        task_context: Optional[str],
        additional_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """构建角色专用的上下文信息"""
        context = {
            "role_definition": role_context.role_definition,
            "role_expertise": role_context.role_definition.get("expertise", []),
            "role_personality": role_context.role_definition.get("personality", {}),
            "role_cognitive_style": role_context.role_definition.get("cognitive_style", {}),
            "interaction_history": role_context.conversation_history,
            "interaction_count": role_context.interaction_count,
            "current_task": task_context
        }

        # 获取角色相关的记忆
        if role_context.role_id:
            role_memories = await self.memory_agent.get_relevant_memories(
                role_context.role_id,
                role_context.current_task or "general"
            )
            context["role_memories"] = role_memories

        # 添加额外上下文
        if additional_context:
            context.update(additional_context)

        return context

    async def _update_performance_stats(self, optimization_result: OptimizationResult):
        """更新性能统计"""
        self.performance_stats["total_calls"] += 1
        self.performance_stats["total_tokens_saved"] += optimization_result.metrics["token_efficiency"]["token_savings"]
        self.performance_stats["total_time_saved"] += optimization_result.metrics["response_time"]["time_difference"]

        # 更新平均改进分数
        current_avg = self.performance_stats["average_improvement"]
        total_calls = self.performance_stats["total_calls"]
        new_score = optimization_result.improvement_score

        self.performance_stats["average_improvement"] = (current_avg * (total_calls - 1) + new_score) / total_calls

    async def _update_role_memory(
        self,
        role_context: RoleContext,
        user_input: str,
        llm_response: str
    ):
        """更新角色记忆"""
        try:
            memory_entry = {
                "role_id": role_context.role_id,
                "interaction_type": "llm_call",
                "user_input": user_input,
                "role_response": llm_response,
                "task_context": role_context.current_task,
                "timestamp": datetime.now().isoformat()
            }

            await self.memory_agent.store_memory(role_context.role_id, memory_entry)

        except Exception as e:
            logger.warning(f"更新角色 {role_context.role_id} 记忆失败: {e}")

    async def _fallback_llm_call(
        self,
        role_id: str,
        user_input: str,
        task_context: Optional[str]
    ) -> Dict[str, Any]:
        """降级LLM调用（不使用优化）"""
        try:
            role_context = await self._get_or_create_role_context(role_id)

            # 构建基础提示
            basic_prompt = f"""你是{role_context.role_name}，具有以下特征：
{json.dumps(role_context.role_definition, ensure_ascii=False, indent=2)}

用户输入: {user_input}

请基于你的角色定义和专业背景回应："""

            # 直接调用LLM（不优化）
            from .real_llm_context_optimizer import RealLLMClient
            llm_client = RealLLMClient()
            await llm_client.initialize()

            response = await llm_client.call_llm(basic_prompt)

            await llm_client.close()

            return {
                "role_id": role_id,
                "role_name": role_context.role_name,
                "response": response.content,
                "optimization_applied": False,
                "fallback_reason": "优化失败，使用基础调用",
                "call_metadata": {
                    "tokens_used": response.tokens_used,
                    "response_time": response.response_time,
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"降级调用也失败: {e}")
            return {
                "role_id": role_id,
                "error": f"LLM调用完全失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _load_all_role_contexts(self):
        """加载所有角色的上下文"""
        try:
            all_roles = await self.role_manager.get_all_roles()

            for role_id, role_definition in all_roles.items():
                self.role_contexts[role_id] = RoleContext(
                    role_id=role_id,
                    role_name=role_definition.get("name", role_id),
                    role_definition=role_definition,
                    conversation_history=[],
                    memory_context={},
                    interaction_count=0
                )

            logger.info(f"加载了 {len(self.role_contexts)} 个角色上下文")

        except Exception as e:
            logger.error(f"加载角色上下文失败: {e}")

    async def _get_debate_optimization_summary(self, debate_results: Dict[str, Any]) -> Dict[str, Any]:
        """获取辩论优化摘要"""
        successful_optimizations = 0
        total_tokens_saved = 0
        total_time_saved = 0.0
        improvement_scores = []

        for role_id, result in debate_results.items():
            if "optimization_metrics" in result:
                successful_optimizations += 1
                metrics = result["optimization_metrics"]
                total_tokens_saved += metrics.get("tokens_saved", 0)
                total_time_saved += metrics.get("time_saved", 0.0)
                improvement_scores.append(metrics.get("improvement_score", 0))

        return {
            "participating_roles": len(debate_results),
            "successful_optimizations": successful_optimizations,
            "optimization_success_rate": successful_optimizations / len(debate_results) if debate_results else 0,
            "total_tokens_saved": total_tokens_saved,
            "total_time_saved": total_time_saved,
            "average_improvement": sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0,
            "debate_optimization_effectiveness": "高效" if sum(improvement_scores) / len(improvement_scores) > 0.3 else "有效" if sum(improvement_scores) / len(improvement_scores) > 0.1 else "基本有效" if improvement_scores else "无效"
        }

    async def close(self):
        """关闭管理器"""
        await self.context_optimizer.close()
        logger.info("集成LLM管理器已关闭")
