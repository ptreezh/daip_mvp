"""Tests for consensus algorithm extensibility.

This module contains tests to validate that new consensus strategies can be registered and used.
"""

import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from src.protocols.consensus_strategies import ConsensusStrategy, ConsensusStrategyFactory
from src.unified_tool_manager import UnifiedToolManager


class CustomConsensusStrategy(ConsensusStrategy):
    """A custom consensus strategy for testing extensibility.
    """

    def __init__(self, custom_param: str = "default"):
        """Initialize the CustomConsensusStrategy.
        
        Args:
            custom_param: A custom parameter for testing

        """
        self.custom_param = custom_param

    async def execute(self, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the custom consensus strategy on a list of opinions.
        
        Args:
            opinions: List of Opinion objects representing different viewpoints
            
        Returns:
            ConsensusResult object containing the consensus outcome

        """
        if not opinions:
            return {
                "consensus_text": "No opinions provided",
                "agreement_level": 0.0,
                "method_description": f"Custom consensus strategy with param: {self.custom_param} (no opinions)"
            }

        # Simple implementation: just take the first opinion as consensus
        consensus_opinion = opinions[0]

        return {
            "consensus_text": consensus_opinion.get("content", ""),
            "agreement_level": 1.0,
            "supporting_opinions": opinions[1:],
            "dissenting_opinions": [],
            "method_description": f"Custom consensus strategy with param: {self.custom_param}",
            "custom_metadata": {
                "custom_param": self.custom_param,
                "num_opinions": len(opinions)
            }
        }


class TestConsensusExtensibility(unittest.TestCase):
    """Test cases for consensus algorithm extensibility."""

    def setUp(self):
        """Set up test environment."""
        # Create a factory
        self.factory = ConsensusStrategyFactory()

        # Register the custom strategy
        self.factory.register("custom_strategy", CustomConsensusStrategy)

        # Create test opinions
        self.opinions = [
            {
                "role_id": "expert",
                "content": "The solution is to use a distributed system",
                "confidence": 0.9
            },
            {
                "role_id": "novice",
                "content": "We should use a centralized approach",
                "confidence": 0.7
            }
        ]

    def test_strategy_registration(self):
        """Test that custom strategies can be registered."""
        # Verify that the strategy is registered
        self.assertIn("custom_strategy", self.factory.strategies)
        self.assertEqual(self.factory.strategies["custom_strategy"], CustomConsensusStrategy)

    def test_strategy_creation(self):
        """Test that custom strategies can be created."""
        # Create a strategy instance
        strategy = self.factory.create("custom_strategy", custom_param="test_param")

        # Verify the instance
        self.assertIsInstance(strategy, CustomConsensusStrategy)
        self.assertEqual(strategy.custom_param, "test_param")

    def test_strategy_creation_with_default_params(self):
        """Test that custom strategies can be created with default parameters."""
        # Create a strategy instance with default parameters
        strategy = self.factory.create("custom_strategy")

        # Verify the instance
        self.assertIsInstance(strategy, CustomConsensusStrategy)
        self.assertEqual(strategy.custom_param, "default")

    def test_unknown_strategy(self):
        """Test handling of unknown strategies."""
        # Try to create an unknown strategy
        with self.assertRaises(ValueError):
            self.factory.create("unknown_strategy")

    @patch("src.unified_tool_manager.UnifiedToolManager.register_tool")
    def test_register_with_tool_manager(self, mock_register_tool):
        """Test registering strategies with the tool manager."""
        # Create a mock tool manager
        tool_manager = MagicMock(spec=UnifiedToolManager)

        # Register strategies with the tool manager
        self.factory.register_strategies_with_tool_manager(tool_manager)

        # Verify that register_tool was called for the custom strategy
        tool_manager.register_tool.assert_any_call(
            "consensus.custom_strategy",
            CustomConsensusStrategy,
            description="Custom consensus strategy"
        )


class TestConsensusExecution(unittest.IsolatedAsyncioTestCase):
    """Test cases for executing consensus strategies."""

    async def asyncSetUp(self):
        """Set up test environment."""
        # Create a factory
        self.factory = ConsensusStrategyFactory()

        # Register the custom strategy
        self.factory.register("custom_strategy", CustomConsensusStrategy)

        # Create a tool manager
        self.tool_manager = UnifiedToolManager(config={})

        # Register strategies with the tool manager
        self.factory.register_strategies_with_tool_manager(self.tool_manager)

        # Create test opinions
        self.opinions = [
            {
                "role_id": "expert",
                "content": "The solution is to use a distributed system",
                "confidence": 0.9
            },
            {
                "role_id": "novice",
                "content": "We should use a centralized approach",
                "confidence": 0.7
            }
        ]

    @patch("src.unified_tool_manager.UnifiedToolManager.execute_tool")
    async def test_strategy_execution(self, mock_execute_tool):
        """Test executing a custom strategy."""
        # Set up the mock to return a consensus result
        mock_result = {
            "consensus_text": "The solution is to use a distributed system",
            "agreement_level": 1.0,
            "method_description": "Custom consensus strategy with param: test_param"
        }
        mock_execute_tool.return_value = mock_result

        # Execute the strategy through the tool manager
        result = await self.tool_manager.execute_tool(
            "consensus.custom_strategy",
            opinions=self.opinions,
            custom_param="test_param"
        )

        # Verify the result
        self.assertEqual(result["consensus_text"], "The solution is to use a distributed system")
        self.assertEqual(result["agreement_level"], 1.0)
        self.assertEqual(result["method_description"], "Custom consensus strategy with param: test_param")

        # Verify that execute_tool was called with the correct parameters
        mock_execute_tool.assert_called_once_with(
            "consensus.custom_strategy",
            opinions=self.opinions,
            custom_param="test_param"
        )

    async def test_direct_strategy_execution(self):
        """Test executing a custom strategy directly."""
        # Create a strategy instance
        strategy = self.factory.create("custom_strategy", custom_param="test_param")

        # Execute the strategy
        result = await strategy.execute(self.opinions)

        # Verify the result
        self.assertEqual(result["consensus_text"], "The solution is to use a distributed system")
        self.assertEqual(result["agreement_level"], 1.0)
        self.assertEqual(result["method_description"], "Custom consensus strategy with param: test_param")
        self.assertEqual(result["custom_metadata"]["custom_param"], "test_param")
        self.assertEqual(result["custom_metadata"]["num_opinions"], 2)


if __name__ == "__main__":
    unittest.main()
