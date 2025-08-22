from typing import Any, Dict, List, Optional
import asyncio
import logging
import json
from pathlib import Path

from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.core_services.intent_analysis_service import BasicIntentAnalysisService
from src.institutional_primitives.workflow_engine import WorkflowEngine, WorkflowDefinition
from src.core_services.task_manager import TaskManager # Assuming TaskManager exists
from src.domain.domain_services import UserInterventionService # Import UserInterventionService

logger = logging.getLogger(__name__)

class PersonalAssistantRouter:
    """
    Personal Assistant Router: CLI entry point responsible for initial user intent classification
    and mode dispatch (idle chat vs. complex task).
    """
    def __init__(
        self,
        intent_analysis_service: BasicIntentAnalysisService,
        llm_manager: IntegratedLLMManager,
        workflow_engine: WorkflowEngine,
        task_manager: TaskManager,
        session_file: str = "data/pa_sessions.json" # Add session_file parameter here
        # Add other necessary core services here via dependency injection
    ):
        self.user_intervention_service = UserInterventionService() # Initialize UserInterventionService
        self.intent_analysis_service = intent_analysis_service
        self.llm_manager = llm_manager
        self.workflow_engine = workflow_engine
        self.task_manager = task_manager
        self.conversation_history: List[Dict[str, Any]] = [] # For idle chat mode
        self.session_file = Path(session_file) # Initialize session_file path
        self.sessions: Dict[str, Dict[str, Any]] = {} # To store conversation sessions
        self._load_sessions() # Load sessions on initialization

    def _load_sessions(self):
        """Loads conversation sessions from the session file."""
        if self.session_file.exists():
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} conversation sessions from {self.session_file}")
            except Exception as e:
                logger.error(f"Error loading sessions from {self.session_file}: {e}")
                self.sessions = {} # Reset sessions on error

    def _save_sessions(self):
        """Saves conversation sessions to the session file."""
        try:
            self.session_file.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.sessions)} conversation sessions to {self.session_file}")
        except Exception as e:
            logger.error(f"Error saving sessions to {self.session_file}: {e}")

    async def process_query(self, query: str, user_id: str = "cli_user") -> Dict[str, Any]: # Add user_id parameter
        """
        Processes a user query, classifies intent, and dispatches to appropriate mode.
        """
        logger.info(f"Processing query: {query} for user: {user_id}")

        # Add current user query to conversation history before intent analysis
        current_user_message = {"role": "user", "content": query}
        self.conversation_history.append(current_user_message)

        # Step 1: Intent Analysis
        intent_result = await self.intent_analysis_service.analyze_intent(
            user_input=query,
            user_id=user_id,
            conversation_context=self.conversation_history[:-1] # Pass history *excluding* current query for intent analysis
        )
        intent_type = intent_result.detected_intent
        complexity_score = intent_result.complexity_score

        if intent_type == "idle_chat" or complexity_score < 0.6: # Simplified logic for idle chat
            logger.info("Entering idle chat mode.")
            response = await self._handle_idle_chat(query)
            # _handle_idle_chat already adds assistant response
            return {"type": "idle_chat_response", "response": response}
        else:
            logger.info("Entering complex task mode.")
            response = await self._handle_complex_task(query, intent_result)
            # Add assistant response for complex task
            self.conversation_history.append({"role": "assistant", "content": response.get("message", "Task processed.")})
            return {"type": "complex_task_response", "response": response}

    async def _handle_idle_chat(self, query: str) -> str:
        """Handles queries in idle chat mode."""
        # Simple LLM interaction for idle chat
        # Use a specific role/prompt for idle chat as per requirements
        # For now, a basic direct LLM call
        llm_response = await self.llm_manager.call_llm_for_role(
            role_id="idle_chatter", # Assuming an 'idle_chatter' role exists
            user_input=query,
            task_context=None,
            additional_context={"conversation_history": self.conversation_history[-5:]} # Pass recent history
        )
        self.conversation_history.append({"role": "assistant", "content": llm_response.get("response", "...")})
        return llm_response.get("response", "I'm not sure how to respond to that.")

    async def _handle_complex_task(self, query: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handles complex tasks by generating and executing workflows."""
        # Step 1: Intent Refinement (using a "Secretary" LLM role)
        # This part needs a specific LLM call for refinement
        refined_instruction = await self.llm_manager.call_llm_for_role(
            role_id="secretary", # Assuming a 'secretary' role exists
            user_input=query,
            task_context=None,
            additional_context={"intent_analysis": intent_result}
        )
        logger.info(f"Refined instruction: {refined_instruction.get('response', query)}")

        # Step 2: Task Decomposition (using a "Planner" LLM role)
        # The Planner LLM generates a JSON workflow definition
        workflow_definition_raw = await self.llm_manager.call_llm_for_role(
            role_id="planner", # Assuming a 'planner' role exists
            user_input=refined_instruction.get('response', query),
            task_context=None,
            additional_context={"available_apis": "GLOBAL_API_DICTIONARY_SCHEMA_HERE"} # Provide API schema
        )
        
        try:
            workflow_definition = json.loads(workflow_definition_raw.get('response', '{}'))
        except json.JSONDecodeError:
            logger.error("Planner LLM did not return valid JSON workflow definition.")
            return {"status": "failed", "message": "Failed to generate a valid task plan."}

        # Step 3: Create and Persist Task
        task_metadata = {
            "title": f"CLI Task: {query[:50]}...", # Use part of query as title
            "user_id": "cli_user", # Placeholder user ID for CLI
            "workflow_definition": workflow_definition,
            "initial_query": query,
            "status": "to_do" # Initial status
        }
        task_description = f"User query: {query}\nWorkflow: {json.dumps(workflow_definition, indent=2)}"

        # TaskManager.create_task returns a Task object, which has a task_id attribute
        created_task = self.task_manager.create_task(
            metadata=task_metadata,
            description=task_description
        )
        task_id = created_task.task_id
        logger.info(f"Complex task created with ID: {task_id}")

        # Store task_id in the current session for intervention purposes
        # Assuming a session is active and we can associate the task with it.
        # This needs a proper session management mechanism if not already present.
        # For now, we'll assume a simple way to link the last created task to a 'current' session.
        # A more robust solution would involve passing session_id to _handle_complex_task
        # and storing task_id within that specific session's data.
        # For demonstration, let's assume a global 'current_task_id' or similar for the CLI user.
        # In a multi-user system, this would be tied to the user's active session.
        # For now, let's add it to the conversation history or a simple in-memory store.
        # This is a placeholder for proper session-task linking.
        self.sessions["cli_user_session"] = self.sessions.get("cli_user_session", {})
        self.sessions["cli_user_session"]["current_task_id"] = task_id
        self._save_sessions() # Save sessions after updating

        # Step 4: Execute Workflow
        # This should ideally be non-blocking for the CLI, or provide status updates
        # For now, we'll run it and return the final status
        try:
            await self.workflow_engine.execute_workflow(WorkflowDefinition(**workflow_definition), params={"task_id": task_id})
            # After execution, update task status to completed
            self.task_manager.update_task_status(task_id, "done") # Update status in TaskManager
            final_task = self.task_manager.get_task(task_id) # Get the updated task object
            final_task_status = final_task.status if final_task else "unknown"
            return {"status": "completed", "task_id": task_id, "final_status": final_task_status}
        except Exception as e:
            logger.error(f"Workflow execution failed for task {task_id}: {e}")
            self.task_manager.update_task_status(task_id, "failed", {"error": str(e)}) # Update status in TaskManager
            return {"status": "failed", "task_id": task_id, "message": f"Task execution failed: {e}"}

    # Methods for other CLI commands would interact with TaskManager directly
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        task = self.task_manager.get_task(task_id)
        if task:
            return {"task_id": task.task_id, "status": task.status, "title": task.title}
        else:
            raise ValueError(f"Task {task_id} not found.")

    async def get_logs(self, limit: int = 10) -> List[str]:
        # This would read from secretary_log.jsonl
        # For now, a placeholder
        return [f"Log entry {i}" for i in range(limit)]

    def get_session_list(self) -> List[Dict[str, Any]]:
        """Returns a list of all conversation sessions."""
        # For now, return the raw sessions dictionary values.
        # In a real scenario, you might want to filter, sort, or format these.
        return list(self.sessions.values())

    def save_session(self, session_id: str):
        """保存会话"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        # In a real application, this would involve writing the session_aggregate
        # to a persistent storage (database, file system, etc.)
        # For now, we just ensure the session exists.
        pass # The actual saving logic would go here

    def load_session(self, session_data: Dict[str, Any]):
        """加载会话"""
        # In a real application, this would involve loading session data from
        # persistent storage and reconstructing the SessionAggregate.
        # For now, we simulate loading by creating a mock SessionAggregate
        # and adding it to self.sessions.
        try:
            # Assuming SessionAggregate has a from_dict method
            session_aggregate = SessionAggregate.from_dict(session_data)
            self.sessions[session_aggregate.session_id] = session_aggregate
        except Exception as e:
            raise ValueError(f"Invalid session data: {e}")

    def cleanup_expired_sessions(self, timeout_hours: int = 24):
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity_str = session_data.get("last_activity")
            if last_activity_str:
                last_activity = datetime.fromisoformat(last_activity_str)
                if (datetime.now() - last_activity) > timedelta(hours=timeout_hours):
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions.")
            self._save_sessions() # Save changes after cleanup
        
        return len(expired_sessions)

    async def get_consensus_info(self) -> Dict[str, Any]:
        """Placeholder for getting consensus information."""
        # In a real scenario, this would interact with ConsensusTrackingService
        # and potentially the debate system to retrieve actual consensus data.
        logger.info("Retrieving consensus information (placeholder).")
        return {
            "type": "consensus_info",
            "topic": "Sample Debate Topic",
            "consensus_level": 0.75, # 75% consensus
            "consensus_description": "Participants largely agree on the need for action, but differ on implementation details.",
            "key_arguments": [
                {"argument": "Argument A: Pro-active measures are essential.", "support": 0.8},
                {"argument": "Argument B: Economic impact must be minimized.", "support": 0.6},
                {"argument": "Argument C: Technological solutions are key.", "support": 0.7}
            ]
        }

    async def get_disagreement_points(self) -> Dict[str, Any]:
        """Placeholder for getting disagreement points."""
        logger.info("Retrieving disagreement points (placeholder).")
        return {
            "type": "disagreement_points",
            "topic": "Sample Debate Topic",
            "key_arguments": [
                {"argument": "Disagreement 1: The timeline for implementation is too aggressive.", "opposing_views": ["View 1.1", "View 1.2"]},
                {"argument": "Disagreement 2: Funding mechanisms are unclear.", "opposing_views": ["View 2.1", "View 2.2"]}
            ]
        }

    def get_session_list(self) -> List[Dict[str, Any]]:
        """Returns a list of all conversation sessions."""
        # For now, return the raw sessions dictionary values.
        # In a real scenario, you might want to filter, sort, or format these.
        return list(self.sessions.values())

    def save_session(self, session_id: str):
        """保存会话"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        # In a real application, this would involve writing the session_aggregate
        # to a persistent storage (database, file system, etc.)
        # For now, we just ensure the session exists.
        pass # The actual saving logic would go here

    def load_session(self, session_data: Dict[str, Any]):
        """加载会话"""
        # In a real application, this would involve loading session data from
        # persistent storage and reconstructing the SessionAggregate.
        # For now, we simulate loading by creating a mock SessionAggregate
        # and adding it to self.sessions.
        try:
            # Assuming SessionAggregate has a from_dict method
            session_aggregate = SessionAggregate.from_dict(session_data)
            self.sessions[session_aggregate.session_id] = session_aggregate
        except Exception as e:
            raise ValueError(f"Invalid session data: {e}")

    def cleanup_expired_sessions(self, timeout_hours: int = 24):
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity_str = session_data.get("last_activity")
            if last_activity_str:
                last_activity = datetime.fromisoformat(last_activity_str)
                if (datetime.now() - last_activity) > timedelta(hours=timeout_hours):
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions.")
            self._save_sessions() # Save changes after cleanup
        
        return len(expired_sessions)

    async def handle_intervention(self, content: str, intent: str) -> Dict[str, Any]:
        """Handles user interventions."""
        logger.info(f"Handling intervention: {content} with intent: {intent}")

        # Retrieve the current task ID from the session
        current_task_id = self.sessions.get("cli_user_session", {}).get("current_task_id")

        intervention_data = {
            "content": content,
            "intent": intent,
            "task_id": current_task_id # Pass the current task ID to the intervention service
        }

        # Call the UserInterventionService to process the intervention
        response = await self.user_intervention_service.process_intervention(
            session_id="cli_user_session", # Assuming a fixed session ID for CLI for now
            intervention_data=intervention_data
        )

        # Log and return the response from the intervention service
        logger.info(f"Intervention service response: {response}")
        self.conversation_history.append({"role": "user", "content": f"Intervention: {content} (Intent: {intent})"})
        self.conversation_history.append({"role": "assistant", "content": response.get("message", "Intervention processed.")})
        return response

        # Log and return the response from the intervention service
        logger.info(f"Intervention service response: {response}")
        self.conversation_history.append({"role": "user", "content": f"Intervention: {content} (Intent: {intent})"})
        self.conversation_history.append({"role": "assistant", "content": response.get("message", "Intervention processed.")})
        return response
