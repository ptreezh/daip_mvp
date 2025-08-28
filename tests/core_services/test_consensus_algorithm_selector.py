import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from src.core_services.consensus_algorithm_selector import ConsensusAlgorithmSelector
from src.core_services.consensus_models import ConsensusInput, ConsensusResult, AlgorithmSelection, AlgorithmType
from src.core_services.consensus_algorithm_selector import SelectionContext
from src.core_services.advanced_consensus_algorithms import WeightedVotingConsensus, BayesianConsensus, CognitiveDiversityPreservingConsensus

class TestConsensusAlgorithmSelector(unittest.TestCase):
    def setUp(self):
        self.selector = ConsensusAlgorithmSelector()
        self.selector.performance_tracker = MagicMock()
        self.selector.performance_tracker.get_algorithm_performance.return_value = 0.5 # Mock a default performance score

    def test_select_algorithm(self):
        inputs = [
            ConsensusInput(agent_id="a1", position="A", confidence=0.8, cognitive_profile={}),
            ConsensusInput(agent_id="a2", position="B", confidence=0.7, cognitive_profile={}),
            ConsensusInput(agent_id="a3", position="A", confidence=0.9, cognitive_profile={}),
        ]
        context = {"diversity_score": 0.6, "urgency": "high"}

        selection = self.selector.select_algorithm(inputs, context)
        self.assertIsInstance(selection, AlgorithmSelection)
        self.assertIn(selection.algorithm_id, [algo.value for algo in AlgorithmType])
        self.assertGreater(selection.confidence, 0.0)

    def test_create_algorithm_instance(self):
        # Test with WeightedVotingConsensus
        mock_context = MagicMock()
        mock_context.accuracy_requirement = 0.9
        mock_context.diversity_score = 0.8
        instance = self.selector.create_algorithm_instance(AlgorithmType.WEIGHTED_VOTING, mock_context)
        self.assertIsInstance(instance, WeightedVotingConsensus)

        # Test with BayesianConsensus
        mock_context = MagicMock()
        mock_context.accuracy_requirement = 0.7
        mock_context.diversity_score = 0.5
        mock_context.confidence_variance = 0.3 # Added for Bayesian
        instance = self.selector.create_algorithm_instance(AlgorithmType.BAYESIAN_CONSENSUS, mock_context)
        self.assertIsInstance(instance, BayesianConsensus)

        # Test with CognitiveDiversityPreservingConsensus
        mock_context = MagicMock()
        mock_context.accuracy_requirement = 0.5
        mock_context.diversity_score = 0.2
        mock_context.participant_count = 15 # Added for CognitiveDiversityPreserving
        instance = self.selector.create_algorithm_instance(AlgorithmType.COGNITIVE_DIVERSITY_PRESERVING, mock_context)
        self.assertIsInstance(instance, CognitiveDiversityPreservingConsensus)

        # Test with unknown type
        with self.assertRaises(ValueError):
            self.selector.create_algorithm_instance(AlgorithmType.SIMPLE_MAJORITY, {})

    def test_record_algorithm_performance(self):
        result = ConsensusResult(
            consensus_value="A", confidence=0.8, algorithm_used=AlgorithmType.WEIGHTED_VOTING,
            participant_count=3, diversity_score=0.5, emergent_insights=[],
            reasoning_trace={}, timestamp=datetime.now(), participants=["a1", "a2", "a3"]
        )
        context = SelectionContext(
            participant_count=3,
            diversity_score=0.5,
            confidence_variance=0.1,
            position_type="categorical",
            task_complexity=0.5,
            time_constraint=0.0,
            accuracy_requirement=0.7
        )

        self.selector.record_algorithm_performance(AlgorithmType.WEIGHTED_VOTING, result, context)
        self.selector.performance_tracker.record_performance.assert_called_once()

if __name__ == "__main__":
    unittest.main()
