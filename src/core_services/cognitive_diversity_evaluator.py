#!/usr/bin/env python3
"""Cognitive Diversity Evaluator

This module implements metrics and algorithms for measuring cognitive diversity
among virtual agents, including cognitive distance calculation, diversity scoring,
and longitudinal consistency tracking.

Requirements: 11.3, 11.4, 11.9
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field


class DiversityMetric(str, Enum):
    """Types of cognitive diversity metrics."""

    REASONING_STYLE = "reasoning_style"
    VALUE_SYSTEM = "value_system"
    EPISTEMOLOGICAL = "epistemological"
    BELIEF_STRUCTURE = "belief_structure"
    COGNITIVE_BIAS = "cognitive_bias"
    DOMAIN_EXPERTISE = "domain_expertise"


@dataclass
class CognitiveDistance:
    """Represents the cognitive distance between two agents."""

    agent_pair: Tuple[str, str]
    overall_distance: float
    metric_distances: Dict[DiversityMetric, float]
    timestamp: datetime


class DiversityScore(BaseModel):
    """Represents a diversity score for a group of agents."""

    group_id: str
    agents: List[str]
    overall_score: float = Field(ge=0.0, le=1.0)
    metric_scores: Dict[DiversityMetric, float] = Field(default_factory=dict)
    timestamp: datetime
    sample_size: int


class ConsistencyTracker(BaseModel):
    """Tracks longitudinal consistency of an agent's cognitive profile."""

    agent_id: str
    baseline_profile: Dict[str, Any]
    consistency_scores: List[Tuple[datetime, float]] = Field(default_factory=list)
    drift_indicators: Dict[str, float] = Field(default_factory=dict)
    last_updated: datetime


