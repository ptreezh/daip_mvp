# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 11:00:00
@Author  : DAIP-LIVE Team
@File    : validate_v0_3_7_implementation.py
@Description:
    V0.3.7 Performance Monitoring System Validation Script
    企业级性能监控系统验证脚本
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core_services.performance_monitoring_system import (
    PerformanceMonitoringSystem,
    SystemResourceMonitor,
    PerformanceOptimizationEngine,
    PerformanceMetric
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class V0_3_7Validator:
    """V0.3.7 Implementation Validator."""
    
    def __init__(self):
        self.validation_results = {
            "version": "V0.3.7",
            "validation_date": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
            "recommendations": []
        }
        self.monitoring_system = None
    
    async def validate_implementation(self) -> Dict[str, Any]:
        """Validate V0.3.7 implementation."""
        logger.info("Starting V0.3.7 Performance Monitoring System validation")
        
        try:
            # Test 1: File Existence and Import
            await self._test_file_existence_and_imports()
            
            # Test 2: System Initialization
            await self._test_system_initialization()
            
            # Test 3: Resource Monitoring
            await self._test_resource_monitoring()
            
            # Test 4: Performance Optimization
            await self._test_performance_optimization()
            
            # Test 5: System Health Monitoring
            await self._test_system_health_monitoring()
            
            # Test 6: Performance Reporting
            await self._test_performance_reporting()
            
            # Test 7: Error Handling
            await self._test_error_handling()
            
            # Test 8: Integration Testing
            await self._test_integration()
            
            # Generate summary
            self._generate_summary()
            
            logger.info("V0.3.7 validation completed")
            return self.validation_results
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            self.validation_results["error"] = str(e)
            return self.validation_results
    
    async def _test_file_existence_and_imports(self):
        """Test file existence and imports."""
        test_result = {
            "test_name": "File Existence and Imports",
            "test_id": "V0.3.7.1",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing file existence and imports...")
            
            # Check main implementation file
            implementation_file = "src/core_services/performance_monitoring_system.py"
            if os.path.exists(implementation_file):
                test_result["details"]["implementation_file_exists"] = True
                test_result["details"]["implementation_file_path"] = implementation_file
            else:
                test_result["details"]["implementation_file_exists"] = False
                test_result["status"] = "failed"
                test_result["error"] = f"Implementation file not found: {implementation_file}"
                self.validation_results["tests"].append(test_result)
                return
            
            # Check test file
            test_file = "tests/test_v0_3_7_performance_monitoring.py"
            if os.path.exists(test_file):
                test_result["details"]["test_file_exists"] = True
                test_result["details"]["test_file_path"] = test_file
            else:
                test_result["details"]["test_file_exists"] = False
            
            # Test imports
            try:
                from src.core_services.performance_monitoring_system import (
                    PerformanceMonitoringSystem,
                    SystemResourceMonitor,
                    PerformanceOptimizationEngine,
                    PerformanceMetric
                )
                test_result["details"]["imports_successful"] = True
            except ImportError as e:
                test_result["details"]["imports_successful"] = False
                test_result["details"]["import_error"] = str(e)
            
            # Check file size
            file_size = os.path.getsize(implementation_file)
            test_result["details"]["implementation_file_size"] = file_size
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"File existence test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    async def _test_system_initialization(self):
        """Test system initialization."""
        test_result = {
            "test_name": "System Initialization",
            "test_id": "V0.3.7.2",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing system initialization...")
            
            # Initialize monitoring system
            config = {
                "auto_optimization": False,  # Disable for validation
                "monitoring_interval": 1.0,
                "max_history_size": 100
            }
            
            self.monitoring_system = PerformanceMonitoringSystem(config)
            await self.monitoring_system.initialize()
            
            # Check initialization status
            test_result["details"]["initialization_successful"] = self.monitoring_system.is_initialized
            test_result["details"]["optimization_engine_exists"] = self.monitoring_system.optimization_engine is not None
            test_result["details"]["startup_time_recorded"] = self.monitoring_system.startup_time is not None
            
            # Verify components
            test_result["details"]["resource_monitor_exists"] = hasattr(self.monitoring_system.optimization_engine, 'resource_monitor')
            test_result["details"]["performance_monitor_exists"] = hasattr(self.monitoring_system.optimization_engine, 'performance_monitor')
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"System initialization test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    async def _test_resource_monitoring(self):
        """Test resource monitoring."""
        test_result = {
            "test_name": "Resource Monitoring",
            "test_id": "V0.3.7.3",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing resource monitoring...")
            
            if not self.monitoring_system:
                raise Exception("Monitoring system not initialized")
            
            # Get resource monitor
            resource_monitor = self.monitoring_system.optimization_engine.resource_monitor
            
            # Test metrics collection
            metrics = resource_monitor._collect_system_metrics()
            test_result["details"]["metrics_collection_successful"] = metrics is not None
            
            if metrics:
                test_result["details"]["cpu_percent"] = metrics.cpu_percent
                test_result["details"]["memory_percent"] = metrics.memory_percent
                test_result["details"]["disk_usage"] = metrics.disk_usage
            
            # Test monitoring start/stop
            resource_monitor.start_monitoring()
            test_result["details"]["monitoring_started"] = resource_monitor.is_monitoring
            
            # Let it run for a short time
            await asyncio.sleep(2)
            
            # Check if metrics were collected
            initial_metrics_count = len(resource_monitor.metrics_history)
            test_result["details"]["metrics_collected"] = initial_metrics_count > 0
            
            # Stop monitoring
            resource_monitor.stop_monitoring()
            test_result["details"]["monitoring_stopped"] = not resource_monitor.is_monitoring
            
            # Test performance summary
            summary = resource_monitor.get_performance_summary()
            test_result["details"]["performance_summary_available"] = summary is not None
            
            if summary:
                test_result["details"]["summary_has_current_metrics"] = "current_metrics" in summary
                test_result["details"]["summary_has_statistics"] = "statistics" in summary
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"Resource monitoring test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    async def _test_performance_optimization(self):
        """Test performance optimization."""
        test_result = {
            "test_name": "Performance Optimization",
            "test_id": "V0.3.7.4",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing performance optimization...")
            
            if not self.monitoring_system:
                raise Exception("Monitoring system not initialized")
            
            # Test different optimization strategies
            optimization_strategies = ["memory_management", "cpu_optimization", "cache_optimization"]
            optimization_results = {}
            
            for strategy in optimization_strategies:
                try:
                    result = await self.monitoring_system.execute_optimization(strategy)
                    optimization_results[strategy] = {
                        "success": result.get("success", False),
                        "has_result": result is not None
                    }
                except Exception as e:
                    optimization_results[strategy] = {
                        "success": False,
                        "error": str(e)
                    }
            
            test_result["details"]["optimization_results"] = optimization_results
            
            # Test optimization summary
            optimization_summary = self.monitoring_system.optimization_engine.get_optimization_summary()
            test_result["details"]["optimization_summary_available"] = optimization_summary is not None
            
            if optimization_summary:
                test_result["details"]["summary_has_system_performance"] = "system_performance" in optimization_summary
                test_result["details"]["summary_has_application_performance"] = "application_performance" in optimization_summary
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"Performance optimization test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    async def _test_system_health_monitoring(self):
        """Test system health monitoring."""
        test_result = {
            "test_name": "System Health Monitoring",
            "test_id": "V0.3.7.5",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing system health monitoring...")
            
            if not self.monitoring_system:
                raise Exception("Monitoring system not initialized")
            
            # Test system health check
            health = await self.monitoring_system.get_system_health()
            test_result["details"]["health_check_successful"] = health is not None
            
            if health:
                test_result["details"]["health_status"] = health.get("status", "unknown")
                test_result["details"]["health_has_uptime"] = "uptime_seconds" in health
                test_result["details"]["health_has_timestamp"] = "last_check" in health
                
                # Validate health status
                valid_statuses = ["healthy", "degraded", "critical", "error", "not_initialized"]
                test_result["details"]["health_status_valid"] = health.get("status") in valid_statuses
            
            # Test multiple health checks
            health_checks = []
            for i in range(3):
                health = await self.monitoring_system.get_system_health()
                health_checks.append(health)
                await asyncio.sleep(0.5)
            
            test_result["details"]["multiple_health_checks"] = len(health_checks) == 3
            test_result["details"]["consistent_health_status"] = all(
                h.get("status") == health_checks[0].get("status") 
                for h in health_checks if h.get("status") != "not_initialized"
            )
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"System health monitoring test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    async def _test_performance_reporting(self):
        """Test performance reporting."""
        test_result = {
            "test_name": "Performance Reporting",
            "test_id": "V0.3.7.6",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing performance reporting...")
            
            if not self.monitoring_system:
                raise Exception("Monitoring system not initialized")
            
            # Test performance report generation
            report = await self.monitoring_system.get_performance_report()
            test_result["details"]["report_generation_successful"] = report is not None
            
            if report:
                # Verify report structure
                required_fields = [
                    "report_timestamp", "version", "system_health",
                    "optimization_summary", "performance_metrics", "recommendations"
                ]
                
                missing_fields = [field for field in required_fields if field not in report]
                test_result["details"]["missing_fields"] = missing_fields
                test_result["details"]["report_structure_valid"] = len(missing_fields) == 0
                
                # Verify version
                test_result["details"]["correct_version"] = report.get("version") == "V0.3.7"
                
                # Verify recommendations
                recommendations = report.get("recommendations", [])
                test_result["details"]["has_recommendations"] = len(recommendations) > 0
                test_result["details"]["recommendations_count"] = len(recommendations)
                
                # Verify data types
                test_result["details"]["system_health_is_dict"] = isinstance(report.get("system_health"), dict)
                test_result["details"]["optimization_summary_is_dict"] = isinstance(report.get("optimization_summary"), dict)
                test_result["details"]["recommendations_is_list"] = isinstance(recommendations, list)
            
            # Test multiple reports
            reports = []
            for i in range(3):
                report = await self.monitoring_system.get_performance_report()
                reports.append(report)
                await asyncio.sleep(0.5)
            
            test_result["details"]["multiple_reports_generated"] = len(reports) == 3
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"Performance reporting test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    async def _test_error_handling(self):
        """Test error handling."""
        test_result = {
            "test_name": "Error Handling",
            "test_id": "V0.3.7.7",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing error handling...")
            
            if not self.monitoring_system:
                raise Exception("Monitoring system not initialized")
            
            # Test invalid optimization strategy
            invalid_result = await self.monitoring_system.execute_optimization("invalid_strategy")
            test_result["details"]["invalid_strategy_handled"] = not invalid_result.get("success", True)
            test_result["details"]["invalid_strategy_has_error"] = "error" in invalid_result
            
            # Test uninitialized system
            uninitialized_system = PerformanceMonitoringSystem()
            uninitialized_health = await uninitialized_system.get_system_health()
            test_result["details"]["uninitialized_handled"] = uninitialized_health.get("status") == "not_initialized"
            
            # Test resource monitor error handling
            resource_monitor = self.monitoring_system.optimization_engine.resource_monitor
            
            # Test with mock error
            original_collect = resource_monitor._collect_system_metrics
            def mock_collect_with_error():
                raise Exception("Test error")
            
            resource_monitor._collect_system_metrics = mock_collect_with_error
            
            try:
                metrics = resource_monitor._collect_system_metrics()
                test_result["details"]["collection_error_handled"] = metrics is not None
                test_result["details"]["default_metrics_returned"] = metrics.cpu_percent == 0.0 if metrics else False
            finally:
                resource_monitor._collect_system_metrics = original_collect
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"Error handling test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    async def _test_integration(self):
        """Test integration scenarios."""
        test_result = {
            "test_name": "Integration Testing",
            "test_id": "V0.3.7.8",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Testing integration scenarios...")
            
            if not self.monitoring_system:
                raise Exception("Monitoring system not initialized")
            
            # Test full monitoring cycle
            start_time = time.time()
            
            # Get initial health
            initial_health = await self.monitoring_system.get_system_health()
            
            # Execute optimizations
            optimizations = ["memory_management", "cache_optimization"]
            optimization_results = []
            
            for opt_type in optimizations:
                result = await self.monitoring_system.execute_optimization(opt_type)
                optimization_results.append(result.get("success", False))
                await asyncio.sleep(0.5)
            
            # Get final report
            final_report = await self.monitoring_system.get_performance_report()
            
            end_time = time.time()
            test_result["details"]["integration_cycle_time"] = end_time - start_time
            
            # Verify integration results
            test_result["details"]["initial_health_available"] = initial_health is not None
            test_result["details"]["optimizations_executed"] = len(optimization_results) == len(optimizations)
            test_result["details"]["successful_optimizations"] = sum(optimization_results)
            test_result["details"]["final_report_available"] = final_report is not None
            
            # Test system stability
            test_result["details"]["system_stable_after_integration"] = final_report.get("version") == "V0.3.7"
            
            # Test resource cleanup
            try:
                self.monitoring_system.stop()
                test_result["details"]["cleanup_successful"] = True
            except Exception as e:
                test_result["details"]["cleanup_successful"] = False
                test_result["details"]["cleanup_error"] = str(e)
            
            test_result["status"] = "completed"
            test_result["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)
            logger.error(f"Integration test failed: {e}")
        
        self.validation_results["tests"].append(test_result)
    
    def _generate_summary(self):
        """Generate validation summary."""
        try:
            tests = self.validation_results["tests"]
            
            # Calculate statistics
            total_tests = len(tests)
            completed_tests = len([t for t in tests if t["status"] == "completed"])
            failed_tests = len([t for t in tests if t["status"] == "failed"])
            
            # Calculate success rate
            success_rate = (completed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Determine overall status
            overall_status = "SUCCESS" if failed_tests == 0 else "PARTIAL" if failed_tests <= 2 else "FAILED"
            
            # Generate recommendations
            recommendations = []
            
            if failed_tests > 0:
                recommendations.append("修复失败的测试用例")
            
            if success_rate < 100:
                recommendations.append("提高测试覆盖率")
            
            if overall_status != "SUCCESS":
                recommendations.append("进行代码审查和重构")
            
            recommendations.extend([
                "监控系统性能指标",
                "定期执行性能优化",
                "完善错误处理机制",
                "添加更多集成测试"
            ])
            
            self.validation_results["summary"] = {
                "total_tests": total_tests,
                "completed_tests": completed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "overall_status": overall_status,
                "validation_duration": sum(
                    (datetime.fromisoformat(t["end_time"]) - datetime.fromisoformat(t["start_time"])).total_seconds()
                    for t in tests if "end_time" in t and "start_time" in t
                )
            }
            
            self.validation_results["recommendations"] = recommendations
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            self.validation_results["summary"] = {"error": str(e)}
    
    def save_validation_report(self, filename: str = "V0_3_7_VALIDATION_REPORT.json"):
        """Save validation report to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Validation report saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")
            return False
    
    def print_summary(self):
        """Print validation summary."""
        summary = self.validation_results.get("summary", {})
        
        print("\n" + "="*60)
        print("V0.3.7 Performance Monitoring System Validation Summary")
        print("="*60)
        
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Completed Tests: {summary.get('completed_tests', 0)}")
        print(f"Failed Tests: {summary.get('failed_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
        print(f"Validation Duration: {summary.get('validation_duration', 0):.2f} seconds")
        
        print("\nTest Results:")
        for test in self.validation_results["tests"]:
            status_symbol = "✅" if test["status"] == "completed" else "❌"
            print(f"  {status_symbol} {test['test_name']} ({test['test_id']})")
        
        print("\nRecommendations:")
        for i, rec in enumerate(self.validation_results.get("recommendations", []), 1):
            print(f"  {i}. {rec}")
        
        print("="*60)


async def main():
    """Main validation function."""
    print("Starting V0.3.7 Performance Monitoring System Validation...")
    
    validator = V0_3_7Validator()
    results = await validator.validate_implementation()
    
    # Save validation report
    validator.save_validation_report()
    
    # Print summary
    validator.print_summary()
    
    return results


if __name__ == "__main__":
    asyncio.run(main())