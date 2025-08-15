"""@Time    : 2025-08-05 10:30:00
@Author  : DAIP-LIVE Team
@File    : test_v0_3_7_performance_monitoring.py
@Description:
    V0.3.7 Performance Monitoring System Test Suite
    企业级性能监控系统测试套件
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.core_services.performance_monitoring_system import (
    PerformanceAlert,
    PerformanceMonitoringSystem,
    PerformanceOptimizationEngine,
    SystemResource,
    SystemResourceMonitor,
)


class TestSystemResourceMonitor:
    """Test System Resource Monitor."""
    
    @pytest.fixture()
    def resource_monitor(self):
        """Create resource monitor instance."""
        config = {
            "monitoring_interval": 1.0,
            "max_history_size": 100
        }
        return SystemResourceMonitor(config)
    
    def test_initialization(self, resource_monitor):
        """Test resource monitor initialization."""
        assert resource_monitor.monitoring_interval == 1.0
        assert resource_monitor.max_history_size == 100
        assert not resource_monitor.is_monitoring
        assert len(resource_monitor.metrics_history) == 0
        assert len(resource_monitor.alerts) == 0
    
    def test_start_stop_monitoring(self, resource_monitor):
        """Test start and stop monitoring."""
        # Start monitoring
        resource_monitor.start_monitoring()
        assert resource_monitor.is_monitoring
        assert resource_monitor.monitor_thread is not None
        
        # Stop monitoring
        resource_monitor.stop_monitoring()
        assert not resource_monitor.is_monitoring
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    @patch('psutil.pids')
    @patch('psutil.Process')
    def test_collect_system_metrics(self, mock_process, mock_pids, mock_net, 
                                   mock_disk_io, mock_disk, mock_memory, mock_cpu, resource_monitor):
        """Test system metrics collection."""
        # Setup mocks
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=60.0, used=4000000000, total=8000000000)
        mock_disk.return_value = Mock(percent=70.0)
        mock_disk_io.return_value = Mock(read_bytes=1000000, write_bytes=500000)
        mock_net.return_value = Mock(bytes_sent=2000000, bytes_recv=3000000)
        mock_pids.return_value = [1, 2, 3, 4, 5]
        mock_process.return_value = Mock(num_threads=10)
        
        # Collect metrics
        metrics = resource_monitor._collect_system_metrics()
        
        # Verify metrics
        assert metrics.cpu_percent == 45.5
        assert metrics.memory_percent == 60.0
        assert metrics.disk_usage == 70.0
        assert metrics.process_count == 5
        assert metrics.thread_count == 10
    
    def test_threshold_checking(self, resource_monitor):
        """Test threshold checking."""
        # Test CPU threshold
        resource_monitor.thresholds["cpu_warning"] = 80.0
        resource_monitor.thresholds["cpu_critical"] = 90.0
        
        # Test warning threshold
        alert = resource_monitor._create_alert(
            PerformanceAlert.WARNING,
            SystemResource.CPU,
            "CPU usage high: 85.0%",
            85.0,
            80.0
        )
        assert alert.alert_type == PerformanceAlert.WARNING
        assert alert.resource_type == SystemResource.CPU
        
        # Test critical threshold
        alert = resource_monitor._create_alert(
            PerformanceAlert.CRITICAL,
            SystemResource.CPU,
            "CPU usage critical: 95.0%",
            95.0,
            90.0
        )
        assert alert.alert_type == PerformanceAlert.CRITICAL
    
    def test_alert_callback(self, resource_monitor):
        """Test alert callback mechanism."""
        callback_called = False
        captured_alert = None
        
        def test_callback(alert):
            nonlocal callback_called, captured_alert
            callback_called = True
            captured_alert = alert
        
        # Add callback
        resource_monitor.add_alert_callback(test_callback)
        
        # Trigger alert
        alert = resource_monitor._create_alert(
            PerformanceAlert.WARNING,
            SystemResource.MEMORY,
            "Test alert",
            85.0,
            80.0
        )
        resource_monitor._trigger_alert(alert)
        
        # Verify callback was called
        assert callback_called
        assert captured_alert is not None
        assert captured_alert.message == "Test alert"
    
    def test_performance_summary(self, resource_monitor):
        """Test performance summary generation."""
        # Add some test metrics
        from src.core_services.performance_monitoring_system import SystemMetrics
        
        test_metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=45.0,
            memory_percent=60.0,
            memory_used=4000000000,
            memory_total=8000000000,
            disk_usage=70.0,
            disk_read_bytes=1000000,
            disk_write_bytes=500000,
            network_sent=2000000,
            network_recv=3000000,
            process_count=5,
            thread_count=10,
            load_average=1.5
        )
        
        resource_monitor.metrics_history.append(test_metrics)
        
        # Get summary
        summary = resource_monitor.get_performance_summary()
        
        # Verify summary
        assert "current_metrics" in summary
        assert "statistics" in summary
        assert summary["monitoring_status"] == "inactive"
        assert summary["statistics"]["cpu"]["current"] == 45.0


class TestPerformanceOptimizationEngine:
    """Test Performance Optimization Engine."""
    
    @pytest.fixture()
    def optimization_engine(self):
        """Create optimization engine instance."""
        config = {
            "auto_optimization": False,  # Disable for testing
            "optimization_interval": 1.0
        }
        return PerformanceOptimizationEngine(config)
    
    def test_initialization(self, optimization_engine):
        """Test optimization engine initialization."""
        assert optimization_engine.auto_optimization_enabled is False
        assert optimization_engine.optimization_interval == 1.0
        assert len(optimization_engine.optimization_strategies) > 0
        assert len(optimization_engine.benchmarks) > 0
    
    @pytest.mark.asyncio()
    async def test_memory_optimization(self, optimization_engine):
        """Test memory optimization."""
        result = await optimization_engine._optimize_memory_management()
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio()
    async def test_cpu_optimization(self, optimization_engine):
        """Test CPU optimization."""
        result = await optimization_engine._optimize_cpu_usage()
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio()
    async def test_cache_optimization(self, optimization_engine):
        """Test cache optimization."""
        result = await optimization_engine._optimize_cache_usage()
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_optimization_strategy_determination(self, optimization_engine):
        """Test optimization strategy determination."""
        # Test CPU bottleneck
        performance_summary = {
            "current_metrics": {
                "cpu_percent": 85.0,
                "memory_percent": 60.0
            },
            "alerts_count": 2
        }
        
        strategy = optimization_engine._determine_optimization_strategy(performance_summary)
        assert strategy == "cpu_optimization"
        
        # Test memory bottleneck
        performance_summary["current_metrics"]["cpu_percent"] = 45.0
        performance_summary["current_metrics"]["memory_percent"] = 85.0
        
        strategy = optimization_engine._determine_optimization_strategy(performance_summary)
        assert strategy == "memory_management"
    
    def test_optimization_need_assessment(self, optimization_engine):
        """Test optimization need assessment."""
        # Test no optimization needed
        performance_summary = {
            "current_metrics": {
                "cpu_percent": 45.0,
                "memory_percent": 60.0
            },
            "alerts_count": 1
        }
        
        needs_optimization = optimization_engine._needs_optimization(performance_summary)
        assert needs_optimization is False
        
        # Test optimization needed
        performance_summary["current_metrics"]["cpu_percent"] = 85.0
        
        needs_optimization = optimization_engine._needs_optimization(performance_summary)
        assert needs_optimization is True


class TestPerformanceMonitoringSystem:
    """Test Performance Monitoring System."""
    
    @pytest.fixture()
    async def monitoring_system(self):
        """Create monitoring system instance."""
        config = {
            "auto_optimization": False,  # Disable for testing
            "monitoring_interval": 1.0
        }
        system = PerformanceMonitoringSystem(config)
        await system.initialize()
        yield system
        system.stop()
    
    @pytest.mark.asyncio()
    async def test_initialization(self, monitoring_system):
        """Test monitoring system initialization."""
        assert monitoring_system.is_initialized is True
        assert monitoring_system.optimization_engine is not None
        assert monitoring_system.startup_time is not None
    
    @pytest.mark.asyncio()
    async def test_system_health_check(self, monitoring_system):
        """Test system health check."""
        health = await monitoring_system.get_system_health()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "uptime_seconds" in health
        assert "last_check" in health
    
    @pytest.mark.asyncio()
    async def test_performance_report(self, monitoring_system):
        """Test performance report generation."""
        report = await monitoring_system.get_performance_report()
        
        assert isinstance(report, dict)
        assert "report_timestamp" in report
        assert "version" in report
        assert report["version"] == "V0.3.7"
        assert "system_health" in report
        assert "optimization_summary" in report
        assert "recommendations" in report
    
    @pytest.mark.asyncio()
    async def test_optimization_execution(self, monitoring_system):
        """Test optimization execution."""
        result = await monitoring_system.execute_optimization("memory_management")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio()
    async def test_recommendation_generation(self, monitoring_system):
        """Test recommendation generation."""
        system_health = {"status": "critical", "cpu_usage": 85, "memory_usage": 90}
        optimization_summary = {"test": "data"}
        
        recommendations = monitoring_system._generate_recommendations(
            system_health, optimization_summary
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("立即执行" in rec for rec in recommendations)  # Check for urgent recommendations


class TestPerformanceMonitoringIntegration:
    """Test integration scenarios."""
    
    @pytest.mark.asyncio()
    async def test_full_monitoring_cycle(self):
        """Test full monitoring cycle."""
        config = {
            "auto_optimization": False,
            "monitoring_interval": 0.1  # Fast for testing
        }
        
        # Create and initialize system
        monitoring_system = PerformanceMonitoringSystem(config)
        await monitoring_system.initialize()
        
        try:
            # Get initial health
            initial_health = await monitoring_system.get_system_health()
            assert initial_health["status"] != "not_initialized"
            
            # Execute optimization
            optimization_result = await monitoring_system.execute_optimization("cache_optimization")
            assert optimization_result["success"] is True
            
            # Get performance report
            report = await monitoring_system.get_performance_report()
            assert report["version"] == "V0.3.7"
            assert len(report["recommendations"]) > 0
            
        finally:
            monitoring_system.stop()
    
    @pytest.mark.asyncio()
    async def test_alert_handling(self):
        """Test alert handling scenario."""
        config = {
            "auto_optimization": False,
            "monitoring_interval": 0.1
        }
        
        monitoring_system = PerformanceMonitoringSystem(config)
        await monitoring_system.initialize()
        
        try:
            # Simulate critical alert
            alert_data = {
                "alert_type": "critical",
                "resource_type": "memory",
                "message": "Memory critical",
                "value": 95.0,
                "threshold": 90.0
            }
            
            # This would normally be triggered by the resource monitor
            # For testing, we'll verify the system can handle alerts
            
            # Get system health - should reflect critical status
            health = await monitoring_system.get_system_health()
            assert "status" in health
            
        finally:
            monitoring_system.stop()
    
    @pytest.mark.asyncio()
    async def test_performance_data_export(self):
        """Test performance data export."""
        config = {
            "auto_optimization": False,
            "monitoring_interval": 0.1
        }
        
        monitoring_system = PerformanceMonitoringSystem(config)
        await monitoring_system.initialize()
        
        try:
            # Get performance report
            report = await monitoring_system.get_performance_report()
            
            # Verify report structure
            required_keys = [
                "report_timestamp", "version", "system_health",
                "optimization_summary", "performance_metrics", "recommendations"
            ]
            
            for key in required_keys:
                assert key in report
            
            # Verify data types
            assert isinstance(report["recommendations"], list)
            assert isinstance(report["system_health"], dict)
            assert isinstance(report["optimization_summary"], dict)
            
        finally:
            monitoring_system.stop()


class TestPerformanceMonitoringErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio()
    async def test_uninitialized_system(self):
        """Test behavior with uninitialized system."""
        monitoring_system = PerformanceMonitoringSystem()
        
        # Should handle uninitialized state gracefully
        health = await monitoring_system.get_system_health()
        assert health["status"] == "not_initialized"
        
        report = await monitoring_system.get_performance_report()
        assert "error" in report
    
    @pytest.mark.asyncio()
    async def test_optimization_failure(self):
        """Test optimization failure handling."""
        config = {
            "auto_optimization": False
        }
        
        monitoring_system = PerformanceMonitoringSystem(config)
        await monitoring_system.initialize()
        
        try:
            # Test with invalid optimization type
            result = await monitoring_system.execute_optimization("invalid_strategy")
            
            assert result["success"] is False
            assert "error" in result
            
        finally:
            monitoring_system.stop()
    
    def test_resource_monitor_error_handling(self):
        """Test resource monitor error handling."""
        resource_monitor = SystemResourceMonitor()
        
        # Test with invalid psutil data
        with patch('psutil.cpu_percent', side_effect=Exception("Test error")):
            metrics = resource_monitor._collect_system_metrics()
            
            # Should return default metrics
            assert metrics.cpu_percent == 0.0
            assert metrics.memory_percent == 0.0


@pytest.mark.asyncio()
async def test_performance_monitoring_system_comprehensive():
    """Comprehensive test of the performance monitoring system."""
    config = {
        "auto_optimization": False,
        "monitoring_interval": 0.1,
        "max_history_size": 10
    }
    
    # Create system
    monitoring_system = PerformanceMonitoringSystem(config)
    await monitoring_system.initialize()
    
    try:
        # Test 1: System Health Check
        health = await monitoring_system.get_system_health()
        assert health["status"] in ["healthy", "degraded", "critical", "error"]
        
        # Test 2: Performance Report
        report = await monitoring_system.get_performance_report()
        assert report["version"] == "V0.3.7"
        assert len(report["recommendations"]) > 0
        
        # Test 3: Multiple Optimizations
        optimizations = ["memory_management", "cpu_optimization", "cache_optimization"]
        for opt_type in optimizations:
            result = await monitoring_system.execute_optimization(opt_type)
            assert result["success"] is True
        
        # Test 4: Final Health Check
        final_health = await monitoring_system.get_system_health()
        assert "uptime_seconds" in final_health
        assert final_health["uptime_seconds"] > 0
        
        # Test 5: Report Consistency
        final_report = await monitoring_system.get_performance_report()
        assert final_report["version"] == "V0.3.7"
        assert "performance_metrics" in final_report
        
    finally:
        monitoring_system.stop()


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_performance_monitoring_system_comprehensive())
    print("V0.3.7 Performance Monitoring System Test completed successfully!")