class CognitiveDiversityEvaluator:
    """Evaluates cognitive diversity among virtual agents.
    
    This class implements various metrics for measuring cognitive distance
    between agents, calculating diversity scores for groups, and tracking
    longitudinal consistency of individual agents.
    """

    def __init__(self):
        """Initialize the cognitive diversity evaluator."""
        self.logger = logging.getLogger("cognitive_diversity_evaluator")
        self.distance_cache: Dict[Tuple[str, str], CognitiveDistance] = {}
        self.consistency_trackers: Dict[str, ConsistencyTracker] = {}
        self.diversity_history: List[DiversityScore] = []

        # Weights for different diversity metrics
        self.metric_weights = {
            DiversityMetric.REASONING_STYLE: 0.25,
            DiversityMetric.VALUE_SYSTEM: 0.20,
            DiversityMetric.EPISTEMOLOGICAL: 0.20,
            DiversityMetric.BELIEF_STRUCTURE: 0.15,
            DiversityMetric.COGNITIVE_BIAS: 0.10,
            DiversityMetric.DOMAIN_EXPERTISE: 0.10
        }

        self.logger.info("Cognitive diversity evaluator initialized")

    def calculate_cognitive_distance(
        self,
        agent1_profile: Dict[str, Any],
        agent2_profile: Dict[str, Any],
        agent1_id: str,
        agent2_id: str
    ) -> CognitiveDistance:
        """Calculate cognitive distance between two agents.
        
        Args:
            agent1_profile: Cognitive profile of first agent
            agent2_profile: Cognitive profile of second agent
            agent1_id: ID of first agent
            agent2_id: ID of second agent
            
        Returns:
            CognitiveDistance object containing distance metrics

        """
        self.logger.debug(f"Calculating cognitive distance between {agent1_id} and {agent2_id}")

        # Calculate distance for each metric
        metric_distances = {}

        # Reasoning style distance
        metric_distances[DiversityMetric.REASONING_STYLE] = self._calculate_reasoning_distance(
            agent1_profile, agent2_profile
        )

        # Value system distance
        metric_distances[DiversityMetric.VALUE_SYSTEM] = self._calculate_value_distance(
            agent1_profile, agent2_profile
        )

        # Epistemological distance
        metric_distances[DiversityMetric.EPISTEMOLOGICAL] = self._calculate_epistemological_distance(
            agent1_profile, agent2_profile
        )

        # Belief structure distance
        metric_distances[DiversityMetric.BELIEF_STRUCTURE] = self._calculate_belief_structure_distance(
            agent1_profile, agent2_profile
        )

        # Cognitive bias distance
        metric_distances[DiversityMetric.COGNITIVE_BIAS] = self._calculate_bias_distance(
            agent1_profile, agent2_profile
        )

        # Domain expertise distance
        metric_distances[DiversityMetric.DOMAIN_EXPERTISE] = self._calculate_expertise_distance(
            agent1_profile, agent2_profile
        )

        # Calculate overall distance as weighted average
        overall_distance = sum(
            distance * self.metric_weights[metric]
            for metric, distance in metric_distances.items()
        )

        # Create cognitive distance object
        cognitive_distance = CognitiveDistance(
            agent_pair=(agent1_id, agent2_id),
            overall_distance=overall_distance,
            metric_distances=metric_distances,
            timestamp=datetime.now()
        )

        # Cache the result
        cache_key = tuple(sorted([agent1_id, agent2_id]))
        self.distance_cache[cache_key] = cognitive_distance

        self.logger.debug(f"Cognitive distance calculated: {overall_distance:.3f}")
        return cognitive_distance

    def _calculate_reasoning_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate distance between reasoning styles."""
        reasoning1 = profile1.get("profile", {}).get("reasoning_style", "analytical")
        reasoning2 = profile2.get("profile", {}).get("reasoning_style", "analytical")

        # Define reasoning style similarity matrix
        style_similarities = {
            ("analytical", "analytical"): 0.0,
            ("analytical", "intuitive"): 0.8,
            ("analytical", "pragmatic"): 0.6,
            ("intuitive", "intuitive"): 0.0,
            ("intuitive", "pragmatic"): 0.7,
            ("pragmatic", "pragmatic"): 0.0
        }

        # Get similarity (symmetric)
        key = tuple(sorted([reasoning1, reasoning2]))
        return style_similarities.get(key, 1.0)  # Default to maximum distance

    def _calculate_value_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate distance between value systems."""
        values1 = profile1.get("profile", {}).get("values", {})
        values2 = profile2.get("profile", {}).get("values", {})

        # Get all unique values
        all_values = set(values1.keys()) | set(values2.keys())

        if not all_values:
            return 0.0

        # Calculate Euclidean distance between value vectors
        distance_sum = 0.0
        for value in all_values:
            v1 = values1.get(value, 0.0)
            v2 = values2.get(value, 0.0)
            distance_sum += (v1 - v2) ** 2

        # Normalize by number of values and maximum possible distance
        max_distance = len(all_values)  # Maximum distance when all values are 1.0 vs 0.0
        return math.sqrt(distance_sum) / math.sqrt(max_distance) if max_distance > 0 else 0.0

    def _calculate_epistemological_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate distance between epistemological approaches."""
        approach1 = profile1.get("profile", {}).get("epistemological_approach", "empirical")
        approach2 = profile2.get("profile", {}).get("epistemological_approach", "empirical")

        # Define epistemological approach similarity matrix
        approach_similarities = {
            ("empirical", "empirical"): 0.0,
            ("empirical", "rationalist"): 0.7,
            ("empirical", "constructivist"): 0.5,
            ("rationalist", "rationalist"): 0.0,
            ("rationalist", "constructivist"): 0.6,
            ("constructivist", "constructivist"): 0.0
        }

        # Get similarity (symmetric)
        key = tuple(sorted([approach1, approach2]))
        return approach_similarities.get(key, 1.0)  # Default to maximum distance

    def _calculate_belief_structure_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate distance between belief structures."""
        structure1 = profile1.get("profile", {}).get("belief_structure", "hierarchical")
        structure2 = profile2.get("profile", {}).get("belief_structure", "hierarchical")

        # Define belief structure similarity matrix
        structure_similarities = {
            ("hierarchical", "hierarchical"): 0.0,
            ("hierarchical", "networked"): 0.6,
            ("hierarchical", "bayesian"): 0.4,
            ("networked", "networked"): 0.0,
            ("networked", "bayesian"): 0.5,
            ("bayesian", "bayesian"): 0.0
        }

        # Get similarity (symmetric)
        key = tuple(sorted([structure1, structure2]))
        return structure_similarities.get(key, 1.0)  # Default to maximum distance

    def _calculate_bias_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate distance between cognitive bias sets."""
        biases1 = set(profile1.get("profile", {}).get("cognitive_biases", []))
        biases2 = set(profile2.get("profile", {}).get("cognitive_biases", []))

        # Calculate Jaccard distance (1 - Jaccard similarity)
        intersection = len(biases1 & biases2)
        union = len(biases1 | biases2)

        if union == 0:
            return 0.0  # Both have no biases

        jaccard_similarity = intersection / union
        return 1.0 - jaccard_similarity

    def _calculate_expertise_distance(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> float:
        """Calculate distance between domain expertise profiles."""
        expertise1 = profile1.get("profile", {}).get("domain_expertise", {})
        expertise2 = profile2.get("profile", {}).get("domain_expertise", {})

        # Get all unique domains
        all_domains = set(expertise1.keys()) | set(expertise2.keys())

        if not all_domains:
            return 0.0

        # Calculate Euclidean distance between expertise vectors
        distance_sum = 0.0
        for domain in all_domains:
            e1 = expertise1.get(domain, 0.0)
            e2 = expertise2.get(domain, 0.0)
            distance_sum += (e1 - e2) ** 2

        # Normalize by number of domains and maximum possible distance
        max_distance = len(all_domains)  # Maximum distance when all expertise are 1.0 vs 0.0
        return math.sqrt(distance_sum) / math.sqrt(max_distance) if max_distance > 0 else 0.0

    def calculate_group_diversity(
        self,
        agent_profiles: Dict[str, Dict[str, Any]],
        group_id: str = "default"
    ) -> DiversityScore:
        """Calculate diversity score for a group of agents.
        
        Args:
            agent_profiles: Dictionary mapping agent IDs to their cognitive profiles
            group_id: Identifier for this group
            
        Returns:
            DiversityScore object containing diversity metrics

        """
        self.logger.info(f"Calculating diversity for group '{group_id}' with {len(agent_profiles)} agents")

        agent_ids = list(agent_profiles.keys())

        if len(agent_ids) < 2:
            self.logger.warning(f"Group '{group_id}' has fewer than 2 agents, diversity score will be 0")
            return DiversityScore(
                group_id=group_id,
                agents=agent_ids,
                overall_score=0.0,
                metric_scores=dict.fromkeys(DiversityMetric, 0.0),
                timestamp=datetime.now(),
                sample_size=len(agent_ids)
            )

        # Calculate pairwise distances
        distances = []
        metric_distance_sums = dict.fromkeys(DiversityMetric, 0.0)
        pair_count = 0

        for i in range(len(agent_ids)):
            for j in range(i + 1, len(agent_ids)):
                agent1_id = agent_ids[i]
                agent2_id = agent_ids[j]

                # Check cache first
                cache_key = tuple(sorted([agent1_id, agent2_id]))
                if cache_key in self.distance_cache:
                    distance = self.distance_cache[cache_key]
                else:
                    distance = self.calculate_cognitive_distance(
                        agent_profiles[agent1_id],
                        agent_profiles[agent2_id],
                        agent1_id,
                        agent2_id
                    )

                distances.append(distance.overall_distance)

                # Accumulate metric distances
                for metric, metric_distance in distance.metric_distances.items():
                    metric_distance_sums[metric] += metric_distance

                pair_count += 1

        # Calculate average distances
        overall_score = sum(distances) / len(distances) if distances else 0.0
        metric_scores = {
            metric: distance_sum / pair_count if pair_count > 0 else 0.0
            for metric, distance_sum in metric_distance_sums.items()
        }

        # Create diversity score
        diversity_score = DiversityScore(
            group_id=group_id,
            agents=agent_ids,
            overall_score=overall_score,
            metric_scores=metric_scores,
            timestamp=datetime.now(),
            sample_size=len(agent_ids)
        )

        # Store in history
        self.diversity_history.append(diversity_score)

        self.logger.info(f"Group diversity calculated: {overall_score:.3f}")
        return diversity_score

    def track_longitudinal_consistency(
        self,
        agent_id: str,
        current_profile: Dict[str, Any],
        baseline_profile: Optional[Dict[str, Any]] = None
    ) -> ConsistencyTracker:
        """Track longitudinal consistency of an agent's cognitive profile.
        
        Args:
            agent_id: ID of the agent to track
            current_profile: Current cognitive profile of the agent
            baseline_profile: Baseline profile to compare against (optional)
            
        Returns:
            ConsistencyTracker object with updated consistency information

        """
        self.logger.debug(f"Tracking longitudinal consistency for agent {agent_id}")

        # Get or create consistency tracker
        if agent_id not in self.consistency_trackers:
            # Create new tracker
            self.consistency_trackers[agent_id] = ConsistencyTracker(
                agent_id=agent_id,
                baseline_profile=baseline_profile or current_profile,
                consistency_scores=[],
                drift_indicators={},
                last_updated=datetime.now()
            )
            self.logger.info(f"Created new consistency tracker for agent {agent_id}")
            return self.consistency_trackers[agent_id]

        tracker = self.consistency_trackers[agent_id]

        # Calculate consistency score against baseline
        consistency_score = self._calculate_profile_consistency(
            tracker.baseline_profile,
            current_profile
        )

        # Add to consistency history
        tracker.consistency_scores.append((datetime.now(), consistency_score))

        # Calculate drift indicators
        tracker.drift_indicators = self._calculate_drift_indicators(
            tracker.baseline_profile,
            current_profile
        )

        tracker.last_updated = datetime.now()

        self.logger.debug(f"Consistency score for agent {agent_id}: {consistency_score:.3f}")
        return tracker

    def _calculate_profile_consistency(
        self,
        baseline_profile: Dict[str, Any],
        current_profile: Dict[str, Any]
    ) -> float:
        """Calculate consistency score between baseline and current profiles.
        
        Args:
            baseline_profile: Baseline cognitive profile
            current_profile: Current cognitive profile
            
        Returns:
            Consistency score (0.0 = completely different, 1.0 = identical)

        """
        # Calculate distance between profiles
        distance = 0.0

        # Compare reasoning style
        baseline_reasoning = baseline_profile.get("profile", {}).get("reasoning_style", "analytical")
        current_reasoning = current_profile.get("profile", {}).get("reasoning_style", "analytical")
        reasoning_distance = 0.0 if baseline_reasoning == current_reasoning else 1.0
        distance += reasoning_distance * self.metric_weights[DiversityMetric.REASONING_STYLE]

        # Compare values
        baseline_values = baseline_profile.get("profile", {}).get("values", {})
        current_values = current_profile.get("profile", {}).get("values", {})
        value_distance = self._calculate_value_distance(
            {"profile": {"values": baseline_values}},
            {"profile": {"values": current_values}}
        )
        distance += value_distance * self.metric_weights[DiversityMetric.VALUE_SYSTEM]

        # Compare epistemological approach
        baseline_epistemology = baseline_profile.get("profile", {}).get("epistemological_approach", "empirical")
        current_epistemology = current_profile.get("profile", {}).get("epistemological_approach", "empirical")
        epistemology_distance = 0.0 if baseline_epistemology == current_epistemology else 1.0
        distance += epistemology_distance * self.metric_weights[DiversityMetric.EPISTEMOLOGICAL]

        # Compare belief structure
        baseline_belief = baseline_profile.get("profile", {}).get("belief_structure", "hierarchical")
        current_belief = current_profile.get("profile", {}).get("belief_structure", "hierarchical")
        belief_distance = 0.0 if baseline_belief == current_belief else 1.0
        distance += belief_distance * self.metric_weights[DiversityMetric.BELIEF_STRUCTURE]

        # Compare cognitive biases
        baseline_biases = set(baseline_profile.get("profile", {}).get("cognitive_biases", []))
        current_biases = set(current_profile.get("profile", {}).get("cognitive_biases", []))
        bias_distance = self._calculate_bias_distance(
            {"profile": {"cognitive_biases": list(baseline_biases)}},
            {"profile": {"cognitive_biases": list(current_biases)}}
        )
        distance += bias_distance * self.metric_weights[DiversityMetric.COGNITIVE_BIAS]

        # Compare domain expertise
        baseline_expertise = baseline_profile.get("profile", {}).get("domain_expertise", {})
        current_expertise = current_profile.get("profile", {}).get("domain_expertise", {})
        expertise_distance = self._calculate_expertise_distance(
            {"profile": {"domain_expertise": baseline_expertise}},
            {"profile": {"domain_expertise": current_expertise}}
        )
        distance += expertise_distance * self.metric_weights[DiversityMetric.DOMAIN_EXPERTISE]

        # Convert distance to consistency (1 - distance)
        return 1.0 - distance

    def _calculate_drift_indicators(
        self,
        baseline_profile: Dict[str, Any],
        current_profile: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate drift indicators for different aspects of the profile.
        
        Args:
            baseline_profile: Baseline cognitive profile
            current_profile: Current cognitive profile
            
        Returns:
            Dictionary mapping aspect names to drift scores

        """
        drift_indicators = {}

        # Value drift
        baseline_values = baseline_profile.get("profile", {}).get("values", {})
        current_values = current_profile.get("profile", {}).get("values", {})
        drift_indicators["values"] = self._calculate_value_distance(
            {"profile": {"values": baseline_values}},
            {"profile": {"values": current_values}}
        )

        # Expertise drift
        baseline_expertise = baseline_profile.get("profile", {}).get("domain_expertise", {})
        current_expertise = current_profile.get("profile", {}).get("domain_expertise", {})
        drift_indicators["expertise"] = self._calculate_expertise_distance(
            {"profile": {"domain_expertise": baseline_expertise}},
            {"profile": {"domain_expertise": current_expertise}}
        )

        # Bias drift
        baseline_biases = baseline_profile.get("profile", {}).get("cognitive_biases", [])
        current_biases = current_profile.get("profile", {}).get("cognitive_biases", [])
        drift_indicators["biases"] = self._calculate_bias_distance(
            {"profile": {"cognitive_biases": baseline_biases}},
            {"profile": {"cognitive_biases": current_biases}}
        )

        return drift_indicators

    def get_diversity_trends(
        self,
        group_id: str,
        time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get diversity trends for a specific group over time.
        
        Args:
            group_id: ID of the group to analyze
            time_window: Time window to consider (optional)
            
        Returns:
            Dictionary containing trend analysis

        """
        # Filter history for the specified group
        group_history = [
            score for score in self.diversity_history
            if score.group_id == group_id
        ]

        if time_window:
            cutoff_time = datetime.now() - time_window
            group_history = [
                score for score in group_history
                if score.timestamp >= cutoff_time
            ]

        if not group_history:
            return {"error": f"No diversity history found for group {group_id}"}

        # Sort by timestamp
        group_history.sort(key=lambda x: x.timestamp)

        # Calculate trends
        timestamps = [score.timestamp for score in group_history]
        overall_scores = [score.overall_score for score in group_history]

        # Calculate trend slope (simple linear regression)
        if len(overall_scores) > 1:
            x = np.arange(len(overall_scores))
            y = np.array(overall_scores)
            trend_slope = np.polyfit(x, y, 1)[0]
        else:
            trend_slope = 0.0

        return {
            "group_id": group_id,
            "sample_count": len(group_history),
            "time_span": (timestamps[-1] - timestamps[0]).total_seconds() / 3600 if len(timestamps) > 1 else 0,  # hours
            "current_score": overall_scores[-1],
            "initial_score": overall_scores[0],
            "trend_slope": trend_slope,
            "trend_direction": "increasing" if trend_slope > 0.01 else "decreasing" if trend_slope < -0.01 else "stable",
            "score_range": (min(overall_scores), max(overall_scores)),
            "average_score": sum(overall_scores) / len(overall_scores)
        }

    def get_consistency_report(
        self,
        agent_id: str,
        time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get consistency report for a specific agent.
        
        Args:
            agent_id: ID of the agent to analyze
            time_window: Time window to consider (optional)
            
        Returns:
            Dictionary containing consistency analysis

        """
        if agent_id not in self.consistency_trackers:
            return {"error": f"No consistency data found for agent {agent_id}"}

        tracker = self.consistency_trackers[agent_id]
        consistency_scores = tracker.consistency_scores

        if time_window:
            cutoff_time = datetime.now() - time_window
            consistency_scores = [
                (timestamp, score) for timestamp, score in consistency_scores
                if timestamp >= cutoff_time
            ]

        if not consistency_scores:
            return {"error": f"No consistency data in specified time window for agent {agent_id}"}

        # Extract scores
        scores = [score for _, score in consistency_scores]

        return {
            "agent_id": agent_id,
            "sample_count": len(scores),
            "current_consistency": scores[-1],
            "average_consistency": sum(scores) / len(scores),
            "consistency_range": (min(scores), max(scores)),
            "drift_indicators": tracker.drift_indicators,
            "stability": "stable" if min(scores) > 0.8 else "moderate" if min(scores) > 0.6 else "unstable",
            "last_updated": tracker.last_updated
        }
