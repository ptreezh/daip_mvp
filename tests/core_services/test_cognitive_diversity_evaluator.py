import asyncio
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from src.core_services.cognitive_diversity_evaluator import CognitiveDiversityEvaluator, DiversityScore
from src.core_services.advanced_consensus_algorithms import ConsensusInput

class TestCognitiveDiversityEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = CognitiveDiversityEvaluator()

    def test_evaluate_diversity_diverse_inputs(self):
        async def run_test():
            inputs = [
                ConsensusInput(
                    agent_id="agent1", position="A", confidence=0.8,
                    cognitive_profile={
                        "profile": {"reasoning_style": "analytical", "values": {"innovation": 0.8}},
                        "cognitive_biases": ["confirmation_bias"]
                    }
                ),
                ConsensusInput(
                    agent_id="agent2", position="B", confidence=0.9,
                    cognitive_profile={
                        "profile": {"reasoning_style": "creative", "values": {"collaboration": 0.9}},
                        "cognitive_biases": ["bandwagon_effect"]
                    }
                ),
                ConsensusInput(
                    agent_id="agent3", position="C", confidence=0.7,
                    cognitive_profile={
                        "profile": {"reasoning_style": "practical", "values": {"efficiency": 0.7}},
                        "cognitive_biases": ["anchoring_bias"]
                    }
                ),
            ]

            agent_profiles = {inp.agent_id: inp.cognitive_profile for inp in inputs}
            diversity_score = self.evaluator.calculate_group_diversity(agent_profiles, group_id="test_group")

            self.assertIsInstance(diversity_score, DiversityScore)
            self.assertAlmostEqual(diversity_score.overall_score, 0.41, places=2)

        asyncio.run(run_test())

    def test_evaluate_diversity_homogeneous_inputs(self):
        async def run_test():
            inputs = [
                ConsensusInput(
                    agent_id="agent1", position="A", confidence=0.8,
                    cognitive_profile={
                        "profile": {"reasoning_style": "analytical", "values": {"innovation": 0.8}},
                        "cognitive_biases": ["confirmation_bias"]
                    }
                ),
                ConsensusInput(
                    agent_id="agent2", position="A", confidence=0.9,
                    cognitive_profile={
                        "profile": {"reasoning_style": "analytical", "values": {"innovation": 0.8}},
                        "cognitive_biases": ["confirmation_bias"]
                    }
                ),
                ConsensusInput(
                    agent_id="agent3", position="A", confidence=0.7,
                    cognitive_profile={
                        "profile": {"reasoning_style": "analytical", "values": {"innovation": 0.8}},
                        "cognitive_biases": ["confirmation_bias"]
                    }
                ),
            ]

            agent_profiles = {inp.agent_id: inp.cognitive_profile for inp in inputs}
            diversity_score = self.evaluator.calculate_group_diversity(agent_profiles, group_id="test_group")

            self.assertIsInstance(diversity_score, DiversityScore)
            self.assertLess(diversity_score.overall_score, 0.3)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()