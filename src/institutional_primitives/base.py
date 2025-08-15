"""Base classes for the Institutional Primitives System.

This module defines the core abstractions for institutional primitives,
including the base InstitutionalPrimitive class and execution context.
"""

from abc import ABC, abstractmethod
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """Context for primitive execution, containing workflow state and available services.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    execution_id: str
    workflow_id: str
    node_id: str
    services: dict[str, Any] = Field(default_factory=dict)  # Available DAIP-LIVE services
    state: dict[str, Any] = Field(default_factory=dict)  # Workflow state
    parent_context: Optional["ExecutionContext"] = None
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed

    def create_child_context(self, node_id: str) -> "ExecutionContext":
        """Create a child execution context for a sub-node."""
        return ExecutionContext(
            execution_id=self.execution_id,
            workflow_id=self.workflow_id,
            node_id=node_id,
            services=self.services,
            state=self.state,
            parent_context=self
        )

    def mark_started(self) -> None:
        """Mark the execution as started."""
        self.start_time = datetime.now()
        self.status = "running"

    def mark_completed(self) -> None:
        """Mark the execution as completed."""
        self.end_time = datetime.now()
        self.status = "completed"

    def mark_failed(self) -> None:
        """Mark the execution as failed."""
        self.end_time = datetime.now()
        self.status = "failed"


class ExecutionStep(BaseModel):
    """Record of a single execution step in the workflow.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    node_id: str
    node_type: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status: str  # completed, failed
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionTrace(BaseModel):
    """Complete trace of workflow execution, including all steps and metrics.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    execution_id: str
    workflow_id: str
    steps: list[ExecutionStep] = Field(default_factory=list)
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str  # running, completed, failed, cancelled
<<<<<<< HEAD
    metrics: Dict[str, Any] = Field(default_factory=dict)

=======
    metrics: dict[str, Any] = Field(default_factory=dict)
    
>>>>>>> feature/core-services-refactor
    def add_step(self, step: ExecutionStep) -> None:
        """Add an execution step to the trace."""
        self.steps.append(step)

    def mark_completed(self) -> None:
        """Mark the execution as completed."""
        self.end_time = datetime.now()
        self.status = "completed"

    def mark_failed(self) -> None:
        """Mark the execution as failed."""
        self.end_time = datetime.now()
        self.status = "failed"

    def mark_cancelled(self) -> None:
        """Mark the execution as cancelled."""
        self.end_time = datetime.now()
        self.status = "cancelled"


class InstitutionalPrimitive(ABC):
    """Base class for all institutional primitives.
    
    Institutional primitives are standardized workflow nodes that encapsulate
    atomic capabilities like fact extraction, opinion synthesis, and voting.
    They serve as the fundamental building blocks for complex social institutions
    within AI collaboration systems.
    """
<<<<<<< HEAD

    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
=======
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
>>>>>>> feature/core-services-refactor
        """Initialize the institutional primitive.
        
        Args:
            primitive_id: Unique identifier for this primitive instance
            config: Configuration parameters for this primitive

        """
        self.primitive_id = primitive_id
        self.config = config or {}

    @abstractmethod
<<<<<<< HEAD
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
=======
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Execute the primitive with given inputs and context.
        
        Args:
            inputs: Input data for the primitive
            context: Execution context containing workflow state and services
            
        Returns:
            Output data produced by the primitive

        """
        pass

    @abstractmethod
<<<<<<< HEAD
    def get_input_schema(self) -> Dict[str, Any]:
=======
    def get_input_schema(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Return JSON schema for expected inputs.
        
        Returns:
            JSON schema describing the expected input format

        """
        pass

    @abstractmethod
<<<<<<< HEAD
    def get_output_schema(self) -> Dict[str, Any]:
=======
    def get_output_schema(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Return JSON schema for produced outputs.
        
        Returns:
            JSON schema describing the produced output format

        """
        pass
<<<<<<< HEAD

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
=======
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
>>>>>>> feature/core-services-refactor
        """Validate that the inputs match the expected schema.
        
        Args:
            inputs: Input data to validate
            
        Returns:
            True if inputs are valid, False otherwise

        """
        # In a real implementation, this would use the JSON schema to validate
        # For now, we'll just return True
        return True
<<<<<<< HEAD

    def validate_outputs(self, outputs: Dict[str, Any]) -> bool:
=======
    
    def validate_outputs(self, outputs: dict[str, Any]) -> bool:
>>>>>>> feature/core-services-refactor
        """Validate that the outputs match the expected schema.
        
        Args:
            outputs: Output data to validate
            
        Returns:
            True if outputs are valid, False otherwise

        """
        # In a real implementation, this would use the JSON schema to validate
        # For now, we'll just return True
        return True
<<<<<<< HEAD

    def get_metadata(self) -> Dict[str, Any]:
=======
    
    def get_metadata(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get metadata about this primitive.
        
        Returns:
            Dictionary containing metadata about this primitive

        """
        return {
            "id": self.primitive_id,
            "type": self.__class__.__name__,
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema(),
            "config": self.config
        }


class PrimitiveInfo(BaseModel):
    """Information about a registered primitive type.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    type: str
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    version: str


class ValidationResult(BaseModel):
    """Result of validating a primitive definition.
    """
<<<<<<< HEAD

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
=======
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
>>>>>>> feature/core-services-refactor
