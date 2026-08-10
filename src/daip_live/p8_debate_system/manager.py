from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from daip_live.core.models import (
    AgentEvent,
    AgentState,
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
    DebateTurnStartEvent,
    DialogueTurn,
    ThoughtEvent,
    TokenUsageEvent,
)
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager

if TYPE_CHECKING:  # 仅类型注解，避免模块级连带加载 litellm（CLI 冷启动优化 2026-08-10）
    from daip_live.model_provider.provider import LiteLLMProvider


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
        self, topic: str, roles_names: list[str], num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """Runs a full debate and yields events for real-time status updates."""
        session = self.session_manager.create_session(
            goal=topic, session_type="debate", participant_ids=roles_names
        )

        roles = [self.role_manager.get_role_by_name(name) for name in roles_names]
        if any(role is None for role in roles):
            raise ValueError("One or more specified roles could not be found.")

        # Emit debate start event
        yield DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=session.session_id,
        )

        # Run debate rounds
        for round_num in range(1, num_rounds + 1):
            # Emit round start event
            yield DebateRoundStartEvent(
                round_number=round_num,
                total_rounds=num_rounds,
                session_id=session.session_id,
            )

            for role in roles:
                # Emit turn start event
                yield DebateTurnStartEvent(
                    participant=role.name,
                    round_number=round_num,
                    session_id=session.session_id,
                )

                yield ThoughtEvent(
                    content=f"{role.name} is preparing their response..."
                )

                # Generate response
                response_content, token_info = await self._generate_response(
                    topic, role.persona, session.history
                )
                turn = DialogueTurn(participant_id=role.name, content=response_content)
                session.history.append(turn)

                # Emit token usage event if token info is available
                if token_info:
                    usage_info = {
                        "prompt_tokens": token_info.get("prompt_tokens", 0),
                        "completion_tokens": token_info.get("completion_tokens", 0),
                        "total_tokens": token_info.get("total_tokens", 0),
                        "session_id": session.session_id,
                    }
                    yield TokenUsageEvent(usage_info=usage_info)

                # Emit turn complete event
                yield DebateTurnCompleteEvent(
                    participant=role.name,
                    round_number=round_num,
                    content_preview=response_content,  # Show complete response
                    session_id=session.session_id,
                )

        # Generate summary
        yield ThoughtEvent(content="Generating debate summary...")
        summary_content, token_info = await self._generate_summary(session.history)
        session.summary = summary_content

        # Emit token usage event for summary generation
        if token_info:
            usage_info = {
                "prompt_tokens": token_info.get("prompt_tokens", 0),
                "completion_tokens": token_info.get("completion_tokens", 0),
                "total_tokens": token_info.get("total_tokens", 0),
                "session_id": session.session_id,
            }
            yield TokenUsageEvent(usage_info=usage_info)

        session.status = AgentState.COMPLETED
        self.session_manager.save_session(session)

        # Emit debate complete event
        yield DebateCompleteEvent(
            session_id=session.session_id, summary=summary_content
        )

    def _format_history(self, history: list[DialogueTurn]) -> str:
        """Format debate history for prompt generation."""
        return "\n".join([f"{turn.participant_id}: {turn.content}" for turn in history])

    async def _generate_response(
        self, topic: str, persona: str, history: list[DialogueTurn]
    ) -> tuple[str, dict | None]:
        """Generate a response from a role given the topic and history."""
        history_str = self._format_history(history)
        prompt = f"Debate Topic: {topic}\n\nYour Persona: {persona}\n\nConversation History:\n{history_str}\n\nBased on the history and your persona, what is your next argument?"  # noqa: E501
        response_content, token_info = await self.model_provider.generate(prompt)
        return response_content, token_info

    async def _generate_summary(
        self, history: list[DialogueTurn]
    ) -> tuple[str, dict | None]:
        """Generate a summary of the debate."""
        history_str = self._format_history(history)
        summary_prompt = f"Please provide a neutral summary of the following debate, identifying key arguments, points of contention, and any potential consensus.\n\nDebate History:\n{history_str}"  # noqa: E501
        summary_content, token_info = await self.model_provider.generate(summary_prompt)
        return summary_content, token_info
