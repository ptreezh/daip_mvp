"""
Agent Orchestrator Implementation

The Agent Orchestrator is the central coordinator that manages the execution flow,
coordinates between services, and handles the overall agent workflow.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from ..events.event_bus import EventBus
from ..events.event_types import (
    BaseEvent,
    EventType,
    SessionStartedEvent,
    SessionCompletedEvent,
    SessionFailedEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    ErrorEvent,
    MetricsEvent
)
from ..integration.service_integration import ServiceIntegrationManager
from ..services.interfaces import (
    IntentRecognitionResult,
    ExecutionResult,
    PermissionDecision,
    StateSnapshot
)
from ..services.permission_service import RiskLevel


logger = logging.getLogger(__name__)


class OrchestratorState(Enum):
    """Orchestrator state enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_FOR_PERMISSION = "waiting_for_permission"
    EXECUTING = "executing"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


class ExecutionContext:
    """Execution context for a single request/task."""

    def __init__(
        self,
        session_id: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id
        self.execution_id = str(uuid4())
        self.user_input = user_input
        self.context = context or {}
        self.start_time = datetime.now()

        # Results from each stage
        self.intent_result: Optional[IntentRecognitionResult] = None
        self.permission_decision: Optional[PermissionDecision] = None
        self.execution_result: Optional[ExecutionResult] = None
        self.state_snapshot: Optional[StateSnapshot] = None

        # Metadata
        self.metadata: Dict[str, Any] = {}
        self.callbacks: Dict[str, List[Callable]] = {}

    def add_callback(self, event_type: str, callback: Callable):
        """Add a callback for a specific event type."""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)

    async def trigger_callbacks(self, event_type: str, **kwargs):
        """Trigger callbacks for a specific event type."""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(self, **kwargs)
                    else:
                        callback(self, **kwargs)
                except Exception as e:
                    logger.error(f"Error in callback for {event_type}: {e}")


