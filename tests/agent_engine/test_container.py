"""Tests for the ServiceContainer dependency injection system."""

import pytest
from typing import Optional

from daip_live.agent_engine_v1.container import (
    ServiceContainer,
    ServiceScope,
    ContainerBuilder,
    ServiceRegistration
)


# Test services for dependency injection
class ITestService:
    """Test service interface."""
    def get_value(self) -> str:
        raise NotImplementedError


class TestServiceA(ITestService):
    """Test service implementation."""
    def __init__(self, value: str = "default"):
        self.value = value

    def get_value(self) -> str:
        return self.value


class TestServiceB:
    """Test service with dependencies."""
    def __init__(self, service_a: ITestService):
        self.service_a = service_a

    def get_combined_value(self) -> str:
        return f"B:{self.service_a.get_value()}"


class TestServiceC:
    """Test service with multiple dependencies."""
    def __init__(self, service_a: ITestService, service_b: TestServiceB):
        self.service_a = service_a
        self.service_b = service_b

    def get_value(self) -> str:
        return f"C:{self.service_a.get_value()}:{self.service_b.get_combined_value()}"


class CircularServiceA:
    """Service that creates circular dependency."""
    def __init__(self, service_b: "CircularServiceB"):
        self.service_b = service_b


class CircularServiceB:
    """Service that creates circular dependency."""
    def __init__(self, service_a: CircularServiceA):
        self.service_a = service_a


class DisposableService:
    """Service that can be disposed."""
    def __init__(self, name: str):
        self.name = name
        self.disposed = False

    def dispose(self):
        self.disposed = True

    def __repr__(self):
        return f"DisposableService({self.name}, disposed={self.disposed})"


class TestServiceScope:
    """Test service scope functionality."""
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value


class TestServiceRegistration:
    """Test ServiceRegistration class."""

    def test_singleton_registration(self):
        """Test singleton service registration."""
        registration = ServiceRegistration(
            service_type=ITestService,
            implementation_type=TestServiceA,
            scope=ServiceScope.SINGLETON
        )

        assert registration.service_type == ITestService
        assert registration.implementation_type == TestServiceA
        assert registration.scope == ServiceScope.SINGLETON
        assert registration.can_instantiate()

    def test_transient_registration(self):
        """Test transient service registration."""
        registration = ServiceRegistration(
            service_type=ITestService,
            implementation_type=TestServiceA,
            scope=ServiceScope.TRANSIENT
        )

        assert registration.scope == ServiceScope.TRANSIENT
        assert registration.can_instantiate()

    def test_instance_registration(self):
        """Test instance registration."""
        instance = TestServiceA("test")
        registration = ServiceRegistration(
            service_type=ITestService,
            instance=instance,
            scope=ServiceScope.SINGLETON
        )

        assert registration.instance == instance
        assert registration.can_instantiate()

    def test_factory_registration(self):
        """Test factory function registration."""
        def factory():
            return TestServiceA("from_factory")

        registration = ServiceRegistration(
            service_type=ITestService,
            factory_func=factory,
            scope=ServiceScope.TRANSIENT
        )

        assert registration.factory_func == factory
        assert registration.can_instantiate()

    def test_validation_errors(self):
        """Test registration validation."""
        # Cannot specify both implementation and factory
        with pytest.raises(ValueError):
            ServiceRegistration(
                service_type=ITestService,
                implementation_type=TestServiceA,
                factory_func=lambda: TestServiceA()
            )

        # Transient cannot have instance
        with pytest.raises(ValueError):
            ServiceRegistration(
                service_type=ITestService,
                instance=TestServiceA(),
                scope=ServiceScope.TRANSIENT
            )

        # Must have implementation, factory, or instance
        with pytest.raises(ValueError):
            ServiceRegistration(
                service_type=ITestService,
                scope=ServiceScope.SINGLETON
            )


