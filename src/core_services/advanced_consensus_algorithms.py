#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Consensus Algorithms

This module implements sophisticated consensus algorithms for collective intelligence
emergence, including dynamic algorithm selection, emergent insight detection,
and cognitive diversity preservation.

Requirements: 11.4, 11.5, 11.8, 11.10
"""

import logging
import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field


class ConsensusAlgorithmType(str, Enum):
    """Types of consensus algorithms."""
    WEIGHTED_VOTING = "weighted_voting"
    BAYESIAN_CONSENSUS = "bayesian_consensus"
    DELPHI_METHOD = "delphi_method"
    COGNITIVE_DIVERSITY_PRESERVING = "cognitive_diversity_preserving"
    EMERGENT_INSIGHT_DETECTION = "emergent_insight_detection"
    DYNAMIC_THRESHOLD = "dynamic_threshold"
    MULTI_CRITERIA_DECISION = "multi_criteria_decision"


@dataclass
class ConsensusInput:
    """Input data for consensus algorithms."""
    agent_id: str
    position: Union[str, float, Dict[str, Any]]
    confidence: float
    reasoning: Optional[str] = None
    evidence: Optional[List[str]] = None
    cognitive_profile: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


@dataclass
class ConsensusResult:
    """Result of consensus algorithm execution."""
    consensus_value: Union[str, float, Dict[str, Any]]
    confidence_level: float
    algorithm_used: ConsensusAlgorithmType
    participant_count: int
    diversity_score: float
    emergent_insights: List[str]
    reasoning_trace: Dict[str, Any]
    timestamp: datetime


class EmergentInsight(BaseModel):
    """Represents an emergent insight detected during consensus."""
    insight_id: str
    content: str
    emergence_score: float = Field(ge=0.0, le=1.0)
    contributing_agents: List[str]
    synthesis_pattern: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime


class AdvancedConsensusAlgorithm(ABC):
    """Abstract base class for advanced consensus algorithms."""
    
    def __init__(self, algorithm_type: ConsensusAlgorithmType):
        self.algorithm_type = algorithm_type
        self.logger = logging.getLogger(f"consensus.{algorithm_type.value}")
    
    @abstractmethod
    def calculate_consensus(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Calculate consensus from input positions."""
        pass
    
    @abstractmethod
    def get_algorithm_parameters(self) -> Dict[str, Any]:
        """Get algorithm-specific parameters."""
        pass
    
    def detect_emergent_insights(
        self,
        inputs: List[ConsensusInput],
        consensus_result: ConsensusResult
    ) -> List[EmergentInsight]:
        """Detect emergent insights from consensus process."""
        insights = []
        
        # Look for synthesis patterns that create new knowledge
        unique_positions = self._extract_unique_positions(inputs)
        if len(unique_positions) > 1:
            # Check if consensus creates something new
            synthesis_insight = self._detect_synthesis_insight(
                unique_positions, consensus_result
            )
            if synthesis_insight:
                insights.append(synthesis_insight)
        
        # Look for contradiction resolution insights
        contradictions = self._detect_contradictions(inputs)
        if contradictions:
            resolution_insight = self._detect_resolution_insight(
                contradictions, consensus_result
            )
            if resolution_insight:
                insights.append(resolution_insight)
        
        return insights
    
    def _extract_unique_positions(self, inputs: List[ConsensusInput]) -> List[Any]:
        """Extract unique positions from inputs."""
        positions = []
        for input_item in inputs:
            if input_item.position not in positions:
                positions.append(input_item.position)
        return positions
    
    def _detect_contradictions(self, inputs: List[ConsensusInput]) -> List[Tuple[ConsensusInput, ConsensusInput]]:
        """Detect contradictory positions in inputs."""
        contradictions = []
        for i, input1 in enumerate(inputs):
            for j, input2 in enumerate(inputs[i+1:], i+1):
                if self._are_contradictory(input1, input2):
                    contradictions.append((input1, input2))
        return contradictions
    
    def _are_contradictory(self, input1: ConsensusInput, input2: ConsensusInput) -> bool:
        """Check if two inputs are contradictory."""
        # Simple heuristic - can be made more sophisticated
        if isinstance(input1.position, str) and isinstance(input2.position, str):
            # Look for opposing keywords
            opposing_pairs = [
                ("agree", "disagree"),
                ("support", "oppose"),
                ("yes", "no"),
                ("true", "false"),
                ("positive", "negative")
            ]
            
            pos1_lower = input1.position.lower()
            pos2_lower = input2.position.lower()
            
            for pair in opposing_pairs:
                if (pair[0] in pos1_lower and pair[1] in pos2_lower) or \
                   (pair[1] in pos1_lower and pair[0] in pos2_lower):
                    return True
        
        return False
    
    def _detect_synthesis_insight(
        self,
        positions: List[Any],
        consensus_result: ConsensusResult
    ) -> Optional[EmergentInsight]:
        """Detect synthesis insights."""
        # Check if consensus result contains elements not in original positions
        if isinstance(consensus_result.consensus_value, str):
            consensus_words = set(consensus_result.consensus_value.lower().split())
            position_words = set()
            
            for pos in positions:
                if isinstance(pos, str):
                    position_words.update(pos.lower().split())
            
            new_concepts = consensus_words - position_words
            if new_concepts and len(new_concepts) > 2:  # Threshold for significance
                return EmergentInsight(
                    insight_id=f"synthesis_{datetime.now().timestamp()}",
                    content=f"Synthesis created new concepts: {', '.join(new_concepts)}",
                    emergence_score=min(len(new_concepts) / 10.0, 1.0),
                    contributing_agents=[],  # Would be filled by caller
                    synthesis_pattern="concept_emergence",
                    confidence=0.7,
                    timestamp=datetime.now()
                )
        
        return None
    
    def _detect_resolution_insight(
        self,
        contradictions: List[Tuple[ConsensusInput, ConsensusInput]],
        consensus_result: ConsensusResult
    ) -> Optional[EmergentInsight]:
        """Detect contradiction resolution insights."""
        if contradictions and consensus_result.confidence_level > 0.6:
            return EmergentInsight(
                insight_id=f"resolution_{datetime.now().timestamp()}",
                content=f"Successfully resolved {len(contradictions)} contradictions",
                emergence_score=min(len(contradictions) / 5.0, 1.0),
                contributing_agents=[],  # Would be filled by caller
                synthesis_pattern="contradiction_resolution",
                confidence=consensus_result.confidence_level,
                timestamp=datetime.now()
            )
        
        return None


