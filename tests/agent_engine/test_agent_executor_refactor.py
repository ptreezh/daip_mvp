import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import (
    AgentState, 
    TodoItem, 
    FinalResponseEvent,
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
    TokenUsageEvent,
    ModelMetricsEvent,
    PermissionRequestEvent,
    SessionContext
)


class TestAgentExecutorRefactor:
    """AgentExecutor重构测试用例"""

    @pytest.fixture
    def mock_dependencies(self):
        """创建模拟依赖项"""
        mock_user_input_queue = asyncio.Queue()
        return {
            "session_manager": Mock(),
            "memory_service": Mock(),
            "knowledge_manager": Mock(),
            "model_provider": Mock(),
            "tool_manager": Mock(),
            "user_input_queue": mock_user_input_queue,
            "permission_manager": Mock(),
        }

    def test_agent_executor_single_responsibility(self, mock_dependencies):
        """测试AgentExecutor类符合单一职责原则"""
        # 创建AgentExecutor实例
        executor = AgentExecutor(**mock_dependencies)
        
        # 验证AgentExecutor具有明确的职责
        assert hasattr(executor, '_execute_step')
        assert hasattr(executor, '_execute_workflow')
        assert hasattr(executor, 'run')
        assert hasattr(executor, 'chat_run')
        
        # 验证没有混合不相关的职责
        # 不应该直接处理UI相关逻辑
        assert not hasattr(executor, 'render_ui')
        # 不应该直接处理数据库操作
        assert not hasattr(executor, 'save_to_database')
        # 不应该直接处理网络请求
        assert not hasattr(executor, 'make_http_request')

    def test_agent_executor_state_transitions(self, mock_dependencies):
        """测试AgentExecutor状态转换"""
        executor = AgentExecutor(**mock_dependencies)
        
        # 初始状态
        assert executor.state == AgentState.IDLE
        
        # 测试状态变更
        executor._change_state(AgentState.RUNNING)
        assert executor.state == AgentState.RUNNING
        
        executor._change_state(AgentState.THINKING)
        assert executor.state == AgentState.THINKING
        
        executor._change_state(AgentState.COMPLETED)
        assert executor.state == AgentState.COMPLETED

if __name__ == "__main__":
    pytest.main([__file__])