class AgentOrchestrator:
    """
    Main orchestrator that coordinates the agent execution workflow.

    The orchestrator manages:
    - Intent recognition workflow
    - Permission checking workflow
    - Execution workflow
    - State management workflow
    - Error handling and recovery
    - Performance monitoring
    """

    def __init__(
        self,
        event_bus: EventBus,
        service_manager: ServiceIntegrationManager,
        config: Optional[Dict[str, Any]] = None
    ):
        self.event_bus = event_bus
        self.service_manager = service_manager
        self.config = config or {}

        # State management
        self.state = OrchestratorState.IDLE
        self.current_execution: Optional[ExecutionContext] = None
        self.execution_history: List[ExecutionContext] = []

        # Performance metrics
        self.metrics = {
            "total_sessions": 0,
            "completed_sessions": 0,
            "failed_sessions": 0,
            "total_executions": 0,
            "avg_execution_time_ms": 0.0,
            "success_rate": 0.0,
            "error_count": 0,
            "last_activity": None
        }

        # Configuration
        self.max_concurrent_executions = self.config.get("max_concurrent_executions", 5)
        self.default_timeout_seconds = self.config.get("default_timeout_seconds", 300)
        self.enable_state_persistence = self.config.get("enable_state_persistence", True)
        self.auto_retry_failed_executions = self.config.get("auto_retry_failed_executions", True)
        self.max_retry_attempts = self.config.get("max_retry_attempts", 3)

        # Event subscriptions
        self._subscriptions = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def start(self) -> None:
        """Start the orchestrator and initialize all services."""
        self.logger.info("Starting Agent Orchestrator...")

        try:
            # Start EventBus
            await self.event_bus.start()

            # Start all services
            await self.service_manager.start_all_services()

            # Subscribe to events
            await self._setup_event_subscriptions()

            # Update state
            self.state = OrchestratorState.IDLE

            self.logger.info("Agent Orchestrator started successfully")

            # Publish system ready event
            await self._publish_metrics_event()

        except Exception as e:
            self.logger.error(f"Failed to start Agent Orchestrator: {e}")
            self.state = OrchestratorState.ERROR
            raise

    async def stop(self) -> None:
        """Stop the orchestrator and all services."""
        self.logger.info("Stopping Agent Orchestrator...")

        self.state = OrchestratorState.SHUTTING_DOWN

        try:
            # Wait for current execution to complete or timeout
            if self.current_execution:
                await self._wait_for_execution_completion(timeout=10.0)

            # Unsubscribe from events
            await self._cleanup_event_subscriptions()

            # Stop all services
            await self.service_manager.stop_all_services()

            # Stop EventBus
            await self.event_bus.stop()

            self.state = OrchestratorState.IDLE
            self.logger.info("Agent Orchestrator stopped successfully")

        except Exception as e:
            self.logger.error(f"Error during orchestrator shutdown: {e}")
            raise

    async def process_request(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionContext:
        """
        Process a user request through the complete workflow.

        Args:
            user_input: The user's input text
            session_id: Optional session ID for conversation continuity
            context: Additional context for the request

        Returns:
            ExecutionContext with results from all stages
        """
        if self.state == OrchestratorState.SHUTTING_DOWN:
            raise RuntimeError("Orchestrator is shutting down")

        if self.state == OrchestratorState.ERROR:
            raise RuntimeError("Orchestrator is in error state")

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid4())

        # Create execution context
        execution_context = ExecutionContext(session_id, user_input, context)
        self.current_execution = execution_context

        try:
            self.state = OrchestratorState.PROCESSING
            start_time = time.time()

            # Publish session started event
            await self._publish_session_started_event(execution_context)

            # Execute the workflow
            await self._execute_workflow(execution_context)

            # Update metrics
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_metrics(execution_context, execution_time_ms)

            # Publish session completed event
            await self._publish_session_completed_event(execution_context)

            # Add to history
            self.execution_history.append(execution_context)

            return execution_context

        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            self.metrics["error_count"] += 1

            # Publish session failed event
            await self._publish_session_failed_event(execution_context, e)

            # Add to history even if failed
            self.execution_history.append(execution_context)

            raise

        finally:
            self.current_execution = None
            self.state = OrchestratorState.IDLE

    async def _execute_workflow(self, context: ExecutionContext) -> None:
        """Execute the complete workflow for the given context."""
        try:
            # Stage 1: Intent Recognition
            await self._stage_intent_recognition(context)
            await context.trigger_callbacks("intent_recognized")

            # Stage 2: Permission Checking
            await self._stage_permission_checking(context)
            await context.trigger_callbacks("permission_checked")

            # Stage 3: Execution (if permission granted)
            if context.permission_decision and context.permission_decision.allowed:
                await self._stage_execution(context)
                await context.trigger_callbacks("execution_completed")
            else:
                self.logger.warning(f"Execution denied for session {context.session_id}: {context.permission_decision.reason if context.permission_decision else 'No permission decision'}")

            # Stage 4: State Management (if enabled)
            if self.enable_state_persistence:
                await self._stage_state_management(context)
                await context.trigger_callbacks("state_updated")

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise

    async def _stage_intent_recognition(self, context: ExecutionContext) -> None:
        """Stage 1: Intent Recognition."""
        self.logger.debug(f"Starting intent recognition for session {context.session_id}")

        intent_service = self.service_manager.get_service("intent_recognition")
        if not intent_service:
            raise RuntimeError("Intent recognition service not available")

        # Create enhanced context for intent recognition
        enhanced_context = {
            **context.context,
            "session_id": context.session_id,
            "execution_id": context.execution_id,
            "history": self._get_recent_context(context.session_id)
        }

        # Recognize intent
        context.intent_result = await intent_service.recognize_intent(
            context.user_input,
            enhanced_context
        )

        self.logger.debug(f"Intent recognized: {context.intent_result.intent} (confidence: {context.intent_result.confidence})")

    async def _stage_permission_checking(self, context: ExecutionContext) -> None:
        """Stage 2: Permission Checking."""
        if not context.intent_result:
            raise RuntimeError("No intent result available for permission checking")

        self.logger.debug(f"Starting permission checking for session {context.session_id}")

        permission_service = self.service_manager.get_service("permission")
        if not permission_service:
            raise RuntimeError("Permission service not available")

        # Create permission context
        permission_context = {
            **context.context,
            "session_id": context.session_id,
            "execution_id": context.execution_id,
            "intent": context.intent_result.intent,
            "confidence": context.intent_result.confidence,
            "parameters": context.intent_result.parameters
        }

        # Create permission request
        from ..services.permission_service import PermissionRequest
        permission_request = PermissionRequest(
            tool_name=context.intent_result.intent,
            tool_args=context.intent_result.parameters or {},
            permission_type="execute",
            risk_level=self._assess_intent_risk(context.intent_result.intent),
            context=permission_context
        )

        # Check permission for the intent
        context.permission_decision = await permission_service.check_permission(permission_request)

        self.logger.debug(f"Permission decision: {context.permission_decision.allowed} (risk: {context.permission_decision.risk_level})")

    def _assess_intent_risk(self, intent: str) -> str:
        """Assess risk level for an intent."""
        # Simple risk assessment based on intent patterns
        high_risk_patterns = ["delete", "remove", "format", "shutdown", "reboot", "system"]
        medium_risk_patterns = ["write", "modify", "execute", "run", "install"]
        low_risk_patterns = ["read", "list", "search", "analyze", "view", "get", "show"]

        intent_lower = intent.lower()

        if any(pattern in intent_lower for pattern in high_risk_patterns):
            return "high"
        elif any(pattern in intent_lower for pattern in medium_risk_patterns):
            return "medium"
        else:
            return "low"

    async def _stage_execution(self, context: ExecutionContext) -> None:
        """Stage 3: Execution."""
        if not context.intent_result or not context.permission_decision:
            raise RuntimeError("Missing intent result or permission decision for execution")

        self.logger.debug(f"Starting execution for session {context.session_id}")

        execution_service = self.service_manager.get_service("execution_engine")
        if not execution_service:
            raise RuntimeError("Execution engine service not available")

        self.state = OrchestratorState.EXECUTING

        # Create execution context
        execution_context = {
            **context.context,
            "session_id": context.session_id,
            "execution_id": context.execution_id,
            "intent": context.intent_result.intent,
            "confidence": context.intent_result.confidence,
            "permission_decision": context.permission_decision.__dict__
        }

        # Create task for execution
        task = {
            "intent": context.intent_result.intent,
            "parameters": context.intent_result.parameters or {}
        }

        # Execute the task
        context.execution_result = await execution_service.execute(
            task,
            execution_context
        )

        self.logger.debug(f"Execution completed: {context.execution_result.success}")

    async def _stage_state_management(self, context: ExecutionContext) -> None:
        """Stage 4: State Management."""
        self.logger.debug(f"Starting state management for session {context.session_id}")

        state_service = self.service_manager.get_service("state_management")
        if not state_service:
            self.logger.warning("State management service not available, skipping")
            return

        # Create state data
        state_data = {
            "user_input": context.user_input,
            "intent": context.intent_result.__dict__ if context.intent_result else None,
            "permission_decision": context.permission_decision.__dict__ if context.permission_decision else None,
            "execution_result": context.execution_result.__dict__ if context.execution_result else None,
            "timestamp": datetime.now().isoformat(),
            "execution_time_ms": context.metadata.get("execution_time_ms", 0)
        }

        # Create state snapshot
        try:
            context.state_snapshot = await state_service.create_snapshot(
                session_id=context.session_id,
                agent_id="orchestrator",
                state_data=state_data,
                metadata={
                    "execution_id": context.execution_id,
                    "workflow_stage": "completed"
                }
            )

            self.logger.debug(f"State snapshot created: {context.state_snapshot.snapshot_id}")

        except Exception as e:
            self.logger.warning(f"Failed to create state snapshot: {e}")

    async def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions for monitoring and coordination."""
        # Subscribe to error events
        async def handle_error_event(event: BaseEvent):
            self.logger.error(f"System error: {event}")
            self.metrics["error_count"] += 1

        subscription = await self.event_bus.subscribe(EventType.ERROR, handle_error_event)
        self._subscriptions.append(subscription)

    async def _cleanup_event_subscriptions(self) -> None:
        """Cleanup event subscriptions."""
        for subscription in self._subscriptions:
            try:
                await self.event_bus.unsubscribe(subscription)
            except Exception as e:
                self.logger.error(f"Error unsubscribing from event: {e}")

        self._subscriptions.clear()

    async def _wait_for_execution_completion(self, timeout: float) -> None:
        """Wait for current execution to complete."""
        if not self.current_execution:
            return

        start_time = time.time()
        while self.current_execution and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)

        if self.current_execution:
            self.logger.warning(f"Execution {self.current_execution.execution_id} did not complete within timeout")

    def _get_recent_context(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent context for a session."""
        recent_contexts = []

        for execution in reversed(self.execution_history):
            if execution.session_id == session_id and len(recent_contexts) < limit:
                if execution.intent_result:
                    recent_contexts.append({
                        "user_input": execution.user_input,
                        "intent": execution.intent_result.intent,
                        "parameters": execution.intent_result.parameters,
                        "timestamp": execution.start_time.isoformat()
                    })

        return recent_contexts

    def _update_metrics(self, context: ExecutionContext, execution_time_ms: float) -> None:
        """Update orchestrator metrics."""
        self.metrics["total_sessions"] += 1
        self.metrics["total_executions"] += 1
        self.metrics["last_activity"] = datetime.now().isoformat()

        # Update success/failure counts
        if context.execution_result and context.execution_result.success:
            self.metrics["completed_sessions"] += 1
        else:
            self.metrics["failed_sessions"] += 1

        # Update average execution time
        total_time = self.metrics["avg_execution_time_ms"] * (self.metrics["total_executions"] - 1)
        self.metrics["avg_execution_time_ms"] = (total_time + execution_time_ms) / self.metrics["total_executions"]

        # Update success rate
        self.metrics["success_rate"] = self.metrics["completed_sessions"] / self.metrics["total_sessions"]

    async def _publish_session_started_event(self, context: ExecutionContext) -> None:
        """Publish session started event."""
        event = SessionStartedEvent(
            session_id=context.session_id,
            goal=context.user_input,
            session_type="agent_orchestration",
            participant_ids=["orchestrator"],
            task_id=context.execution_id,
            correlation_id=UUID(context.execution_id)
        )

        await self.event_bus.publish(event)

    async def _publish_session_completed_event(self, context: ExecutionContext) -> None:
        """Publish session completed event."""
        execution_time = (datetime.now() - context.start_time).total_seconds()

        event = SessionCompletedEvent(
            session_id=context.session_id,
            task_id=context.execution_id,
            final_response=context.execution_result.output if context.execution_result and hasattr(context.execution_result, 'output') else None,
            total_tasks=1,
            completed_tasks=1 if context.execution_result and context.execution_result.success else 0,
            duration_seconds=execution_time,
            correlation_id=UUID(context.execution_id)
        )

        await self.event_bus.publish(event)

    async def _publish_session_failed_event(self, context: ExecutionContext, error: Exception) -> None:
        """Publish session failed event."""
        event = SessionFailedEvent(
            session_id=context.session_id,
            task_id=context.execution_id,
            error_message=str(error),
            error_type=type(error).__name__,
            completed_tasks=0,
            correlation_id=UUID(context.execution_id)
        )

        await self.event_bus.publish(event)

    async def _publish_metrics_event(self) -> None:
        """Publish metrics event."""
        event = MetricsEvent(
            service_name="AgentOrchestrator",
            metrics=self.metrics.copy(),
            context={"state": self.state.value}
        )

        await self.event_bus.publish(event)

    # Public API methods

    def get_state(self) -> OrchestratorState:
        """Get current orchestrator state."""
        return self.state

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics."""
        # Include service metrics
        service_metrics = asyncio.create_task(self.service_manager.get_all_metrics())

        combined_metrics = {
            "orchestrator": self.metrics.copy(),
            "state": self.state.value,
            "current_execution": self.current_execution.execution_id if self.current_execution else None,
            "execution_history_count": len(self.execution_history)
        }

        try:
            # Add service metrics if available
            combined_metrics["services"] = service_metrics.result()
        except Exception:
            combined_metrics["services"] = {"error": "Failed to get service metrics"}

        return combined_metrics

    def get_execution_history(self, session_id: Optional[str] = None, limit: int = 50) -> List[ExecutionContext]:
        """Get execution history, optionally filtered by session ID."""
        history = self.execution_history

        if session_id:
            history = [ctx for ctx in history if ctx.session_id == session_id]

        return history[-limit:] if limit > 0 else history

    def is_healthy(self) -> bool:
        """Check if the orchestrator is healthy."""
        return (
            self.state not in [OrchestratorState.ERROR, OrchestratorState.SHUTTING_DOWN] and
            self.service_manager.get_service("intent_recognition") and
            self.service_manager.get_service("execution_engine") and
            self.service_manager.get_service("permission") and
            self.service_manager.get_service("state_management")
        )

    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state for a session."""
        state_service = self.service_manager.get_service("state_management")
        if not state_service:
            return None

        try:
            latest_snapshot = await state_service.get_latest_snapshot(session_id)
            if latest_snapshot:
                return latest_snapshot.state_data
        except Exception as e:
            self.logger.error(f"Error getting session state: {e}")

        return None

    async def retry_execution(self, execution_id: str) -> Optional[ExecutionContext]:
        """Retry a failed execution."""
        # Find the execution in history
        original_execution = None
        for ctx in self.execution_history:
            if ctx.execution_id == execution_id:
                original_execution = ctx
                break

        if not original_execution:
            raise ValueError(f"Execution {execution_id} not found")

        if not (original_execution.execution_result and not original_execution.execution_result.success):
            raise ValueError(f"Execution {execution_id} was not failed")

        # Check retry limit
        retry_count = original_execution.metadata.get("retry_count", 0)
        if retry_count >= self.max_retry_attempts:
            raise ValueError(f"Maximum retry attempts ({self.max_retry_attempts}) exceeded for execution {execution_id}")

        # Retry the execution
        retry_context = ExecutionContext(
            original_execution.session_id,
            original_execution.user_input,
            original_execution.context
        )
        retry_context.metadata = original_execution.metadata.copy()
        retry_context.metadata["retry_count"] = retry_count + 1
        retry_context.metadata["original_execution_id"] = execution_id

        return await self.process_request(
            original_execution.user_input,
            original_execution.session_id,
            original_execution.context
        )