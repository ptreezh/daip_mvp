"""@Time    : 2025-07-25 05:00:00
@Author  : DAIP-LIVE Team
@File    : service_adapters.py
@Description:
    Service adapter registration system for external service integration.
    Implements requirement 7.3 - standardized adapters for external services.
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Types of services that can be adapted."""
    FACT_SOURCE = "fact_source"
    VALIDATION_SERVICE = "validation_service"
    SYNTHESIS_ENGINE = "synthesis_engine"
    KNOWLEDGE_BASE = "knowledge_base"
    LLM_PROVIDER = "llm_provider"
    TOOL_EXECUTOR = "tool_executor"
    MEMORY_STORE = "memory_store"
    NOTIFICATION_SERVICE = "notification_service"
    CUSTOM = "custom"


class AdapterCapability(str, Enum):
    """Capabilities that adapters can provide."""
    READ = "read"
    WRITE = "write"
    QUERY = "query"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    NOTIFY = "notify"
    EXECUTE = "execute"
    STREAM = "stream"


class ServiceAdapterMetadata(BaseModel):
    """Metadata for a service adapter."""
    name: str
    version: str
    service_type: ServiceType
    capabilities: list[AdapterCapability]
    description: str
    author: str
    created_at: datetime = Field(default_factory=datetime.now)
    dependencies: list[str] = Field(default_factory=list)
    configuration_schema: dict[str, Any] = Field(default_factory=dict)


class AdapterConfiguration(BaseModel):
    """Configuration for a service adapter instance."""
    adapter_name: str
    instance_id: str
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ServiceRequest(BaseModel):
    """Request to a service through an adapter."""
    request_id: str
    operation: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class ServiceResponse(BaseModel):
    """Response from a service through an adapter."""
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_ms: Optional[float] = None


class ServiceAdapter(ABC):
    """Abstract base class for service adapters.
    
    Service adapters provide standardized interfaces for integrating
    external services with the institutional primitives system.
    """
    
    def __init__(self, instance_id: str, config: AdapterConfiguration):
        """Initialize the service adapter.
        
        Args:
            instance_id: Unique identifier for this adapter instance
            config: Configuration for the adapter
        """
        self.instance_id = instance_id
        self.config = config
        self.is_initialized = False
        self.last_health_check = None
        
    @abstractmethod
    def get_metadata(self) -> ServiceAdapterMetadata:
        """Return metadata about this adapter."""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the adapter and establish connections.
        
        Returns:
            True if initialization was successful
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources and close connections."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the adapter and underlying service are healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def execute_request(self, request: ServiceRequest) -> ServiceResponse:
        """Execute a request through this adapter.
        
        Args:
            request: Service request to execute
            
        Returns:
            Service response
        """
        pass
    
    def supports_capability(self, capability: AdapterCapability) -> bool:
        """Check if this adapter supports a specific capability."""
        metadata = self.get_metadata()
        return capability in metadata.capabilities
    
    def validate_configuration(self, config: dict[str, Any]) -> list[str]:
        """Validate adapter configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        metadata = self.get_metadata()
        schema = metadata.configuration_schema
        
        # Basic validation - in a real implementation, this would use JSON schema
        for required_field in schema.get("required", []):
            if required_field not in config:
                errors.append(f"Required configuration field missing: {required_field}")
        
        return errors


class FactSourceAdapter(ServiceAdapter):
    """Adapter for fact source services."""
    
    async def query_facts(self, query: str, filters: dict[str, Any] = None) -> list[dict[str, Any]]:
        """Query facts from the source."""
        request = ServiceRequest(
            request_id=f"fact_query_{datetime.now().timestamp()}",
            operation="query_facts",
            parameters={"query": query, "filters": filters or {}}
        )
        
        response = await self.execute_request(request)
        if response.success:
            return response.data or []
        else:
            logger.error(f"Fact query failed: {response.error}")
            return []
    
    async def validate_fact(self, fact: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Validate a fact using the source."""
        request = ServiceRequest(
            request_id=f"fact_validation_{datetime.now().timestamp()}",
            operation="validate_fact",
            parameters={"fact": fact, "context": context or {}}
        )
        
        response = await self.execute_request(request)
        if response.success:
            return response.data or {}
        else:
            logger.error(f"Fact validation failed: {response.error}")
            return {"valid": False, "error": response.error}