class WeightedVotingConsensus(AdvancedConsensusAlgorithm):
    """Weighted voting consensus algorithm with cognitive diversity consideration."""
    
    def __init__(self, expertise_weight: float = 0.3, confidence_weight: float = 0.4, diversity_weight: float = 0.3):
        super().__init__(ConsensusAlgorithmType.WEIGHTED_VOTING)
        self.expertise_weight = expertise_weight
        self.confidence_weight = confidence_weight
        self.diversity_weight = diversity_weight
    
    def calculate_consensus(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Calculate weighted voting consensus."""
        self.logger.info(f"Calculating weighted voting consensus with {len(inputs)} inputs")
        
        if not inputs:
            raise ValueError("No inputs provided for consensus calculation")
        
        # Calculate weights for each input
        weights = self._calculate_weights(inputs, context)
        
        # Determine consensus based on input type
        if isinstance(inputs[0].position, str):
            consensus_value = self._calculate_categorical_consensus(inputs, weights)
        elif isinstance(inputs[0].position, (int, float)):
            consensus_value = self._calculate_numerical_consensus(inputs, weights)
        else:
            consensus_value = self._calculate_complex_consensus(inputs, weights)
        
        # Calculate overall confidence
        confidence_level = self._calculate_confidence(inputs, weights)
        
        # Calculate diversity score
        diversity_score = self._calculate_diversity_score(inputs)
        
        # Detect emergent insights
        result = ConsensusResult(
            consensus_value=consensus_value,
            confidence_level=confidence_level,
            algorithm_used=self.algorithm_type,
            participant_count=len(inputs),
            diversity_score=diversity_score,
            emergent_insights=[],
            reasoning_trace={
                "weights": weights,
                "method": "weighted_voting"
            },
            timestamp=datetime.now()
        )
        
        emergent_insights = self.detect_emergent_insights(inputs, result)
        result.emergent_insights = [insight.content for insight in emergent_insights]
        
        return result
    
    def _calculate_weights(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """Calculate weights for each input based on expertise, confidence, and diversity."""
        weights = []
        
        for input_item in inputs:
            # Base weight from confidence
            confidence_component = input_item.confidence * self.confidence_weight
            
            # Expertise component
            expertise_component = 0.5  # Default
            if input_item.cognitive_profile:
                domain_expertise = input_item.cognitive_profile.get("profile", {}).get("domain_expertise", {})
                if context and "domain" in context:
                    expertise_component = domain_expertise.get(context["domain"], 0.5)
                else:
                    # Average expertise across all domains
                    if domain_expertise:
                        expertise_component = sum(domain_expertise.values()) / len(domain_expertise)
            
            expertise_component *= self.expertise_weight
            
            # Diversity component (higher weight for more diverse perspectives)
            diversity_component = self._calculate_individual_diversity(input_item, inputs) * self.diversity_weight
            
            total_weight = confidence_component + expertise_component + diversity_component
            weights.append(total_weight)
        
        # Normalize weights
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
        else:
            weights = [1.0 / len(inputs)] * len(inputs)
        
        return weights
    
    def _calculate_individual_diversity(
        self,
        target_input: ConsensusInput,
        all_inputs: List[ConsensusInput]
    ) -> float:
        """Calculate how diverse an individual input is compared to others."""
        if not target_input.cognitive_profile:
            return 0.5  # Default diversity score
        
        diversity_scores = []
        target_profile = target_input.cognitive_profile
        
        for other_input in all_inputs:
            if other_input.agent_id == target_input.agent_id:
                continue
            
            if not other_input.cognitive_profile:
                continue
            
            # Calculate cognitive distance (simplified)
            distance = self._calculate_cognitive_distance(
                target_profile,
                other_input.cognitive_profile
            )
            diversity_scores.append(distance)
        
        return sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0.5
    
    def _calculate_cognitive_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate cognitive distance between two profiles."""
        # Simplified distance calculation
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
        all_values = set(values1.keys()) | set(values2.keys())
        if not all_values:
            return 0.0
        
        distance_sum = 0.0
        for value in all_values:
            v1 = values1.get(value, 0.0)
            v2 = values2.get(value, 0.0)
            distance_sum += (v1 - v2) ** 2
        
        return math.sqrt(distance_sum) / math.sqrt(len(all_values))
    
    def _calculate_categorical_consensus(
        self,
        inputs: List[ConsensusInput],
        weights: List[float]
    ) -> str:
        """Calculate consensus for categorical positions."""
        position_weights = {}
        
        for input_item, weight in zip(inputs, weights):
            position = input_item.position
            if position in position_weights:
                position_weights[position] += weight
            else:
                position_weights[position] = weight
        
        # Return position with highest weight
        return max(position_weights, key=position_weights.get)
    
    def _calculate_numerical_consensus(
        self,
        inputs: List[ConsensusInput],
        weights: List[float]
    ) -> float:
        """Calculate consensus for numerical positions."""
        weighted_sum = sum(input_item.position * weight for input_item, weight in zip(inputs, weights))
        return weighted_sum
    
    def _calculate_complex_consensus(
        self,
        inputs: List[ConsensusInput],
        weights: List[float]
    ) -> Dict[str, Any]:
        """Calculate consensus for complex positions."""
        # For complex positions, we'll create a weighted combination
        consensus = {"type": "complex_consensus", "components": []}
        
        for input_item, weight in zip(inputs, weights):
            consensus["components"].append({
                "position": input_item.position,
                "weight": weight,
                "agent_id": input_item.agent_id
            })
        
        return consensus
    
    def _calculate_confidence(
        self,
        inputs: List[ConsensusInput],
        weights: List[float]
    ) -> float:
        """Calculate overall confidence in consensus."""
        # Weighted average of individual confidences
        weighted_confidence = sum(input_item.confidence * weight for input_item, weight in zip(inputs, weights))
        
        # Adjust based on agreement level
        agreement_factor = self._calculate_agreement_factor(inputs)
        
        return min(weighted_confidence * agreement_factor, 1.0)
    
    def _calculate_agreement_factor(self, inputs: List[ConsensusInput]) -> float:
        """Calculate agreement factor based on position similarity."""
        if len(inputs) < 2:
            return 1.0
        
        if isinstance(inputs[0].position, str):
            # For categorical positions, calculate percentage agreement
            positions = [input_item.position for input_item in inputs]
            most_common_count = max(positions.count(pos) for pos in set(positions))
            return most_common_count / len(positions)
        
        elif isinstance(inputs[0].position, (int, float)):
            # For numerical positions, calculate based on standard deviation
            positions = [input_item.position for input_item in inputs]
            if len(set(positions)) == 1:
                return 1.0
            
            std_dev = np.std(positions)
            mean_val = np.mean(positions)
            if mean_val != 0:
                coefficient_of_variation = std_dev / abs(mean_val)
                return max(0.1, 1.0 - coefficient_of_variation)
            else:
                return max(0.1, 1.0 - std_dev)
        
        return 0.7  # Default for complex positions
    
    def _calculate_diversity_score(self, inputs: List[ConsensusInput]) -> float:
        """Calculate diversity score for the group."""
        if len(inputs) < 2:
            return 0.0
        
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
        
        return total_distance / pair_count if pair_count > 0 else 0.0
    
    def get_algorithm_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        return {
            "expertise_weight": self.expertise_weight,
            "confidence_weight": self.confidence_weight,
            "diversity_weight": self.diversity_weight
        }


class BayesianConsensus(AdvancedConsensusAlgorithm):
    """Bayesian consensus algorithm that updates beliefs based on evidence."""
    
    def __init__(self, prior_strength: float = 1.0):
        super().__init__(ConsensusAlgorithmType.BAYESIAN_CONSENSUS)
        self.prior_strength = prior_strength
    
    def calculate_consensus(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Calculate Bayesian consensus."""
        self.logger.info(f"Calculating Bayesian consensus with {len(inputs)} inputs")
        
        if not inputs:
            raise ValueError("No inputs provided for consensus calculation")
        
        # For numerical positions, use Bayesian updating
        if isinstance(inputs[0].position, (int, float)):
            consensus_value, confidence = self._bayesian_numerical_consensus(inputs)
        else:
            # For categorical positions, use Bayesian model averaging
            consensus_value, confidence = self._bayesian_categorical_consensus(inputs)
        
        diversity_score = self._calculate_diversity_score(inputs)
        
        result = ConsensusResult(
            consensus_value=consensus_value,
            confidence_level=confidence,
            algorithm_used=self.algorithm_type,
            participant_count=len(inputs),
            diversity_score=diversity_score,
            emergent_insights=[],
            reasoning_trace={
                "method": "bayesian_updating",
                "prior_strength": self.prior_strength
            },
            timestamp=datetime.now()
        )
        
        emergent_insights = self.detect_emergent_insights(inputs, result)
        result.emergent_insights = [insight.content for insight in emergent_insights]
        
        return result
    
    def _bayesian_numerical_consensus(
        self,
        inputs: List[ConsensusInput]
    ) -> Tuple[float, float]:
        """Calculate Bayesian consensus for numerical values."""
        # Use precision-weighted average (inverse variance weighting)
        precisions = []
        values = []
        
        for input_item in inputs:
            # Convert confidence to precision (inverse variance)
            # Higher confidence = higher precision = lower variance
            precision = input_item.confidence / (1.0 - input_item.confidence + 0.01)
            precisions.append(precision)
            values.append(input_item.position)
        
        # Bayesian update
        total_precision = sum(precisions)
        weighted_mean = sum(v * p for v, p in zip(values, precisions)) / total_precision
        
        # Confidence based on total precision
        confidence = min(total_precision / (total_precision + self.prior_strength), 0.95)
        
        return weighted_mean, confidence
    
    def _bayesian_categorical_consensus(
        self,
        inputs: List[ConsensusInput]
    ) -> Tuple[str, float]:
        """Calculate Bayesian consensus for categorical values."""
        # Count evidence for each category
        category_evidence = {}
        
        for input_item in inputs:
            category = input_item.position
            evidence_strength = input_item.confidence
            
            if category in category_evidence:
                category_evidence[category] += evidence_strength
            else:
                category_evidence[category] = evidence_strength
        
        # Apply Bayesian model averaging
        total_evidence = sum(category_evidence.values()) + self.prior_strength * len(category_evidence)
        
        # Find most probable category
        best_category = max(category_evidence, key=category_evidence.get)
        best_evidence = category_evidence[best_category]
        
        # Calculate posterior probability
        confidence = (best_evidence + self.prior_strength) / total_evidence
        
        return best_category, confidence
    
    def _calculate_diversity_score(self, inputs: List[ConsensusInput]) -> float:
        """Calculate diversity score."""
        # Simple diversity measure based on position variance
        if isinstance(inputs[0].position, (int, float)):
            positions = [input_item.position for input_item in inputs]
            return min(np.std(positions) / (np.mean(positions) + 0.01), 1.0)
        else:
            # For categorical, diversity is based on number of unique categories
            unique_positions = len(set(input_item.position for input_item in inputs))
            return min(unique_positions / len(inputs), 1.0)
    
    def get_algorithm_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        return {
            "prior_strength": self.prior_strength
        }


class CognitiveDiversityPreservingConsensus(AdvancedConsensusAlgorithm):
    """Consensus algorithm that explicitly preserves cognitive diversity."""
    
    def __init__(self, diversity_threshold: float = 0.3, minority_protection: float = 0.2):
        super().__init__(ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING)
        self.diversity_threshold = diversity_threshold
        self.minority_protection = minority_protection
    
    def calculate_consensus(
        self,
        inputs: List[ConsensusInput],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Calculate consensus while preserving cognitive diversity."""
        self.logger.info(f"Calculating diversity-preserving consensus with {len(inputs)} inputs")
        
        if not inputs:
            raise ValueError("No inputs provided for consensus calculation")
        
        # Group inputs by cognitive similarity
        cognitive_clusters = self._cluster_by_cognitive_similarity(inputs)
        
        # Calculate cluster representatives
        cluster_representatives = self._calculate_cluster_representatives(cognitive_clusters)
        
        # Ensure minority perspectives are preserved
        consensus_value = self._diversity_preserving_aggregation(cluster_representatives)
        
        # Calculate confidence with diversity penalty for homogeneous groups
        base_confidence = self._calculate_base_confidence(inputs)
        diversity_score = self._calculate_diversity_score(inputs)
        
        # Penalize low diversity
        diversity_bonus = min(diversity_score / self.diversity_threshold, 1.0)
        confidence_level = base_confidence * (0.7 + 0.3 * diversity_bonus)
        
        result = ConsensusResult(
            consensus_value=consensus_value,
            confidence_level=confidence_level,
            algorithm_used=self.algorithm_type,
            participant_count=len(inputs),
            diversity_score=diversity_score,
            emergent_insights=[],
            reasoning_trace={
                "method": "diversity_preserving",
                "clusters": len(cognitive_clusters),
                "diversity_bonus": diversity_bonus
            },
            timestamp=datetime.now()
        )
        
        emergent_insights = self.detect_emergent_insights(inputs, result)
        result.emergent_insights = [insight.content for insight in emergent_insights]
        
        return result
    
    def _cluster_by_cognitive_similarity(
        self,
        inputs: List[ConsensusInput]
    ) -> List[List[ConsensusInput]]:
        """Cluster inputs by cognitive similarity."""
        clusters = []
        
        for input_item in inputs:
            # Find the most similar existing cluster
            best_cluster = None
            best_similarity = -1
            
            for cluster in clusters:
                similarity = self._calculate_cluster_similarity(input_item, cluster)
                if similarity > best_similarity and similarity > 0.7:  # Similarity threshold
                    best_similarity = similarity
                    best_cluster = cluster
            
            if best_cluster:
                best_cluster.append(input_item)
            else:
                # Create new cluster
                clusters.append([input_item])
        
        return clusters
    
    def _calculate_cluster_similarity(
        self,
        input_item: ConsensusInput,
        cluster: List[ConsensusInput]
    ) -> float:
        """Calculate similarity between an input and a cluster."""
        if not input_item.cognitive_profile:
            return 0.5
        
        similarities = []
        for cluster_member in cluster:
            if cluster_member.cognitive_profile:
                # Calculate cognitive similarity (inverse of distance)
                distance = self._calculate_cognitive_distance(
                    input_item.cognitive_profile,
                    cluster_member.cognitive_profile
                )
                similarity = 1.0 - distance
                similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.5
    
    def _calculate_cognitive_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate cognitive distance between profiles."""
        # Reuse implementation from WeightedVotingConsensus
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
        all_values = set(values1.keys()) | set(values2.keys())
        if not all_values:
            return 0.0
        
        distance_sum = 0.0
        for value in all_values:
            v1 = values1.get(value, 0.0)
            v2 = values2.get(value, 0.0)
            distance_sum += (v1 - v2) ** 2
        
        return math.sqrt(distance_sum) / math.sqrt(len(all_values))
    
    def _calculate_cluster_representatives(
        self,
        clusters: List[List[ConsensusInput]]
    ) -> List[ConsensusInput]:
        """Calculate representative for each cluster."""
        representatives = []
        
        for cluster in clusters:
            if len(cluster) == 1:
                representatives.append(cluster[0])
            else:
                # Find the most representative member (highest average similarity to others)
                best_member = None
                best_score = -1
                
                for candidate in cluster:
                    similarity_sum = 0
                    for other in cluster:
                        if candidate.agent_id != other.agent_id:
                            if candidate.cognitive_profile and other.cognitive_profile:
                                distance = self._calculate_cognitive_distance(
                                    candidate.cognitive_profile,
                                    other.cognitive_profile
                                )
                                similarity_sum += (1.0 - distance)
                    
                    avg_similarity = similarity_sum / (len(cluster) - 1) if len(cluster) > 1 else 0
                    if avg_similarity > best_score:
                        best_score = avg_similarity
                        best_member = candidate
                
                if best_member:
                    representatives.append(best_member)
                else:
                    representatives.append(cluster[0])  # Fallback
        
        return representatives
    
    def _diversity_preserving_aggregation(
        self,
        representatives: List[ConsensusInput]
    ) -> Union[str, float, Dict[str, Any]]:
        """Aggregate representatives while preserving diversity."""
        if not representatives:
            return "No consensus"
        
        # For categorical positions
        if isinstance(representatives[0].position, str):
            # Give minority positions minimum representation
            position_counts = {}
            for rep in representatives:
                pos = rep.position
                position_counts[pos] = position_counts.get(pos, 0) + 1
            
            # If there's a clear majority but minorities exist, create a nuanced consensus
            total_reps = len(representatives)
            majority_pos = max(position_counts, key=position_counts.get)
            majority_count = position_counts[majority_pos]
            
            if majority_count / total_reps > 0.6 and len(position_counts) > 1:
                # Create nuanced consensus that acknowledges minorities
                minority_positions = [pos for pos, count in position_counts.items() 
                                    if pos != majority_pos and count / total_reps >= self.minority_protection]
                
                if minority_positions:
                    return f"{majority_pos} (with significant minority views: {', '.join(minority_positions)})"
                else:
                    return majority_pos
            else:
                return majority_pos
        
        # For numerical positions
        elif isinstance(representatives[0].position, (int, float)):
            # Weighted average with diversity consideration
            positions = [rep.position for rep in representatives]
            confidences = [rep.confidence for rep in representatives]
            
            # Give equal weight to each cluster representative
            return sum(positions) / len(positions)
        
        # For complex positions
        else:
            return {
                "type": "diversity_preserving_consensus",
                "representatives": [
                    {
                        "position": rep.position,
                        "agent_id": rep.agent_id,
                        "confidence": rep.confidence
                    }
                    for rep in representatives
                ]
            }
    
    def _calculate_base_confidence(self, inputs: List[ConsensusInput]) -> float:
        """Calculate base confidence from inputs."""
        return sum(input_item.confidence for input_item in inputs) / len(inputs)
    
    def _calculate_diversity_score(self, inputs: List[ConsensusInput]) -> float:
        """Calculate diversity score for the group."""
        if len(inputs) < 2:
            return 0.0
        
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
        
        return total_distance / pair_count if pair_count > 0 else 0.0
    
    def get_algorithm_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        return {
            "diversity_threshold": self.diversity_threshold,
            "minority_protection": self.minority_protection
        }