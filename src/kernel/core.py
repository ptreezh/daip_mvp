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
from typing import Optional

import ollama
from .interaction_manager import InteractionManager
from .tool_executor import ToolExecutor
from .tool_registry import tool_executor_instance
from src.core_services.synthesis_engine import SynthesisEngine


class Kernel:
    """
    A unified entry point to the kernel layer.

    This class manages the lifecycle of the LLM interface and the scheduler,
    providing a single, clean interface for the application layer to interact
    with the kernel.
    """

    def __init__(self, model: str = "llama3:8b-instruct-q5_K_M"):
        """
        Initializes the complete kernel.

        Args:
            model: The name of the Ollama model to be used by kernel components.
        """
        # Create a single, shared client for all LLM interactions
        client = ollama.AsyncClient()
        
        # Instantiate all core components
        self.synthesis_engine: SynthesisEngine = SynthesisEngine(client=client, model=model)
        self.tool_executor: ToolExecutor = tool_executor_instance
        self.interaction_manager: InteractionManager = InteractionManager(
            client=client, model=model
        )
        logging.info("Kernel initialized successfully.")