class ValidationServiceAdapter(ServiceAdapter):
    """Adapter for validation services."""
    
    async def validate_content(self, content: str, validation_type: str, criteria: dict[str, Any] = None) -> dict[str, Any]:
        """Validate content using the service."""
        request = ServiceRequest(
            request_id=f"content_validation_{datetime.now().timestamp()}",
            operation="validate_content",
            parameters={
                "content": content,
                "validation_type": validation_type,
                "criteria": criteria or {}
            }
        )
        
        response = await self.execute_request(request)
        if response.success:
            return response.data or {}
        else:
            logger.error(f"Content validation failed: {response.error}")
            return {"valid": False, "error": response.error}


class SynthesisEngineAdapter(ServiceAdapter):
    """Adapter for synthesis engine services."""
    
    async def synthesize_content(self, inputs: list[str], synthesis_strategy: str, parameters: dict[str, Any] = None) -> dict[str, Any]:
        """Synthesize content from multiple inputs."""
        request = ServiceRequest(
            request_id=f"synthesis_{datetime.now().timestamp()}",
            operation="synthesize_content",
            parameters={
                "inputs": inputs,
                "strategy": synthesis_strategy,
                "parameters": parameters or {}
            }
        )
        
        response = await self.execute_request(request)
        if response.success:
            return response.data or {}
        else:
            logger.error(f"Content synthesis failed: {response.error}")
            return {"success": False, "error": response.error}


