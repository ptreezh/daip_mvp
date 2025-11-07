"""
Debate Roles Configuration for newP6 TUI

Defines debate role types and configurations.
"""

from enum import Enum
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RoleType(Enum):
    """Debate role types"""
    PROPONENT = "proponent"  # Supports the topic
    OPPONENT = "opponent"    # Opposes the topic
    MODERATOR = "moderator"  # Facilitates the debate
    EXPERT = "expert"        # Provides expert insights
    DEVILS_ADVOCATE = "devils_advocate"  # Challenges assumptions


class DebateRole:
    """Debate role configuration"""

    def __init__(
        self,
        name: str,
        role_type: RoleType,
        description: str,
        model: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        self.name = name
        self.role_type = role_type
        self.description = description
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_configuration(self) -> Dict[str, Any]:
        """Get role configuration for AI model"""
        return {
            "name": self.name,
            "role_type": self.role_type.value,
            "description": self.description,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

    def is_valid(self) -> bool:
        """Validate role configuration"""
        return (
            bool(self.name.strip()) and
            bool(self.description.strip()) and
            bool(self.system_prompt.strip()) and
            bool(self.model.strip()) and
            0.0 <= self.temperature <= 2.0 and
            self.max_tokens > 0
        )

    def get_debate_prompt(self, topic: str, context: Dict[str, Any]) -> str:
        """Generate debate-specific prompt for this role"""
        base_prompt = self.system_prompt

        # Add role-specific instructions
        if self.role_type == RoleType.PROPONENT:
            role_instruction = f"You are advocating FOR the topic: '{topic}'. Provide strong supporting arguments."
        elif self.role_type == RoleType.OPPONENT:
            role_instruction = f"You are arguing AGAINST the topic: '{topic}'. Provide strong counterarguments."
        elif self.role_type == RoleType.MODERATOR:
            role_instruction = f"You are moderating a debate on: '{topic}'. Ensure balanced discussion."
        elif self.role_type == RoleType.EXPERT:
            role_instruction = f"You are providing expert insights on: '{topic}'. Share your expertise objectively."
        elif self.role_type == RoleType.DEVILS_ADVOCATE:
            role_instruction = f"You are playing devil's advocate for: '{topic}'. Challenge all assumptions and arguments."
        else:
            role_instruction = f"Participate in the debate on: '{topic}' according to your role."

        # Add context
        context_info = ""
        if context.get("round"):
            context_info += f"Round: {context['round']}\n"
        if context.get("previous_arguments"):
            context_info += "Previous arguments:\n"
            for i, arg in enumerate(context["previous_arguments"][-3:], 1):  # Last 3 arguments
                context_info += f"{i}. {arg}\n"

        return f"{base_prompt}\n\n{role_instruction}\n\n{context_info}\n\nProvide your argument:"


# Predefined debate roles
PREDEFINED_ROLES = {
    "technology_optimist": DebateRole(
        name="Technology Optimist",
        role_type=RoleType.PROPONENT,
        description="Advocates for technological progress and innovation",
        model="gpt-4",
        system_prompt="You are a technology optimist who believes in the positive potential of technology to solve human problems. You focus on benefits, progress, and opportunities while being realistic about challenges.",
        temperature=0.8
    ),

    "technology_skeptic": DebateRole(
        name="Technology Skeptic",
        role_type=RoleType.OPPONENT,
        description="Questions the safety and ethics of technological development",
        model="claude-3",
        system_prompt="You are a thoughtful technology skeptic who raises important questions about safety, ethics, and unintended consequences. You believe in proceeding with caution and ensuring proper safeguards.",
        temperature=0.7
    ),

    "ethical_philosopher": DebateRole(
        name="Ethical Philosopher",
        role_type=RoleType.EXPERT,
        description="Provides philosophical and ethical perspectives",
        model="gpt-4",
        system_prompt="You are an ethical philosopher who considers the moral implications and philosophical foundations of technology. You bring historical context and ethical frameworks to the discussion.",
        temperature=0.6
    ),

    "pragmatic_moderator": DebateRole(
        name="Pragmatic Moderator",
        role_type=RoleType.MODERATOR,
        description="Facilitates balanced discussion and finds common ground",
        model="claude-3",
        system_prompt="You are a pragmatic moderator who ensures all voices are heard and the discussion stays productive. You identify key points of agreement and disagreement, and help move toward constructive conclusions.",
        temperature=0.5
    ),

    "devils_advocate": DebateRole(
        name="Devil's Advocate",
        role_type=RoleType.DEVILS_ADVOCATE,
        description="Challenges assumptions and explores edge cases",
        model="gpt-4",
        system_prompt="You are a devil's advocate who questions all assumptions and explores potential problems, edge cases, and unintended consequences. Your role is to strengthen arguments by identifying weaknesses.",
        temperature=0.9
    )
}


def get_role(role_name: str) -> Optional[DebateRole]:
    """Get predefined role by name"""
    return PREDEFINED_ROLES.get(role_name.lower())


def list_available_roles() -> Dict[str, DebateRole]:
    """List all available predefined roles"""
    return PREDEFINED_ROLES.copy()