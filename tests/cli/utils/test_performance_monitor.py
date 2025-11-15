"""
测试性能监控系统
遵循TDD原则 - 先写测试，后写实现
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional
import psutil
from pathlib import Path


class TestPerformanceMonitorBasics:
    """测试性能监控器基础功能"""

    def test_performance_monitor_class_exists(self):
        """测试性能监控器类是否存在"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        # Test instantiation
        monitor = PerformanceMonitor()

        # Verify attributes
        assert hasattr(monitor, 'metrics')
        assert hasattr(monitor, 'current_measurements')
        assert hasattr(monitor, 'command_measurements')

    def test_performance_monitor_initialization(self):
        """测试性能监控器初始化"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Verify initial state
        assert isinstance(monitor.metrics, dict)
        assert isinstance(monitor.current_measurements, dict)
        assert isinstance(monitor.command_measurements, dict)

        # Verify metrics structure
        assert 'total_commands' in monitor.metrics
        assert 'total_duration' in monitor.metrics
        assert 'avg_duration' in monitor.metrics
        assert 'max_duration' in monitor.metrics
        assert 'min_duration' in monitor.metrics

        # Verify initial values
        assert monitor.metrics['total_commands'] == 0
        assert monitor.metrics['total_duration'] == 0.0
        assert monitor.metrics['avg_duration'] == 0.0
        assert monitor.metrics['max_duration'] == 0.0
        assert monitor.metrics['min_duration'] == float('inf')

    def test_measure_command_context_manager(self):
        """测试命令测量上下文管理器"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Test context manager exists and returns async context manager
        assert hasattr(monitor, 'measure_command')
        context_manager = monitor.measure_command("test")
        assert hasattr(context_manager, '__aenter__')
        assert hasattr(context_manager, '__aexit__')

    @pytest.mark.asyncio
    async def test_measure_command_basic_functionality(self):
        """测试命令测量基本功能"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Test successful measurement
        async with monitor.measure_command("test_command") as metrics:
            assert 'command_name' in metrics
            assert metrics['command_name'] == "test_command"
            assert 'start_time' in metrics
            assert 'start_memory' in metrics
            assert isinstance(metrics['start_time'], float)
            assert isinstance(metrics['start_memory'], float)

        # Verify metrics recorded
        assert 'test_command' in monitor.command_measurements
        assert monitor.metrics['total_commands'] == 1
        # Allow for very small duration due to precision
        assert monitor.metrics['total_duration'] >= 0

    @pytest.mark.asyncio
    async def test_measure_command_with_delay(self):
        """测试带延迟的命令测量"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()
        delay = 0.1  # 100ms

        start_time = time.time()
        async with monitor.measure_command("delayed_command") as metrics:
            await asyncio.sleep(delay)

        end_time = time.time()
        actual_duration = end_time - start_time

        # Verify duration is recorded
        assert 'duration' in metrics
        assert metrics['duration'] >= delay
        assert actual_duration >= delay

    @pytest.mark.asyncio
    async def test_measure_command_with_exception(self):
        """测试命令异常时的测量"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Test measurement with exception
        with pytest.raises(ValueError):
            async with monitor.measure_command("error_command"):
                raise ValueError("Test error")

        # Verify metrics still recorded
        assert 'error_command' in monitor.command_measurements
        assert monitor.metrics['total_commands'] == 1
        # Allow for very small duration due to precision
        assert monitor.metrics['total_duration'] >= 0

    @pytest.mark.asyncio
    async def test_measure_command_memory_tracking(self):
        """测试内存使用跟踪"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        async with monitor.measure_command("memory_test") as metrics:
            # Verify memory tracking
            assert 'start_memory' in metrics
            assert 'end_memory' in metrics
            assert 'memory_delta' in metrics
            assert isinstance(metrics['start_memory'], float)
            assert isinstance(metrics['end_memory'], float)
            assert isinstance(metrics['memory_delta'], float)

        # Verify memory delta calculation
        command_metrics = monitor.command_measurements['memory_test']
        memory_delta = command_metrics['memory_delta']
        assert isinstance(memory_delta, float)

    @pytest.mark.asyncio
    async def test_concurrent_command_measurements(self):
        """测试并发命令测量"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Create multiple concurrent measurements
        async def dummy_command(command_id):
            async with monitor.measure_command(f"command_{command_id}") as metrics:
                await asyncio.sleep(0.01)  # 10ms
                return metrics

        # Run commands concurrently
        tasks = [dummy_command(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all commands measured
        assert len([r for r in results if not isinstance(r, Exception)]) == 5
        assert monitor.metrics['total_commands'] == 5

        # Verify each command has metrics
        for i in range(5):
            assert f"command_{i}" in monitor.command_measurements

    @pytest.mark.asyncio
    async def test_get_performance_stats(self):
        """测试获取性能统计"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Run some commands to generate stats
        commands = []
        for i in range(3):
            async with monitor.measure_command(f"stats_test_{i}"):
                await asyncio.sleep(0.01)
                commands.append(f"stats_test_{i}")

        stats = monitor.get_performance_stats()

        # Verify stats structure
        assert isinstance(stats, dict)
        assert 'total_commands' in stats
        assert 'total_duration' in stats
        assert 'avg_duration' in stats
        assert 'max_duration' in stats
        assert 'min_duration' in stats
        assert 'command_details' in stats

        # Verify values
        assert stats['total_commands'] == 3
        assert stats['total_duration'] > 0
        assert stats['avg_duration'] > 0
        assert stats['max_duration'] > 0
        assert stats['min_duration'] > 0
        assert stats['min_duration'] <= stats['avg_duration'] <= stats['max_duration']

        # Verify command details
        command_details = stats['command_details']
        for cmd in commands:
            assert cmd in command_details
            assert 'duration' in command_details[cmd]
            assert 'memory_delta' in command_details[cmd]

    def test_reset_stats(self):
        """测试重置统计"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Simulate some activity
        monitor.metrics['total_commands'] = 10
        monitor.metrics['total_duration'] = 15.5
        monitor.command_measurements['test_command'] = {
            'duration': 1.5,
            'memory_delta': 1024
        }

        # Reset stats
        monitor.reset_stats()

        # Verify reset
        assert monitor.metrics['total_commands'] == 0
        assert monitor.metrics['total_duration'] == 0.0
        assert monitor.metrics['avg_duration'] == 0.0
        assert monitor.metrics['max_duration'] == 0.0
        assert monitor.metrics['min_duration'] == float('inf')
        assert monitor.command_measurements == {}

    def test_get_current_measurements(self):
        """测试获取当前测量值"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # No active measurements initially
        current = monitor.get_current_measurements()
        assert isinstance(current, dict)
        assert len(current) == 0

        # Simulate active measurement
        monitor.current_measurements['test'] = {
            'command_name': 'test',
            'start_time': time.time(),
            'duration': 0.5
        }

        current = monitor.get_current_measurements()
        assert 'test' in current
        assert current['test']['command_name'] == 'test'

    def test_performance_thresholds(self):
        """测试性能阈值检查"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Test threshold checking
        assert monitor.is_within_threshold(1.0, 2.0) == True
        assert monitor.is_within_threshold(2.5, 2.0) == False
        assert monitor.is_within_threshold(2.0, 2.0) == True

    def test_memory_usage_tracking(self):
        """测试内存使用跟踪功能"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Test memory tracking methods
        assert hasattr(monitor, '_get_memory_usage')
        assert callable(monitor._get_memory_usage)

        # Test memory usage function
        memory_usage = monitor._get_memory_usage()
        assert isinstance(memory_usage, float)
        assert memory_usage > 0

    def test_command_measurements_limit(self):
        """测试命令测量数量限制"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor(max_measurements=2)

        # Simulate exceeding limit
        monitor.command_measurements['cmd1'] = {'duration': 1.0}
        monitor.command_measurements['cmd2'] = {'duration': 1.0}
        monitor.command_measurements['cmd3'] = {'duration': 1.0}

        # Should limit to max_measurements
        assert len(monitor.command_measurements) == 2
        assert 'cmd1' in monitor.command_measurements
        assert 'cmd2' in monitor.command_measurements
        assert 'cmd3' not in monitor.command_measurements


class TestPerformanceMetricsIntegration:
    """测试性能指标集成功能"""

    @pytest.mark.asyncio
    async def test_slow_command_detection(self):
        """测试慢命令检测"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor(slow_threshold=0.05)  # 50ms

        # Fast command (should not be detected as slow)
        async with monitor.measure_command("fast_command"):
            await asyncio.sleep(0.01)  # 10ms

        slow_commands = monitor.get_slow_commands()
        assert len(slow_commands) == 0

        # Slow command (should be detected)
        async with monitor.measure_command("slow_command"):
            await asyncio.sleep(0.1)  # 100ms

        slow_commands = monitor.get_slow_commands()
        assert len(slow_commands) == 1
        assert 'slow_command' in slow_commands
        assert slow_commands['slow_command']['duration'] >= 0.05

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """测试内存泄漏检测"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor(memory_threshold=10 * 1024 * 1024)  # 10MB

        # Normal memory usage
        async with monitor.measure_command("normal_command"):
            # Simulate small memory allocation
            data = [0] * 1000  # ~8KB
            del data

        high_memory_commands = monitor.get_high_memory_commands()
        assert len(high_memory_commands) == 0

        # High memory usage (simulate)
        with patch('daip_live.cli.utils.performance_monitor.psutil.Process') as mock_process:
            # Mock high memory usage
            mock_process_instance = MagicMock()
            mock_process_instance.memory_info.return_value.rss = 20 * 1024 * 1024  # 20MB
            mock_process.return_value = mock_process_instance

            async with monitor.measure_command("high_memory_command"):
                # This will trigger memory leak detection
                pass

        high_memory_commands = monitor.get_high_memory_commands()
        assert len(high_memory_commands) == 1
        assert 'high_memory_command' in high_memory_commands

    def test_performance_report_generation(self):
        """测试性能报告生成"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Simulate some performance data
        monitor.metrics.update({
            'total_commands': 10,
            'total_duration': 15.5,
            'avg_duration': 1.55,
            'max_duration': 3.2,
            'min_duration': 0.3
        })

        monitor.command_measurements.update({
            'command1': {'duration': 1.0, 'memory_delta': 1024},
            'command2': {'duration': 2.0, 'memory_delta': 2048},
            'command3': {'duration': 3.0, 'memory_delta': 3072}
        })

        # Generate performance report
        report = monitor.generate_performance_report()

        # Verify report structure
        assert isinstance(report, str)
        assert 'Performance Report' in report
        assert 'Total Commands: 10' in report
        assert 'Average Duration: 1.55s' in report
        assert 'Max Duration: 3.20s' in report
        assert 'Min Duration: 0.30s' in report

    def test_export_metrics(self):
        """测试指标导出功能"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Add some data
        monitor.metrics['total_commands'] = 5
        monitor.command_measurements['test'] = {'duration': 1.0}

        # Test JSON export
        json_data = monitor.export_metrics('json')
        assert isinstance(json_data, str)
        import json
        parsed_data = json.loads(json_data)
        assert parsed_data['metrics']['total_commands'] == 5
        assert parsed_data['command_measurements']['test']['duration'] == 1.0

        # Test CSV export
        csv_data = monitor.export_metrics('csv')
        assert isinstance(csv_data, str)
        assert 'total_commands' in csv_data
        assert '5' in csv_data

    @pytest.mark.asyncio
    async def test_real_time_monitoring(self):
        """测试实时监控功能"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Start real-time monitoring
        monitor.start_monitoring()

        # Run commands while monitoring
        for i in range(3):
            async with monitor.measure_command(f"real_time_test_{i}"):
                await asyncio.sleep(0.01)

        # Stop monitoring
        monitor.stop_monitoring()

        # Verify monitoring data
        assert monitor.metrics['total_commands'] == 3
        assert len(monitor.command_measurements) == 3

    def test_monitoring_state_management(self):
        """测试监控状态管理"""
        from daip_live.cli.utils.performance_monitor import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Initial state
        assert not monitor.is_monitoring

        # Start monitoring
        monitor.start_monitoring()
        assert monitor.is_monitoring

        # Stop monitoring
        monitor.stop_monitoring()
        assert not monitor.is_monitoring

        # Can start again
        monitor.start_monitoring()
        assert monitor.is_monitoring