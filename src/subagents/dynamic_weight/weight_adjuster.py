# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 11:00:00
@Author  : DAIP-LIVE Team
@File    : weight_adjuster.py
@Description:
    Dynamic Weight Adjuster for adaptive multi-perspective synthesis.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import statistics
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WeightAdjustmentStrategy(Enum):
    """Weight adjustment strategies."""
    QUALITY_BASED = "quality_based"
    PERFORMANCE_BASED = "performance_based"
    DIVERSITY_BASED = "diversity_based"
    CONSENSUS_BASED = "consensus_based"
    ADAPTIVE_HYBRID = "adaptive_hybrid"


@dataclass
class WeightConfig:
    """Weight configuration for a dimension."""
    name: str
    current_weight: float
    min_weight: float
    max_weight: float
    default_weight: float
    adjustment_factor: float
    performance_history: List[float]
    last_adjustment: Optional[str] = None


class DynamicWeightAdjuster:
    """
    动态权重调整器 - Intelligent weight adjustment for synthesis optimization.
    
    Dynamically adjusts weights for different synthesis dimensions based on
    performance metrics, quality feedback, and contextual factors.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Dynamic Weight Adjuster.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        
        # Default weight configurations
        self.default_weights = {
            "cognitive_depth": 0.20,
            "insight_quality": 0.18,
            "synthesis_coherence": 0.15,
            "perspective_integration": 0.12,
            "conflict_resolution": 0.10,
            "evidence_utilization": 0.10,
            "practical_value": 0.08,
            "innovation_level": 0.07
        }
        
        # Initialize weight configurations
        self.weight_configs = {}
        for name, default_weight in self.default_weights.items():
            self.weight_configs[name] = WeightConfig(
                name=name,
                current_weight=default_weight,
                min_weight=0.02,
                max_weight=0.30,
                default_weight=default_weight,
                adjustment_factor=0.1,
                performance_history=[],
                last_adjustment=None
            )
        
        # Adjustment strategy
        self.adjustment_strategy = WeightAdjustmentStrategy(
            self.config.get("adjustment_strategy", "adaptive_hybrid")
        )
        
        # Performance thresholds
        self.performance_thresholds = {
            "excellent": 0.85,
            "good": 0.70,
            "acceptable": 0.55,
            "poor": 0.40
        }
        
        # Adjustment history
        self.adjustment_history = []
        
        # Learning parameters
        self.learning_rate = self.config.get("learning_rate", 0.05)
        self.exploration_rate = self.config.get("exploration_rate", 0.1)
        self.stabilization_factor = self.config.get("stabilization_factor", 0.8)
        
    async def adjust_weights(
        self,
        quality_assessment: Dict[str, Any],
        synthesis_result: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Adjust weights based on quality assessment and performance.
        
        Args:
            quality_assessment: Quality assessment results
            synthesis_result: Synthesis result
            context: Additional context information
            
        Returns:
            Weight adjustment results
        """
        try:
            logger.info("Starting dynamic weight adjustment")
            
            # Extract dimension scores
            dimension_scores = self._extract_dimension_scores(quality_assessment)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                dimension_scores, quality_assessment, synthesis_result
            )
            
            # Select adjustment strategy
            strategy = await self._select_adjustment_strategy(
                performance_metrics, context
            )
            
            # Perform weight adjustment
            adjustment_result = await self._perform_weight_adjustment(
                dimension_scores, performance_metrics, strategy
            )
            
            # Validate and normalize weights
            normalized_weights = self._validate_and_normalize_weights(
                adjustment_result["adjusted_weights"]
            )
            
            # Update weight configurations
            self._update_weight_configs(normalized_weights, performance_metrics)
            
            # Record adjustment
            adjustment_record = {
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy.value,
                "performance_metrics": performance_metrics,
                "original_weights": {name: config.current_weight for name, config in self.weight_configs.items()},
                "adjusted_weights": normalized_weights,
                "adjustment_magnitude": adjustment_result["adjustment_magnitude"],
                "quality_score": quality_assessment.get("overall_score", 0.0)
            }
            self.adjustment_history.append(adjustment_record)
            
            return {
                "success": True,
                "adjusted_weights": normalized_weights,
                "adjustment_strategy": strategy.value,
                "performance_metrics": performance_metrics,
                "adjustment_magnitude": adjustment_result["adjustment_magnitude"],
                "convergence_indicators": self._calculate_convergence_indicators(),
                "recommendations": adjustment_result["recommendations"]
            }
            
        except Exception as e:
            logger.error(f"Dynamic weight adjustment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "adjusted_weights": {name: config.current_weight for name, config in self.weight_configs.items()}
            }
    
    def _extract_dimension_scores(self, quality_assessment: Dict[str, Any]) -> Dict[str, float]:
        """Extract dimension scores from quality assessment."""
        dimension_scores = {}
        
        dimensions = quality_assessment.get("dimensions", {})
        for dim_name, dim_data in dimensions.items():
            if hasattr(dim_data, 'score'):
                dimension_scores[dim_name] = dim_data.score
            elif isinstance(dim_data, dict):
                dimension_scores[dim_name] = dim_data.get("score", 0.0)
        
        return dimension_scores
    
    def _calculate_performance_metrics(
        self,
        dimension_scores: Dict[str, float],
        quality_assessment: Dict[str, Any],
        synthesis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate performance metrics for weight adjustment."""
        
        overall_score = quality_assessment.get("overall_score", 0.0)
        
        # Calculate dimension performance
        dimension_performance = {}
        for dim_name, score in dimension_scores.items():
            weight_config = self.weight_configs.get(dim_name)
            if weight_config:
                # Calculate efficiency (score per unit weight)
                efficiency = score / weight_config.current_weight if weight_config.current_weight > 0 else 0
                
                # Calculate contribution to overall quality
                contribution = score * weight_config.current_weight
                
                dimension_performance[dim_name] = {
                    "score": score,
                    "efficiency": efficiency,
                    "contribution": contribution,
                    "weight": weight_config.current_weight
                }
        
        # Calculate overall metrics
        avg_efficiency = statistics.mean([
            perf["efficiency"] for perf in dimension_performance.values()
        ]) if dimension_performance else 0.0
        
        efficiency_variance = statistics.variance([
            perf["efficiency"] for perf in dimension_performance.values()
        ]) if len(dimension_performance) > 1 else 0.0
        
        # Identify overperforming and underperforming dimensions
        overperforming = [
            name for name, perf in dimension_performance.items()
            if perf["efficiency"] > avg_efficiency * 1.2
        ]
        
        underperforming = [
            name for name, perf in dimension_performance.items()
            if perf["efficiency"] < avg_efficiency * 0.8
        ]
        
        return {
            "overall_score": overall_score,
            "dimension_performance": dimension_performance,
            "average_efficiency": avg_efficiency,
            "efficiency_variance": efficiency_variance,
            "overperforming_dimensions": overperforming,
            "underperforming_dimensions": underperforming,
            "performance_balance": 1.0 / (1.0 + efficiency_variance)  # Higher balance = lower variance
        }
    
    async def _select_adjustment_strategy(
        self,
        performance_metrics: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> WeightAdjustmentStrategy:
        """Select optimal weight adjustment strategy."""
        
        overall_score = performance_metrics.get("overall_score", 0.0)
        performance_balance = performance_metrics.get("performance_balance", 0.0)
        
        # Strategy selection logic
        if overall_score > self.performance_thresholds["excellent"]:
            return WeightAdjustmentStrategy.CONSENSUS_BASED
        elif overall_score > self.performance_thresholds["good"]:
            return WeightAdjustmentStrategy.QUALITY_BASED
        elif performance_balance < 0.5:  # High imbalance
            return WeightAdjustmentStrategy.DIVERSITY_BASED
        else:
            return WeightAdjustmentStrategy.ADAPTIVE_HYBRID
    
    async def _perform_weight_adjustment(
        self,
        dimension_scores: Dict[str, float],
        performance_metrics: Dict[str, Any],
        strategy: WeightAdjustmentStrategy
    ) -> Dict[str, Any]:
        """Perform weight adjustment using selected strategy."""
        
        adjustment_methods = {
            WeightAdjustmentStrategy.QUALITY_BASED: self._quality_based_adjustment,
            WeightAdjustmentStrategy.PERFORMANCE_BASED: self._performance_based_adjustment,
            WeightAdjustmentStrategy.DIVERSITY_BASED: self._diversity_based_adjustment,
            WeightAdjustmentStrategy.CONSENSUS_BASED: self._consensus_based_adjustment,
            WeightAdjustmentStrategy.ADAPTIVE_HYBRID: self._adaptive_hybrid_adjustment
        }
        
        if strategy in adjustment_methods:
            return await adjustment_methods[strategy](
                dimension_scores, performance_metrics
            )
        else:
            return await self._adaptive_hybrid_adjustment(dimension_scores, performance_metrics)
    
    async def _quality_based_adjustment(
        self,
        dimension_scores: Dict[str, float],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Quality-based weight adjustment."""
        
        adjusted_weights = {}
        recommendations = []
        
        # Calculate target weights based on quality scores
        total_score = sum(dimension_scores.values()) if dimension_scores else 1.0
        
        for dim_name, score in dimension_scores.items():
            weight_config = self.weight_configs.get(dim_name)
            if not weight_config:
                continue
            
            # Calculate target weight based on quality score
            quality_ratio = score / total_score if total_score > 0 else 1.0 / len(dimension_scores)
            target_weight = quality_ratio * 2.0  # Amplify quality differences
            
            # Apply gradual adjustment
            current_weight = weight_config.current_weight
            adjustment = (target_weight - current_weight) * self.learning_rate
            new_weight = current_weight + adjustment
            
            # Apply bounds
            new_weight = max(weight_config.min_weight, min(weight_config.max_weight, new_weight))
            
            adjusted_weights[dim_name] = new_weight
        
        # Generate recommendations
        overperforming = performance_metrics.get("overperforming_dimensions", [])
        underperforming = performance_metrics.get("underperforming_dimensions", [])
        
        if overperforming:
            recommendations.append(f"增加权重：{', '.join(overperforming[:2])}")
        if underperforming:
            recommendations.append(f"减少权重：{', '.join(underperforming[:2])}")
        
        adjustment_magnitude = self._calculate_adjustment_magnitude(adjusted_weights)
        
        return {
            "adjusted_weights": adjusted_weights,
            "adjustment_magnitude": adjustment_magnitude,
            "recommendations": recommendations
        }
    
    async def _performance_based_adjustment(
        self,
        dimension_scores: Dict[str, float],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Performance-based weight adjustment."""
        
        adjusted_weights = {}
        recommendations = []
        
        dimension_performance = performance_metrics.get("dimension_performance", {})
        avg_efficiency = performance_metrics.get("average_efficiency", 0.0)
        
        for dim_name, perf_data in dimension_performance.items():
            weight_config = self.weight_configs.get(dim_name)
            if not weight_config:
                continue
            
            efficiency = perf_data.get("efficiency", 0.0)
            current_weight = weight_config.current_weight
            
            # Adjust based on efficiency relative to average
            efficiency_ratio = efficiency / avg_efficiency if avg_efficiency > 0 else 1.0
            
            # Calculate adjustment
            adjustment_factor = (efficiency_ratio - 1.0) * self.learning_rate
            new_weight = current_weight * (1.0 + adjustment_factor)
            
            # Apply bounds
            new_weight = max(weight_config.min_weight, min(weight_config.max_weight, new_weight))
            
            adjusted_weights[dim_name] = new_weight
        
        # Generate recommendations
        recommendations.append("基于性能效率调整权重分配")
        
        adjustment_magnitude = self._calculate_adjustment_magnitude(adjusted_weights)
        
        return {
            "adjusted_weights": adjusted_weights,
            "adjustment_magnitude": adjustment_magnitude,
            "recommendations": recommendations
        }
    
    async def _diversity_based_adjustment(
        self,
        dimension_scores: Dict[str, float],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Diversity-based weight adjustment for balance."""
        
        adjusted_weights = {}
        recommendations = []
        
        # Target more balanced distribution
        target_weight = 1.0 / len(self.weight_configs)
        
        for dim_name, weight_config in self.weight_configs.items():
            current_weight = weight_config.current_weight
            
            # Move towards target weight for balance
            adjustment = (target_weight - current_weight) * self.learning_rate * 2.0
            new_weight = current_weight + adjustment
            
            # Apply bounds
            new_weight = max(weight_config.min_weight, min(weight_config.max_weight, new_weight))
            
            adjusted_weights[dim_name] = new_weight
        
        recommendations.append("增加权重分配的多样性")
        
        adjustment_magnitude = self._calculate_adjustment_magnitude(adjusted_weights)
        
        return {
            "adjusted_weights": adjusted_weights,
            "adjustment_magnitude": adjustment_magnitude,
            "recommendations": recommendations
        }
    
    async def _consensus_based_adjustment(
        self,
        dimension_scores: Dict[str, float],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consensus-based weight adjustment for stable performance."""
        
        adjusted_weights = {}
        recommendations = []
        
        overall_score = performance_metrics.get("overall_score", 0.0)
        
        if overall_score > self.performance_thresholds["excellent"]:
            # Excellent performance - make small adjustments
            adjustment_factor = self.learning_rate * 0.5
            recommendations.append("优秀表现，微调权重以保持稳定")
        else:
            adjustment_factor = self.learning_rate
            recommendations.append("基于共识调整权重")
        
        for dim_name, weight_config in self.weight_configs.items():
            current_weight = weight_config.current_weight
            
            # Small adjustments towards default weights
            target_weight = weight_config.default_weight
            adjustment = (target_weight - current_weight) * adjustment_factor
            new_weight = current_weight + adjustment
            
            # Apply bounds
            new_weight = max(weight_config.min_weight, min(weight_config.max_weight, new_weight))
            
            adjusted_weights[dim_name] = new_weight
        
        adjustment_magnitude = self._calculate_adjustment_magnitude(adjusted_weights)
        
        return {
            "adjusted_weights": adjusted_weights,
            "adjustment_magnitude": adjustment_magnitude,
            "recommendations": recommendations
        }
    
    async def _adaptive_hybrid_adjustment(
        self,
        dimension_scores: Dict[str, float],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adaptive hybrid adjustment combining multiple strategies."""
        
        adjusted_weights = {}
        recommendations = []
        
        # Combine multiple adjustment factors
        quality_factor = await self._calculate_quality_factor(dimension_scores)
        performance_factor = await self._calculate_performance_factor(performance_metrics)
        diversity_factor = await self._calculate_diversity_factor(performance_metrics)
        
        for dim_name, weight_config in self.weight_configs.items():
            current_weight = weight_config.current_weight
            
            # Calculate combined adjustment
            quality_adjustment = quality_factor.get(dim_name, 0.0)
            performance_adjustment = performance_factor.get(dim_name, 0.0)
            diversity_adjustment = diversity_factor.get(dim_name, 0.0)
            
            # Weight the factors
            total_adjustment = (
                quality_adjustment * 0.4 +
                performance_adjustment * 0.4 +
                diversity_adjustment * 0.2
            )
            
            new_weight = current_weight + total_adjustment
            
            # Apply bounds
            new_weight = max(weight_config.min_weight, min(weight_config.max_weight, new_weight))
            
            adjusted_weights[dim_name] = new_weight
        
        recommendations.append("自适应混合策略调整权重")
        
        adjustment_magnitude = self._calculate_adjustment_magnitude(adjusted_weights)
        
        return {
            "adjusted_weights": adjusted_weights,
            "adjustment_magnitude": adjustment_magnitude,
            "recommendations": recommendations
        }
    
    async def _calculate_quality_factor(self, dimension_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate quality-based adjustment factors."""
        total_score = sum(dimension_scores.values()) if dimension_scores else 1.0
        
        factors = {}
        for dim_name, score in dimension_scores.items():
            weight_config = self.weight_configs.get(dim_name)
            if not weight_config:
                continue
            
            quality_ratio = score / total_score if total_score > 0 else 0.0
            adjustment = (quality_ratio - 1.0 / len(dimension_scores)) * self.learning_rate
            factors[dim_name] = adjustment
        
        return factors
    
    async def _calculate_performance_factor(self, performance_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance-based adjustment factors."""
        dimension_performance = performance_metrics.get("dimension_performance", {})
        avg_efficiency = performance_metrics.get("average_efficiency", 0.0)
        
        factors = {}
        for dim_name, perf_data in dimension_performance.items():
            efficiency = perf_data.get("efficiency", 0.0)
            efficiency_ratio = efficiency / avg_efficiency if avg_efficiency > 0 else 1.0
            
            adjustment = (efficiency_ratio - 1.0) * self.learning_rate * 0.5
            factors[dim_name] = adjustment
        
        return factors
    
    async def _calculate_diversity_factor(self, performance_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate diversity-based adjustment factors."""
        factors = {}
        target_weight = 1.0 / len(self.weight_configs)
        
        for dim_name, weight_config in self.weight_configs.items():
            current_weight = weight_config.current_weight
            adjustment = (target_weight - current_weight) * self.learning_rate * 0.3
            factors[dim_name] = adjustment
        
        return factors
    
    def _calculate_adjustment_magnitude(self, adjusted_weights: Dict[str, float]) -> float:
        """Calculate the magnitude of weight adjustments."""
        total_change = 0.0
        
        for dim_name, new_weight in adjusted_weights.items():
            weight_config = self.weight_configs.get(dim_name)
            if weight_config:
                change = abs(new_weight - weight_config.current_weight)
                total_change += change
        
        return total_change / len(adjusted_weights) if adjusted_weights else 0.0
    
    def _validate_and_normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Validate and normalize weights to sum to 1.0."""
        # Apply bounds
        normalized_weights = {}
        for dim_name, weight in weights.items():
            weight_config = self.weight_configs.get(dim_name)
            if weight_config:
                normalized_weights[dim_name] = max(
                    weight_config.min_weight,
                    min(weight_config.max_weight, weight)
                )
        
        # Normalize to sum to 1.0
        total_weight = sum(normalized_weights.values())
        if total_weight > 0:
            for dim_name in normalized_weights:
                normalized_weights[dim_name] /= total_weight
        
        return normalized_weights
    
    def _update_weight_configs(self, normalized_weights: Dict[str, float], performance_metrics: Dict[str, Any]):
        """Update weight configurations with new values."""
        for dim_name, new_weight in normalized_weights.items():
            weight_config = self.weight_configs.get(dim_name)
            if weight_config:
                weight_config.current_weight = new_weight
                weight_config.last_adjustment = datetime.now().isoformat()
                
                # Update performance history
                performance_score = performance_metrics.get("overall_score", 0.0)
                weight_config.performance_history.append(performance_score)
                
                # Keep history manageable
                if len(weight_config.performance_history) > 100:
                    weight_config.performance_history = weight_config.performance_history[-50:]
    
    def _calculate_convergence_indicators(self) -> Dict[str, Any]:
        """Calculate convergence indicators for weight stability."""
        if len(self.adjustment_history) < 3:
            return {"converged": False, "reason": "Insufficient history"}
        
        # Calculate recent adjustment magnitudes
        recent_adjustments = [
            record["adjustment_magnitude"] 
            for record in self.adjustment_history[-5:]
        ]
        
        avg_recent_adjustment = sum(recent_adjustments) / len(recent_adjustments)
        
        # Check convergence criteria
        converged = avg_recent_adjustment < 0.05  # Less than 5% average adjustment
        
        return {
            "converged": converged,
            "average_adjustment": avg_recent_adjustment,
            "adjustment_trend": "decreasing" if len(recent_adjustments) > 1 and recent_adjustments[-1] < recent_adjustments[0] else "stable"
        }
    
    def get_current_weights(self) -> Dict[str, float]:
        """Get current weight configuration."""
        return {name: config.current_weight for name, config in self.weight_configs.items()}
    
    def get_weight_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get weight adjustment history."""
        return self.adjustment_history.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.adjustment_history:
            return {"message": "No adjustment history available"}
        
        # Calculate weight stability
        weight_changes = []
        for i in range(1, len(self.adjustment_history)):
            prev_weights = self.adjustment_history[i-1]["adjusted_weights"]
            curr_weights = self.adjustment_history[i]["adjusted_weights"]
            
            total_change = sum(
                abs(curr_weights[dim] - prev_weights.get(dim, 0.0))
                for dim in curr_weights
            )
            weight_changes.append(total_change)
        
        avg_weight_change = sum(weight_changes) / len(weight_changes) if weight_changes else 0.0
        
        # Quality trend
        quality_scores = [record["quality_score"] for record in self.adjustment_history]
        quality_trend = "improving" if len(quality_scores) > 1 and quality_scores[-1] > quality_scores[0] else "stable"
        
        return {
            "total_adjustments": len(self.adjustment_history),
            "average_weight_change": avg_weight_change,
            "weight_stability": "high" if avg_weight_change < 0.1 else "medium" if avg_weight_change < 0.2 else "low",
            "quality_trend": quality_trend,
            "latest_adjustment": self.adjustment_history[-1] if self.adjustment_history else None
        }
    
    def reset_weights(self) -> Dict[str, float]:
        """Reset weights to default values."""
        for weight_config in self.weight_configs.values():
            weight_config.current_weight = weight_config.default_weight
            weight_config.last_adjustment = datetime.now().isoformat()
        
        return self.get_current_weights()
    
    def export_weights(self) -> Dict[str, Any]:
        """Export weight configuration."""
        return {
            "timestamp": datetime.now().isoformat(),
            "current_weights": self.get_current_weights(),
            "default_weights": self.default_weights,
            "adjustment_strategy": self.adjustment_strategy.value,
            "performance_summary": self.get_performance_summary()
        }