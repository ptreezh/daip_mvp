#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consensus Algorithm Selector

This module implements dynamic algorithm selection for consensus processes,
choosing the most appropriate algorithm based on context, participant
characteristics, and task requirements.

Requirements: 11.4, 11.5, 11.8, 11.10
"""

import logging
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from enum import Enum

from .advanced_consensus_algorithms import (
    AdvancedConsensusAlgorithm,
    ConsensusAlgorithmType,
    ConsensusInput,
    ConsensusResult,
    WeightedVotingConsensus,
    BayesianConsensus,
    CognitiveDiversityPreservingConsensus
)


class SelectionCriteria(str, Enum):
    """Criteria for algorithm selection."""
    PARTICIPANT_COUNT = "participant_count"
    DIVERSITY_LEVEL = "diversity_level"
    CONFIDENCE_VARIANCE = "confidence_variance"
    POSITION_TYPE = "position_type"
    TASK_COMPLEXITY = "task_complexity"
    TIME_CONSTRAINT = "time_constraint"
    ACCURACY_REQUIREMENT = "accuracy_requirement"


@dataclass
class SelectionContext:
    """Context information for algorithm selection."""
    participant_count: int
    diversity_score: float
    confidence_variance: float
    position_type: str  # "categorical", "numerical", "complex"
    task_complexity: float  # 0.0 to 1.0
    time_constraint: float  # 0.0 (no constraint) to 1.0 (very tight)
    accuracy_requirement: float  # 0.0 to 1.0
    domain: Optional[str] = None
    previous_algorithm_performance: Optional[Dict[str, float]] = None


class AlgorithmPerformanceTracker:
    """Tracks performance of different algorithms over time."""
    
    def __init__(self):
        self.performance_history: Dict[ConsensusAlgorithmType, List[float]] = {}
        self.context_performance: Dict[str, Dict[ConsensusAlgorithmType, List[float]]] = {}
        self.logger = logging.getLogger("algorithm_performance_tracker")
    
    def record_performance(
        self,
        algorithm_type: ConsensusAlgorithmType,
        performance_score: float,
        context: SelectionContext
    ) -> None:
        """Record performance of an algorithm."""
        # Record overall performance
        if algorithm_type not in self.performance_history:
            self.performance_history[algorithm_type] = []
        self.performance_history[algorithm_type].append(performance_score)
        
        # Record context-specific performance
        context_key = self._generate_context_key(context)
        if context_key not in self.context_performance:
            self.context_performance[context_key] = {}
        
        if algorithm_type not in self.context_performance[context_key]:
            self.context_performance[context_key][algorithm_type] = []
        
        self.context_performance[context_key][algorithm_type].append(performance_score)
        
        self.logger.debug(f"Recorded performance {performance_score:.3f} for {algorithm_type.value} in context {context_key}")
    
    def get_algorithm_performance(
        self,
        algorithm_type: ConsensusAlgorithmType,
        context: Optional[SelectionContext] = None
    ) -> float:
        """Get average performance of an algorithm."""
        if context:
            context_key = self._generate_context_key(context)
            if (context_key in self.context_performance and 
                algorithm_type in self.context_performance[context_key]):
                scores = self.context_performance[context_key][algorithm_type]
                return sum(scores) / len(scores)
        
        # Fall back to overall performance
        if algorithm_type in self.performance_history:
            scores = self.performance_history[algorithm_type]
            return sum(scores) / len(scores)
        
        return 0.5  # Default performance score
    
    def _generate_context_key(self, context: SelectionContext) -> str:
        """Generate a key for context-specific performance tracking."""
        # Discretize continuous values for grouping
        participant_group = "small" if context.participant_count < 5 else "medium" if context.participant_count < 10 else "large"
        diversity_group = "low" if context.diversity_score < 0.3 else "medium" if context.diversity_score < 0.7 else "high"
        complexity_group = "simple" if context.task_complexity < 0.3 else "medium" if context.task_complexity < 0.7 else "complex"
        
        return f"{participant_group}_{diversity_group}_{context.position_type}_{complexity_group}"


class ConsensusAlgorithmSelector:
    """Selects the most appropriate consensus algorithm based on context."""
    
    def __init__(self):
        self.logger = logging.getLogger("consensus_algorithm_selector")
        self.performance_tracker = AlgorithmPerformanceTracker()
        
        # Available algorithms
        self.algorithms: Dict[ConsensusAlgorithmType, Type[AdvancedConsensusAlgorithm]] = {
            ConsensusAlgorithmType.WEIGHTED_VOTING: WeightedVotingConsensus,
            ConsensusAlgorithmType.BAYESIAN_CONSENSUS: BayesianConsensus,
            ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: CognitiveDiversityPreservingConsensus
        }
        
        # Selection rules (can be learned over time)
        self.selection_rules = self._initialize_selection_rules()
    
    def _initialize_selection_rules(self) -> Dict[str, Dict[ConsensusAlgorithmType, float]]:
        """Initialize algorithm selection rules."""
        return {
            # Rules based on participant count
            "small_group": {  # < 5 participants
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.8,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.7,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 0.6
            },
            "medium_group": {  # 5-10 participants
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.7,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.8,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 0.9
            },
            "large_group": {  # > 10 participants
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.6,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.7,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 0.9
            },
            
            # Rules based on diversity level
            "low_diversity": {  # < 0.3
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.8,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.9,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 0.5
            },
            "high_diversity": {  # > 0.7
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.6,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.7,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 1.0
            },
            
            # Rules based on position type
            "numerical": {
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.7,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.9,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 0.8
            },
            "categorical": {
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.9,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.8,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 0.9
            },
            "complex": {
                ConsensusAlgorithmType.WEIGHTED_VOTING: 0.6,
                ConsensusAlgorithmType.BAYESIAN_CONSENSUS: 0.7,
                ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: 0.9
            }
        }
    
    def select_algorithm(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusAlgorithmType:
        """Select the most appropriate consensus algorithm."""
        self.logger.info(f"Selecting consensus algorithm for {len(inputs)} inputs")
        
        # Analyze the selection context
        selection_context = self._analyze_context(inputs, context)
        
        # Calculate scores for each algorithm
        algorithm_scores = self._calculate_algorithm_scores(selection_context)
        
        # Select the algorithm with the highest score
        best_algorithm = max(algorithm_scores, key=algorithm_scores.get)
        
        self.logger.info(f"Selected algorithm: {best_algorithm.value} (score: {algorithm_scores[best_algorithm]:.3f})")
        
        return best_algorithm
    
    def _analyze_context(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> SelectionContext:
        """Analyze the context for algorithm selection."""
        # Determine position type
        if inputs:
            first_position = inputs[0].position
            if isinstance(first_position, (int, float)):
                position_type = "numerical"
            elif isinstance(first_position, str):
                position_type = "categorical"
            else:
                position_type = "complex"
        else:
            position_type = "categorical"
        
        # Calculate diversity score
        diversity_score = self._calculate_diversity_score(inputs)
        
        # Calculate confidence variance
        confidences = [input_item.confidence for input_item in inputs]
        confidence_variance = self._calculate_variance(confidences) if confidences else 0.0
        
        # Extract context parameters
        task_complexity = context.get("task_complexity", 0.5) if context else 0.5
        time_constraint = context.get("time_constraint", 0.0) if context else 0.0
        accuracy_requirement = context.get("accuracy_requirement", 0.7) if context else 0.7
        domain = context.get("domain") if context else None
        
        return SelectionContext(
            participant_count=len(inputs),
            diversity_score=diversity_score,
            confidence_variance=confidence_variance,
            position_type=position_type,
            task_complexity=task_complexity,
            time_constraint=time_constraint,
            accuracy_requirement=accuracy_requirement,
            domain=domain
        )
    
    def _calculate_diversity_score(self, inputs: List[ConsensusInput]) -> float:
        """Calculate diversity score for inputs."""
        if len(inputs) < 2:
            return 0.0
        
        # Simple diversity measure based on cognitive profiles
        total_distance = 0.0
        pair_count = 0
        
        for i in range(len(inputs)):
            for j in range(i + 1, len(inputs)):
                if inputs[i].cognitive_profile and inputs[j].cognitive_profile:
                    distance = self._calculate_cognitive_distance(
                        inputs[i].cognitive_profile,
                        inputs[j].cognitive_profile
                    )
                    total_distance += distance
                    pair_count += 1
        
        return total_distance / pair_count if pair_count > 0 else 0.5
    
    def _calculate_cognitive_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate cognitive distance between profiles."""
        distance = 0.0
        
        # Compare reasoning styles
        reasoning1 = profile1.get("profile", {}).get("reasoning_style", "analytical")
        reasoning2 = profile2.get("profile", {}).get("reasoning_style", "analytical")
        if reasoning1 != reasoning2:
            distance += 0.3
        
        # Compare values
        values1 = profile1.get("profile", {}).get("values", {})
        values2 = profile2.get("profile", {}).get("values", {})
        if values1 and values2:
            value_distance = self._calculate_value_distance(values1, values2)
            distance += value_distance * 0.4
        
        # Compare biases
        biases1 = set(profile1.get("profile", {}).get("cognitive_biases", []))
        biases2 = set(profile2.get("profile", {}).get("cognitive_biases", []))
        bias_distance = 1.0 - (len(biases1 & biases2) / len(biases1 | biases2)) if (biases1 | biases2) else 0.0
        distance += bias_distance * 0.3
        
        return min(distance, 1.0)
    
    def _calculate_value_distance(self, values1: Dict[str, float], values2: Dict[str, float]) -> float:
        """Calculate distance between value systems."""
        import math
        
        all_values = set(values1.keys()) | set(values2.keys())
        if not all_values:
            return 0.0
        
        distance_sum = 0.0
        for value in all_values:
            v1 = values1.get(value, 0.0)
            v2 = values2.get(value, 0.0)
            distance_sum += (v1 - v2) ** 2
        
        return math.sqrt(distance_sum) / math.sqrt(len(all_values))
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_algorithm_scores(self, context: SelectionContext) -> Dict[ConsensusAlgorithmType, float]:
        """Calculate scores for each algorithm based on context."""
        scores = {}
        
        for algorithm_type in self.algorithms:
            score = 0.0
            
            # Base score from selection rules
            score += self._apply_selection_rules(algorithm_type, context)
            
            # Historical performance score
            performance_score = self.performance_tracker.get_algorithm_performance(algorithm_type, context)
            score += performance_score * 0.3  # Weight for historical performance
            
            # Context-specific adjustments
            score += self._apply_context_adjustments(algorithm_type, context)
            
            scores[algorithm_type] = score
        
        return scores
    
    def _apply_selection_rules(
        self,
        algorithm_type: ConsensusAlgorithmType,
        context: SelectionContext
    ) -> float:
        """Apply selection rules to calculate base score."""
        score = 0.0
        rule_count = 0
        
        # Participant count rules
        if context.participant_count < 5:
            score += self.selection_rules["small_group"].get(algorithm_type, 0.5)
            rule_count += 1
        elif context.participant_count < 10:
            score += self.selection_rules["medium_group"].get(algorithm_type, 0.5)
            rule_count += 1
        else:
            score += self.selection_rules["large_group"].get(algorithm_type, 0.5)
            rule_count += 1
        
        # Diversity rules
        if context.diversity_score < 0.3:
            score += self.selection_rules["low_diversity"].get(algorithm_type, 0.5)
            rule_count += 1
        elif context.diversity_score > 0.7:
            score += self.selection_rules["high_diversity"].get(algorithm_type, 0.5)
            rule_count += 1
        
        # Position type rules
        if context.position_type in self.selection_rules:
            score += self.selection_rules[context.position_type].get(algorithm_type, 0.5)
            rule_count += 1
        
        return score / rule_count if rule_count > 0 else 0.5
    
    def _apply_context_adjustments(
        self,
        algorithm_type: ConsensusAlgorithmType,
        context: SelectionContext
    ) -> float:
        """Apply context-specific adjustments to algorithm scores."""
        adjustment = 0.0
        
        # Time constraint adjustments
        if context.time_constraint > 0.7:
            # Favor simpler algorithms under time pressure
            if algorithm_type == ConsensusAlgorithmType.WEIGHTED_VOTING:
                adjustment += 0.2
            elif algorithm_type == ConsensusAlgorithmType.BAYESIAN_CONSENSUS:
                adjustment += 0.1
        
        # Accuracy requirement adjustments
        if context.accuracy_requirement > 0.8:
            # Favor more sophisticated algorithms for high accuracy
            if algorithm_type == ConsensusAlgorithmType.BAYESIAN_CONSENSUS:
                adjustment += 0.2
            elif algorithm_type == ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING:
                adjustment += 0.15
        
        # Task complexity adjustments
        if context.task_complexity > 0.7:
            # Favor diversity-preserving algorithms for complex tasks
            if algorithm_type == ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING:
                adjustment += 0.25
        
        # Confidence variance adjustments
        if context.confidence_variance > 0.2:
            # High confidence variance suggests need for sophisticated handling
            if algorithm_type == ConsensusAlgorithmType.BAYESIAN_CONSENSUS:
                adjustment += 0.15
        
        return adjustment
    
    def create_algorithm_instance(
        self,
        algorithm_type: ConsensusAlgorithmType,
        context: SelectionContext
    ) -> AdvancedConsensusAlgorithm:
        """Create an instance of the selected algorithm with optimized parameters."""
        algorithm_class = self.algorithms[algorithm_type]
        
        # Create algorithm with context-optimized parameters
        if algorithm_type == ConsensusAlgorithmType.WEIGHTED_VOTING:
            # Adjust weights based on context
            expertise_weight = 0.4 if context.accuracy_requirement > 0.8 else 0.3
            diversity_weight = 0.4 if context.diversity_score > 0.7 else 0.3
            confidence_weight = 1.0 - expertise_weight - diversity_weight
            
            return algorithm_class(
                expertise_weight=expertise_weight,
                confidence_weight=confidence_weight,
                diversity_weight=diversity_weight
            )
        
        elif algorithm_type == ConsensusAlgorithmType.BAYESIAN_CONSENSUS:
            # Adjust prior strength based on context
            prior_strength = 2.0 if context.confidence_variance > 0.2 else 1.0
            return algorithm_class(prior_strength=prior_strength)
        
        elif algorithm_type == ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING:
            # Adjust diversity parameters based on context
            diversity_threshold = 0.2 if context.diversity_score < 0.3 else 0.3
            minority_protection = 0.3 if context.participant_count > 10 else 0.2
            
            return algorithm_class(
                diversity_threshold=diversity_threshold,
                minority_protection=minority_protection
            )
        
        else:
            return algorithm_class()
    
    def record_algorithm_performance(
        self,
        algorithm_type: ConsensusAlgorithmType,
        result: ConsensusResult,
        context: SelectionContext,
        user_satisfaction: Optional[float] = None
    ) -> None:
        """Record the performance of an algorithm for future selection."""
        # Calculate performance score based on multiple factors
        performance_score = 0.0
        
        # Confidence level contributes to performance
        performance_score += result.confidence_level * 0.4
        
        # Diversity preservation contributes to performance
        performance_score += result.diversity_score * 0.3
        
        # User satisfaction (if available) is highly weighted
        if user_satisfaction is not None:
            performance_score += user_satisfaction * 0.3
        else:
            # Default satisfaction based on confidence and diversity
            performance_score += (result.confidence_level + result.diversity_score) / 2 * 0.3
        
        # Record the performance
        self.performance_tracker.record_performance(
            algorithm_type,
            performance_score,
            context
        )
    
    def get_algorithm_recommendations(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[ConsensusAlgorithmType, float]:
        """Get recommendations for all algorithms with their scores."""
        selection_context = self._analyze_context(inputs, context)
        return self._calculate_algorithm_scores(selection_context)
    
    def update_selection_rules(
        self,
        performance_data: Dict[str, Dict[ConsensusAlgorithmType, float]]
    ) -> None:
        """Update selection rules based on performance data."""
        # Simple rule updating - can be made more sophisticated
        for context_key, algorithm_performances in performance_data.items():
            if context_key in self.selection_rules:
                for algorithm_type, performance in algorithm_performances.items():
                    if algorithm_type in self.selection_rules[context_key]:
                        # Exponential moving average update
                        current_score = self.selection_rules[context_key][algorithm_type]
                        updated_score = 0.9 * current_score + 0.1 * performance
                        self.selection_rules[context_key][algorithm_type] = updated_score
        
        self.logger.info("Updated selection rules based on performance data")