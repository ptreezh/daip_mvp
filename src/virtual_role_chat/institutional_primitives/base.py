"""Base classes for institutional primitives.

This module defines the abstract base class and core interfaces for all
institutional primitives - standardized workflow nodes that encapsulate
atomic capabilities for AI collaboration workflows.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """Context information available during primitive execution."""

    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    node_id: str
    services: dict[str, Any] = Field(default_factory=dict)  # Available DAIP-LIVE services
    state: dict[str, Any] = Field(default_factory=dict)  # Workflow state
    metadata: dict[str, Any] = Field(default_factory=dict)  # Additional metadata
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True


class PrimitiveInfo(BaseModel):
    """Information about a registered primitive."""

    type: str
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    version: str = "1.0.0"
    tags: list[str] = Field(default_factory=list)
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ValidationResult(BaseModel):
    """Result of primitive validation."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    """Result of primitive execution."""

    success: bool
    outputs: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    execution_time: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class InstitutionalPrimitive(ABC):
    """Abstract base class for all institutional primitives.
    
    Institutional primitives are standardized workflow nodes that encapsulate
    atomic capabilities like fact extraction, opinion synthesis, voting, etc.
    They serve as the fundamental building blocks for complex social institutions
    within AI collaboration systems.
    """
    
    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize the primitive with configuration.
        
        Args:
            config: Optional configuration dictionary for the primitive

        """
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        """Execute the primitive with given inputs and context.
        
        Args:
            inputs: Input data for the primitive execution
            context: Execution context containing services, state, and metadata
            
        Returns:
            ExecutionResult containing outputs, errors, and execution metadata

        """
        pass

    @abstractmethod
    def get_input_schema(self) -> dict[str, Any]:
        """Return JSON schema for expected inputs.
        
        Returns:
            JSON schema dictionary describing expected input structure

        """
        pass

    @abstractmethod
    def get_output_schema(self) -> dict[str, Any]:
        """Return JSON schema for produced outputs.
        
        Returns:
            JSON schema dictionary describing output structure

        """
        pass

    def get_primitive_info(self) -> PrimitiveInfo:
        """Get information about this primitive.
        
        Returns:
            PrimitiveInfo containing metadata about the primitive

        """
        return PrimitiveInfo(
            type=self.get_primitive_type(),
            name=self.get_name(),
            description=self.get_description(),
            input_schema=self.get_input_schema(),
            output_schema=self.get_output_schema(),
            version=self.get_version(),
            tags=self.get_tags(),
            author=self.get_author()
        )
    
    def validate_inputs(self, inputs: dict[str, Any]) -> ValidationResult:
        """Validate inputs against the input schema.
        
        Args:
            inputs: Input data to validate
            
        Returns:
            ValidationResult indicating whether inputs are valid

        """
        try:
            # Basic validation - can be extended with jsonschema
            schema = self.get_input_schema()
            required_fields = schema.get('required', [])

            errors = []
            warnings = []

            # Check required fields
            for field in required_fields:
                if field not in inputs:
                    errors.append(f"Required field '{field}' is missing")

            # Check for unexpected fields
            properties = schema.get('properties', {})
            for field in inputs:
                if field not in properties:
                    warnings.append(f"Unexpected field '{field}' in inputs")

            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def validate_outputs(self, outputs: dict[str, Any]) -> ValidationResult:
        """Validate outputs against the output schema.
        
        Args:
            outputs: Output data to validate
            
        Returns:
            ValidationResult indicating whether outputs are valid

        """
        try:
            # Basic validation - can be extended with jsonschema
            schema = self.get_output_schema()
            required_fields = schema.get('required', [])

            errors = []
            warnings = []

            # Check required fields
            for field in required_fields:
                if field not in outputs:
                    errors.append(f"Required output field '{field}' is missing")

            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Output validation error: {str(e)}"]
            )

    def get_primitive_type(self) -> str:
        """Get the type identifier for this primitive.
        
        Returns:
            String identifier for the primitive type

        """
        return self.__class__.__name__.lower().replace('primitive', '').replace('node', '')

    def get_name(self) -> str:
        """Get the human-readable name for this primitive.
        
        Returns:
            Human-readable name

        """
        return self.__class__.__name__

    def get_description(self) -> str:
        """Get the description for this primitive.
        
        Returns:
            Description of what this primitive does

        """
        return self.__doc__ or "No description available"

    def get_version(self) -> str:
        """Get the version of this primitive.
        
        Returns:
            Version string

        """
        return "1.0.0"
    
    def get_tags(self) -> list[str]:
        """Get tags associated with this primitive.
        
        Returns:
            List of tags

        """
        return []

    def get_author(self) -> Optional[str]:
        """Get the author of this primitive.
        
        Returns:
            Author name or None

        """
        return None

    def _validate_config(self) -> None:
        """Validate the primitive configuration.
        
        Raises:
            ValueError: If configuration is invalid

        """
        # Override in subclasses to add specific validation
        pass
    
    async def _pre_execute(self, inputs: dict[str, Any], context: ExecutionContext) -> None:
        """Pre-execution hook for setup operations.
        
        Args:
            inputs: Input data
            context: Execution context

        """
        pass

    async def _post_execute(self, result: ExecutionResult, context: ExecutionContext) -> None:
        """Post-execution hook for cleanup operations.
        
        Args:
            result: Execution result
            context: Execution context

        """
        pass