"""Primitive Registry for managing institutional primitives.

This module provides the registry system for discovering, registering,
and instantiating institutional primitive nodes.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from .base import InstitutionalPrimitive, PrimitiveInfo, ValidationResult

logger = logging.getLogger(__name__)


class PrimitiveRegistry:
    """Registry for managing institutional primitive types.
    
    The registry handles registration, discovery, and instantiation of
    institutional primitives, providing a centralized way to manage
    available workflow nodes.
    """

    def __init__(self):
        """Initialize the primitive registry."""
        self._primitives: Dict[str, Type[InstitutionalPrimitive]] = {}
        self._primitive_info: Dict[str, PrimitiveInfo] = {}

    def register_primitive(
        self,
        primitive_type: str,
        primitive_class: Type[InstitutionalPrimitive]
    ) -> bool:
        """Register a primitive type with the registry.
        
        Args:
            primitive_type: Unique identifier for the primitive type
            primitive_class: Class implementing the InstitutionalPrimitive interface
            
        Returns:
            True if registration was successful, False otherwise

        """
        try:
            # Validate that the class implements InstitutionalPrimitive
            if not issubclass(primitive_class, InstitutionalPrimitive):
                logger.error(f"Class {primitive_class.__name__} does not implement InstitutionalPrimitive")
                return False

            # Check if primitive type is already registered
            if primitive_type in self._primitives:
                logger.warning(f"Primitive type '{primitive_type}' is already registered. Overwriting.")

            # Create an instance to get primitive info
            try:
                instance = primitive_class()
                primitive_info = instance.get_primitive_info()
                primitive_info.type = primitive_type  # Ensure type matches registration
            except Exception as e:
                logger.error(f"Failed to create instance of {primitive_class.__name__}: {e}")
                return False

            # Register the primitive
            self._primitives[primitive_type] = primitive_class
            self._primitive_info[primitive_type] = primitive_info

            logger.info(f"Successfully registered primitive '{primitive_type}' ({primitive_class.__name__})")
            return True

        except Exception as e:
            logger.error(f"Failed to register primitive '{primitive_type}': {e}")
            return False

    def get_primitive(self, primitive_type: str) -> Optional[Type[InstitutionalPrimitive]]:
        """Get a primitive class by type.
        
        Args:
            primitive_type: Type identifier of the primitive
            
        Returns:
            Primitive class if found, None otherwise

        """
        return self._primitives.get(primitive_type)

    def create_primitive(
        self,
        primitive_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[InstitutionalPrimitive]:
        """Create an instance of a primitive by type.
        
        Args:
            primitive_type: Type identifier of the primitive
            config: Optional configuration for the primitive
            
        Returns:
            Primitive instance if successful, None otherwise

        """
        primitive_class = self.get_primitive(primitive_type)
        if primitive_class is None:
            logger.error(f"Primitive type '{primitive_type}' not found in registry")
            return None

        try:
            return primitive_class(config)
        except Exception as e:
            logger.error(f"Failed to create primitive '{primitive_type}': {e}")
            return None

    def list_primitives(self) -> List[PrimitiveInfo]:
        """List all registered primitives.
        
        Returns:
            List of PrimitiveInfo objects for all registered primitives

        """
        return list(self._primitive_info.values())

    def get_primitive_info(self, primitive_type: str) -> Optional[PrimitiveInfo]:
        """Get information about a specific primitive.
        
        Args:
            primitive_type: Type identifier of the primitive
            
        Returns:
            PrimitiveInfo if found, None otherwise

        """
        return self._primitive_info.get(primitive_type)

    def validate_primitive(self, primitive_def: Dict[str, Any]) -> ValidationResult:
        """Validate a primitive definition.
        
        Args:
            primitive_def: Dictionary containing primitive definition
            
        Returns:
            ValidationResult indicating whether the definition is valid

        """
        errors = []
        warnings = []

        try:
            # Check required fields
            required_fields = ['type', 'config']
            for field in required_fields:
                if field not in primitive_def:
                    errors.append(f"Required field '{field}' is missing from primitive definition")

            # Check if primitive type exists
            primitive_type = primitive_def.get('type')
            if primitive_type and primitive_type not in self._primitives:
                errors.append(f"Primitive type '{primitive_type}' is not registered")

            # Validate configuration if primitive type exists
            if primitive_type and primitive_type in self._primitives:
                try:
                    config = primitive_def.get('config', {})
                    primitive = self.create_primitive(primitive_type, config)
                    if primitive is None:
                        errors.append("Failed to create primitive instance for validation")
                except Exception as e:
                    errors.append(f"Configuration validation failed: {str(e)}")

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

    def unregister_primitive(self, primitive_type: str) -> bool:
        """Unregister a primitive type.
        
        Args:
            primitive_type: Type identifier of the primitive to unregister
            
        Returns:
            True if unregistration was successful, False otherwise

        """
        if primitive_type not in self._primitives:
            logger.warning(f"Primitive type '{primitive_type}' is not registered")
            return False

        try:
            del self._primitives[primitive_type]
            del self._primitive_info[primitive_type]
            logger.info(f"Successfully unregistered primitive '{primitive_type}'")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister primitive '{primitive_type}': {e}")
            return False

    def is_registered(self, primitive_type: str) -> bool:
        """Check if a primitive type is registered.
        
        Args:
            primitive_type: Type identifier to check
            
        Returns:
            True if the primitive type is registered, False otherwise

        """
        return primitive_type in self._primitives

    def get_primitives_by_tag(self, tag: str) -> List[PrimitiveInfo]:
        """Get all primitives that have a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of PrimitiveInfo objects for primitives with the specified tag

        """
        return [
            info for info in self._primitive_info.values()
            if tag in info.tags
        ]

    def clear(self) -> None:
        """Clear all registered primitives."""
        self._primitives.clear()
        self._primitive_info.clear()
        logger.info("Cleared all registered primitives")


# Global registry instance
_global_registry = PrimitiveRegistry()


def get_global_registry() -> PrimitiveRegistry:
    """Get the global primitive registry instance.
    
    Returns:
        Global PrimitiveRegistry instance

    """
    return _global_registry


def register_primitive(primitive_type: str, primitive_class: Type[InstitutionalPrimitive]) -> bool:
    """Register a primitive with the global registry.
    
    Args:
        primitive_type: Unique identifier for the primitive type
        primitive_class: Class implementing the InstitutionalPrimitive interface
        
    Returns:
        True if registration was successful, False otherwise

    """
    return _global_registry.register_primitive(primitive_type, primitive_class)
