#!/usr/bin/env python3
"""共识可视化模块

提供共识形成过程的实时可视化展示
"""

import logging
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class ConsensusVisualization:
    """共识可视化器"""

    def __init__(self):
        """初始化共识可视化器"""
        self.visualization_types = [
            "convergence_chart",
            "participant_agreement_matrix",
            "consensus_timeline",
            "quality_metrics_dashboard",
            "conflict_resolution_flow"
        ]
        self.consensus_data = {}
        self.visualization_history = []

    def create_consensus_chart(
        self,
        consensus_data: dict[str, Any],
        chart_type: str = "convergence_chart"
    ) -> dict[str, Any]:
        """创建共识图表"""
        try:
            chart_config = {
                "chart_id": f"consensus_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": chart_type,
                "data": consensus_data,
                "timestamp": datetime.now().isoformat()
            }

            if chart_type == "convergence_chart":
                chart_config["visualization"] = self._create_convergence_chart(consensus_data)
            elif chart_type == "agreement_matrix":
                chart_config["visualization"] = self._create_agreement_matrix(consensus_data)
            elif chart_type == "timeline":
                chart_config["visualization"] = self._create_consensus_timeline(consensus_data)
            else:
                chart_config["visualization"] = self._create_default_chart(consensus_data)

            self.visualization_history.append(chart_config)
            return chart_config

        except Exception as e:
            logger.error(f"创建共识图表失败: {e}")
            return {"error": str(e)}

    def show_convergence_process(
        self,
        process_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """展示共识收敛过程"""
        try:
            convergence_visualization = {
                "process_id": f"convergence_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "stages": [],
                "overall_trend": "unknown",
                "convergence_rate": 0.0
            }

            # 分析收敛阶段
            for i, stage_data in enumerate(process_data):
                stage_info = {
                    "stage": i + 1,
                    "consensus_score": stage_data.get("consensus_score", 0.0),
                    "participant_agreement": stage_data.get("participant_agreement", {}),
                    "conflicts_resolved": stage_data.get("conflicts_resolved", 0),
                    "timestamp": stage_data.get("timestamp", datetime.now().isoformat())
                }
                convergence_visualization["stages"].append(stage_info)

            # 计算整体趋势
            if len(convergence_visualization["stages"]) >= 2:
                first_score = convergence_visualization["stages"][0]["consensus_score"]
                last_score = convergence_visualization["stages"][-1]["consensus_score"]

                if last_score > first_score:
                    convergence_visualization["overall_trend"] = "converging"
                elif last_score < first_score:
                    convergence_visualization["overall_trend"] = "diverging"
                else:
                    convergence_visualization["overall_trend"] = "stable"

                convergence_visualization["convergence_rate"] = (last_score - first_score) / len(convergence_visualization["stages"])

            return convergence_visualization

        except Exception as e:
            logger.error(f"展示收敛过程失败: {e}")
            return {"error": str(e)}

    def display_quality_metrics(
        self,
        quality_data: dict[str, Any]
    ) -> dict[str, Any]:
        """显示质量指标"""
        try:
            metrics_display = {
                "display_id": f"quality_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "metrics": {},
                "visualizations": [],
                "recommendations": []
            }

            # 处理质量指标
            for metric_name, metric_value in quality_data.items():
                if isinstance(metric_value, (int, float)):
                    metrics_display["metrics"][metric_name] = {
                        "value": metric_value,
                        "status": self._evaluate_metric_status(metric_name, metric_value),
                        "visualization_type": self._get_metric_visualization_type(metric_name)
                    }

            # 生成可视化配置
            for metric_name, metric_info in metrics_display["metrics"].items():
                viz_config = {
                    "metric": metric_name,
                    "type": metric_info["visualization_type"],
                    "value": metric_info["value"],
                    "status": metric_info["status"]
                }
                metrics_display["visualizations"].append(viz_config)

            # 生成改进建议
            metrics_display["recommendations"] = self._generate_quality_recommendations(quality_data)

            return metrics_display

        except Exception as e:
            logger.error(f"显示质量指标失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def _create_convergence_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _create_convergence_chart(self, data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """创建收敛图表"""
        return {
            "chart_type": "line_chart",
            "x_axis": "time_steps",
            "y_axis": "consensus_score",
            "data_points": data.get("convergence_points", []),
            "trend_line": True,
            "confidence_bands": True
        }
<<<<<<< HEAD

    def _create_agreement_matrix(self, data: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _create_agreement_matrix(self, data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """创建同意度矩阵"""
        return {
            "chart_type": "heatmap",
            "matrix_data": data.get("agreement_matrix", []),
            "participants": data.get("participants", []),
            "color_scale": "consensus_agreement"
        }
<<<<<<< HEAD

    def _create_consensus_timeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _create_consensus_timeline(self, data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """创建共识时间线"""
        return {
            "chart_type": "timeline",
            "events": data.get("consensus_events", []),
            "milestones": data.get("milestones", []),
            "interactive": True
        }
<<<<<<< HEAD

    def _create_default_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _create_default_chart(self, data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """创建默认图表"""
        return {
            "chart_type": "bar_chart",
            "data": data,
            "message": "使用默认可视化"
        }

    def _evaluate_metric_status(self, metric_name: str, value: float) -> str:
        """评估指标状态"""
        # 简单的阈值评估
        thresholds = {
            "consensus_score": {"good": 0.8, "fair": 0.6},
            "coherence_score": {"good": 0.7, "fair": 0.5},
            "participant_satisfaction": {"good": 0.75, "fair": 0.6}
        }

        if metric_name in thresholds:
            if value >= thresholds[metric_name]["good"]:
                return "good"
            elif value >= thresholds[metric_name]["fair"]:
                return "fair"
            else:
                return "poor"

        return "unknown"

    def _get_metric_visualization_type(self, metric_name: str) -> str:
        """获取指标可视化类型"""
        viz_types = {
            "consensus_score": "gauge",
            "coherence_score": "progress_bar",
            "participant_satisfaction": "radar_chart",
            "convergence_rate": "line_chart"
        }

        return viz_types.get(metric_name, "bar_chart")
<<<<<<< HEAD

    def _generate_quality_recommendations(self, quality_data: Dict[str, Any]) -> List[str]:
=======
    
    def _generate_quality_recommendations(self, quality_data: dict[str, Any]) -> list[str]:
>>>>>>> feature/core-services-refactor
        """生成质量改进建议"""
        recommendations = []

        consensus_score = quality_data.get("consensus_score", 0.0)
        if consensus_score < 0.6:
            recommendations.append("共识分数较低，建议增加讨论轮次或调整参与者权重")

        coherence_score = quality_data.get("coherence_score", 0.0)
        if coherence_score < 0.5:
            recommendations.append("观点一致性不足，建议引入更多结构化讨论")

        participant_satisfaction = quality_data.get("participant_satisfaction", 0.0)
        if participant_satisfaction < 0.6:
            recommendations.append("参与者满意度偏低，建议改进参与机制")

        if not recommendations:
            recommendations.append("当前共识质量良好，继续保持")

        return recommendations
<<<<<<< HEAD

    def get_visualization_history(self) -> List[Dict[str, Any]]:
=======
    
    def get_visualization_history(self) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """获取可视化历史"""
        return self.visualization_history.copy()

    def clear_visualization_data(self) -> bool:
        """清除可视化数据"""
        try:
            self.consensus_data.clear()
            self.visualization_history.clear()
            return True
        except Exception as e:
            logger.error(f"清除可视化数据失败: {e}")
            return False
