"""
Registry for institutional primitives.

This module provides a registry for institutional primitives, allowing
for their registration, discovery, and instantiation.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from .base import InstitutionalPrimitive, PrimitiveInfo, ValidationResult


class PrimitiveRegistry:
    """
    Registry for institutional primitives.
    
    This class manages the registration, discovery, and instantiation of
    institutional primitive nodes with persistent storage.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the primitive registry.
        
        Args:
            storage_path: Path to store workflow definitions. If None, uses default.
        """
        self._primitives: Dict[str, Type[InstitutionalPrimitive]] = {}
        self._workflow_definitions: Dict[str, Dict[str, Any]] = {}
        self._logger = logging.getLogger(__name__)
        
        # Set up persistent storage
        if storage_path is None:
            # Use default path relative to project root
            self.storage_path = Path("data/workflows")
        else:
            self.storage_path = Path(storage_path)
        
        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing workflow definitions
        self._load_workflow_definitions()
        
        self._logger.info(f"PrimitiveRegistry initialized with storage at: {self.storage_path}")
    
    def _load_workflow_definitions(self):
        """Load workflow definitions from persistent storage."""
        try:
            for workflow_file in self.storage_path.glob("*.json"):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        workflow_def = json.load(f)
                        workflow_id = workflow_def.get("id", workflow_file.stem)
                        self._workflow_definitions[workflow_id] = workflow_def
                        
                        # Create and register the workflow primitive class
                        self._register_workflow_primitive(workflow_id, workflow_def)
                        
                        self._logger.info(f"Loaded workflow definition: {workflow_id}")
                except Exception as e:
                    self._logger.error(f"Error loading workflow from {workflow_file}: {e}")
        except Exception as e:
            self._logger.error(f"Error scanning workflow directory: {e}")
    
    def _register_workflow_primitive(self, workflow_id: str, workflow_def: Dict[str, Any]):
        """Create and register a workflow primitive class."""
        try:
            class WorkflowPrimitive:
                def __init__(self, primitive_id: str):
                    self.id = primitive_id
                    self.definition = workflow_def
                
                def get_input_schema(self):
                    return {"type": "object", "properties": {}}
                
                def get_output_schema(self):
                    return {"type": "object", "properties": {}}
                
                def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
                    # Basic execution implementation
                    return {
                        "status": "success",
                        "result": f"Workflow {workflow_id} executed successfully",
                        "workflow_id": workflow_id,
                        "params": params,
                        "steps_executed": len(workflow_def.get("steps", []))
                    }
            
            # Register the primitive class
            self.register_primitive(workflow_id, WorkflowPrimitive)
            self._logger.info(f"Registered workflow primitive: {workflow_id}")
            
        except Exception as e:
            self._logger.error(f"Error registering workflow primitive {workflow_id}: {e}")
    
    def _save_workflow_definition(self, workflow_id: str, workflow_def: Dict[str, Any]):
        """Save workflow definition to persistent storage."""
        try:
            workflow_file = self.storage_path / f"{workflow_id}.json"
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(workflow_def, f, indent=2, ensure_ascii=False)
            self._logger.info(f"Saved workflow definition: {workflow_id} to {workflow_file}")
        except Exception as e:
            self._logger.error(f"Error saving workflow {workflow_id}: {e}")
            raise
    
    def register_workflow(self, workflow_def: Dict[str, Any]) -> bool:
        """
        Register a workflow with persistent storage.
        
        Args:
            workflow_def: Workflow definition dictionary
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Validate workflow definition
            required_fields = ["name", "description", "steps"]
            for field in required_fields:
                if field not in workflow_def:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure workflow has an ID
            if "id" not in workflow_def:
                workflow_def["id"] = workflow_def["name"].lower().replace(" ", "_")
            
            workflow_id = workflow_def["id"]
            
            # Create a workflow primitive class
            class WorkflowPrimitive:
                def __init__(self, primitive_id: str):
                    self.id = primitive_id
                    self.definition = workflow_def
                
                def get_input_schema(self):
                    return {"type": "object", "properties": {}}
                
                def get_output_schema(self):
                    return {"type": "object", "properties": {}}
                
                def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
                    # Basic execution implementation
                    return {
                        "status": "success",
                        "result": f"Workflow {workflow_id} executed",
                        "workflow_id": workflow_id,
                        "params": params
                    }
            
            # Register the primitive class
            success = self.register_primitive(workflow_id, WorkflowPrimitive)
            
            if success:
                # Save workflow definition to persistent storage
                self._save_workflow_definition(workflow_id, workflow_def)
                self._workflow_definitions[workflow_id] = workflow_def
            
            return success
            
        except Exception as e:
            self._logger.error(f"Error registering workflow: {e}")
            return False
    
    def get_workflow_definition(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow definition by ID.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow definition dictionary, or None if not found
        """
        return self._workflow_definitions.get(workflow_id)
    
    def list_workflow_definitions(self) -> List[Dict[str, Any]]:
        """
        List all registered workflow definitions.
        
        Returns:
            List of workflow definition dictionaries
        """
        return list(self._workflow_definitions.values())
    
    def unregister_workflow(self, workflow_id: str) -> bool:
        """
        Unregister a workflow and remove from persistent storage.
        
        Args:
            workflow_id: ID of the workflow to unregister
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from memory
            if workflow_id in self._workflow_definitions:
                del self._workflow_definitions[workflow_id]
            
            if workflow_id in self._primitives:
                del self._primitives[workflow_id]
            
            # Remove from persistent storage
            workflow_file = self.storage_path / f"{workflow_id}.json"
            if workflow_file.exists():
                workflow_file.unlink()
            
            self._logger.info(f"Unregistered workflow: {workflow_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error unregistering workflow {workflow_id}: {e}")
            return False
    
    def register_primitive(self, primitive_type: str, primitive_class: Type[InstitutionalPrimitive]) -> bool:
        """
        Register a primitive type with the registry.
        
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
        """
        Get a primitive class by type.
        
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
        """
        List all registered primitives.
        
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
        """
        Validate a primitive definition.
        
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
        """
        Instantiate a primitive from a definition.
        
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