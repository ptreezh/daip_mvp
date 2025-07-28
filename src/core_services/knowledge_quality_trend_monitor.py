#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识质量趋势监控

监控知识质量随时间的变化趋势
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class KnowledgeQualityTrendMonitor:
    """知识质量趋势监控器"""
    
    def __init__(self):
        """初始化知识质量趋势监控器"""
        self.quality_history = {}  # {knowledge_id: [quality_measurements]}
        self.trend_indicators = {
            "improving": "质量提升",
            "declining": "质量下降", 
            "stable": "质量稳定",
            "volatile": "质量波动"
        }
    
    def record_quality_measurement(self, measurement: Dict[str, Any]) -> bool:
        """记录质量测量"""
        try:
            knowledge_id = measurement.get("knowledge_id")
            if not knowledge_id:
                return False
            
            if knowledge_id not in self.quality_history:
                self.quality_history[knowledge_id] = []
            
            # 添加时间戳如果没有
            if "timestamp" not in measurement:
                measurement["timestamp"] = datetime.now().isoformat()
            
            self.quality_history[knowledge_id].append(measurement)
            return True
            
        except Exception as e:
            logger.error(f"记录质量测量失败: {e}")
            return False
    
    def analyze_quality_trends(self, knowledge_id: str) -> Dict[str, Any]:
        """分析质量趋势"""
        try:
            if knowledge_id not in self.quality_history:
                return {"error": f"知识项不存在: {knowledge_id}"}
            
            measurements = self.quality_history[knowledge_id]
            if len(measurements) < 2:
                return {"overall_trend": "insufficient_data"}
            
            # 提取质量分数
            quality_scores = [m.get("overall_quality", 0.0) for m in measurements]
            
            # 计算趋势
            trend_analysis = {
                "overall_trend": self._determine_trend(quality_scores),
                "trend_direction": self._calculate_trend_direction(quality_scores),
                "improvement_rate": self._calculate_improvement_rate(quality_scores),
                "volatility": self._calculate_volatility(quality_scores),
                "current_quality": quality_scores[-1],
                "quality_range": {
                    "min": min(quality_scores),
                    "max": max(quality_scores),
                    "average": statistics.mean(quality_scores)
                }
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"分析质量趋势失败: {e}")
            return {"error": str(e)}
    
    def generate_quality_forecast(self, knowledge_id: str, forecast_periods: int = 3) -> Dict[str, Any]:
        """生成质量预测"""
        try:
            if knowledge_id not in self.quality_history:
                return {"error": f"知识项不存在: {knowledge_id}"}
            
            measurements = self.quality_history[knowledge_id]
            if len(measurements) < 3:
                return {"forecast": "insufficient_data"}
            
            quality_scores = [m.get("overall_quality", 0.0) for m in measurements]
            
            # 简单的线性预测
            recent_scores = quality_scores[-3:]
            trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
            
            forecast = {
                "forecast_periods": forecast_periods,
                "predicted_scores": [],
                "confidence": 0.6,
                "trend_continuation": trend > 0
            }
            
            current_score = quality_scores[-1]
            for i in range(1, forecast_periods + 1):
                predicted_score = current_score + (trend * i)
                predicted_score = max(0.0, min(1.0, predicted_score))  # 限制在0-1范围
                forecast["predicted_scores"].append(predicted_score)
            
            return forecast
            
        except Exception as e:
            logger.error(f"生成质量预测失败: {e}")
            return {"error": str(e)}
    
    def _determine_trend(self, quality_scores: List[float]) -> str:
        """确定趋势类型"""
        if len(quality_scores) < 2:
            return "stable"
        
        # 计算整体变化
        first_half = quality_scores[:len(quality_scores)//2]
        second_half = quality_scores[len(quality_scores)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_ratio = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        if change_ratio > 0.1:
            return "improving"
        elif change_ratio < -0.1:
            return "declining"
        else:
            # 检查波动性
            volatility = self._calculate_volatility(quality_scores)
            if volatility > 0.2:
                return "volatile"
            else:
                return "stable"
    
    def _calculate_trend_direction(self, quality_scores: List[float]) -> str:
        """计算趋势方向"""
        if len(quality_scores) < 2:
            return "neutral"
        
        first_score = quality_scores[0]
        last_score = quality_scores[-1]
        
        if last_score > first_score * 1.05:
            return "upward"
        elif last_score < first_score * 0.95:
            return "downward"
        else:
            return "neutral"
    
    def _calculate_improvement_rate(self, quality_scores: List[float]) -> float:
        """计算改进率"""
        if len(quality_scores) < 2:
            return 0.0
        
        first_score = quality_scores[0]
        last_score = quality_scores[-1]
        periods = len(quality_scores) - 1
        
        if first_score > 0 and periods > 0:
            return (last_score - first_score) / (first_score * periods)
        else:
            return 0.0
    
    def _calculate_volatility(self, quality_scores: List[float]) -> float:
        """计算波动性"""
        if len(quality_scores) < 2:
            return 0.0
        
        try:
            return statistics.stdev(quality_scores) / statistics.mean(quality_scores)
        except (statistics.StatisticsError, ZeroDivisionError):
            return 0.0