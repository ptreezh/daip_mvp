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
import asyncio
import ollama
from typing import Any, Dict

from src.config_loader import load_config
from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services.role_manager import RoleManager # Import RoleManager
from src.core_services.role_recommender_service import RoleRecommenderService # Import RoleRecommenderService
from src.kernel.core import Kernel
from src.kernel.llm_interface import LLMConfig, LLMFactory
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

    # Create LLM Interface
    llm_config = LLMConfig(
        provider=app_config.llm.provider,
        model=app_config.llm.ollama.generation_model,  # Or adapt for other providers
        base_url=app_config.llm.ollama.base_url
    )
    llm_interface = LLMFactory.create(llm_config)

    # Instantiate the Kernel
    kernel = Kernel(llm_interface=llm_interface)

    # Instantiate RoleManager and RoleRecommenderService
    role_manager = RoleManager()
    role_recommender_service = RoleRecommenderService(
        role_manager=role_manager,
        llm_interface=llm_interface
    )
    # Build role index if it doesn't exist or needs rebuilding
    role_recommender_service.build_index()

    debate_protocol = DebateProtocol(
        kernel=kernel,
        event_queue=output_queue,
    )

    return {
        "debate_protocol": debate_protocol,
        "role_manager": role_manager,
        "role_recommender_service": role_recommender_service,
        "kernel": kernel # Also return kernel for potential future use
    }