class ServiceAdapterRegistry:
    """Registry for service adapters.
    
    This class manages the registration, configuration, and lifecycle
    of service adapters.
    """
    
    def __init__(self):
        """Initialize the service adapter registry."""
        self.adapter_classes: dict[str, type[ServiceAdapter]] = {}
        self.adapter_instances: dict[str, ServiceAdapter] = {}
        self.configurations: dict[str, AdapterConfiguration] = {}
        
        logger.info("ServiceAdapterRegistry initialized")
    
    def register_adapter_class(self, adapter_name: str, adapter_class: type[ServiceAdapter]) -> bool:
        """Register a service adapter class.
        
        Args:
            adapter_name: Name of the adapter
            adapter_class: Adapter class to register
            
        Returns:
            True if registration was successful
        """
        if adapter_name in self.adapter_classes:
            logger.warning(f"Adapter class '{adapter_name}' already registered. Overwriting.")
        
        self.adapter_classes[adapter_name] = adapter_class
        logger.info(f"Registered adapter class: {adapter_name}")
        return True
    
    def create_adapter_instance(self, adapter_name: str, instance_id: str, config: dict[str, Any]) -> Optional[ServiceAdapter]:
        """Create an instance of a service adapter.
        
        Args:
            adapter_name: Name of the adapter class
            instance_id: Unique ID for the instance
            config: Configuration for the adapter
            
        Returns:
            Created adapter instance, or None if creation failed
        """
        if adapter_name not in self.adapter_classes:
            logger.error(f"Adapter class '{adapter_name}' not found")
            return None
        
        if instance_id in self.adapter_instances:
            logger.error(f"Adapter instance '{instance_id}' already exists")
            return None
        
        try:
            adapter_class = self.adapter_classes[adapter_name]
            adapter_config = AdapterConfiguration(
                adapter_name=adapter_name,
                instance_id=instance_id,
                config=config
            )
            
            # Validate configuration
            temp_instance = adapter_class(instance_id, adapter_config)
            validation_errors = temp_instance.validate_configuration(config)
            if validation_errors:
                logger.error(f"Adapter configuration validation failed: {validation_errors}")
                return None
            
            # Create the actual instance
            instance = adapter_class(instance_id, adapter_config)
            
            # Store configuration and instance
            self.configurations[instance_id] = adapter_config
            self.adapter_instances[instance_id] = instance
            
            logger.info(f"Created adapter instance: {instance_id}")
            return instance
            
        except Exception as e:
            logger.error(f"Error creating adapter instance '{instance_id}': {e}")
            return None
    
    async def initialize_adapter(self, instance_id: str) -> bool:
        """Initialize a service adapter instance.
        
        Args:
            instance_id: ID of the adapter instance
            
        Returns:
            True if initialization was successful
        """
        if instance_id not in self.adapter_instances:
            logger.error(f"Adapter instance '{instance_id}' not found")
            return False
        
        try:
            adapter = self.adapter_instances[instance_id]
            success = await adapter.initialize()
            
            if success:
                adapter.is_initialized = True
                logger.info(f"Initialized adapter instance: {instance_id}")
            else:
                logger.error(f"Failed to initialize adapter instance: {instance_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing adapter '{instance_id}': {e}")
            return False
    
    async def cleanup_adapter(self, instance_id: str) -> bool:
        """Clean up a service adapter instance.
        
        Args:
            instance_id: ID of the adapter instance
            
        Returns:
            True if cleanup was successful
        """
        if instance_id not in self.adapter_instances:
            logger.error(f"Adapter instance '{instance_id}' not found")
            return False
        
        try:
            adapter = self.adapter_instances[instance_id]
            await adapter.cleanup()
            
            # Remove from registry
            del self.adapter_instances[instance_id]
            del self.configurations[instance_id]
            
            logger.info(f"Cleaned up adapter instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up adapter '{instance_id}': {e}")
            return False
    
    def get_adapter_instance(self, instance_id: str) -> Optional[ServiceAdapter]:
        """Get an adapter instance by ID."""
        return self.adapter_instances.get(instance_id)
    
    def list_adapter_classes(self) -> list[str]:
        """List all registered adapter classes."""
        return list(self.adapter_classes.keys())
    
    def list_adapter_instances(self) -> list[str]:
        """List all created adapter instances."""
        return list(self.adapter_instances.keys())
    
    def get_adapters_by_type(self, service_type: ServiceType) -> list[ServiceAdapter]:
        """Get all adapter instances of a specific service type."""
        result = []
        for adapter in self.adapter_instances.values():
            metadata = adapter.get_metadata()
            if metadata.service_type == service_type:
                result.append(adapter)
        return result
    
    def get_adapters_by_capability(self, capability: AdapterCapability) -> list[ServiceAdapter]:
        """Get all adapter instances that support a specific capability."""
        result = []
        for adapter in self.adapter_instances.values():
            if adapter.supports_capability(capability):
                result.append(adapter)
        return result
    
    async def health_check_all(self) -> dict[str, bool]:
        """Perform health checks on all adapter instances."""
        results = {}
        
        for instance_id, adapter in self.adapter_instances.items():
            try:
                is_healthy = await adapter.health_check()
                results[instance_id] = is_healthy
                adapter.last_health_check = datetime.now()
            except Exception as e:
                logger.error(f"Health check failed for adapter '{instance_id}': {e}")
                results[instance_id] = False
        
        return results
    
    def get_adapter_info(self, instance_id: str) -> Optional[dict[str, Any]]:
        """Get detailed information about an adapter instance."""
        if instance_id not in self.adapter_instances:
            return None
        
        adapter = self.adapter_instances[instance_id]
        config = self.configurations[instance_id]
        metadata = adapter.get_metadata()
        
        return {
            "instance_id": instance_id,
            "adapter_name": config.adapter_name,
            "metadata": metadata.dict(),
            "configuration": config.dict(),
            "is_initialized": adapter.is_initialized,
            "last_health_check": adapter.last_health_check.isoformat() if adapter.last_health_check else None
        }


