import asyncio
import unittest
from datetime import datetime
from typing import Any, List, Optional
from unittest.mock import MagicMock

from src.core_services.consensus_algorithm_interface import (
    ConsensusAlgorithm,
    ConsensusContext,
    AlgorithmCapabilities,
    AlgorithmMetadata,
)
from src.core_services.consensus_models import ConsensusInput, ConsensusResult, ValidationResult, AlgorithmType

class DummyConsensusAlgorithm(ConsensusAlgorithm):
    def __init__(self, configuration: Optional[dict[str, Any]] = None):
        super().__init__("dummy_algo", configuration)

    async def calculate(self, inputs: List[ConsensusInput], context: ConsensusContext) -> ConsensusResult:
        raise NotImplementedError

    def get_metadata(self) -> AlgorithmMetadata:
        raise NotImplementedError

    def get_capabilities(self) -> AlgorithmCapabilities:
        raise NotImplementedError

    def validate_inputs(self, inputs: List[ConsensusInput]) -> ValidationResult:
        raise NotImplementedError

    def validate_configuration(self, config: dict[str, Any]) -> ValidationResult:
        raise NotImplementedError

    def estimate_execution_time(self, request: Any) -> float:
        raise NotImplementedError

    def get_health_status(self) -> dict[str, Any]:
        raise NotImplementedError

class TestConsensusAlgorithmInterface(unittest.TestCase):
    def test_abstract_methods_raise_not_implemented_error(self):
        algo = DummyConsensusAlgorithm()

        with self.assertRaises(NotImplementedError):
            asyncio.run(algo.calculate([], MagicMock()))

        with self.assertRaises(NotImplementedError):
            algo.get_metadata()

        with self.assertRaises(NotImplementedError):
            algo.get_capabilities()

        with self.assertRaises(NotImplementedError):
            algo.validate_inputs([])

        with self.assertRaises(NotImplementedError):
            algo.validate_configuration({})

        with self.assertRaises(NotImplementedError):
            algo.estimate_execution_time(None)

        with self.assertRaises(NotImplementedError):
            algo.get_health_status()

if __name__ == "__main__":
    unittest.main()
