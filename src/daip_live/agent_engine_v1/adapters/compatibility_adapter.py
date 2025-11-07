"""
Compatibility Adapter Layer

This module provides compatibility adapters that bridge the new agent_engine_v1 architecture
with the existing legacy systems, ensuring smooth migration and backward compatibility.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from ..orchestration.agent_orchestrator import AgentOrchestrator
from ..events.event_bus import EventBus
from ..integration.service_integration import ServiceIntegrationManager
from ..services.interfaces import (
    IntentRecognitionResult,
    ExecutionResult,
    PermissionDecision,
    StateSnapshot
)


logger = logging.getLogger(__name__)


@dataclass
class LegacyRequest:
    """Legacy request format from old agent engine."""
    user_input: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    tool_permissions: Optional[Dict[str, bool]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LegacyResponse:
    """Legacy response format compatible with old agent engine."""
    response: str
    success: bool
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    state_changes: Optional[Dict[str, Any]] = None


class CompatibilityAdapter(ABC):
    """Abstract base class for compatibility adapters."""

    @abstractmethod
    async def adapt_request(self, legacy_request: LegacyRequest) -> Any:
        """Adapt legacy request to new format."""
        pass

    @abstractmethod
    async def adapt_response(self, new_response: Any, legacy_request: LegacyRequest) -> LegacyResponse:
        """Adapt new response to legacy format."""
        pass


class AgentEngineV1ToLegacyAdapter(CompatibilityAdapter):
    """
    Adapter that converts between Agent Engine V1 and legacy formats.

    This adapter allows existing code that uses the old agent engine interface
    to work seamlessly with the new agent_engine_v1 architecture.
    """

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        event_bus: EventBus,
        service_manager: ServiceIntegrationManager
    ):
        self.orchestrator = orchestrator
        self.event_bus = event_bus
        self.service_manager = service_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Adapter configuration
        self.enable_legacy_tool_mapping = True
        self.preserve_legacy_state_format = True
        self.legacy_timeout_seconds = 300

        # Legacy tool mapping
        self._setup_legacy_tool_mapping()

    def _setup_legacy_tool_mapping(self):
        """Setup mapping between legacy tool names and new intent names."""
        self.legacy_tool_mapping = {
            # File operations
            "read_file": "file_read",
            "write_file": "file_write",
            "delete_file": "file_delete",
            "list_directory": "file_list",

            # Code operations
            "execute_code": "code_execute",
            "analyze_code": "code_analyze",
            "modify_code": "code_modify",

            # Web operations
            "web_search": "web_search",
            "web_scrape": "web_scrape",
            "open_url": "web_open",

            # System operations
            "run_command": "system_execute",
            "get_system_info": "system_info",

            # Knowledge operations
            "search_knowledge": "knowledge_search",
            "add_knowledge": "knowledge_add",

            # Default mappings for unmapped tools
            "default": "unknown"
        }

    async def adapt_request(self, legacy_request: LegacyRequest) -> Dict[str, Any]:
        """
        Adapt legacy request to new AgentOrchestrator format.

        Args:
            legacy_request: Legacy request format

        Returns:
            Adapted request format for AgentOrchestrator
        """
        self.logger.debug(f"Adapting legacy request: {legacy_request.user_input[:50]}...")

        # Create enhanced context from legacy request
        enhanced_context = {
            "user_id": legacy_request.user_id,
            "legacy_format": True,
            "tool_permissions": legacy_request.tool_permissions or {},
            "adapter_version": "1.0.0",
            "adapted_at": datetime.now().isoformat()
        }

        # Add legacy metadata
        if legacy_request.metadata:
            enhanced_context["legacy_metadata"] = legacy_request.metadata

        # Map legacy tools to new intents if specified
        if legacy_request.context and "tool_requests" in legacy_request.context:
            enhanced_context["mapped_intents"] = self._map_legacy_tools(
                legacy_request.context["tool_requests"]
            )

        # Create adapted request
        adapted_request = {
            "user_input": legacy_request.user_input,
            "session_id": legacy_request.session_id,
            "context": enhanced_context,
            "timeout": self.legacy_timeout_seconds,
            "legacy_mode": True
        }

        return adapted_request

    async def adapt_response(self, execution_context, legacy_request: LegacyRequest) -> LegacyResponse:
        """
        Adapt new AgentOrchestrator response to legacy format.

        Args:
            execution_context: Result from AgentOrchestrator
            legacy_request: Original legacy request

        Returns:
            Legacy response format
        """
        self.logger.debug(f"Adapting response for session: {execution_context.session_id}")

        # Extract response from execution result
        response_text = ""
        success = True
        error_message = None
        execution_time_ms = 0.0

        if execution_context.execution_result:
            if execution_context.execution_result.success:
                # Extract response from result data
                if execution_context.execution_result.result_data:
                    response_text = execution_context.execution_result.result_data.get(
                        "response",
                        execution_context.execution_result.result_data.get("output", "")
                    )

                execution_time_ms = execution_context.execution_result.execution_time_ms
            else:
                success = False
                error_message = execution_context.execution_result.error_message

        # Handle cases where execution failed early
        if not execution_context.execution_result:
            if execution_context.permission_decision and not execution_context.permission_decision.allowed:
                success = False
                error_message = f"Permission denied: {execution_context.permission_decision.reason}"
            else:
                success = False
                error_message = "Execution failed"

        # Create tool calls list
        tool_calls = []
        if execution_context.intent_result:
            tool_calls.append({
                "tool": execution_context.intent_result.intent,
                "parameters": execution_context.intent_result.parameters,
                "confidence": execution_context.intent_result.confidence,
                "strategy": execution_context.intent_result.strategy_used
            })

        # Create state changes
        state_changes = None
        if self.preserve_legacy_state_format and execution_context.state_snapshot:
            state_changes = {
                "session_id": execution_context.session_id,
                "snapshot_id": execution_context.state_snapshot.snapshot_id,
                "state_data": execution_context.state_snapshot.state_data,
                "timestamp": execution_context.state_snapshot.timestamp
            }

        # Create legacy response
        legacy_response = LegacyResponse(
            response=response_text or "No response generated",
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            metadata={
                "session_id": execution_context.session_id,
                "execution_id": execution_context.execution_id,
                "adapter_version": "1.0.0",
                "intent": execution_context.intent_result.intent if execution_context.intent_result else None,
                "confidence": execution_context.intent_result.confidence if execution_context.intent_result else 0.0,
                "risk_level": execution_context.permission_decision.risk_level.value if execution_context.permission_decision else "unknown",
                "adapted_at": datetime.now().isoformat()
            },
            tool_calls=tool_calls,
            state_changes=state_changes
        )

        return legacy_response

    def _map_legacy_tools(self, tool_requests: List[str]) -> List[str]:
        """Map legacy tool names to new intent names."""
        mapped_intents = []

        for tool_name in tool_requests:
            # Direct mapping
            if tool_name in self.legacy_tool_mapping:
                mapped_intents.append(self.legacy_tool_mapping[tool_name])
            else:
                # Try fuzzy matching
                mapped_intent = self._fuzzy_match_tool(tool_name)
                mapped_intents.append(mapped_intent)

        return mapped_intents

    def _fuzzy_match_tool(self, tool_name: str) -> str:
        """Fuzzy match legacy tool name to intent."""
        tool_lower = tool_name.lower()

        # Check for partial matches
        for legacy_tool, intent in self.legacy_tool_mapping.items():
            if legacy_tool in tool_lower or tool_lower in legacy_tool:
                return intent

        # Default fallback
        return self.legacy_tool_mapping["default"]

    async def process_legacy_request(self, legacy_request: LegacyRequest) -> LegacyResponse:
        """
        Process a legacy request through the new system.

        This is the main entry point for legacy compatibility.

        Args:
            legacy_request: Legacy request format

        Returns:
            Legacy response format
        """
        try:
            # Adapt the request
            adapted_request = await self.adapt_request(legacy_request)

            # Process through new orchestrator
            execution_context = await self.orchestrator.process_request(
                user_input=adapted_request["user_input"],
                session_id=adapted_request["session_id"],
                context=adapted_request["context"]
            )

            # Adapt the response
            legacy_response = await self.adapt_response(execution_context, legacy_request)

            return legacy_response

        except Exception as e:
            self.logger.error(f"Error processing legacy request: {e}")

            # Return error response in legacy format
            return LegacyResponse(
                response="",
                success=False,
                error_message=f"Processing error: {str(e)}",
                metadata={
                    "adapter_version": "1.0.0",
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            )


class LegacyEventAdapter:
    """
    Adapter for legacy event system compatibility.

    This adapter converts events between the new EventBus format and legacy event formats.
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.legacy_event_handlers: Dict[str, List[Callable]] = {}

    def register_legacy_handler(self, event_type: str, handler: Callable):
        """Register a legacy event handler."""
        if event_type not in self.legacy_event_handlers:
            self.legacy_event_handlers[event_type] = []
        self.legacy_event_handlers[event_type].append(handler)

    async def adapt_and_publish_legacy_event(self, legacy_event: Dict[str, Any]):
        """
        Adapt and publish a legacy event to the new EventBus.

        Args:
            legacy_event: Legacy event format
        """
        try:
            # Convert legacy event to new format
            new_event = self._convert_legacy_event(legacy_event)

            # Publish to new EventBus
            await self.event_bus.publish(new_event)

        except Exception as e:
            self.logger.error(f"Error adapting legacy event: {e}")

    def _convert_legacy_event(self, legacy_event: Dict[str, Any]) -> Any:
        """Convert legacy event to new event format."""
        # This would contain the logic to convert legacy events
        # to new event types. Implementation depends on specific legacy format.
        pass

    async def subscribe_to_legacy_events(self, event_type: str, handler: Callable):
        """Subscribe to events and convert them to legacy format for handlers."""
        # Implementation would subscribe to new EventBus events
        # and convert them to legacy format before calling handlers
        pass