@pytest.mark.asyncio
class TestServiceContainer:
    """Test ServiceContainer functionality."""

    async def test_register_and_resolve_singleton(self):
        """Test registering and resolving a singleton service."""
        container = ServiceContainer()

        # Register singleton
        container.register_singleton(ITestService, TestServiceA)

        # Resolve service
        service1 = container.resolve(ITestService)
        service2 = container.resolve(ITestService)

        # Should be the same instance
        assert service1 is service2
        assert isinstance(service1, TestServiceA)
        assert service1.get_value() == "default"

    async def test_register_and_resolve_transient(self):
        """Test registering and resolving a transient service."""
        container = ServiceContainer()

        # Register transient
        container.register_transient(ITestService, TestServiceA)

        # Resolve service
        service1 = container.resolve(ITestService)
        service2 = container.resolve(ITestService)

        # Should be different instances
        assert service1 is not service2
        assert isinstance(service1, TestServiceA)
        assert isinstance(service2, TestServiceA)

    async def test_register_and_resolve_scoped(self):
        """Test registering and resolving a scoped service."""
        container = ServiceContainer()

        # Register scoped
        container.register_scoped(TestServiceScope)

        # Create scope and resolve
        scope_id = container.create_scope()
        service1 = container.resolve(TestServiceScope, scope_id)
        service2 = container.resolve(TestServiceScope, scope_id)

        # Should be same instance within scope
        assert service1 is service2

        # Different scope should give different instance
        scope_id2 = container.create_scope()
        service3 = container.resolve(TestServiceScope, scope_id2)
        assert service1 is not service3

        # Cleanup
        container.dispose_scope(scope_id)
        container.dispose_scope(scope_id2)

    async def test_register_instance(self):
        """Test registering a pre-created instance."""
        container = ServiceContainer()
        instance = TestServiceA("pre_created")

        # Register instance
        container.register_instance(ITestService, instance)

        # Resolve service
        resolved = container.resolve(ITestService)

        # Should be the same instance
        assert resolved is instance
        assert resolved.get_value() == "pre_created"

    async def test_register_factory(self):
        """Test registering with factory function."""
        container = ServiceContainer()

        def factory():
            return TestServiceA("from_factory")

        # Register with factory
        container.register_singleton(ITestService, factory_func=factory)

        # Resolve service
        service = container.resolve(ITestService)

        assert isinstance(service, TestServiceA)
        assert service.get_value() == "from_factory"

    async def test_dependency_injection(self):
        """Test constructor dependency injection."""
        container = ServiceContainer()

        # Register services
        container.register_singleton(ITestService, TestServiceA)
        container.register_singleton(TestServiceB)

        # Resolve service with dependency
        service_b = container.resolve(TestServiceB)

        assert isinstance(service_b, TestServiceB)
        assert isinstance(service_b.service_a, TestServiceA)
        assert service_b.get_combined_value() == "B:default"

    async def test_multiple_dependencies(self):
        """Test service with multiple dependencies."""
        container = ServiceContainer()

        # Register services
        container.register_singleton(ITestService, TestServiceA)
        container.register_singleton(TestServiceB)
        container.register_singleton(TestServiceC)

        # Resolve service
        service_c = container.resolve(TestServiceC)

        assert isinstance(service_c, TestServiceC)
        assert isinstance(service_c.service_a, TestServiceA)
        assert isinstance(service_c.service_b, TestServiceB)
        assert service_c.get_value() == "C:default:B:default"

    async def test_factory_with_dependencies(self):
        """Test factory function with dependencies."""
        container = ServiceContainer()

        def factory(service_a: ITestService):
            return TestServiceB(service_a)

        # Register services
        container.register_singleton(ITestService, TestServiceA)
        container.register_singleton(TestServiceB, factory_func=factory)

        # Resolve service
        service_b = container.resolve(TestServiceB)

        assert isinstance(service_b, TestServiceB)
        assert isinstance(service_b.service_a, TestServiceA)

    async def test_lazy_singletons(self):
        """Test lazy singleton initialization."""
        container = ServiceContainer()

        # Register lazy singleton
        container.register_singleton(ITestService, TestServiceA, lazy=True)

        # Service should not be created yet
        assert ITestService not in container._singleton_instances

        # Resolve service
        service = container.resolve(ITestService)

        # Now it should be created
        assert ITestService in container._singleton_instances
        assert isinstance(service, TestServiceA)

    async def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        container = ServiceContainer()

        # Register services with circular dependency
        container.register_singleton(CircularServiceA)
        container.register_singleton(CircularServiceB)

        # Should raise circular dependency error
        with pytest.raises(RuntimeError, match="Circular dependency detected"):
            container.resolve(CircularServiceA)

    async def test_check_circular_dependencies(self):
        """Test explicit circular dependency checking."""
        container = ServiceContainer()

        # Register services with circular dependency
        container.register_singleton(CircularServiceA)
        container.register_singleton(CircularServiceB)

        # Check for circular dependencies
        cycles = container.check_circular_dependencies()
        assert len(cycles) == 1
        assert CircularServiceA in cycles[0]
        assert CircularServiceB in cycles[0]

    async def test_scoped_service_without_scope(self):
        """Test resolving scoped service without scope ID."""
        container = ServiceContainer()
        container.register_scoped(TestServiceScope)

        # Should raise error without scope ID
        with pytest.raises(ValueError, match="Scope ID is required"):
            container.resolve(TestServiceScope)

    async def test_is_registered(self):
        """Test service registration checking."""
        container = ServiceContainer()

        assert not container.is_registered(ITestService)

        container.register_singleton(ITestService, TestServiceA)
        assert container.is_registered(ITestService)

    async def test_get_registrations(self):
        """Test getting service registrations."""
        container = ServiceContainer()

        # Register services with tags
        container.register_singleton(ITestService, TestServiceA, tags={"test", "core"})
        container.register_transient(TestServiceB, tags={"test"})

        # Get all registrations
        all_regs = container.get_registrations()
        assert len(all_regs) == 2

        # Get registrations by tag
        test_regs = container.get_registrations("test")
        assert len(test_regs) == 2

        core_regs = container.get_registrations("core")
        assert len(core_regs) == 1

    async def test_service_disposal(self):
        """Test service disposal."""
        container = ServiceContainer()

        # Register disposable service
        disposable = DisposableService("test")
        container.register_instance(DisposableService, disposable)

        # Dispose container
        container.dispose()

        # Service should be disposed
        assert disposable.disposed

    async def test_scope_disposal(self):
        """Test scope disposal."""
        container = ServiceContainer()
        container.register_scoped(DisposableService)

        # Create scope and service
        scope_id = container.create_scope()
        service = container.resolve(DisposableService, scope_id, "scoped")

        # Dispose scope
        container.dispose_scope(scope_id)

        # Service should be disposed
        assert service.disposed

    async def test_container_lifecycle(self):
        """Test container start/stop lifecycle."""
        container = ServiceContainer()

        # Register non-lazy singleton
        container.register_singleton(ITestService, TestServiceA, lazy=False)

        # Services should not be created yet
        assert ITestService not in container._singleton_instances

        # Start container
        await container.start()

        # Services should be created
        assert ITestService in container._singleton_instances

        # Stop container
        await container.stop()

        assert not container._started

    async def test_resolve_unregistered_service(self):
        """Test resolving unregistered service."""
        container = ServiceContainer()

        with pytest.raises(ValueError, match="is not registered"):
            container.resolve(ITestService)

    async def test_container_info(self):
        """Test container information."""
        container = ServiceContainer()

        container.register_singleton(ITestService, TestServiceA)
        container.register_transient(TestServiceB)
        container.register_scoped(TestServiceScope)

        info = container.get_container_info()

        assert info["total_registrations"] == 3
        assert info["disposed"] is False
        assert info["services_by_scope"]["singleton"] == 1
        assert info["services_by_scope"]["transient"] == 1
        assert info["services_by_scope"]["scoped"] == 1

    async def test_disposed_container_error(self):
        """Test error when using disposed container."""
        container = ServiceContainer()
        container.dispose()

        with pytest.raises(RuntimeError, match="has been disposed"):
            container.register_singleton(ITestService, TestServiceA)

        with pytest.raises(RuntimeError, match="has been disposed"):
            container.resolve(ITestService)


