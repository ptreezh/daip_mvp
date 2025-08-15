"""@Time    : 2025-07-25 11:00:00
@Author  : DAIP-LIVE Team
@File    : debate_protocol.py
@Description:
    Orchestrates a structured debate between multiple AI roles.
"""
import asyncio
import logging

from src.kernel.core import Kernel
from src.models import (
    DebateConfig,
    DebateEndEvent,
    DebateResult,
    DebateStartEvent,
    DebateTurn,
    ErrorEvent,
    NewTurnEvent,
    TechLogEvent,
    UserInterventionCommand,
)

logger = logging.getLogger(__name__)


class DebateProtocol:
    """Orchestrates a structured debate between multiple AI roles using kernel components.
    """

    def __init__(self, kernel: Kernel, event_queue: asyncio.Queue):
        """Initializes the DebateProtocol.

        Args:
            kernel: An instance of the application kernel.
            event_queue: An asyncio queue to emit events to the UI or other listeners.

        """
        self.kernel = kernel
        self.event_queue = event_queue
        self.history: list[DebateTurn] = []

    async def _emit_event(self, event):
        """Helper to put an event on the queue."""
        await self.event_queue.put(event)

    async def handle_command(self, command: UserInterventionCommand):
        """Handles commands, such as user interventions."""
        if isinstance(command, UserInterventionCommand):
            logger.info(f"Handling user intervention: {command.content}")
            turn = DebateTurn(
                role_id="User (Intervention)",
                opinion=command.content,
                round=self.history[-1].round if self.history else 1,
            )
            self.history.append(turn)
            await self._emit_event(NewTurnEvent(turn=turn))

    async def run(self, config: DebateConfig):
        """Executes the entire debate flow based on the provided configuration.
        """
        try:
            self.history = []
            await self._emit_event(DebateStartEvent(config=config))

            # Main debate loop
            for i in range(config.rounds):
                current_round = i + 1
                await self._emit_event(
                    TechLogEvent(source="DebateProtocol", message=f"Starting Round {current_round}...")
                )
                for role_id in config.roles:
                    await self._emit_event(
                        TechLogEvent(
                            source="DebateProtocol",
                            message=f"Turn for role: {role_id}",
                            function="run",
                        )
                    )

                    # 1. Summarize context for the current role
                    context = await self.kernel.synthesis_engine.summarize_context(self.history)
                    if context.startswith("Error:"):
                        raise Exception(f"Synthesis engine failed: {context}")

                    # 2. Get opinion from the current role (with token tracking)
                    messages = [
                        {"role": "system", "content": f"You are an AI assistant playing the role of '{role_id}'. Your task is to provide a concise opinion based on the debate context. Do not add any preamble or explanation of your role. Directly state your opinion."},
                        {"role": "user", "content": f"Debate Context:\n---\n{context}\n---\nYour Opinion:"}
                    ]
                    opinion_response = await self.kernel.llm_interface.generate(messages, participant_id=role_id)
                    opinion = opinion_response.get("content", "").strip()
                    if not opinion:
                        raise Exception(f"LLM failed to generate an opinion for role {role_id}")

                    # Log token usage if available
                    if "token_usage" in opinion_response:
                        token_info = opinion_response["token_usage"]
                        await self._emit_event(
                            TechLogEvent(
                                source="DebateProtocol",
                                message=f"Token usage for {role_id}: {token_info['total_tokens']} tokens",
                                function="run"
                            )
                        )

                    # 3. Record and broadcast the new turn
                    turn = DebateTurn(role_id=role_id, opinion=opinion, round=current_round)
                    self.history.append(turn)
                    await self._emit_event(NewTurnEvent(turn=turn))

            # Consensus phase
            await self._emit_event(TechLogEvent(source="DebateProtocol", message="Debate rounds complete. Moving to consensus."))

            # Execute consensus tool
            try:
                # Try to use the tool if available
                consensus_result = self.kernel.tool_executor.execute_tool(tool_name=config.consensus_strategy, history=self.history)
                if isinstance(consensus_result, dict) and consensus_result.get("status") == "success":
                    consensus_outcome = consensus_result.get("result", "No clear consensus reached. Both perspectives have merit.")
                elif isinstance(consensus_result, dict) and consensus_result.get("status") == "error":
                    # If tool execution returned an error status
                    raise Exception(f"Consensus tool failed: {consensus_result.get('message', 'Unknown error')}")
                elif consensus_result:
                    # If we get a simple string result, use it
                    consensus_outcome = str(consensus_result)
                else:
                    # If tool execution returned None or empty result
                    raise Exception("Consensus tool returned no result")
            except Exception as e:
                # If tool execution fails, create a simple consensus
                await self._emit_event(TechLogEvent(source="DebateProtocol", message=f"Consensus tool failed: {e}. Using simple consensus."))
                consensus_outcome = "No clear consensus reached. Both perspectives have merit."

            # Synthesis phase
            await self._emit_event(TechLogEvent(source="DebateProtocol", message="Consensus reached. Synthesizing final result."))
            final_synthesis = await self.kernel.synthesis_engine.synthesize_opinions(topic=config.topic, history=self.history)
            if final_synthesis.startswith("Error:"):
                raise Exception(f"Final synthesis failed: {final_synthesis}")

            # Final result
            result = DebateResult(topic=config.topic, history=self.history, consensus_outcome=consensus_outcome, synthesis=final_synthesis)
            await self._emit_event(DebateEndEvent(result=result))

        except Exception as e:
            logger.exception("A critical error occurred during the debate protocol.")
            await self._emit_event(ErrorEvent(error_message="Debate protocol failed", details=str(e)))
