import asyncio
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from src.core_services.bayesian_algorithm import BayesianAlgorithm
from src.core_services.consensus_models import ConsensusInput, ConsensusResult, AlgorithmType
from src.core_services.consensus_algorithm_interface import ConsensusContext

class TestBayesianAlgorithm(unittest.TestCase):
    def setUp(self):
        self.config = {"prior_strength": 1.0}
        self.bayesian_algo = BayesianAlgorithm(self.config)

    def test_numerical_consensus_calculation(self):
        async def run_test():
            inputs = [
                ConsensusInput(agent_id="agent1", position=10.0, confidence=0.8),
                ConsensusInput(agent_id="agent2", position=12.0, confidence=0.9),
                ConsensusInput(agent_id="agent3", position=11.0, confidence=0.7),
            ]
            mock_context = MagicMock(spec=ConsensusContext)
            mock_context.set_metric = MagicMock()
            mock_context.configuration = {}

            result = await self.bayesian_algo.calculate(inputs, mock_context)

            self.assertIsInstance(result, ConsensusResult)
            self.assertAlmostEqual(result.consensus_value, 11.31, places=2) # Expected value based on weighted average
            self.assertGreater(result.confidence, 0.5)
            self.assertEqual(result.metadata.get("algorithm_used"), AlgorithmType.BAYESIAN_CONSENSUS.value)
            mock_context.set_metric.assert_called()

        asyncio.run(run_test())

    def test_categorical_consensus_calculation(self):
        async def run_test():
            inputs = [
                ConsensusInput(agent_id="agent1", position="A", confidence=0.8),
                ConsensusInput(agent_id="agent2", position="B", confidence=0.9),
                ConsensusInput(agent_id="agent3", position="A", confidence=0.7),
            ]
            mock_context = MagicMock(spec=ConsensusContext)
            mock_context.set_metric = MagicMock()
            mock_context.configuration = {}

            result = await self.bayesian_algo.calculate(inputs, mock_context)

            self.assertIsInstance(result, ConsensusResult)
            self.assertEqual(result.consensus_value, "A")
            self.assertGreater(result.confidence, 0.5)
            self.assertEqual(result.metadata.get("algorithm_used"), AlgorithmType.BAYESIAN_CONSENSUS.value)
            mock_context.set_metric.assert_called()

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
