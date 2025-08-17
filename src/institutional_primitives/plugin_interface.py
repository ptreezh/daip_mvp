# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 04:00:00
@Author  : DAIP-LIVE Team
@File    : plugin_interface.py
@Description:
    Plugin interface system for custom primitive creation.
    Implements requirement 7.1 - plugin interfaces for new workflow nodes.
"""
import logging
import importlib
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Callable
from datetime import datetime

from pydantic import BaseModel, Field

from .base import InstitutionalPrimitive, ExecutionContext, PrimitiveInfo, ValidationResult
from .registry import PrimitiveRegistry

logger = logging.getLogger(__name__)


class PluginMetadata(BaseModel):
    """Metadata for a plugin."""
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    primitive_types: List[str] = Field(default_factory=list)
    service_adapters: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class PluginValidationResult(BaseModel):
    """Result of plugin validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Optional[PluginMetadata] = None


class CustomPrimitiveBase(InstitutionalPrimitive):
    """
    Enhanced base class for custom primitives with plugin support.
    
    This class extends the basic InstitutionalPrimitive with additional
    features needed for plugin-based custom primitives.
    """
    
    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.plugin_metadata: Optional[PluginMetadata] = None
        self.service_adapters: Dict[str, Any] = {}
    
    def set_plugin_metadata(self, metadata: PluginMetadata) -> None:
        """Set plugin metadata for this primitive."""
        self.plugin_metadata = metadata
    
    def register_service_adapter(self, service_name: str, adapter: Any) -> None:
        """Register a service adapter for this primitive."""
        self.service_adapters[service_name] = adapter
    
    def get_service_adapter(self, service_name: str) -> Optional[Any]:
        """Get a registered service adapter."""
        return self.service_adapters.get(service_name)
    
    @abstractmethod
    def get_primitive_type(self) -> str:
        """Return the primitive type identifier."""
        pass
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information for this primitive."""
        return {
            "primitive_type": self.get_primitive_type(),
            "plugin_metadata": self.plugin_metadata.dict() if self.plugin_metadata else None,
            "service_adapters": list(self.service_adapters.keys()),
            "base_metadata": self.get_metadata()
        }


class PluginInterface(ABC):
    """
    Abstract interface for plugins that provide custom primitives.
    
    Plugins must implement this interface to be loaded by the plugin system.
    """
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return metadata about this plugin."""
        pass
    
    @abstractmethod
    def get_primitive_classes(self) -> Dict[str, Type[CustomPrimitiveBase]]:
        """Return a dictionary of primitive type -> primitive class mappings."""
        pass
    
    @abstractmethod
    def get_service_adapters(self) -> Dict[str, Any]:
        """Return a dictionary of service name -> adapter mappings."""
        pass
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with the given context.
        
        Args:
            context: Initialization context containing system services
            
        Returns:
            True if initialization was successful
        """
        return True
    
    def cleanup(self) -> None:
        """Clean up resources when the plugin is unloaded."""
        pass


class PluginLoader:
    """
    Loader for plugin-based custom primitives.
    
    This class handles loading, validating, and managing plugins that
    provide custom institutional primitives.
    """
    
    def __init__(self, registry: PrimitiveRegistry):
        """
        Initialize the plugin loader.
        
        Args:
            registry: Primitive registry to register loaded primitives
        """
        self.registry = registry
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.service_adapters: Dict[str, Any] = {}
        
        logger.info("PluginLoader initialized")
    
    def load_plugin_from_module(self, module_path: str) -> PluginValidationResult:
        """
        Load a plugin from a Python module.
        
        Args:
            module_path: Path to the Python module containing the plugin
            
        Returns:
            Result of plugin loading and validation
        """
        logger.info(f"Loading plugin from module: {module_path}")
        
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                return PluginValidationResult(
                    is_valid=False,
                    errors=[f"No plugin classes found in module {module_path}"]
                )
            
            # Use the first plugin class found
            plugin_class = plugin_classes[0]
            plugin_instance = plugin_class()
            
            # Validate the plugin
            validation_result = self._validate_plugin(plugin_instance)
            if not validation_result.is_valid:
                return validation_result
            
            # Register the plugin
            metadata = plugin_instance.get_metadata()
            self._register_plugin(metadata.name, plugin_instance, metadata)
            
            validation_result.metadata = metadata
            logger.info(f"Successfully loaded plugin: {metadata.name}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error loading plugin from {module_path}: {e}")
            return PluginValidationResult(
                is_valid=False,
                errors=[f"Failed to load plugin: {str(e)}"]
            )
    
    def load_plugin_from_file(self, file_path: str) -> PluginValidationResult:
        """
        Load a plugin from a Python file.
        
        Args:
            file_path: Path to the Python file containing the plugin
            
        Returns:
            Result of plugin loading and validation
        """
        logger.info(f"Loading plugin from file: {file_path}")
        
        try:
            # Convert file path to module path
            path = Path(file_path)
            if not path.exists():
                return PluginValidationResult(
                    is_valid=False,
                    errors=[f"Plugin file not found: {file_path}"]
                )
            
            # Load the module from file
            spec = importlib.util.spec_from_file_location("plugin_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                return PluginValidationResult(
                    is_valid=False,
                    errors=[f"No plugin classes found in file {file_path}"]
                )
            
            # Use the first plugin class found
            plugin_class = plugin_classes[0]
            plugin_instance = plugin_class()
            
            # Validate the plugin
            validation_result = self._validate_plugin(plugin_instance)
            if not validation_result.is_valid:
                return validation_result
            
            # Register the plugin
            metadata = plugin_instance.get_metadata()
            self._register_plugin(metadata.name, plugin_instance, metadata)
            
            validation_result.metadata = metadata
            logger.info(f"Successfully loaded plugin: {metadata.name}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error loading plugin from {file_path}: {e}")
            return PluginValidationResult(
                is_valid=False,
                errors=[f"Failed to load plugin: {str(e)}"]
            )
    
    def _validate_plugin(self, plugin: PluginInterface) -> PluginValidationResult:
        """Validate a plugin instance."""
        result = PluginValidationResult(is_valid=True)
        
        try:
            # Validate metadata
            metadata = plugin.get_metadata()
            if not metadata.name:
                result.is_valid = False
                result.errors.append("Plugin metadata missing name")
            
            if not metadata.version:
                result.is_valid = False
                result.errors.append("Plugin metadata missing version")
            
            # Validate primitive classes
            primitive_classes = plugin.get_primitive_classes()
            for primitive_type, primitive_class in primitive_classes.items():
                if not issubclass(primitive_class, CustomPrimitiveBase):
                    result.is_valid = False
                    result.errors.append(
                        f"Primitive class {primitive_class.__name__} must inherit from CustomPrimitiveBase"
                    )
            
            # Validate service adapters
            service_adapters = plugin.get_service_adapters()
            if not isinstance(service_adapters, dict):
                result.warnings.append("Service adapters should be a dictionary")
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Plugin validation error: {str(e)}")
        
        return result
    
    def _register_plugin(self, plugin_name: str, plugin: PluginInterface, metadata: PluginMetadata) -> None:
        """Register a validated plugin."""
        # Store plugin instance and metadata
        self.loaded_plugins[plugin_name] = plugin
        self.plugin_metadata[plugin_name] = metadata
        
        # Initialize the plugin
        context = {
            "registry": self.registry,
            "service_adapters": self.service_adapters
        }
        plugin.initialize(context)
        
        # Register primitive classes
        primitive_classes = plugin.get_primitive_classes()
        for primitive_type, primitive_class in primitive_classes.items():
            self.registry.register_primitive(primitive_type, primitive_class)
            logger.info(f"Registered primitive type '{primitive_type}' from plugin '{plugin_name}'")
        
        # Register service adapters
        service_adapters = plugin.get_service_adapters()
        for service_name, adapter in service_adapters.items():
            self.service_adapters[service_name] = adapter
            logger.info(f"Registered service adapter '{service_name}' from plugin '{plugin_name}'")
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin and clean up its resources.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if unloading was successful
        """
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"Plugin '{plugin_name}' not found")
            return False
        
        try:
            plugin = self.loaded_plugins[plugin_name]
            
            # Clean up the plugin
            plugin.cleanup()
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]
            del self.plugin_metadata[plugin_name]
            
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def list_loaded_plugins(self) -> List[PluginMetadata]:
        """List all loaded plugins."""
        return list(self.plugin_metadata.values())
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a loaded plugin."""
        if plugin_name not in self.loaded_plugins:
            return None
        
        plugin = self.loaded_plugins[plugin_name]
        metadata = self.plugin_metadata[plugin_name]
        
        return {
            "metadata": metadata.dict(),
            "primitive_classes": list(plugin.get_primitive_classes().keys()),
            "service_adapters": list(plugin.get_service_adapters().keys()),
            "status": "loaded"
        }
    
    def get_service_adapter(self, service_name: str) -> Optional[Any]:
        """Get a registered service adapter."""
        return self.service_adapters.get(service_name)
    
    def list_service_adapters(self) -> List[str]:
        """List all registered service adapters."""
        return list(self.service_adapters.keys())


class PluginManager:
    """
    High-level manager for the plugin system.
    
    This class provides a convenient interface for managing plugins,
    including loading, validation, and lifecycle management.
    """
    
    def __init__(self, registry: PrimitiveRegistry):
        """
        Initialize the plugin manager.
        
        Args:
            registry: Primitive registry for registering loaded primitives
        """
        self.registry = registry
        self.loader = PluginLoader(registry)
        self.plugin_directories: List[str] = []
        
        logger.info("PluginManager initialized")
    
    def add_plugin_directory(self, directory: str) -> None:
        """Add a directory to search for plugins."""
        if directory not in self.plugin_directories:
            self.plugin_directories.append(directory)
            logger.info(f"Added plugin directory: {directory}")
    
    def discover_and_load_plugins(self) -> Dict[str, PluginValidationResult]:
        """
        Discover and load all plugins from registered directories.
        
        Returns:
            Dictionary mapping plugin names to their loading results
        """
        results = {}
        
        for directory in self.plugin_directories:
            directory_path = Path(directory)
            if not directory_path.exists():
                logger.warning(f"Plugin directory not found: {directory}")
                continue
            
            # Find Python files in the directory
            for file_path in directory_path.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue  # Skip __init__.py and similar files
                
                result = self.loader.load_plugin_from_file(str(file_path))
                if result.metadata:
                    results[result.metadata.name] = result
                else:
                    results[file_path.name] = result
        
        return results
    
    def load_plugin(self, plugin_path: str) -> PluginValidationResult:
        """
        Load a single plugin from a file or module path.
        
        Args:
            plugin_path: Path to the plugin file or module
            
        Returns:
            Result of plugin loading
        """
        if plugin_path.endswith(".py"):
            return self.loader.load_plugin_from_file(plugin_path)
        else:
            return self.loader.load_plugin_from_module(plugin_path)
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        return self.loader.unload_plugin(plugin_name)
    
    def list_plugins(self) -> List[PluginMetadata]:
        """List all loaded plugins."""
        return self.loader.list_loaded_plugins()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin."""
        return self.loader.get_plugin_info(plugin_name)
    
    def get_service_adapter(self, service_name: str) -> Optional[Any]:
        """Get a service adapter by name."""
        return self.loader.get_service_adapter(service_name)
    
    def create_primitive_instance(self, primitive_type: str, primitive_id: str, config: Dict[str, Any] = None) -> Optional[InstitutionalPrimitive]:
        """
        Create an instance of a primitive type.
        
        Args:
            primitive_type: Type of primitive to create
            primitive_id: Unique ID for the primitive instance
            config: Configuration for the primitive
            
        Returns:
            Created primitive instance, or None if creation failed
        """
        primitive_def = {
            "type": primitive_type,
            "id": primitive_id,
            "config": config or {}
        }
        
        return self.registry.instantiate_primitive(primitive_def)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall status of the plugin system."""
        return {
            "loaded_plugins": len(self.loader.loaded_plugins),
            "registered_primitives": len(self.registry._primitives),
            "service_adapters": len(self.loader.service_adapters),
            "plugin_directories": self.plugin_directories,
            "plugins": [metadata.dict() for metadata in self.list_plugins()]
        }