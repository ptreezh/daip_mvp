"""
Debate Round Management for newP6 TUI Debate System

Handles individual debate rounds and argument collection.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from .argument import Argument

logger = logging.getLogger(__name__)


class DebateRound:
    """Represents a single debate round"""

    def __init__(
        self,
        round_number: int,
        topic: str,
        max_arguments_per_participant: int = 2,
        round_id: Optional[str] = None,
    ):
        self.id = round_id or str(uuid.uuid4())
        self.round_number = round_number
        self.topic = topic
        self.max_arguments_per_participant = max_arguments_per_participant
        self.arguments: list[Argument] = []
        self.status = "active"  # active, completed, paused
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.metadata: dict[str, Any] = {}

    def start(self) -> None:
        """Start the round"""
        self.status = "active"
        self.started_at = datetime.now()
        logger.info(f"Started debate round {self.round_number}")

    def add_argument(self, argument: Argument) -> bool:
        """Add an argument to the round"""
        # Check if participant has reached max arguments
        participant_args = self.get_arguments_by_participant(argument.participant_id)
        if len(participant_args) >= self.max_arguments_per_participant:
            logger.warning(
                f"Participant {argument.participant_id} has reached max arguments for round {self.round_number}"  # noqa: E501
            )
            return False

        # Set round number on argument
        argument.round_number = self.round_number

        self.arguments.append(argument)
        logger.info(f"Added argument {argument.id} to round {self.round_number}")
        return True

    def get_arguments_by_participant(self, participant_id: str) -> list[Argument]:
        """Get all arguments from a specific participant"""
        return [arg for arg in self.arguments if arg.participant_id == participant_id]

    def get_argument_count(self, participant_id: Optional[str] = None) -> int:
        """Get argument count, optionally filtered by participant"""
        if participant_id:
            return len(self.get_arguments_by_participant(participant_id))
        return len(self.arguments)

    def is_complete(self) -> bool:
        """Check if round is complete"""
        return self.status == "completed"

    def complete(self) -> None:
        """Complete the round"""
        self.status = "completed"
        self.completed_at = datetime.now()
        logger.info(f"Completed debate round {self.round_number}")

    def pause(self) -> None:
        """Pause the round"""
        self.status = "paused"
        logger.info(f"Paused debate round {self.round_number}")

    def resume(self) -> None:
        """Resume the round"""
        if self.status == "paused":
            self.status = "active"
            logger.info(f"Resumed debate round {self.round_number}")

    def get_summary(self) -> str:
        """Get round summary"""
        summary = f"Round {self.round_number}: {self.topic}\n"
        summary += f"Status: {self.status}\n"
        summary += f"Arguments: {len(self.arguments)}\n"

        if self.arguments:
            summary += "Arguments by participant:\n"
            participant_counts = {}
            for arg in self.arguments:
                participant_counts[arg.participant_id] = (
                    participant_counts.get(arg.participant_id, 0) + 1
                )

            for participant_id, count in participant_counts.items():
                summary += f"  {participant_id}: {count} arguments\n"

        if self.started_at:
            summary += f"Started: {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

        if self.completed_at:
            duration = self.completed_at - self.started_at if self.started_at else None
            summary += f"Completed: {self.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if duration:
                summary += f"Duration: {duration.total_seconds():.1f} seconds\n"

        return summary

    def get_statistics(self) -> dict[str, Any]:
        """Get round statistics"""
        stats = {
            "round_number": self.round_number,
            "topic": self.topic,
            "status": self.status,
            "total_arguments": len(self.arguments),
            "max_arguments_per_participant": self.max_arguments_per_participant,
            "participant_count": len({arg.participant_id for arg in self.arguments}),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }

        if self.started_at and self.completed_at:
            stats["duration_seconds"] = (
                self.completed_at - self.started_at
            ).total_seconds()

        # Argument statistics
        if self.arguments:
            word_counts = [arg.get_word_count() for arg in self.arguments]
            stats["avg_word_count"] = sum(word_counts) / len(word_counts)
            stats["min_word_count"] = min(word_counts)
            stats["max_word_count"] = max(word_counts)

            scored_args = [arg for arg in self.arguments if arg.score is not None]
            if scored_args:
                scores = [arg.score for arg in scored_args]
                stats["avg_score"] = sum(scores) / len(scores)
                stats["min_score"] = min(scores)
                stats["max_score"] = max(scores)

        return stats

    def to_dict(self) -> dict[str, Any]:
        """Convert round to dictionary"""
        return {
            "id": self.id,
            "round_number": self.round_number,
            "topic": self.topic,
            "max_arguments_per_participant": self.max_arguments_per_participant,
            "arguments": [arg.to_dict() for arg in self.arguments],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "metadata": self.metadata,
            "statistics": self.get_statistics(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DebateRound":
        """Create round from dictionary"""
        round = cls(
            round_number=data["round_number"],
            topic=data["topic"],
            max_arguments_per_participant=data.get("max_arguments_per_participant", 2),
            round_id=data.get("id"),
        )

        if "status" in data:
            round.status = data["status"]

        if "created_at" in data:
            round.created_at = datetime.fromisoformat(data["created_at"])

        if "started_at" in data and data["started_at"]:
            round.started_at = datetime.fromisoformat(data["started_at"])

        if "completed_at" in data and data["completed_at"]:
            round.completed_at = datetime.fromisoformat(data["completed_at"])

        if "metadata" in data:
            round.metadata = data["metadata"]

        # Restore arguments
        if "arguments" in data:
            from .argument import Argument

            round.arguments = [
                Argument.from_dict(arg_data) for arg_data in data["arguments"]
            ]

        return round

    def __str__(self) -> str:
        """String representation"""
        return f"Round {self.round_number}: {self.topic} ({self.status})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"DebateRound(id={self.id[:8]}..., round_number={self.round_number}, "
            f"topic='{self.topic}', status='{self.status}', arguments={len(self.arguments)})"  # noqa: E501
        )
