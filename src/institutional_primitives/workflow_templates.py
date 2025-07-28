# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 04:30:00
@Author  : DAIP-LIVE Team
@File    : workflow_templates.py
@Description:
    Template-based workflow definition system.
    Implements requirement 7.2 - template-based workflow definition with parameterization.
"""
import logging
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class ParameterType(str, Enum):
    """Types of template parameters."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    ROLE_CONFIG = "role_config"
    THRESHOLD = "threshold"
    STRATEGY = "strategy"


class TemplateParameter(BaseModel):
    """Definition of a template parameter."""
    name: str
    type: ParameterType
    description: str
    default: Optional[Any] = None
    required: bool = True
    constraints: Dict[str, Any] = Field(default_factory=dict)  # min, max, choices, etc.
    
    @validator('default')
    def validate_default(cls, v, values):
        """Validate that default value matches the parameter type."""
        if v is None:
            return v
        
        param_type = values.get('type')
        if param_type == ParameterType.STRING and not isinstance(v, str):
            raise ValueError("Default value must be a string")
        elif param_type == ParameterType.INTEGER and not isinstance(v, int):
            raise ValueError("Default value must be an integer")
        elif param_type == ParameterType.FLOAT and not isinstance(v, (int, float)):
            raise ValueError("Default value must be a number")
        elif param_type == ParameterType.BOOLEAN and not isinstance(v, bool):
            raise ValueError("Default value must be a boolean")
        elif param_type == ParameterType.LIST and not isinstance(v, list):
            raise ValueError("Default value must be a list")
        elif param_type == ParameterType.DICT and not isinstance(v, dict):
            raise ValueError("Default value must be a dictionary")
        
        return v


class WorkflowNode(BaseModel):
    """Definition of a workflow node in a template."""
    id: str
    type: str  # Primitive type
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    conditions: Dict[str, Any] = Field(default_factory=dict)  # Conditional execution
    parallel_group: Optional[str] = None  # For parallel execution grouping


class WorkflowEdge(BaseModel):
    """Definition of a workflow edge in a template."""
    from_node: str
    to_node: str
    condition: Optional[str] = None  # Conditional edge
    data_mapping: Dict[str, str] = Field(default_factory=dict)  # Output -> Input mapping


class WorkflowTemplate(BaseModel):
    """Complete workflow template definition."""
    name: str
    version: str
    description: str
    author: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Template parameters
    parameters: List[TemplateParameter] = Field(default_factory=list)
    
    # Workflow structure
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    category: str = "general"
    use_cases: List[str] = Field(default_factory=list)
    
    def get_parameter(self, name: str) -> Optional[TemplateParameter]:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def validate_structure(self) -> List[str]:
        """Validate the workflow structure and return any errors."""
        errors = []
        
        # Check for duplicate node IDs
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            errors.append("Duplicate node IDs found")
        
        # Check edge references
        for edge in self.edges:
            if not self.get_node(edge.from_node):
                errors.append(f"Edge references unknown from_node: {edge.from_node}")
            if not self.get_node(edge.to_node):
                errors.append(f"Edge references unknown to_node: {edge.to_node}")
        
        # Check for cycles (basic check)
        # In a real implementation, this would be more sophisticated
        
        return errors


