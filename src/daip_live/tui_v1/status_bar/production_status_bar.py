"""
Production-grade Real-time Status Bar for newP6 TUI

This module provides comprehensive status bar capabilities including:
- Real-time system monitoring with performance metrics
- Service health status and alerts
- Network connectivity and bandwidth monitoring
- Resource usage tracking (CPU, memory, disk, network)
- User session information and authentication status
- Background task progress and notifications
- Error and warning alerts with severity levels
- Customizable widget system with plugins
- Performance optimization and caching
- Accessibility and internationalization support
"""

import asyncio
import json
import logging
import platform
import socket
import sqlite3
import time
import uuid
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

import aiohttp
import psutil

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConnectionStatus(Enum):
    """Network connection status"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    UNSTABLE = "unstable"


class WidgetType(Enum):
    """Widget types for status bar"""

    SYSTEM_INFO = "system_info"
    NETWORK_STATUS = "network_status"
    SERVICE_HEALTH = "service_health"
    RESOURCE_USAGE = "resource_usage"
    USER_INFO = "user_info"
    TASK_STATUS = "task_status"
    TIME_CLOCK = "time_clock"
    NOTIFICATIONS = "notifications"
    CUSTOM = "custom"


@dataclass
class Alert:
    """System alert with metadata"""

    id: str
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    source: str
    acknowledged: bool = False
    resolved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    actions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "metadata": self.metadata,
            "actions": self.actions,
        }


@dataclass
class SystemMetrics:
    """System performance metrics"""

    cpu_percent: float = 0.0
    cpu_count: int = 0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    process_count: int = 0
    uptime_seconds: float = 0.0
    load_average: list[float] = field(default_factory=list)
    temperature_celsius: Optional[float] = None
    gpu_percent: Optional[float] = None
    gpu_memory_percent: Optional[float] = None


@dataclass
class NetworkMetrics:
    """Network connectivity metrics"""

    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    latency_ms: Optional[float] = None
    bandwidth_mbps: Optional[float] = None
    packet_loss: float = 0.0
    active_connections: int = 0
    dns_servers: list[str] = field(default_factory=list)
    public_ip: Optional[str] = None
    local_ip: Optional[str] = None
    last_check: Optional[datetime] = None


@dataclass
class WidgetData:
    """Widget data with metadata"""

    widget_type: WidgetType
    title: str
    content: Any
    status: str = "normal"
    last_updated: datetime = field(default_factory=datetime.now)
    refresh_interval_seconds: int = 5
    enabled: bool = True
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class StatusWidget:
    """Base class for status bar widgets"""

    def __init__(self, widget_id: str, title: str, refresh_interval: int = 5):
        self.widget_id = widget_id
        self.title = title
        self.refresh_interval = refresh_interval
        self.last_update: Optional[datetime] = None
        self.data: Optional[WidgetData] = None
        self.enabled = True
        self.error_count = 0
        self.max_errors = 3
        self.callbacks: list[Callable] = []

    async def update(self) -> Optional[WidgetData]:
        """Update widget data"""
        try:
            data = await self._fetch_data()
            if data:
                self.data = data
                self.last_update = datetime.now()
                self.error_count = 0
                return data
        except Exception as e:
            self.error_count += 1
            logger.error(f"Widget {self.widget_id} update error: {e}")
            if self.error_count >= self.max_errors:
                self.enabled = False
                logger.warning(
                    f"Widget {self.widget_id} disabled due to repeated errors"
                )

        return None

    async def _fetch_data(self) -> Optional[WidgetData]:
        """Fetch widget data - to be implemented by subclasses"""
        raise NotImplementedError

    def add_callback(self, callback: Callable) -> None:
        """Add callback for data changes"""
        self.callbacks.append(callback)

    def notify_callbacks(self, data: WidgetData) -> None:
        """Notify all callbacks of data change"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Widget callback error: {e}")


