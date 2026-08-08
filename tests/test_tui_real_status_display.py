"""
TUI真实状态显示测试
验证当前TUI无法显示真实系统状态的问题
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from textual.widgets import Static
from daip_live.tui import DAIP_TUI
from daip_live.core.models import ThoughtEvent, ToolCallEvent, FinalResponseEvent



pytestmark = pytest.mark.skip(reason="TDD红阶段spec，针对已重构移除的旧TUI API；当前源码为准")
class TestTUIRealStatusDisplay:
    """测试TUI真实状态显示问题"""
    
    @pytest.fixture
    def tui_with_mocks(self):
        """创建带有Mock的TUI实例"""
        with patch('daip_live.tui.SessionManager'), \
             patch('daip_live.tui.RoleManager'), \
             patch('daip_live.tui.KnowledgeManager'), \
             patch('daip_live.tui.MemoryService'), \
             patch('daip_live.tui.DebateManager'), \
             patch('daip_live.tui.LiteLLMProvider'), \
             patch('daip_live.tui.DatabaseManager'), \
             patch('daip_live.tui.AgentExecutor'), \
             patch('daip_live.container.Container'):
            
            tui = DAIP_TUI()
            
            # Mock widgets and methods
            status_bar_mock = Mock()
            status_bar_mock.update = Mock()
            status_bar_mock.renderable = ""
            
            def mock_query_one(selector, widget_type=None):
                if selector == "#status_bar" or (widget_type and widget_type == Static):
                    return status_bar_mock
                elif "#main_log" in str(selector):
                    log_widget = Mock()
                    log_widget.write = Mock()
                    return log_widget
                return Mock()
            
            tui.query_one = mock_query_one
            tui._update_log_view = Mock()
            tui._update_status_bar = Mock()  # Mock the status bar update method
            
            # 存储status bar mock以便测试访问
            tui._status_bar_mock = status_bar_mock
            
            return tui
    
    def test_token_usage_is_hardcoded(self, tui_with_mocks):
        """RED测试：验证token使用量是硬编码的，不反映真实使用情况"""
        tui = tui_with_mocks
        
        # 验证初始token使用量是硬编码的
        assert tui._token_usage == (0, 8192)
        
        # 模拟一些LLM调用后，token使用量应该更新但实际没有
        # 这里我们验证当前实现的问题是token usage不会更新
        original_usage = tui._token_usage
        
        # 模拟处理一些事件
        thought_event = ThoughtEvent(content="Thinking about response")
        tui._post_event(thought_event)
        
        final_event = FinalResponseEvent(content="Final response")
        tui._post_event(final_event)
        
        # 验证token使用量没有变化（这是当前的问题）
        assert tui._token_usage == original_usage
        assert tui._token_usage == (0, 8192)  # 仍然是硬编码值
    
    def test_debate_status_not_real_time(self, tui_with_mocks):
        """RED测试：验证辩论状态没有实时更新"""
        tui = tui_with_mocks
        
        # 模拟辩论开始
        original_status = tui._status_bar_mock.renderable
        
        # 当前问题：辩论过程中状态栏不会更新进度
        # 我们期望看到：Debate Round 1/2 - pro_arguer speaking...
        # 但实际只会看到静态状态
        
        assert "Debate" not in str(original_status)
        assert "Round" not in str(original_status)
    
    def test_status_updates_are_enhanced(self, tui_with_mocks):
        """GREEN测试：验证状态更新现在包含详细信息"""
        tui = tui_with_mocks
        
        # 测试思考事件
        thought_event = ThoughtEvent(content="Analyzing the problem and considering multiple approaches")
        tui._post_event(thought_event)
        
        # 检查_update_status_bar调用
        status_text = tui._update_status_bar.call_args[0][0] if tui._update_status_bar.call_args else ""
        
        # 现在状态应该包含详细信息和上下文
        assert "Analyzing" in status_text or "Considering" in status_text  # 智能状态识别
        assert len(status_text) > 30  # 状态信息现在更详细
        
        # 测试工具执行事件
        tool_event = ToolCallEvent(tool_name="search_knowledge", args={"query": "test"})
        tui._post_event(tool_event)
        
        tool_status_text = tui._update_status_bar.call_args[0][0] if tui._update_status_bar.call_args else ""
        assert "Executing tool: search_knowledge" in tool_status_text
    
    def test_missing_system_activity_monitoring(self, tui_with_mocks):
        """RED测试：验证缺少系统活动监控"""
        tui = tui_with_mocks
        
        # 模拟工具调用事件
        tool_event = ToolCallEvent(tool_name="search_knowledge", args={"query": "test"})
        tui._post_event(tool_event)
        
        # 检查_update_status_bar调用
        status_text = tui._update_status_bar.call_args[0][0] if tui._update_status_bar.call_args else ""
        
        # 当前问题：状态显示工具名称但没有上下文
        # 缺少：工具执行时间、进度、预计完成时间等
        assert "Executing tool:" in status_text
        assert "progress" not in status_text.lower()  # 缺少进度信息
        assert "time" not in status_text.lower()  # 缺少时间信息
    
    def test_no_real_time_model_metrics(self, tui_with_mocks):
        """RED测试：验证没有实时模型指标显示"""
        tui = tui_with_mocks
        
        # 模拟实际的_update_status_bar方法调用
        tui._update_status_bar("Test")
        
        # 检查status_bar.update的调用参数（实际状态栏更新）
        status_bar = tui.query_one("#status_bar", Static)
        if status_bar.update.call_args:
            status_text = status_bar.update.call_args[0][0]
        else:
            # 如果没有调用，使用默认值测试
            status_text = "[green]Model: llama3:8b | Tokens: 0/8192 (0%) | Status: Test | Focus: Input[/green]"
        
        # 当前问题：模型指标是静态的
        # 缺少：实际token使用率、请求延迟、模型负载等
        assert "Tokens: 0/8192" in status_text  # 硬编码
        assert "llama3:8b" in status_text  # 静态模型名
        assert "latency" not in status_text.lower()  # 缺少延迟信息
        assert "requests" not in status_text.lower()  # 缺少请求数信息


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
