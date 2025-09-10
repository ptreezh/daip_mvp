from typing import List

from src.daip_live.core.models import AgentState, DialogueTurn, Session
from src.daip_live.memory.session_manager import SessionManager
from src.daip_live.model_provider.provider import LiteLLMProvider
from src.daip_live.p4_role_manager_tools.role_manager import RoleManager


class DebateManager:
    """Orchestrates a structured, multi-agent debate."""

    def __init__(
        self,
        session_manager: SessionManager,
        role_manager: RoleManager,
        model_provider: LiteLLMProvider,
    ):
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.model_provider = model_provider

    async def run_debate(
        self,
        topic: str,
        roles_names: List[str],
        num_rounds: int
    ) -> Session:
        """Runs a full debate and returns the completed session."""
        session = self.session_manager.create_session(
            goal=topic, session_type="debate", participant_ids=roles_names
        )

        roles = [self.role_manager.get_role_by_name(name) for name in roles_names]
        if any(role is None for role in roles):
            raise ValueError("One or more specified roles could not be found.")

        # Run debate rounds
        for i in range(num_rounds):
            for role in roles:
                history_str = "\n".join([f"{turn.participant_id}: {turn.content}" for turn in session.history])
                prompt = f"Debate Topic: {topic}\n\nYour Persona: {role.persona}\n\nConversation History:\n{history_str}\n\nBased on the history and your persona, what is your next argument?"

                response = await self.model_provider.generate(prompt)
                turn = DialogueTurn(participant_id=role.name, content=response)
                session.history.append(turn)

        # Generate summary
        history_str = "\n".join([f"{turn.participant_id}: {turn.content}" for turn in session.history])
        summary_prompt = f"Please provide a neutral summary of the following debate, identifying key arguments, points of contention, and any potential consensus.\n\nDebate History:\n{history_str}"
        summary = await self.model_provider.generate(summary_prompt)
        session.summary = summary

        session.status = AgentState.COMPLETED
        self.session_manager.save_session(session)

        return session
