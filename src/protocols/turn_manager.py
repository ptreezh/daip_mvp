"""@Time    : 2024-07-12 10:30:00
@Author  : DAIP-LIVE Team
@File    : turn_manager.py
@Description:
    Manages the state of a debate's turns, including round and role tracking.
"""

from src.models import DebateConfig


class TurnManager:
    """Manages the turn-taking logic for a debate based on a configuration.
    This class tracks the current round and which role is set to speak next,
    implementing a round-robin policy.
    """

    def __init__(self, config: DebateConfig):
        """Initializes the TurnManager with the debate configuration.

        Args:
            config (DebateConfig): The configuration object for the debate,
                                   containing roles and number of rounds.
        """
        self._roles: list[str] = config.roles
        self._total_rounds: int = config.rounds
        self._current_round: int = 1
        self._current_role_index: int = 0

    def is_finished(self) -> bool:
        """Checks if the debate has completed all its configured rounds.

        Returns:
            bool: True if the current round exceeds the total rounds, False otherwise.
        """
        return self._current_round > self._total_rounds

    def get_current_turn(self) -> tuple[int, str]:
        """Gets the current turn's round number and the ID of the role that should speak.

        Returns:
            Tuple[int, str]: A tuple containing the current round number and the current role ID.
        """
        return self._current_round, self._roles[self._current_role_index]

    def advance(self) -> None:
        """Advances the state to the next turn.
        It moves to the next role in the list. If all roles have spoken in the
        current round, it advances to the next round and resets the role index.
        """
        self._current_role_index += 1
        if self._current_role_index >= len(self._roles):
            self._current_role_index = 0
            self._current_round += 1