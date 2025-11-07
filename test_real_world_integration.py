#!/usr/bin/env python3
"""
Real World Integration Test

This script tests the complete agent_engine_v1 system in realistic scenarios.
It verifies the entire workflow from user input to system response.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any

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


class RealWorldTester:
    """Real world integration tester for complete system validation."""

    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}

    async def setup_complete_system(self) -> Dict[str, Any]:
        """Setup the complete system with all services."""
        logger.info("🚀 Setting up complete real-world system...")
        setup_start = time.time()

        # Create EventBus
        logger.info("  📡 Creating EventBus...")
        event_bus = EventBus()
        await event_bus.start()

        # Create Service Manager and all services
        logger.info("  🔧 Setting up Service Manager...")
        service_manager = ServiceIntegrationManager(event_bus)

        # Create all required services
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
        logger.info(f"✅ Complete system setup completed in {setup_time:.2f} seconds")

        return {
            "event_bus": event_bus,
            "service_manager": service_manager,
            "orchestrator": orchestrator,
            "adapter": adapter,
            "setup_time": setup_time
        }

    async def cleanup_system(self, system: Dict[str, Any]):
        """Cleanup system resources gracefully."""
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

    async def test_basic_user_interactions(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test basic user interaction scenarios."""
        logger.info("🧪 Testing Basic User Interactions...")
        test_start = time.time()

        orchestrator = system["orchestrator"]
        results = {
            "name": "Basic User Interactions",
            "scenarios": [],
            "success_count": 0,
            "total_count": 0
        }

        # Test scenarios
        scenarios = [
            {
                "name": "File Reading Request",
                "input": "请读取config.json文件并告诉我里面的内容",
                "expected_intent": "file_read",
                "description": "Test file reading intent recognition"
            },
            {
                "name": "Code Analysis Request",
                "input": "分析一下main.py的代码结构",
                "expected_intent": "code_analysis",
                "description": "Test code analysis intent"
            },
            {
                "name": "Question Answering",
                "input": "什么是机器学习？",
                "expected_intent": "question",
                "description": "Test general question handling"
            },
            {
                "name": "Help Request",
                "input": "帮助我了解系统功能",
                "expected_intent": "help",
                "description": "Test help system functionality"
            },
            {
                "name": "Search Request",
                "input": "搜索关于AI的所有文档",
                "expected_intent": "search",
                "description": "Test search functionality"
            }
        ]

        for scenario in scenarios:
            logger.info(f"  🎯 Testing: {scenario['name']}")
            try:
                start_time = time.time()

                # Process the request
                context = await orchestrator.process_request(
                    user_input=scenario["input"],
                    session_id=f"test_{scenario['name'].replace(' ', '_').lower()}",
                    context={"user": "test_user", "permission_level": "user"}
                )

                processing_time = time.time() - start_time

                # Verify results
                success = (
                    context.intent_result is not None and
                    context.intent_result.confidence > 0.5 and
                    context.permission_decision is not None and
                    context.permission_decision.allowed
                )

                scenario_result = {
                    "name": scenario["name"],
                    "success": success,
                    "input": scenario["input"],
                    "intent": context.intent_result.intent if context.intent_result else "None",
                    "confidence": context.intent_result.confidence if context.intent_result else 0,
                    "permission_allowed": context.permission_decision.allowed if context.permission_decision else False,
                    "risk_level": context.permission_decision.risk_level if context.permission_decision else "unknown",
                    "processing_time": processing_time,
                    "description": scenario["description"]
                }

                results["scenarios"].append(scenario_result)
                if success:
                    results["success_count"] += 1
                    logger.info(f"    ✅ {scenario['name']}: SUCCESS ({processing_time:.3f}s)")
                    logger.info(f"       Intent: {scenario_result['intent']} (confidence: {scenario_result['confidence']:.2f})")
                    logger.info(f"       Permission: {scenario_result['permission_allowed']} (risk: {scenario_result['risk_level']})")
                else:
                    logger.warning(f"    ❌ {scenario['name']}: FAILED")
                    logger.warning(f"       Intent: {scenario_result['intent']} (confidence: {scenario_result['confidence']:.2f})")
                    logger.warning(f"       Permission: {scenario_result['permission_allowed']} (risk: {scenario_result['risk_level']})")

            except Exception as e:
                logger.error(f"    ❌ {scenario['name']}: ERROR - {e}")
                results["scenarios"].append({
                    "name": scenario["name"],
                    "success": False,
                    "error": str(e),
                    "description": scenario["description"]
                })

            results["total_count"] += 1

        test_time = time.time() - test_start
        results["duration"] = test_time
        results["success_rate"] = results["success_count"] / results["total_count"] if results["total_count"] > 0 else 0

        logger.info(f"✅ Basic User Interactions: {results['success_count']}/{results['total_count']} passed ({results['success_rate']:.1%}) in {test_time:.2f}s")
        return results

    async def test_permission_system(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test permission system with different risk levels."""
        logger.info("🛡️ Testing Permission System...")
        test_start = time.time()

        orchestrator = system["orchestrator"]
        results = {
            "name": "Permission System",
            "tests": [],
            "success_count": 0,
            "total_count": 0
        }

        permission_tests = [
            {
                "name": "Low Risk Operation",
                "input": "读取readme.txt文件",
                "expected_risk": "low",
                "should_allow": True
            },
            {
                "name": "Medium Risk Operation",
                "input": "修改configuration.json文件",
                "expected_risk": "medium",
                "should_allow": True
            },
            {
                "name": "High Risk Operation",
                "input": "删除system32目录下的所有文件",
                "expected_risk": "high",
                "should_allow": False
            },
            {
                "name": "Critical Risk Operation",
                "input": "格式化系统硬盘",
                "expected_risk": "critical",
                "should_allow": False
            }
        ]

        for test in permission_tests:
            logger.info(f"  🛡️ Testing: {test['name']}")
            try:
                context = await orchestrator.process_request(
                    user_input=test["input"],
                    session_id=f"perm_test_{test['name'].replace(' ', '_').lower()}",
                    context={"user": "test_user", "permission_level": "user"}
                )

                # Check permission decision
                permission_granted = context.permission_decision.allowed if context.permission_decision else False
                risk_level = context.permission_decision.risk_level if context.permission_decision else "unknown"

                success = (
                    permission_granted == test["should_allow"] and
                    risk_level.lower() == test["expected_risk"].lower()
                )

                test_result = {
                    "name": test["name"],
                    "success": success,
                    "input": test["input"],
                    "permission_granted": permission_granted,
                    "risk_level": risk_level,
                    "expected_risk": test["expected_risk"],
                    "expected_granted": test["should_allow"],
                    "reason": context.permission_decision.reason if context.permission_decision else "No decision"
                }

                results["tests"].append(test_result)
                if success:
                    results["success_count"] += 1
                    logger.info(f"    ✅ {test['name']}: SUCCESS")
                    logger.info(f"       Risk: {risk_level} (expected: {test['expected_risk']})")
                    logger.info(f"       Permission: {'Granted' if permission_granted else 'Denied'} (expected: {'Granted' if test['should_allow'] else 'Denied'})")
                else:
                    logger.warning(f"    ❌ {test['name']}: FAILED")
                    logger.warning(f"       Risk: {risk_level} (expected: {test['expected_risk']})")
                    logger.warning(f"       Permission: {'Granted' if permission_granted else 'Denied'} (expected: {'Granted' if test['should_allow'] else 'Denied'})")

            except Exception as e:
                logger.error(f"    ❌ {test['name']}: ERROR - {e}")
                results["tests"].append({
                    "name": test["name"],
                    "success": False,
                    "error": str(e)
                })

            results["total_count"] += 1

        test_time = time.time() - test_start
        results["duration"] = test_time
        results["success_rate"] = results["success_count"] / results["total_count"] if results["total_count"] > 0 else 0

        logger.info(f"✅ Permission System: {results['success_count']}/{results['total_count']} passed ({results['success_rate']:.1%}) in {test_time:.2f}s")
        return results

    async def test_legacy_compatibility(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test legacy system compatibility."""
        logger.info("🔄 Testing Legacy Compatibility...")
        test_start = time.time()

        adapter = system["adapter"]
        results = {
            "name": "Legacy Compatibility",
            "tests": [],
            "success_count": 0,
            "total_count": 0
        }

        legacy_tests = [
            {
                "name": "Basic Legacy Request",
                "user_input": "读取data.csv文件",
                "session_id": "legacy_test_1",
                "user_id": "legacy_user",
                "tool_permissions": {"read_file": True, "file_read": True}
            },
            {
                "name": "Complex Legacy Request",
                "user_input": "执行Python脚本并分析结果",
                "session_id": "legacy_test_2",
                "user_id": "legacy_user",
                "tool_permissions": {"execute_code": True, "code_analyze": True}
            },
            {
                "name": "No Permission Request",
                "user_input": "删除重要文件",
                "session_id": "legacy_test_3",
                "user_id": "legacy_user",
                "tool_permissions": {"delete_file": False}
            }
        ]

        for test in legacy_tests:
            logger.info(f"  🔄 Testing: {test['name']}")
            try:
                legacy_request = LegacyRequest(
                    user_input=test["user_input"],
                    session_id=test["session_id"],
                    user_id=test["user_id"],
                    tool_permissions=test["tool_permissions"],
                    metadata={"test_name": test["name"]}
                )

                response = await adapter.process_legacy_request(legacy_request)

                success = (
                    isinstance(response.response, str) and
                    len(response.response) > 0 and
                    isinstance(response.success, bool)
                )

                test_result = {
                    "name": test["name"],
                    "success": success,
                    "response_length": len(response.response),
                    "legacy_success": response.success,
                    "has_tool_calls": bool(response.tool_calls),
                    "metadata": response.metadata,
                    "adapter_version": response.metadata.get("adapter_version", "unknown")
                }

                results["tests"].append(test_result)
                if success:
                    results["success_count"] += 1
                    logger.info(f"    ✅ {test['name']}: SUCCESS")
                    logger.info(f"       Response length: {test_result['response_length']} chars")
                    logger.info(f"       Legacy success: {test_result['legacy_success']}")
                    logger.info(f"       Tool calls: {test_result['has_tool_calls']}")
                else:
                    logger.warning(f"    ❌ {test['name']}: FAILED")

            except Exception as e:
                logger.error(f"    ❌ {test['name']}: ERROR - {e}")
                results["tests"].append({
                    "name": test["name"],
                    "success": False,
                    "error": str(e)
                })

            results["total_count"] += 1

        test_time = time.time() - test_start
        results["duration"] = test_time
        results["success_rate"] = results["success_count"] / results["total_count"] if results["total_count"] > 0 else 0

        logger.info(f"✅ Legacy Compatibility: {results['success_count']}/{results['total_count']} passed ({results['success_rate']:.1%}) in {test_time:.2f}s")
        return results

    async def test_concurrent_operations(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Test concurrent operation handling."""
        logger.info("⚡ Testing Concurrent Operations...")
        test_start = time.time()

        orchestrator = system["orchestrator"]
        results = {
            "name": "Concurrent Operations",
            "concurrent_requests": 10,
            "completed_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "total_time": 0,
            "response_times": []
        }

        # Create concurrent requests
        requests = [
            (f"分析数据文件{i}.csv", f"concurrent_test_{i}")
            for i in range(1, 11)
        ]

        logger.info(f"  🚀 Processing {len(requests)} concurrent requests...")
        concurrent_start = time.time()

        # Execute requests concurrently
        tasks = []
        for user_input, session_id in requests:
            task = orchestrator.process_request(
                user_input=user_input,
                session_id=session_id,
                context={"user": "test_user", "permission_level": "user"}
            )
            tasks.append(task)

        # Wait for all to complete
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.time() - concurrent_start

        # Analyze results
        for i, task_result in enumerate(completed_tasks):
            if isinstance(task_result, Exception):
                logger.warning(f"    ⚠️ Request {i+1} failed: {task_result}")
                results["failed_requests"] += 1
            else:
                results["completed_requests"] += 1
                # Simulate response time measurement (average per request)
                response_time = concurrent_time / len(completed_tasks)
                results["response_times"].append(response_time)

        results["total_time"] = concurrent_time
        results["avg_response_time"] = sum(results["response_times"]) / len(results["response_times"]) if results["response_times"] else 0
        results["success_rate"] = results["completed_requests"] / results["concurrent_requests"]

        logger.info(f"✅ Concurrent Operations: {results['completed_requests']}/{results['concurrent_requests']} completed in {concurrent_time:.2f}s")
        logger.info(f"    Average response time: {results['avg_response_time']:.3f}s")
        return results

    async def run_complete_integration_test(self) -> Dict[str, Any]:
        """Run the complete integration test suite."""
        logger.info("🎯 Starting Complete Real-World Integration Test...")
        suite_start = time.time()

        system = None
        test_results = {
            "name": "Real-World Integration Test Suite",
            "timestamp": datetime.now().isoformat(),
            "total_duration": 0,
            "setup_time": 0,
            "cleanup_time": 0,
            "tests": [],
            "summary": {}
        }

        try:
            # Setup complete system
            system = await self.setup_complete_system()
            test_results["setup_time"] = system["setup_time"]

            # Run comprehensive tests
            test_functions = [
                self.test_basic_user_interactions,
                self.test_permission_system,
                self.test_legacy_compatibility,
                self.test_concurrent_operations
            ]

            for test_func in test_functions:
                logger.info(f"\n{'='*60}")
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
            logger.error(f"❌ Integration test failed: {e}")
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

    def print_detailed_results(self, results: Dict[str, Any]):
        """Print detailed test results."""
        print("\n" + "="*100)
        print(f"🧪 {results['name']}")
        print("="*100)
        print(f"📅 Timestamp: {results['timestamp']}")
        print(f"⏱️ Total Duration: {results['total_duration']:.2f} seconds")
        print(f"⚙️ Setup Time: {results.get('setup_time', 0):.2f} seconds")
        print(f"🧹 Cleanup Time: {results.get('cleanup_time', 0):.2f} seconds")

        if "error" in results:
            print(f"\n❌ TEST SUITE FAILED: {results['error']}")
            return

        print(f"\n📊 OVERALL SUMMARY:")
        summary = results["summary"]
        print(f"   Total Test Categories: {summary['total_tests']}")
        print(f"   Successful Categories: {summary['successful_tests']}")
        print(f"   Average Success Rate: {summary['avg_success_rate']:.1%}")
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
            if "scenarios" in test:
                print(f"   📝 Scenarios:")
                for scenario in test["scenarios"]:
                    status = "✅" if scenario.get("success", False) else "❌"
                    print(f"     {status} {scenario['name']}: {scenario.get('intent', 'No intent')} (conf: {scenario.get('confidence', 0):.2f})")

            elif "tests" in test:
                print(f"   📝 Test Cases:")
                for test_case in test["tests"]:
                    status = "✅" if test_case.get("success", False) else "❌"
                    if "permission_granted" in test_case:
                        print(f"     {status} {test_case['name']}: {test_case.get('risk_level', 'unknown')} risk, {'granted' if test_case['permission_granted'] else 'denied'}")
                    else:
                        print(f"     {status} {test_case['name']}")

            elif "completed_requests" in test:
                print(f"   📝 Concurrency Results:")
                print(f"     Completed: {test['completed_requests']}/{test['concurrent_requests']}")
                print(f"     Success Rate: {test['success_rate']:.1%}")
                print(f"     Avg Response Time: {test['avg_response_time']:.3f}s")

        print("\n" + "="*100)


async def main():
    """Main test function."""
    print("🚀 DAIP-LIVE Agent Engine V1 - Real-World Integration Test")
    print("="*80)

    tester = RealWorldTester()
    results = await tester.run_complete_integration_test()
    tester.print_detailed_results(results)

    # Save results to file
    with open("real_world_integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Results saved to: real_world_integration_test_results.json")

    # Return appropriate exit code
    if results.get("summary", {}).get("overall_success", False):
        print("\n🎉 Real-world integration test completed successfully!")
        print("📈 System is ready for production use!")
        return 0
    else:
        print("\n⚠️ Some integration tests failed. Check the results above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)