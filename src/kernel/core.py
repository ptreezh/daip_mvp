"""@Time    : 2024-07-16 11:00:00
@Author  : DAIP-LIVE Team
@File    : core.py
@Description:
    Provides a unified entry point for the entire kernel layer.
    The Kernel class encapsulates the instantiation and lifecycle management
    of all core kernel components.
"""

import logging

from src.core_services.synthesis_engine import SynthesisEngine

from .llm_interface import LLMInterface
from .tool_executor import ToolExecutor
from .tool_registry import tool_executor_instance


class Kernel:
    """A unified entry point to the kernel layer.

    This class manages the lifecycle of the LLM interface and the scheduler,
    providing a single, clean interface for the application layer to interact
    with the kernel.
    """

    def __init__(self, llm_interface: LLMInterface):
        """Initializes the complete kernel.

        Args:
            llm_interface: An instance of a class that adheres to the LLMInterface.

        """
        # Store the LLM interface
        self.llm_interface = llm_interface

        # Instantiate other core components
        self.synthesis_engine: SynthesisEngine = SynthesisEngine(llm_interface=self.llm_interface)
        self.tool_executor: ToolExecutor = tool_executor_instance
        logging.info("Kernel initialized successfully.")
