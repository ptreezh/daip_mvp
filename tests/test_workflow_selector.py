#!/usr/bin/env python3
"""
测试工作流选择器
"""

import asyncio
import logging
from unittest.mock import AsyncMock, patch

import pytest

from src.scenario_engine.workflow_selector import WorkflowSelector, get_workflow_selector
from src.core_services.llm_based_workflow_selector import LLMIntentResult, WorkflowType, ScenarioType

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def workflow_selector():
    """创建工作流选择器实例"""
    return WorkflowSelector()


@pytest.fixture
def mock_llm_result():
    """创建模拟的LLM结果"""
    return LLMIntentResult(
        workflow_type=WorkflowType.MULTI_PERSPECTIVE,
        scenario_type=ScenarioType.ACADEMIC_RESEARCH,
        confidence=0.95,
        reasoning="基于语义分析，用户输入涉及学术研究主题",
        topic="AI在教育中的应用",
        semantic_analysis={
            "intent": "研究探讨",
            "complexity": "high",
            "domain": "education",
            "tone": "学术性"
        }
    )


@pytest.mark.asyncio
async def test_select_workflow_success(workflow_selector, mock_llm_result):
    """测试成功选择工作流的情况"""
    # 模拟LLM选择器的返回值
    with patch.object(workflow_selector.llm_selector, 'analyze_intent_with_llm', new=AsyncMock(return_value=mock_llm_result)):
        # 调用被测试的方法
        result = await workflow_selector.select_workflow("请分析AI在教育中的应用前景")
        
        # 验证结果
        assert result.workflow_type == WorkflowType.MULTI_PERSPECTIVE
        assert result.scenario_type == ScenarioType.ACADEMIC_RESEARCH
        assert result.confidence == 0.95
        assert result.topic == "AI在教育中的应用"


@pytest.mark.asyncio
async def test_select_workflow_failure(workflow_selector):
    """测试工作流选择失败的情况"""
    # 模拟LLM选择器抛出异常
    with patch.object(workflow_selector.llm_selector, 'analyze_intent_with_llm', new=AsyncMock(side_effect=Exception("LLM服务不可用"))):
        # 调用被测试的方法
        result = await workflow_selector.select_workflow("请分析AI在教育中的应用前景")
        
        # 验证返回了降级结果
        assert result.workflow_type == WorkflowType.MULTI_PERSPECTIVE
        assert result.scenario_type == ScenarioType.CASUAL_DISCUSSION
        assert result.confidence == 0.5
        assert "降级策略" in result.reasoning


@pytest.mark.asyncio
async def test_select_workflow_with_context(workflow_selector, mock_llm_result):
    """测试带上下文的工作流选择"""
    context = {
        "previous_topic": "教育技术",
        "user_preferences": {"preferred_scenario": "academic_research"},
        "session_history": ["讨论在线学习平台"]
    }
    
    # 模拟LLM选择器的返回值
    with patch.object(workflow_selector.llm_selector, 'analyze_intent_with_llm', new=AsyncMock(return_value=mock_llm_result)):
        # 调用被测试的方法
        result = await workflow_selector.select_workflow("请分析AI在教育中的应用前景", context)
        
        # 验证结果
        assert result.workflow_type == WorkflowType.MULTI_PERSPECTIVE
        assert result.scenario_type == ScenarioType.ACADEMIC_RESEARCH
        assert result.topic == "AI在教育中的应用"


def test_get_workflow_selector():
    """测试获取工作流选择器全局实例"""
    # 获取实例
    selector1 = get_workflow_selector()
    selector2 = get_workflow_selector()
    
    # 验证是同一个实例
    assert selector1 is selector2
    assert isinstance(selector1, WorkflowSelector)


def test_get_workflow_statistics(workflow_selector):
    """测试获取工作流统计信息"""
    # 调用方法
    stats = workflow_selector.get_workflow_statistics()
    
    # 验证返回了统计信息
    assert isinstance(stats, dict)
    assert "total_workflows" in stats
    assert "workflow_types" in stats
    assert "scenario_coverage" in stats