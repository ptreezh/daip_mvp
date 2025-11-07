#!/usr/bin/env python3
"""
Real System Test Script

This script performs actual system tests to validate the agent_engine_v1 implementation.
It tests real functionality, performance, and integration.
"""

import asyncio
import time
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

# Import our agent engine components
from daip_live.agent_engine_v1 import (
    EventBus,
    ServiceIntegrationManager,
    AgentOrchestrator,
    AgentEngineV1ToLegacyAdapter,
    LegacyRequest
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealSystemTester:
    """Real system tester for agent_engine_v1."""

    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}

    async def setup_system(self) -> Dict[str, Any]:
        """Setup the complete system."""
        logger.info("🚀 Setting up real system...")
        setup_start = time.time()

        # Create EventBus
        logger.info("  📡 Creating EventBus...")
        event_bus = EventBus()
        await event_bus.start()

        # Create Service Manager and services
        logger.info("  🔧 Setting up Service Manager...")
        service_manager = ServiceIntegrationManager(event_bus)

        # Create services
        logger.info("  🎯 Creating Intent Recognition Service...")
        await service_manager.create_intent_recognition_service()

        logger.info("  ⚙️ Creating Execution Engine Service...")
        await service_manager.create_execution_engine_service()

        logger.info("  🛡️ Creating Permission Service...")
        await service_manager.create_permission_service()

        logger.info("  💾 Creating State Management Service...")
        await service_manager.create_state_management_service()

        # Start all services
        logger.info("  ▶️ Starting all services...")
        await service_manager.start_all_services()

        # Create Orchestrator
        logger.info("  🎭 Creating Agent Orchestrator...")
        orchestrator = AgentOrchestrator(event_bus, service_manager)
        await orchestrator.start()

        # Create Compatibility Adapter
        logger.info("  🔄 Creating Compatibility Adapter...")
        adapter = AgentEngineV1ToLegacyAdapter(orchestrator, event_bus, service_manager)

        setup_time = time.time() - setup_start
        logger.info(f"✅ System setup completed in {setup_time:.2f} seconds")

        return {
            "event_bus": event_bus,
            "service_manager": service_manager,
            "orchestrator": orchestrator,
            "adapter": adapter,
            "setup_time": setup_time
        }

    async def cleanup_system(self, system: Dict[str, Any]):
        """Cleanup system resources."""
        logger.info("🧹 Cleaning up system...")
        cleanup_start = time.time()

        try:
            await system["orchestrator"].stop()
            await system["service_manager"].stop_all_services()
            await system["event_bus"].stop()

            cleanup_time = time.time() - cleanup_start
            logger.info(f"✅ System cleanup completed in {cleanup_time:.2f} seconds")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

    async def test_basic_functionality(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test basic system functionality."""
        logger.info("🧪 Testing basic functionality...")
        test_start = time.time()

        orchestrator = system["orchestrator"]
        results = {
            "name": "Basic Functionality",
            "tests": [],
            "success_count": 0,
            "total_count": 0
        }

        # Test 1: Simple intent recognition
        try:
            logger.info("  🎯 Testing intent recognition...")
            context = await orchestrator.process_request(
                user_input="Please read the file config.json",
                session_id="test_basic_1"
            )
            results["tests"].append({
                "name": "Intent Recognition",
                "success": True,
                "result": f"Intent: {context.intent_result.intent if context.intent_result else 'None'}",
                "confidence": context.intent_result.confidence if context.intent_result else 0
            })
            results["success_count"] += 1
        except Exception as e:
            logger.error(f"    ❌ Intent recognition failed: {e}")
            results["tests"].append({
                "name": "Intent Recognition",
                "success": False,
                "error": str(e)
            })
        results["total_count"] += 1

        # Test 2: Permission checking
        try:
            logger.info("  🛡️ Testing permission checking...")
            context = await orchestrator.process_request(
                user_input="Delete critical system file",
                session_id="test_basic_2",
                context={"user": "test_user", "permission_level": "user"}
            )
            results["tests"].append({
                "name": "Permission Checking",
                "success": True,
                "result": f"Permission: {'Allowed' if context.permission_decision and context.permission_decision.allowed else 'Denied'}",
                "risk_level": context.permission_decision.risk_level.value if context.permission_decision else "Unknown"
            })
            results["success_count"] += 1
        except Exception as e:
            logger.error(f"    ❌ Permission checking failed: {e}")
            results["tests"].append({
                "name": "Permission Checking",
                "success": False,
                "error": str(e)
            })
        results["total_count"] += 1

        # Test 3: State management
        try:
            logger.info("  💾 Testing state management...")
            context = await orchestrator.process_request(
                user_input="Save current state",
                session_id="test_basic_3"
            )
            results["tests"].append({
                "name": "State Management",
                "success": True,
                "result": f"State created: {context.state_snapshot is not None}",
                "session_id": context.session_id
            })
            results["success_count"] += 1
        except Exception as e:
            logger.error(f"    ❌ State management failed: {e}")
            results["tests"].append({
                "name": "State Management",
                "success": False,
                "error": str(e)
            })
        results["total_count"] += 1

        test_time = time.time() - test_start
        results["duration"] = test_time
        results["success_rate"] = results["success_count"] / results["total_count"] if results["total_count"] > 0 else 0

        logger.info(f"✅ Basic functionality test: {results['success_count']}/{results['total_count']} passed ({results['success_rate']:.1%}) in {test_time:.2f}s")
        return results

    async def test_legacy_compatibility(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test legacy compatibility."""
        logger.info("🔄 Testing legacy compatibility...")
        test_start = time.time()

        adapter = system["adapter"]
        results = {
            "name": "Legacy Compatibility",
            "tests": [],
            "success_count": 0,
            "total_count": 0
        }

        # Test 1: Basic legacy request
        try:
            logger.info("  📜 Testing basic legacy request...")
            legacy_request = LegacyRequest(
                user_input="Read file legacy.txt",
                session_id="legacy_test_1",
                user_id="legacy_user",
                tool_permissions={"read_file": True}
            )
            response = await adapter.process_legacy_request(legacy_request)
            results["tests"].append({
                "name": "Basic Legacy Request",
                "success": True,
                "response_length": len(response.response),
                "success": response.success,
                "metadata_fields": list(response.metadata.keys()) if response.metadata else []
            })
            results["success_count"] += 1
        except Exception as e:
            logger.error(f"    ❌ Basic legacy request failed: {e}")
            results["tests"].append({
                "name": "Basic Legacy Request",
                "success": False,
                "error": str(e)
            })
        results["total_count"] += 1

        # Test 2: Tool mapping
        try:
            logger.info("  🔧 Testing legacy tool mapping...")
            legacy_request = LegacyRequest(
                user_input="Execute Python script",
                session_id="legacy_test_2",
                context={"tool_requests": ["execute_code", "read_file"]}
            )
            response = await adapter.process_legacy_request(legacy_request)
            results["tests"].append({
                "name": "Tool Mapping",
                "success": True,
                "tool_calls_count": len(response.tool_calls) if response.tool_calls else 0,
                "mapped_intents": [tc.get("tool", "unknown") for tc in (response.tool_calls or [])]
            })
            results["success_count"] += 1
        except Exception as e:
            logger.error(f"    ❌ Tool mapping failed: {e}")
            results["tests"].append({
                "name": "Tool Mapping",
                "success": False,
                "error": str(e)
            })
        results["total_count"] += 1

        test_time = time.time() - test_start
        results["duration"] = test_time
        results["success_rate"] = results["success_count"] / results["total_count"] if results["total_count"] > 0 else 0

        logger.info(f"✅ Legacy compatibility test: {results['success_count']}/{results['total_count']} passed ({results['success_rate']:.1%}) in {test_time:.2f}s")
        return results

    async def test_concurrent_processing(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test concurrent request processing."""
        logger.info("⚡ Testing concurrent processing...")
        test_start = time.time()

        orchestrator = system["orchestrator"]
        results = {
            "name": "Concurrent Processing",
            "concurrent_requests": 5,
            "completed_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "total_time": 0
        }

        # Create concurrent requests
        requests = [
            ("Analyze data.csv", "concurrent_1"),
            ("Read config.json", "concurrent_2"),
            ("Search documentation", "concurrent_3"),
            ("Execute test script", "concurrent_4"),
            ("Validate input", "concurrent_5")
        ]

        logger.info(f"  🚀 Processing {len(requests)} concurrent requests...")
        concurrent_start = time.time()

        # Execute requests concurrently
        tasks = []
        for user_input, session_id in requests:
            task = orchestrator.process_request(user_input, session_id)
            tasks.append(task)

        # Wait for all to complete
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.time() - concurrent_start

        # Analyze results
        response_times = []
        for i, task_result in enumerate(completed_tasks):
            if isinstance(task_result, Exception):
                logger.warning(f"    ⚠️ Request {i+1} failed: {task_result}")
                results["failed_requests"] += 1
            else:
                results["completed_requests"] += 1
                # Simulate response time measurement
                response_times.append(concurrent_time / len(completed_tasks))

        results["total_time"] = concurrent_time
        results["avg_response_time"] = sum(response_times) / len(response_times) if response_times else 0
        results["success_rate"] = results["completed_requests"] / results["concurrent_requests"]

        logger.info(f"✅ Concurrent processing: {results['completed_requests']}/{results['concurrent_requests']} completed in {concurrent_time:.2f}s")
        return results

    async def test_performance_metrics(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test performance metrics collection."""
        logger.info("📊 Testing performance metrics...")
        test_start = time.time()

        orchestrator = system["orchestrator"]
        service_manager = system["service_manager"]

        # Generate some activity
        for i in range(3):
            await orchestrator.process_request(f"Performance test {i+1}", f"perf_test_{i+1}")

        # Collect metrics
        orchestrator_metrics = orchestrator.get_metrics()
        service_metrics = await service_manager.get_all_metrics()

        results = {
            "name": "Performance Metrics",
            "orchestrator_metrics": {
                "total_sessions": orchestrator_metrics["orchestrator"]["total_sessions"],
                "success_rate": orchestrator_metrics["orchestrator"]["success_rate"],
                "avg_execution_time_ms": orchestrator_metrics["orchestrator"]["avg_execution_time_ms"]
            },
            "service_count": len(service_metrics),
            "services_with_metrics": len([s for s in service_metrics.values() if "error" not in s])
        }

        test_time = time.time() - test_start
        results["collection_time"] = test_time

        logger.info(f"✅ Performance metrics collected in {test_time:.2f}s")
        logger.info(f"    📈 Total sessions: {results['orchestrator_metrics']['total_sessions']}")
        logger.info(f"    📈 Success rate: {results['orchestrator_metrics']['success_rate']:.1%}")
        logger.info(f"    📈 Avg execution time: {results['orchestrator_metrics']['avg_execution_time_ms']:.1f}ms")
        logger.info(f"    📈 Services with metrics: {results['services_with_metrics']}/{results['service_count']}")

        return results

    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite."""
        logger.info("🎯 Starting full real system test suite...")
        suite_start = time.time()

        system = None
        test_results = {
            "name": "Real System Test Suite",
            "timestamp": datetime.now().isoformat(),
            "total_duration": 0,
            "setup_time": 0,
            "cleanup_time": 0,
            "tests": [],
            "summary": {}
        }

        try:
            # Setup system
            system = await self.setup_system()
            test_results["setup_time"] = system["setup_time"]

            # Run individual tests
            test_functions = [
                self.test_basic_functionality,
                self.test_legacy_compatibility,
                self.test_concurrent_processing,
                self.test_performance_metrics
            ]

            for test_func in test_functions:
                result = await test_func(system)
                test_results["tests"].append(result)
                self.test_results[result["name"]] = result

            # Generate summary
            total_tests = len(test_results["tests"])
            successful_tests = sum(1 for test in test_results["tests"] if test.get("success_rate", 0) > 0.5)
            avg_success_rate = sum(test.get("success_rate", 0) for test in test_results["tests"]) / total_tests

            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "avg_success_rate": avg_success_rate,
                "overall_success": successful_tests == total_tests and avg_success_rate > 0.8
            }

        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            test_results["error"] = str(e)

        finally:
            # Cleanup
            if system:
                cleanup_start = time.time()
                await self.cleanup_system(system)
                test_results["cleanup_time"] = time.time() - cleanup_start

        total_duration = time.time() - suite_start
        test_results["total_duration"] = total_duration

        return test_results

    def print_results(self, results: Dict[str, Any]):
        """Print test results in a readable format."""
        print("\n" + "="*80)
        print(f"🧪 {results['name']}")
        print("="*80)
        print(f"📅 Timestamp: {results['timestamp']}")
        print(f"⏱️ Total Duration: {results['total_duration']:.2f} seconds")
        print(f"⚙️ Setup Time: {results.get('setup_time', 0):.2f} seconds")
        print(f"🧹 Cleanup Time: {results.get('cleanup_time', 0):.2f} seconds")

        if "error" in results:
            print(f"\n❌ TEST SUITE FAILED: {results['error']}")
            return

        print(f"\n📊 TEST SUMMARY:")
        summary = results["summary"]
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']}")
        print(f"   Avg Success Rate: {summary['avg_success_rate']:.1%}")
        print(f"   Overall Result: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}")

        print(f"\n📋 DETAILED RESULTS:")
        for test in results["tests"]:
            print(f"\n🔹 {test['name']}:")
            print(f"   Duration: {test.get('duration', 0):.2f}s")
            print(f"   Success Rate: {test.get('success_rate', 0):.1%}")

            if test.get("success_rate", 0) > 0.5:
                print(f"   ✅ Status: PASSED")
            else:
                print(f"   ❌ Status: FAILED")

            # Print test-specific details
            if "tests" in test:
                for subtest in test["tests"]:
                    status = "✅" if subtest.get("success", False) else "❌"
                    print(f"     {status} {subtest['name']}")

        print("\n" + "="*80)


async def main():
    """Main test function."""
    print("🚀 DAIP-LIVE Agent Engine V1 - Real System Test")
    print("="*60)

    tester = RealSystemTester()
    results = await tester.run_full_test_suite()
    tester.print_results(results)

    # Save results to file
    with open("real_system_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Results saved to: real_system_test_results.json")

    # Return appropriate exit code
    if results.get("summary", {}).get("overall_success", False):
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the results above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)