# -*- coding: utf-8 -*-
"""
@Time    : 2023-10-27 10:05:00
@Author  : DAIP-LIVE Team
@File    : consensus_strategies.py
@Description:
    Implements the Strategy Pattern for reaching consensus in debates.
    Includes an abstract base class, concrete strategy implementations,
    and a factory for managing strategies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from src.models import DebateTurn


class ConsensusStrategy(ABC):
    """Abstract base class for all consensus strategies."""

    @abstractmethod
    def execute(self, history: List[DebateTurn]) -> Any:
        """
        Executes the consensus-finding logic.

        Args:
            history (List[DebateTurn]): The full history of the debate.

        Returns:
            Any: The outcome of the consensus process.
        """
        pass


class SimpleMajorityVoteStrategy(ConsensusStrategy):
    """
    A simple consensus strategy based on majority vote.

    This strategy parses the last opinion of each role for keywords to determine
    their vote (e.g., 'agree' vs. 'disagree').
    """

    @staticmethod # Make it a static method
    def execute(history: List[DebateTurn]) -> Dict[str, Any]:
        """
        Counts votes based on keywords in the last turn of each role.
        """
        votes: Dict[str, int] = {"agree": 0, "disagree": 0, "neutral": 0}
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
        self._strategies: Dict[str, Type[ConsensusStrategy]] = {}

    def register(self, name: str, strategy_class: Type[ConsensusStrategy]):
        """Registers a new consensus strategy."""
        self._strategies[name] = strategy_class

    def get_strategy(self, name: str) -> ConsensusStrategy:
        """Gets an instance of a registered consensus strategy."""
        strategy_class = self._strategies.get(name)
        if not strategy_class:
            raise ValueError(f"Consensus strategy '{name}' not registered.")
        return strategy_class()

    def get_all_strategies(self) -> Dict[str, Type[ConsensusStrategy]]:
        """Returns all registered strategy classes."""
        return self._strategies
