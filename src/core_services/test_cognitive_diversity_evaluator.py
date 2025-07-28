#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Cognitive Diversity Evaluator

This module contains unit tests for the cognitive diversity evaluation functionality,
including cognitive distance calculation, diversity scoring, and consistency tracking.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.core_services.cognitive_diversity_evaluator import (
    CognitiveDiversityEvaluator,
    DiversityMetric,
    CognitiveDistance,
    DiversityScore,
    ConsistencyTracker
)


class TestCognitiveDiversityEvaluator:
    """Test cases for CognitiveDiversityEvaluator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = CognitiveDiversityEvaluator()
        
        # Sample agent profiles for testing
        self.agent1_profile = {
            "agent_id": "agent1",
            "name": "Analytical Agent",
            "profile": {
                "reasoning_style": "analytical",
                "belief_structure": "hierarchical",
                "epistemological_approach": "empirical",
                "metacognitive_level": 4,
                "cognitive_biases": ["confirmation", "anchoring"],
                "values": {
                    "truth": 0.9,
                    "justice": 0.7,
                    "utility": 0.8
                },
                "domain_expertise": {
                    "science": 0.9,
                    "logic": 0.8,
                    "mathematics": 0.7
                }
            }
        }
        
        self.agent2_profile = {
            "agent_id": "agent2",
            "name": "Intuitive Agent",
            "profile": {
                "reasoning_style": "intuitive",
                "belief_structure": "networked",
                "epistemological_approach": "constructivist",
                "metacognitive_level": 3,
                "cognitive_biases": ["availability", "confirmation"],
                "values": {
                    "care": 0.9,
                    "harmony": 0.8,
                    "innovation": 0.7
                },
                "domain_expertise": {
                    "art": 0.9,
                    "psychology": 0.8,
                    "creativity": 0.9
                }
            }
        }
        
        self.agent3_profile = {
            "agent_id": "agent3",
            "name": "Pragmatic Agent",
            "profile": {
                "reasoning_style": "pragmatic",
                "belief_structure": "bayesian",
                "epistemological_approach": "rationalist",
                "metacognitive_level": 5,
                "cognitive_biases": ["anchoring"],
                "values": {
                    "utility": 0.9,
                    "autonomy": 0.8,
                    "innovation": 0.6
                },
                "domain_expertise": {
                    "business": 0.9,
                    "economics": 0.8,
                    "strategy": 0.7
                }
            }
        }
    
    def test_initialization(self):
        """Test evaluator initialization."""
        assert isinstance(self.evaluator, CognitiveDiversityEvaluator)
        assert len(self.evaluator.distance_cache) == 0
        assert len(self.evaluator.consistency_trackers) == 0
        assert len(self.evaluator.diversity_history) == 0
        
        # Check metric weights sum to 1.0
        total_weight = sum(self.evaluator.metric_weights.values())
        assert abs(total_weight - 1.0) < 0.001
    
    def test_calculate_cognitive_distance(self):
        """Test cognitive distance calculation between two agents."""
        distance = self.evaluator.calculate_cognitive_distance(
            self.agent1_profile,
            self.agent2_profile,
            "agent1",
            "agent2"
        )
        
        assert isinstance(distance, CognitiveDistance)
        assert distance.agent_pair == ("agent1", "agent2")
        assert 0.0 <= distance.overall_distance <= 1.0
        assert len(distance.metric_distances) == len(DiversityMetric)
        
        # Check that all metric distances are valid
        for metric, metric_distance in distance.metric_distances.items():
            assert isinstance(metric, DiversityMetric)
            assert 0.0 <= metric_distance <= 1.0
        
        # Check caching
        cache_key = tuple(sorted(["agent1", "agent2"]))
        assert cache_key in self.evaluator.distance_cache
    
    def test_reasoning_distance_calculation(self):
        """Test reasoning style distance calculation."""
        # Same reasoning style should have distance 0
        distance = self.evaluator._calculate_reasoning_distance(
            {"profile": {"reasoning_style": "analytical"}},
            {"profile": {"reasoning_style": "analytical"}}
        )
        assert distance == 0.0
        
        # Different reasoning styles should have positive distance
        distance = self.evaluator._calculate_reasoning_distance(
            {"profile": {"reasoning_style": "analytical"}},
            {"profile": {"reasoning_style": "intuitive"}}
        )
        assert distance > 0.0
    
    def test_value_distance_calculation(self):
        """Test value system distance calculation."""
        # Same values should have distance 0
        values = {"truth": 0.8, "justice": 0.7}
        distance = self.evaluator._calculate_value_distance(
            {"profile": {"values": values}},
            {"profile": {"values": values}}
        )
        assert distance == 0.0
        
        # Different values should have positive distance
        distance = self.evaluator._calculate_value_distance(
            {"profile": {"values": {"truth": 0.9, "justice": 0.8}}},
            {"profile": {"values": {"care": 0.9, "harmony": 0.8}}}
        )
        assert distance > 0.0
    
    def test_bias_distance_calculation(self):
        """Test cognitive bias distance calculation."""
        # Same biases should have distance 0
        biases = ["confirmation", "anchoring"]
        distance = self.evaluator._calculate_bias_distance(
            {"profile": {"cognitive_biases": biases}},
            {"profile": {"cognitive_biases": biases}}
        )
        assert distance == 0.0
        
        # Completely different biases should have distance 1
        distance = self.evaluator._calculate_bias_distance(
            {"profile": {"cognitive_biases": ["confirmation"]}},
            {"profile": {"cognitive_biases": ["availability"]}}
        )
        assert distance == 1.0
        
        # Partial overlap should have intermediate distance
        distance = self.evaluator._calculate_bias_distance(
            {"profile": {"cognitive_biases": ["confirmation", "anchoring"]}},
            {"profile": {"cognitive_biases": ["confirmation", "availability"]}}
        )
        assert 0.0 < distance < 1.0
    
    def test_expertise_distance_calculation(self):
        """Test domain expertise distance calculation."""
        # Same expertise should have distance 0
        expertise = {"science": 0.8, "logic": 0.7}
        distance = self.evaluator._calculate_expertise_distance(
            {"profile": {"domain_expertise": expertise}},
            {"profile": {"domain_expertise": expertise}}
        )
        assert distance == 0.0
        
        # Different expertise should have positive distance
        distance = self.evaluator._calculate_expertise_distance(
            {"profile": {"domain_expertise": {"science": 0.9, "logic": 0.8}}},
            {"profile": {"domain_expertise": {"art": 0.9, "creativity": 0.8}}}
        )
        assert distance > 0.0
    
    def test_calculate_group_diversity(self):
        """Test group diversity calculation."""
        agent_profiles = {
            "agent1": self.agent1_profile,
            "agent2": self.agent2_profile,
            "agent3": self.agent3_profile
        }
        
        diversity_score = self.evaluator.calculate_group_diversity(
            agent_profiles,
            "test_group"
        )
        
        assert isinstance(diversity_score, DiversityScore)
        assert diversity_score.group_id == "test_group"
        assert set(diversity_score.agents) == {"agent1", "agent2", "agent3"}
        assert 0.0 <= diversity_score.overall_score <= 1.0
        assert diversity_score.sample_size == 3
        assert len(diversity_score.metric_scores) == len(DiversityMetric)
        
        # Check that diversity score is stored in history
        assert len(self.evaluator.diversity_history) == 1
        assert self.evaluator.diversity_history[0] == diversity_score
    
    def test_calculate_group_diversity_single_agent(self):
        """Test group diversity calculation with single agent."""
        agent_profiles = {"agent1": self.agent1_profile}
        
        diversity_score = self.evaluator.calculate_group_diversity(
            agent_profiles,
            "single_agent_group"
        )
        
        assert diversity_score.overall_score == 0.0
        assert diversity_score.sample_size == 1
        assert all(score == 0.0 for score in diversity_score.metric_scores.values())
    
    def test_track_longitudinal_consistency_new_agent(self):
        """Test longitudinal consistency tracking for new agent."""
        tracker = self.evaluator.track_longitudinal_consistency(
            "agent1",
            self.agent1_profile
        )
        
        assert isinstance(tracker, ConsistencyTracker)
        assert tracker.agent_id == "agent1"
        assert tracker.baseline_profile == self.agent1_profile
        assert len(tracker.consistency_scores) == 0  # No comparison yet for new agent
        
        # Check that tracker is stored
        assert "agent1" in self.evaluator.consistency_trackers
    
    def test_track_longitudinal_consistency_existing_agent(self):
        """Test longitudinal consistency tracking for existing agent."""
        # First call to establish baseline
        self.evaluator.track_longitudinal_consistency("agent1", self.agent1_profile)
        
        # Second call with modified profile
        modified_profile = self.agent1_profile.copy()
        modified_profile["profile"] = modified_profile["profile"].copy()
        modified_profile["profile"]["values"] = {"truth": 0.8, "justice": 0.6}  # Changed values
        
        tracker = self.evaluator.track_longitudinal_consistency(
            "agent1",
            modified_profile
        )
        
        assert len(tracker.consistency_scores) == 1
        timestamp, consistency_score = tracker.consistency_scores[0]
        assert isinstance(timestamp, datetime)
        assert 0.0 <= consistency_score <= 1.0
        assert len(tracker.drift_indicators) > 0
    
    def test_calculate_profile_consistency(self):
        """Test profile consistency calculation."""
        # Same profile should have consistency 1.0
        consistency = self.evaluator._calculate_profile_consistency(
            self.agent1_profile,
            self.agent1_profile
        )
        assert abs(consistency - 1.0) < 0.001
        
        # Different profiles should have consistency < 1.0
        consistency = self.evaluator._calculate_profile_consistency(
            self.agent1_profile,
            self.agent2_profile
        )
        assert consistency < 1.0
    
    def test_get_diversity_trends(self):
        """Test diversity trends analysis."""
        # Add some diversity scores to history
        agent_profiles = {
            "agent1": self.agent1_profile,
            "agent2": self.agent2_profile
        }
        
        # Calculate diversity at different times
        for i in range(3):
            self.evaluator.calculate_group_diversity(agent_profiles, "test_group")
        
        trends = self.evaluator.get_diversity_trends("test_group")
        
        assert "group_id" in trends
        assert trends["group_id"] == "test_group"
        assert "sample_count" in trends
        assert trends["sample_count"] == 3
        assert "current_score" in trends
        assert "trend_direction" in trends
        assert trends["trend_direction"] in ["increasing", "decreasing", "stable"]
    
    def test_get_diversity_trends_no_data(self):
        """Test diversity trends analysis with no data."""
        trends = self.evaluator.get_diversity_trends("nonexistent_group")
        
        assert "error" in trends
        assert "No diversity history found" in trends["error"]
    
    def test_get_consistency_report(self):
        """Test consistency report generation."""
        # Track consistency for an agent
        self.evaluator.track_longitudinal_consistency("agent1", self.agent1_profile)
        
        # Modify profile and track again
        modified_profile = self.agent1_profile.copy()
        modified_profile["profile"] = modified_profile["profile"].copy()
        modified_profile["profile"]["values"] = {"truth": 0.7}
        
        self.evaluator.track_longitudinal_consistency("agent1", modified_profile)
        
        report = self.evaluator.get_consistency_report("agent1")
        
        assert "agent_id" in report
        assert report["agent_id"] == "agent1"
        assert "sample_count" in report
        assert "current_consistency" in report
        assert "average_consistency" in report
        assert "drift_indicators" in report
        assert "stability" in report
        assert report["stability"] in ["stable", "moderate", "unstable"]
    
    def test_get_consistency_report_no_data(self):
        """Test consistency report with no data."""
        report = self.evaluator.get_consistency_report("nonexistent_agent")
        
        assert "error" in report
        assert "No consistency data found" in report["error"]
    
    def test_metric_weights_configuration(self):
        """Test that metric weights are properly configured."""
        weights = self.evaluator.metric_weights
        
        # Check all metrics are present
        for metric in DiversityMetric:
            assert metric in weights
        
        # Check weights are positive
        for weight in weights.values():
            assert weight > 0.0
        
        # Check weights sum to 1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.001
    
    def test_distance_caching(self):
        """Test that cognitive distances are properly cached."""
        # Calculate distance
        distance1 = self.evaluator.calculate_cognitive_distance(
            self.agent1_profile,
            self.agent2_profile,
            "agent1",
            "agent2"
        )
        
        # Check cache
        cache_key = tuple(sorted(["agent1", "agent2"]))
        assert cache_key in self.evaluator.distance_cache
        cached_distance = self.evaluator.distance_cache[cache_key]
        
        # Verify cached distance matches calculated distance
        assert cached_distance.overall_distance == distance1.overall_distance
        assert cached_distance.metric_distances == distance1.metric_distances
    
    def test_drift_indicators_calculation(self):
        """Test drift indicators calculation."""
        baseline_profile = self.agent1_profile
        
        # Create modified profile
        modified_profile = self.agent1_profile.copy()
        modified_profile["profile"] = modified_profile["profile"].copy()
        modified_profile["profile"]["values"] = {"truth": 0.5, "utility": 0.3}  # Changed values
        modified_profile["profile"]["cognitive_biases"] = ["availability"]  # Changed biases
        
        drift_indicators = self.evaluator._calculate_drift_indicators(
            baseline_profile,
            modified_profile
        )
        
        assert "values" in drift_indicators
        assert "expertise" in drift_indicators
        assert "biases" in drift_indicators
        
        # Values should show drift
        assert drift_indicators["values"] > 0.0
        
        # Biases should show drift
        assert drift_indicators["biases"] > 0.0


if __name__ == "__main__":
    pytest.main([__file__])