#!/usr/bin/env python3
"""
工作流智能选择器

基于用户输入和意图分析，智能选择最适合的辩论场景和工作流。
支持学术研究、专家咨询、轻松讨论三大场景的自动识别和选择。
"""

import logging
from typing import Any, Optional

from src.core_services.llm_based_workflow_selector import (
    LLMIntentResult,
    get_llm_workflow_selector
)

logger = logging.getLogger(__name__)


class WorkflowSelector:
    """工作流选择器 - 基于真实LLM实现"""
    
    def __init__(self):
        """初始化工作流选择器"""
        # 使用现有的LLM-based工作流选择器
        self.llm_selector = get_llm_workflow_selector()
        logger.info("WorkflowSelector initialized with real LLM implementation")
    
    async def select_workflow(
        self, 
        user_input: str, 
        context: Optional[dict[str, Any]] = None
    ) -> LLMIntentResult:
        """选择最合适的工作流和场景
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            LLMIntentResult: 包含工作流类型、场景类型、置信度等信息的分析结果
        """
        try:
            # 使用真实的LLM进行意图分析和工作流选择
            result = await self.llm_selector.analyze_intent_with_llm(user_input, context)
            
            # 记录选择结果用于优化
            if result.workflow_type and result.scenario_type:
                logger.info(
                    f"Selected workflow: {result.workflow_type.value} "
                    f"for scenario: {result.scenario_type.value} "
                    f"(confidence: {result.confidence:.2f})"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to select workflow: {e}")
            # 返回默认选择作为降级策略
            from src.core_services.llm_based_workflow_selector import WorkflowType, ScenarioType
            return LLMIntentResult(
                workflow_type=WorkflowType.MULTI_PERSPECTIVE,
                scenario_type=ScenarioType.CASUAL_DISCUSSION,
                confidence=0.5,
                reasoning=f"降级策略：工作流选择失败 ({str(e)})",
                topic=user_input[:50] if user_input else "",
                semantic_analysis={"error": str(e)}
            )
    
    def get_workflow_statistics(self) -> dict[str, Any]:
        """获取工作流使用统计信息
        
        Returns:
            dict: 工作流使用统计信息
        """
        return self.llm_selector.get_workflow_statistics()


# 全局实例
_workflow_selector = None


def get_workflow_selector() -> WorkflowSelector:
    """获取工作流选择器的全局实例
    
    Returns:
        WorkflowSelector: 工作流选择器实例
    """
    global _workflow_selector
    if _workflow_selector is None:
        _workflow_selector = WorkflowSelector()
    return _workflow_selector