"""
Performance Testing Suite for DAIP-LIVE P7 GUI

This module implements performance benchmarks and stress tests for the P7 GUI system.
"""

import asyncio
import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath('.'))

@dataclass
class PerformanceResult:
    """Data class for performance test results."""
    test_name: str
    duration: float
    memory_before: float
    memory_after: float
    cpu_usage: float
    success: bool
    details: Optional[Dict[str, Any]] = None


class PerformanceTester:
    """
    Performance tester for P7 GUI system.
    
    This tester validates performance characteristics including:
    - Startup time
    - Response latency
    - Memory usage
    - CPU consumption
    - Throughput under load
    """
    
    def __init__(self):
        """Initialize the performance tester."""
        self._results: List[PerformanceResult] = []
        self._start_time = 0
        self._end_time = 0
    
    async def test_startup_performance(self) -> PerformanceResult:
        """
        Test application startup performance.
        
        Returns:
            Performance test result
        """
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Test GUI startup performance
            import customtkinter as ctk
            import sys
            
            # Create and configure root window
            root = ctk.CTk()
            root.withdraw()  # Don't display during test
            
            # Import all required modules to simulate full load
            start_import_time = time.time()
            
            # Import core modules
            from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel
            from src.daip_live.p7_gui_v1.views.main_window import MainWindow
            from src.daip_live.p7_gui_v1.container import ServiceContainer
            from src.daip_live.p7_gui_v1.theme.theme_manager import ThemeManager
            from unittest.mock import Mock
            
            # Create mock services
            mock_interaction = Mock()
            vm = MainViewModel(mock_interaction)
            window = MainWindow(root, vm)
            
            end_time = time.time()
            total_duration = end_time - start_time
            import_duration = end_time - start_import_time
            
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            cpu_usage = psutil.cpu_percent()
            
            # Cleanup
            root.destroy()
            
            success = total_duration <= 5.0  # Should start in under 5 seconds
            
            return PerformanceResult(
                test_name="Startup Performance",
                duration=total_duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=cpu_usage,
                success=success,
                details={
                    "import_duration": import_duration,
                    "memory_increase": memory_after - memory_before,
                    "target_duration": 5.0,
                    "actual_duration": total_duration
                }
            )
            
        except Exception as e:
            end_time = time.time()
            total_duration = end_time - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            return PerformanceResult(
                test_name="Startup Performance",
                duration=total_duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=psutil.cpu_percent(),
                success=False,
                details={
                    "error": str(e),
                    "duration": total_duration
                }
            )
    
    async def test_response_latency(self) -> PerformanceResult:
        """
        Test UI response latency.
        
        Returns:
            Performance test result
        """
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Create a mock GUI to test response times
            import customtkinter as ctk
            import sys
            
            root = ctk.CTk()
            root.withdraw()
            root.geometry("800x600")
            
            # Create a simple button and measure click response time
            result_container = {"response_time": 0}
            
            def on_click():
                nonlocal result_container
                click_time = time.time()
                result_container["response_time"] = click_time - start_click_time
            
            button = ctk.CTkButton(root, text="Click Me", command=on_click)
            button.grid(row=0, column=0, padx=10, pady=10)
            
            # Simulate a click and measure response
            start_click_time = time.time()
            button.invoke()  # Directly invoke to simulate click
            
            end_time = time.time()
            duration = end_time - start_time
            
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            cpu_usage = psutil.cpu_percent()
            
            root.destroy()
            
            # Check if response was timely (under 200ms)
            success = result_container["response_time"] <= 0.2
            
            return PerformanceResult(
                test_name="Response Latency",
                duration=result_container["response_time"],
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=cpu_usage,
                success=success,
                details={
                    "click_time": result_container["response_time"],
                    "target_response": 0.2,  # 200ms
                    "actual_response": result_container["response_time"]
                }
            )
            
        except Exception as e:
            end_time = time.time()
            total_duration = end_time - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            return PerformanceResult(
                test_name="Response Latency",
                duration=total_duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=psutil.cpu_percent(),
                success=False,
                details={
                    "error": str(e),
                    "duration": total_duration
                }
            )
    
    async def test_memory_usage(self) -> PerformanceResult:
        """
        Test memory usage under normal operation.
        
        Returns:
            Performance test result
        """
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()
        
        try:
            # Simulate normal GUI operations
            import customtkinter as ctk
            import sys
            
            root = ctk.CTk()
            root.withdraw()
            
            # Create multiple UI components to test memory growth
            frames = []
            for i in range(10):
                frame = ctk.CTkFrame(root)
                label = ctk.CTkLabel(frame, text=f"Test Component {i}")
                label.pack()
                frames.append(frame)
            
            # Update UI multiple times to simulate activity
            for i in range(100):
                # Simulate UI activity
                root.update_idletasks()
                await asyncio.sleep(0.01)  # Small delay to allow other tasks
            
            end_time = time.time()
            duration = end_time - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            cpu_usage = psutil.cpu_percent()
            
            # Check if memory usage stayed reasonable (under 500MB)
            success = memory_after <= 500.0
            
            root.destroy()
            
            return PerformanceResult(
                test_name="Memory Usage",
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=cpu_usage,
                success=success,
                details={
                    "memory_growth": memory_after - memory_before,
                    "target_memory": 500.0,
                    "actual_memory": memory_after
                }
            )
            
        except Exception as e:
            end_time = time.time()
            total_duration = end_time - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            return PerformanceResult(
                test_name="Memory Usage",
                duration=total_duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=psutil.cpu_percent(),
                success=False,
                details={
                    "error": str(e),
                    "memory_increase": memory_after - memory_before
                }
            )
    
    async def test_concurrent_users(self) -> PerformanceResult:
        """
        Test performance under concurrent user simulation.
        
        Returns:
            Performance test result
        """
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Simulate multiple concurrent operations
            import asyncio
            
            async def simulate_concurrent_task(task_id: int) -> float:
                """Simulate a concurrent GUI task."""
                task_start = time.time()
                
                # Simulate processing
                await asyncio.sleep(0.05)  # Short processing time
                import random
                await asyncio.sleep(random.uniform(0.01, 0.05))  # Random additional processing
                
                return time.time() - task_start
            
            # Run 10 concurrent tasks
            tasks = [simulate_concurrent_task(i) for i in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            duration = end_time - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            cpu_usage = psutil.cpu_percent()
            
            # Calculate average task time
            successful_results = [r for r in results if isinstance(r, float)]
            avg_task_time = sum(successful_results) / len(successful_results) if successful_results else 0
            
            # Success if average task time is reasonable (under 100ms)
            success = avg_task_time <= 0.1 and len(successful_results) == 10
            
            return PerformanceResult(
                test_name="Concurrent Performance",
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=cpu_usage,
                success=success,
                details={
                    "avg_task_time": avg_task_time,
                    "successful_tasks": len(successful_results),
                    "total_tasks": 10,
                    "target_avg_time": 0.1
                }
            )
            
        except Exception as e:
            end_time = time.time()
            total_duration = end_time - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            return PerformanceResult(
                test_name="Concurrent Performance",
                duration=total_duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=psutil.cpu_percent(),
                success=False,
                details={
                    "error": str(e),
                    "successful_tasks": 0,
                    "total_tasks": 10
                }
            )
    
    async def run_all_performance_tests(self) -> List[PerformanceResult]:
        """
        Run all performance tests.
        
        Returns:
            List of performance test results
        """
        print("🏃 Running Performance Tests...")
        
        tests_to_run = [
            self.test_startup_performance,
            self.test_response_latency,
            self.test_memory_usage,
            self.test_concurrent_users,
        ]
        
        results = []
        for test_func in tests_to_run:
            print(f"  Testing: {test_func.__name__.replace('test_', '').replace('_', ' ').title()}...")
            result = await test_func()
            results.append(result)
            self._results.append(result)
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"    {status} Duration: {result.duration:.3f}s, Memory: {result.memory_after:.1f}MB")
        
        return results
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self._results:
            return {"message": "No performance tests have been run yet"}
        
        total_tests = len(self._results)
        passed_tests = sum(1 for result in self._results if result.success)
        failed_tests = total_tests - passed_tests
        
        # Calculate averages
        total_duration = sum(result.duration for result in self._results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        avg_memory_before = sum(result.memory_before for result in self._results) / total_tests if total_tests > 0 else 0
        avg_memory_after = sum(result.memory_after for result in self._results) / total_tests if total_tests > 0 else 0
        avg_cpu_usage = sum(result.cpu_usage for result in self._results) / total_tests if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "average_initial_memory_mb": avg_memory_before,
            "average_final_memory_mb": avg_memory_after,
            "average_cpu_usage": avg_cpu_usage,
            "memory_increase_mb": avg_memory_after - avg_memory_before,
            "detailed_results": [
                {
                    "test": result.test_name,
                    "duration": result.duration,
                    "success": result.success,
                    "memory_before": result.memory_before,
                    "memory_after": result.memory_after,
                    "cpu_usage": result.cpu_usage,
                    "details": result.details
                }
                for result in self._results
            ]
        }
    
    def print_performance_report(self):
        """Print a formatted performance report."""
        report = self.generate_performance_report()
        
        print("\n" + "="*70)
        print(" PERFORMANCE TEST REPORT ")
        print("="*70)
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed:      {report['passed_tests']}")
        print(f"Failed:      {report['failed_tests']}")
        print(f"Success Rate: {report['success_rate']*100:.1f}%")
        print(f"Average Duration: {report['average_duration']:.3f}s")
        print(f"Average Memory: {report['average_final_memory_mb']:.1f}MB")
        print(f"Memory Increase: {report['memory_increase_mb']:.1f}MB")
        print(f"Average CPU: {report['average_cpu_usage']:.1f}%")
        print("="*70)
        
        for result in report.get('detailed_results', []):
            status = "✅ PASS" if result['success'] else "❌ FAIL" 
            print(f"{status} {result['test']:<30} {result['duration']:.3f}s")
        
        print("="*70)


# Convenience function to run performance tests
async def run_performance_tests() -> Dict[str, Any]:
    """
    Run the complete performance test suite.
    
    Returns:
        Dictionary with performance test results
    """
    tester = PerformanceTester()
    results = await tester.run_all_performance_tests()
    report = tester.generate_performance_report()
    
    tester.print_performance_report()
    
    return report


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_performance_tests())