class TestContainerBuilder:
    """Test ContainerBuilder fluent API."""

    def test_builder_pattern(self):
        """Test container builder pattern."""
        builder = ContainerBuilder()

        container = (builder
                    .add_singleton(ITestService, TestServiceA)
                    .add_transient(TestServiceB)
                    .add_scoped(TestServiceScope)
                    .add_instance(DisposableService("test"))
                    .build())

        # Verify registrations
        assert container.is_registered(ITestService)
        assert container.is_registered(TestServiceB)
        assert container.is_registered(TestServiceScope)
        assert container.is_registered(DisposableService)

    def test_builder_with_tags(self):
        """Test builder with service tags."""
        builder = ContainerBuilder()

        container = (builder
                    .add_singleton(ITestService, TestServiceA, tags={"core", "test"})
                    .add_transient(TestServiceB, tags={"test"})
                    .build())

        # Check registrations by tags
        core_regs = container.get_registrations("core")
        assert len(core_regs) == 1

        test_regs = container.get_registrations("test")
        assert len(test_regs) == 2

    def test_builder_lazy_singletons(self):
        """Test builder with lazy singletons."""
        builder = ContainerBuilder()

        container = (builder
                    .add_singleton(ITestService, TestServiceA, lazy=True)
                    .build())

        # Service should not be created yet
        assert ITestService not in container._singleton_instances

        # Resolve service
        service = container.resolve(ITestService)

        # Now it should be created
        assert ITestService in container._singleton_instances
        assert isinstance(service, TestServiceA)