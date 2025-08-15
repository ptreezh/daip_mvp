#!/usr/bin/env python3
"""Personal Intelligence Hub - Transparency Monitor Tests

测试透明度监控组件功能
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from personal_intelligence_hub.components.transparency_monitor import TransparencyMonitor
from personal_intelligence_hub.models.transparency_models import (
    AgentStatus,
    AgentStatusInfo,
    LLMCall,
    MemoryOperation,
    MemoryOperationType,
    MemoryType,
    SystemStatus,
    TokenUsage,
)


class TestTransparencyMonitor:
    """透明度监控组件测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        with patch('lona.View.__init__', return_value=None):
            self.monitor = TransparencyMonitor()
            self.monitor.system_status = SystemStatus(active_agents=[])
            self.monitor.operation_logs = []
    
    def test_initialization(self):
        """测试组件初始化"""
        with patch('lona.View.__init__', return_value=None):
            monitor = TransparencyMonitor()
            assert monitor is not None
            assert isinstance(monitor.system_status, SystemStatus)
            assert monitor.system_status.active_agents == []
            assert isinstance(monitor.operation_logs, list)
            assert len(monitor.operation_logs) == 0
    
    def test_render_agent_status_all_states(self):
        """测试所有代理状态的渲染"""
        test_cases = [
            (AgentStatus.IDLE, "空闲状态"),
            (AgentStatus.THINKING, "思考状态"),
            (AgentStatus.RESPONDING, "响应状态"),
            (AgentStatus.WAITING, "等待状态")
        ]
        
        for status, description in test_cases:
            agent = AgentStatusInfo(
                agent_id=f"agent_{status.value}",
                name=f"Agent {status.value}",
                status=status,
                current_task=description,
                reasoning_framework="测试框架",
                epistemology="测试认识论"
            )
            
            html = self.monitor.render_agent_status(agent)
            
            assert html is not None
            assert hasattr(html, 'tag_name')
            assert html.tag_name == 'div'
    
    def test_render_agent_status_minimal_data(self):
        """测试最小数据的代理状态渲染"""
        minimal_agent = AgentStatusInfo(
            agent_id="minimal_agent",
            name="Minimal Agent",
            status=AgentStatus.IDLE
            # 其他字段使用默认值None
        )
        
        html = self.monitor.render_agent_status(minimal_agent)
        
        assert html is not None
        assert hasattr(html, 'tag_name')
    
    def test_render_llm_call(self):
        """测试LLM调用渲染"""
        test_call = LLMCall(
            id="call_001",
            model_id="gpt-4",
            input_tokens=150,
            output_tokens=75,
            cost=0.0035,
            latency=2.1,
            timestamp=datetime.now()
        )
        
        html = self.monitor.render_llm_call(test_call)
        
        assert html is not None
        assert hasattr(html, 'tag_name')
        assert html.tag_name == 'div'
    
    def test_render_token_usage_with_data(self):
        """测试Token使用统计渲染 - 有数据"""
        test_usage = TokenUsage(
            input_tokens=2000,
            output_tokens=1000,
            total_tokens=3000,
            estimated_cost=0.015
        )
        
        self.monitor.system_status.token_usage = test_usage
        
        html = self.monitor.render_token_usage()
        
        assert html is not None
        assert hasattr(html, 'tag_name')
    
    def test_render_token_usage_no_data(self):
        """测试Token使用统计渲染 - 无数据"""
        self.monitor.system_status.token_usage = None
        
        html = self.monitor.render_token_usage()
        
        assert html is not None
        assert hasattr(html, 'tag_name')
    
    def test_render_empty_state(self):
        """测试空状态渲染"""
        self.monitor.system_status = SystemStatus(active_agents=[])
        
        html = self.monitor.render()
        
        assert html is not None
        assert hasattr(html, 'tag_name')
        assert html.tag_name == 'div'
    
    def test_render_with_full_data(self):
        """测试完整数据的渲染"""
        # 创建完整的测试数据
        test_agent = AgentStatusInfo(
            agent_id="full_test_agent",
            name="Full Test Agent",
            status=AgentStatus.RESPONDING,
            current_task="执行复杂分析",
            reasoning_framework="多层推理",
            epistemology="批判现实主义"
        )
        
        test_call = LLMCall(
            id="full_test_call",
            model_id="gpt-4-turbo",
            input_tokens=500,
            output_tokens=250,
            cost=0.0125,
            latency=3.2,
            timestamp=datetime.now()
        )
        
        test_usage = TokenUsage(
            input_tokens=5000,
            output_tokens=2500,
            total_tokens=7500,
            estimated_cost=0.0375
        )
        
        # 设置完整系统状态
        self.monitor.system_status = SystemStatus(
            active_agents=[test_agent],
            current_workflow="multi_perspective",
            llm_calls=[test_call],
            token_usage=test_usage
        )
        
        html = self.monitor.render()
        
        assert html is not None
        assert hasattr(html, 'tag_name')
        assert html.tag_name == 'div'
    
    def test_render_multiple_agents(self):
        """测试多个代理的渲染"""
        agents = [
            AgentStatusInfo(
                agent_id=f"agent_{i}",
                name=f"Agent {i}",
                status=AgentStatus.THINKING if i % 2 == 0 else AgentStatus.RESPONDING,
                current_task=f"任务 {i}"
            )
            for i in range(5)
        ]
        
        self.monitor.system_status.active_agents = agents
        
        html = self.monitor.render()
        
        assert html is not None
        assert hasattr(html, 'tag_name')
    
    def test_render_multiple_llm_calls(self):
        """测试多个LLM调用的渲染（测试显示限制）"""
        calls = [
            LLMCall(
                id=f"call_{i}",
                model_id=f"model_{i}",
                input_tokens=100 + i * 10,
                output_tokens=50 + i * 5,
                cost=0.001 + i * 0.0005,
                latency=1.0 + i * 0.2,
                timestamp=datetime.now()
            )
            for i in range(8)  # 超过显示限制(5)的数量
        ]
        
        self.monitor.system_status.llm_calls = calls
        
        html = self.monitor.render()
        
        assert html is not None
        assert hasattr(html, 'tag_name')


