"""@Time    : 2025-08-06 09:00:00
@Author  : DAIP-LIVE Team
@File    : service_monitoring_system.py
@Description:
    Service Monitoring and Auto-Recovery System
    Provides comprehensive monitoring, health checks, and automatic recovery for DAIP-LIVE services.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import aiohttp
import psutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RESTARTING = "restarting"
    STOPPED = "stopped"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ServiceHealth:
    """Service health information."""
    service_name: str
    status: ServiceStatus
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    metrics: dict[str, Any] = field(default_factory=dict)
    consecutive_failures: int = 0


@dataclass
class ServiceAlert:
    """Service alert information."""
    service_name: str
    alert_level: AlertLevel
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class ServiceConfig:
    """Service configuration."""
    name: str
    health_check_url: str
    port: int
    host: str = "localhost"
    check_interval: int = 30  # seconds
    timeout: int = 10  # seconds
    max_consecutive_failures: int = 3
    restart_command: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)


class ServiceMonitoringSystem:
    """Service monitoring and auto-recovery system."""
    
    def __init__(self):
        self.services: dict[str, ServiceConfig] = {}
        self.health_data: dict[str, ServiceHealth] = {}
        self.alerts: list[ServiceAlert] = []
        self.recovery_actions: dict[str, Callable] = {}
        self.monitoring_active = False
        self.monitoring_task = None
        self.alert_handlers: list[Callable] = []
        
        logger.info("Service Monitoring System initialized")
    
    def register_service(self, config: ServiceConfig):
        """Register a service for monitoring."""
        self.services[config.name] = config
        self.health_data[config.name] = ServiceHealth(
            service_name=config.name,
            status=ServiceStatus.STOPPED,
            response_time=0.0,
            last_check=datetime.now()
        )
        logger.info(f"Service registered for monitoring: {config.name}")
    
    def register_recovery_action(self, service_name: str, action: Callable):
        """Register a custom recovery action for a service."""
        self.recovery_actions[service_name] = action
        logger.info(f"Recovery action registered for service: {service_name}")
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler."""
        self.alert_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start monitoring all registered services."""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Service monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring all services."""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Service monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            tasks = []
            for service_name, config in self.services.items():
                tasks.append(self._check_service_health(service_name, config))
            
            # Check all services concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Wait for next check interval
            await asyncio.sleep(min(config.check_interval for config in self.services.values()))
    
    async def _check_service_health(self, service_name: str, config: ServiceConfig):
        """Check the health of a specific service."""
        try:
            # Check if service dependencies are healthy
            dependencies_healthy = await self._check_dependencies(config.dependencies)
            if not dependencies_healthy:
                health_status = ServiceStatus.DEGRADED
                error_msg = "Dependencies not healthy"
            else:
                # Perform HTTP health check
                health_status, response_time, error_msg = await self._perform_health_check(config)
            
            # Update health data
            old_health = self.health_data[service_name]
            new_health = ServiceHealth(
                service_name=service_name,
                status=health_status,
                response_time=response_time,
                last_check=datetime.now(),
                error_message=error_msg,
                metrics=await self._collect_service_metrics(service_name),
                consecutive_failures=old_health.consecutive_failures + 1 if health_status == ServiceStatus.UNHEALTHY else 0
            )
            
            self.health_data[service_name] = new_health
            
            # Generate alerts for status changes
            if old_health.status != health_status:
                await self._generate_alert(service_name, health_status, error_msg)
            
            # Trigger auto-recovery if needed
            if (new_health.consecutive_failures >= config.max_consecutive_failures and 
                health_status == ServiceStatus.UNHEALTHY):
                await self._trigger_recovery(service_name)
            
            logger.debug(f"Health check completed for {service_name}: {health_status.value}")
            
        except Exception as e:
            logger.error(f"Error checking health for {service_name}: {e}")
            await self._generate_alert(service_name, ServiceStatus.UNHEALTHY, str(e))
    
    async def _check_dependencies(self, dependencies: list[str]) -> bool:
        """Check if service dependencies are healthy."""
        for dep_name in dependencies:
            if dep_name in self.health_data:
                dep_health = self.health_data[dep_name]
                if dep_health.status not in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                    return False
        return True
    
    async def _perform_health_check(self, config: ServiceConfig) -> tuple[ServiceStatus, float, str]:
        """Perform HTTP health check on service."""
        url = f"http://{config.host}:{config.port}{config.health_check_url}"
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=config.timeout)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            if data.get("status") == "healthy":
                                return ServiceStatus.HEALTHY, response_time, ""
                            else:
                                return ServiceStatus.DEGRADED, response_time, f"Service reported: {data.get('status', 'unknown')}"
                        except:
                            return ServiceStatus.HEALTHY, response_time, ""
                    else:
                        return ServiceStatus.UNHEALTHY, response_time, f"HTTP {response.status}"
        
        except asyncio.TimeoutError:
            return ServiceStatus.UNHEALTHY, config.timeout, "Timeout"
        except Exception as e:
            return ServiceStatus.UNHEALTHY, 0.0, str(e)
    
    async def _collect_service_metrics(self, service_name: str) -> dict[str, Any]:
        """Collect metrics for a service."""
        metrics = {}
        
        try:
            # System-level metrics
            process = psutil.Process()
            metrics.update({
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
                "thread_count": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections())
            })
            
            # Service-specific metrics could be added here
            if service_name in self.services:
                config = self.services[service_name]
                metrics.update({
                    "service_uptime": (datetime.now() - self.health_data[service_name].last_check).total_seconds(),
                    "port": config.port,
                    "check_interval": config.check_interval
                })
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {service_name}: {e}")
        
        return metrics
    
    async def _generate_alert(self, service_name: str, status: ServiceStatus, error_message: str):
        """Generate and distribute alerts."""
        alert_level = AlertLevel.INFO
        if status == ServiceStatus.UNHEALTHY:
            alert_level = AlertLevel.ERROR
        elif status == ServiceStatus.DEGRADED:
            alert_level = AlertLevel.WARNING
        
        alert = ServiceAlert(
            service_name=service_name,
            alert_level=alert_level,
            message=f"Service {service_name} status changed to {status.value}: {error_message}",
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
        
        logger.warning(f"Alert generated: {alert.message}")
    
    async def _trigger_recovery(self, service_name: str):
        """Trigger auto-recovery for a service."""
        logger.info(f"Triggering auto-recovery for service: {service_name}")
        
        # Update status to restarting
        self.health_data[service_name].status = ServiceStatus.RESTARTING
        
        try:
            # Try custom recovery action first
            if service_name in self.recovery_actions:
                await self.recovery_actions[service_name]()
            else:
                # Default recovery: restart via command
                await self._restart_service(service_name)
            
            # Wait a bit and check if recovery worked
            await asyncio.sleep(10)
            
            if self.health_data[service_name].status == ServiceStatus.HEALTHY:
                logger.info(f"Auto-recovery successful for service: {service_name}")
                await self._generate_alert(service_name, ServiceStatus.HEALTHY, "Auto-recovery successful")
            else:
                logger.error(f"Auto-recovery failed for service: {service_name}")
                
        except Exception as e:
            logger.error(f"Error during auto-recovery for {service_name}: {e}")
            await self._generate_alert(service_name, ServiceStatus.UNHEALTHY, f"Auto-recovery failed: {e}")
    
    async def _restart_service(self, service_name: str):
        """Restart a service using its restart command."""
        if service_name not in self.services:
            raise ValueError(f"Service not found: {service_name}")
        
        config = self.services[service_name]
        if not config.restart_command:
            raise ValueError(f"No restart command configured for service: {service_name}")
        
        logger.info(f"Restarting service {service_name} with command: {config.restart_command}")
        
        # Execute restart command
        process = await asyncio.create_subprocess_shell(
            config.restart_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Restart command failed: {stderr.decode()}")
        
        logger.info(f"Service {service_name} restart command executed successfully")
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health information for a specific service."""
        return self.health_data.get(service_name)
    
    def get_all_services_health(self) -> dict[str, ServiceHealth]:
        """Get health information for all services."""
        return self.health_data.copy()
    
    def get_alerts(self, service_name: Optional[str] = None, 
                  level: Optional[AlertLevel] = None,
                  resolved: Optional[bool] = None) -> list[ServiceAlert]:
        """Get alerts with optional filtering."""
        alerts = self.alerts.copy()
        
        if service_name:
            alerts = [a for a in alerts if a.service_name == service_name]
        
        if level:
            alerts = [a for a in alerts if a.alert_level == level]
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def resolve_alert(self, alert_id: int):
        """Resolve a specific alert."""
        if 0 <= alert_id < len(self.alerts):
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolution_time = datetime.now()
            logger.info(f"Alert resolved: {self.alerts[alert_id].message}")
    
    def get_system_summary(self) -> dict[str, Any]:
        """Get system monitoring summary."""
        total_services = len(self.services)
        healthy_services = sum(1 for h in self.health_data.values() if h.status == ServiceStatus.HEALTHY)
        degraded_services = sum(1 for h in self.health_data.values() if h.status == ServiceStatus.DEGRADED)
        unhealthy_services = sum(1 for h in self.health_data.values() if h.status == ServiceStatus.UNHEALTHY)
        
        active_alerts = [a for a in self.alerts if not a.resolved]
        critical_alerts = [a for a in active_alerts if a.alert_level == AlertLevel.CRITICAL]
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": degraded_services,
            "unhealthy_services": unhealthy_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "monitoring_active": self.monitoring_active,
            "last_updated": datetime.now().isoformat()
        }


# Example usage and default setup
def create_default_monitoring_system():
    """Create a default monitoring system for DAIP-LIVE services."""
    monitoring = ServiceMonitoringSystem()
    
    # Register DAIP-LIVE services
    services = [
        ServiceConfig(
            name="backend_api",
            health_check_url="/health",
            port=8002,
            check_interval=30,
            restart_command="python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8002"
        ),
        ServiceConfig(
            name="web_interface",
            health_check_url="/health",
            port=8001,
            check_interval=30,
            restart_command="python web_demo_app.py"
        ),
        ServiceConfig(
            name="database",
            health_check_url="/health",
            port=5432,
            check_interval=60,
            dependencies=["backend_api"]
        )
    ]
    
    for service in services:
        monitoring.register_service(service)
    
    return monitoring


# Console alert handler for development
async def console_alert_handler(alert: ServiceAlert):
    """Console alert handler for development."""
    print(f"[{alert.timestamp.isoformat()}] {alert.alert_level.value.upper()}: {alert.message}")


if __name__ == "__main__":
    # Example usage
    async def main():
        monitoring = create_default_monitoring_system()
        monitoring.add_alert_handler(console_alert_handler)
        
        await monitoring.start_monitoring()
        
        try:
            # Keep monitoring running
            while True:
                await asyncio.sleep(60)
                summary = monitoring.get_system_summary()
                print(f"System Health: {summary['health_percentage']:.1f}%")
        except KeyboardInterrupt:
            await monitoring.stop_monitoring()
    
    asyncio.run(main())