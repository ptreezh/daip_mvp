"""@Time    : 2025-08-04 11:30:00
@Author  : DAIP-LIVE Team
@File    : performance_monitor.py
@Description:
    Performance Monitor for tracking synthesis system performance.
"""

import asyncio
import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Performance metric types."""
    QUALITY_SCORE = "quality_score"
    SYNTHESIS_SPEED = "synthesis_speed"
    MEMORY_USAGE = "memory_usage"
    TOKEN_EFFICIENCY = "token_efficiency"
    CONVERGENCE_RATE = "convergence_rate"
    USER_SATISFACTION = "user_satisfaction"
    ERROR_RATE = "error_rate"


@dataclass
class PerformanceDataPoint:
    """Single performance data point."""
    timestamp: str
    metric_type: PerformanceMetric
    value: float
    metadata: dict[str, Any]
    context: dict[str, Any]


@dataclass
class PerformanceAlert:
    """Performance alert."""
    alert_id: str
    metric_type: PerformanceMetric
    severity: str
    message: str
    timestamp: str
    suggested_actions: list[str]


class PerformanceMonitor:
    """性能监控器 - Comprehensive performance monitoring for synthesis system.
    
    Tracks system performance metrics, detects anomalies, generates alerts,
    and provides performance insights for optimization.
    """
    
    def __init__(self, config: dict[str, Any] = None):
        """Initialize the Performance Monitor.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        
        # Performance thresholds
        self.thresholds = {
            "quality_score": {"warning": 0.5, "critical": 0.3},
            "synthesis_speed": {"warning": 30.0, "critical": 60.0},  # seconds
            "memory_usage": {"warning": 0.8, "critical": 0.9},  # 80%, 90%
            "token_efficiency": {"warning": 0.6, "critical": 0.4},
            "convergence_rate": {"warning": 0.4, "critical": 0.2},
            "error_rate": {"warning": 0.1, "critical": 0.2}
        }
        
        # Performance data storage
        self.performance_data = []
        self.alerts = []
        
        # Monitoring configuration
        self.monitoring_enabled = self.config.get("monitoring_enabled", True)
        self.alert_enabled = self.config.get("alert_enabled", True)
        self.data_retention_days = self.config.get("data_retention_days", 30)
        
        # Performance baselines
        self.baselines = self._initialize_baselines()
        
        # Performance trends
        self.trends = {}
        
        # Anomaly detection
        self.anomaly_detector = AnomalyDetector(self.config.get("anomaly_config", {}))
        
    async def record_performance(
        self,
        metric_type: PerformanceMetric,
        value: float,
        metadata: dict[str, Any] = None,
        context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Record a performance data point.
        
        Args:
            metric_type: Type of performance metric
            value: Metric value
            metadata: Additional metadata
            context: Context information
            
        Returns:
            Recording result
        """
        try:
            if not self.monitoring_enabled:
                return {"success": False, "message": "Monitoring disabled"}
            
            # Create data point
            data_point = PerformanceDataPoint(
                timestamp=datetime.now().isoformat(),
                metric_type=metric_type,
                value=value,
                metadata=metadata or {},
                context=context or {}
            )
            
            # Store data point
            self.performance_data.append(data_point)
            
            # Check for alerts
            alerts = await self._check_alerts(data_point)
            
            # Update trends
            self._update_trends(data_point)
            
            # Detect anomalies
            anomalies = await self.anomaly_detector.detect_anomalies(data_point)
            
            # Clean old data
            self._cleanup_old_data()
            
            return {
                "success": True,
                "data_point": asdict(data_point),
                "alerts_triggered": len(alerts),
                "anomalies_detected": len(anomalies)
            }
            
        except Exception as e:
            logger.error(f"Failed to record performance data: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_alerts(self, data_point: PerformanceDataPoint) -> list[PerformanceAlert]:
        """Check for performance alerts."""
        alerts = []
        
        if not self.alert_enabled:
            return alerts
        
        metric_name = data_point.metric_type.value
        threshold = self.thresholds.get(metric_name)
        
        if not threshold:
            return alerts
        
        value = data_point.value
        
        # Check thresholds
        if value <= threshold.get("critical", 0):
            severity = "critical"
        elif value <= threshold.get("warning", 0):
            severity = "warning"
        else:
            return alerts
        
        # Create alert
        alert = PerformanceAlert(
            alert_id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{metric_name}",
            metric_type=data_point.metric_type,
            severity=severity,
            message=f"{metric_name} {severity}: {value:.3f}",
            timestamp=datetime.now().isoformat(),
            suggested_actions=self._get_suggested_actions(metric_name, severity, value)
        )
        
        self.alerts.append(alert)
        alerts.append(alert)
        
        # Log alert
        logger.warning(f"Performance alert: {alert.message}")
        
        return alerts
    
    def _get_suggested_actions(self, metric_name: str, severity: str, value: float) -> list[str]:
        """Get suggested actions for alerts."""
        actions = []
        
        if metric_name == "quality_score":
            if severity == "critical":
                actions.extend([
                    "立即检查综合算法配置",
                    "审查专家观点质量",
                    "考虑重新运行综合过程"
                ])
            else:
                actions.extend([
                    "监控质量趋势",
                    "考虑调整权重配置"
                ])
        
        elif metric_name == "synthesis_speed":
            if severity == "critical":
                actions.extend([
                    "检查系统资源使用情况",
                    "优化算法性能",
                    "考虑增加并行处理"
                ])
            else:
                actions.extend([
                    "监控处理时间",
                    "优化数据处理流程"
                ])
        
        elif metric_name == "memory_usage":
            if severity == "critical":
                actions.extend([
                    "立即释放内存资源",
                    "重启相关服务",
                    "检查内存泄漏"
                ])
            else:
                actions.extend([
                    "监控内存使用",
                    "优化内存管理"
                ])
        
        elif metric_name == "token_efficiency":
            if severity == "critical":
                actions.extend([
                    "优化提示词设计",
                    "减少冗余输出",
                    "改进上下文管理"
                ])
            else:
                actions.extend([
                    "监控Token使用效率",
                    "优化提示策略"
                ])
        
        return actions
    
    def _update_trends(self, data_point: PerformanceDataPoint):
        """Update performance trends."""
        metric_name = data_point.metric_type.value
        
        if metric_name not in self.trends:
            self.trends[metric_name] = {
                "values": [],
                "trend": "stable",
                "last_updated": None
            }
        
        # Add new value
        self.trends[metric_name]["values"].append({
            "timestamp": data_point.timestamp,
            "value": data_point.value
        })
        
        # Keep only recent values (last 100)
        if len(self.trends[metric_name]["values"]) > 100:
            self.trends[metric_name]["values"] = self.trends[metric_name]["values"][-100:]
        
        # Update trend analysis
        self._analyze_trend(metric_name)
        
        self.trends[metric_name]["last_updated"] = datetime.now().isoformat()
    
    def _analyze_trend(self, metric_name: str):
        """Analyze performance trend for a metric."""
        trend_data = self.trends[metric_name]
        values = [point["value"] for point in trend_data["values"]]
        
        if len(values) < 3:
            trend_data["trend"] = "insufficient_data"
            return
        
        # Calculate trend using simple linear regression
        x_values = list(range(len(values)))
        
        # Calculate slope
        n = len(values)
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values, strict=False))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0
        
        # Determine trend direction
        if slope > 0.01:
            trend_data["trend"] = "improving"
        elif slope < -0.01:
            trend_data["trend"] = "declining"
        else:
            trend_data["trend"] = "stable"
        
        # Add trend strength
        trend_data["trend_strength"] = abs(slope)
    
    def _cleanup_old_data(self):
        """Clean up old performance data."""
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        
        # Clean performance data
        self.performance_data = [
            point for point in self.performance_data
            if datetime.fromisoformat(point.timestamp) > cutoff_date
        ]
        
        # Clean alerts (keep last 1000)
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    def _initialize_baselines(self) -> dict[str, Any]:
        """Initialize performance baselines."""
        return {
            "quality_score": {"target": 0.75, "minimum": 0.5},
            "synthesis_speed": {"target": 15.0, "maximum": 30.0},
            "memory_usage": {"target": 0.6, "maximum": 0.8},
            "token_efficiency": {"target": 0.8, "minimum": 0.6},
            "convergence_rate": {"target": 0.7, "minimum": 0.5},
            "error_rate": {"target": 0.05, "maximum": 0.1}
        }
    
    async def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary."""
        try:
            # Calculate current metrics
            current_metrics = self._calculate_current_metrics()
            
            # Get trend analysis
            trend_analysis = self._get_trend_analysis()
            
            # Get alert summary
            alert_summary = self._get_alert_summary()
            
            # Get health status
            health_status = self._calculate_health_status(current_metrics)
            
            # Get performance insights
            insights = await self._generate_performance_insights(current_metrics, trend_analysis)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "current_metrics": current_metrics,
                "trend_analysis": trend_analysis,
                "alert_summary": alert_summary,
                "health_status": health_status,
                "insights": insights,
                "monitoring_status": {
                    "enabled": self.monitoring_enabled,
                    "alerts_enabled": self.alert_enabled,
                    "data_points_count": len(self.performance_data),
                    "alerts_count": len(self.alerts)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {e}")
            return {"error": str(e)}
    
    def _calculate_current_metrics(self) -> dict[str, Any]:
        """Calculate current performance metrics."""
        current_metrics = {}
        
        # Group data by metric type
        metric_groups = {}
        for point in self.performance_data:
            metric_name = point.metric_type.value
            if metric_name not in metric_groups:
                metric_groups[metric_name] = []
            metric_groups[metric_name].append(point)
        
        # Calculate statistics for each metric
        for metric_name, points in metric_groups.items():
            if not points:
                continue
            
            values = [point.value for point in points]
            
            current_metrics[metric_name] = {
                "current_value": values[-1] if values else 0.0,
                "average": statistics.mean(values) if values else 0.0,
                "minimum": min(values) if values else 0.0,
                "maximum": max(values) if values else 0.0,
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "data_points": len(values),
                "last_updated": points[-1].timestamp if points else None
            }
        
        return current_metrics
    
    def _get_trend_analysis(self) -> dict[str, Any]:
        """Get trend analysis for all metrics."""
        trend_analysis = {}
        
        for metric_name, trend_data in self.trends.items():
            if not trend_data["values"]:
                continue
            
            trend_analysis[metric_name] = {
                "trend": trend_data["trend"],
                "trend_strength": trend_data.get("trend_strength", 0.0),
                "recent_values": [point["value"] for point in trend_data["values"][-10:]],
                "last_updated": trend_data["last_updated"]
            }
        
        return trend_analysis
    
    def _get_alert_summary(self) -> dict[str, Any]:
        """Get alert summary."""
        # Count alerts by severity
        severity_counts = {"critical": 0, "warning": 0, "info": 0}
        recent_alerts = []
        
        # Get alerts from last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert.timestamp)
            if alert_time > cutoff_time:
                severity_counts[alert.severity] += 1
                recent_alerts.append(alert)
        
        return {
            "total_alerts": len(self.alerts),
            "recent_alerts_24h": len(recent_alerts),
            "severity_breakdown": severity_counts,
            "most_recent_alert": recent_alerts[-1].timestamp if recent_alerts else None
        }
    
    def _calculate_health_status(self, current_metrics: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall system health status."""
        health_scores = {}
        
        for metric_name, metrics in current_metrics.items():
            baseline = self.baselines.get(metric_name, {})
            current_value = metrics.get("current_value", 0.0)
            
            # Calculate health score based on baseline
            if "target" in baseline:
                target = baseline["target"]
                # Score based on proximity to target
                if metric_name in ["synthesis_speed", "memory_usage", "error_rate"]:
                    # Lower is better
                    score = max(0, 1 - (current_value - target) / target)
                else:
                    # Higher is better
                    score = min(1, current_value / target)
            else:
                score = 0.5  # Default score
            
            health_scores[metric_name] = score
        
        # Calculate overall health
        overall_health = sum(health_scores.values()) / len(health_scores) if health_scores else 0.0
        
        # Determine health status
        if overall_health >= 0.8:
            status = "excellent"
        elif overall_health >= 0.6:
            status = "good"
        elif overall_health >= 0.4:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "overall_health": overall_health,
            "status": status,
            "metric_scores": health_scores,
            "critical_issues": [
                metric for metric, score in health_scores.items()
                if score < 0.3
            ]
        }
    
    async def _generate_performance_insights(
        self,
        current_metrics: dict[str, Any],
        trend_analysis: dict[str, Any]
    ) -> list[str]:
        """Generate performance insights."""
        insights = []
        
        # Quality score insights
        if "quality_score" in current_metrics:
            quality = current_metrics["quality_score"]
            if quality.get("current_value", 0.0) < 0.5:
                insights.append("质量分数低于目标值，建议检查综合算法")
            elif quality.get("current_value", 0.0) > 0.8:
                insights.append("质量表现优秀，保持当前配置")
        
        # Performance trend insights
        for metric_name, trend in trend_analysis.items():
            if trend["trend"] == "declining" and trend.get("trend_strength", 0.0) > 0.1:
                insights.append(f"{metric_name}呈现下降趋势，需要关注")
            elif trend["trend"] == "improving" and trend.get("trend_strength", 0.0) > 0.1:
                insights.append(f"{metric_name}持续改善，表现良好")
        
        # Resource usage insights
        if "memory_usage" in current_metrics:
            memory = current_metrics["memory_usage"]
            if memory.get("current_value", 0.0) > 0.8:
                insights.append("内存使用率较高，建议优化资源管理")
        
        # Speed insights
        if "synthesis_speed" in current_metrics:
            speed = current_metrics["synthesis_speed"]
            if speed.get("current_value", 0.0) > 30.0:
                insights.append("综合处理时间较长，考虑性能优化")
        
        return insights[:5]  # Return top 5 insights
    
    def get_performance_history(self, metric_type: PerformanceMetric = None, days: int = 7) -> list[dict[str, Any]]:
        """Get performance history for a specific metric."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_data = [
            asdict(point) for point in self.performance_data
            if datetime.fromisoformat(point.timestamp) > cutoff_date
            and (metric_type is None or point.metric_type == metric_type)
        ]
        
        return filtered_data
    
    def get_alerts(self, severity: str = None, days: int = 7) -> list[dict[str, Any]]:
        """Get alerts with optional filtering."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_alerts = [
            asdict(alert) for alert in self.alerts
            if datetime.fromisoformat(alert.timestamp) > cutoff_date
            and (severity is None or alert.severity == severity)
        ]
        
        return filtered_alerts
    
    def get_performance_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report."""
        return {
            "report_timestamp": datetime.now().isoformat(),
            "system_health": self._calculate_health_status(self._calculate_current_metrics()),
            "performance_summary": asyncio.run(self.get_performance_summary()),
            "recent_alerts": self.get_alerts(days=1),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> list[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        # Based on current metrics
        current_metrics = self._calculate_current_metrics()
        
        if "quality_score" in current_metrics:
            quality = current_metrics["quality_score"]
            if quality.get("current_value", 0.0) < 0.6:
                recommendations.append("考虑调整综合算法权重配置")
        
        if "synthesis_speed" in current_metrics:
            speed = current_metrics["synthesis_speed"]
            if speed.get("current_value", 0.0) > 25.0:
                recommendations.append("优化算法性能或增加并行处理")
        
        if "memory_usage" in current_metrics:
            memory = current_metrics["memory_usage"]
            if memory.get("current_value", 0.0) > 0.7:
                recommendations.append("优化内存使用策略")
        
        # Based on alerts
        recent_alerts = self.get_alerts(days=3)
        if len(recent_alerts) > 5:
            recommendations.append("频繁告警，建议全面系统检查")
        
        return recommendations
    
    def reset_monitoring_data(self):
        """Reset all monitoring data."""
        self.performance_data.clear()
        self.alerts.clear()
        self.trends.clear()
        logger.info("Performance monitoring data reset")
    
    def export_performance_data(self) -> dict[str, Any]:
        """Export performance data for analysis."""
        return {
            "export_timestamp": datetime.now().isoformat(),
            "performance_data": [asdict(point) for point in self.performance_data],
            "alerts": [asdict(alert) for alert in self.alerts],
            "trends": self.trends,
            "baselines": self.baselines,
            "thresholds": self.thresholds
        }


class AnomalyDetector:
    """Simple anomaly detector for performance metrics."""
    
    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.sensitivity = self.config.get("sensitivity", 2.0)  # Standard deviations
    
    async def detect_anomalies(self, data_point: PerformanceDataPoint) -> list[dict[str, Any]]:
        """Detect anomalies in performance data."""
        # This is a simplified anomaly detection
        # In practice, would use more sophisticated methods
        
        anomalies = []
        
        # For now, return empty list
        # Future implementation could include:
        # - Statistical outlier detection
        # - Time series anomaly detection
        # - Machine learning-based anomaly detection
        
        return anomalies