#!/usr/bin/env python3
"""Test suite for Advanced Consensus Algorithms

This module contains unit tests for the advanced consensus algorithms,
including weighted voting, Bayesian consensus, and cognitive diversity
preserving consensus.
"""

from datetime import datetime

import pytest

from src.core_services.advanced_consensus_algorithms import (
    BayesianConsensus,
    CognitiveDiversityPreservingConsensus,
    ConsensusAlgorithmType,
    ConsensusInput,
    ConsensusResult,
    WeightedVotingConsensus,
)


class TestAdvancedConsensusAlgorithms:
    """Test cases for advanced consensus algorithms."""

    def setup_method(self):
        """Set up test fixtures."""
        # Sample cognitive profiles
        self.profile1 = {
            "profile": {
                "reasoning_style": "analytical",
                "values": {"truth": 0.9, "justice": 0.7},
                "cognitive_biases": ["confirmation", "anchoring"],
                "domain_expertise": {"science": 0.8, "logic": 0.9}
            }
        }

        self.profile2 = {
            "profile": {
                "reasoning_style": "intuitive",
                "values": {"care": 0.8, "harmony": 0.9},
                "cognitive_biases": ["availability"],
                "domain_expertise": {"art": 0.9, "psychology": 0.7}
            }
        }

        self.profile3 = {
            "profile": {
                "reasoning_style": "pragmatic",
                "values": {"utility": 0.9, "autonomy": 0.8},
                "cognitive_biases": ["anchoring"],
                "domain_expertise": {"business": 0.8, "economics": 0.9}
            }
        }

        # Sample consensus inputs
        self.inputs = [
            ConsensusInput(
                agent_id="agent1",
                position="strongly agree",
                confidence=0.9,
                reasoning="Based on scientific evidence",
                evidence=["study1", "study2"],
                cognitive_profile=self.profile1,
                timestamp=datetime.now()
            ),
            ConsensusInput(
                agent_id="agent2",
                position="somewhat agree",
                confidence=0.6,
                reasoning="Feels right intuitively",
                evidence=["personal_experience"],
                cognitive_profile=self.profile2,
                timestamp=datetime.now()
            ),
            ConsensusInput(
                agent_id="agent3",
                position="agree",
                confidence=0.8,
                reasoning="Practical benefits are clear",
                evidence=["cost_analysis"],
                cognitive_profile=self.profile3,
                timestamp=datetime.now()
            )
        ]

        self.numerical_inputs = [
            ConsensusInput(
                agent_id="agent1",
                position=8.5,
                confidence=0.9,
                cognitive_profile=self.profile1
            ),
            ConsensusInput(
                agent_id="agent2",
                position=7.2,
                confidence=0.6,
                cognitive_profile=self.profile2
            ),
            ConsensusInput(
                agent_id="agent3",
                position=8.0,
                confidence=0.8,
                cognitive_profile=self.profile3
            )
        ]

    def test_weighted_voting_consensus_categorical(self):
        """Test weighted voting consensus with categorical positions."""
        algorithm = WeightedVotingConsensus()
        result = algorithm.calculate_consensus(self.inputs)

        assert isinstance(result, ConsensusResult)
        assert result.algorithm_used == ConsensusAlgorithmType.WEIGHTED_VOTING
        assert result.participant_count == 3
        assert 0.0 <= result.confidence_level <= 1.0
        assert 0.0 <= result.diversity_score <= 1.0
        assert isinstance(result.consensus_value, str)
        assert "agree" in result.consensus_value.lower()

    def test_weighted_voting_consensus_numerical(self):
        """Test weighted voting consensus with numerical positions."""
        algorithm = WeightedVotingConsensus()
        result = algorithm.calculate_consensus(self.numerical_inputs)

        assert isinstance(result, ConsensusResult)
        assert isinstance(result.consensus_value, float)
        assert 7.0 <= result.consensus_value <= 9.0  # Should be within input range
        assert result.participant_count == 3

    def test_weighted_voting_weights_calculation(self):
        """Test weight calculation in weighted voting."""
        algorithm = WeightedVotingConsensus(
            expertise_weight=0.5,
            confidence_weight=0.3,
            diversity_weight=0.2
        )

        weights = algorithm._calculate_weights(self.inputs, {"domain": "science"})

        assert len(weights) == len(self.inputs)
        assert all(0.0 <= w <= 1.0 for w in weights)
        assert abs(sum(weights) - 1.0) < 0.001  # Weights should sum to 1

        # Agent1 should have higher weight due to science expertise
        assert weights[0] > weights[1]  # agent1 > agent2

    def test_bayesian_consensus_numerical(self):
        """Test Bayesian consensus with numerical values."""
        algorithm = BayesianConsensus(prior_strength=1.0)
        result = algorithm.calculate_consensus(self.numerical_inputs)

        assert isinstance(result, ConsensusResult)
        assert result.algorithm_used == ConsensusAlgorithmType.BAYESIAN_CONSENSUS
        assert isinstance(result.consensus_value, float)
        assert 0.0 <= result.confidence_level <= 1.0

    def test_bayesian_consensus_categorical(self):
        """Test Bayesian consensus with categorical values."""
        algorithm = BayesianConsensus(prior_strength=1.0)
        result = algorithm.calculate_consensus(self.inputs)

        assert isinstance(result, ConsensusResult)
        assert isinstance(result.consensus_value, str)
        assert result.confidence_level > 0.0

    def test_cognitive_diversity_preserving_consensus(self):
        """Test cognitive diversity preserving consensus."""
        algorithm = CognitiveDiversityPreservingConsensus(
            diversity_threshold=0.3,
            minority_protection=0.2
        )
        result = algorithm.calculate_consensus(self.inputs)

        assert isinstance(result, ConsensusResult)
        assert result.algorithm_used == ConsensusAlgorithmType.COGNITIVE_DIVERSITY_PRESERVING
        assert result.diversity_score > 0.0  # Should preserve some diversity

    def test_cognitive_clustering(self):
        """Test cognitive similarity clustering."""
        algorithm = CognitiveDiversityPreservingConsensus()
        clusters = algorithm._cluster_by_cognitive_similarity(self.inputs)

        assert len(clusters) > 0
        assert all(len(cluster) > 0 for cluster in clusters)

        # Total inputs should equal sum of cluster sizes
        total_clustered = sum(len(cluster) for cluster in clusters)
        assert total_clustered == len(self.inputs)

    def test_cognitive_distance_calculation(self):
        """Test cognitive distance calculation."""
        algorithm = WeightedVotingConsensus()
        distance = algorithm._calculate_cognitive_distance(self.profile1, self.profile2)

        assert 0.0 <= distance <= 1.0

        # Distance between identical profiles should be 0
        same_distance = algorithm._calculate_cognitive_distance(self.profile1, self.profile1)
        assert same_distance == 0.0

        # Distance should be symmetric
        reverse_distance = algorithm._calculate_cognitive_distance(self.profile2, self.profile1)
        assert abs(distance - reverse_distance) < 0.001

    def test_value_distance_calculation(self):
        """Test value system distance calculation."""
        algorithm = WeightedVotingConsensus()

        values1 = {"truth": 0.9, "justice": 0.8}
        values2 = {"care": 0.8, "harmony": 0.9}

        distance = algorithm._calculate_value_distance(values1, values2)
        assert 0.0 <= distance <= 1.0

        # Same values should have distance 0
        same_distance = algorithm._calculate_value_distance(values1, values1)
        assert same_distance == 0.0

    def test_emergent_insight_detection(self):
        """Test emergent insight detection."""
        algorithm = WeightedVotingConsensus()
        result = algorithm.calculate_consensus(self.inputs)

        insights = algorithm.detect_emergent_insights(self.inputs, result)

        assert isinstance(insights, list)
        # May or may not detect insights depending on input complexity

    def test_algorithm_parameters(self):
        """Test algorithm parameter retrieval."""
        weighted_algo = WeightedVotingConsensus(
            expertise_weight=0.4,
            confidence_weight=0.3,
            diversity_weight=0.3
        )
        params = weighted_algo.get_algorithm_parameters()

        assert "expertise_weight" in params
        assert "confidence_weight" in params
        assert "diversity_weight" in params
        assert params["expertise_weight"] == 0.4

        bayesian_algo = BayesianConsensus(prior_strength=2.0)
        params = bayesian_algo.get_algorithm_parameters()

        assert "prior_strength" in params
        assert params["prior_strength"] == 2.0

    def test_empty_inputs_handling(self):
        """Test handling of empty inputs."""
        algorithm = WeightedVotingConsensus()

        with pytest.raises(ValueError):
            algorithm.calculate_consensus([])

    def test_single_input_handling(self):
        """Test handling of single input."""
        algorithm = WeightedVotingConsensus()
        single_input = [self.inputs[0]]

        result = algorithm.calculate_consensus(single_input)

        assert result.participant_count == 1
        assert result.consensus_value == single_input[0].position
        assert result.diversity_score == 0.0  # No diversity with single input

    def test_confidence_calculation(self):
        """Test confidence calculation."""
        algorithm = WeightedVotingConsensus()

        # High agreement should lead to high confidence
        high_agreement_inputs = [
            ConsensusInput("agent1", "agree", 0.9, cognitive_profile=self.profile1),
            ConsensusInput("agent2", "agree", 0.8, cognitive_profile=self.profile2),
            ConsensusInput("agent3", "agree", 0.9, cognitive_profile=self.profile3)
        ]

        result = algorithm.calculate_consensus(high_agreement_inputs)
        high_confidence = result.confidence_level

        # Low agreement should lead to lower confidence
        low_agreement_inputs = [
            ConsensusInput("agent1", "agree", 0.5, cognitive_profile=self.profile1),
            ConsensusInput("agent2", "disagree", 0.6, cognitive_profile=self.profile2),
            ConsensusInput("agent3", "neutral", 0.4, cognitive_profile=self.profile3)
        ]

        result = algorithm.calculate_consensus(low_agreement_inputs)
        low_confidence = result.confidence_level

        assert high_confidence > low_confidence

    def test_diversity_score_calculation(self):
        """Test diversity score calculation."""
        algorithm = WeightedVotingConsensus()

        # Diverse profiles should have higher diversity score
        diverse_inputs = [
            ConsensusInput("agent1", "position1", 0.8, cognitive_profile=self.profile1),
            ConsensusInput("agent2", "position2", 0.8, cognitive_profile=self.profile2),
            ConsensusInput("agent3", "position3", 0.8, cognitive_profile=self.profile3)
        ]

        result = algorithm.calculate_consensus(diverse_inputs)
        diverse_score = result.diversity_score

        # Similar profiles should have lower diversity score
        similar_inputs = [
            ConsensusInput("agent1", "position1", 0.8, cognitive_profile=self.profile1),
            ConsensusInput("agent2", "position2", 0.8, cognitive_profile=self.profile1),
            ConsensusInput("agent3", "position3", 0.8, cognitive_profile=self.profile1)
        ]

        result = algorithm.calculate_consensus(similar_inputs)
        similar_score = result.diversity_score

        assert diverse_score > similar_score

    def test_complex_position_handling(self):
        """Test handling of complex position types."""
        complex_inputs = [
            ConsensusInput(
                "agent1",
                {"option": "A", "confidence": 0.8, "reasoning": "logical"},
                0.9,
                cognitive_profile=self.profile1
            ),
            ConsensusInput(
                "agent2",
                {"option": "B", "confidence": 0.6, "reasoning": "intuitive"},
                0.7,
                cognitive_profile=self.profile2
            )
        ]

        algorithm = WeightedVotingConsensus()
        result = algorithm.calculate_consensus(complex_inputs)

        assert isinstance(result.consensus_value, dict)
        assert "components" in result.consensus_value
        assert len(result.consensus_value["components"]) == 2


if __name__ == "__main__":
    pytest.main([__file__])
