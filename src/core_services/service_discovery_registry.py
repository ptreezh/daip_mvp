"""@Time    : 2025-08-06 09:45:00
@Author  : DAIP-LIVE Team
@File    : service_discovery_registry.py
@Description:
    Service Discovery Mechanism with Registry
    Provides dynamic service registration, discovery, and health monitoring for DAIP-LIVE services.
"""

import asyncio
import logging
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import aiohttp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""
    UP = "up"
    DOWN = "down"
    STARTING = "starting"
    STOPPING = "stopping"
    UNHEALTHY = "unhealthy"


class RegistrationType(Enum):
    """Service registration types."""
    STATIC = "static"      # Manually registered
    DYNAMIC = "dynamic"    # Auto-discovered
    EXTERNAL = "external"  # External services


@dataclass
class ServiceInstance:
    """Service instance information."""
    instance_id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus
    health_check_url: str
    metadata: dict[str, Any] = field(default_factory=dict)
    registration_type: RegistrationType = RegistrationType.DYNAMIC
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 10  # seconds
    consecutive_failures: int = 0
    max_consecutive_failures: int = 3


@dataclass
class ServiceEndpoint:
    """Service endpoint information."""
    service_name: str
    endpoint_type: str
    url: str
    method: str
    description: str
    version: str = "1.0"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceQuery:
    """Service discovery query."""
    service_name: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    status: Optional[ServiceStatus] = None
    metadata_filter: dict[str, Any] = field(default_factory=dict)
    version_constraint: Optional[str] = None


