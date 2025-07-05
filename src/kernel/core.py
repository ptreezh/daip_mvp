# -*- coding: utf-8 -*-
"""
@Time    : 2024-07-16 11:00:00
@Author  : DAIP-LIVE Team
@File    : core.py
@Description:
    Provides a unified entry point for the entire kernel layer.
    The Kernel class encapsulates the instantiation and lifecycle management
    of all core kernel components.
"""

import logging
from typing import Any, Dict, List

from .interaction_manager import InteractionManager
from .llm_interface import LLMConfig, LLMFactory, LLMInterface
from .llm_scheduler import LLMScheduler
from .tool_executor import ToolExecutor
from .tool_registry import tool_executor_instance
from src.core_services.memory_service import MemoryService
from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services.wiki_service import WikiService


class Kernel:
    """
    A unified entry point to the kernel layer.

    This class manages the lifecycle of the LLM interface and the scheduler,
    providing a single, clean interface for the application layer to interact
    with the kernel.
    """
    def __init__(self, llm_config: LLMConfig, context_token_threshold: int = 4096):
        """
        Initializes the complete kernel.

        Args:
            llm_config: The configuration for the LLM to be used.
            context_token_threshold: The token limit for the interaction manager.
        """
        # Instantiate all services required by the kernel components
        wiki_service = WikiService()
        memory_service = MemoryService()

        self.llm_interface: LLMInterface = LLMFactory.create(llm_config)

        # The SynthesisEngine needs an LLM interface to perform summarization
        synthesis_engine = SynthesisEngine(llm_interface=self.llm_interface)

        self.tool_executor: ToolExecutor = tool_executor_instance
        self.interaction_manager: InteractionManager = InteractionManager(
            wiki_service=wiki_service,
            memory_service=memory_service,
            synthesis_engine=synthesis_engine,
            context_token_threshold=context_token_threshold,
        )
        self.scheduler: LLMScheduler = LLMScheduler(
            llm_interface=self.llm_interface,
            tool_executor=self.tool_executor,
            interaction_manager=self.interaction_manager,
        )
        logging.info("Kernel initialized successfully.")

    async def start(self) -> None:
        """Starts the kernel's background services (e.g., the LLM scheduler)."""
        logging.info("Starting kernel services...")
        await self.scheduler.start()
        logging.info("Kernel services started.")

    async def stop(self) -> None:
        """Stops the kernel's background services gracefully."""
        logging.info("Stopping kernel services...")
        await self.scheduler.stop()
        logging.info("Kernel services stopped.")

    async def submit_request(self, history: List[Dict[str, Any]]) -> str:
        """
        Submits a request for processing by the kernel.

        This is the primary method for interaction. It queues the request
        and returns the final response from the LLM after any tool calls.
        """
        return await self.scheduler.submit_request(history)