"""
Service Integration Module

Integrates domain services with the EventBus for event-driven communication.
This module provides the integration layer that connects services with the event system,
enabling loose coupling and real-time communication between components.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Type
from datetime import datetime

from ..events.event_bus import EventBus
from ..events.event_types import (
    BaseEvent,
    IntentRecognizedEvent,
    ExecutionStartedEvent,
    ExecutionCompletedEvent,
    PermissionCheckedEvent,
    StateChangedEvent,
    ServiceHealthChangedEvent,
    ErrorEvent,
    MetricsEvent
)
from ..services.interfaces import (
    IDomainService,
    IntentRecognitionResult,
    ExecutionResult,
    PermissionDecision,
    PermissionRequest,
    StateSnapshot
)
from ..services.intent_recognition import IntentRecognitionService
from ..services.execution_engine import ExecutionEngineService
from ..services.permission_service import PermissionService
from ..services.state_management import StateManagementService


logger = logging.getLogger(__name__)


class ServiceEventPublisher:
    """Publisher for service events to the EventBus."""

    def __init__(self, event_bus: EventBus, service_name: str):
        self.event_bus = event_bus
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")

    async def publish_intent_recognized(
        self,
        result: IntentRecognitionResult,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish intent recognition result event."""
        event = IntentRecognizedEvent(
            service_name=self.service_name,
            intent=result.intent,
            confidence=result.confidence,
            input_text=input_text,
            parameters=result.parameters,
            context=context or {},
            strategy_used=result.strategy_used,
            reasoning=result.reasoning
        )

        await self.event_bus.publish(event)
        self.logger.debug(f"Published intent recognized event: {result.intent}")

    async def publish_execution_started(
        self,
        execution_id: str,
        intent: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish execution started event."""
        event = ExecutionStartedEvent(
            service_name=self.service_name,
            execution_id=execution_id,
            intent=intent,
            parameters=parameters,
            context=context or {}
        )

        await self.event_bus.publish(event)
        self.logger.debug(f"Published execution started event: {execution_id}")

    async def publish_execution_completed(
        self,
        execution_id: str,
        intent: str,
        result: ExecutionResult,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish execution completed event."""
        event = ExecutionCompletedEvent(
            service_name=self.service_name,
            execution_id=execution_id,
            intent=intent,
            success=result.success,
            result_data=result.output,
            error_message=result.error,
            execution_time_ms=result.execution_time_ms,
            context=context or {}
        )

        await self.event_bus.publish(event)
        self.logger.debug(f"Published execution completed event: {execution_id}")

    async def publish_permission_checked(
        self,
        decision: PermissionDecision,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish permission checked event."""
        event = PermissionCheckedEvent(
            service_name=self.service_name,
            action=action,
            allowed=decision.allowed,
            confidence=decision.confidence,
            reason=decision.reason,
            risk_level=decision.risk_level,
            rules_applied=decision.rules_applied,
            context=context or {}
        )

        await self.event_bus.publish(event)
        self.logger.debug(f"Published permission checked event: {action} -> {decision.allowed}")

    async def publish_state_changed(
        self,
        session_id: str,
        agent_id: str,
        old_state: Optional[Dict[str, Any]],
        new_state: Dict[str, Any],
        change_type: str = "update",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish state changed event."""
        event = StateChangedEvent(
            service_name=self.service_name,
            session_id=session_id,
            agent_id=agent_id,
            old_state=old_state,
            new_state=new_state,
            change_type=change_type,
            context=context or {}
        )

        await self.event_bus.publish(event)
        self.logger.debug(f"Published state changed event: {session_id}/{agent_id}")

    async def publish_service_health_changed(
        self,
        healthy: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish service health changed event."""
        event = ServiceHealthChangedEvent(
            service_name=self.service_name,
            healthy=healthy,
            details=details or {}
        )

        await self.event_bus.publish(event)
        self.logger.debug(f"Published service health changed event: {healthy}")

    async def publish_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish error event."""
        event = ErrorEvent(
            service_name=self.service_name,
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {}
        )

        await self.event_bus.publish(event)
        self.logger.error(f"Published error event: {type(error).__name__}: {error}")

    async def publish_metrics(
        self,
        metrics: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish metrics event."""
        event = MetricsEvent(
            service_name=self.service_name,
            metrics=metrics,
            context=context or {}
        )

        await self.event_bus.publish(event)
        self.logger.debug(f"Published metrics event: {len(metrics)} metrics")


class ServiceEventSubscriber:
    """Subscriber for handling events in services."""

    def __init__(self, event_bus: EventBus, service_name: str):
        self.event_bus = event_bus
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        self._subscriptions: List[Callable] = []

    async def subscribe_to_intent_recognized(
        self,
        handler: Callable[[IntentRecognizedEvent], None]
    ) -> None:
        """Subscribe to intent recognized events."""
        async def wrapper(event: IntentRecognizedEvent):
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Error in intent recognized handler: {e}")

        subscription = await self.event_bus.subscribe(IntentRecognizedEvent, wrapper)
        self._subscriptions.append(subscription)

    async def subscribe_to_execution_started(
        self,
        handler: Callable[[ExecutionStartedEvent], None]
    ) -> None:
        """Subscribe to execution started events."""
        async def wrapper(event: ExecutionStartedEvent):
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Error in execution started handler: {e}")

        subscription = await self.event_bus.subscribe(ExecutionStartedEvent, wrapper)
        self._subscriptions.append(subscription)

    async def subscribe_to_execution_completed(
        self,
        handler: Callable[[ExecutionCompletedEvent], None]
    ) -> None:
        """Subscribe to execution completed events."""
        async def wrapper(event: ExecutionCompletedEvent):
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Error in execution completed handler: {e}")

        subscription = await self.event_bus.subscribe(ExecutionCompletedEvent, wrapper)
        self._subscriptions.append(subscription)

    async def subscribe_to_permission_checked(
        self,
        handler: Callable[[PermissionCheckedEvent], None]
    ) -> None:
        """Subscribe to permission checked events."""
        async def wrapper(event: PermissionCheckedEvent):
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Error in permission checked handler: {e}")

        subscription = await self.event_bus.subscribe(PermissionCheckedEvent, wrapper)
        self._subscriptions.append(subscription)

    async def subscribe_to_state_changed(
        self,
        handler: Callable[[StateChangedEvent], None]
    ) -> None:
        """Subscribe to state changed events."""
        async def wrapper(event: StateChangedEvent):
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Error in state changed handler: {e}")

        subscription = await self.event_bus.subscribe(StateChangedEvent, wrapper)
        self._subscriptions.append(subscription)

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all events."""
        for subscription in self._subscriptions:
            await self.event_bus.unsubscribe(subscription)
        self._subscriptions.clear()


class IntentRecognitionServiceIntegrated(IntentRecognitionService):
    """Intent Recognition Service with EventBus integration."""

    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(**kwargs)
        self.event_bus = event_bus
        self.publisher = ServiceEventPublisher(event_bus, "IntentRecognitionService")
        self.subscriber = ServiceEventSubscriber(event_bus, "IntentRecognitionService")

    async def recognize_intent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentRecognitionResult:
        """Recognize intent and publish event."""
        try:
            result = await super().recognize_intent(input_text, context)

            # Publish intent recognized event
            await self.publisher.publish_intent_recognized(
                result=result,
                input_text=input_text,
                context=context
            )

            # Publish metrics
            metrics = self.get_metrics()
            await self.publisher.publish_metrics(metrics, {"operation": "recognize_intent"})

            return result

        except Exception as e:
            await self.publisher.publish_error(e, {"input_text": input_text})
            raise

    async def start(self) -> None:
        """Start service and publish health event."""
        await super().start()
        await self.publisher.publish_service_health_changed(True)

    async def stop(self) -> None:
        """Stop service and publish health event."""
        await self.publisher.publish_service_health_changed(False)
        await super().stop()
        await self.subscriber.unsubscribe_all()


class ExecutionEngineServiceIntegrated(ExecutionEngineService):
    """Execution Engine Service with EventBus integration."""

    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(**kwargs)
        self.event_bus = event_bus
        self.publisher = ServiceEventPublisher(event_bus, "ExecutionEngineService")
        self.subscriber = ServiceEventSubscriber(event_bus, "ExecutionEngineService")
        self._execution_contexts: Dict[str, Dict[str, Any]] = {}

    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """Execute task and publish events."""
        execution_id = f"exec_{datetime.now().timestamp()}"

        # Extract intent and parameters from task
        intent = task.get("intent", "unknown")
        parameters = task.get("parameters", {})

        # Store execution context
        self._execution_contexts[execution_id] = {
            "intent": intent,
            "parameters": parameters,
            "context": context or {},
            "start_time": datetime.now()
        }

        try:
            # Publish execution started event
            await self.publisher.publish_execution_started(
                execution_id=execution_id,
                intent=intent,
                parameters=parameters,
                context=context
            )

            # Execute the intent using the parent method
            result = await super().execute(task, context)

            # Publish execution completed event
            await self.publisher.publish_execution_completed(
                execution_id=execution_id,
                intent=intent,
                result=result,
                context=context
            )

            # Publish metrics
            metrics = self.get_metrics()
            await self.publisher.publish_metrics(metrics, {
                "operation": "execute",
                "execution_id": execution_id
            })

            return result

        except Exception as e:
            # Publish error event
            await self.publisher.publish_error(e, {
                "execution_id": execution_id,
                "intent": intent,
                "parameters": parameters
            })

            # Create error result
            error_result = ExecutionResult(
                success=False,
                error=str(e),
                execution_time_ms=0.0,
                metadata={
                    "intent": intent,
                    "parameters": parameters
                }
            )

            await self.publisher.publish_execution_completed(
                execution_id=execution_id,
                intent=intent,
                result=error_result,
                context=context
            )

            raise

        finally:
            # Clean up execution context
            self._execution_contexts.pop(execution_id, None)

    async def start(self) -> None:
        """Start service and publish health event."""
        await super().start()
        await self.publisher.publish_service_health_changed(True)

    async def stop(self) -> None:
        """Stop service and publish health event."""
        await self.publisher.publish_service_health_changed(False)
        await super().stop()
        await self.subscriber.unsubscribe_all()


class PermissionServiceIntegrated(PermissionService):
    """Permission Service with EventBus integration."""

    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(**kwargs)
        self.event_bus = event_bus
        self.publisher = ServiceEventPublisher(event_bus, "PermissionService")
        self.subscriber = ServiceEventSubscriber(event_bus, "PermissionService")

    async def check_permission(
        self,
        request: PermissionRequest
    ) -> PermissionDecision:
        """Check permission and publish event."""
        try:
            decision = await super().check_permission(request)

            # Publish permission checked event
            await self.publisher.publish_permission_checked(
                decision=decision,
                action=request.tool_name,
                context=request.context
            )

            # Publish metrics for high-risk decisions
            if decision.risk_level in ["high", "critical"]:
                metrics = self.get_metrics()
                await self.publisher.publish_metrics(metrics, {
                    "operation": "check_permission_high_risk",
                    "action": request.tool_name,
                    "risk_level": decision.risk_level
                })

            return decision

        except Exception as e:
            await self.publisher.publish_error(e, {"action": request.tool_name})
            raise

    async def start(self) -> None:
        """Start service and publish health event."""
        await super().start()
        await self.publisher.publish_service_health_changed(True)

    async def stop(self) -> None:
        """Stop service and publish health event."""
        await self.publisher.publish_service_health_changed(False)
        await super().stop()
        await self.subscriber.unsubscribe_all()


class StateManagementServiceIntegrated(StateManagementService):
    """State Management Service with EventBus integration."""

    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(**kwargs)
        self.event_bus = event_bus
        self.publisher = ServiceEventPublisher(event_bus, "StateManagementService")
        self.subscriber = ServiceEventSubscriber(event_bus, "StateManagementService")
        self._last_known_states: Dict[str, Dict[str, Any]] = {}

    async def create_snapshot(
        self,
        session_id: str,
        agent_id: str,
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> StateSnapshot:
        """Create snapshot and publish state changed event."""
        try:
            snapshot = await super().create_snapshot(
                session_id, agent_id, state_data, metadata
            )

            # Get previous state for comparison
            state_key = f"{session_id}:{agent_id}"
            old_state = self._last_known_states.get(state_key)

            # Store new state
            self._last_known_states[state_key] = state_data

            # Publish state changed event
            await self.publisher.publish_state_changed(
                session_id=session_id,
                agent_id=agent_id,
                old_state=old_state,
                new_state=state_data,
                change_type="create",
                context={"snapshot_id": snapshot.snapshot_id}
            )

            return snapshot

        except Exception as e:
            await self.publisher.publish_error(e, {
                "session_id": session_id,
                "agent_id": agent_id
            })
            raise

    async def update_snapshot(
        self,
        session_id: str,
        snapshot_id: str,
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> StateSnapshot:
        """Update snapshot and publish state changed event."""
        try:
            # Get current snapshot for old state
            current_snapshot = await self.get_snapshot(session_id, snapshot_id)
            old_state = current_snapshot.state_data if current_snapshot else None

            # Update snapshot
            updated_snapshot = await super().update_snapshot(
                session_id, snapshot_id, state_data, metadata
            )

            # Update last known state
            state_key = f"{session_id}:{current_snapshot.agent_id if current_snapshot else 'unknown'}"
            self._last_known_states[state_key] = state_data

            # Publish state changed event
            await self.publisher.publish_state_changed(
                session_id=session_id,
                agent_id=updated_snapshot.agent_id,
                old_state=old_state,
                new_state=state_data,
                change_type="update",
                context={"snapshot_id": snapshot_id}
            )

            return updated_snapshot

        except Exception as e:
            await self.publisher.publish_error(e, {
                "session_id": session_id,
                "snapshot_id": snapshot_id
            })
            raise

    async def start(self) -> None:
        """Start service and publish health event."""
        await super().start()
        await self.publisher.publish_service_health_changed(True)

    async def stop(self) -> None:
        """Stop service and publish health event."""
        await self.publisher.publish_service_health_changed(False)
        await super().stop()
        await self.subscriber.unsubscribe_all()


class ServiceIntegrationManager:
    """Manages integration between services and EventBus."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.integrated_services: Dict[str, IDomainService] = {}

    async def create_intent_recognition_service(self, **kwargs) -> IntentRecognitionServiceIntegrated:
        """Create integrated intent recognition service."""
        service = IntentRecognitionServiceIntegrated(self.event_bus, **kwargs)
        self.integrated_services["intent_recognition"] = service
        return service

    async def create_execution_engine_service(self, **kwargs) -> ExecutionEngineServiceIntegrated:
        """Create integrated execution engine service."""
        service = ExecutionEngineServiceIntegrated(self.event_bus, **kwargs)
        self.integrated_services["execution_engine"] = service
        return service

    async def create_permission_service(self, **kwargs) -> PermissionServiceIntegrated:
        """Create integrated permission service."""
        service = PermissionServiceIntegrated(self.event_bus, **kwargs)
        self.integrated_services["permission"] = service
        return service

    async def create_state_management_service(self, **kwargs) -> StateManagementServiceIntegrated:
        """Create integrated state management service."""
        service = StateManagementServiceIntegrated(self.event_bus, **kwargs)
        self.integrated_services["state_management"] = service
        return service

    async def start_all_services(self) -> None:
        """Start all integrated services."""
        self.logger.info("Starting all integrated services...")

        for service_name, service in self.integrated_services.items():
            try:
                await service.start()
                self.logger.info(f"Started service: {service_name}")
            except Exception as e:
                self.logger.error(f"Failed to start service {service_name}: {e}")
                raise

    async def stop_all_services(self) -> None:
        """Stop all integrated services."""
        self.logger.info("Stopping all integrated services...")

        for service_name, service in self.integrated_services.items():
            try:
                await service.stop()
                self.logger.info(f"Stopped service: {service_name}")
            except Exception as e:
                self.logger.error(f"Failed to stop service {service_name}: {e}")

    def get_service(self, service_name: str) -> Optional[IDomainService]:
        """Get an integrated service by name."""
        return self.integrated_services.get(service_name)

    async def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics from all integrated services."""
        metrics = {}

        for service_name, service in self.integrated_services.items():
            try:
                if hasattr(service, 'get_metrics'):
                    service_metrics = service.get_metrics()
                    metrics[service_name] = service_metrics
            except Exception as e:
                self.logger.error(f"Failed to get metrics from {service_name}: {e}")
                metrics[service_name] = {"error": str(e)}

        return metrics