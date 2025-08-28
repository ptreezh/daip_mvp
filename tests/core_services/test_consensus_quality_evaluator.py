import unittest
from datetime import datetime
from unittest.mock import MagicMock

from src.core_services.consensus_quality_evaluator import ConsensusQualityEvaluator, ConsensusQualityReport
from src.core_services.consensus_models import ConsensusResult, ConsensusInput, AlgorithmType

class TestConsensusQualityEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = ConsensusQualityEvaluator()

    def test_evaluate_quality_simple_case(self):
        inputs = [
            ConsensusInput(agent_id="a1", position="Yes", confidence=0.9),
            ConsensusInput(agent_id="a2", position="Yes", confidence=0.8),
            ConsensusInput(agent_id="a3", position="Yes", confidence=0.7),
        ]
        consensus_result = ConsensusResult(
            consensus_value="Yes", confidence=0.85, participants=["a1", "a2", "a3"],
            reasoning_trace={}, metadata={}, timestamp=datetime.now(), diversity_score=0.1
        )

        report = self.evaluator.evaluate_consensus_quality(inputs, consensus_result)

        self.assertIsInstance(report, ConsensusQualityReport)
        self.assertGreater(report.overall_score, 0.0)
        self.assertIn("consensus_score", report.metrics)
        self.assertIn("coherence_score", report.metrics)
        self.assertIn("stability_index", report.metrics)

    def test_evaluate_quality_complex_case(self):
        inputs = [
            ConsensusInput(agent_id="a1", position="Option A", confidence=0.9, cognitive_profile={"style": "analytical"}),
            ConsensusInput(agent_id="a2", position="Option B", confidence=0.6, cognitive_profile={"style": "creative"}),
            ConsensusInput(agent_id="a3", position="Option A", confidence=0.7, cognitive_profile={"style": "analytical"}),
            ConsensusInput(agent_id="a4", position="Option C", confidence=0.5, cognitive_profile={"style": "intuitive"}),
        ]
        consensus_result = ConsensusResult(
            consensus_value="Option A", confidence=0.7, participants=["a1", "a2", "a3", "a4"],
            reasoning_trace={}, metadata={}, timestamp=datetime.now(), diversity_score=0.6
        )

        report = self.evaluator.evaluate_consensus_quality(inputs, consensus_result)

        self.assertIsInstance(report, ConsensusQualityReport)
        self.assertGreater(report.overall_score, 0.0)
        self.assertIn("diversity_preservation", report.metrics)
        self.assertIn("coherence_score", report.metrics)

if __name__ == "__main__":
    unittest.main()