class ServiceRegistry:
    """Central service registry for DAIP-LIVE."""
    
    def __init__(self):
        self.services: dict[str, list[ServiceInstance]] = {}
        self.endpoints: dict[str, list[ServiceEndpoint]] = {}
        self.service_lock = threading.Lock()
        self.heartbeat_monitor = None
        self.monitoring_active = False
        self.event_subscribers: list[callable] = []
        
        logger.info("Service Registry initialized")
    
    async def start(self):
        """Start the service registry."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.heartbeat_monitor = asyncio.create_task(self._monitor_heartbeats())
        logger.info("Service Registry started")
    
    async def stop(self):
        """Stop the service registry."""
        self.monitoring_active = False
        if self.heartbeat_monitor:
            self.heartbeat_monitor.cancel()
            try:
                await self.heartbeat_monitor
            except asyncio.CancelledError:
                pass
        logger.info("Service Registry stopped")
    
    def register_service(self, instance: ServiceInstance) -> bool:
        """Register a service instance."""
        with self.service_lock:
            service_name = instance.service_name
            
            if service_name not in self.services:
                self.services[service_name] = []
            
            # Check if instance already exists
            existing_instance = next(
                (inst for inst in self.services[service_name] 
                 if inst.instance_id == instance.instance_id), 
                None
            )
            
            if existing_instance:
                # Update existing instance
                self.services[service_name].remove(existing_instance)
                logger.info(f"Updated service instance: {instance.instance_id}")
            else:
                logger.info(f"Registered new service instance: {instance.instance_id}")
            
            self.services[service_name].append(instance)
            
            # Notify subscribers
            self._notify_subscribers("service_registered", {
                "service_name": service_name,
                "instance_id": instance.instance_id,
                "action": "registered"
            })
            
            return True
    
    def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister a service instance."""
        with self.service_lock:
            if service_name not in self.services:
                return False
            
            instances = self.services[service_name]
            instance_to_remove = next(
                (inst for inst in instances if inst.instance_id == instance_id),
                None
            )
            
            if instance_to_remove:
                instances.remove(instance_to_remove)
                
                # Remove service entry if no instances left
                if not instances:
                    del self.services[service_name]
                
                logger.info(f"Deregistered service instance: {instance_id}")
                
                # Notify subscribers
                self._notify_subscribers("service_deregistered", {
                    "service_name": service_name,
                    "instance_id": instance_id,
                    "action": "deregistered"
                })
                
                return True
            
            return False
    
    def register_endpoint(self, endpoint: ServiceEndpoint) -> bool:
        """Register a service endpoint."""
        service_name = endpoint.service_name
        
        if service_name not in self.endpoints:
            self.endpoints[service_name] = []
        
        # Check if endpoint already exists
        existing_endpoint = next(
            (ep for ep in self.endpoints[service_name] 
             if ep.url == endpoint.url and ep.method == endpoint.method), 
            None
        )
        
        if existing_endpoint:
            self.endpoints[service_name].remove(existing_endpoint)
        
        self.endpoints[service_name].append(endpoint)
        logger.info(f"Registered endpoint: {endpoint.method} {endpoint.url}")
        
        return True
    
    def discover_services(self, query: ServiceQuery = None) -> list[ServiceInstance]:
        """Discover services based on query."""
        if query is None:
            query = ServiceQuery()
        
        with self.service_lock:
            results = []
            
            for service_name, instances in self.services.items():
                # Filter by service name
                if query.service_name and service_name != query.service_name:
                    continue
                
                for instance in instances:
                    # Filter by status
                    if query.status and instance.status != query.status:
                        continue
                    
                    # Filter by metadata
                    if query.metadata_filter:
                        match = True
                        for key, value in query.metadata_filter.items():
                            if instance.metadata.get(key) != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    results.append(instance)
            
            return results
    
    def discover_endpoints(self, service_name: str = None, 
                          endpoint_type: str = None,
                          tags: list[str] = None) -> list[ServiceEndpoint]:
        """Discover service endpoints."""
        results = []
        
        for svc_name, endpoints in self.endpoints.items():
            if service_name and svc_name != service_name:
                continue
            
            for endpoint in endpoints:
                if endpoint_type and endpoint.endpoint_type != endpoint_type:
                    continue
                
                if tags:
                    if not all(tag in endpoint.tags for tag in tags):
                        continue
                
                results.append(endpoint)
        
        return results
    
    def get_service_instances(self, service_name: str) -> list[ServiceInstance]:
        """Get all instances of a specific service."""
        with self.service_lock:
            return self.services.get(service_name, []).copy()
    
    def get_service_endpoints(self, service_name: str) -> list[ServiceEndpoint]:
        """Get all endpoints of a specific service."""
        return self.endpoints.get(service_name, []).copy()
    
    async def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """Receive heartbeat from service instance."""
        with self.service_lock:
            if service_name not in self.services:
                return False
            
            instance = next(
                (inst for inst in self.services[service_name] 
                 if inst.instance_id == instance_id),
                None
            )
            
            if instance:
                instance.last_heartbeat = datetime.now()
                instance.consecutive_failures = 0
                
                # Update status if it was down
                if instance.status == ServiceStatus.DOWN:
                    instance.status = ServiceStatus.UP
                    self._notify_subscribers("service_up", {
                        "service_name": service_name,
                        "instance_id": instance_id,
                        "action": "recovered"
                    })
                
                return True
            
            return False
    
    def update_service_status(self, service_name: str, instance_id: str, 
                           status: ServiceStatus) -> bool:
        """Update service status."""
        with self.service_lock:
            if service_name not in self.services:
                return False
            
            instance = next(
                (inst for inst in self.services[service_name] 
                 if inst.instance_id == instance_id),
                None
            )
            
            if instance:
                old_status = instance.status
                instance.status = status
                
                if old_status != status:
                    self._notify_subscribers("status_changed", {
                        "service_name": service_name,
                        "instance_id": instance_id,
                        "old_status": old_status.value,
                        "new_status": status.value,
                        "action": "status_changed"
                    })
                
                return True
            
            return False
    
    def get_registry_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        with self.service_lock:
            total_services = len(self.services)
            total_instances = sum(len(instances) for instances in self.services.values())
            total_endpoints = sum(len(endpoints) for endpoints in self.endpoints.values())
            
            status_counts = {}
            for instances in self.services.values():
                for instance in instances:
                    status = instance.status.value
                    status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total_services": total_services,
                "total_instances": total_instances,
                "total_endpoints": total_endpoints,
                "service_status_counts": status_counts,
                "monitoring_active": self.monitoring_active,
                "last_updated": datetime.now().isoformat()
            }
    
    def subscribe_to_events(self, callback: callable):
        """Subscribe to registry events."""
        self.event_subscribers.append(callback)
    
    def _notify_subscribers(self, event_type: str, data: dict[str, Any]):
        """Notify subscribers of registry events."""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        for callback in self.event_subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    async def _monitor_heartbeats(self):
        """Monitor service heartbeats and detect failures."""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                instances_to_check = []
                
                with self.service_lock:
                    for instances in self.services.values():
                        for instance in instances:
                            instances_to_check.append(instance)
                
                # Check heartbeats
                for instance in instances_to_check:
                    time_since_heartbeat = (current_time - instance.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > instance.health_check_interval * 2:
                        instance.consecutive_failures += 1
                        
                        if instance.consecutive_failures >= instance.max_consecutive_failures:
                            old_status = instance.status
                            instance.status = ServiceStatus.DOWN
                            
                            if old_status != ServiceStatus.DOWN:
                                logger.warning(f"Service {instance.service_name} instance {instance.instance_id} marked as DOWN")
                                self._notify_subscribers("service_down", {
                                    "service_name": instance.service_name,
                                    "instance_id": instance.instance_id,
                                    "old_status": old_status.value,
                                    "new_status": ServiceStatus.DOWN.value,
                                    "action": "timeout"
                                })
                
                # Wait for next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitoring: {e}")
                await asyncio.sleep(10)


class ServiceDiscoveryClient:
    """Client for service discovery and registration."""
    
    def __init__(self, registry_url: str = "http://localhost:8003"):
        self.registry_url = registry_url
        self.instance_id = str(uuid.uuid4())
        self.session = None
        self.heartbeat_task = None
    
    async def start(self):
        """Start the discovery client."""
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        """Stop the discovery client."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self.session:
            await self.session.close()
    
    async def register_service(self, service_name: str, host: str, port: int,
                             health_check_url: str = "/health",
                             metadata: dict[str, Any] = None,
                             health_check_interval: int = 30) -> bool:
        """Register a service with the registry."""
        instance = ServiceInstance(
            instance_id=self.instance_id,
            service_name=service_name,
            host=host,
            port=port,
            status=ServiceStatus.UP,
            health_check_url=health_check_url,
            metadata=metadata or {},
            health_check_interval=health_check_interval
        )
        
        try:
            async with self.session.post(
                f"{self.registry_url}/register",
                json=asdict(instance),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            return False
    
    async def deregister_service(self, service_name: str) -> bool:
        """Deregister a service from the registry."""
        try:
            async with self.session.delete(
                f"{self.registry_url}/deregister/{service_name}/{self.instance_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to deregister service: {e}")
            return False
    
    async def discover_service(self, service_name: str) -> list[ServiceInstance]:
        """Discover instances of a service."""
        try:
            async with self.session.get(
                f"{self.registry_url}/discover/{service_name}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return [ServiceInstance(**instance) for instance in data]
                return []
        except Exception as e:
            logger.error(f"Failed to discover service: {e}")
            return []
    
    async def start_heartbeat(self, service_name: str, interval: int = 30):
        """Start sending heartbeats for a service."""
        async def send_heartbeat():
            while True:
                try:
                    async with self.session.post(
                        f"{self.registry_url}/heartbeat/{service_name}/{self.instance_id}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status != 200:
                            logger.warning(f"Heartbeat failed: {response.status}")
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                
                await asyncio.sleep(interval)
        
        self.heartbeat_task = asyncio.create_task(send_heartbeat())


# DAIP-LIVE Service Registry Setup
def create_daip_service_registry():
    """Create and configure DAIP-LIVE service registry."""
    registry = ServiceRegistry()
    
    # Register default DAIP-LIVE services
    default_services = [
        ServiceInstance(
            instance_id="backend_api_001",
            service_name="backend_api",
            host="localhost",
            port=8002,
            status=ServiceStatus.UP,
            health_check_url="/health",
            metadata={
                "version": "1.0.0",
                "description": "DAIP-LIVE Backend API",
                "environment": "development"
            },
            registration_type=RegistrationType.STATIC
        ),
        ServiceInstance(
            instance_id="web_interface_001",
            service_name="web_interface",
            host="localhost",
            port=8001,
            status=ServiceStatus.UP,
            health_check_url="/health",
            metadata={
                "version": "1.0.0",
                "description": "DAIP-LIVE Web Interface",
                "environment": "development"
            },
            registration_type=RegistrationType.STATIC
        ),
        ServiceInstance(
            instance_id="database_001",
            service_name="database",
            host="localhost",
            port=5432,
            status=ServiceStatus.UP,
            health_check_url="/health",
            metadata={
                "version": "13.0",
                "description": "PostgreSQL Database",
                "environment": "development"
            },
            registration_type=RegistrationType.STATIC
        )
    ]
    
    for service in default_services:
        registry.register_service(service)
    
    # Register default endpoints
    default_endpoints = [
        ServiceEndpoint(
            service_name="backend_api",
            endpoint_type="api",
            url="/health",
            method="GET",
            description="Health check endpoint",
            tags=["system", "health"]
        ),
        ServiceEndpoint(
            service_name="backend_api",
            endpoint_type="api",
            url="/scenarios/execute",
            method="POST",
            description="Execute scenario endpoint",
            tags=["scenarios", "execution"]
        ),
        ServiceEndpoint(
            service_name="web_interface",
            endpoint_type="api",
            url="/chat",
            method="POST",
            description="Chat interface endpoint",
            tags=["chat", "interface"]
        )
    ]
    
    for endpoint in default_endpoints:
        registry.register_endpoint(endpoint)
    
    return registry


if __name__ == "__main__":
    # Example usage
    async def main():
        registry = create_daip_service_registry()
        await registry.start()
        
        try:
            # Test service discovery
            query = ServiceQuery(service_name="backend_api")
            services = registry.discover_services(query)
            print(f"Found {len(services)} backend API instances")
            
            # Test endpoint discovery
            endpoints = registry.discover_endpoints(service_name="backend_api")
            print(f"Found {len(endpoints)} backend API endpoints")
            
            # Print registry stats
            stats = registry.get_registry_stats()
            print(f"Registry stats: {stats}")
            
            # Keep running
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            await registry.stop()
    
    asyncio.run(main())