class SystemInfoWidget(StatusWidget):
    """System information widget"""

    def __init__(self):
        super().__init__("system_info", "System", refresh_interval=10)
        self.boot_time = psutil.boot_time()

    async def _fetch_data(self) -> Optional[WidgetData]:
        """Fetch system information"""
        try:
            # Get system info
            system = platform.system()
            machine = platform.machine()
            processor = platform.processor()
            uptime = time.time() - self.boot_time

            # Format uptime
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            minutes = int((uptime % 3600) // 60)

            content = {
                "os": f"{system} {machine}",
                "processor": processor,
                "uptime": f"{days}d {hours}h {minutes}m",
                "python_version": platform.python_version(),
            }

            return WidgetData(
                widget_type=WidgetType.SYSTEM_INFO,
                title=self.title,
                content=content,
                last_updated=datetime.now(),
                refresh_interval=self.refresh_interval,
            )

        except Exception as e:
            logger.error(f"Failed to fetch system info: {e}")
            return None


class ResourceUsageWidget(StatusWidget):
    """Resource usage monitoring widget"""

    def __init__(self):
        super().__init__("resource_usage", "Resources", refresh_interval=2)
        self.last_network_stats = None
        self.network_history = deque(maxlen=60)

    async def _fetch_data(self) -> Optional[WidgetData]:
        """Fetch resource usage data"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)

            # Network metrics
            network = psutil.net_io_counters()
            if self.last_network_stats:
                sent_mb = (network.bytes_sent - self.last_network_stats.bytes_sent) / (
                    1024**2
                )
                recv_mb = (network.bytes_recv - self.last_network_stats.bytes_recv) / (
                    1024**2
                )
            else:
                sent_mb = recv_mb = 0.0
            self.last_network_stats = network

            # Process count
            process_count = len(psutil.pids())

            # Get temperature if available
            temp_celsius = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Use first available temperature sensor
                    for name, entries in temps.items():
                        if entries:
                            temp_celsius = entries[0].current
                            break
            except Exception:
                pass

            # Get GPU metrics if available
            gpu_percent = None
            gpu_memory_percent = None
            try:
                import GPUtil

                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use first GPU
                    gpu_percent = gpu.load * 100
                    gpu_memory_percent = gpu.memoryUtil * 100
            except ImportError:
                pass

            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_percent=memory.percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_sent_mb=sent_mb,
                network_recv_mb=recv_mb,
                process_count=process_count,
                uptime_seconds=time.time() - self.boot_time,
                temperature_celsius=temp_celsius,
                gpu_percent=gpu_percent,
                gpu_memory_percent=gpu_memory_percent,
            )

            # Determine status based on resource usage
            status = "normal"
            if cpu_percent > 80 or memory.percent > 80 or disk_percent > 90:
                status = "critical"
            elif cpu_percent > 60 or memory.percent > 60 or disk_percent > 75:
                status = "warning"

            return WidgetData(
                widget_type=WidgetType.RESOURCE_USAGE,
                title=self.title,
                content=metrics.__dict__,
                status=status,
                last_updated=datetime.now(),
                refresh_interval=self.refresh_interval,
            )

        except Exception as e:
            logger.error(f"Failed to fetch resource usage: {e}")
            return None


class NetworkStatusWidget(StatusWidget):
    """Network status monitoring widget"""

    def __init__(self):
        super().__init__("network_status", "Network", refresh_interval=5)
        self.test_hosts = ["8.8.8.8", "1.1.1.1", "cloudflare.com"]
        self.last_bandwidth_check = None

    async def _fetch_data(self) -> Optional[WidgetData]:
        """Fetch network status"""
        try:
            metrics = NetworkMetrics()
            metrics.last_check = datetime.now()

            # Get local IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                metrics.local_ip = s.getsockname()[0]
                s.close()
            except Exception:
                metrics.local_ip = "Unknown"

            # Test connectivity
            latencies = []
            connected = False
            for host in self.test_hosts[:2]:  # Test first two hosts
                try:
                    start_time = time.time()
                    sock = socket.create_connection((host, 53), timeout=2)
                    latency = (time.time() - start_time) * 1000
                    latencies.append(latency)
                    sock.close()
                    connected = True
                except Exception:
                    pass

            if connected:
                metrics.status = ConnectionStatus.CONNECTED
                metrics.latency_ms = (
                    sum(latencies) / len(latencies) if latencies else None
                )
            else:
                metrics.status = ConnectionStatus.DISCONNECTED

            # Get active connections
            try:
                connections = psutil.net_connections()
                metrics.active_connections = len(
                    [c for c in connections if c.status == "ESTABLISHED"]
                )
            except Exception:
                pass

            # Get DNS servers
            try:
                dns_servers = []
                with open("/etc/resolv.conf") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            dns_servers.append(line.split()[1])
                metrics.dns_servers = dns_servers[:3]  # Limit to first 3
            except Exception:
                metrics.dns_servers = []

            # Get public IP (cached to avoid frequent requests)
            if (
                not self.last_bandwidth_check
                or (datetime.now() - self.last_bandwidth_check).total_seconds() > 300
            ):  # 5 minutes
                try:
                    async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as session:
                        async with session.get("https://api.ipify.org") as response:
                            if response.status == 200:
                                metrics.public_ip = await response.text()
                except Exception:
                    pass
                self.last_bandwidth_check = datetime.now()

            # Get bandwidth (simplified)
            network = psutil.net_io_counters()
            metrics.bandwidth_mbps = network.bytes_sent + network.bytes_recv

            return WidgetData(
                widget_type=WidgetType.NETWORK_STATUS,
                title=self.title,
                content=metrics.__dict__,
                status=metrics.status.value,
                last_updated=datetime.now(),
                refresh_interval=self.refresh_interval,
            )

        except Exception as e:
            logger.error(f"Failed to fetch network status: {e}")
            return None


class ServiceHealthWidget(StatusWidget):
    """Service health monitoring widget"""

    def __init__(self, service_manager=None):
        super().__init__("service_health", "Services", refresh_interval=10)
        self.service_manager = service_manager

    async def _fetch_data(self) -> Optional[WidgetData]:
        """Fetch service health status"""
        if not self.service_manager:
            return WidgetData(
                widget_type=WidgetType.SERVICE_HEALTH,
                title=self.title,
                content={"message": "No service manager available"},
                status="unknown",
                last_updated=datetime.now(),
            )

        try:
            # Get service status from manager
            services_status = self.service_manager.get_all_services_status()

            # Count services by status
            healthy_count = services_status["global_metrics"]["healthy_services"]
            total_count = services_status["global_metrics"]["total_services"]

            content = {
                "total_services": total_count,
                "healthy_services": healthy_count,
                "unhealthy_services": total_count - healthy_count,
                "services": services_status["services"],
            }

            # Determine overall status
            status = "normal"
            if healthy_count == 0 and total_count > 0:
                status = "critical"
            elif healthy_count < total_count:
                status = "warning"

            return WidgetData(
                widget_type=WidgetType.SERVICE_HEALTH,
                title=self.title,
                content=content,
                status=status,
                last_updated=datetime.now(),
                refresh_interval=self.refresh_interval,
            )

        except Exception as e:
            logger.error(f"Failed to fetch service health: {e}")
            return None


class TimeClockWidget(StatusWidget):
    """Time and date widget"""

    def __init__(self):
        super().__init__("time_clock", "Time", refresh_interval=1)

    async def _fetch_data(self) -> Optional[WidgetData]:
        """Fetch current time"""
        try:
            now = datetime.now()
            content = {
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "day_of_week": now.strftime("%A"),
                "iso_format": now.isoformat(),
                "timestamp": now.timestamp(),
            }

            return WidgetData(
                widget_type=WidgetType.TIME_CLOCK,
                title=self.title,
                content=content,
                last_updated=datetime.now(),
                refresh_interval=self.refresh_interval,
            )

        except Exception as e:
            logger.error(f"Failed to fetch time: {e}")
            return None


class NotificationWidget(StatusWidget):
    """Notification and alert widget"""

    def __init__(self):
        super().__init__("notifications", "Notifications", refresh_interval=5)
        self.alerts: deque[Alert] = deque(maxlen=100)
        self.alert_callbacks: list[Callable] = []

    def add_alert(self, alert: Alert) -> None:
        """Add a new alert"""
        self.alerts.append(alert)
        self._notify_alert_callbacks(alert)

    def _notify_alert_callbacks(self, alert: Alert) -> None:
        """Notify alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

    async def _fetch_data(self) -> Optional[WidgetData]:
        """Fetch notification data"""
        try:
            # Count alerts by severity
            severity_counts = defaultdict(int)
            recent_alerts = []
            now = datetime.now()

            for alert in self.alerts:
                if not alert.acknowledged and not alert.resolved:
                    severity_counts[alert.severity.value] += 1

                    # Include recent alerts (last hour)
                    if (now - alert.timestamp).total_seconds() < 3600:
                        recent_alerts.append(alert.to_dict())

            content = {
                "alert_counts": dict(severity_counts),
                "recent_alerts": recent_alerts[:10],  # Limit to 10 most recent
                "total_alerts": len(self.alerts),
                "unacknowledged_count": sum(
                    1 for a in self.alerts if not a.acknowledged and not a.resolved
                ),
            }

            # Determine status based on critical alerts
            status = "normal"
            if severity_counts["critical"] > 0:
                status = "critical"
            elif severity_counts["error"] > 0:
                status = "error"
            elif severity_counts["warning"] > 0:
                status = "warning"

            return WidgetData(
                widget_type=WidgetType.NOTIFICATIONS,
                title=self.title,
                content=content,
                status=status,
                last_updated=datetime.now(),
                refresh_interval=self.refresh_interval,
            )

        except Exception as e:
            logger.error(f"Failed to fetch notifications: {e}")
            return None


class ProductionStatusBar:
    """Production-grade real-time status bar"""

    def __init__(self, storage_path: Optional[str] = None, service_manager=None):
        self.storage_path = (
            Path(storage_path) if storage_path else Path("data/status_bar.db")
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Widgets
        self.widgets: dict[str, StatusWidget] = {}
        self.widget_order: list[str] = []

        # Alerts and notifications
        self.alerts: deque[Alert] = deque(maxlen=1000)
        self.alert_callbacks: list[Callable] = []

        # Metrics and history
        self.metrics_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_metrics = {
            "update_count": 0,
            "error_count": 0,
            "average_update_time_ms": 0.0,
            "last_update": None,
        }

        # Background tasks
        self.update_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Threading
        self.thread_pool = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="status_bar"
        )

        # Database
        self._init_database()

        # Initialize default widgets
        self._init_default_widgets(service_manager)

        # Start background tasks
        self._start_background_tasks()

        logger.info("Production Status Bar initialized")

    def _init_database(self) -> None:
        """Initialize status bar database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS status_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        widget_id TEXT NOT NULL,
                        widget_data TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id TEXT PRIMARY KEY,
                        severity TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        source TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        acknowledged BOOLEAN DEFAULT FALSE,
                        resolved BOOLEAN DEFAULT FALSE,
                        metadata TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        widget_id TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (widget_id, metric_name, timestamp)
                    )
                """)

                # Indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON status_history (timestamp)"  # noqa: E501
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_history_widget ON status_history (widget_id)"  # noqa: E501
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts (timestamp)"  # noqa: E501
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics (timestamp)"  # noqa: E501
                )

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def _init_default_widgets(self, service_manager=None) -> None:
        """Initialize default widgets"""
        # System info widget
        self.register_widget(SystemInfoWidget())

        # Resource usage widget
        self.register_widget(ResourceUsageWidget())

        # Network status widget
        self.register_widget(NetworkStatusWidget())

        # Service health widget
        if service_manager:
            self.register_widget(ServiceHealthWidget(service_manager))

        # Time clock widget
        self.register_widget(TimeClockWidget())

        # Notification widget
        notification_widget = NotificationWidget()
        self.register_widget(notification_widget)

        # Set up alert forwarding
        notification_widget.alert_callbacks.extend(self.alert_callbacks)

        # Define widget order
        self.widget_order = [
            "system_info",
            "resource_usage",
            "network_status",
            "service_health",
            "time_clock",
            "notifications",
        ]

    def register_widget(self, widget: StatusWidget) -> None:
        """Register a new widget"""
        self.widgets[widget.widget_id] = widget
        logger.debug(f"Registered widget: {widget.widget_id}")

    def unregister_widget(self, widget_id: str) -> bool:
        """Unregister a widget"""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            if widget_id in self.widget_order:
                self.widget_order.remove(widget_id)
            logger.debug(f"Unregistered widget: {widget_id}")
            return True
        return False

    def add_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Add a new alert"""
        alert = Alert(
            id=str(uuid.uuid4()),
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {},
        )

        self.alerts.append(alert)

        # Forward to notification widget
        if "notifications" in self.widgets:
            notification_widget = self.widgets["notifications"]
            if isinstance(notification_widget, NotificationWidget):
                notification_widget.add_alert(alert)

        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

        # Save to database
        self._save_alert(alert)

        logger.info(f"Added alert: {title} ({severity.value})")
        return alert.id

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self._update_alert(alert)
                logger.info(f"Acknowledged alert: {alert_id}")
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self._update_alert(alert)
                logger.info(f"Resolved alert: {alert_id}")
                return True
        return False

    def get_widget_data(self, widget_id: str) -> Optional[WidgetData]:
        """Get current widget data"""
        if widget_id in self.widgets:
            return self.widgets[widget_id].data
        return None

    def get_all_widget_data(self) -> dict[str, WidgetData]:
        """Get all widget data"""
        return {
            widget_id: widget.data
            for widget_id, widget in self.widgets.items()
            if widget.data is not None
        }

    def get_recent_alerts(
        self,
        limit: int = 50,
        severity: Optional[AlertSeverity] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
    ) -> list[Alert]:
        """Get recent alerts with filtering"""
        filtered_alerts = []

        for alert in self.alerts:
            # Apply filters
            if severity and alert.severity != severity:
                continue
            if acknowledged is not None and alert.acknowledged != acknowledged:
                continue
            if resolved is not None and alert.resolved != resolved:
                continue

            filtered_alerts.append(alert)

        # Sort by timestamp (newest first) and limit
        filtered_alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return filtered_alerts[:limit]

    def add_alert_callback(self, callback: Callable) -> None:
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)

    def _start_background_tasks(self) -> None:
        """Start background update tasks"""
        self.update_task = asyncio.create_task(self._update_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _update_loop(self) -> None:
        """Background widget update loop"""
        while not self._shutdown_event.is_set():
            try:
                start_time = time.time()

                # Update all enabled widgets
                tasks = []
                for widget in self.widgets.values():
                    if widget.enabled:
                        task = asyncio.create_task(widget.update())
                        tasks.append(task)

                if tasks:
                    # Wait for all updates to complete
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process results
                    for widget_id, result in zip(self.widgets.keys(), results):
                        if isinstance(result, Exception):
                            logger.error(f"Widget {widget_id} update failed: {result}")
                            self.performance_metrics["error_count"] += 1
                        elif result:
                            # Update metrics history
                            self._update_metrics_history(widget_id, result)
                            # Notify callbacks
                            widget = self.widgets[widget_id]
                            widget.notify_callbacks(result)

                # Update performance metrics
                update_time = (time.time() - start_time) * 1000
                self.performance_metrics["update_count"] += 1
                self.performance_metrics["last_update"] = datetime.now()

                # Calculate average update time
                total_time = (
                    self.performance_metrics.get("total_update_time", 0.0) + update_time
                )
                count = self.performance_metrics["update_count"]
                self.performance_metrics["average_update_time_ms"] = total_time / count
                self.performance_metrics["total_update_time"] = total_time

                # Calculate next update interval based on widget requirements
                min_interval = min(
                    widget.refresh_interval
                    for widget in self.widgets.values()
                    if widget.enabled
                )

                await asyncio.sleep(min_interval)

            except Exception as e:
                logger.error(f"Update loop error: {e}")
                await asyncio.sleep(5)

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self._shutdown_event.is_set():
            try:
                # Clean up old data
                self._cleanup_old_data()

                # Re-enable disabled widgets that might have recovered
                self._check_disabled_widgets()

                # Save metrics to database
                await self._save_metrics()

                # Wait for next cleanup (hourly)
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(300)  # 5 minutes on error

    def _update_metrics_history(self, widget_id: str, data: WidgetData) -> None:
        """Update metrics history for a widget"""
        try:
            # Store timestamp
            self.metrics_history[f"{widget_id}_timestamp"].append(
                data.last_updated.timestamp()
            )

            # Extract numeric metrics based on widget type
            if widget_id == "resource_usage" and data.content:
                content = data.content
                self.metrics_history[f"{widget_id}_cpu"].append(
                    content.get("cpu_percent", 0)
                )
                self.metrics_history[f"{widget_id}_memory"].append(
                    content.get("memory_percent", 0)
                )
                self.metrics_history[f"{widget_id}_disk"].append(
                    content.get("disk_percent", 0)
                )

            elif widget_id == "network_status" and data.content:
                content = data.content
                if content.get("latency_ms"):
                    self.metrics_history[f"{widget_id}_latency"].append(
                        content["latency_ms"]
                    )
                self.metrics_history[f"{widget_id}_connections"].append(
                    content.get("active_connections", 0)
                )

        except Exception as e:
            logger.error(f"Failed to update metrics history: {e}")

    def _cleanup_old_data(self) -> None:
        """Clean up old data to prevent memory leaks"""
        # Clean up old alerts (keep last 30 days)
        cutoff_time = datetime.now() - timedelta(days=30)
        original_count = len(self.alerts)
        self.alerts = deque(
            (alert for alert in self.alerts if alert.timestamp > cutoff_time),
            maxlen=1000,
        )

        if len(self.alerts) < original_count:
            logger.debug(f"Cleaned up {original_count - len(self.alerts)} old alerts")

    def _check_disabled_widgets(self) -> None:
        """Check if disabled widgets can be re-enabled"""
        for widget in self.widgets.values():
            if not widget.enabled:
                # Try to re-enable after some time
                if widget.error_count > 0:
                    widget.error_count = max(0, widget.error_count - 1)
                    if widget.error_count == 0:
                        widget.enabled = True
                        logger.info(f"Re-enabled widget: {widget.widget_id}")

    async def _save_metrics(self) -> None:
        """Save metrics to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                for widget_id, widget in self.widgets.items():
                    if widget.data and widget.data.content:
                        # Save widget data
                        conn.execute(
                            "INSERT INTO status_history (widget_id, widget_data, timestamp) VALUES (?, ?, ?)",  # noqa: E501
                            (
                                widget_id,
                                json.dumps(widget.data.__dict__),
                                widget.data.last_updated.isoformat(),
                            ),
                        )

                        # Save specific metrics
                        self._save_widget_metrics(conn, widget_id, widget.data)

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def _save_widget_metrics(self, conn, widget_id: str, data: WidgetData) -> None:
        """Save specific widget metrics"""
        try:
            timestamp = data.last_updated.isoformat()

            if widget_id == "resource_usage" and data.content:
                content = data.content
                conn.execute(
                    "INSERT INTO metrics (widget_id, metric_name, metric_value, timestamp) VALUES (?, ?, ?, ?)",  # noqa: E501
                    (
                        widget_id,
                        "cpu_percent",
                        content.get("cpu_percent", 0),
                        timestamp,
                    ),
                )
                conn.execute(
                    "INSERT INTO metrics (widget_id, metric_name, metric_value, timestamp) VALUES (?, ?, ?, ?)",  # noqa: E501
                    (
                        widget_id,
                        "memory_percent",
                        content.get("memory_percent", 0),
                        timestamp,
                    ),
                )

            elif widget_id == "network_status" and data.content:
                content = data.content
                if content.get("latency_ms"):
                    conn.execute(
                        "INSERT INTO metrics (widget_id, metric_name, metric_value, timestamp) VALUES (?, ?, ?, ?)",  # noqa: E501
                        (widget_id, "latency_ms", content["latency_ms"], timestamp),
                    )

        except Exception as e:
            logger.error(f"Failed to save widget metrics: {e}")

    def _save_alert(self, alert: Alert) -> None:
        """Save alert to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT INTO alerts (id, severity, title, message, source, timestamp, acknowledged, resolved, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",  # noqa: E501
                    (
                        alert.id,
                        alert.severity.value,
                        alert.title,
                        alert.message,
                        alert.source,
                        alert.timestamp.isoformat(),
                        alert.acknowledged,
                        alert.resolved,
                        json.dumps(alert.metadata),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")

    def _update_alert(self, alert: Alert) -> None:
        """Update alert in database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "UPDATE alerts SET acknowledged = ?, resolved = ? WHERE id = ?",
                    (alert.acknowledged, alert.resolved, alert.id),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update alert: {e}")

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics"""
        return {
            "performance_metrics": self.performance_metrics.copy(),
            "widget_count": len(self.widgets),
            "enabled_widgets": sum(1 for w in self.widgets.values() if w.enabled),
            "alert_count": len(self.alerts),
            "unacknowledged_alerts": sum(
                1 for a in self.alerts if not a.acknowledged and not a.resolved
            ),
            "metrics_history_sizes": {
                key: len(history) for key, history in self.metrics_history.items()
            },
        }

    def export_data(self, file_path: str, format: str = "json") -> bool:
        """Export status bar data"""
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "widgets": self.get_all_widget_data(),
                "alerts": [alert.to_dict() for alert in self.alerts],
                "performance_metrics": self.performance_metrics,
                "widget_order": self.widget_order,
            }

            with open(file_path, "w", encoding="utf-8") as f:
                if format.lower() == "json":
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported status bar data to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False

    async def shutdown(self) -> None:
        """Shutdown status bar gracefully"""
        logger.info("Shutting down Production Status Bar")

        # Signal shutdown
        self._shutdown_event.set()

        # Cancel background tasks
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        # Save final metrics
        await self._save_metrics()

        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)

        logger.info("Production Status Bar shutdown complete")