class TestTransparencyModels:
    """透明度相关数据模型测试"""
    
    def test_agent_status_info_creation(self):
        """测试代理状态信息创建"""
        agent = AgentStatusInfo(
            agent_id="test_agent",
            name="Test Agent",
            status=AgentStatus.THINKING,
            current_task="测试任务",
            reasoning_framework="测试框架",
            epistemology="测试认识论"
        )
        
        assert agent.agent_id == "test_agent"
        assert agent.name == "Test Agent"
        assert agent.status == AgentStatus.THINKING
        assert agent.current_task == "测试任务"
        assert agent.reasoning_framework == "测试框架"
        assert agent.epistemology == "测试认识论"
    
    def test_llm_call_creation(self):
        """测试LLM调用记录创建"""
        timestamp = datetime.now()
        call = LLMCall(
            id="test_call",
            model_id="gpt-4",
            input_tokens=200,
            output_tokens=100,
            cost=0.005,
            latency=1.8,
            timestamp=timestamp
        )
        
        assert call.id == "test_call"
        assert call.model_id == "gpt-4"
        assert call.input_tokens == 200
        assert call.output_tokens == 100
        assert call.cost == 0.005
        assert call.latency == 1.8
        assert call.timestamp == timestamp
    
    def test_memory_operation_creation(self):
        """测试记忆操作记录创建"""
        operation = MemoryOperation(
            operation_type=MemoryOperationType.RETRIEVE,
            agent_id="test_agent",
            memory_type=MemoryType.EPISODIC,
            item_count=10
        )
        
        assert operation.operation_type == MemoryOperationType.RETRIEVE
        assert operation.agent_id == "test_agent"
        assert operation.memory_type == MemoryType.EPISODIC
        assert operation.item_count == 10
        assert operation.timestamp is not None
    
    def test_token_usage_creation(self):
        """测试Token使用统计创建"""
        usage = TokenUsage(
            input_tokens=1500,
            output_tokens=750,
            total_tokens=2250,
            estimated_cost=0.01125
        )
        
        assert usage.input_tokens == 1500
        assert usage.output_tokens == 750
        assert usage.total_tokens == 2250
        assert usage.estimated_cost == 0.01125
        assert usage.timestamp is not None
    
    def test_system_status_creation(self):
        """测试系统状态创建"""
        agent = AgentStatusInfo(
            agent_id="status_test_agent",
            name="Status Test Agent",
            status=AgentStatus.IDLE
        )
        
        status = SystemStatus(
            active_agents=[agent],
            current_workflow="test_workflow"
        )
        
        assert len(status.active_agents) == 1
        assert status.active_agents[0].name == "Status Test Agent"
        assert status.current_workflow == "test_workflow"
        assert isinstance(status.memory_operations, list)
        assert isinstance(status.llm_calls, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
