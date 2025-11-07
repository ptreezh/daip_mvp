"""Service interfaces for the agent engine domain services."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ..events.event_types import BaseEvent


# Core service interface
class IDomainService(ABC):
    """Base interface for all domain services."""

    @abstractmethod
    async def start(self) -> None:
        """Start the service."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the service."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        pass


# Intent Recognition Service Interface
class IntentRecognitionResult:
    """Result of intent recognition."""

    def __init__(
        self,
        intent: str,
        confidence: float,
        parameters: Optional[Dict[str, Any]] = None,
        reasoning: Optional[str] = None,
        strategy_used: Optional[str] = None
    ):
        """
        Initialize intent recognition result.

        Args:
            intent: The recognized intent
            confidence: Confidence score (0.0 to 1.0)
            parameters: Extracted parameters for the intent
            reasoning: Explanation of the recognition process
            strategy_used: Which recognition strategy was used
        """
        self.intent = intent
        self.confidence = confidence
        self.parameters = parameters or {}
        self.reasoning = reasoning
        self.strategy_used = strategy_used
        self.timestamp = asyncio.get_event_loop().time()


class IIntentRecognitionService(IDomainService):
    """Interface for intent recognition service."""

    @abstractmethod
    async def recognize_intent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentRecognitionResult:
        """
        Recognize the intent from input text.

        Args:
            input_text: The input text to analyze
            context: Optional context information

        Returns:
            Intent recognition result with confidence and parameters
        """
        pass

    @abstractmethod
    async def batch_recognize_intents(
        self,
        inputs: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[IntentRecognitionResult]:
        """
        Recognize intents for multiple inputs.

        Args:
            inputs: List of input texts
            context: Optional context information

        Returns:
            List of intent recognition results
        """
        pass

    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents."""
        pass

    @abstractmethod
    def add_custom_intent(
        self,
        intent: str,
        patterns: List[str],
        parameters: Optional[List[str]] = None
    ) -> None:
        """
        Add a custom intent pattern.

        Args:
            intent: Intent name
            patterns: Pattern strings that match this intent
            parameters: List of parameter names to extract
        """
        pass


# Execution Engine Service Interface
class ExecutionResult:
    """Result of task execution."""

    def __init__(
        self,
        success: bool,
        output: Any = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution result.

        Args:
            success: Whether the execution was successful
            output: The execution output
            error: Error message if execution failed
            execution_time_ms: Execution time in milliseconds
            metadata: Additional execution metadata
        """
        self.success = success
        self.output = output
        self.error = error
        self.execution_time_ms = execution_time_ms
        self.metadata = metadata or {}
        self.timestamp = asyncio.get_event_loop().time()


class IExecutionEngineService(IDomainService):
    """Interface for execution engine service."""

    @abstractmethod
    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a task.

        Args:
            task: Task specification
            context: Optional execution context

        Returns:
            Execution result
        """
        pass

    @abstractmethod
    async def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a specific tool.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            context: Optional execution context

        Returns:
            Execution result
        """
        pass

    @abstractmethod
    async def execute_with_timeout(
        self,
        task: Dict[str, Any],
        timeout_seconds: float,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a task with a timeout.

        Args:
            task: Task specification
            timeout_seconds: Maximum execution time
            context: Optional execution context

        Returns:
            Execution result
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        pass

    @abstractmethod
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        pass


# State Management Service Interface
class StateSnapshot:
    """Snapshot of system state."""

    def __init__(
        self,
        state_data: Dict[str, Any],
        timestamp: Optional[float] = None,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize state snapshot.

        Args:
            state_data: The state data
            timestamp: Snapshot timestamp
            version: State version
            metadata: Additional metadata
        """
        self.state_data = state_data
        self.timestamp = timestamp or asyncio.get_event_loop().time()
        self.version = version
        self.metadata = metadata or {}


class IStateManagementService(IDomainService):
    """Interface for state management service."""

    @abstractmethod
    async def get_state(
        self,
        state_key: str,
        scope: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get state value.

        Args:
            state_key: Key of the state
            scope: Optional scope identifier

        Returns:
            State value or None if not found
        """
        pass

    @abstractmethod
    async def set_state(
        self,
        state_key: str,
        value: Any,
        scope: Optional[str] = None
    ) -> None:
        """
        Set state value.

        Args:
            state_key: Key of the state
            value: State value
            scope: Optional scope identifier
        """
        pass

    @abstractmethod
    async def update_state(
        self,
        state_key: str,
        updates: Dict[str, Any],
        scope: Optional[str] = None
    ) -> Any:
        """
        Update state with partial updates.

        Args:
            state_key: Key of the state
            updates: Dictionary of updates
            scope: Optional scope identifier

        Returns:
            Updated state value
        """
        pass

    @abstractmethod
    async def delete_state(
        self,
        state_key: str,
        scope: Optional[str] = None
    ) -> bool:
        """
        Delete state.

        Args:
            state_key: Key of the state
            scope: Optional scope identifier

        Returns:
            True if state was deleted, False if not found
        """
        pass

    @abstractmethod
    async def create_snapshot(
        self,
        scope: Optional[str] = None
    ) -> StateSnapshot:
        """
        Create a snapshot of current state.

        Args:
            scope: Optional scope identifier

        Returns:
            State snapshot
        """
        pass

    @abstractmethod
    async def restore_snapshot(
        self,
        snapshot: StateSnapshot,
        scope: Optional[str] = None
    ) -> None:
        """
        Restore state from snapshot.

        Args:
            snapshot: Snapshot to restore
            scope: Optional scope identifier
        """
        pass

    @abstractmethod
    def get_state_history(
        self,
        state_key: str,
        scope: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get history of state changes.

        Args:
            state_key: Key of the state
            scope: Optional scope identifier
            limit: Maximum number of history entries

        Returns:
            List of state change records
        """
        pass


# Permission Service Interface
class PermissionRequest:
    """Permission request data."""

    def __init__(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        permission_type: str = "execute",
        risk_level: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize permission request.

        Args:
            tool_name: Name of the tool requiring permission
            tool_args: Arguments for the tool
            permission_type: Type of permission required
            risk_level: Risk level (low, medium, high, critical)
            context: Additional context information
        """
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.permission_type = permission_type
        self.risk_level = risk_level
        self.context = context or {}
        self.request_id = f"perm_{id(self)}"
        self.timestamp = asyncio.get_event_loop().time()


class PermissionDecision:
    """Permission decision result."""

    def __init__(
        self,
        granted: bool,
        reason: Optional[str] = None,
        conditions: Optional[List[str]] = None,
        expires_at: Optional[float] = None,
        risk_level: Optional[str] = None
    ):
        """
        Initialize permission decision.

        Args:
            granted: Whether permission is granted
            reason: Reason for the decision
            conditions: Any conditions for the permission
            expires_at: When the permission expires
            risk_level: Risk level for this decision
        """
        self.granted = granted
        self.allowed = granted  # Alias for compatibility with orchestrator
        self.reason = reason
        self.conditions = conditions or []
        self.expires_at = expires_at
        self.risk_level = risk_level or "medium"
        self.confidence = 1.0 if granted else 0.0  # Default confidence
        self.rules_applied = []  # Default empty rules list
        self.timestamp = asyncio.get_event_loop().time()


class IPermissionService(IDomainService):
    """Interface for permission service."""

    @abstractmethod
    async def check_permission(
        self,
        request: PermissionRequest
    ) -> PermissionDecision:
        """
        Check if a permission request should be granted.

        Args:
            request: Permission request to evaluate

        Returns:
            Permission decision
        """
        pass

    @abstractmethod
    async def batch_check_permissions(
        self,
        requests: List[PermissionRequest]
    ) -> List[PermissionDecision]:
        """
        Check multiple permission requests.

        Args:
            requests: List of permission requests

        Returns:
            List of permission decisions
        """
        pass

    @abstractmethod
    async def grant_permission(
        self,
        tool_name: str,
        conditions: Optional[List[str]] = None,
        expires_at: Optional[float] = None
    ) -> None:
        """
        Grant permission for a tool.

        Args:
            tool_name: Tool name
            conditions: Any conditions
            expires_at: Expiration time
        """
        pass

    @abstractmethod
    async def revoke_permission(
        self,
        tool_name: str,
        reason: Optional[str] = None
    ) -> None:
        """
        Revoke permission for a tool.

        Args:
            tool_name: Tool name
            reason: Reason for revocation
        """
        pass

    @abstractmethod
    def get_permission_policy(
        self,
        tool_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get permission policy for a tool.

        Args:
            tool_name: Tool name

        Returns:
            Permission policy or None
        """
        pass

    @abstractmethod
    def set_permission_policy(
        self,
        tool_name: str,
        policy: Dict[str, Any]
    ) -> None:
        """
        Set permission policy for a tool.

        Args:
            tool_name: Tool name
            policy: Permission policy
        """
        pass

    @abstractmethod
    def get_audit_log(
        self,
        limit: int = 100,
        tool_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get permission audit log.

        Args:
            limit: Maximum number of entries
            tool_name: Optional tool name filter

        Returns:
            List of audit log entries
        """
        pass