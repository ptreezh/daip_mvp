"""Dependency injection container for the agent engine."""

import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    get_type_hints
)

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ServiceScope(Enum):
    """Service lifecycle scopes."""
    SINGLETON = "singleton"      # One instance for the entire container lifetime
    TRANSIENT = "transient"      # New instance every time
    SCOPED = "scoped"           # One instance per scope (e.g., per session)

T = TypeVar('T')


class ServiceDescriptor(BaseModel):
    """Describes a service registration."""

    service_type: str
    implementation_type: Optional[str] = None
    factory_func: Optional[str] = None
    instance: Optional[str] = None
    scope: ServiceScope = ServiceScope.SINGLETON
    dependencies: List[str] = []
    tags: Set[str] = set()
    lazy: bool = False


class ServiceRegistration:
    """Represents a service registration in the container."""

    def __init__(
        self,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        factory_func: Optional[Callable] = None,
        instance: Optional[Any] = None,
        scope: ServiceScope = ServiceScope.SINGLETON,
        dependencies: Optional[List[Type]] = None,
        tags: Optional[Set[str]] = None,
        lazy: bool = False
    ):
        """
        Initialize service registration.

        Args:
            service_type: The interface/base type being registered
            implementation_type: The concrete implementation type
            factory_func: Factory function to create instances
            instance: Pre-created instance (for SINGLETON scope)
            scope: Service lifecycle scope
            dependencies: List of dependencies this service requires
            tags: Optional tags for categorizing services
            lazy: Whether to create the instance lazily
        """
        self.service_type = service_type
        self.implementation_type = implementation_type
        self.factory_func = factory_func
        self.instance = instance
        self.scope = scope
        self.dependencies = dependencies or []
        self.tags = tags or set()
        self.lazy = lazy

        # Validation and type inference
        if scope == ServiceScope.SINGLETON and instance is None and not lazy:
            # If implementation_type is not provided, assume service_type is the implementation
            if not implementation_type and not factory_func:
                self.implementation_type = service_type

        if scope == ServiceScope.TRANSIENT and instance is not None:
            raise ValueError("Transient services cannot have pre-created instances")

        if implementation_type and factory_func:
            raise ValueError("Cannot specify both implementation_type and factory_func")

    def can_instantiate(self) -> bool:
        """Check if this registration can create instances."""
        return (
            self.instance is not None or
            self.implementation_type is not None or
            self.factory_func is not None
        )


class ServiceScopeContext:
    """Service scope context for scoped services."""

    def __init__(self, scope_id: Optional[str] = None):
        """
        Initialize service scope.

        Args:
            scope_id: Unique identifier for this scope
        """
        self.scope_id = scope_id or f"scope_{id(self)}"
        self._instances: Dict[Type, Any] = {}
        self._disposed = False

    def get_instance(self, service_type: Type) -> Optional[Any]:
        """Get instance from scope."""
        if self._disposed:
            raise RuntimeError("Scope has been disposed")
        return self._instances.get(service_type)

    def set_instance(self, service_type: Type, instance: Any) -> None:
        """Set instance in scope."""
        if self._disposed:
            raise RuntimeError("Scope has been disposed")
        self._instances[service_type] = instance

    def dispose(self) -> None:
        """Dispose the scope and cleanup instances."""
        if self._disposed:
            return

        # Dispose instances that implement IDisposable
        for instance in self._instances.values():
            if hasattr(instance, 'dispose'):
                try:
                    if asyncio.iscoroutinefunction(instance.dispose):
                        # For async dispose, we can't await here
                        # In a real implementation, you'd want to handle this better
                        logger.warning(f"Async dispose not supported in scope cleanup for {instance}")
                    else:
                        instance.dispose()
                except Exception as e:
                    logger.error(f"Error disposing instance {instance}: {e}")

        self._instances.clear()
        self._disposed = True


