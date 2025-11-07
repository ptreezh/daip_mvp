#!/usr/bin/env python3
"""
Real User Scenarios Test

This script tests the agent_engine_v1 system with real business scenarios.
It simulates actual user workflows and requirements.
"""

import asyncio
import json
import logging
import time
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

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


@dataclass
class UserScenario:
    """User scenario definition."""
    name: str
    description: str
    user_input: str
    expected_intent: str
    expected_risk_level: str
    user_permission_level: str = "user"
    expected_success: bool = True
    business_context: Dict[str, Any] = None


class RealUserScenarioTester:
    """Real user scenario tester for business workflow validation."""

    def __init__(self):
        self.test_results = {}
        self.scenario_metrics = {}

    async def setup_production_system(self) -> Dict[str, Any]:
        """Setup production-like system with enhanced configuration."""
        logger.info("🚀 Setting up Production-like System...")
        setup_start = time.time()

        # Create EventBus
        logger.info("  📡 Creating EventBus with production config...")
        event_bus = EventBus()
        await event_bus.start()

        # Create Service Manager
        logger.info("  🔧 Setting up Service Manager...")
        service_manager = ServiceIntegrationManager(event_bus)

        # Create all services with production configuration
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
        logger.info(f"✅ Production system setup completed in {setup_time:.2f} seconds")

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

    def get_business_scenarios(self) -> List[UserScenario]:
        """Get real business scenarios for testing."""
        return [
            # Document Management Scenarios
            UserScenario(
                name="文档分析场景",
                description="用户需要分析项目文档并生成摘要",
                user_input="请分析项目根目录下的README.md文件，提取项目的主要功能、技术栈和部署要求，并生成一个简洁的项目摘要报告",
                expected_intent="file_read",
                expected_risk_level="low",
                business_context={
                    "project_phase": "analysis",
                    "document_type": "README",
                    "stakeholder": "project_manager"
                }
            ),
            UserScenario(
                name="代码审查场景",
                description="开发人员需要进行代码审查和重构建议",
                user_input="请审查src/main.py文件的代码质量，检查是否存在潜在的安全漏洞、性能问题和代码规范问题，并提供具体的改进建议",
                expected_intent="code_analysis",
                expected_risk_level="medium",
                business_context={
                    "project_phase": "review",
                    "file_type": "source_code",
                    "stakeholder": "developer"
                }
            ),
            UserScenario(
                name="配置管理场景",
                description="系统管理员需要更新和验证配置文件",
                user_input="请检查config.yaml配置文件的语法正确性，验证所有必需的配置项是否已设置，并检查数据库连接配置是否正确",
                expected_intent="file_read",
                expected_risk_level="low",
                business_context={
                    "project_phase": "maintenance",
                    "file_type": "config",
                    "stakeholder": "admin"
                }
            ),

            # Development Workflow Scenarios
            UserScenario(
                name="新功能开发场景",
                description="开发团队需要创建新的功能模块",
                user_input="请创建一个新的用户认证模块，包含用户注册、登录、密码重置和权限管理功能，并生成相应的API接口文档",
                expected_intent="file_write",
                expected_risk_level="medium",
                business_context={
                    "project_phase": "development",
                    "feature_type": "authentication",
                    "stakeholder": "developer"
                }
            ),
            UserScenario(
                name="数据库操作场景",
                description="需要进行数据库备份和迁移操作",
                user_input="请创建数据库备份脚本，包含全量备份和增量备份功能，并添加数据验证和恢复测试的步骤",
                expected_intent="file_write",
                expected_risk_level="high",
                business_context={
                    "project_phase": "maintenance",
                    "operation_type": "database_backup",
                    "stakeholder": "dba"
                }
            ),

            # Data Analysis Scenarios
            UserScenario(
                name="数据分析场景",
                description="数据分析师需要处理和分析业务数据",
                user_input="请分析data/sales.csv文件中的销售数据，计算月度增长率、最畅销产品和客户满意度趋势，并生成可视化报告",
                expected_intent="data_analysis",
                expected_risk_level="low",
                business_context={
                    "project_phase": "analysis",
                    "data_type": "sales_data",
                    "stakeholder": "analyst"
                }
            ),
            UserScenario(
                name="报告生成场景",
                description="业务经理需要生成月度业务报告",
                user_input="请根据logs/access.log文件分析网站访问统计数据，包括页面访问量、用户活跃度和错误率，生成月度运营报告",
                expected_intent="file_read",
                expected_risk_level="low",
                business_context={
                    "project_phase": "reporting",
                    "data_type": "access_logs",
                    "stakeholder": "manager"
                }
            ),

            # Security and Compliance Scenarios
            UserScenario(
                name="安全检查场景",
                description="安全团队需要进行安全漏洞扫描",
                user_input="请对整个代码库进行安全扫描，检查是否存在SQL注入、XSS攻击、文件上传漏洞等安全问题，并提供修复建议",
                expected_intent="security_scan",
                expected_risk_level="high",
                business_context={
                    "project_phase": "security_audit",
                    "scan_type": "vulnerability_assessment",
                    "stakeholder": "security_team"
                }
            ),
            UserScenario(
                name="权限管理场景",
                description="管理员需要配置用户权限和访问控制",
                user_input="请设计并实现基于角色的访问控制(RBAC)系统，包含管理员、普通用户和访客三种角色的权限配置",
                expected_intent="system_design",
                expected_risk_level="medium",
                business_context={
                    "project_phase": "security_design",
                    "feature_type": "rbac",
                    "stakeholder": "admin"
                }
            ),

            # Testing and Quality Assurance Scenarios
            UserScenario(
                name="自动化测试场景",
                description="QA团队需要创建自动化测试套件",
                user_input="请为用户认证模块创建完整的自动化测试套件，包含单元测试、集成测试和端到端测试",
                expected_intent="test_creation",
                expected_risk_level="low",
                business_context={
                    "project_phase": "testing",
                    "test_type": "automation",
                    "stakeholder": "qa_engineer"
                }
            ),
            UserScenario(
                name="性能测试场景",
                description="性能团队需要进行负载测试",
                user_input="请对API接口进行负载测试，模拟1000个并发用户访问，分析响应时间、吞吐量和系统瓶颈",
                expected_intent="performance_test",
                expected_risk_level="medium",
                business_context={
                    "project_phase": "performance_testing",
                    "test_type": "load_test",
                    "stakeholder": "performance_engineer"
                }
            ),

            # Deployment and Operations Scenarios
            UserScenario(
                name="部署配置场景",
                description="DevOps团队需要配置生产环境部署",
                user_input="请创建Docker容器化部署配置，包含应用容器、数据库容器和负载均衡器的完整部署方案",
                expected_intent="deployment_config",
                expected_risk_level="high",
                business_context={
                    "project_phase": "deployment",
                    "deployment_type": "docker",
                    "stakeholder": "devops_engineer"
                }
            ),
            UserScenario(
                name="监控配置场景",
                description="运维团队需要设置系统监控",
                user_input="请配置完整的系统监控方案，包含应用性能监控、基础设施监控和告警机制",
                expected_intent="monitoring_setup",
                expected_risk_level="medium",
                business_context={
                    "project_phase": "operations",
                    "monitoring_type": "full_stack",
                    "stakeholder": "ops_engineer"
                }
            )
        ]

    async def test_business_scenario(self, system: Dict[str, Any], scenario: UserScenario) -> Dict[str, Any]:
        """Test a single business scenario."""
        logger.info(f"🎯 Testing Scenario: {scenario.name}")

        orchestrator = system["orchestrator"]
        start_time = time.time()

        try:
            # Create business context
            context = {
                "user": "test_user",
                "permission_level": scenario.user_permission_level,
                "scenario_name": scenario.name,
                "business_context": scenario.business_context or {}
            }

            # Process the request
            result = await orchestrator.process_request(
                user_input=scenario.user_input,
                session_id=f"scenario_{scenario.name.replace(' ', '_').lower()}",
                context=context
            )

            processing_time = time.time() - start_time

            # Evaluate results
            intent_correct = (
                result.intent_result is not None and
                result.intent_result.intent == scenario.expected_intent
            )

            permission_correct = (
                result.permission_decision is not None and
                result.permission_decision.allowed == scenario.expected_success
            )

            risk_level_correct = (
                result.permission_decision is not None and
                result.permission_decision.risk_level.lower() == scenario.expected_risk_level.lower()
            )

            execution_success = (
                result.execution_result is not None and
                result.execution_result.success == scenario.expected_success
            )

            # Calculate overall success
            success_criteria = [intent_correct, permission_correct, execution_success]
            success_rate = sum(success_criteria) / len(success_criteria)

            scenario_result = {
                "name": scenario.name,
                "description": scenario.description,
                "success": success_rate >= 0.75,  # 75% criteria for success
                "success_rate": success_rate,
                "processing_time": processing_time,
                "user_input": scenario.user_input,
                "business_context": scenario.business_context,
                "results": {
                    "intent_recognition": {
                        "success": intent_correct,
                        "detected_intent": result.intent_result.intent if result.intent_result else "None",
                        "confidence": result.intent_result.confidence if result.intent_result else 0,
                        "expected_intent": scenario.expected_intent
                    },
                    "permission_check": {
                        "success": permission_correct,
                        "allowed": result.permission_decision.allowed if result.permission_decision else False,
                        "risk_level": result.permission_decision.risk_level if result.permission_decision else "unknown",
                        "expected_risk": scenario.expected_risk_level,
                        "reason": result.permission_decision.reason if result.permission_decision else "No decision"
                    },
                    "execution": {
                        "success": execution_success,
                        "completed": result.execution_result.success if result.execution_result else False,
                        "has_output": bool(result.execution_result.output if result.execution_result else False),
                        "error": result.execution_result.error if result.execution_result else None
                    }
                }
            }

            if success_rate >= 0.75:
                logger.info(f"    ✅ {scenario.name}: SUCCESS ({success_rate:.1%})")
                logger.info(f"       Intent: {scenario_result['results']['intent_recognition']['detected_intent']} (conf: {scenario_result['results']['intent_recognition']['confidence']:.2f})")
                logger.info(f"       Permission: {scenario_result['results']['permission_check']['allowed']} (risk: {scenario_result['results']['permission_check']['risk_level']})")
                logger.info(f"       Execution: {scenario_result['results']['execution']['success']}")
            else:
                logger.warning(f"    ⚠️ {scenario.name}: PARTIAL ({success_rate:.1%})")
                logger.warning(f"       Intent: {scenario_result['results']['intent_recognition']['detected_intent']} (expected: {scenario_result['results']['intent_recognition']['expected_intent']})")
                logger.warning(f"       Permission: {scenario_result['results']['permission_check']['allowed']} (risk: {scenario_result['results']['permission_check']['risk_level']})")
                logger.warning(f"       Execution: {scenario_result['results']['execution']['success']}")

            return scenario_result

        except Exception as e:
            logger.error(f"    ❌ {scenario.name}: ERROR - {e}")
            return {
                "name": scenario.name,
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "description": scenario.description,
                "business_context": scenario.business_context
            }

    async def run_business_scenario_tests(self) -> Dict[str, Any]:
        """Run all business scenario tests."""
        logger.info("🎯 Starting Real User Business Scenario Tests...")
        suite_start = time.time()

        system = None
        test_results = {
            "name": "Real User Business Scenario Tests",
            "timestamp": datetime.now().isoformat(),
            "total_duration": 0,
            "setup_time": 0,
            "cleanup_time": 0,
            "scenarios": [],
            "summary": {}
        }

        try:
            # Setup production system
            system = await self.setup_production_system()
            test_results["setup_time"] = system["setup_time"]

            # Get business scenarios
            scenarios = self.get_business_scenarios()
            logger.info(f"📋 Running {len(scenarios)} business scenarios...")

            # Run each scenario
            for scenario in scenarios:
                result = await self.test_business_scenario(system, scenario)
                test_results["scenarios"].append(result)
                self.test_results[scenario.name] = result

            # Generate summary
            total_scenarios = len(test_results["scenarios"])
            successful_scenarios = sum(1 for s in test_results["scenarios"] if s.get("success", False))
            avg_success_rate = sum(s.get("success_rate", 0) for s in test_results["scenarios"]) / total_scenarios

            test_results["summary"] = {
                "total_scenarios": total_scenarios,
                "successful_scenarios": successful_scenarios,
                "avg_success_rate": avg_success_rate,
                "overall_success": successful_scenarios >= total_scenarios * 0.8 and avg_success_rate > 0.7
            }

        except Exception as e:
            logger.error(f"❌ Business scenario test failed: {e}")
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

    def print_business_results(self, results: Dict[str, Any]):
        """Print business scenario test results."""
        print("\n" + "="*120)
        print(f"🧪 {results['name']}")
        print("="*120)
        print(f"📅 Timestamp: {results['timestamp']}")
        print(f"⏱️ Total Duration: {results['total_duration']:.2f} seconds")
        print(f"⚙️ Setup Time: {results.get('setup_time', 0):.2f} seconds")
        print(f"🧹 Cleanup Time: {results.get('cleanup_time', 0):.2f} seconds")

        if "error" in results:
            print(f"\n❌ TEST SUITE FAILED: {results['error']}")
            return

        print(f"\n📊 BUSINESS SCENARIO SUMMARY:")
        summary = results["summary"]
        print(f"   Total Scenarios: {summary['total_scenarios']}")
        print(f"   Successful Scenarios: {summary['successful_scenarios']}")
        print(f"   Average Success Rate: {summary['avg_success_rate']:.1%}")
        print(f"   Overall Result: {'✅ PRODUCTION READY' if summary['overall_success'] else '⚠️ NEEDS OPTIMIZATION'}")

        print(f"\n📋 DETAILED SCENARIO RESULTS:")
        for scenario in results["scenarios"]:
            print(f"\n🔹 {scenario['name']}:")
            print(f"   Description: {scenario['description']}")
            print(f"   Duration: {scenario.get('processing_time', 0):.3f}s")
            print(f"   Success Rate: {scenario.get('success_rate', 0):.1%}")

            if scenario.get("success", False):
                print(f"   ✅ Status: PASSED")
            else:
                print(f"   ⚠️ Status: NEEDS ATTENTION")

            if "error" in scenario:
                print(f"   ❌ Error: {scenario['error']}")
            elif "results" in scenario:
                results_data = scenario["results"]
                print(f"   📝 Intent Recognition: {'✅' if results_data['intent_recognition']['success'] else '❌'}")
                print(f"       Detected: {results_data['intent_recognition']['detected_intent']}")
                print(f"       Expected: {results_data['intent_recognition']['expected_intent']}")
                print(f"       Confidence: {results_data['intent_recognition']['confidence']:.2f}")

                print(f"   🛡️ Permission Check: {'✅' if results_data['permission_check']['success'] else '❌'}")
                print(f"       Allowed: {results_data['permission_check']['allowed']}")
                print(f"       Risk Level: {results_data['permission_check']['risk_level']}")
                print(f"       Reason: {results_data['permission_check']['reason']}")

                print(f"   ⚙️ Execution: {'✅' if results_data['execution']['success'] else '❌'}")
                print(f"       Completed: {results_data['execution']['success']}")
                print(f"       Has Output: {results_data['execution']['has_output']}")

        # Business insights
        print(f"\n💼 BUSINESS INSIGHTS:")
        if summary['overall_success']:
            print("   ✅ System is ready for production business use")
            print("   ✅ Core workflows are functioning correctly")
            print("   ✅ Security controls are in place")
        else:
            print("   ⚠️ System needs optimization before production deployment")
            print("   ⚠️ Some business workflows need improvement")
            print("   ⚠️ Consider additional training for intent recognition")

        print("\n" + "="*120)


async def main():
    """Main test function."""
    print("🚀 DAIP-LIVE Agent Engine V1 - Real User Business Scenario Tests")
    print("="*100)

    tester = RealUserScenarioTester()
    results = await tester.run_business_scenario_tests()
    tester.print_business_results(results)

    # Save results to file
    with open("real_user_scenario_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Results saved to: real_user_scenario_test_results.json")

    # Return appropriate exit code
    if results.get("summary", {}).get("overall_success", False):
        print("\n🎉 Real user scenario tests completed successfully!")
        print("📈 System is ready for production business deployment!")
        return 0
    else:
        print("\n⚠️ Some business scenarios need optimization.")
        print("📝 Review the results above for improvement areas.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)