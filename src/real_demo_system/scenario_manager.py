#!/usr/bin/env python3
"""演示场景管理器
"""

from typing import Any

from .demo_types import DemoScenarioType


class ScenarioManager:
    """演示场景管理器"""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> dict[str, dict[str, Any]]:
        """初始化演示场景"""
        return {
            DemoScenarioType.MULTI_ROLE_DEBATE.value: {
                "name": "多角色辩论演示",
                "description": "展示不同角色就特定话题进行辩论的过程",
                "duration_estimate": "10-15分钟",
                "complexity": "medium",
                "required_components": ["role_manager", "workflow_engine"],
                "customizable_params": ["topic", "roles", "debate_rounds"],
                "steps": [
                    "scenario_setup",
                    "role_selection", 
                    "debate_initialization",
                    "debate_rounds",
                    "consensus_formation",
                    "result_analysis"
                ]
            },
            
            DemoScenarioType.ETHICAL_ANALYSIS.value: {
                "name": "AI伦理决策分析",
                "description": "展示AI系统如何进行伦理决策分析",
                "duration_estimate": "8-12分钟",
                "complexity": "high",
                "required_components": ["role_manager", "workflow_engine", "wiki_service"],
                "customizable_params": ["ethical_dilemma", "stakeholders"],
                "steps": [
                    "dilemma_presentation",
                    "stakeholder_analysis",
                    "framework_application",
                    "ethical_evaluation",
                    "recommendation_generation"
                ]
            },
            
            DemoScenarioType.CONFLICT_RESOLUTION.value: {
                "name": "知识冲突解决",
                "description": "展示如何识别和解决知识冲突",
                "duration_estimate": "6-10分钟",
                "complexity": "medium",
                "required_components": ["wiki_service", "workflow_engine"],
                "customizable_params": ["conflict_type", "evidence_sources"],
                "steps": [
                    "conflict_detection",
                    "evidence_analysis",
                    "strategy_selection",
                    "resolution_execution",
                    "quality_verification"
                ]
            }
        }
    
    def get_available_scenarios(self) -> dict[str, dict[str, Any]]:
        """获取可用场景"""
        return self.scenarios.copy()
    
    def get_scenario(self, scenario_type: str) -> dict[str, Any]:
        """获取特定场景"""
        if scenario_type not in self.scenarios:
            raise ValueError(f"未知场景类型: {scenario_type}")
        return self.scenarios[scenario_type].copy()
    
    def validate_scenario_params(self, scenario_type: str, params: dict[str, Any]) -> bool:
        """验证场景参数"""
        if scenario_type not in self.scenarios:
            return False
        
        scenario = self.scenarios[scenario_type]
        customizable_params = scenario.get("customizable_params", [])
        
        # 检查是否有不支持的参数
        for param in params:
            if param not in customizable_params:
                return False
        
        return True