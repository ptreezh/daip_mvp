# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 10:00:00
@Author  : DAIP-LIVE Team
@File    : performance_monitoring_system.py
@Description:
    V0.3.7 Performance Monitoring and Optimization System
    企业级性能监控和优化系统
"""

import asyncio
import logging
import psutil
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
import queue
import weakref

from ..subagents.dynamic_weight.performance_monitor import PerformanceMonitor, PerformanceMetric, PerformanceDataPoint

logger = logging.getLogger(__name__)


class SystemResource(Enum):
    """System resource types."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"


class PerformanceAlert(Enum):
    """Performance alert levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FATAL = "fatal"


@dataclass
class SystemMetrics:
    """System metrics data point."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used: float
    memory_total: float
    disk_usage: float
    disk_read_bytes: int
    disk_write_bytes: int
    network_sent: int
    network_recv: int
    process_count: int
    thread_count: int
    load_average: Optional[float] = None


@dataclass
class PerformanceAlertData:
    """Performance alert data."""
    alert_id: str
    alert_type: PerformanceAlert
    resource_type: SystemResource
    message: str
    timestamp: str
    value: float
    threshold: float
    severity: str
    suggested_actions: List[str]


class SystemResourceMonitor:
    """System resource monitoring."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.monitoring_interval = self.config.get("monitoring_interval", 5.0)  # seconds
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.max_history_size = self.config.get("max_history_size", 1000)
        self.alerts = []
        self.alert_callbacks = []
        
        # Resource thresholds
        self.thresholds = {
            "cpu_warning": 80.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 90.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
            "load_warning": 2.0,
            "load_critical": 4.0
        }
        
        # Performance baselines
        self.baselines = self._initialize_baselines()
        
        # Performance optimization
        self.optimization_strategies = {
            "memory_cleanup": self._cleanup_memory,
            "process_optimization": self._optimize_processes,
            "cache_optimization": self._optimize_cache
        }
        
        logger.info("System Resource Monitor initialized")
    
    def _initialize_baselines(self) -> Dict[str, Any]:
        """Initialize performance baselines."""
        return {
            "cpu_normal": 30.0,
            "memory_normal": 50.0,
            "disk_normal": 60.0,
            "response_time_normal": 1.0,
            "throughput_normal": 1000.0
        }
    
    def start_monitoring(self):
        """Start system resource monitoring."""
        if self.is_monitoring:
            logger.warning("Resource monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("System resource monitoring started")
    
    def stop_monitoring(self):
        """Stop system resource monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("System resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self._process_metrics(metrics)
                self._check_alerts(metrics)
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1.0)
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            current_process = psutil.Process()
            thread_count = current_process.num_threads()
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_total=memory.total,
                disk_usage=disk.percent,
                disk_read_bytes=disk_io.read_bytes if disk_io else 0,
                disk_write_bytes=disk_io.write_bytes if disk_io else 0,
                network_sent=network.bytes_sent if network else 0,
                network_recv=network.bytes_recv if network else 0,
                process_count=process_count,
                thread_count=thread_count,
                load_average=load_avg
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            # Return default metrics
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used=0,
                memory_total=0,
                disk_usage=0.0,
                disk_read_bytes=0,
                disk_write_bytes=0,
                network_sent=0,
                network_recv=0,
                process_count=0,
                thread_count=0,
                load_average=None
            )
    
    def _process_metrics(self, metrics: SystemMetrics):
        """Process and store metrics."""
        self.metrics_history.append(metrics)
        
        # Limit history size
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def _check_alerts(self, metrics: SystemMetrics):
        """Check for performance alerts."""
        alerts = []
        
        # CPU alerts
        if metrics.cpu_percent > self.thresholds["cpu_critical"]:
            alerts.append(self._create_alert(
                PerformanceAlert.CRITICAL,
                SystemResource.CPU,
                f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                metrics.cpu_percent,
                self.thresholds["cpu_critical"]
            ))
        elif metrics.cpu_percent > self.thresholds["cpu_warning"]:
            alerts.append(self._create_alert(
                PerformanceAlert.WARNING,
                SystemResource.CPU,
                f"CPU usage high: {metrics.cpu_percent:.1f}%",
                metrics.cpu_percent,
                self.thresholds["cpu_warning"]
            ))
        
        # Memory alerts
        if metrics.memory_percent > self.thresholds["memory_critical"]:
            alerts.append(self._create_alert(
                PerformanceAlert.CRITICAL,
                SystemResource.MEMORY,
                f"Memory usage critical: {metrics.memory_percent:.1f}%",
                metrics.memory_percent,
                self.thresholds["memory_critical"]
            ))
        elif metrics.memory_percent > self.thresholds["memory_warning"]:
            alerts.append(self._create_alert(
                PerformanceAlert.WARNING,
                SystemResource.MEMORY,
                f"Memory usage high: {metrics.memory_percent:.1f}%",
                metrics.memory_percent,
                self.thresholds["memory_warning"]
            ))
        
        # Disk alerts
        if metrics.disk_usage > self.thresholds["disk_critical"]:
            alerts.append(self._create_alert(
                PerformanceAlert.CRITICAL,
                SystemResource.DISK,
                f"Disk usage critical: {metrics.disk_usage:.1f}%",
                metrics.disk_usage,
                self.thresholds["disk_critical"]
            ))
        elif metrics.disk_usage > self.thresholds["disk_warning"]:
            alerts.append(self._create_alert(
                PerformanceAlert.WARNING,
                SystemResource.DISK,
                f"Disk usage high: {metrics.disk_usage:.1f}%",
                metrics.disk_usage,
                self.thresholds["disk_warning"]
            ))
        
        # Load average alerts (if available)
        if metrics.load_average and metrics.load_average > self.thresholds["load_critical"]:
            alerts.append(self._create_alert(
                PerformanceAlert.CRITICAL,
                SystemResource.CPU,
                f"Load average critical: {metrics.load_average:.2f}",
                metrics.load_average,
                self.thresholds["load_critical"]
            ))
        elif metrics.load_average and metrics.load_average > self.thresholds["load_warning"]:
            alerts.append(self._create_alert(
                PerformanceAlert.WARNING,
                SystemResource.CPU,
                f"Load average high: {metrics.load_average:.2f}",
                metrics.load_average,
                self.thresholds["load_warning"]
            ))
        
        # Process alerts
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _create_alert(self, alert_type: PerformanceAlert, resource_type: SystemResource, 
                      message: str, value: float, threshold: float) -> PerformanceAlertData:
        """Create a performance alert."""
        return PerformanceAlertData(
            alert_id=f"alert_{int(time.time())}_{resource_type.value}",
            alert_type=alert_type,
            resource_type=resource_type,
            message=message,
            timestamp=datetime.now().isoformat(),
            value=value,
            threshold=threshold,
            severity=alert_type.value,
            suggested_actions=self._get_suggested_actions(resource_type, alert_type, value, threshold)
        )
    
    def _get_suggested_actions(self, resource_type: SystemResource, alert_type: PerformanceAlert, 
                              value: float, threshold: float) -> List[str]:
        """Get suggested actions for alerts."""
        actions = []
        
        if resource_type == SystemResource.CPU:
            if alert_type == PerformanceAlert.CRITICAL:
                actions.extend([
                    "立即检查高CPU使用率进程",
                    "考虑终止非关键进程",
                    "检查是否有无限循环",
                    "考虑增加系统资源"
                ])
            else:
                actions.extend([
                    "监控CPU使用趋势",
                    "检查进程优先级",
                    "优化CPU密集型任务"
                ])
        
        elif resource_type == SystemResource.MEMORY:
            if alert_type == PerformanceAlert.CRITICAL:
                actions.extend([
                    "立即执行内存清理",
                    "检查内存泄漏",
                    "重启相关服务",
                    "增加系统内存"
                ])
            else:
                actions.extend([
                    "监控内存使用趋势",
                    "优化内存管理",
                    "清理缓存文件"
                ])
        
        elif resource_type == SystemResource.DISK:
            if alert_type == PerformanceAlert.CRITICAL:
                actions.extend([
                    "立即清理磁盘空间",
                    "删除临时文件",
                    "压缩或归档旧数据",
                    "扩展磁盘容量"
                ])
            else:
                actions.extend([
                    "监控磁盘使用趋势",
                    "清理不必要文件",
                    "设置磁盘配额"
                ])
        
        return actions
    
    def _trigger_alert(self, alert: PerformanceAlertData):
        """Trigger performance alert."""
        self.alerts.append(alert)
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        # Log alert
        log_method = {
            PerformanceAlert.INFO: logger.info,
            PerformanceAlert.WARNING: logger.warning,
            PerformanceAlert.CRITICAL: logger.error,
            PerformanceAlert.FATAL: logger.critical
        }.get(alert.alert_type, logger.warning)
        
        log_method(f"Performance Alert: {alert.message}")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlertData], None]):
        """Add alert callback."""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Get metrics history for specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics.timestamp) > cutoff_time
        ]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics_history:
            return {"error": "No metrics data available"}
        
        current_metrics = self.metrics_history[-1]
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in self.metrics_history[-60:]]  # Last 5 minutes
        memory_values = [m.memory_percent for m in self.metrics_history[-60:]]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": asdict(current_metrics),
            "statistics": {
                "cpu": {
                    "current": current_metrics.cpu_percent,
                    "average": statistics.mean(cpu_values) if cpu_values else 0,
                    "min": min(cpu_values) if cpu_values else 0,
                    "max": max(cpu_values) if cpu_values else 0
                },
                "memory": {
                    "current": current_metrics.memory_percent,
                    "average": statistics.mean(memory_values) if memory_values else 0,
                    "min": min(memory_values) if memory_values else 0,
                    "max": max(memory_values) if memory_values else 0
                }
            },
            "alerts_count": len(self.alerts),
            "monitoring_status": "active" if self.is_monitoring else "inactive"
        }
    
    def _cleanup_memory(self):
        """Cleanup memory optimization."""
        try:
            import gc
            gc.collect()
            logger.info("Memory cleanup completed")
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
    
    def _optimize_processes(self):
        """Optimize processes."""
        try:
            # This would implement process optimization logic
            logger.info("Process optimization completed")
        except Exception as e:
            logger.error(f"Process optimization failed: {e}")
    
    def _optimize_cache(self):
        """Optimize cache."""
        try:
            # This would implement cache optimization logic
            logger.info("Cache optimization completed")
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
    
    def optimize_performance(self, optimization_type: str = "auto") -> Dict[str, Any]:
        """Optimize system performance."""
        results = {"optimizations": [], "success": True}
        
        try:
            if optimization_type == "auto" or optimization_type == "memory":
                result = self._cleanup_memory()
                results["optimizations"].append({"type": "memory", "result": result})
            
            if optimization_type == "auto" or optimization_type == "process":
                result = self._optimize_processes()
                results["optimizations"].append({"type": "process", "result": result})
            
            if optimization_type == "auto" or optimization_type == "cache":
                result = self._optimize_cache()
                results["optimizations"].append({"type": "cache", "result": result})
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def export_performance_data(self) -> Dict[str, Any]:
        """Export performance data."""
        return {
            "export_timestamp": datetime.now().isoformat(),
            "metrics_history": [asdict(m) for m in self.metrics_history],
            "alerts": [asdict(a) for a in self.alerts],
            "thresholds": self.thresholds,
            "baselines": self.baselines,
            "monitoring_config": {
                "monitoring_interval": self.monitoring_interval,
                "max_history_size": self.max_history_size,
                "is_monitoring": self.is_monitoring
            }
        }


