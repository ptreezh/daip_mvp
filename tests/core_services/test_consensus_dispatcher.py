import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.core_services.consensus_dispatcher import UnifiedConsensusDispatcher
from src.core_services.consensus_models import ConsensusInput, ConsensusResult, AlgorithmSelection, AlgorithmType
from src.core_services.consensus_algorithm_selector import ConsensusAlgorithmSelector
from src.core_services.advanced_consensus_algorithms import AdvancedConsensusAlgorithm

class TestConsensusDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = UnifiedConsensusDispatcher()
        
        # Mock internal components of the dispatcher
        self.dispatcher.strategy_factory = MagicMock()
        self.dispatcher.advanced_algorithms = {
            AlgorithmType.WEIGHTED_VOTING: AsyncMock(spec=AdvancedConsensusAlgorithm),
            AlgorithmType.BAYESIAN_CONSENSUS: AsyncMock(spec=AdvancedConsensusAlgorithm),
            AlgorithmType.COGNITIVE_DIVERSITY_PRESERVING: AsyncMock(spec=AdvancedConsensusAlgorithm),
        }

    def test_dispatch_request_success(self):
        async def run_test():
            # Mock the selected algorithm's calculate_consensus method
            mock_weighted_voting_algo = self.dispatcher.advanced_algorithms[AlgorithmType.WEIGHTED_VOTING]
            mock_weighted_voting_algo.calculate_consensus.return_value = ConsensusResult(
                consensus_value="Agreed", confidence=0.9, participants=["a1", "a2"],
                reasoning_trace={}, metadata={}, timestamp=datetime.now(), diversity_score=0.5
            )

            # Mock the optimal method selection
            self.dispatcher._select_optimal_method = MagicMock(return_value=AlgorithmType.WEIGHTED_VOTING)

            inputs = [
                ConsensusInput(agent_id="a1", position="A", confidence=0.8),
                ConsensusInput(agent_id="a2", position="B", confidence=0.7),
            ]
            context = {"test": "context"}

            result = await self.dispatcher.calculate_consensus(inputs, context=context)

            self.assertIsInstance(result, ConsensusResult)
            self.assertEqual(result.consensus_value, "Agreed")
            self.dispatcher._select_optimal_method.assert_called_once_with(inputs, context)
            mock_weighted_voting_algo.calculate_consensus.assert_called_once_with(inputs, context)

        asyncio.run(run_test())

    def test_dispatch_request_unknown_algorithm(self):
        async def run_test():
            # Mock the optimal method selection to return an unsupported method
            self.dispatcher._select_optimal_method = MagicMock(return_value="unsupported_method")

            inputs = [
                ConsensusInput(agent_id="a1", position="A", confidence=0.8),
            ]
            context = {"test": "context"}

            with self.assertRaisesRegex(ValueError, "不支持的共识方法: unsupported_method"):
                await self.dispatcher.calculate_consensus(inputs, context=context)

            self.dispatcher._select_optimal_method.assert_called_once_with(inputs, context)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
