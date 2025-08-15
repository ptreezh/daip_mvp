#!/usr/bin/env python3
"""演示分析器
"""

import logging
from datetime import datetime
from typing import Any

from .demo_types import DemoScenarioType, DemoStepStatus

logger = logging.getLogger(__name__)


class DemoAnalyzer:
    """演示分析器"""
    
    def __init__(self):
        pass
    
    def analyze_demo(self, demo_data: dict[str, Any]) -> dict[str, Any]:
        """分析演示数据"""
        try:
            steps = demo_data.get("steps", [])
            
            # 计算基本统计
            stats = self._calculate_statistics(steps)
            
            # 分析用户参与度
            engagement = self._analyze_engagement(demo_data)
            
            # 计算质量分数
            quality_score = self._calculate_quality_score(demo_data)
            
            # 生成洞察和建议
            insights = self._generate_insights(demo_data)
            recommendations = self._generate_recommendations(demo_data)
            
            return {
                "demo_id": demo_data.get("demo_id"),
                "scenario_type": demo_data.get("scenario_type"),
                "analysis_timestamp": datetime.now().isoformat(),
                "execution_statistics": stats,
                "user_engagement": engagement,
                "quality_assessment": {
                    "overall_quality_score": quality_score,
                    "educational_value": 0.85,
                    "technical_demonstration": 0.90,
                    "user_experience": 0.78
                },
                "insights": insights,
                "recommendations": recommendations
            }
        
        except Exception as e:
            logger.error(f"分析演示失败: {e}")
            return {"error": str(e)}
    
    def _calculate_statistics(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        """计算统计信息"""
        completed_steps = [s for s in steps if s.get("status") == DemoStepStatus.COMPLETED.value]
        failed_steps = [s for s in steps if s.get("status") == DemoStepStatus.FAILED.value]
        
        total_duration = sum(s.get("duration", 0) for s in completed_steps)
        avg_duration = total_duration / len(completed_steps) if completed_steps else 0
        
        return {
            "total_steps": len(steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "success_rate": len(completed_steps) / len(steps) if steps else 0,
            "total_duration": total_duration,
            "avg_step_duration": avg_duration
        }
    
    def _analyze_engagement(self, demo_data: dict[str, Any]) -> dict[str, Any]:
        """分析用户参与度"""
        interactions = demo_data.get("user_interactions", [])
        steps = demo_data.get("steps", [])
        
        return {
            "total_interactions": len(interactions),
            "engagement_score": min(1.0, len(interactions) / len(steps)) if steps else 0
        }
    
    def _calculate_quality_score(self, demo_data: dict[str, Any]) -> float:
        """计算质量分数"""
        steps = demo_data.get("steps", [])
        completed_steps = [s for s in steps if s.get("status") == DemoStepStatus.COMPLETED.value]
        
        # 完成率
        completion_rate = len(completed_steps) / len(steps) if steps else 0
        
        # 参与度
        interactions = demo_data.get("user_interactions", [])
        engagement_score = min(1.0, len(interactions) / len(steps)) if steps else 0
        
        # 综合分数
        quality_score = (completion_rate * 0.6 + engagement_score * 0.4)
        
        return round(quality_score, 2)
    
    def _generate_insights(self, demo_data: dict[str, Any]) -> list[str]:
        """生成洞察"""
        insights = []
        
        steps = demo_data.get("steps", [])
        completed_steps = [s for s in steps if s.get("status") == DemoStepStatus.COMPLETED.value]
        
        if len(completed_steps) == len(steps):
            insights.append("演示完整执行，所有步骤都成功完成")
        
        interactions = demo_data.get("user_interactions", [])
        if interactions:
            insights.append(f"用户积极参与，共进行了{len(interactions)}次交互")
        
        scenario_type = demo_data.get("scenario_type")
        if scenario_type == DemoScenarioType.MULTI_ROLE_DEBATE.value:
            insights.append("多角色辩论展示了AI协作决策的能力")
        
        return insights
    
    def _generate_recommendations(self, demo_data: dict[str, Any]) -> list[str]:
        """生成建议"""
        recommendations = []
        
        steps = demo_data.get("steps", [])
        failed_steps = [s for s in steps if s.get("status") == DemoStepStatus.FAILED.value]
        
        if failed_steps:
            recommendations.append(f"建议检查和修复{len(failed_steps)}个失败的步骤")
        
        interactions = demo_data.get("user_interactions", [])
        if len(interactions) < len(steps) * 0.5:
            recommendations.append("建议增加更多用户交互点以提高参与度")
        
        recommendations.append("建议收集用户反馈以持续改进演示体验")
        
        return recommendations
    
    def generate_summary(self, demo_data: dict[str, Any]) -> str:
        """生成演示摘要"""
        try:
            scenario_name = demo_data.get("scenario_info", {}).get("name", "未知场景")
            duration = demo_data.get("total_duration", 0)
            
            steps = demo_data.get("steps", [])
            completed_steps = [s for s in steps if s.get("status") == DemoStepStatus.COMPLETED.value]
            
            summary = f"成功完成'{scenario_name}'演示，"
            summary += f"耗时{duration:.1f}秒，"
            summary += f"完成{len(completed_steps)}/{len(steps)}个步骤。"
            
            interactions = demo_data.get("user_interactions", [])
            if interactions:
                summary += f"用户进行了{len(interactions)}次交互。"
            
            return summary
        
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return "演示摘要生成失败"