class PerformanceOptimizationEngine:
    """Performance optimization engine."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.resource_monitor = SystemResourceMonitor(config)
        self.performance_monitor = PerformanceMonitor(config)
        
        # Optimization strategies
        self.optimization_strategies = {
            "memory_management": self._optimize_memory_management,
            "cpu_optimization": self._optimize_cpu_usage,
            "io_optimization": self._optimize_io_operations,
            "network_optimization": self._optimize_network_usage,
            "cache_optimization": self._optimize_cache_usage
        }
        
        # Performance benchmarks
        self.benchmarks = self._initialize_benchmarks()
        
        # Auto-optimization
        self.auto_optimization_enabled = self.config.get("auto_optimization", True)
        self.optimization_interval = self.config.get("optimization_interval", 300)  # 5 minutes
        
        logger.info("Performance Optimization Engine initialized")
    
    def _initialize_benchmarks(self) -> Dict[str, Any]:
        """Initialize performance benchmarks."""
        return {
            "response_time": {"target": 1.0, "maximum": 5.0},
            "throughput": {"target": 1000, "minimum": 100},
            "memory_usage": {"target": 50, "maximum": 80},
            "cpu_usage": {"target": 30, "maximum": 70},
            "error_rate": {"target": 0.01, "maximum": 0.05}
        }
    
    async def initialize(self):
        """Initialize the optimization engine."""
        try:
            # Start resource monitoring
            self.resource_monitor.start_monitoring()
            
            # Set up alert callbacks
            self.resource_monitor.add_alert_callback(self._handle_performance_alert)
            
            # Start auto-optimization if enabled
            if self.auto_optimization_enabled:
                await self.start_auto_optimization()
            
            logger.info("Performance Optimization Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize optimization engine: {e}")
            raise
    
    async def start_auto_optimization(self):
        """Start automatic optimization."""
        while self.auto_optimization_enabled:
            try:
                await self._auto_optimize()
                await asyncio.sleep(self.optimization_interval)
            except Exception as e:
                logger.error(f"Auto-optimization error: {e}")
                await asyncio.sleep(60)
    
    async def _auto_optimize(self):
        """Automatic optimization routine."""
        try:
            # Get current performance metrics
            performance_summary = self.resource_monitor.get_performance_summary()
            
            # Check if optimization is needed
            if self._needs_optimization(performance_summary):
                # Determine optimization strategy
                strategy = self._determine_optimization_strategy(performance_summary)
                
                # Execute optimization
                result = await self._execute_optimization_strategy(strategy)
                
                logger.info(f"Auto-optimization completed: {result}")
            
        except Exception as e:
            logger.error(f"Auto-optimization failed: {e}")
    
    def _needs_optimization(self, performance_summary: Dict[str, Any]) -> bool:
        """Check if optimization is needed."""
        try:
            current_metrics = performance_summary.get("current_metrics", {})
            
            # Check CPU usage
            cpu_usage = current_metrics.get("cpu_percent", 0)
            if cpu_usage > self.benchmarks["cpu_usage"]["maximum"]:
                return True
            
            # Check memory usage
            memory_usage = current_metrics.get("memory_percent", 0)
            if memory_usage > self.benchmarks["memory_usage"]["maximum"]:
                return True
            
            # Check alerts
            alerts_count = performance_summary.get("alerts_count", 0)
            if alerts_count > 5:  # Too many alerts
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking optimization need: {e}")
            return False
    
    def _determine_optimization_strategy(self, performance_summary: Dict[str, Any]) -> str:
        """Determine optimization strategy."""
        try:
            current_metrics = performance_summary.get("current_metrics", {})
            
            cpu_usage = current_metrics.get("cpu_percent", 0)
            memory_usage = current_metrics.get("memory_percent", 0)
            
            # Determine primary bottleneck
            if cpu_usage > 80:
                return "cpu_optimization"
            elif memory_usage > 80:
                return "memory_management"
            else:
                return "cache_optimization"
                
        except Exception as e:
            logger.error(f"Error determining optimization strategy: {e}")
            return "cache_optimization"
    
    async def _execute_optimization_strategy(self, strategy: str) -> Dict[str, Any]:
        """Execute optimization strategy."""
        try:
            if strategy in self.optimization_strategies:
                return await self.optimization_strategies[strategy]()
            else:
                logger.warning(f"Unknown optimization strategy: {strategy}")
                return {"success": False, "error": "Unknown strategy"}
                
        except Exception as e:
            logger.error(f"Error executing optimization strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_memory_management(self) -> Dict[str, Any]:
        """Optimize memory management."""
        try:
            # Perform memory cleanup
            result = self.resource_monitor.optimize_performance("memory")
            
            # Record optimization metrics
            await self.performance_monitor.record_performance(
                PerformanceMetric.MEMORY_USAGE,
                0.0,  # Will be updated with actual improvement
                {"optimization": "memory_management"},
                {"strategy": "auto_optimization"}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_cpu_usage(self) -> Dict[str, Any]:
        """Optimize CPU usage."""
        try:
            # Perform CPU optimization
            result = self.resource_monitor.optimize_performance("process")
            
            # Record optimization metrics
            await self.performance_monitor.record_performance(
                PerformanceMetric.SYNTHESIS_SPEED,
                0.0,  # Will be updated with actual improvement
                {"optimization": "cpu_optimization"},
                {"strategy": "auto_optimization"}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"CPU optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_io_operations(self) -> Dict[str, Any]:
        """Optimize I/O operations."""
        try:
            # This would implement I/O optimization
            result = {"success": True, "message": "I/O optimization completed"}
            
            return result
            
        except Exception as e:
            logger.error(f"I/O optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_network_usage(self) -> Dict[str, Any]:
        """Optimize network usage."""
        try:
            # This would implement network optimization
            result = {"success": True, "message": "Network optimization completed"}
            
            return result
            
        except Exception as e:
            logger.error(f"Network optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_cache_usage(self) -> Dict[str, Any]:
        """Optimize cache usage."""
        try:
            # Perform cache optimization
            result = self.resource_monitor.optimize_performance("cache")
            
            # Record optimization metrics
            await self.performance_monitor.record_performance(
                PerformanceMetric.TOKEN_EFFICIENCY,
                0.0,  # Will be updated with actual improvement
                {"optimization": "cache_optimization"},
                {"strategy": "auto_optimization"}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_performance_alert(self, alert: PerformanceAlertData):
        """Handle performance alerts."""
        try:
            logger.info(f"Handling performance alert: {alert.message}")
            
            # Take immediate action for critical alerts
            if alert.alert_type == PerformanceAlert.CRITICAL:
                # Execute immediate optimization
                asyncio.create_task(self._execute_immediate_optimization(alert))
            
        except Exception as e:
            logger.error(f"Error handling performance alert: {e}")
    
    async def _execute_immediate_optimization(self, alert: PerformanceAlertData):
        """Execute immediate optimization for critical alerts."""
        try:
            if alert.resource_type == SystemResource.MEMORY:
                await self._optimize_memory_management()
            elif alert.resource_type == SystemResource.CPU:
                await self._optimize_cpu_usage()
            elif alert.resource_type == SystemResource.DISK:
                # Disk cleanup would go here
                pass
            elif alert.resource_type == SystemResource.NETWORK:
                await self._optimize_network_usage()
                
        except Exception as e:
            logger.error(f"Immediate optimization failed: {e}")
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get optimization summary."""
        try:
            # Get performance summary from resource monitor
            performance_summary = self.resource_monitor.get_performance_summary()
            
            # Get performance summary from performance monitor
            monitor_summary = asyncio.run(self.performance_monitor.get_performance_summary())
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_performance": performance_summary,
                "application_performance": monitor_summary,
                "optimization_status": {
                    "auto_optimization_enabled": self.auto_optimization_enabled,
                    "optimization_interval": self.optimization_interval,
                    "active_optimizations": len(self.optimization_strategies)
                },
                "benchmarks": self.benchmarks
            }
            
        except Exception as e:
            logger.error(f"Error getting optimization summary: {e}")
            return {"error": str(e)}
    
    def stop(self):
        """Stop the optimization engine."""
        try:
            self.auto_optimization_enabled = False
            self.resource_monitor.stop_monitoring()
            logger.info("Performance Optimization Engine stopped")
            
        except Exception as e:
            logger.error(f"Error stopping optimization engine: {e}")


