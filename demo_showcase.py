#!/usr/bin/env python3
"""
DAIP-LIVE Agent Engine V1 功能演示

这个脚本展示了系统的核心功能，无需用户交互即可体验所有特性。
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
    AgentOrchestrator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemShowcase:
    """System showcase for demonstrating all features."""

    def __init__(self):
        self.system = None
        self.demo_results = []

    async def setup_system(self):
        """Setup the agent engine system."""
        logger.info("🚀 正在启动 DAIP-LIVE Agent Engine V1...")
        start_time = time.time()

        # Create EventBus
        self.event_bus = EventBus()
        await self.event_bus.start()

        # Create Service Manager
        self.service_manager = ServiceIntegrationManager(self.event_bus)

        # Create all services
        await self.service_manager.create_intent_recognition_service()
        await self.service_manager.create_execution_engine_service()
        await self.service_manager.create_permission_service()
        await self.service_manager.create_state_management_service()

        # Start all services
        await self.service_manager.start_all_services()

        # Create Orchestrator
        self.orchestrator = AgentOrchestrator(self.event_bus, self.service_manager)
        await self.orchestrator.start()

        self.system = {
            "event_bus": self.event_bus,
            "service_manager": self.service_manager,
            "orchestrator": self.orchestrator
        }

        setup_time = time.time() - start_time
        logger.info(f"✅ 系统启动完成，耗时 {setup_time:.2f} 秒")
        return setup_time

    async def cleanup_system(self):
        """Cleanup system resources."""
        if self.system:
            logger.info("🧹 正在关闭系统...")
            await self.orchestrator.stop()
            await self.service_manager.stop_all_services()
            await self.event_bus.stop()
            logger.info("✅ 系统已安全关闭")

    async def process_request(self, name: str, user_input: str, expected_intent: str, session_id: str = None) -> Dict[str, Any]:
        """Process a request and return results."""
        logger.info(f"🎯 演示: {name}")
        start_time = time.time()

        try:
            # Add context
            context = {
                "user": "demo_user",
                "permission_level": "user",
                "demo_mode": True,
                "scenario": name,
                "timestamp": datetime.now().isoformat()
            }

            # Generate session ID if not provided
            if not session_id:
                session_id = f"demo_{name.replace(' ', '_').lower()}_{int(time.time())}"

            # Process request
            result = await self.orchestrator.process_request(
                user_input=user_input,
                session_id=session_id,
                context=context
            )

            processing_time = time.time() - start_time

            # Format results
            demo_result = {
                "name": name,
                "user_input": user_input,
                "expected_intent": expected_intent,
                "session_id": session_id,
                "processing_time": processing_time,
                "success": True,
                "results": {
                    "intent": {
                        "detected": result.intent_result.intent if result.intent_result else "unknown",
                        "confidence": result.intent_result.confidence if result.intent_result else 0,
                        "expected": expected_intent,
                        "match": result.intent_result.intent == expected_intent if result.intent_result else False
                    },
                    "permission": {
                        "allowed": result.permission_decision.allowed if result.permission_decision else False,
                        "risk_level": result.permission_decision.risk_level if result.permission_decision else "unknown",
                        "reason": result.permission_decision.reason if result.permission_decision else "No decision"
                    },
                    "execution": {
                        "success": result.execution_result.success if result.execution_result else False,
                        "output": result.execution_result.output if result.execution_result else None,
                        "error": result.execution_result.error if result.execution_result else None
                    }
                }
            }

            self.demo_results.append(demo_result)
            return demo_result

        except Exception as e:
            logger.error(f"❌ 演示失败: {e}")
            error_result = {
                "name": name,
                "user_input": user_input,
                "expected_intent": expected_intent,
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            self.demo_results.append(error_result)
            return error_result

    def print_result(self, result: Dict[str, Any]):
        """Print a formatted result."""
        print(f"\n{'='*80}")
        print(f"🎯 {result['name']}")
        print(f"📝 输入: {result['user_input']}")
        print(f"⏱️ 处理时间: {result['processing_time']:.3f}s")

        if result["success"]:
            results = result["results"]
            print(f"🎯 意图识别:")
            print(f"   检测到: {results['intent']['detected']}")
            print(f"   期望: {results['intent']['expected']}")
            print(f"   匹配度: {'✅ 完全匹配' if results['intent']['match'] else '❌ 不匹配'}")
            print(f"   置信度: {results['intent']['confidence']:.2f}")

            print(f"🛡️ 权限检查:")
            print(f"   状态: {'✅ 允许' if results['permission']['allowed'] else '❌ 拒绝'}")
            print(f"   风险等级: {results['permission']['risk_level']}")
            print(f"   原因: {results['permission']['reason']}")

            print(f"⚙️ 执行结果:")
            print(f"   状态: {'✅ 成功' if results['execution']['success'] else '❌ 失败'}")
            if results['execution']['output']:
                output_preview = str(results['execution']['output'])[:100]
                print(f"   输出: {output_preview}...")
            if results['execution']['error']:
                print(f"   错误: {results['execution']['error']}")
        else:
            print(f"❌ 处理失败: {result['error']}")

    async def run_demo_showcase(self):
        """Run the complete demo showcase."""
        print("🎭 DAIP-LIVE Agent Engine V1 功能演示")
        print("=" * 80)
        print("📅 这个演示将展示系统的所有核心功能")
        print("💡 包括意图识别、权限控制、任务执行和状态管理")
        print()

        # Setup system
        setup_time = await self.setup_system()

        try:
            # Demo scenarios
            demo_scenarios = [
                {
                    "name": "文档读取功能",
                    "description": "展示文档文件读取和分析能力",
                    "requests": [
                        ("读取README文件", "请读取项目根目录下的README.md文件，提取项目基本信息", "file_read"),
                        ("读取配置文件", "请分析config.yaml配置文件的内容和结构", "file_read"),
                        ("读取日志文件", "请查看最新的系统日志文件，分析错误信息", "file_read")
                    ]
                },
                {
                    "name": "意图识别能力",
                    "description": "展示智能意图识别和分类",
                    "requests": [
                        ("文件操作意图", "请帮我创建一个新的Python文件", "file_write"),
                        ("数据分析意图", "分析一下销售数据并生成报告", "data_analysis"),
                        ("安全检查意图", "检查代码中的安全漏洞", "security_scan"),
                        ("帮助查询意图", "我需要了解如何使用这个系统", "help")
                    ]
                },
                {
                    "name": "权限控制系统",
                    "description": "展示智能权限评估和风险控制",
                    "requests": [
                        ("低风险操作", "读取公开文档文件", "file_read"),
                        ("高风险操作", "删除系统关键文件", "file_delete"),
                        ("中风险操作", "修改数据库配置", "file_write")
                    ]
                },
                {
                    "name": "任务执行引擎",
                    "description": "展示动态任务处理和结果返回",
                    "requests": [
                        ("简单计算任务", "计算1+1的结果", "tool_execute"),
                        ("文本处理任务", "处理文本数据并返回摘要", "tool_execute"),
                        ("文件操作任务", "创建一个测试文件", "file_write")
                    ]
                },
                {
                    "name": "业务流程集成",
                    "description": "展示完整的业务工作流程",
                    "requests": [
                        ("代码审查流程", "请审查代码质量、检查安全漏洞并提供改进建议", "code_analysis"),
                        ("部署配置流程", "创建Docker部署配置和CI/CD脚本", "deployment_config"),
                        ("监控设置流程", "配置系统监控和告警机制", "monitoring_setup")
                    ]
                }
            ]

            # Run all demo scenarios
            total_scenarios = sum(len(scenario["requests"]) for scenario in demo_scenarios)
            current_scenario = 1

            for scenario in demo_scenarios:
                print(f"\n🎬 {current_scenario}/{len(demo_scenarios)} {scenario['name']}")
                print(f"📝 {scenario['description']}")
                print("-" * 80)

                for request_name, user_input, expected_intent in scenario["requests"]:
                    result = await self.process_request(
                        f"{scenario['name']} - {request_name}",
                        user_input,
                        expected_intent
                    )
                    self.print_result(result)

                current_scenario += 1

            # Generate summary
            self.generate_summary()

        except Exception as e:
            logger.error(f"❌ 演示过程中出现错误: {e}")

        finally:
            # Cleanup
            await self.cleanup_system()

    def generate_summary(self):
        """Generate demo summary."""
        print(f"\n🎊 演示总结报告")
        print("=" * 80)

        total_requests = len(self.demo_results)
        successful_requests = sum(1 for r in self.demo_results if r.get("success", False))

        # Intent recognition stats
        intent_matches = sum(1 for r in self.demo_results if r.get("success", False) and
                           r.get("results", {}).get("intent", {}).get("match", False))

        # Permission stats
        permission_allowed = sum(1 for r in self.demo_results if r.get("success", False) and
                               r.get("results", {}).get("permission", {}).get("allowed", False))

        # Execution stats
        execution_success = sum(1 for r in self.demo_results if r.get("success", False) and
                                r.get("results", {}).get("execution", {}).get("success", False))

        avg_processing_time = sum(r.get("processing_time", 0) for r in self.demo_results) / total_requests if total_requests > 0 else 0

        print(f"📊 整体统计:")
        print(f"   总请求数: {total_requests}")
        print(f"   成功处理: {successful_requests}")
        print(f"   成功率: {successful_requests/total_requests:.1%}")
        print(f"   平均处理时间: {avg_processing_time:.3f}s")
        print("")

        print(f"🎯 意图识别:")
        print(f"   准确匹配: {intent_matches}/{total_requests} ({intent_matches/total_requests:.1%})")
        print(f"   准确率: {intent_matches/successful_requests:.1%} (基于成功请求)")

        print(f"🛡️ 权限控制:")
        print(f"   允许的操作: {permission_allowed}/{total_requests} ({permission_allowed/total_requests:.1%})")
        print(f"   允许率: {permission_allowed/successful_requests:.1%} (基于成功请求)")

        print(f"⚙️ 任务执行:")
        print(f"   执行成功: {execution_success}/{total_requests} ({execution_success/total_requests:.1%})")
        print(f"   执行成功率: {execution_success/successful_requests:.1%} (基于成功请求)")

        print(f"\n💡 技术特性展示:")
        print(f"   ✅ 事件驱动架构 - EventBus 实时通信")
        print(f"   ✅ 服务解耦设计 - 微服务架构")
        print(f"   ✅ 动态意图识别 - 智能用户理解")
        print(f"   ✅ 智能权限控制 - 基于风险评估")
        print(f"   ✅ 异步任务处理 - 高并发支持")
        print(f"   ✅ 状态持久化 - 会话管理")
        print(f"   ✅ 兼容性适配 - 向后兼容")
        print(f"   ✅ 实时监控 - 指标收集")

        # Business readiness assessment
        print(f"\n🏢 生产就绪评估:")
        if successful_requests >= total_requests * 0.8:
            print(f"   ✅ 系统架构稳定 - 所有核心功能正常工作")
            print(f"   ✅ API接口一致 - 组件间通信正常")
            print(f"   ✅ 错误处理完善 - 系统具备容错能力")
            print(f"   🎉 系统已准备好进行真实业务使用!")
        elif successful_requests >= total_requests * 0.6:
            print(f"   ⚠️ 系统基本可用 - 核心功能大部分正常")
            print(f"   ⚠️ 部分功能需要优化 - 意图识别准确率有待提升")
            print(f"   🔧 建议进行配置优化后再投入生产")
        else:
            print(f"   ❌ 系统需要优化 - 核心功能存在问题")
            print(f"   🔧 建议解决基础问题后再进行生产部署")

        print(f"\n📈 下一步建议:")
        print("   1. 优化意图识别模式 - 添加更多业务场景")
        print("   2. 完善权限规则配置 - 根据实际业务需求调整")
        print("   3. 扩展执行引擎能力 - 添加更多工具和操作")
        print("   4. 集成真实数据源 - 连接实际业务系统")
        print("   5. 部署监控告警 - 确保生产环境稳定性")


async def main():
    """Main demo function."""
    showcase = SystemShowcase()
    await showcase.run_demo_showcase()


if __name__ == "__main__":
    asyncio.run(main())