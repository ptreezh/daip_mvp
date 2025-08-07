# -*- coding: utf-8 -*-
"""
Integration Patterns for Multi-Agent Collaboration System

Provides integration patterns and utilities for connecting the multi-agent
collaboration system with existing DAIP services and external systems.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import weakref

from .multi_agent_collaboration_system import (
    MultiAgentService, CollaborationSession, AgentMessage, AgentProfile,
    CollaborationWebSocketManager, CollaborationAnalytics
)
# Import from institutional primitives with fallback
try:
    from .institutional_primitives import (
        InstitutionalPrimitiveFactory, PrimitiveContext, PrimitiveResult
    )
except ImportError:
    # Define fallback classes if institutional primitives not available
    class PrimitiveContext:
        def __init__(self, primitive_id, primitive_type, session_id, execution_id, inputs, assigned_agents):
            self.primitive_id = primitive_id
            self.primitive_type = primitive_type
            self.session_id = session_id
            self.execution_id = execution_id
            self.inputs = inputs
            self.assigned_agents = assigned_agents
            self.start_time = datetime.now()
            self.end_time = None
            self.status = "pending"
            self.results = {}
            self.error = None
            self.metadata = {}
    
    class PrimitiveResult:
        def __init__(self, success, outputs, execution_time, messages_generated=None, next_primitives=None, error=None, metadata=None):
            self.success = success
            self.outputs = outputs
            self.execution_time = execution_time
            self.messages_generated = messages_generated or []
            self.next_primitives = next_primitives or []
            self.error = error
            self.metadata = metadata or {}
    
    class InstitutionalPrimitiveFactory:
        def get_primitive(self, primitive_type):
            return None
        def list_primitives(self):
            return []

logger = logging.getLogger(__name__)

class IntegrationEventType(str, Enum):
    """Integration event types"""
    SESSION_CREATED = "session_created"
    SESSION_UPDATED = "session_updated"
    SESSION_COMPLETED = "session_completed"
    AGENT_JOINED = "agent_joined"
    AGENT_LEFT = "agent_left"
    MESSAGE_SENT = "message_sent"
    CONSENSUS_REACHED = "consensus_reached"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    ERROR_OCCURRED = "error_occurred"

@dataclass
class IntegrationEvent:
    """Event for integration between systems"""
    event_id: str
    event_type: IntegrationEventType
    source_system: str
    target_system: Union[str, List[str]]
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    priority: int = 1  # 1-5, 5 being highest

class IntegrationAdapter:
    """Base adapter for system integration"""
    
    def __init__(self, adapter_id: str, target_system: str):
        self.adapter_id = adapter_id
        self.target_system = target_system
        self.event_handlers: Dict[IntegrationEventType, List[Callable]] = {}
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to target system"""
        self.is_connected = True
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from target system"""
        self.is_connected = False
    
    async def send_event(self, event: IntegrationEvent) -> bool:
        """Send event to target system"""
        if not self.is_connected:
            logger.warning(f"Adapter {self.adapter_id} not connected")
            return False
        
        # Override in subclasses
        return True
    
    def register_event_handler(
        self, 
        event_type: IntegrationEventType, 
        handler: Callable
    ) -> None:
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def handle_event(self, event: IntegrationEvent) -> None:
        """Handle incoming event"""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type}: {e}")

class DAIPServiceAdapter(IntegrationAdapter):
    """Adapter for integrating with existing DAIP services"""
    
    def __init__(self, app_state):
        super().__init__("daip_service_adapter", "daip_core")
        self.app_state = app_state
        self.service_mappings = {
            "memory_service": "memory_service",
            "role_manager": "_role_manager",
            "synthesis_engine": "_synthesis_engine",
            "expert_service": "_expert_service",
            "task_manager": "_task_manager"
        }
    
    async def send_event(self, event: IntegrationEvent) -> bool:
        """Send event to DAIP services"""
        try:
            # Route event to appropriate DAIP service
            if event.event_type == IntegrationEventType.SESSION_CREATED:
                await self._handle_session_created(event)
            elif event.event_type == IntegrationEventType.MESSAGE_SENT:
                await self._handle_message_sent(event)
            elif event.event_type == IntegrationEventType.CONSENSUS_REACHED:
                await self._handle_consensus_reached(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending event to DAIP services: {e}")
            return False
    
    async def _handle_session_created(self, event: IntegrationEvent) -> None:
        """Handle session creation in DAIP services"""
        session_data = event.payload.get("session", {})
        
        # Store session in memory service
        if hasattr(self.app_state, 'memory_service'):
            memory_service = self.app_state.memory_service
            await memory_service.add_memory(
                role_id="system",
                content=f"Collaboration session created: {session_data.get('session_name', 'Unknown')}",
                memory_type="session_management",
                importance=0.8,
                metadata={
                    "session_id": session_data.get("session_id"),
                    "collaboration_mode": session_data.get("collaboration_mode"),
                    "participants": session_data.get("participants", [])
                }
            )
    
    async def _handle_message_sent(self, event: IntegrationEvent) -> None:
        """Handle message events in DAIP services"""
        message_data = event.payload.get("message", {})
        
        # Store message in memory service
        if hasattr(self.app_state, 'memory_service'):
            memory_service = self.app_state.memory_service
            await memory_service.add_memory(
                role_id=message_data.get("sender_id", "unknown"),
                content=str(message_data.get("content", "")),
                memory_type="collaboration_message",
                importance=0.6,
                metadata={
                    "message_id": message_data.get("message_id"),
                    "session_id": message_data.get("session_id"),
                    "message_type": message_data.get("message_type"),
                    "timestamp": message_data.get("timestamp")
                }
            )
    
    async def _handle_consensus_reached(self, event: IntegrationEvent) -> None:
        """Handle consensus events in DAIP services"""
        consensus_data = event.payload.get("consensus", {})
        
        # Store consensus result
        if hasattr(self.app_state, 'memory_service'):
            memory_service = self.app_state.memory_service
            await memory_service.add_memory(
                role_id="system",
                content=f"Consensus reached: {consensus_data.get('consensus_value', 'Unknown')}",
                memory_type="consensus_result",
                importance=0.9,
                metadata={
                    "consensus_method": consensus_data.get("consensus_method"),
                    "confidence": consensus_data.get("confidence"),
                    "participants": consensus_data.get("participants", [])
                }
            )

class WebSocketIntegrationAdapter(IntegrationAdapter):
    """Adapter for WebSocket integration"""
    
    def __init__(self, websocket_manager: CollaborationWebSocketManager):
        super().__init__("websocket_adapter", "websocket_clients")
        self.websocket_manager = websocket_manager
        self.event_subscriptions: Dict[str, List[str]] = {}  # session_id -> subscribed clients
    
    async def send_event(self, event: IntegrationEvent) -> bool:
        """Send event to WebSocket clients"""
        try:
            session_id = event.payload.get("session_id")
            if not session_id:
                return False
            
            # Convert event to WebSocket message
            message = {
                "event_type": event.event_type.value,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat(),
                "correlation_id": event.correlation_id
            }
            
            # Broadcast to session
            await self.websocket_manager.broadcast_to_session(session_id, message)
            return True
            
        except Exception as e:
            logger.error(f"Error sending event to WebSocket clients: {e}")
            return False

class EventBus:
    """Central event bus for system integration"""
    
    def __init__(self):
        self.adapters: Dict[str, IntegrationAdapter] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.event_handlers: Dict[IntegrationEventType, List[Callable]] = {}
        self.is_running = False
    
    def register_adapter(self, adapter: IntegrationAdapter) -> None:
        """Register an integration adapter"""
        self.adapters[adapter.adapter_id] = adapter
    
    def unregister_adapter(self, adapter_id: str) -> None:
        """Unregister an integration adapter"""
        if adapter_id in self.adapters:
            del self.adapters[adapter_id]
    
    async def publish_event(self, event: IntegrationEvent) -> None:
        """Publish event to all adapters"""
        await self.event_queue.put(event)
    
    def register_event_handler(
        self, 
        event_type: IntegrationEventType, 
        handler: Callable
    ) -> None:
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def start(self) -> None:
        """Start event bus processing"""
        self.is_running = True
        
        while self.is_running:
            try:
                event = await self.event_queue.get()
                await self._process_event(event)
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def stop(self) -> None:
        """Stop event bus processing"""
        self.is_running = False
    
    async def _process_event(self, event: IntegrationEvent) -> None:
        """Process a single event"""
        # Send to all adapters
        for adapter in self.adapters.values():
            try:
                await adapter.send_event(event)
            except Exception as e:
                logger.error(f"Error sending event to adapter {adapter.adapter_id}: {e}")
        
        # Call local handlers
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type}: {e}")

class ServiceRegistry:
    """Registry for managing service dependencies"""
    
    def __init__(self):
        self.services: Dict[str, Any] = {}
        self.service_factories: Dict[str, Callable] = {}
        self.weak_references: Dict[str, weakref.ref] = {}
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Register a service instance"""
        self.services[service_name] = service_instance
        self.weak_references[service_name] = weakref.ref(service_instance)
    
    def register_service_factory(self, service_name: str, factory: Callable) -> None:
        """Register a service factory"""
        self.service_factories[service_name] = factory
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get service instance"""
        if service_name in self.services:
            # Check if service is still alive
            service = self.services[service_name]
            if self.weak_references[service_name]() is not None:
                return service
            else:
                # Service was garbage collected, remove it
                del self.services[service_name]
                del self.weak_references[service_name]
        
        # Try to create from factory
        if service_name in self.service_factories:
            try:
                service = self.service_factories[service_name]()
                self.register_service(service_name, service)
                return service
            except Exception as e:
                logger.error(f"Error creating service {service_name} from factory: {e}")
        
        return None
    
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.services.keys())
    
    def unregister_service(self, service_name: str) -> None:
        """Unregister a service"""
        if service_name in self.services:
            del self.services[service_name]
        if service_name in self.weak_references:
            del self.weak_references[service_name]

class MultiAgentIntegrationManager:
    """Main integration manager for multi-agent collaboration system"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        self.service_registry = ServiceRegistry()
        self.event_bus = EventBus()
        self.websocket_manager = CollaborationWebSocketManager()
        self.analytics = CollaborationAnalytics()
        
        # Initialize adapters
        self.daip_adapter = DAIPServiceAdapter(app_state)
        self.websocket_adapter = WebSocketIntegrationAdapter(self.websocket_manager)
        
        # Register adapters
        self.event_bus.register_adapter(self.daip_adapter)
        self.event_bus.register_adapter(self.websocket_adapter)
        
        # Initialize multi-agent service
        self.multi_agent_service = MultiAgentService(app_state)
        
        # Register services
        self._register_services()
        
        # Register event handlers
        self._register_event_handlers()
    
    def _register_services(self) -> None:
        """Register core services"""
        # Register multi-agent service
        self.service_registry.register_service("multi_agent_service", self.multi_agent_service)
        
        # Register DAIP services
        if hasattr(self.app_state, 'memory_service'):
            self.service_registry.register_service("memory_service", self.app_state.memory_service)
        
        if hasattr(self.app_state, '_role_manager'):
            self.service_registry.register_service("role_manager", self.app_state._role_manager)
        
        if hasattr(self.app_state, '_synthesis_engine'):
            self.service_registry.register_service("synthesis_engine", self.app_state._synthesis_engine)
        
        # Register utility services
        self.service_registry.register_service("event_bus", self.event_bus)
        self.service_registry.register_service("websocket_manager", self.websocket_manager)
        self.service_registry.register_service("analytics", self.analytics)
    
    def _register_event_handlers(self) -> None:
        """Register event handlers"""
        self.event_bus.register_event_handler(
            IntegrationEventType.SESSION_CREATED,
            self._on_session_created
        )
        self.event_bus.register_event_handler(
            IntegrationEventType.SESSION_UPDATED,
            self._on_session_updated
        )
        self.event_bus.register_event_handler(
            IntegrationEventType.CONSENSUS_REACHED,
            self._on_consensus_reached
        )
    
    async def start(self) -> None:
        """Start the integration manager"""
        # Connect adapters
        await self.daip_adapter.connect()
        await self.websocket_adapter.connect()
        
        # Start event bus
        await self.event_bus.start()
        
        logger.info("Multi-agent integration manager started")
    
    async def stop(self) -> None:
        """Stop the integration manager"""
        # Stop event bus
        await self.event_bus.stop()
        
        # Disconnect adapters
        await self.daip_adapter.disconnect()
        await self.websocket_adapter.disconnect()
        
        logger.info("Multi-agent integration manager stopped")
    
    async def handle_user_request(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle user request through integrated system"""
        
        # Create session event
        session_id = str(uuid.uuid4())
        event = IntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type=IntegrationEventType.SESSION_CREATED,
            source_system="user_interface",
            target_system=["multi_agent_service", "websocket_manager"],
            payload={
                "user_input": user_input,
                "user_id": user_id,
                "context": context or {},
                "session_id": session_id
            },
            correlation_id=session_id
        )
        
        # Publish event
        await self.event_bus.publish_event(event)
        
        # Process request through multi-agent service
        result = await self.multi_agent_service.handle_user_request(
            user_input, user_id, context
        )
        
        # Create completion event
        completion_event = IntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type=IntegrationEventType.SESSION_COMPLETED,
            source_system="multi_agent_service",
            target_system=["websocket_manager", "analytics"],
            payload={
                "session_id": session_id,
                "result": result,
                "processing_time": result.get("processing_time", 0)
            },
            correlation_id=session_id
        )
        
        # Publish completion event
        await self.event_bus.publish_event(completion_event)
        
        return result
    
    async def _on_session_created(self, event: IntegrationEvent) -> None:
        """Handle session creation event"""
        session_data = event.payload
        
        # Record analytics
        if "session_id" in session_data:
            session = CollaborationSession(
                session_id=session_data["session_id"],
                session_name=session_data.get("session_name", "Unknown"),
                collaboration_mode=session_data.get("collaboration_mode", "general"),
                initiator_id=session_data.get("user_id", "unknown"),
                participants=session_data.get("participants", []),
                topic=session_data.get("user_input", ""),
                objectives=session_data.get("objectives", []),
                institutional_primitives=session_data.get("institutional_primitives", []),
                consensus_method=session_data.get("consensus_method", "simple_majority")
            )
            
            self.analytics.record_session_start(session)
    
    async def _on_session_updated(self, event: IntegrationEvent) -> None:
        """Handle session update event"""
        # Handle session updates (e.g., agent joining/leaving)
        pass
    
    async def _on_consensus_reached(self, event: IntegrationEvent) -> None:
        """Handle consensus reached event"""
        consensus_data = event.payload
        
        if "consensus_result" in consensus_data:
            self.analytics.record_consensus_computation(
                consensus_data.get("session_id", ""),
                consensus_data["consensus_result"]
            )

class WebSocketIntegrationHandler:
    """Handles WebSocket integration for real-time updates"""
    
    def __init__(self, integration_manager: MultiAgentIntegrationManager):
        self.integration_manager = integration_manager
        self.websocket_manager = integration_manager.websocket_manager
    
    async def handle_websocket_connection(
        self, 
        websocket: Any, 
        session_id: str, 
        user_id: str
    ) -> None:
        """Handle new WebSocket connection"""
        await self.websocket_manager.connect(websocket, session_id, user_id)
        
        # Send initial session state
        initial_state = {
            "type": "session_state",
            "session_id": session_id,
            "user_id": user_id,
            "connected_at": datetime.now().isoformat(),
            "status": "connected"
        }
        
        await websocket.send_json(initial_state)
    
    async def handle_websocket_message(
        self, 
        websocket: Any, 
        message: Dict[str, Any]
    ) -> None:
        """Handle incoming WebSocket message"""
        try:
            message_type = message.get("type")
            
            if message_type == "user_message":
                await self._handle_user_message(websocket, message)
            elif message_type == "session_command":
                await self._handle_session_command(websocket, message)
            elif message_type == "agent_request":
                await self._handle_agent_request(websocket, message)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            
            # Send error response
            error_response = {
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(error_response)
    
    async def handle_websocket_disconnection(self, websocket: Any) -> None:
        """Handle WebSocket disconnection"""
        await self.websocket_manager.disconnect(websocket)
    
    async def _handle_user_message(self, websocket: Any, message: Dict[str, Any]) -> None:
        """Handle user message from WebSocket"""
        user_input = message.get("content", "")
        user_id = message.get("user_id", "unknown")
        session_id = message.get("session_id")
        
        if not user_input or not session_id:
            return
        
        # Process through integration manager
        result = await self.integration_manager.handle_user_request(
            user_input, user_id, {"session_id": session_id}
        )
        
        # Send response
        response = {
            "type": "message_response",
            "request_id": message.get("request_id"),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send_json(response)
    
    async def _handle_session_command(self, websocket: Any, message: Dict[str, Any]) -> None:
        """Handle session command from WebSocket"""
        command = message.get("command")
        session_id = message.get("session_id")
        
        if command == "get_session_info":
            # Get session information
            session_info = {
                "type": "session_info",
                "session_id": session_id,
                "status": "active",
                "participants": [],
                "last_activity": datetime.now().isoformat()
            }
            
            await websocket.send_json(session_info)
        
        elif command == "end_session":
            # End session
            await self._end_session(session_id)
            
            response = {
                "type": "session_ended",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_json(response)
    
    async def _handle_agent_request(self, websocket: Any, message: Dict[str, Any]) -> None:
        """Handle agent request from WebSocket"""
        request_type = message.get("request_type")
        
        if request_type == "list_agents":
            # List available agents
            agents = self.integration_manager.multi_agent_service.agent_registry.agents
            
            agent_list = {
                "type": "agent_list",
                "agents": [
                    {
                        "agent_id": agent_id,
                        "name": agent.name,
                        "agent_type": agent.agent_type.value,
                        "specializations": [s.value for s in agent.specializations],
                        "availability": agent.availability
                    }
                    for agent_id, agent in agents.items()
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_json(agent_list)
    
    async def _end_session(self, session_id: str) -> None:
        """End a collaboration session"""
        # Create session end event
        event = IntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type=IntegrationEventType.SESSION_COMPLETED,
            source_system="websocket_manager",
            target_system=["multi_agent_service", "analytics"],
            payload={
                "session_id": session_id,
                "end_reason": "user_requested"
            }
        )
        
        await self.integration_manager.event_bus.publish_event(event)

# FastAPI integration helpers
class FastAPIIntegrationHelper:
    """Helper class for integrating with FastAPI application"""
    
    def __init__(self, integration_manager: MultiAgentIntegrationManager):
        self.integration_manager = integration_manager
        self.websocket_handler = WebSocketIntegrationHandler(integration_manager)
    
    def create_websocket_endpoint(self) -> Callable:
        """Create WebSocket endpoint for FastAPI"""
        async def websocket_endpoint(websocket):
            session_id = websocket.query_params.get("session_id")
            user_id = websocket.query_params.get("user_id")
            
            if not session_id or not user_id:
                await websocket.close(code=4000, reason="Missing session_id or user_id")
                return
            
            try:
                # Handle connection
                await self.websocket_handler.handle_websocket_connection(
                    websocket, session_id, user_id
                )
                
                # Message handling loop
                while True:
                    try:
                        # Receive message
                        data = await websocket.receive_json()
                        
                        # Handle message
                        await self.websocket_handler.handle_websocket_message(
                            websocket, data
                        )
                        
                    except Exception as e:
                        logger.error(f"Error in WebSocket message handling: {e}")
                        break
                        
            except Exception as e:
                logger.error(f"Error in WebSocket connection: {e}")
            finally:
                # Handle disconnection
                await self.websocket_handler.handle_websocket_disconnection(websocket)
        
        return websocket_endpoint
    
    def create_api_endpoints(self) -> Dict[str, Callable]:
        """Create API endpoints for multi-agent collaboration"""
        endpoints = {}
        
        async def start_collaboration_session(request):
            """Start a new collaboration session"""
            try:
                data = await request.json()
                user_input = data.get("user_input")
                user_id = data.get("user_id")
                
                if not user_input or not user_id:
                    return {"error": "Missing user_input or user_id"}
                
                result = await self.integration_manager.handle_user_request(
                    user_input, user_id, data.get("context")
                )
                
                return {
                    "success": True,
                    "session_id": result["session"].session_id,
                    "result": result
                }
                
            except Exception as e:
                return {"error": str(e)}
        
        async def get_session_status(request):
            """Get session status"""
            session_id = request.query_params.get("session_id")
            
            if not session_id:
                return {"error": "Missing session_id"}
            
            # Get session summary from analytics
            summary = self.integration_manager.analytics.get_session_summary(session_id)
            
            return {
                "session_id": session_id,
                "summary": summary
            }
        
        async def list_available_agents(request):
            """List available agents"""
            agents = self.integration_manager.multi_agent_service.agent_registry.agents
            
            return {
                "agents": [
                    {
                        "agent_id": agent_id,
                        "name": agent.name,
                        "agent_type": agent.agent_type.value,
                        "specializations": [s.value for s in agent.specializations],
                        "availability": agent.availability
                    }
                    for agent_id, agent in agents.items()
                ]
            }
        
        endpoints["start_collaboration"] = start_collaboration_session
        endpoints["get_session_status"] = get_session_status
        endpoints["list_agents"] = list_available_agents
        
        return endpoints

# Example usage and integration
async def example_integration():
    """Example of how to use the integration system"""
    
    # Initialize integration manager
    from src.app_state import AppState
    app_state = AppState()
    integration_manager = MultiAgentIntegrationManager(app_state)
    
    # Start integration manager
    await integration_manager.start()
    
    # Handle user request
    result = await integration_manager.handle_user_request(
        "I need to organize a debate about AI ethics",
        "user_123",
        {"priority": "high"}
    )
    
    print(f"Integration result: {result}")
    
    # Stop integration manager
    await integration_manager.stop()
    
    return result

if __name__ == "__main__":
    print("Multi-Agent Integration System")
    print("=============================")
    print("This module provides integration patterns for connecting")
    print("the multi-agent collaboration system with existing DAIP services.")
    print("\nKey components:")
    print("- Integration adapters for different systems")
    print("- Event bus for inter-system communication")
    print("- Service registry for dependency management")
    print("- WebSocket integration for real-time updates")
    print("- FastAPI integration helpers")
    print("\nExample usage available in example_integration()")