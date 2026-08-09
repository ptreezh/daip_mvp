"""
Argument Management for newP6 TUI Debate System

Handles debate arguments, rebuttals, and evaluation.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Argument:
    """Represents a debate argument"""

    def __init__(
        self,
        participant_id: str,
        content: str,
        position: str,
        round_number: int = 1,
        argument_id: Optional[str] = None,
    ):
        self.id = argument_id or str(uuid.uuid4())
        self.participant_id = participant_id
        self.content = content
        self.position = position
        self.round_number = round_number
        self.created_at = datetime.now()
        self.rebuttals: list[Argument] = []
        self.score: Optional[float] = None
        self.evaluation: Optional[str] = None
        self.evaluated_at: Optional[datetime] = None
        self.metadata: dict[str, Any] = {}

    def add_rebuttal(self, rebuttal: "Argument") -> None:
        """Add a rebuttal to this argument"""
        if rebuttal.id not in [r.id for r in self.rebuttals]:
            self.rebuttals.append(rebuttal)
            logger.debug(f"Added rebuttal {rebuttal.id} to argument {self.id}")

    def remove_rebuttal(self, rebuttal_id: str) -> bool:
        """Remove a rebuttal by ID"""
        for i, rebuttal in enumerate(self.rebuttals):
            if rebuttal.id == rebuttal_id:
                del self.rebuttals[i]
                logger.debug(f"Removed rebuttal {rebuttal_id} from argument {self.id}")
                return True
        return False

    def evaluate(self, score: float, evaluation: str) -> None:
        """Evaluate the argument"""
        self.score = max(0.0, min(10.0, score))  # Clamp between 0 and 10
        self.evaluation = evaluation
        self.evaluated_at = datetime.now()
        logger.debug(f"Evaluated argument {self.id} with score {self.score}")

    def get_word_count(self) -> int:
        """Get word count of the argument"""
        return len(self.content.split())

    def get_rebuttal_count(self) -> int:
        """Get number of rebuttals"""
        return len(self.rebuttals)

    def to_dict(self) -> dict[str, Any]:
        """Convert argument to dictionary"""
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "content": self.content,
            "position": self.position,
            "round_number": self.round_number,
            "created_at": self.created_at.isoformat(),
            "rebuttals": [r.to_dict() for r in self.rebuttals],
            "score": self.score,
            "evaluation": self.evaluation,
            "evaluated_at": self.evaluated_at.isoformat()
            if self.evaluated_at
            else None,
            "metadata": self.metadata,
            "word_count": self.get_word_count(),
            "rebuttal_count": self.get_rebuttal_count(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Argument":
        """Create argument from dictionary"""
        argument = cls(
            participant_id=data["participant_id"],
            content=data["content"],
            position=data["position"],
            round_number=data.get("round_number", 1),
            argument_id=data.get("id"),
        )

        if "created_at" in data:
            argument.created_at = datetime.fromisoformat(data["created_at"])

        if "score" in data:
            argument.score = data["score"]

        if "evaluation" in data:
            argument.evaluation = data["evaluation"]

        if "evaluated_at" in data and data["evaluated_at"]:
            argument.evaluated_at = datetime.fromisoformat(data["evaluated_at"])

        if "metadata" in data:
            argument.metadata = data["metadata"]

        return argument

    def __str__(self) -> str:
        """String representation"""
        return f"Argument({self.id[:8]}...) by {self.participant_id} - {self.position}"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"Argument(id={self.id[:8]}..., participant_id={self.participant_id}, "
            f"position={self.position}, score={self.score})"
        )
