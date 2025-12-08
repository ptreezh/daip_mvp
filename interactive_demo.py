#!/usr/bin/env python3
"""
Interactive Demo for DAIP-LIVE Agent Engine V1

This script provides an interactive demo where users can type natural language
requests and see how the agent engine processes them in real-time.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

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


class InteractiveDemo:
    """Interactive demo for real user experience."""

    def __init__(self):
        self.system = None
        self.session_history = []
        self.demo_active = False

    async def setup_system(self):
        """Setup the agent engine system."""
        print("🚀 正在启动 DAIP-LIVE Agent Engine V1...")

        # Create EventBus
        self.event_bus = EventBus()
        await self.event_bus.start()

        # Create Service Manager
        self.service_manager = ServiceIntegrationManager(self.event_bus)

        # Create services
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

        print("✅ 系统启动完成!")
        print("📝 您现在可以开始与AI助手对话了")
        print("💡 输入 'help' 查看可用命令，输入 'exit' 退出")
        print("-" * 60)

    async def cleanup_system(self):
        """Cleanup system resources."""
        if self.system:
            print("🧹 正在关闭系统...")
            await self.orchestrator.stop()
            await self.service_manager.stop_all_services()
            await self.event_bus.stop()
            print("✅ 系统已安全关闭")

    async def process_user_request(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Process a user request through the agent engine."""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = f"demo_{datetime.now().strftime('%H%M%S')}"

            # Add business context
            context = {
                "user": "demo_user",
                "permission_level": "user",
                "demo_mode": True,
                "timestamp": datetime.now().isoformat()
            }

            print("🤖 思考中...")
            start_time = time.time()

            # Process through orchestrator
            result = await self.orchestrator.process_request(
                user_input=user_input,
                session_id=session_id,
                context=context
            )

            processing_time = time.time() - start_time

            # Format response
            response = {
                "session_id": session_id,
                "user_input": user_input,
                "processing_time": processing_time,
                "results": {
                    "intent": {
                        "detected": result.intent_result.intent if result.intent_result else "unknown",
                        "confidence": result.intent_result.confidence if result.intent_result else 0,
                        "strategy": result.intent_result.strategy_used if result.intent_result else "none"
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

            # Store in history
            self.session_history.append(response)

            return response

        except Exception as e:
            error_response = {
                "session_id": session_id or "unknown",
                "user_input": user_input,
                "processing_time": 0,
                "error": str(e),
                "results": None
            }
            self.session_history.append(error_response)
            return error_response

    def format_response(self, response: Dict[str, Any]) -> str:
        """Format the response for user display."""
        if "error" in response:
            return f"❌ 处理错误: {response['error']}"

        results = response["results"]

        output_lines = [
            f"📋 处理结果 (耗时: {response['processing_time']:.3f}s)",
            "",
            f"🎯 意图识别:",
            f"   检测到: {results['intent']['detected']}",
            f"   置信度: {results['intent']['confidence']:.2f}",
            f"   策略: {results['intent']['strategy']}",
            "",
            f"🛡️ 权限检查:",
            f"   状态: {'✅ 允许' if results['permission']['allowed'] else '❌ 拒绝'}",
            f"   风险等级: {results['permission']['risk_level']}",
            f"   原因: {results['permission']['reason']}"
        ]

        if results["execution"]["success"]:
            output_lines.extend([
                "",
                f"⚙️ 执行结果: ✅ 成功",
                f"   输出: {str(results['execution']['output'])[:100]}..." if results['execution']['output'] else "   输出: 无"
            ])
        else:
            output_lines.extend([
                "",
                f"⚙️ 执行结果: ❌ 失败",
                f"   错误: {results['execution']['error']}" if results['execution']['error'] else "   错误: 未知错误"
            ])

        return "\n".join(output_lines)

    def show_help(self):
        """Show help information."""
        help_text = """
🤖 DAIP-LIVE Agent Engine V1 交互式演示

📝 可用命令:
  help      - 显示此帮助信息
  status    - 显示系统状态
  history   - 显示会话历史
  stats     - 显示处理统计
  clear     - 清除会话历史
  exit      - 退出程序

💡 示例请求:
  "读取config.yaml文件内容"
  "分析这个Python代码的安全问题"
  "创建一个用户注册功能"
  "帮我优化数据库查询性能"
  "生成API文档"
  "检查系统日志错误"

🔧 技术功能演示:
  • 意图识别 - 自动理解用户需求
  • 权限控制 - 智能风险评估和访问控制
  • 任务执行 - 动态任务处理和结果返回
  • 状态管理 - 会话状态持久化
  • 事件驱动 - 实时事件发布和订阅

💡 使用提示:
  • 输入自然语言描述您的需求
  • 系统会自动识别意图并执行相应操作
  • 所有操作都会经过安全检查
  • 可以询问任何技术或业务相关问题
        """
        print(help_text)

    def show_status(self):
        """Show system status."""
        if not self.system:
            print("❌ 系统未启动")
            return

        print("📊 系统状态:")
        print(f"   EventBus: {'✅ 运行中' if self.event_bus.is_healthy() else '❌ 已停止'}")
        print(f"   Orchestrator: {'✅ 运行中' if self.orchestrator.is_healthy() else '❌ 已停止'}")
        print(f"   会话历史: {len(self.session_history)} 条记录")

        # Show service metrics
        try:
            orchestrator_metrics = self.orchestrator.get_metrics()
            print(f"   处理的会话: {orchestrator_metrics['orchestrator']['total_sessions']}")
            print(f"   成功率: {orchestrator_metrics['orchestrator']['success_rate']:.1%}")
        except Exception as e:
            print(f"   ⚠️ 获取指标时出错: {e}")

    def show_history(self):
        """Show session history."""
        if not self.session_history:
            print("📝 暂无会话历史")
            return

        print(f"📝 会话历史 (最近 {min(5, len(self.session_history))} 条):")
        print("-" * 60)

        for i, record in enumerate(self.session_history[-5:], 1):
            timestamp = record.get("timestamp", "unknown")
            user_input = record.get("user_input", "no input")[:50]
            if len(record.get("user_input", "")) > 50:
                user_input += "..."

            print(f"{i}. {timestamp[:19]} - {user_input}")

            if "results" in record and record["results"]:
                results = record["results"]
                intent = results.get("intent", {}).get("detected", "unknown")
                confidence = results.get("intent", {}).get("confidence", 0)
                permission_allowed = results.get("permission", {}).get("allowed", False)
                print(f"   → 意图: {intent} (置信度: {confidence:.2f}), 权限: {'允许' if permission_allowed else '拒绝'}")

    def show_stats(self):
        """Show processing statistics."""
        if not self.session_history:
            print("📊 暂无统计数据")
            return

        total_requests = len(self.session_history)
        successful_requests = 0
        total_processing_time = 0

        intent_counts = {}
        risk_counts = {}

        for record in self.session_history:
            total_processing_time += record.get("processing_time", 0)

            if "results" in record and record["results"]:
                successful_requests += 1

                # Count intents
                intent = record["results"].get("intent", {}).get("detected", "unknown")
                intent_counts[intent] = intent_counts.get(intent, 0) + 1

                # Count risk levels
                risk = record["results"].get("permission", {}).get("risk_level", "unknown")
                risk_counts[risk] = risk_counts.get(risk, 0) + 1

        print("📊 处理统计:")
        print(f"   总请求数: {total_requests}")
        print(f"   成功处理: {successful_requests}")
        print(f"   成功率: {successful_requests/total_requests:.1%}")
        print(f"   平均处理时间: {total_processing_time/total_requests:.3f}s")
        print("")
        print("🎯 意图分布:")
        for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {intent}: {count} 次")
        print("")
        print("🛡️ 风险等级分布:")
        for risk, count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {risk}: {count} 次")

    async def run_interactive_demo(self):
        """Run the interactive demo."""
        print("🎭 欢迎使用 DAIP-LIVE Agent Engine V1 交互式演示")
        print("=" * 60)

        # Setup system
        await self.setup_system()

        self.demo_active = True
        session_counter = 1

        try:
            while self.demo_active:
                # Get user input
                user_input = input("\n💬 请输入您的需求 (或输入 'help' 查看帮助): ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("👋 感谢使用 DAIP-LIVE Agent Engine!")
                    break

                elif user_input.lower() in ['help', '帮助']:
                    self.show_help()

                elif user_input.lower() in ['status', '状态']:
                    self.show_status()

                elif user_input.lower() in ['history', '历史']:
                    self.show_history()

                elif user_input.lower() in ['stats', '统计']:
                    self.show_stats()

                elif user_input.lower() in ['clear', '清除']:
                    self.session_history.clear()
                    print("🧹 会话历史已清除")

                else:
                    # Process the request
                    session_id = f"interactive_{session_counter}"
                    response = await self.process_user_request(user_input, session_id)

                    print("\n" + "="*60)
                    print(self.format_response(response))
                    print("="*60)

                    session_counter += 1

        except KeyboardInterrupt:
            print("\n👋 用户中断，正在安全关闭系统...")

        finally:
            # Cleanup
            await self.cleanup_system()
            self.demo_active = False


async def main():
    """Main demo function."""
    print("🚀 启动 DAIP-LIVE Agent Engine V1 交互式演示")
    print("=" * 80)

    demo = InteractiveDemo()
    await demo.run_interactive_demo()


if __name__ == "__main__":
    asyncio.run(main())