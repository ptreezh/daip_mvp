# -*- coding: utf-8 -*-
"""
@Time    : 2023-10-27 10:10:00
@Author  : DAIP-LIVE Team
@File    : debate_protocol.py
@Description:
    Orchestrates a multi-role debate from configuration to result.
    This protocol manages the debate flow, interacts with core services via
    injected dependencies, and produces a structured outcome.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

# Assume these are the interfaces for the services we depend on.
# In a real scenario, these would be imported from src.core_services and src.kernel
from src.kernel.tool_executor import ToolExecutor

from .turn_manager import TurnManager
from src.models import DebateConfig, DebateResult, DebateTurn

if TYPE_CHECKING:
    from src.core_services.synthesis_engine import SynthesisEngine
    from src.kernel.interaction_manager import InteractionManager


class DebateProtocol:
    """
    Implements the core logic for conducting a structured debate.
    """

    def __init__(
        self,
        interaction_manager: "InteractionManager",
        synthesis_engine: "SynthesisEngine",
        tool_executor: ToolExecutor,
    ):
        """
        Initializes the protocol with its dependencies.

        Args:
            interaction_manager (InteractionManager): Service to get responses from roles.
            synthesis_engine (SynthesisEngine): Service to synthesize final conclusions.
            tool_executor (ToolExecutor): Service to execute tools, like consensus strategies.
        """
        self.interaction_manager = interaction_manager
        self.synthesis_engine = synthesis_engine
        self.tool_executor = tool_executor

    async def execute(self, config: DebateConfig) -> DebateResult:
        """
        Executes the full debate lifecycle.

        This method orchestrates the debate rounds, triggers the consensus mechanism,
        invokes the synthesis engine, and returns the final result.
        """
        logging.info(f"Starting debate on topic: '{config.topic}'")
        history: List[DebateTurn] = []
        
        turn_manager = TurnManager(config)
        
        while not turn_manager.is_finished():
            current_round, role_id = turn_manager.get_current_turn()
            logging.info(f"Round {current_round}, Turn: {role_id}")
            
            # Summarize the history to create a concise context for the next turn.
            # For the very first turn, the context is the debate topic itself.
            if not history:
                context_for_llm = config.topic
            else:
                context_for_llm = await self.synthesis_engine.summarize_context(history=history)

            opinion_text = await self.interaction_manager.get_response(
                role_id=role_id, context=context_for_llm
            )
            
            turn = DebateTurn(role_id=role_id, opinion=opinion_text, round=current_round)
            history.append(turn)
            
            turn_manager.advance()

        logging.info("Debate rounds complete. Executing consensus strategy.")
        consensus_result = self.tool_executor.execute(config.consensus_strategy, history=history)
        
        if consensus_result.get("status") == "success":
            consensus_outcome = consensus_result.get("result")
        else:
            error_message = consensus_result.get("message", "Consensus execution failed")
            logging.error(f"Consensus strategy failed: {error_message}")
            consensus_outcome = {"error": error_message}

        logging.info("Synthesizing final opinions.")
        synthesis = await self.synthesis_engine.synthesize_opinions(config.topic, history)

        return DebateResult(
            topic=config.topic,
            history=history,
            consensus_outcome=consensus_outcome,
            synthesis=synthesis,
        )