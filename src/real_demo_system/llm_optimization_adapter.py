#!/usr/bin/env python3
"""LLM优化适配器

将智能上下文优化集成到现有的真实演示系统中
"""

import logging
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from ..core_services.integrated_llm_manager import IntegratedLLMManager

logger = logging.getLogger(__name__)


class LLMOptimizationAdapter:
    """LLM优化适配器"""

    def __init__(self):
        """初始化适配器"""
        self.llm_manager = IntegratedLLMManager()
        self.is_initialized = False

    async def initialize(self):
        """初始化适配器"""
        if not self.is_initialized:
            await self.llm_manager.initialize()
            self.is_initialized = True
            logger.info("LLM优化适配器初始化完成")

    async def optimize_role_response(
        self,
        role_id: str,
        user_input: str,
        context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """为角色响应提供优化（适配现有接口）"""
        if not self.is_initialized:
            await self.initialize()

        # 提取任务上下文
        task_context = None
        additional_context = {}

        if context:
            task_context = context.get("current_task") or context.get("scenario")
            additional_context = {
                "scenario_context": context.get("scenario_context", {}),
                "debate_context": context.get("debate_context", {}),
                "workflow_context": context.get("workflow_context", {}),
                "user_context": context.get("user_context", {})
            }

        # 调用集成LLM管理器
        result = await self.llm_manager.call_llm_for_role(
            role_id=role_id,
            user_input=user_input,
            task_context=task_context,
            additional_context=additional_context
        )

        # 适配返回格式以兼容现有系统
        return {
            "role_id": role_id,
            "role_name": result.get("role_name", role_id),
            "response": result["response"],
            "optimization_applied": result.get("optimization_applied", False),
            "optimization_metrics": result.get("optimization_metrics", {}),
            "metadata": result.get("call_metadata", {}),
            "timestamp": datetime.now().isoformat()
        }

    async def optimize_multi_role_debate(
        self,
        roles: list[str],
        topic: str,
        context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """优化多角色辩论（适配现有接口）"""
        if not self.is_initialized:
            await self.initialize()

        # 构建辩论上下文
        debate_context = {
            "history": context.get("debate_history", []) if context else [],
            "positions": context.get("role_positions", {}) if context else {},
            "rules": context.get("debate_rules", []) if context else [],
            "round_info": context.get("round_info", {}) if context else {}
        }

        round_number = context.get("round_number", 1) if context else 1

        # 调用集成LLM管理器
        result = await self.llm_manager.call_llm_for_multi_role_debate(
            participating_roles=roles,
            debate_topic=topic,
            debate_context=debate_context,
            round_number=round_number
        )

        # 适配返回格式
        adapted_responses = {}
        for role_id, role_result in result["role_responses"].items():
            if "error" not in role_result:
                adapted_responses[role_id] = {
                    "role_id": role_id,
                    "role_name": role_result.get("role_name", role_id),
                    "response": role_result["response"],
                    "optimization_applied": role_result.get("optimization_applied", False),
                    "optimization_metrics": role_result.get("optimization_metrics", {}),
                    "metadata": role_result.get("call_metadata", {})
                }
            else:
                adapted_responses[role_id] = {
                    "role_id": role_id,
                    "error": role_result["error"],
                    "optimization_applied": False
                }

        return {
            "debate_topic": topic,
            "round_number": round_number,
            "participating_roles": roles,
            "responses": adapted_responses,
            "optimization_summary": result.get("optimization_summary", {}),
            "timestamp": result.get("debate_timestamp")
        }
<<<<<<< HEAD

    async def get_optimization_analytics(self, role_id: Optional[str] = None) -> Dict[str, Any]:
=======
    
    async def get_optimization_analytics(self, role_id: Optional[str] = None) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取优化分析（适配现有接口）"""
        if not self.is_initialized:
            await self.initialize()

        if role_id:
            # 获取特定角色的分析
            return await self.llm_manager.get_role_performance_analytics(role_id)
        else:
            # 获取系统级分析
            return await self.llm_manager.get_system_wide_analytics()

    async def close(self):
        """关闭适配器"""
        if self.is_initialized:
            await self.llm_manager.close()
            self.is_initialized = False


# 全局适配器实例
_global_adapter = None

async def get_llm_optimization_adapter() -> LLMOptimizationAdapter:
    """获取全局LLM优化适配器实例"""
    global _global_adapter

    if _global_adapter is None:
        _global_adapter = LLMOptimizationAdapter()
        await _global_adapter.initialize()

    return _global_adapter

async def optimize_role_llm_call(
    role_id: str,
    user_input: str,
    context: dict[str, Any] = None
) -> dict[str, Any]:
    """便捷函数：优化角色LLM调用"""
    adapter = await get_llm_optimization_adapter()
    return await adapter.optimize_role_response(role_id, user_input, context)

async def optimize_debate_llm_calls(
    roles: list[str],
    topic: str,
    context: dict[str, Any] = None
) -> dict[str, Any]:
    """便捷函数：优化辩论LLM调用"""
    adapter = await get_llm_optimization_adapter()
    return await adapter.optimize_multi_role_debate(roles, topic, context)

async def get_llm_optimization_stats(role_id: Optional[str] = None) -> dict[str, Any]:
    """便捷函数：获取LLM优化统计"""
    adapter = await get_llm_optimization_adapter()
    return await adapter.get_optimization_analytics(role_id)
