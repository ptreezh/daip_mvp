"""
Debate Manager for newP6 TUI Debate System

Coordinates debate creation, management, and execution.
"""

from typing import List, Dict, Any, Optional
import logging
import uuid
import asyncio

from .debate import Debate
from .participant import DebateParticipant
from .argument import Argument
from .round import DebateRound
from .roles import DebateRole, RoleType, get_role, list_available_roles

logger = logging.getLogger(__name__)


class DebateManager:
    """Manages multiple debates and debate execution"""

    def __init__(self):
        self.debates: List[Debate] = []
        self._debate_id_counter = 1
        self.model_service: Optional[Any] = None

    def set_model_service(self, model_service: Any) -> None:
        """Set the model service for argument generation"""
        self.model_service = model_service

    def create_debate(
        self,
        topic: str,
        description: str = "",
        max_participants: int = 4,
        max_rounds: int = 3
    ) -> Debate:
        """Create a new debate"""
        debate = Debate(
            topic=topic,
            description=description,
            max_participants=max_participants,
            max_rounds=max_rounds
        )

        self.debates.append(debate)
        self._debate_id_counter += 1
        logger.info(f"Created debate: {debate.id} - {topic}")
        return debate

    def get_debate(self, debate_id: str) -> Optional[Debate]:
        """Get debate by ID"""
        for debate in self.debates:
            if debate.id == debate_id:
                return debate
        return None

    def list_debates(self) -> List[Debate]:
        """List all debates"""
        return self.debates.copy()

    def list_active_debates(self) -> List[Debate]:
        """List only active debates"""
        return [debate for debate in self.debates if debate.is_active]

    def delete_debate(self, debate_id: str) -> bool:
        """Delete a debate"""
        for i, debate in enumerate(self.debates):
            if debate.id == debate_id:
                debate.cancel()  # Cancel the debate first
                del self.debates[i]
                logger.info(f"Deleted debate: {debate_id}")
                return True
        return False

    async def start_debate(self, debate_id: str) -> bool:
        """Start a debate"""
        debate = self.get_debate(debate_id)
        if not debate:
            logger.error(f"Debate {debate_id} not found")
            return False

        success = debate.start()
        if success:
            # Set model service for all participants
            for participant in debate.participants:
                participant.set_model_service(self.model_service)

            logger.info(f"Started debate {debate_id}")
        return success

    async def execute_round(
        self,
        debate_id: str,
        round_number: Optional[int] = None
    ) -> Optional[DebateRound]:
        """Execute a debate round"""
        debate = self.get_debate(debate_id)
        if not debate:
            logger.error(f"Debate {debate_id} not found")
            return None

        if not debate.is_active:
            logger.error(f"Debate {debate_id} is not active")
            return None

        # Determine which round to execute
        if round_number is None:
            round_number = debate.current_round
        elif round_number > len(debate.rounds):
            logger.error(f"Round {round_number} does not exist in debate {debate_id}")
            return None

        # Get the round
        if round_number <= 0 or round_number > len(debate.rounds):
            logger.error(f"Invalid round number {round_number} for debate {debate_id}")
            return None

        current_round = debate.rounds[round_number - 1]
        if current_round.status != "active":
            logger.warning(f"Round {round_number} is not active (status: {current_round.status})")
            return current_round

        logger.info(f"Executing round {round_number} for debate {debate_id}")

        # Generate arguments from each participant
        context = {
            "round": round_number,
            "previous_arguments": [arg.content for arg in debate.get_all_arguments()]
        }

        for participant in debate.participants:
            try:
                # Check if participant has already reached max arguments for this round
                participant_args = current_round.get_arguments_by_participant(participant.id)
                if len(participant_args) >= current_round.max_arguments_per_participant:
                    logger.debug(f"Participant {participant.name} has reached max arguments for round {round_number}")
                    continue

                # Generate argument
                argument = await participant.generate_argument(
                    topic=debate.topic,
                    context=context,
                    previous_arguments=context["previous_arguments"]
                )

                # Add argument to round
                if current_round.add_argument(argument):
                    logger.info(f"Generated argument from {participant.name} for round {round_number}")
                else:
                    logger.warning(f"Failed to add argument from {participant.name} to round {round_number}")

            except Exception as e:
                logger.error(f"Error generating argument from {participant.name}: {e}")
                # Create fallback argument
                fallback_content = participant._generate_fallback_argument(debate.topic, context)
                argument = Argument(
                    participant_id=participant.id,
                    content=fallback_content,
                    position=participant.role.value,
                    round_number=round_number
                )
                current_round.add_argument(argument)

        # Complete the round
        current_round.complete()
        logger.info(f"Completed round {round_number} for debate {debate_id}")

        return current_round

    async def execute_debate_to_completion(self, debate_id: str) -> bool:
        """Execute a debate until completion"""
        debate = self.get_debate(debate_id)
        if not debate:
            logger.error(f"Debate {debate_id} not found")
            return False

        # Start the debate if not already started
        if debate.status == "preparing":
            if not await self.start_debate(debate_id):
                return False

        # Execute all rounds
        while debate.current_round <= debate.max_rounds and debate.is_active:
            logger.info(f"Executing round {debate.current_round}/{debate.max_rounds} for debate {debate_id}")

            round_result = await self.execute_round(debate_id, debate.current_round)
            if not round_result:
                logger.error(f"Failed to execute round {debate.current_round} for debate {debate_id}")
                return False

            # Small delay between rounds
            await asyncio.sleep(0.1)

            # Start next round unless we've reached max rounds
            if debate.current_round < debate.max_rounds:
                if not debate.start_next_round():
                    break

        # End the debate
        debate.end()
        logger.info(f"Completed debate {debate_id}")
        return True

    async def get_debate_statistics(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a debate"""
        debate = self.get_debate(debate_id)
        if not debate:
            return None

        return debate.get_statistics()

    def create_participant_from_role(
        self,
        role_name: str,
        model: Optional[str] = None
    ) -> Optional[DebateParticipant]:
        """Create a participant from a predefined role"""
        role = get_role(role_name)
        if not role:
            logger.error(f"Role '{role_name}' not found")
            return None

        participant = DebateParticipant(
            name=role.name,
            role=role.role_type,
            model=model or role.model,
            system_prompt=role.system_prompt
        )

        # Set model service if available
        if self.model_service:
            participant.set_model_service(self.model_service)

        return participant

    def get_available_roles(self) -> Dict[str, DebateRole]:
        """Get all available predefined roles"""
        return list_available_roles()

    def search_debates(self, query: str) -> List[Debate]:
        """Search debates by topic or description"""
        query_lower = query.lower()
        matching_debates = []

        for debate in self.debates:
            if (query_lower in debate.topic.lower() or
                query_lower in debate.description.lower()):
                matching_debates.append(debate)

        return matching_debates

    def get_debates_by_status(self, status: str) -> List[Debate]:
        """Get debates filtered by status"""
        return [debate for debate in self.debates if debate.status == status]

    def cleanup_completed_debates(self, max_age_days: int = 30) -> int:
        """Clean up old completed debates"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        old_debates = [
            debate for debate in self.debates
            if (debate.status in ["completed", "cancelled"] and
                debate.ended_at and debate.ended_at < cutoff_date)
        ]

        for debate in old_debates:
            self.delete_debate(debate.id)

        logger.info(f"Cleaned up {len(old_debates)} old debates")
        return len(old_debates)

    def export_debate_data(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """Export complete debate data"""
        debate = self.get_debate(debate_id)
        if not debate:
            return None

        return debate.to_dict()

    def import_debate_data(self, data: Dict[str, Any]) -> Optional[Debate]:
        """Import debate data"""
        try:
            debate = Debate.from_dict(data)
            self.debates.append(debate)
            logger.info(f"Imported debate: {debate.id}")
            return debate
        except Exception as e:
            logger.error(f"Error importing debate data: {e}")
            return None

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        stats = {
            "total_debates": len(self.debates),
            "active_debates": len(self.list_active_debates()),
            "completed_debates": len(self.get_debates_by_status("completed")),
            "cancelled_debates": len(self.get_debates_by_status("cancelled")),
            "preparing_debates": len(self.get_debates_by_status("preparing"))
        }

        if self.debates:
            total_participants = sum(len(debate.participants) for debate in self.debates)
            stats["total_participants"] = total_participants
            stats["avg_participants_per_debate"] = total_participants / len(self.debates)

            total_arguments = sum(len(debate.get_all_arguments()) for debate in self.debates)
            stats["total_arguments"] = total_arguments
            stats["avg_arguments_per_debate"] = total_arguments / len(self.debates)

        return stats