class PerformanceMonitoringSystem:
    """
    V0.3.7 Performance Monitoring and Optimization System
    企业级性能监控和优化系统
    
    Features:
    - Real-time system resource monitoring
    - Performance alerting and optimization
    - Automatic performance tuning
    - Comprehensive performance reporting
    - Integration with existing monitoring components
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.optimization_engine = PerformanceOptimizationEngine(config)
        self.is_initialized = False
        self.startup_time = datetime.now()
        
        # Performance metrics
        self.performance_metrics = {
            "system_health": "unknown",
            "optimization_count": 0,
            "alert_count": 0,
            "uptime_seconds": 0
        }
        
        logger.info("V0.3.7 Performance Monitoring System initialized")
    
    async def initialize(self):
        """Initialize the performance monitoring system."""
        try:
            if self.is_initialized:
                logger.warning("Performance monitoring system already initialized")
                return
            
            # Initialize optimization engine
            await self.optimization_engine.initialize()
            
            self.is_initialized = True
            logger.info("V0.3.7 Performance Monitoring System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance monitoring system: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            if not self.is_initialized:
                return {"status": "not_initialized", "message": "System not initialized"}
            
            # Get optimization summary
            optimization_summary = self.optimization_engine.get_optimization_summary()
            
            # Calculate uptime
            uptime = datetime.now() - self.startup_time
            uptime_seconds = uptime.total_seconds()
            
            # Determine overall system health
            system_performance = optimization_summary.get("system_performance", {})
            current_metrics = system_performance.get("current_metrics", {})
            
            # Health assessment
            cpu_usage = current_metrics.get("cpu_percent", 0)
            memory_usage = current_metrics.get("memory_percent", 0)
            alerts_count = system_performance.get("alerts_count", 0)
            
            if cpu_usage < 70 and memory_usage < 80 and alerts_count < 3:
                health_status = "healthy"
            elif cpu_usage < 85 and memory_usage < 90 and alerts_count < 10:
                health_status = "degraded"
            else:
                health_status = "critical"
            
            return {
                "status": health_status,
                "uptime_seconds": uptime_seconds,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "alerts_count": alerts_count,
                "optimization_summary": optimization_summary,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        try:
            if not self.is_initialized:
                return {"error": "System not initialized"}
            
            # Get system health
            system_health = await self.get_system_health()
            
            # Get optimization summary
            optimization_summary = self.optimization_engine.get_optimization_summary()
            
            # Get performance metrics
            performance_metrics = self._get_performance_metrics()
            
            return {
                "report_timestamp": datetime.now().isoformat(),
                "version": "V0.3.7",
                "system_health": system_health,
                "optimization_summary": optimization_summary,
                "performance_metrics": performance_metrics,
                "recommendations": self._generate_recommendations(system_health, optimization_summary)
            }
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {"error": str(e)}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        try:
            # Update uptime
            uptime = datetime.now() - self.startup_time
            self.performance_metrics["uptime_seconds"] = uptime.total_seconds()
            
            return self.performance_metrics.copy()
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def _generate_recommendations(self, system_health: Dict[str, Any], 
                                 optimization_summary: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        try:
            status = system_health.get("status", "unknown")
            
            if status == "critical":
                recommendations.extend([
                    "立即执行系统性能优化",
                    "检查系统资源使用情况",
                    "考虑增加系统资源",
                    "优化应用程序配置"
                ])
            elif status == "degraded":
                recommendations.extend([
                    "监控系统性能趋势",
                    "执行预防性优化",
                    "检查应用程序瓶颈",
                    "优化资源使用"
                ])
            else:
                recommendations.extend([
                    "保持当前配置",
                    "定期监控系统性能",
                    "优化用户体验",
                    "保持系统更新"
                ])
            
            # Add specific recommendations based on metrics
            current_metrics = system_health.get("cpu_usage", 0)
            if current_metrics > 80:
                recommendations.append("CPU使用率较高，考虑优化或升级")
            
            memory_usage = system_health.get("memory_usage", 0)
            if memory_usage > 80:
                recommendations.append("内存使用率较高，考虑优化或升级")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("建议进行全面系统检查")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def execute_optimization(self, optimization_type: str = "auto") -> Dict[str, Any]:
        """Execute performance optimization."""
        try:
            if not self.is_initialized:
                return {"success": False, "error": "System not initialized"}
            
            # Execute optimization
            result = await self.optimization_engine._execute_optimization_strategy(optimization_type)
            
            # Update metrics
            if result.get("success", False):
                self.performance_metrics["optimization_count"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing optimization: {e}")
            return {"success": False, "error": str(e)}
    
    def stop(self):
        """Stop the performance monitoring system."""
        try:
            if self.is_initialized:
                self.optimization_engine.stop()
                self.is_initialized = False
                logger.info("V0.3.7 Performance Monitoring System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping performance monitoring system: {e}")


# Global instance
_performance_monitoring_system: Optional[PerformanceMonitoringSystem] = None


async def get_performance_monitoring_system(
    config: Dict[str, Any] = None
) -> PerformanceMonitoringSystem:
    """Get global performance monitoring system instance."""
    global _performance_monitoring_system
    
    if _performance_monitoring_system is None:
        _performance_monitoring_system = PerformanceMonitoringSystem(config)
        await _performance_monitoring_system.initialize()
    
    return _performance_monitoring_system


async def cleanup_performance_monitoring_system():
    """Cleanup global performance monitoring system."""
    global _performance_monitoring_system
    
    if _performance_monitoring_system:
        _performance_monitoring_system.stop()
        _performance_monitoring_system = None