class ServiceContainer:
    """
    Dependency injection container with lifecycle management and cycle detection.

    This container provides:
    - Service registration and resolution
    - Lifecycle management (Singleton, Transient, Scoped)
    - Dependency injection with automatic constructor injection
    - Circular dependency detection
    - Service health checking
    - Lazy loading support
    """

    def __init__(self):
        """Initialize the service container."""
        self._registrations: Dict[Type, ServiceRegistration] = {}
        self._singleton_instances: Dict[Type, Any] = {}
        self._scopes: Dict[str, ServiceScopeContext] = {}
        self._dependency_graph: Dict[Type, Set[Type]] = {}
        self._resolving_stack: List[Type] = []
        self._started = False
        self._disposed = False

    def register_singleton(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory_func: Optional[Callable[[], T]] = None,
        instance: Optional[T] = None,
        tags: Optional[Set[str]] = None,
        lazy: bool = False
    ) -> "ServiceContainer":
        """Register a singleton service."""
        registration = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            factory_func=factory_func,
            instance=instance,
            scope=ServiceScope.SINGLETON,
            tags=tags,
            lazy=lazy
        )
        return self._register_service(registration)

    def register_transient(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory_func: Optional[Callable[[], T]] = None,
        tags: Optional[Set[str]] = None
    ) -> "ServiceContainer":
        """Register a transient service."""
        registration = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            factory_func=factory_func,
            scope=ServiceScope.TRANSIENT,
            tags=tags
        )
        return self._register_service(registration)

    def register_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory_func: Optional[Callable[[], T]] = None,
        tags: Optional[Set[str]] = None
    ) -> "ServiceContainer":
        """Register a scoped service."""
        registration = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            factory_func=factory_func,
            scope=ServiceScope.SCOPED,
            tags=tags
        )
        return self._register_service(registration)

    def register_instance(
        self,
        service_type: Type[T],
        instance: T,
        tags: Optional[Set[str]] = None
    ) -> "ServiceContainer":
        """Register a pre-created instance as a singleton."""
        registration = ServiceRegistration(
            service_type=service_type,
            instance=instance,
            scope=ServiceScope.SINGLETON,
            tags=tags
        )
        return self._register_service(registration)

    def _register_service(self, registration: ServiceRegistration) -> "ServiceContainer":
        """Internal method to register a service."""
        if self._disposed:
            raise RuntimeError("Container has been disposed")

        if registration.service_type in self._registrations:
            logger.warning(f"Service {registration.service_type} is being overwritten")

        self._registrations[registration.service_type] = registration

        # Build dependency graph
        dependencies = self._analyze_dependencies(registration)
        self._dependency_graph[registration.service_type] = dependencies

        # Create singleton instance immediately if not lazy
        if (
            registration.scope == ServiceScope.SINGLETON and
            not registration.lazy and
            registration.instance is None
        ):
            try:
                instance = self._create_instance(registration)
                registration.instance = instance
                self._singleton_instances[registration.service_type] = instance
            except Exception as e:
                logger.error(f"Failed to create singleton instance for {registration.service_type}: {e}")
                raise

        logger.debug(f"Registered service {registration.service_type} with scope {registration.scope.value}")
        return self

    def resolve(self, service_type: Type[T], scope_id: Optional[str] = None) -> T:
        """
        Resolve a service instance.

        Args:
            service_type: The type of service to resolve
            scope_id: Optional scope ID for scoped services

        Returns:
            Service instance

        Raises:
            ValueError: If service is not registered
            RuntimeError: If there are circular dependencies
        """
        if self._disposed:
            raise RuntimeError("Container has been disposed")

        if service_type not in self._registrations:
            raise ValueError(f"Service {service_type} is not registered")

        # Check for circular dependencies
        if service_type in self._resolving_stack:
            cycle_path = " -> ".join(str(t) for t in self._resolving_stack + [service_type])
            raise RuntimeError(f"Circular dependency detected: {cycle_path}")

        registration = self._registrations[service_type]

        # Handle different scopes
        if registration.scope == ServiceScope.SINGLETON:
            return self._resolve_singleton(registration)
        elif registration.scope == ServiceScope.TRANSIENT:
            return self._resolve_transient(registration)
        elif registration.scope == ServiceScope.SCOPED:
            return self._resolve_scoped(registration, scope_id)
        else:
            raise ValueError(f"Unknown scope: {registration.scope}")

    def _resolve_singleton(self, registration: ServiceRegistration) -> Any:
        """Resolve a singleton service."""
        if registration.instance is not None:
            return registration.instance

        if registration.service_type in self._singleton_instances:
            return self._singleton_instances[registration.service_type]

        # Create new singleton instance
        instance = self._create_instance(registration)
        registration.instance = instance
        self._singleton_instances[registration.service_type] = instance

        return instance

    def _resolve_transient(self, registration: ServiceRegistration) -> Any:
        """Resolve a transient service."""
        return self._create_instance(registration)

    def _resolve_scoped(self, registration: ServiceRegistration, scope_id: Optional[str]) -> Any:
        """Resolve a scoped service."""
        if scope_id is None:
            raise ValueError("Scope ID is required for scoped services")

        scope = self._scopes.get(scope_id)
        if scope is None:
            scope = ServiceScopeContext(scope_id)
            self._scopes[scope_id] = scope

        # Check if instance already exists in scope
        instance = scope.get_instance(registration.service_type)
        if instance is not None:
            return instance

        # Create new instance for scope
        instance = self._create_instance(registration)
        scope.set_instance(registration.service_type, instance)

        return instance

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create a new instance of a service."""
        self._resolving_stack.append(registration.service_type)

        try:
            if registration.factory_func:
                return self._create_with_factory(registration.factory_func)
            elif registration.implementation_type:
                return self._create_with_constructor(registration.implementation_type)
            else:
                raise ValueError(f"No way to create instance for {registration.service_type}")
        finally:
            self._resolving_stack.pop()

    def _create_with_factory(self, factory_func: Callable) -> Any:
        """Create instance using factory function."""
        # Analyze factory dependencies
        sig = inspect.signature(factory_func)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            # Only inject dependencies for registered services
            if (param.annotation != inspect.Parameter.empty and
                param.annotation in self._registrations):
                dependency = self.resolve(param.annotation)
                kwargs[param_name] = dependency

            # Handle parameters with default values that aren't dependencies
            elif param.default != inspect.Parameter.empty:
                # Skip - will use default value
                continue

            # Handle required parameters that aren't registered services
            elif param.default == inspect.Parameter.empty:
                raise ValueError(
                    f"Cannot create instance using factory {factory_func.__name__}: "
                    f"Required parameter '{param_name}' of type {param.annotation} "
                    f"is not registered as a service"
                )

        return factory_func(**kwargs)

    def _create_with_constructor(self, implementation_type: Type) -> Any:
        """Create instance using constructor injection."""
        sig = inspect.signature(implementation_type.__init__)
        args = []
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            # Only inject dependencies for registered services
            if (param.annotation != inspect.Parameter.empty and
                param.annotation in self._registrations):
                dependency = self.resolve(param.annotation)

                if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                    args.append(dependency)
                else:
                    kwargs[param_name] = dependency

            # Handle parameters with default values that aren't dependencies
            elif param.default != inspect.Parameter.empty:
                # Skip - will use default value
                continue

            # Handle required parameters that aren't registered services
            elif param.default == inspect.Parameter.empty:
                # For parameters without defaults that aren't registered,
                # we can't create the instance
                raise ValueError(
                    f"Cannot create instance of {implementation_type.__name__}: "
                    f"Required parameter '{param_name}' of type {param.annotation} "
                    f"is not registered as a service"
                )

        return implementation_type(*args, **kwargs)

    def _analyze_dependencies(self, registration: ServiceRegistration) -> Set[Type]:
        """Analyze dependencies of a service registration."""
        dependencies = set()

        if registration.factory_func:
            sig = inspect.signature(registration.factory_func)
            for param in sig.parameters.values():
                if param.annotation != inspect.Parameter.empty:
                    dependencies.add(param.annotation)

        elif registration.implementation_type:
            sig = inspect.signature(registration.implementation_type.__init__)
            for param in sig.parameters.values():
                if param.name != 'self' and param.annotation != inspect.Parameter.empty:
                    dependencies.add(param.annotation)

        registration.dependencies = list(dependencies)
        return dependencies

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._registrations

    def get_registrations(self, tag: Optional[str] = None) -> List[ServiceRegistration]:
        """Get all registrations, optionally filtered by tag."""
        registrations = list(self._registrations.values())

        if tag:
            registrations = [r for r in registrations if tag in r.tags]

        return registrations

    def create_scope(self, scope_id: Optional[str] = None) -> str:
        """Create a new service scope and return its ID."""
        if scope_id is None:
            scope_id = f"scope_{len(self._scopes)}_{id(self)}"

        if scope_id in self._scopes:
            raise ValueError(f"Scope with ID '{scope_id}' already exists")

        self._scopes[scope_id] = ServiceScopeContext(scope_id)
        return scope_id

    def dispose_scope(self, scope_id: str) -> None:
        """Dispose a service scope."""
        if scope_id in self._scopes:
            self._scopes[scope_id].dispose()
            del self._scopes[scope_id]

    def check_circular_dependencies(self) -> List[List[Type]]:
        """
        Check for circular dependencies in registered services.

        Returns:
            List of dependency cycles found
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(service_type: Type, path: List[Type]) -> None:
            if service_type in rec_stack:
                # Found a cycle
                cycle_start = path.index(service_type)
                cycle = path[cycle_start:] + [service_type]
                cycles.append(cycle)
                return

            if service_type in visited:
                return

            visited.add(service_type)
            rec_stack.add(service_type)

            dependencies = self._dependency_graph.get(service_type, set())
            for dep in dependencies:
                if dep in self._registrations:  # Only check registered dependencies
                    dfs(dep, path + [service_type])

            rec_stack.remove(service_type)

        for service_type in self._registrations:
            if service_type not in visited:
                dfs(service_type, [])

        return cycles

    async def start(self) -> None:
        """Start the container and initialize non-lazy singletons."""
        if self._started:
            return

        self._started = True

        # Check for circular dependencies
        cycles = self.check_circular_dependencies()
        if cycles:
            cycle_strs = [" -> ".join(str(t) for t in cycle) for cycle in cycles]
            raise RuntimeError(f"Circular dependencies detected: {'; '.join(cycle_strs)}")

        # Initialize remaining singleton instances
        for service_type, registration in self._registrations.items():
            if (
                registration.scope == ServiceScope.SINGLETON and
                registration.instance is None and
                not registration.lazy
            ):
                try:
                    instance = self._create_instance(registration)
                    registration.instance = instance
                    self._singleton_instances[service_type] = instance
                    logger.debug(f"Initialized singleton service: {service_type}")
                except Exception as e:
                    logger.error(f"Failed to initialize singleton service {service_type}: {e}")
                    raise

        logger.info("ServiceContainer started")

    async def stop(self) -> None:
        """Stop the container and dispose all services."""
        if not self._started:
            return

        self._started = False

        # Dispose all scopes
        for scope_id in list(self._scopes.keys()):
            self.dispose_scope(scope_id)

        # Dispose singleton instances
        for service_type, instance in self._singleton_instances.items():
            if hasattr(instance, 'dispose'):
                try:
                    if asyncio.iscoroutinefunction(instance.dispose):
                        await instance.dispose()
                    else:
                        instance.dispose()
                    logger.debug(f"Disposed singleton service: {service_type}")
                except Exception as e:
                    logger.error(f"Error disposing singleton service {service_type}: {e}")

        self._singleton_instances.clear()
        logger.info("ServiceContainer stopped")

    def dispose(self) -> None:
        """Dispose the container synchronously."""
        if self._disposed:
            return

        self._disposed = True

        # Dispose scopes
        for scope_id in list(self._scopes.keys()):
            self.dispose_scope(scope_id)

        # Dispose singleton instances
        for service_type, instance in self._singleton_instances.items():
            if hasattr(instance, 'dispose'):
                try:
                    instance.dispose()
                    logger.debug(f"Disposed singleton service: {service_type}")
                except Exception as e:
                    logger.error(f"Error disposing singleton service {service_type}: {e}")

        self._singleton_instances.clear()
        self._registrations.clear()
        self._dependency_graph.clear()

        logger.info("ServiceContainer disposed")

    def get_container_info(self) -> Dict[str, Any]:
        """Get information about the container state."""
        return {
            "started": self._started,
            "disposed": self._disposed,
            "total_registrations": len(self._registrations),
            "singleton_instances": len(self._singleton_instances),
            "active_scopes": len(self._scopes),
            "services_by_scope": {
                scope.value: len([r for r in self._registrations.values() if r.scope == scope])
                for scope in ServiceScope
            },
            "circular_dependencies": self.check_circular_dependencies(),
        }


