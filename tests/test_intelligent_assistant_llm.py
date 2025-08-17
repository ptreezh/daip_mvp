#!/usr/bin/env python3
"""测试智能助手的LLM集成

按照TDD方法，先编写测试用例，然后实现功能
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.intelligent_assistant_app import IntelligentAssistant
from src.core_services.role_manager import Role

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_role():
    """创建一个模拟角色"""
    return Role(
        id="test_role_001",
        name="测试角色",
        description="用于测试的角色",
        system_prompt="你是一个测试角色",
        capabilities=["test"]
    )


@pytest.fixture
def assistant_with_mocked_llm():
    """创建一个带有模拟LLM管理器的智能助手实例"""
    assistant = IntelligentAssistant()
    
    # 创建模拟的LLM管理器
    mock_llm_manager = MagicMock()
    mock_generate_response = AsyncMock()
    mock_llm_manager.generate_response = mock_generate_response
    assistant.llm_manager = mock_llm_manager
    
    return assistant, mock_llm_manager


@pytest.mark.asyncio
async def test_call_llm_for_role_success(assistant_with_mocked_llm, mock_role):
    """测试成功调用LLM的情况"""
    assistant, mock_llm_manager = assistant_with_mocked_llm
    
    # 设置模拟返回值
    expected_response = "这是一个来自LLM的真实响应"
    future = asyncio.Future()
    future.set_result({
        "response": expected_response,
        "role_id": mock_role.id,
        "role_name": mock_role.name
    })
    mock_llm_manager.call_llm_for_role.return_value = future
    
    # 调用被测试的方法
    result = await assistant._call_llm_for_role(mock_role, "测试提示词")
    
    # 验证结果
    assert result == expected_response
    
    # 验证LLM管理器被正确调用
    mock_llm_manager.call_llm_for_role.assert_called_once_with(
        role_id=mock_role.id,
        user_input="测试提示词",
        task_context=None,
        additional_context=None
    )


@pytest.mark.asyncio
async def test_call_llm_for_role_failure(assistant_with_mocked_llm, mock_role):
    """测试LLM调用失败的情况"""
    assistant, mock_llm_manager = assistant_with_mocked_llm
    
    # 设置模拟异常
    future = asyncio.Future()
    future.set_exception(Exception("LLM服务不可用"))
    mock_llm_manager.call_llm_for_role.return_value = future
    
    # 捕获日志
    with patch('src.intelligent_assistant_app.logger') as mock_logger:
        # 调用被测试的方法
        result = await assistant._call_llm_for_role(mock_role, "测试提示词")
        
        # 验证返回了回退响应
        assert f"作为{mock_role.name}，我正在分析这个问题，但遇到了一些技术困难。" in result
        
        # 验证记录了错误日志
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_call_llm_for_role_empty_response(assistant_with_mocked_llm, mock_role):
    """测试LLM返回空响应的情况"""
    assistant, mock_llm_manager = assistant_with_mocked_llm
    
    # 设置模拟返回空值
    future = asyncio.Future()
    future.set_result({
        "response": "",
        "role_id": mock_role.id,
        "role_name": mock_role.name
    })
    mock_llm_manager.call_llm_for_role.return_value = future
    
    # 调用被测试的方法
    result = await assistant._call_llm_for_role(mock_role, "测试提示词")
    
    # 验证返回了回退响应
    assert f"作为{mock_role.name}，我认为这个问题需要从专业角度深入分析。" in result or \
           "分析这个问题，但遇到了一些技术困难" in result