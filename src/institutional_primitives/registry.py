"""Registry for institutional primitives.

This module provides a registry for institutional primitives, allowing
for their registration, discovery, and instantiation.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from .base import InstitutionalPrimitive, PrimitiveInfo, ValidationResult


class PrimitiveRegistry:
    """Registry for institutional primitives.
    
    This class manages the registration, discovery, and instantiation of
    institutional primitive nodes.
    """

    def __init__(self):
        """Initialize the primitive registry."""
        self._primitives: Dict[str, Type[InstitutionalPrimitive]] = {}
        self._logger = logging.getLogger(__name__)

    def register_primitive(self, primitive_type: str, primitive_class: Type[InstitutionalPrimitive]) -> bool:
        """Register a primitive type with the registry.
        
        Args:
            primitive_type: Type identifier for the primitive
            primitive_class: Class implementing the primitive
            
        Returns:
            True if registration was successful, False otherwise

        """
        if primitive_type in self._primitives:
            self._logger.warning(f"Primitive type '{primitive_type}' already registered. Overwriting.")

        self._primitives[primitive_type] = primitive_class
        self._logger.info(f"Registered primitive type '{primitive_type}'")
        return True

    def get_primitive(self, primitive_type: str) -> Optional[Type[InstitutionalPrimitive]]:
        """Get a primitive class by type.
        
        Args:
            primitive_type: Type identifier for the primitive
            
        Returns:
            The primitive class, or None if not found

        """
        if primitive_type not in self._primitives:
            self._logger.warning(f"Primitive type '{primitive_type}' not found in registry")
            return None

        return self._primitives[primitive_type]

    def list_primitives(self) -> List[PrimitiveInfo]:
        """List all registered primitives.
        
        Returns:
            List of information about registered primitives

        """
        result = []
        for primitive_type, primitive_class in self._primitives.items():
            # Create a temporary instance to get schemas
            # In a real implementation, this might be handled differently
            temp_instance = primitive_class(primitive_id="temp")

            info = PrimitiveInfo(
                type=primitive_type,
                name=primitive_class.__name__,
                description=primitive_class.__doc__ or "",
                input_schema=temp_instance.get_input_schema(),
                output_schema=temp_instance.get_output_schema(),
                version="1.0.0"  # In a real implementation, this would be dynamic
            )
            result.append(info)

        return result

    def validate_primitive(self, primitive_def: Dict[str, Any]) -> ValidationResult:
        """Validate a primitive definition.
        
        Args:
            primitive_def: Definition of the primitive to validate
            
        Returns:
            Validation result indicating whether the definition is valid

        """
        result = ValidationResult(is_valid=True)

        # Check required fields
        required_fields = ["type", "id", "config"]
        for field in required_fields:
            if field not in primitive_def:
                result.is_valid = False
                result.errors.append(f"Missing required field '{field}'")

        if not result.is_valid:
            return result

        # Check if primitive type exists
        primitive_type = primitive_def["type"]
        if primitive_type not in self._primitives:
            result.is_valid = False
            result.errors.append(f"Unknown primitive type '{primitive_type}'")
            return result

        # In a real implementation, we would also validate the config against
        # the primitive's expected configuration schema

        return result

    def instantiate_primitive(self, primitive_def: Dict[str, Any]) -> Optional[InstitutionalPrimitive]:
        """Instantiate a primitive from a definition.
        
        Args:
            primitive_def: Definition of the primitive to instantiate
            
        Returns:
            Instantiated primitive, or None if instantiation failed

        """
        validation = self.validate_primitive(primitive_def)
        if not validation.is_valid:
            self._logger.error(f"Cannot instantiate invalid primitive: {validation.errors}")
            return None

        primitive_type = primitive_def["type"]
        primitive_id = primitive_def["id"]
        config = primitive_def.get("config", {})

        primitive_class = self._primitives[primitive_type]
        try:
            instance = primitive_class(primitive_id=primitive_id, config=config)
            return instance
        except Exception as e:
            self._logger.error(f"Error instantiating primitive '{primitive_id}' of type '{primitive_type}': {e}")
            return None