class TemplateParameterValues(BaseModel):
    """Values for template parameters."""
    values: Dict[str, Any] = Field(default_factory=dict)
    
    def get(self, name: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self.values.get(name, default)
    
    def set(self, name: str, value: Any) -> None:
        """Set a parameter value."""
        self.values[name] = value


class WorkflowInstance(BaseModel):
    """Instance of a workflow created from a template."""
    instance_id: str
    template_name: str
    template_version: str
    parameter_values: TemplateParameterValues
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Instantiated workflow structure
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    
    # Runtime information
    status: str = "created"  # created, running, completed, failed
    execution_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class TemplateEngine:
    """
    Engine for processing workflow templates and creating instances.
    
    This class handles template parameterization, validation, and instantiation.
    """
    
    def __init__(self):
        """Initialize the template engine."""
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        
        logger.info("TemplateEngine initialized")
    
    def register_template(self, template: WorkflowTemplate) -> bool:
        """
        Register a workflow template.
        
        Args:
            template: Template to register
            
        Returns:
            True if registration was successful
        """
        # Validate template structure
        errors = template.validate_structure()
        if errors:
            logger.error(f"Template validation failed: {errors}")
            return False
        
        template_key = f"{template.name}:{template.version}"
        self.templates[template_key] = template
        
        logger.info(f"Registered template: {template_key}")
        return True
    
    def load_template_from_file(self, file_path: str) -> Optional[WorkflowTemplate]:
        """
        Load a template from a YAML or JSON file.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            Loaded template, or None if loading failed
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Template file not found: {file_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    logger.error(f"Unsupported template file format: {path.suffix}")
                    return None
            
            # Convert string enum values back to enums
            def restore_enums(obj):
                if isinstance(obj, dict):
                    result = {}
                    for k, v in obj.items():
                        if k == 'type' and isinstance(v, str):
                            try:
                                result[k] = ParameterType(v)
                            except ValueError:
                                result[k] = v
                        else:
                            result[k] = restore_enums(v)
                    return result
                elif isinstance(obj, list):
                    return [restore_enums(item) for item in obj]
                else:
                    return obj
            
            restored_data = restore_enums(data)
            template = WorkflowTemplate(**restored_data)
            
            if self.register_template(template):
                return template
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error loading template from {file_path}: {e}")
            return None
    
    def save_template_to_file(self, template: WorkflowTemplate, file_path: str, format: str = "yaml") -> bool:
        """
        Save a template to a file.
        
        Args:
            template: Template to save
            file_path: Path to save the template
            format: File format ("yaml" or "json")
            
        Returns:
            True if saving was successful
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            data = template.dict()
            
            # Convert enums to strings for serialization
            def convert_enums(obj):
                if isinstance(obj, dict):
                    return {k: convert_enums(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_enums(item) for item in obj]
                elif hasattr(obj, 'value'):  # Enum
                    return obj.value
                else:
                    return obj
            
            serializable_data = convert_enums(data)
            
            with open(path, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    yaml.dump(serializable_data, f, default_flow_style=False, indent=2)
                elif format.lower() == "json":
                    json.dump(serializable_data, f, indent=2, default=str)
                else:
                    logger.error(f"Unsupported format: {format}")
                    return False
            
            logger.info(f"Saved template to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving template to {file_path}: {e}")
            return False
    
    def get_template(self, name: str, version: str = None) -> Optional[WorkflowTemplate]:
        """
        Get a template by name and version.
        
        Args:
            name: Template name
            version: Template version (if None, gets the latest)
            
        Returns:
            Template if found, None otherwise
        """
        if version:
            template_key = f"{name}:{version}"
            return self.templates.get(template_key)
        else:
            # Find the latest version
            matching_templates = [
                (key, template) for key, template in self.templates.items()
                if key.startswith(f"{name}:")
            ]
            
            if not matching_templates:
                return None
            
            # Sort by version (simple string sort, could be improved)
            matching_templates.sort(key=lambda x: x[1].version, reverse=True)
            return matching_templates[0][1]
    
    def list_templates(self) -> List[WorkflowTemplate]:
        """List all registered templates."""
        return list(self.templates.values())
    
    def validate_parameters(self, template: WorkflowTemplate, parameter_values: TemplateParameterValues) -> List[str]:
        """
        Validate parameter values against template parameter definitions.
        
        Args:
            template: Template to validate against
            parameter_values: Parameter values to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required parameters
        for param in template.parameters:
            if param.required and param.name not in parameter_values.values:
                if param.default is None:
                    errors.append(f"Required parameter '{param.name}' is missing")
        
        # Validate parameter types and constraints
        for param_name, value in parameter_values.values.items():
            param = template.get_parameter(param_name)
            if not param:
                errors.append(f"Unknown parameter: {param_name}")
                continue
            
            # Type validation
            if param.type == ParameterType.STRING and not isinstance(value, str):
                errors.append(f"Parameter '{param_name}' must be a string")
            elif param.type == ParameterType.INTEGER and not isinstance(value, int):
                errors.append(f"Parameter '{param_name}' must be an integer")
            elif param.type == ParameterType.FLOAT and not isinstance(value, (int, float)):
                errors.append(f"Parameter '{param_name}' must be a number")
            elif param.type == ParameterType.BOOLEAN and not isinstance(value, bool):
                errors.append(f"Parameter '{param_name}' must be a boolean")
            elif param.type == ParameterType.LIST and not isinstance(value, list):
                errors.append(f"Parameter '{param_name}' must be a list")
            elif param.type == ParameterType.DICT and not isinstance(value, dict):
                errors.append(f"Parameter '{param_name}' must be a dictionary")
            
            # Constraint validation
            constraints = param.constraints
            if "min" in constraints and value < constraints["min"]:
                errors.append(f"Parameter '{param_name}' must be >= {constraints['min']}")
            if "max" in constraints and value > constraints["max"]:
                errors.append(f"Parameter '{param_name}' must be <= {constraints['max']}")
            if "choices" in constraints and value not in constraints["choices"]:
                errors.append(f"Parameter '{param_name}' must be one of {constraints['choices']}")
        
        return errors
    
    def instantiate_template(self, template_name: str, parameter_values: TemplateParameterValues, instance_id: str = None, template_version: str = None) -> Optional[WorkflowInstance]:
        """
        Create a workflow instance from a template.
        
        Args:
            template_name: Name of the template to instantiate
            parameter_values: Values for template parameters
            instance_id: Unique ID for the instance (generated if None)
            template_version: Version of template to use (latest if None)
            
        Returns:
            Created workflow instance, or None if creation failed
        """
        # Get the template
        template = self.get_template(template_name, template_version)
        if not template:
            logger.error(f"Template not found: {template_name}:{template_version}")
            return None
        
        # Validate parameters
        validation_errors = self.validate_parameters(template, parameter_values)
        if validation_errors:
            logger.error(f"Parameter validation failed: {validation_errors}")
            return None
        
        # Generate instance ID if not provided
        if not instance_id:
            instance_id = f"{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create parameter values with defaults
        final_parameter_values = TemplateParameterValues()
        
        # Set defaults first
        for param in template.parameters:
            if param.default is not None:
                final_parameter_values.set(param.name, param.default)
        
        # Override with provided values
        for name, value in parameter_values.values.items():
            final_parameter_values.set(name, value)
        
        # Instantiate nodes and edges with parameter substitution
        instantiated_nodes = []
        instantiated_edges = []
        
        for node in template.nodes:
            instantiated_node = self._instantiate_node(node, final_parameter_values)
            instantiated_nodes.append(instantiated_node)
        
        for edge in template.edges:
            instantiated_edge = self._instantiate_edge(edge, final_parameter_values)
            instantiated_edges.append(instantiated_edge)
        
        # Create workflow instance
        instance = WorkflowInstance(
            instance_id=instance_id,
            template_name=template.name,
            template_version=template.version,
            parameter_values=final_parameter_values,
            nodes=instantiated_nodes,
            edges=instantiated_edges
        )
        
        # Store the instance
        self.instances[instance_id] = instance
        
        logger.info(f"Created workflow instance: {instance_id}")
        return instance
    
    def _instantiate_node(self, node: WorkflowNode, parameter_values: TemplateParameterValues) -> WorkflowNode:
        """Instantiate a node with parameter substitution."""
        instantiated_config = self._substitute_parameters(node.config, parameter_values)
        
        return WorkflowNode(
            id=node.id,
            type=node.type,
            config=instantiated_config,
            inputs=node.inputs.copy(),
            outputs=node.outputs.copy(),
            conditions=self._substitute_parameters(node.conditions, parameter_values),
            parallel_group=node.parallel_group
        )
    
    def _instantiate_edge(self, edge: WorkflowEdge, parameter_values: TemplateParameterValues) -> WorkflowEdge:
        """Instantiate an edge with parameter substitution."""
        return WorkflowEdge(
            from_node=edge.from_node,
            to_node=edge.to_node,
            condition=self._substitute_parameter_string(edge.condition, parameter_values) if edge.condition else None,
            data_mapping=edge.data_mapping.copy()
        )
    
    def _substitute_parameters(self, data: Any, parameter_values: TemplateParameterValues) -> Any:
        """Recursively substitute parameters in data structures."""
        if isinstance(data, dict):
            return {key: self._substitute_parameters(value, parameter_values) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_parameters(item, parameter_values) for item in data]
        elif isinstance(data, str):
            return self._substitute_parameter_string(data, parameter_values)
        else:
            return data
    
    def _substitute_parameter_string(self, text: str, parameter_values: TemplateParameterValues) -> str:
        """Substitute parameters in a string using ${param_name} syntax."""
        if not text:
            return text
        
        result = text
        for param_name, param_value in parameter_values.values.items():
            placeholder = f"${{{param_name}}}"
            if placeholder in result:
                # Try to preserve original type if the entire string is just the placeholder
                if result.strip() == placeholder:
                    return param_value
                else:
                    result = result.replace(placeholder, str(param_value))
        
        return result
    
    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get a workflow instance by ID."""
        return self.instances.get(instance_id)
    
    def list_instances(self) -> List[WorkflowInstance]:
        """List all workflow instances."""
        return list(self.instances.values())
    
    def delete_instance(self, instance_id: str) -> bool:
        """Delete a workflow instance."""
        if instance_id in self.instances:
            del self.instances[instance_id]
            logger.info(f"Deleted workflow instance: {instance_id}")
            return True
        return False


class TemplateLibrary:
    """
    Library for managing workflow templates.
    
    This class provides higher-level functionality for template management,
    including categorization, search, and template sharing.
    """
    
    def __init__(self, template_engine: TemplateEngine):
        """
        Initialize the template library.
        
        Args:
            template_engine: Template engine to use
        """
        self.engine = template_engine
        self.template_directories: List[str] = []
        
        logger.info("TemplateLibrary initialized")
    
    def add_template_directory(self, directory: str) -> None:
        """Add a directory to search for templates."""
        if directory not in self.template_directories:
            self.template_directories.append(directory)
            logger.info(f"Added template directory: {directory}")
    
    def discover_templates(self) -> Dict[str, bool]:
        """
        Discover and load templates from registered directories.
        
        Returns:
            Dictionary mapping template files to loading success status
        """
        results = {}
        
        for directory in self.template_directories:
            directory_path = Path(directory)
            if not directory_path.exists():
                logger.warning(f"Template directory not found: {directory}")
                continue
            
            # Find template files
            for file_path in directory_path.glob("*.yaml"):
                template = self.engine.load_template_from_file(str(file_path))
                results[str(file_path)] = template is not None
            
            for file_path in directory_path.glob("*.yml"):
                template = self.engine.load_template_from_file(str(file_path))
                results[str(file_path)] = template is not None
            
            for file_path in directory_path.glob("*.json"):
                template = self.engine.load_template_from_file(str(file_path))
                results[str(file_path)] = template is not None
        
        return results
    
    def search_templates(self, query: str = None, category: str = None, tags: List[str] = None) -> List[WorkflowTemplate]:
        """
        Search templates by various criteria.
        
        Args:
            query: Text query to search in name and description
            category: Template category to filter by
            tags: Tags to filter by
            
        Returns:
            List of matching templates
        """
        templates = self.engine.list_templates()
        results = []
        
        for template in templates:
            # Text query filter
            if query:
                query_lower = query.lower()
                if (query_lower not in template.name.lower() and 
                    query_lower not in template.description.lower()):
                    continue
            
            # Category filter
            if category and template.category != category:
                continue
            
            # Tags filter
            if tags:
                if not any(tag in template.tags for tag in tags):
                    continue
            
            results.append(template)
        
        return results
    
    def get_template_categories(self) -> List[str]:
        """Get all template categories."""
        categories = set()
        for template in self.engine.list_templates():
            categories.add(template.category)
        return sorted(list(categories))
    
    def get_template_tags(self) -> List[str]:
        """Get all template tags."""
        tags = set()
        for template in self.engine.list_templates():
            tags.update(template.tags)
        return sorted(list(tags))
    
    def create_template_from_instance(self, instance: WorkflowInstance, template_name: str, description: str) -> WorkflowTemplate:
        """
        Create a new template from an existing workflow instance.
        
        Args:
            instance: Workflow instance to create template from
            template_name: Name for the new template
            description: Description for the new template
            
        Returns:
            Created template
        """
        # Extract parameters from the instance
        parameters = []
        for param_name, param_value in instance.parameter_values.values.items():
            param_type = ParameterType.STRING  # Default type
            if isinstance(param_value, int):
                param_type = ParameterType.INTEGER
            elif isinstance(param_value, float):
                param_type = ParameterType.FLOAT
            elif isinstance(param_value, bool):
                param_type = ParameterType.BOOLEAN
            elif isinstance(param_value, list):
                param_type = ParameterType.LIST
            elif isinstance(param_value, dict):
                param_type = ParameterType.DICT
            
            parameter = TemplateParameter(
                name=param_name,
                type=param_type,
                description=f"Parameter {param_name}",
                default=param_value,
                required=False
            )
            parameters.append(parameter)
        
        # Create template
        template = WorkflowTemplate(
            name=template_name,
            version="1.0.0",
            description=description,
            author="system",
            parameters=parameters,
            nodes=instance.nodes.copy(),
            edges=instance.edges.copy()
        )
        
        return template