class ContainerBuilder:
    """Builder pattern for configuring ServiceContainer."""

    def __init__(self):
        """Initialize the container builder."""
        self._registrations: List[Callable[[ServiceContainer], None]] = []

    def add_singleton(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory_func: Optional[Callable[[], T]] = None,
        instance: Optional[T] = None,
        tags: Optional[Set[str]] = None,
        lazy: bool = False
    ) -> "ContainerBuilder":
        """Add a singleton service registration."""
        def register(container: ServiceContainer):
            container.register_singleton(
                service_type, implementation_type, factory_func, instance, tags, lazy
            )
        self._registrations.append(register)
        return self

    def add_transient(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory_func: Optional[Callable[[], T]] = None,
        tags: Optional[Set[str]] = None
    ) -> "ContainerBuilder":
        """Add a transient service registration."""
        def register(container: ServiceContainer):
            container.register_transient(service_type, implementation_type, factory_func, tags)
        self._registrations.append(register)
        return self

    def add_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory_func: Optional[Callable[[], T]] = None,
        tags: Optional[Set[str]] = None
    ) -> "ContainerBuilder":
        """Add a scoped service registration."""
        def register(container: ServiceContainer):
            container.register_scoped(service_type, implementation_type, factory_func, tags)
        self._registrations.append(register)
        return self

    def add_instance(
        self,
        service_type: Type[T],
        instance: T,
        tags: Optional[Set[str]] = None
    ) -> "ContainerBuilder":
        """Add an instance registration."""
        def register(container: ServiceContainer):
            container.register_instance(service_type, instance, tags)
        self._registrations.append(register)
        return self

    def build(self) -> ServiceContainer:
        """Build and return a configured ServiceContainer."""
        container = ServiceContainer()
        for register_func in self._registrations:
            register_func(container)
        return container