class ServiceAdapterManager:
    """High-level manager for service adapters.
    
    This class provides a convenient interface for managing service adapters,
    including automatic discovery, configuration, and lifecycle management.
    """
    
    def __init__(self):
        """Initialize the service adapter manager."""
        self.registry = ServiceAdapterRegistry()
        self.auto_initialize = True
        self.health_check_interval = 300  # 5 minutes
        
        logger.info("ServiceAdapterManager initialized")
    
    def register_standard_adapters(self) -> None:
        """Register standard adapter classes."""
        # Register built-in adapter types
        self.registry.register_adapter_class("fact_source", FactSourceAdapter)
        self.registry.register_adapter_class("validation_service", ValidationServiceAdapter)
        self.registry.register_adapter_class("synthesis_engine", SynthesisEngineAdapter)
        
        logger.info("Registered standard adapter classes")
    
    def register_custom_adapter(self, adapter_name: str, adapter_class: type[ServiceAdapter]) -> bool:
        """Register a custom adapter class."""
        return self.registry.register_adapter_class(adapter_name, adapter_class)
    
    async def create_and_initialize_adapter(self, adapter_name: str, instance_id: str, config: dict[str, Any]) -> Optional[ServiceAdapter]:
        """Create and initialize a service adapter in one step.
        
        Args:
            adapter_name: Name of the adapter class
            instance_id: Unique ID for the instance
            config: Configuration for the adapter
            
        Returns:
            Created and initialized adapter instance
        """
        # Create the adapter
        adapter = self.registry.create_adapter_instance(adapter_name, instance_id, config)
        if not adapter:
            return None
        
        # Initialize if auto-initialize is enabled
        if self.auto_initialize:
            success = await self.registry.initialize_adapter(instance_id)
            if not success:
                # Clean up on initialization failure
                await self.registry.cleanup_adapter(instance_id)
                return None
        
        return adapter
    
    def get_adapter(self, instance_id: str) -> Optional[ServiceAdapter]:
        """Get an adapter instance by ID."""
        return self.registry.get_adapter_instance(instance_id)
    
    def find_adapters(self, service_type: ServiceType = None, capability: AdapterCapability = None) -> list[ServiceAdapter]:
        """Find adapters by type or capability.
        
        Args:
            service_type: Service type to filter by
            capability: Capability to filter by
            
        Returns:
            List of matching adapters
        """
        if service_type:
            return self.registry.get_adapters_by_type(service_type)
        elif capability:
            return self.registry.get_adapters_by_capability(capability)
        else:
            return list(self.registry.adapter_instances.values())
    
    async def execute_service_request(self, instance_id: str, operation: str, parameters: dict[str, Any] = None, context: dict[str, Any] = None) -> ServiceResponse:
        """Execute a service request through an adapter.
        
        Args:
            instance_id: ID of the adapter instance
            operation: Operation to execute
            parameters: Operation parameters
            context: Request context
            
        Returns:
            Service response
        """
        adapter = self.registry.get_adapter_instance(instance_id)
        if not adapter:
            return ServiceResponse(
                request_id=f"error_{datetime.now().timestamp()}",
                success=False,
                error=f"Adapter instance '{instance_id}' not found"
            )
        
        request = ServiceRequest(
            request_id=f"request_{datetime.now().timestamp()}",
            operation=operation,
            parameters=parameters or {},
            context=context or {}
        )
        
        return await adapter.execute_request(request)
    
    async def health_check_all(self) -> dict[str, Any]:
        """Perform comprehensive health check on all adapters."""
        health_results = await self.registry.health_check_all()
        
        summary = {
            "total_adapters": len(health_results),
            "healthy_adapters": sum(1 for healthy in health_results.values() if healthy),
            "unhealthy_adapters": sum(1 for healthy in health_results.values() if not healthy),
            "health_check_timestamp": datetime.now().isoformat(),
            "adapter_status": health_results
        }
        
        return summary
    
    def get_system_status(self) -> dict[str, Any]:
        """Get overall status of the service adapter system."""
        return {
            "registered_classes": len(self.registry.adapter_classes),
            "active_instances": len(self.registry.adapter_instances),
            "auto_initialize": self.auto_initialize,
            "health_check_interval": self.health_check_interval,
            "adapter_classes": self.registry.list_adapter_classes(),
            "adapter_instances": self.registry.list_adapter_instances()
        }