"""
Debate Participant Management for newP6 TUI Debate System

Handles AI participants in debates.
"""

from typing import List, Dict, Any, Optional, Union
import logging
import uuid
import asyncio

from .argument import Argument
from .roles import DebateRole, RoleType

logger = logging.getLogger(__name__)


class DebateParticipant:
    """Represents a debate participant"""

    def __init__(
        self,
        name: str,
        role: Union[str, RoleType],
        model: str,
        participant_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        self.id = participant_id or str(uuid.uuid4())
        self.name = name
        self.role = role if isinstance(role, RoleType) else RoleType(role)
        self.model = model
        self.system_prompt = system_prompt or self._get_default_prompt()
        self.arguments: List[Argument] = []
        self.model_service: Optional[Any] = None
        self.metadata: Dict[str, Any] = {}

    def _get_default_prompt(self) -> str:
        """Get default system prompt based on role"""
        prompts = {
            RoleType.PROPONENT: "You are advocating for the given topic. Provide strong supporting arguments with evidence and reasoning.",
            RoleType.OPPONENT: "You are arguing against the given topic. Provide strong counterarguments with evidence and reasoning.",
            RoleType.MODERATOR: "You are moderating the debate. Ensure balanced discussion and provide constructive feedback.",
            RoleType.EXPERT: "You are an expert providing insights. Share your expertise objectively and professionally.",
            RoleType.DEVILS_ADVOCATE: "You are playing devil's advocate. Challenge assumptions and explore potential problems."
        }
        return prompts.get(self.role, "Participate in the debate according to your role.")

    def add_argument(self, argument: Argument) -> None:
        """Add an argument from this participant"""
        if argument.participant_id == self.id:
            self.arguments.append(argument)
            logger.debug(f"Added argument {argument.id} to participant {self.name}")

    def get_argument_count(self) -> int:
        """Get number of arguments from this participant"""
        return len(self.arguments)

    def get_position(self) -> str:
        """Get participant position as string"""
        return f"{self.role.value} ({self.name})"

    def set_model_service(self, model_service: Any) -> None:
        """Set the model service for generating arguments"""
        self.model_service = model_service

    async def generate_argument(
        self,
        topic: str,
        context: Dict[str, Any],
        previous_arguments: Optional[List[str]] = None
    ) -> Argument:
        """Generate an argument for the given topic"""
        if not self.model_service:
            # Fallback argument generation
            content = self._generate_fallback_argument(topic, context)
        else:
            content = await self._generate_model_argument(topic, context, previous_arguments or [])

        argument = Argument(
            participant_id=self.id,
            content=content,
            position=self.role.value,
            round_number=context.get("round", 1)
        )

        self.add_argument(argument)
        return argument

    async def _generate_model_argument(
        self,
        topic: str,
        context: Dict[str, Any],
        previous_arguments: List[str]
    ) -> str:
        """Generate argument using the model service"""
        try:
            # Build the prompt
            prompt = self.system_prompt + "\n\n"
            prompt += f"Topic: {topic}\n"
            prompt += f"Round: {context.get('round', 1)}\n"

            if previous_arguments:
                prompt += "Previous arguments:\n"
                for i, arg in enumerate(previous_arguments[-3:], 1):  # Last 3 arguments
                    prompt += f"{i}. {arg}\n"

            prompt += f"\nProvide your {self.role.value} argument:"

            # Call the model service
            if hasattr(self.model_service, 'generate_response'):
                response = await self.model_service.generate_response(prompt)
                return response.get("content", "Unable to generate argument.")
            elif hasattr(self.model_service, 'chat'):
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
                response = await self.model_service.chat(messages)
                return response.get("content", "Unable to generate argument.")
            else:
                return self._generate_fallback_argument(topic, context)

        except Exception as e:
            logger.error(f"Error generating argument for participant {self.name}: {e}")
            return self._generate_fallback_argument(topic, context)

    def _generate_fallback_argument(self, topic: str, context: Dict[str, Any]) -> str:
        """Generate a fallback argument when model service is unavailable"""
        round_num = context.get("round", 1)

        fallbacks = {
            RoleType.PROPONENT: [
                f"I strongly support {topic} because it offers significant benefits and opportunities for progress.",
                f"{topic} represents an important step forward that we should embrace for the betterment of society.",
                f"The advantages of {topic} far outweigh any potential concerns when properly implemented."
            ],
            RoleType.OPPONENT: [
                f"I have serious concerns about {topic} due to potential risks and unintended consequences.",
                f"We should carefully reconsider {topic} as it may create more problems than it solves.",
                f"The drawbacks of {topic} require thorough examination before proceeding."
            ],
            RoleType.MODERATOR: [
                f"Let's ensure we consider all perspectives on {topic} in a balanced and constructive manner.",
                f"The discussion on {topic} requires careful moderation to ensure productive dialogue.",
                f"We should focus on finding common ground regarding {topic} while respecting diverse viewpoints."
            ],
            RoleType.EXPERT: [
                f"From an expert perspective, {topic} requires careful analysis of both benefits and risks.",
                f"My professional assessment of {topic} indicates several key factors that must be considered.",
                f"Based on expertise in this area, {topic} presents both opportunities and challenges."
            ],
            RoleType.DEVILS_ADVOCATE: [
                f"While {topic} may seem appealing, we must question the underlying assumptions and potential failures.",
                f"Let's challenge the conventional wisdom about {topic} and explore alternative perspectives.",
                f"The arguments for {topic} deserve critical examination to identify potential weaknesses."
            ]
        }

        role_fallbacks = fallbacks.get(self.role, ["I will provide a thoughtful argument on this topic."])

        # Select argument based on round number
        index = (round_num - 1) % len(role_fallbacks)
        return role_fallbacks[index]

    def get_statistics(self) -> Dict[str, Any]:
        """Get participant statistics"""
        stats = {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "model": self.model,
            "argument_count": len(self.arguments)
        }

        if self.arguments:
            word_counts = [arg.get_word_count() for arg in self.arguments]
            stats["total_words"] = sum(word_counts)
            stats["avg_words_per_argument"] = sum(word_counts) / len(word_counts)

            scored_args = [arg for arg in self.arguments if arg.score is not None]
            if scored_args:
                scores = [arg.score for arg in scored_args]
                stats["avg_score"] = sum(scores) / len(scores)
                stats["best_score"] = max(scores)
                stats["worst_score"] = min(scores)

            rebuttal_counts = [arg.get_rebuttal_count() for arg in self.arguments]
            stats["total_rebuttals_received"] = sum(rebuttal_counts)
            stats["avg_rebuttals_per_argument"] = sum(rebuttal_counts) / len(rebuttal_counts)

        return stats

    def to_dict(self) -> Dict[str, Any]:
        """Convert participant to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "arguments": [arg.to_dict() for arg in self.arguments],
            "metadata": self.metadata,
            "statistics": self.get_statistics()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebateParticipant":
        """Create participant from dictionary"""
        participant = cls(
            name=data["name"],
            role=RoleType(data["role"]),
            model=data["model"],
            participant_id=data.get("id"),
            system_prompt=data.get("system_prompt")
        )

        if "metadata" in data:
            participant.metadata = data["metadata"]

        # Restore arguments
        if "arguments" in data:
            participant.arguments = [Argument.from_dict(arg_data) for arg_data in data["arguments"]]

        return participant

    def __str__(self) -> str:
        """String representation"""
        return f"{self.name} ({self.role.value})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"DebateParticipant(id={self.id[:8]}..., name='{self.name}', "
                f"role={self.role.value}, model='{self.model}', arguments={len(self.arguments)})")