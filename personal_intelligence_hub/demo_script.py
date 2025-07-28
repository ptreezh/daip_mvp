#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - 演示脚本

展示Personal Intelligence Hub的所有功能和技术亮点
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
from personal_intelligence_hub.services.backend_integration import get_backend_service
from personal_intelligence_hub.components.transparency_monitor import TransparencyMonitor
from personal_intelligence_hub.models.chat_models import ChatMessage, MessageType
from datetime import datetime


class PersonalIntelligenceHubDemo:
    """Personal Intelligence Hub演示类"""
    
    def __init__(self):
        self.assistant = PersonalAssistantService()
        self.session_id = "demo_session_001"
        
    async def run_demo(self):
        """运行完整演示"""
        print("🎭 Personal Intelligence Hub 功能演示")
        print("=" * 60)
        
        # 1. 系统初始化演示
        await self.demo_system_initialization()
        
        # 2. 意图分析演示
        await self.demo_intent_analysis()
        
        # 3. 团队组建演示
        await self.demo_team_assembly()
        
        # 4. 命令执行演示
        await self.demo_command_execution()
        
        # 5. 透明度监控演示
        await self.demo_transparency_monitoring()
        
        # 6. 后端集成演示
        await self.demo_backend_integration()
        
        print("\n🎉 演示完成！")
        print("=" * 60)
        
    async def demo_system_initialization(self):
        """演示系统初始化"""
        print("\n📋 1. 系统初始化演示")
        print("-" * 30)
        
        try:
            backend_service = await get_backend_service()
            health_status = await backend_service.check_backend_health()
            
            print("✅ 后端服务连接状态:")
            for service_name, status in health_status.items():
                status_emoji = {
                    "healthy": "🟢",
                    "degraded": "🟡", 
                    "unhealthy": "🔴",
                    "unavailable": "⚫"
                }.get(status.status.value, "❓")
                
                print(f"   {status_emoji} {status.service_name}: {status.status.value}")
                print(f"      响应时间: {status.response_time:.2f}s")
                
        except Exception as e:
            print(f"⚠️ 后端服务连接失败: {e}")
            print("   将使用本地降级模式")
    
    async def demo_intent_analysis(self):
        """演示意图分析功能"""
        print("\n🧠 2. 意图分析演示")
        print("-" * 30)
        
        test_inputs = [
            "我需要对这个AI威胁报告进行可靠的分析",
            "请从多个角度讨论人工智能的伦理问题",
            "帮我分析一下区块链技术的优缺点"
        ]
        
        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n测试 {i}: {user_input}")
            
            try:
                context = self.assistant.get_conversation_context(self.session_id)
                intent_result = await self.assistant.analyze_intent(user_input, context)
                
                print(f"   🎯 工作流类型: {intent_result.workflow_type.value}")
                print(f"   📊 置信度: {intent_result.confidence:.2f}")
                print(f"   💭 推理: {intent_result.reasoning}")
                
            except Exception as e:
                print(f"   ❌ 分析失败: {e}")
    
    async def demo_team_assembly(self):
        """演示团队组建功能"""
        print("\n👥 3. 智能团队组建演示")
        print("-" * 30)
        
        from personal_intelligence_hub.services.personal_assistant import WorkflowType
        
        test_cases = [
            ("AI安全威胁分析", WorkflowType.CRITICAL_REVIEW),
            ("气候变化政策讨论", WorkflowType.MULTI_PERSPECTIVE),
            ("技术创新评估", WorkflowType.CUSTOM)
        ]
        
        for topic, workflow_type in test_cases:
            print(f"\n📋 话题: {topic}")
            print(f"   工作流: {workflow_type.value}")
            
            try:
                team_proposal = await self.assistant.assemble_team(topic, workflow_type)
                
                print(f"   🤖 团队成员: {', '.join(team_proposal.agents)}")
                print(f"   🎯 多样性评分: {team_proposal.diversity_score:.2f}")
                print(f"   💡 选择理由: {team_proposal.rationale}")
                print(f"   ✅ 确认消息: {team_proposal.confirmation_message}")
                
            except Exception as e:
                print(f"   ❌ 团队组建失败: {e}")
    
    async def demo_command_execution(self):
        """演示命令执行功能"""
        print("\n⚡ 4. 命令执行演示")
        print("-" * 30)
        
        commands = ["/help", "/status", "/consensus now", "/clear"]
        
        for command in commands:
            print(f"\n🔧 执行命令: {command}")
            
            try:
                result = await self.assistant.execute_command(command, self.session_id)
                print(f"   📤 结果: {result[:100]}{'...' if len(result) > 100 else ''}")
                
            except Exception as e:
                print(f"   ❌ 命令执行失败: {e}")
    
    async def demo_transparency_monitoring(self):
        """演示透明度监控功能"""
        print("\n🔍 5. 透明度监控演示")
        print("-" * 30)
        
        try:
            monitor = TransparencyMonitor()
            
            # 启动监控更新
            await monitor.update_system_status()
            
            print("✅ 透明度监控组件已初始化")
            print(f"   📊 活跃代理数量: {len(monitor.system_status.active_agents)}")
            print(f"   📡 LLM调用记录: {len(monitor.system_status.llm_calls or [])}")
            
            if monitor.system_status.token_usage:
                usage = monitor.system_status.token_usage
                print(f"   🎯 Token使用: {usage.total_tokens:,} (${usage.estimated_cost:.4f})")
            
            # 演示自动刷新功能
            print("   🔄 启动自动刷新...")
            await monitor.start_auto_refresh()
            
            # 等待几秒钟展示实时更新
            await asyncio.sleep(3)
            
            await monitor.stop_auto_refresh()
            print("   ⏸️ 停止自动刷新")
            
        except Exception as e:
            print(f"❌ 透明度监控演示失败: {e}")
    
    async def demo_backend_integration(self):
        """演示后端集成功能"""
        print("\n🔗 6. 后端集成演示")
        print("-" * 30)
        
        try:
            backend_service = await get_backend_service()
            
            # 测试角色获取
            print("📋 获取可用角色...")
            roles = await backend_service.get_available_roles()
            print(f"   ✅ 获取到 {len(roles)} 个角色")
            
            if roles:
                for role in roles[:3]:  # 显示前3个角色
                    print(f"      🤖 {role.get('name', 'Unknown')}: {role.get('description', 'No description')[:50]}...")
            
            # 测试Wiki搜索
            print("\n🔍 Wiki搜索测试...")
            search_results = await backend_service.search_wiki("AI", limit=3)
            print(f"   ✅ 搜索结果: {len(search_results)} 条")
            
            # 测试记忆上下文
            print("\n🧠 记忆上下文测试...")
            memory_context = await backend_service.get_memory_context("demo_user", "AI技术")
            if "error" not in memory_context:
                print("   ✅ 记忆上下文获取成功")
            else:
                print(f"   ⚠️ 记忆上下文获取失败: {memory_context['error']}")
            
        except Exception as e:
            print(f"❌ 后端集成演示失败: {e}")
    
    async def demo_message_processing(self):
        """演示消息处理流程"""
        print("\n💬 7. 完整消息处理演示")
        print("-" * 30)
        
        test_message = "我需要分析人工智能在医疗领域的应用前景和风险"
        
        print(f"📝 用户输入: {test_message}")
        
        try:
            # 处理消息
            response = await self.assistant.process_message(test_message, self.session_id)
            
            print("🤖 助手响应:")
            print(f"   {response}")
            
            # 显示会话上下文
            context = self.assistant.get_conversation_context(self.session_id)
            print(f"\n📊 会话状态:")
            print(f"   活跃代理: {context.get('active_agents', [])}")
            print(f"   消息历史: {len(context.get('message_history', []))} 条")
            
        except Exception as e:
            print(f"❌ 消息处理失败: {e}")


async def main():
    """主函数"""
    demo = PersonalIntelligenceHubDemo()
    
    try:
        await demo.run_demo()
        
        # 额外的消息处理演示
        await demo.demo_message_processing()
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("🎭 Personal Intelligence Hub - 功能演示")
    print("请确保DAIP-LIVE后端服务正在运行 (http://localhost:8000)")
    print("如果后端不可用，将使用本地降级模式演示")
    print()
    
    # 运行演示
    asyncio.run(main())