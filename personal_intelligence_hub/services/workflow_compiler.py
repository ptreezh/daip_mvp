"""Personal Intelligence Hub - Workflow Compiler Service

自然语言工作流编译器服务
"""

import re
from datetime import datetime
from typing import Any

from personal_intelligence_hub.models.workflow_models import (
    StepType,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowValidationResult,
)


class WorkflowCompiler:
    """自然语言工作流编译器"""
    
    def __init__(self):
        self.institutional_primitives = {
            "analyze": ["analysis", "examine", "review", "assess", "evaluate"],
            "synthesize": ["synthesize", "combine", "integrate", "merge", "consolidate"],
            "critique": ["critique", "criticize", "challenge", "question", "debate"],
            "validate": ["validate", "verify", "confirm", "check", "test"],
            "document": ["document", "record", "write", "report", "summarize"],
            "collaborate": ["collaborate", "work together", "cooperate", "coordinate"],
            "iterate": ["iterate", "repeat", "refine", "improve", "optimize"]
        }
        
        self.workflow_patterns = {
            "critical_review": {
                "keywords": ["critical review", "deep analysis", "thorough examination", "批判性审查"],
                "steps": ["analyze", "critique", "validate", "synthesize"]
            },
            "multi_perspective": {
                "keywords": ["multiple perspectives", "different viewpoints", "diverse opinions", "多个角度", "多视角", "不同观点"],
                "steps": ["analyze", "collaborate", "synthesize", "validate"]
            },
            "iterative_improvement": {
                "keywords": ["iterative", "continuous improvement", "refinement", "迭代", "持续改进", "优化"],
                "steps": ["analyze", "critique", "iterate", "validate"]
            }
        }
    
    def compile_natural_language(self, description: str) -> WorkflowDefinition:
        """将自然语言描述编译为工作流定义"""
        try:
            # 分析描述中的关键词
            detected_pattern = self._detect_pattern(description)
            
            # 提取任务和步骤
            steps = self._extract_steps(description, detected_pattern)
            
            # 生成工作流定义
            workflow = self._generate_workflow(description, steps)
            
            return workflow
            
        except Exception:
            # 返回默认工作流
            return self._create_default_workflow(description)
    
    def _detect_pattern(self, description: str) -> str:
        """检测工作流模式"""
        description_lower = description.lower()
        
        for pattern_name, pattern_data in self.workflow_patterns.items():
            for keyword in pattern_data["keywords"]:
                if keyword.lower() in description_lower:
                    return pattern_name
        
        return "critical_review"  # 默认模式
    
    def _extract_steps(self, description: str, pattern: str) -> list[WorkflowStep]:
        """提取工作流步骤"""
        steps = []
        
        # 基于模式获取步骤模板
        if pattern in self.workflow_patterns:
            step_types = self.workflow_patterns[pattern]["steps"]
        else:
            step_types = ["analyze", "critique", "validate", "synthesize"]
        
        # 创建步骤
        for i, step_type in enumerate(step_types):
            step = WorkflowStep(
                id=f"step_{i+1}",
                name=f"{step_type.capitalize()} Step",
                type=self._get_step_type(step_type),
                description=f"Perform {step_type} on the given topic",
                agent_roles=self._get_agent_roles_for_step(step_type),
                dependencies=[f"step_{i}"] if i > 0 else [],
                parameters={"timeout": 300, "depth": "detailed"},
                validation_criteria=self._get_validation_criteria(step_type)
            )
            steps.append(step)
        
        return steps
    
    def _get_step_type(self, step_name: str) -> StepType:
        """获取步骤类型"""
        step_mapping = {
            "analyze": StepType.ANALYSIS,
            "synthesize": StepType.SYNTHESIS,
            "critique": StepType.CRITIQUE,
            "validate": StepType.VALIDATION,
            "document": StepType.DOCUMENTATION,
            "collaborate": StepType.COLLABORATION,
            "iterate": StepType.ITERATION
        }
        return step_mapping.get(step_name, StepType.ANALYSIS)
    
    def _get_agent_roles_for_step(self, step_type: str) -> list[str]:
        """获取步骤的代理角色"""
        role_mapping = {
            "analyze": ["Analyst-AI", "Research-AI"],
            "synthesize": ["Synthesizer-AI", "Integrator-AI"],
            "critique": ["Critic-AI", "Skeptic-AI"],
            "validate": ["Validator-AI", "Tester-AI"],
            "document": ["Documenter-AI", "Writer-AI"],
            "collaborate": ["Coordinator-AI", "Facilitator-AI"],
            "iterate": ["Optimizer-AI", "Refiner-AI"]
        }
        return role_mapping.get(step_type, ["General-AI"])
    
    def _get_validation_criteria(self, step_type: str) -> dict[str, Any]:
        """获取验证标准"""
        criteria_mapping = {
            "analyze": {"completeness": 0.9, "accuracy": 0.85},
            "synthesize": {"coherence": 0.9, "integration": 0.8},
            "critique": {"constructiveness": 0.8, "depth": 0.85},
            "validate": {"correctness": 0.95, "reliability": 0.9},
            "document": {"clarity": 0.9, "completeness": 0.85},
            "collaborate": {"coordination": 0.85, "effectiveness": 0.8},
            "iterate": {"improvement": 0.8, "convergence": 0.75}
        }
        return criteria_mapping.get(step_type, {"quality": 0.8})
    
    def _generate_workflow(self, description: str, steps: list[WorkflowStep]) -> WorkflowDefinition:
        """生成工作流定义"""
        return WorkflowDefinition(
            id=f"workflow_{int(datetime.now().timestamp())}",
            name=self._generate_workflow_name(description),
            description=description,
            steps=steps,
            parameters={
                "timeout": 3600,
                "max_iterations": 5,
                "quality_threshold": 0.8
            },
            metadata={
                "source": "natural_language",
                "created_at": datetime.now().isoformat(),
                "confidence": 0.85
            }
        )
    
    def _generate_workflow_name(self, description: str) -> str:
        """生成工作流名称"""
        # 从描述中提取关键词
        words = description.split()[:5]
        key_phrase = "_".join(words).lower()
        key_phrase = re.sub(r'[^\w\s]', '', key_phrase)
        return f"workflow_{key_phrase}"
    
    def _create_default_workflow(self, description: str) -> WorkflowDefinition:
        """创建默认工作流"""
        steps = [
            WorkflowStep(
                id="step_1",
                name="Initial Analysis",
                type=StepType.ANALYSIS,
                description="Analyze the given topic",
                agent_roles=["Analyst-AI"],
                dependencies=[],
                parameters={"timeout": 300},
                validation_criteria={"completeness": 0.8}
            ),
            WorkflowStep(
                id="step_2",
                name="Critical Review",
                type=StepType.CRITIQUE,
                description="Provide critical review",
                agent_roles=["Critic-AI"],
                dependencies=["step_1"],
                parameters={"timeout": 300},
                validation_criteria={"constructiveness": 0.8}
            ),
            WorkflowStep(
                id="step_3",
                name="Final Synthesis",
                type=StepType.SYNTHESIS,
                description="Synthesize findings",
                agent_roles=["Synthesizer-AI"],
                dependencies=["step_2"],
                parameters={"timeout": 300},
                validation_criteria={"coherence": 0.8}
            )
        ]
        
        return WorkflowDefinition(
            id=f"default_workflow_{int(datetime.now().timestamp())}",
            name="default_critical_review",
            description=description,
            steps=steps,
            parameters={"timeout": 900, "quality_threshold": 0.8},
            metadata={"source": "default", "created_at": datetime.now().isoformat()}
        )
    
    def validate_workflow(self, workflow: WorkflowDefinition) -> WorkflowValidationResult:
        """验证工作流定义"""
        issues = []
        
        # 检查步骤完整性
        if not workflow.steps:
            issues.append("工作流必须包含至少一个步骤")
        
        # 检查依赖关系
        step_ids = {step.id for step in workflow.steps}
        for step in workflow.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    issues.append(f"步骤 {step.id} 依赖不存在的步骤 {dep}")
        
        # 检查循环依赖
        if self._has_circular_dependency(workflow.steps):
            issues.append("工作流存在循环依赖")
        
        return WorkflowValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            suggestions=self._generate_suggestions(issues)
        )
    
    def _has_circular_dependency(self, steps: list[WorkflowStep]) -> bool:
        """检查循环依赖"""
        # 简化的循环检测
        visited = set()
        rec_stack = set()
        
        def dfs(step_id):
            if step_id in rec_stack:
                return True
            if step_id in visited:
                return False
            
            rec_stack.add(step_id)
            visited.add(step_id)
            
            step = next((s for s in steps if s.id == step_id), None)
            if step:
                for dep in step.dependencies:
                    if dfs(dep):
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        for step in steps:
            if dfs(step.id):
                return True
        
        return False
    
    def _generate_suggestions(self, issues: list[str]) -> list[str]:
        """生成改进建议"""
        suggestions = []
        
        for issue in issues:
            if "依赖不存在的步骤" in issue:
                suggestions.append("请检查并修正步骤依赖关系")
            elif "循环依赖" in issue:
                suggestions.append("请重新设计步骤依赖关系，避免循环")
            elif "必须包含至少一个步骤" in issue:
                suggestions.append("请添加至少一个工作流步骤")
        
        return suggestions
    
    def preview_workflow(self, workflow: WorkflowDefinition) -> dict[str, Any]:
        """预览工作流"""
        return {
            "name": workflow.name,
            "description": workflow.description,
            "total_steps": len(workflow.steps),
            "estimated_duration": sum(step.parameters.get("timeout", 300) for step in workflow.steps),
            "agent_roles": list(set(role for step in workflow.steps for role in step.agent_roles)),
            "complexity": "high" if len(workflow.steps) > 5 else "medium" if len(workflow.steps) > 2 else "low"
        }
