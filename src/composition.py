# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 11:00:00
@Author  : DAIP-LIVE Team
@File    : composition.py
@Description:
    The Composition Root for the application.
    This module is responsible for creating and wiring up all the major
    components of the application, such as services, protocols, and repositories.
    This approach to dependency injection helps to decouple the components.
"""
import asyncio
import ollama
from typing import Any, Dict

from src.config_loader import load_config # Import load_config
from src.core_services.synthesis_engine import SynthesisEngine
from src.kernel.core import Kernel # Import Kernel
from src.kernel.interaction_manager import InteractionManager
from src.kernel.tool_executor import ToolExecutor
from src.protocols.consensus_strategies import (
    ConsensusStrategyFactory,
    SimpleMajorityVoteStrategy,
)
from src.protocols.debate_protocol import DebateProtocol


def create_application_dependencies(output_queue: asyncio.Queue) -> Dict[str, Any]:
    """
    Creates and wires up all application dependencies.

    Args:
        output_queue: The queue for the debate protocol to send events to the UI.

    Returns:
        A dictionary containing the initialized components.
    """
    # Load configuration
    app_config = load_config()
    ollama_model_name = app_config.llm.ollama.generation_model

    # Instantiate the Kernel, which now manages its own internal dependencies
    kernel = Kernel(model=ollama_model_name)

    debate_protocol = DebateProtocol(
        kernel=kernel,
        event_queue=output_queue,
    )

    return {"debate_protocol": debate_protocol}
