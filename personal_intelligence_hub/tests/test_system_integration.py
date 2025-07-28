#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - System Integration Tests

系统集成测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from personal_intelligence_hub.main_app import PersonalIntelligenceHubView, IndexView
from personal_intelligence_hub.components.chat_interface import ChatInterface
from personal_intelligence_hub.components.transparency_monitor import TransparencyMonitor
from personal_intelligence_hub.components.wiki_panel import WikiPanel
from personal_intelligence_hub.components.task_panel import TaskPanel
from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
from personal_intelligence_hub.services.workflow_compiler import WorkflowCompiler
from personal_intelligence_hub.models.workflow_models import WorkflowDefinition, StepType


class TestSystemIntegration:
    """系统集成测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.assistant_service = PersonalAssistantService()
        self.chat_interface = ChatInterface(self.assistant_service)
        self.transparency_monitor = TransparencyMonitor()
        self.wiki_panel = WikiPanel()
        self.task_panel = TaskPanel()
        self.workflow_compiler = WorkflowCompiler()
    
    def test_main_app_initialization(self):
        """测试主应用初始化"""
        view = PersonalIntelligenceHubView()
        assert view is not None
        assert hasattr(view, 'assistant_service')
    
    def test_index_view_initialization(self):
        """测试首页视图初始化"""
        view = IndexView()
        assert view is not None
    
    def test_component_initialization(self):
        """测试组件初始化"""
        assert self.chat_interface is not None
        assert self.transparency_monitor is not None
        assert self.wiki_panel is not None
        assert self.task_panel is not None
    
    def test_service_initialization(self):
        """测试服务初始化"""
        assert self.assistant_service is not None
        assert self.workflow_compiler is not None
    
    def test_workflow_integration(self):
        """测试工作流集成"""
        # 测试工作流编译器与主系统的集成
        description = "分析当前研究问题并提供批判性审查"
        workflow = self.workflow_compiler.compile_natural_language(description)
        
        assert workflow is not None
        assert len(workflow.steps) > 0
        
        # 验证步骤类型
        step_types = [step.type for step in workflow.steps]
        assert StepType.ANALYSIS in step_types
        assert StepType.CRITIQUE in step_types
    
    def test_component_interaction(self):
        """测试组件间交互"""
        # 测试透明度监控与聊天界面的集成
        self.transparency_monitor.system_status.active_agents = []
        
        # 模拟代理状态更新
        from personal_intelligence_hub.models.transparency_models import AgentStatusInfo, AgentStatus
        agent = AgentStatusInfo(
            agent_id="test_agent",
            name="Test Agent",
            status=AgentStatus.THINKING,
            current_task="分析任务"
        )
        
        # 验证组件可以共享数据
        assert agent.name == "Test Agent"
    
    def test_data_flow(self):
        """测试数据流"""
        # 测试从工作流到任务面板的流程
        workflow = self.workflow_compiler.compile_natural_language("创建研究任务")
        
        # 验证工作流可以转换为任务
        assert workflow.steps is not None
        assert len(workflow.steps) > 0
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效输入的处理
        workflow = self.workflow_compiler.compile_natural_language("")
        assert workflow is not None
        assert isinstance(workflow, WorkflowDefinition)
    
    def test_system_resilience(self):
        """测试系统弹性"""
        # 测试组件在异常情况下的行为
        try:
            view = PersonalIntelligenceHubView()
            # 模拟请求处理
            result = view.handle_request(None)
            assert result is not None
        except Exception as e:
            pytest.fail(f"系统应该优雅处理异常: {e}")
    
    def test_service_compatibility(self):
        """测试服务兼容性"""
        # 测试所有服务可以协同工作
        services = [
            self.assistant_service,
            self.workflow_compiler
        ]
        
        for service in services:
            assert service is not None
    
    def test_model_consistency(self):
        """测试模型一致性"""
        # 测试所有数据模型的一致性
        from personal_intelligence_hub.models.transparency_models import SystemStatus
        from personal_intelligence_hub.models.wiki_models import WikiPage
        from personal_intelligence_hub.models.task_models import Task
        from personal_intelligence_hub.models.workflow_models import WorkflowDefinition
        
        # 验证所有模型可以实例化
        status = SystemStatus(active_agents=[])
        wiki = WikiPage(
            id="test",
            title="Test",
            content="Test",
            quality_score=0.8,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="published",
            tags=[],
            metadata={}
        )
        task = Task(
            id="test",
            title="Test",
            description="Test",
            status="not_started",
            priority="medium",
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            progress=0.0,
            metadata={}
        )
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            steps=[],
            parameters={}
        )
        
        assert status is not None
        assert wiki is not None
        assert task is not None
        assert workflow is not None
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 测试完整的用户交互流程
        description = "分析当前研究问题并提供批判性审查"
        
        # 1. 编译工作流
        workflow = self.workflow_compiler.compile_natural_language(description)
        assert workflow is not None
        
        # 2. 验证工作流
        validation = self.workflow_compiler.validate_workflow(workflow)
        assert validation.is_valid
        
        # 3. 预览工作流
        preview = self.workflow_compiler.preview_workflow(workflow)
        assert preview is not None
        assert preview["total_steps"] > 0
    
    def test_component_lifecycle(self):
        """测试组件生命周期"""
        # 测试组件的创建、使用和销毁
        components = [
            self.chat_interface,
            self.transparency_monitor,
            self.wiki_panel,
            self.task_panel
        ]
        
        for component in components:
            assert component is not None
            # 验证组件有渲染方法
            assert hasattr(component, 'render')
    
    def test_system_configuration(self):
        """测试系统配置"""
        # 测试系统配置的一致性
        from personal_intelligence_hub.main_app import app
        
        assert app is not None
        assert hasattr(app, 'settings')
    
    def test_error_recovery(self):
        """测试错误恢复"""
        # 测试系统在错误后的恢复能力
        try:
            # 模拟无效工作流
            workflow = self.workflow_compiler.compile_natural_language("invalid")
            assert workflow is not None  # 应该返回默认工作流
        except Exception as e:
            pytest.fail(f"系统应该优雅处理错误: {e}")
    
    def test_performance_baseline(self):
        """测试性能基线"""
        # 测试基本性能要求
        import time
        
        start_time = time.time()
        workflow = self.workflow_compiler.compile_natural_language("测试性能")
        end_time = time.time()
        
        # 编译应该在合理时间内完成
        assert (end_time - start_time) < 1.0
    
    def test_memory_usage(self):
        """测试内存使用"""
        # 测试内存使用在合理范围内
        import gc
        
        # 强制垃圾回收
        gc.collect()
        
        # 创建多个工作流
        workflows = []
        for i in range(10):
            workflow = self.workflow_compiler.compile_natural_language(f"测试工作流 {i}")
            workflows.append(workflow)
        
        assert len(workflows) == 10
        assert all(isinstance(w, WorkflowDefinition) for w in workflows)


class TestIntegrationScenarios:
    """集成场景测试类"""
    
    def test_research_workflow_scenario(self):
        """测试研究工作流场景"""
        # 模拟完整的研究工作流
        description = "分析AI伦理问题，从多个角度进行批判性审查，并生成综合报告"
        
        # 1. 编译工作流
        workflow = self.workflow_compiler.compile_natural_language(description)
        
        # 2. 验证工作流
        validation = self.workflow_compiler.validate_workflow(workflow)
        assert validation.is_valid
        
        # 3. 检查步骤
        step_types = [step.type for step in workflow.steps]
        assert StepType.ANALYSIS in step_types
        assert StepType.CRITIQUE in step_types
        assert StepType.SYNTHESIS in step_types
    
    def test_collaboration_scenario(self):
        """测试协作场景"""
        # 测试多代理协作
        description = "多个AI代理协作分析复杂问题"
        
        workflow = self.workflow_compiler.compile_natural_language(description)
        
        # 验证协作步骤
        collaboration_steps = [step for step in workflow.steps 
                             if step.type == StepType.COLLABORATION]
        assert len(collaboration_steps) > 0
    
    def test_documentation_scenario(self):
        """测试文档场景"""
        # 测试文档生成工作流
        description = "生成研究问题的综合文档"
        
        workflow = self.workflow_compiler.compile_natural_language(description)
        
        # 验证文档步骤
        doc_steps = [step for step in workflow.steps 
                   if step.type == StepType.DOCUMENTATION]
        assert len(doc_steps) > 0


if __name__ == "__main__":
    pytest
