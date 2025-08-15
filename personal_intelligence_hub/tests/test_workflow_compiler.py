#!/usr/bin/env python3
"""Personal Intelligence Hub - Workflow Compiler Tests

测试自然语言工作流编译器功能
"""


import pytest

from personal_intelligence_hub.models.workflow_models import (
    StepType,
    WorkflowDefinition,
    WorkflowStep,
)
from personal_intelligence_hub.services.workflow_compiler import WorkflowCompiler


class TestWorkflowCompiler:
    """工作流编译器测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.compiler = WorkflowCompiler()
    
    def test_initialization(self):
        """测试编译器初始化"""
        assert self.compiler is not None
        assert hasattr(self.compiler, 'institutional_primitives')
        assert hasattr(self.compiler, 'workflow_patterns')
    
    def test_compile_natural_language_simple(self):
        """测试简单自然语言编译"""
        description = "请分析这个研究问题"
        workflow = self.compiler.compile_natural_language(description)
        
        assert workflow is not None
        assert isinstance(workflow, WorkflowDefinition)
        assert len(workflow.steps) > 0
    
    def test_compile_natural_language_critical_review(self):
        """测试批判性审查模式"""
        description = "对这个论文进行批判性审查"
        workflow = self.compiler.compile_natural_language(description)
        
        assert workflow is not None
        assert len(workflow.steps) >= 3
        assert any(step.type == StepType.CRITIQUE for step in workflow.steps)
    
    def test_compile_natural_language_multi_perspective(self):
        """测试多视角模式"""
        description = "从多个角度分析这个问题"
        workflow = self.compiler.compile_natural_language(description)
        
        assert workflow is not None
        assert any(step.type == StepType.COLLABORATION for step in workflow.steps)
    
    def test_compile_natural_language_iterative(self):
        """测试迭代改进模式"""
        description = "通过迭代改进这个方案"
        workflow = self.compiler.compile_natural_language(description)
        
        assert workflow is not None
        assert any(step.type == StepType.ITERATION for step in workflow.steps)
    
    def test_detect_pattern(self):
        """测试模式检测"""
        # 测试批判性审查模式
        pattern = self.compiler._detect_pattern("critical review of the topic")
        assert pattern == "critical_review"
        
        # 测试多视角模式
        pattern = self.compiler._detect_pattern("multiple perspectives analysis")
        assert pattern == "multi_perspective"
        
        # 测试迭代模式
        pattern = self.compiler._detect_pattern("iterative improvement")
        assert pattern == "iterative_improvement"
        
        # 测试默认模式
        pattern = self.compiler._detect_pattern("simple analysis")
        assert pattern == "critical_review"
    
    def test_extract_steps(self):
        """测试步骤提取"""
        steps = self.compiler._extract_steps("test description", "critical_review")
        
        assert len(steps) > 0
        assert all(isinstance(step, WorkflowStep) for step in steps)
        assert steps[0].dependencies == []
    
    def test_get_step_type(self):
        """测试获取步骤类型"""
        assert self.compiler._get_step_type("analyze") == StepType.ANALYSIS
        assert self.compiler._get_step_type("synthesize") == StepType.SYNTHESIS
        assert self.compiler._get_step_type("critique") == StepType.CRITIQUE
        assert self.compiler._get_step_type("unknown") == StepType.ANALYSIS
    
    def test_get_agent_roles_for_step(self):
        """测试获取代理角色"""
        roles = self.compiler._get_agent_roles_for_step("analyze")
        assert "Analyst-AI" in roles
        
        roles = self.compiler._get_agent_roles_for_step("critique")
        assert "Critic-AI" in roles
        
        roles = self.compiler._get_agent_roles_for_step("unknown")
        assert "General-AI" in roles
    
    def test_get_validation_criteria(self):
        """测试获取验证标准"""
        criteria = self.compiler._get_validation_criteria("analyze")
        assert "completeness" in criteria
        
        criteria = self.compiler._get_validation_criteria("validate")
        assert "correctness" in criteria
    
    def test_generate_workflow_name(self):
        """测试生成工作流名称"""
        name = self.compiler._generate_workflow_name("Test workflow description")
        assert name.startswith("workflow_")
        assert "test" in name.lower()
    
    def test_create_default_workflow(self):
        """测试创建默认工作流"""
        workflow = self.compiler._create_default_workflow("Test description")
        
        assert workflow is not None
        assert isinstance(workflow, WorkflowDefinition)
        assert len(workflow.steps) == 3
        assert workflow.steps[0].type == StepType.ANALYSIS
    
    def test_validate_workflow_valid(self):
        """测试验证有效工作流"""
        steps = [
            WorkflowStep(
                id="step1",
                name="Step 1",
                type=StepType.ANALYSIS,
                description="First step",
                agent_roles=["Analyst-AI"],
                dependencies=[],
                parameters={},
                validation_criteria={}
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                type=StepType.SYNTHESIS,
                description="Second step",
                agent_roles=["Synthesizer-AI"],
                dependencies=["step1"],
                parameters={},
                validation_criteria={}
            )
        ]
        
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="Test description",
            steps=steps,
            parameters={}
        )
        
        result = self.compiler.validate_workflow(workflow)
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_validate_workflow_invalid(self):
        """测试验证无效工作流"""
        steps = [
            WorkflowStep(
                id="step1",
                name="Step 1",
                type=StepType.ANALYSIS,
                description="First step",
                agent_roles=["Analyst-AI"],
                dependencies=["step2"],  # 循环依赖
                parameters={},
                validation_criteria={}
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                type=StepType.SYNTHESIS,
                description="Second step",
                agent_roles=["Synthesizer-AI"],
                dependencies=["step1"],  # 循环依赖
                parameters={},
                validation_criteria={}
            )
        ]
        
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="Test description",
            steps=steps,
            parameters={}
        )
        
        result = self.compiler.validate_workflow(workflow)
        
        assert not result.is_valid
        assert len(result.issues) > 0
    
    def test_has_circular_dependency(self):
        """测试循环依赖检测"""
        steps = [
            WorkflowStep(
                id="step1",
                name="Step 1",
                type=StepType.ANALYSIS,
                description="First step",
                agent_roles=["Analyst-AI"],
                dependencies=["step2"],
                parameters={},
                validation_criteria={}
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                type=StepType.SYNTHESIS,
                description="Second step",
                agent_roles=["Synthesizer-AI"],
                dependencies=["step1"],
                parameters={},
                validation_criteria={}
            )
        ]
        
        has_cycle = self.compiler._has_circular_dependency(steps)
        assert has_cycle
    
    def test_no_circular_dependency(self):
        """测试无循环依赖"""
        steps = [
            WorkflowStep(
                id="step1",
                name="Step 1",
                type=StepType.ANALYSIS,
                description="First step",
                agent_roles=["Analyst-AI"],
                dependencies=[],
                parameters={},
                validation_criteria={}
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                type=StepType.SYNTHESIS,
                description="Second step",
                agent_roles=["Synthesizer-AI"],
                dependencies=["step1"],
                parameters={},
                validation_criteria={}
            )
        ]
        
        has_cycle = self.compiler._has_circular_dependency(steps)
        assert not has_cycle
    
    def test_preview_workflow(self):
        """测试工作流预览"""
        steps = [
            WorkflowStep(
                id="step1",
                name="Step 1",
                type=StepType.ANALYSIS,
                description="First step",
                agent_roles=["Analyst-AI"],
                dependencies=[],
                parameters={"timeout": 300},
                validation_criteria={}
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                type=StepType.SYNTHESIS,
                description="Second step",
                agent_roles=["Synthesizer-AI"],
                dependencies=["step1"],
                parameters={"timeout": 300},
                validation_criteria={}
            )
        ]
        
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="Test description",
            steps=steps,
            parameters={}
        )
        
        preview = self.compiler.preview_workflow(workflow)
        
        assert preview is not None
        assert preview["name"] == "Test Workflow"
        assert preview["total_steps"] == 2
        assert preview["estimated_duration"] == 600
        assert "Analyst-AI" in preview["agent_roles"]
        assert "Synthesizer-AI" in preview["agent_roles"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
