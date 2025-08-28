import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.core_services.collective_intelligence_manager import (
    CollectiveIntelligenceManager,
    CollectiveIntelligenceSession,
)
from src.core_services.advanced_consensus_algorithms import ConsensusInput, ConsensusResult, EmergentInsight
from src.core_services.cognitive_diversity_evaluator import DiversityScore
from src.core_services.consensus_models import AlgorithmSelection

class TestCollectiveIntelligenceManager(unittest.TestCase):
    def setUp(self):
        self.mock_diversity_evaluator = AsyncMock()
        self.mock_algorithm_selector = MagicMock()
        self.mock_insight_detector = MagicMock()

        self.manager = CollectiveIntelligenceManager()
        self.manager.diversity_evaluator = self.mock_diversity_evaluator
        self.manager.algorithm_selector = self.mock_algorithm_selector
        self.manager.insight_detector = self.mock_insight_detector

    def test_start_collective_intelligence_session(self):
        async def run_test():
            session_id = "test_session_1"
            participants = ["agent1", "agent2"]
            topic = "AI Ethics"
            participant_profiles = {"agent1": {"profile": {}}, "agent2": {"profile": {}}}

            self.mock_diversity_evaluator.calculate_group_diversity.return_value = DiversityScore(
                group_id=session_id, agents=participants, overall_score=0.7, timestamp=datetime.now(), sample_size=2
            )

            session = await self.manager.start_collective_intelligence_session(
                session_id, participants, topic, participant_profiles
            )

            self.assertIsInstance(session, CollectiveIntelligenceSession)
            self.assertIn(session_id, self.manager.active_sessions)
            self.assertEqual(session.topic, topic)
            self.assertEqual(session.diversity_score, 0.7)
            self.mock_diversity_evaluator.calculate_group_diversity.assert_called_once_with(
                participant_profiles, session_id
            )

        asyncio.run(run_test())

    def test_process_collective_input(self):
        async def run_test():
            session_id = "test_session_2"
            participants = ["agent1", "agent2"]
            topic = "Future of Work"
            participant_profiles = {"agent1": {"profile": {}}, "agent2": {"profile": {}}}

            # Setup initial session
            self.mock_diversity_evaluator.calculate_group_diversity.return_value = DiversityScore(
                group_id=session_id, agents=participants, overall_score=0.6, timestamp=datetime.now(), sample_size=2
            )
            session = await self.manager.start_collective_intelligence_session(
                session_id, participants, topic, participant_profiles
            )

            # Mock dependencies for process_collective_input
            mock_consensus_result = ConsensusResult(
                consensus_value="Agreed", confidence_level=0.8, algorithm_used="weighted_voting",
                participant_count=2, diversity_score=0.5, emergent_insights=[],
                reasoning_trace={}, timestamp=datetime.now()
            )
            mock_emergent_insight = EmergentInsight(
                insight_id="insight1", content="New idea", emergence_score=0.9,
                contributing_agents=["agent1"], synthesis_pattern="synthesis",
                confidence=0.9, timestamp=datetime.now()
            )

            self.mock_algorithm_selector.select_algorithm.return_value = AlgorithmSelection(algorithm_id="weighted_voting", confidence=0.8, reasoning="mock", alternatives=[], selection_time=0.0)
            self.mock_algorithm_selector.create_algorithm_instance.return_value = MagicMock(
                calculate_consensus=MagicMock(return_value=mock_consensus_result)
            )
            self.mock_insight_detector.detect_emergent_insights.return_value = [mock_emergent_insight]
            self.mock_algorithm_selector.record_algorithm_performance = MagicMock()

            inputs = [
                ConsensusInput(agent_id="agent1", position="Agree", confidence=0.7),
                ConsensusInput(agent_id="agent2", position="Agree", confidence=0.9),
            ]

            consensus_result, emergent_insights = await self.manager.process_collective_input(
                session_id, inputs
            )

            self.assertEqual(consensus_result, mock_consensus_result)
            self.assertEqual(emergent_insights, [mock_emergent_insight])
            self.assertIn(mock_consensus_result, session.consensus_results)
            self.assertIn(mock_emergent_insight, session.emergent_insights)
            self.mock_algorithm_selector.select_algorithm.assert_called_once()
            self.mock_algorithm_selector.create_algorithm_instance.assert_called_once()
            self.mock_insight_detector.detect_emergent_insights.assert_called_once()
            self.mock_algorithm_selector.record_algorithm_performance.assert_called_once()

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()