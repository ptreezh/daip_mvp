"""
Core Debate Management for newP6 TUI Debate System

Handles debate lifecycle, participants, and rounds.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from .argument import Argument
from .participant import DebateParticipant
from .round import DebateRound

logger = logging.getLogger(__name__)


class Debate:
    """Represents a complete debate"""

    def __init__(
        self,
        topic: str,
        description: str = "",
        max_participants: int = 4,
        max_rounds: int = 3,
        debate_id: Optional[str] = None,
    ):
        self.id = debate_id or str(uuid.uuid4())
        self.topic = topic
        self.description = description
        self.max_participants = max_participants
        self.max_rounds = max_rounds
        self.participants: list[DebateParticipant] = []
        self.rounds: list[DebateRound] = []
        self.status = "preparing"  # preparing, active, paused, completed, cancelled
        self.current_round = 0
        self.is_active = False
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.metadata: dict[str, Any] = {}

    def add_participant(self, participant: DebateParticipant) -> bool:
        """Add a participant to the debate"""
        if len(self.participants) >= self.max_participants:
            logger.warning(f"Debate {self.id} has reached max participants")
            return False

        if self.status != "preparing":
            logger.warning(
                f"Cannot add participants to debate {self.id} in status {self.status}"
            )
            return False

        # Check for duplicate participant IDs
        if any(p.id == participant.id for p in self.participants):
            logger.warning(f"Participant {participant.id} already in debate {self.id}")
            return False

        self.participants.append(participant)
        logger.info(f"Added participant {participant.name} to debate {self.id}")
        return True

    def remove_participant(self, participant_id: str) -> bool:
        """Remove a participant from the debate"""
        if self.status != "preparing":
            logger.warning(
                f"Cannot remove participants from debate {self.id} in status {self.status}"  # noqa: E501
            )
            return False

        for i, participant in enumerate(self.participants):
            if participant.id == participant_id:
                del self.participants[i]
                logger.info(
                    f"Removed participant {participant_id} from debate {self.id}"
                )
                return True

        return False

    def start(self) -> bool:
        """Start the debate"""
        if self.status != "preparing":
            logger.warning(f"Cannot start debate {self.id} in status {self.status}")
            return False

        if len(self.participants) < 2:
            logger.warning(f"Debate {self.id} needs at least 2 participants to start")
            return False

        self.status = "active"
        self.is_active = True
        self.started_at = datetime.now()
        self.current_round = 1

        # Create first round
        first_round = DebateRound(
            round_number=1, topic=self.topic, max_arguments_per_participant=1
        )
        first_round.start()
        self.rounds.append(first_round)

        logger.info(
            f"Started debate {self.id} with {len(self.participants)} participants"
        )
        return True

    def end(self) -> None:
        """End the debate"""
        if self.status == "completed":
            return

        self.status = "completed"
        self.is_active = False
        self.ended_at = datetime.now()

        # Complete current round if still active
        if self.current_round <= len(self.rounds):
            current_round = self.get_current_round()
            if current_round and current_round.status == "active":
                current_round.complete()

        logger.info(f"Ended debate {self.id}")

    def pause(self) -> None:
        """Pause the debate"""
        if self.status == "active":
            self.status = "paused"
            self.is_active = False

            current_round = self.get_current_round()
            if current_round:
                current_round.pause()

            logger.info(f"Paused debate {self.id}")

    def resume(self) -> None:
        """Resume the debate"""
        if self.status == "paused":
            self.status = "active"
            self.is_active = True

            current_round = self.get_current_round()
            if current_round:
                current_round.resume()

            logger.info(f"Resumed debate {self.id}")

    def cancel(self) -> None:
        """Cancel the debate"""
        self.status = "cancelled"
        self.is_active = False
        self.ended_at = datetime.now()
        logger.info(f"Cancelled debate {self.id}")

    def start_next_round(self) -> bool:
        """Start the next round"""
        if not self.is_active or self.status != "active":
            logger.warning(
                f"Cannot start next round for debate {self.id} - debate not active"
            )
            return False

        if self.current_round >= self.max_rounds:
            logger.info(f"Debate {self.id} has reached maximum rounds")
            self.end()
            return False

        # Complete current round
        current_round = self.get_current_round()
        if current_round:
            current_round.complete()

        # Start next round
        self.current_round += 1
        next_round = DebateRound(
            round_number=self.current_round,
            topic=self.topic,
            max_arguments_per_participant=2,
        )
        next_round.start()
        self.rounds.append(next_round)

        logger.info(f"Started round {self.current_round} for debate {self.id}")
        return True

    def get_current_round(self) -> Optional[DebateRound]:
        """Get the current round"""
        if 1 <= self.current_round <= len(self.rounds):
            return self.rounds[self.current_round - 1]
        return None

    def get_participant(self, participant_id: str) -> Optional[DebateParticipant]:
        """Get participant by ID"""
        for participant in self.participants:
            if participant.id == participant_id:
                return participant
        return None

    def get_all_arguments(self) -> list[Argument]:
        """Get all arguments from all rounds"""
        all_arguments = []
        for round in self.rounds:
            all_arguments.extend(round.arguments)
        return all_arguments

    def get_arguments_by_participant(self, participant_id: str) -> list[Argument]:
        """Get all arguments from a specific participant"""
        return [
            arg
            for arg in self.get_all_arguments()
            if arg.participant_id == participant_id
        ]

    def get_summary(self) -> str:
        """Get debate summary"""
        summary = f"Debate: {self.topic}\n"
        summary += f"Description: {self.description}\n"
        summary += f"Status: {self.status}\n"
        summary += f"Participants: {len(self.participants)}\n"
        summary += f"Rounds: {self.current_round}/{self.max_rounds}\n"

        if self.participants:
            summary += "Participants:\n"
            for participant in self.participants:
                summary += f"  - {participant.name} ({participant.role.value})\n"

        if self.rounds:
            summary += "Rounds completed:\n"
            for round in self.rounds:
                status_emoji = "✓" if round.status == "completed" else "○"
                summary += f"  {status_emoji} Round {round.round_number}: {len(round.arguments)} arguments\n"  # noqa: E501

        if self.started_at:
            summary += f"Started: {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

        if self.ended_at:
            duration = self.ended_at - self.started_at if self.started_at else None
            summary += f"Ended: {self.ended_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if duration:
                summary += f"Duration: {duration.total_seconds():.1f} seconds\n"

        return summary

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive debate statistics"""
        stats = {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "status": self.status,
            "max_participants": self.max_participants,
            "actual_participants": len(self.participants),
            "max_rounds": self.max_rounds,
            "actual_rounds": self.current_round,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }

        # Duration statistics
        if self.started_at:
            if self.ended_at:
                stats["duration_seconds"] = (
                    self.ended_at - self.started_at
                ).total_seconds()
            else:
                stats["duration_seconds"] = (
                    datetime.now() - self.started_at
                ).total_seconds()

        # Argument statistics
        all_arguments = self.get_all_arguments()
        stats["total_arguments"] = len(all_arguments)

        if all_arguments:
            word_counts = [arg.get_word_count() for arg in all_arguments]
            stats["avg_word_count"] = sum(word_counts) / len(word_counts)
            stats["min_word_count"] = min(word_counts)
            stats["max_word_count"] = max(word_counts)

            scored_args = [arg for arg in all_arguments if arg.score is not None]
            if scored_args:
                scores = [arg.score for arg in scored_args]
                stats["avg_score"] = sum(scores) / len(scores)
                stats["min_score"] = min(scores)
                stats["max_score"] = max(scores)

            # Arguments by role
            role_stats = {}
            for participant in self.participants:
                role = participant.role.value
                role_args = len(self.get_arguments_by_participant(participant.id))
                role_stats[role] = role_stats.get(role, 0) + role_args
            stats["arguments_by_role"] = role_stats

        # Round statistics
        stats["round_statistics"] = []
        for round in self.rounds:
            stats["round_statistics"].append(round.get_statistics())

        return stats

    def to_dict(self) -> dict[str, Any]:
        """Convert debate to dictionary"""
        return {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "max_participants": self.max_participants,
            "max_rounds": self.max_rounds,
            "participants": [p.to_dict() for p in self.participants],
            "rounds": [r.to_dict() for r in self.rounds],
            "status": self.status,
            "current_round": self.current_round,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "metadata": self.metadata,
            "statistics": self.get_statistics(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Debate":
        """Create debate from dictionary"""
        debate = cls(
            topic=data["topic"],
            description=data.get("description", ""),
            max_participants=data.get("max_participants", 4),
            max_rounds=data.get("max_rounds", 3),
            debate_id=data.get("id"),
        )

        if "status" in data:
            debate.status = data["status"]

        if "current_round" in data:
            debate.current_round = data["current_round"]

        if "is_active" in data:
            debate.is_active = data["is_active"]

        if "created_at" in data:
            debate.created_at = datetime.fromisoformat(data["created_at"])

        if "started_at" in data and data["started_at"]:
            debate.started_at = datetime.fromisoformat(data["started_at"])

        if "ended_at" in data and data["ended_at"]:
            debate.ended_at = datetime.fromisoformat(data["ended_at"])

        if "metadata" in data:
            debate.metadata = data["metadata"]

        # Restore participants
        if "participants" in data:
            debate.participants = [
                DebateParticipant.from_dict(p_data) for p_data in data["participants"]
            ]

        # Restore rounds
        if "rounds" in data:
            debate.rounds = [DebateRound.from_dict(r_data) for r_data in data["rounds"]]

        return debate

    def __str__(self) -> str:
        """String representation"""
        return f"Debate: {self.topic} ({self.status})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"Debate(id={self.id[:8]}..., topic='{self.topic}', status='{self.status}', "  # noqa: E501
            f"participants={len(self.participants)}, rounds={self.current_round}/{self.max_rounds})"  # noqa: E501
        )