class MigrationHelper:
    """
    Helper class for managing migration from legacy to new system.

    Provides utilities for gradual migration and compatibility checking.
    """

    def __init__(self, compatibility_adapter: AgentEngineV1ToLegacyAdapter):
        self.adapter = compatibility_adapter
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Migration tracking
        self.migration_metrics = {
            "legacy_requests_processed": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "compatibility_issues": [],
            "last_migration": None
        }

    async def test_legacy_compatibility(self, test_cases: List[LegacyRequest]) -> Dict[str, Any]:
        """
        Test legacy compatibility with sample requests.

        Args:
            test_cases: List of legacy requests to test

        Returns:
            Compatibility test results
        """
        results = {
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "compatibility_score": 0.0
        }

        for i, test_case in enumerate(test_cases):
            try:
                # Process test case
                start_time = datetime.now()
                response = await self.adapter.process_legacy_request(test_case)
                end_time = datetime.now()

                # Record result
                test_result = {
                    "test_index": i,
                    "input": test_case.user_input[:100] + "..." if len(test_case.user_input) > 100 else test_case.user_input,
                    "success": response.success,
                    "response_length": len(response.response),
                    "processing_time_ms": (end_time - start_time).total_seconds() * 1000,
                    "error": response.error_message
                }

                results["test_results"].append(test_result)

                if response.success:
                    results["passed_tests"] += 1
                else:
                    results["failed_tests"] += 1

            except Exception as e:
                # Record test failure
                test_result = {
                    "test_index": i,
                    "input": test_case.user_input[:100] + "..." if len(test_case.user_input) > 100 else test_case.user_input,
                    "success": False,
                    "error": str(e),
                    "processing_time_ms": 0
                }

                results["test_results"].append(test_result)
                results["failed_tests"] += 1

        # Calculate compatibility score
        if results["total_tests"] > 0:
            results["compatibility_score"] = results["passed_tests"] / results["total_tests"]

        return results

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status and metrics."""
        return {
            "migration_metrics": self.migration_metrics.copy(),
            "adapter_health": self._check_adapter_health(),
            "recommendations": self._get_migration_recommendations()
        }

    def _check_adapter_health(self) -> Dict[str, Any]:
        """Check the health of the compatibility adapter."""
        health_status = {
            "healthy": True,
            "issues": [],
            "performance": "good"
        }

        # Check success rate
        total = self.migration_metrics["legacy_requests_processed"]
        if total > 0:
            success_rate = self.migration_metrics["successful_migrations"] / total
            if success_rate < 0.9:
                health_status["healthy"] = False
                health_status["issues"].append(f"Low success rate: {success_rate:.2%}")
                health_status["performance"] = "poor"
            elif success_rate < 0.95:
                health_status["performance"] = "fair"

        return health_status

    def _get_migration_recommendations(self) -> List[str]:
        """Get recommendations for migration improvement."""
        recommendations = []

        if len(self.migration_metrics["compatibility_issues"]) > 0:
            recommendations.append("Address compatibility issues in adapter")

        success_rate = 0
        total = self.migration_metrics["legacy_requests_processed"]
        if total > 0:
            success_rate = self.migration_metrics["successful_migrations"] / total

        if success_rate < 0.95:
            recommendations.append("Improve error handling and edge case coverage")

        if not self.migration_metrics["last_migration"]:
            recommendations.append("Start processing migration test cases")

        return recommendations

    async def record_migration_attempt(self, success: bool, error: Optional[str] = None):
        """Record a migration attempt for metrics tracking."""
        self.migration_metrics["legacy_requests_processed"] += 1

        if success:
            self.migration_metrics["successful_migrations"] += 1
        else:
            self.migration_metrics["failed_migrations"] += 1
            if error:
                self.migration_metrics["compatibility_issues"].append({
                    "timestamp": datetime.now().isoformat(),
                    "error": error
                })

        self.migration_metrics["last_migration"] = datetime.now().isoformat()