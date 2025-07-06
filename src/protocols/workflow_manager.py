"""@Time    : 2025-07-03 17:40:42
@Author  : DAIP-LIVE Team
@File    : workflow_manager.py
@Description:
    The main state machine for the system, managing high-level states.
"""

import logging
from enum import Enum, auto
from typing import Any, Optional, Union

from src.core_services.memory_service import MemoryService
from src.core_services.role_manager import RoleManager
from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services.task_manager import TaskManager
from src.core_services.wiki_service import WikiService

# 假设协议类已创建
# from src.protocols.agile_protocol import AgileProtocol
# from src.protocols.debate_protocol import DebateProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SystemState(Enum):
    """Enumeration for the system's high-level states."""

    IDLE = auto()
    PROJECT_EXECUTION = auto()
    DEBATE_ANALYSIS = auto()
    DEBATE_IN_PROGRESS = auto()
    CONSENSUS_VOTE = auto()
    SYNTHESIS_GENERATION = auto()


class WorkflowManager:
    """Manages the overall workflow and state transitions of a session.
    It receives events and calls appropriate protocol modules.
    """

    def __init__(
        self,
        session_id: str,
        role_manager: RoleManager,
        task_manager: TaskManager,
        wiki_service: WikiService,
        memory_service: MemoryService,
        synthesis_engine: SynthesisEngine,
    ):
        """Initializes the WorkflowManager for a specific session.

        Args:
        ----
            session_id (str): The ID of the session this manager belongs to.
            role_manager (RoleManager): Service for managing roles.
            task_manager (TaskManager): Service for managing tasks.
            wiki_service (WikiService): Service for the versioned knowledge base.
            memory_service (MemoryService): Service for session history.
            synthesis_engine (SynthesisEngine): Service for generating summaries.
        """
        self.session_id = session_id
        self.current_state: SystemState = SystemState.IDLE

        # Core services dependency injection
        self.role_manager = role_manager
        self.task_manager = task_manager
        self.wiki_service = wiki_service
        self.memory_service = memory_service
        self.synthesis_engine = synthesis_engine

        # Active protocol instance
        self.active_protocol: Optional[Any] = None  # Union[AgileProtocol, DebateProtocol]

        logging.info(
            "WorkflowManager for session '%s' initialized in state: %s",
            self.session_id, self.current_state.name
        )

    def handle_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Handles an incoming event and triggers state transitions or protocol actions.
        (This is a placeholder for the actual implementation).

        Args:
        ----
            event_type (str): The type of the event (e.g., 'user_message', 'command').
            payload (Dict[str, Any]): The data associated with the event.
        """
        logging.info(
            "Handling event '%s' in state '%s' with payload: %s",
            event_type, self.current_state.name, payload
        )

        command = payload.get("command", "").lower()

        # --- State Transition Logic ---
        if self.current_state == SystemState.IDLE:
            if command.startswith("!debate"):
                # Placeholder for parsing topic and roles from command
                topic = "Parsed topic from command"
                roles = ["economist", "sociologist"]
                self._transition_to(SystemState.DEBATE_IN_PROGRESS, topic=topic, roles=roles)
            elif command.startswith("!decompose"):
                # Placeholder for parsing task from command
                task_description = "Parsed task from command"
                self._transition_to(SystemState.PROJECT_EXECUTION, task=task_description)
        
        # --- Delegate to Active Protocol ---
        elif self.active_protocol:
            # In a real implementation, you would await the handling
            # await self.active_protocol.handle_message(payload.get("message"))
            logging.info("Delegating event to active protocol: %s", self.active_protocol.__class__.__name__)

        else:
            logging.warning(
                "No action defined for event '%s' in state '%s'.",
                event_type, self.current_state.name
            )

    def _transition_to(self, new_state: SystemState, **kwargs) -> None:
        """Transitions the state machine to a new state.

        Args:
        ----
            new_state (SystemState): The state to transition to.
            **kwargs: Arguments needed to initialize the new state's protocol.
        """
        logging.info(
            "Transitioning state from %s to %s", self.current_state.name, new_state.name
        )
        self.current_state = new_state
        self.active_protocol = None # Reset active protocol

        # Instantiate the corresponding protocol for the new state
        # if new_state == SystemState.DEBATE_IN_PROGRESS:
        #     self.active_protocol = DebateProtocol(self.session_id, self.role_manager, ...)
        #     # await self.active_protocol.start_debate(topic=kwargs['topic'], ...)
        # elif new_state == SystemState.PROJECT_EXECUTION:
        #     self.active_protocol = AgileProtocol(self.session_id, self.task_manager, ...)
        #     # await self.active_protocol.start_decomposition(high_level_task=kwargs['task'])

    def get_status(self) -> dict[str, Any]:
        """Gets the current status of the workflow.

        Returns
        -------
            Dict[str, Any]: A dictionary representing the current status.
        """
        return {
            "session_id": self.session_id,
            "current_state": self.current_state.name,
        }
