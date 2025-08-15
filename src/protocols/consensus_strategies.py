"""@Time    : 2023-10-27 10:05:00
@Author  : DAIP-LIVE Team
@File    : consensus_strategies.py
@Description:
    Implements the Strategy Pattern for reaching consensus in debates.
    Includes an abstract base class, concrete strategy implementations,
    and a factory for managing strategies.
"""

from abc import ABC, abstractmethod
from typing import Any

from src.models import DebateTurn


class ConsensusStrategy(ABC):
    """Abstract base class for all consensus strategies."""

    @abstractmethod
<<<<<<< HEAD
    def execute(self, history: List[DebateTurn]) -> Any:
=======
    def execute(self, history: list[DebateTurn]) -> Any:
>>>>>>> feature/core-services-refactor
        """Executes the consensus-finding logic.

        Args:
            history (List[DebateTurn]): The full history of the debate.

        Returns:
            Any: The outcome of the consensus process.

        """
        pass


class SimpleMajorityVoteStrategy(ConsensusStrategy):
    """A simple consensus strategy based on majority vote.

    This strategy parses the last opinion of each role for keywords to determine
    their vote (e.g., 'agree' vs. 'disagree').
    """

    @staticmethod # Make it a static method
<<<<<<< HEAD
    def execute(history: List[DebateTurn]) -> Dict[str, Any]:
        """Counts votes based on keywords in the last turn of each role.
        """
        votes: Dict[str, int] = {"agree": 0, "disagree": 0, "neutral": 0}
=======
    def execute(history: list[DebateTurn]) -> dict[str, Any]:
        """Counts votes based on keywords in the last turn of each role.
        """
        votes: dict[str, int] = {"agree": 0, "disagree": 0, "neutral": 0}
>>>>>>> feature/core-services-refactor
        roles_voted = set()
        # Iterate backwards to find the last opinion of each role
        for turn in reversed(history):
            if turn.role_id not in roles_voted:
                opinion = turn.opinion.lower()
                if "agree" in opinion or "support" in opinion:
                    votes["agree"] += 1
                elif "disagree" in opinion or "oppose" in opinion:
                    votes["disagree"] += 1
                else:
                    votes["neutral"] += 1
                roles_voted.add(turn.role_id)

        winner = max(votes, key=votes.get)
        return {"votes": votes, "outcome": winner}


class ConsensusStrategyFactory:
    """Factory for creating and managing consensus strategy instances."""

    def __init__(self):
        self._strategies: dict[str, type[ConsensusStrategy]] = {}
        # Public property for test compatibility
        self.strategies = self._strategies

    def register(self, name: str, strategy_class: type[ConsensusStrategy]):
        """Registers a new consensus strategy."""
        self._strategies[name] = strategy_class

    def get_strategy(self, name: str) -> ConsensusStrategy:
        """Gets an instance of a registered consensus strategy."""
        strategy_class = self._strategies.get(name)
        if not strategy_class:
            raise ValueError(f"Consensus strategy '{name}' not registered.")
        return strategy_class()

    def get_all_strategies(self) -> dict[str, type[ConsensusStrategy]]:
        """Returns all registered strategy classes."""
        return self._strategies

    def create(self, name: str, **kwargs) -> ConsensusStrategy:
        """Creates an instance of a registered consensus strategy with parameters."""
        strategy_class = self._strategies.get(name)
        if not strategy_class:
            raise ValueError(f"Consensus strategy '{name}' not registered.")
        return strategy_class(**kwargs)

    def register_strategies_with_tool_manager(self, tool_manager):
        """Registers all strategies with the tool manager."""
        for name, strategy_class in self._strategies.items():
            tool_manager.register_tool(
                f"consensus.{name}",
                strategy_class,
                description="Custom consensus strategy" if name == "custom_strategy" else f"{name.replace('_', ' ').title()} consensus strategy"
            )
