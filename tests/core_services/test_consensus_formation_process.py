import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.core_services.consensus_formation_process import ConsensusFormationProcess, FormationStage
from src.core_services.consensus_dispatcher import UnifiedConsensusDispatcher
from src.core_services.consensus_models import ConsensusInput, ConsensusResult, AlgorithmType

class TestConsensusFormationProcess(unittest.TestCase):
    def setUp(self):
        self.mock_dispatcher = AsyncMock(spec=UnifiedConsensusDispatcher)
        self.process = ConsensusFormationProcess(self.mock_dispatcher)

    def test_start_process(self):
        async def run_test():
            inputs = [
                {"agent_id": "a1", "position": "A", "confidence": 0.8, "participant": "a1"},
                {"agent_id": "a2", "position": "B", "confidence": 0.7, "participant": "a2"},
            ]
            context = {"test": "context"}

            # Mock the dispatcher's calculate_consensus method
            self.mock_dispatcher.calculate_consensus.return_value = ConsensusResult(
                consensus_value="Agreed", confidence=0.9, participants=["a1", "a2"],
                reasoning_trace={}, metadata={}, timestamp=datetime.now(), diversity_score=0.5
            )

            # Call the actual initiate_consensus_formation method
            result_dict = self.process.initiate_consensus_formation(
                topic="test_topic", initial_positions=inputs, process_config=context
            )

            self.assertIsInstance(result_dict, dict)
            self.assertEqual(result_dict["status"], "initiated")
            self.assertIn("formation_id", result_dict)
            # Verify that the dispatcher's calculate_consensus was NOT called directly by initiate_consensus_formation
            # It should be called by facilitate_convergence later
            self.mock_dispatcher.calculate_consensus.assert_not_called()

        asyncio.run(run_test())

    def test_get_current_state(self):
        async def run_test():
            # First, initiate a process to get a formation_id
            inputs = [
                {"agent_id": "a1", "position": "A", "confidence": 0.8, "participant": "a1"},
            ]
            result_dict = self.process.initiate_consensus_formation(
                topic="test_topic", initial_positions=inputs
            )
            formation_id = result_dict["formation_id"]

            # Now, get the current state using get_process_status
            state = self.process.get_process_status(formation_id)

            self.assertIsInstance(state, dict)
            self.assertEqual(state["current_stage"], FormationStage.POSITION_COLLECTION.value) # Initial status
            self.assertEqual(state["current_consensus"], 0.0) # Initial consensus
             # Duration is calculated in get_process_status

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
