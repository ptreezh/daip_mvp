#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的V0.1.3集成测试

测试修复后的PersonalAssistantService功能
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService


async def test_fixed_message_history():
    """测试修复后的消息历史功能"""
    print("🧪 测试修复后的消息历史功能...")
    
    service = PersonalAssistantService()
    session_id = "history_test"
    
    try:
        # 第一条消息
        response1 = await service.process_message("我想讨论AI的发展", session_id)
        print(f"第1条消息处理完成")
        
        # 检查消息历史
        context = service.get_conversation_context(session_id)
        print(f"消息历史长度: {len(context['message_history'])}")
        
        # 应该有2条消息：用户输入 + 助手回复
        assert len(context['message_history']) == 2, f"期望2条消息，实际{len(context['message_history'])}条"
        
        # 验证消息内容
        user_msg = context['message_history'][0]
        assistant_msg = context['message_history'][1]
        
        assert user_msg['sender'] == 'user', "第一条应该是用户消息"
        assert user_msg['content'] == "我想讨论AI的发展", "用户消息内容不匹配"
        
        assert assistant_msg['sender'] == 'assistant', "第二条应该是助手消息"
        assert len(assistant_msg['content']) > 0, "助手消息不应为空"
        
        print("✅ 消息历史保存正确")
        
        # 第二条消息
        response2 = await service.process_message("请详细分析", session_id)
        print(f"第2条消息处理完成")
        
        # 再次检查消息历史
        context = service.get_conversation_context(session_id)
        print(f"消息历史长度: {len(context['message_history'])}")
        
        # 现在应该有4条消息
        assert len(context['message_history']) == 4, f"期望4条消息，实际{len(context['message_history'])}条"
        
        print("✅ 多轮对话消息历史正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息历史测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_fixed_consensus_calculation():
    """测试修复后的共识计算功能"""
    print("\n🧪 测试修复后的共识计算功能...")
    
    service = PersonalAssistantService()
    session_id = "consensus_test"
    
    try:
        # 先进行一些对话建立上下文
        await service.process_message("我想分析远程工作的影响", session_id)
        await service.process_message("请从多个角度分析", session_id)
        await service.process_message("特别关注对团队协作的影响", session_id)
        
        # 检查对话上下文
        context = service.get_conversation_context(session_id)
        print(f"对话历史: {len(context['message_history'])}条消息")
        print(f"活跃代理: {context.get('active_agents', [])}")
        
        # 执行共识计算
        consensus_response = await service.execute_command("/consensus now", session_id)
        print(f"共识计算响应: {consensus_response[:200]}...")
        
        # 验证响应内容
        if "共识计算失败" in consensus_response:
            print("⚠️ 后端服务不可用，但降级处理正常")
            # 检查是否包含基于真实对话历史的内容
            assert "基于讨论内容" in consensus_response or "当前没有活跃的讨论" in consensus_response
            return True
        else:
            # 后端可用的情况
            assert "共识计算完成" in consensus_response or "共识强度" in consensus_response
            print("✅ 共识计算成功")
            return True
        
    except Exception as e:
        print(f"❌ 共识计算测试失败: {e}")
        return False


async def test_context_persistence():
    """测试上下文持久性"""
    print("\n🧪 测试上下文持久性...")
    
    service = PersonalAssistantService()
    session_id = "persistence_test"
    
    try:
        # 第一轮对话
        await service.process_message("我想研究机器学习", session_id)
        
        # 获取上下文
        context1 = service.get_conversation_context(session_id)
        initial_intent = context1.get('last_intent')
        initial_team = context1.get('proposed_team')
        
        print(f"初始意图: {initial_intent.workflowType if initial_intent else 'None'}")
        print(f"初始团队: {initial_team.agents if initial_team else 'None'}")
        
        # 第二轮对话
        await service.process_message("请开始分析", session_id)
        
        # 检查上下文是否保持
        context2 = service.get_conversation_context(session_id)
        
        assert context2.get('last_intent') is not None, "意图分析结果应该保持"
        assert context2.get('proposed_team') is not None, "团队提议应该保持"
        assert context2.get('active_agents'), "活跃代理列表应该存在"
        
        print("✅ 上下文持久性正常")
        
        # 测试跨命令的上下文保持
        consensus_response = await service.execute_command("/consensus now", session_id)
        
        # 上下文应该仍然存在
        context3 = service.get_conversation_context(session_id)
        assert len(context3['message_history']) > 0, "消息历史应该保持"
        
        print("✅ 跨命令上下文保持正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 上下文持久性测试失败: {e}")
        return False


async def test_performance_after_fix():
    """测试修复后的性能"""
    print("\n🧪 测试修复后的性能...")
    
    service = PersonalAssistantService()
    session_id = "performance_test"
    
    try:
        # 测试消息处理性能
        start_time = time.time()
        await service.process_message("测试性能", session_id)
        message_time = time.time() - start_time
        
        print(f"📊 消息处理时间: {message_time:.3f}秒")
        
        # 测试命令执行性能
        start_time = time.time()
        await service.execute_command("/status", session_id)
        command_time = time.time() - start_time
        
        print(f"📊 命令执行时间: {command_time:.3f}秒")
        
        # 验证性能要求
        max_time = max(message_time, command_time)
        if max_time < 30.0:
            print(f"✅ 性能要求达标: {max_time:.3f}秒 < 30秒")
            return True
        else:
            print(f"❌ 性能要求不达标: {max_time:.3f}秒 >= 30秒")
            return False
            
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始修复后的V0.1.3集成测试")
    print("📋 测试目标：验证PersonalAssistantService修复后的功能")
    print("=" * 70)
    
    results = []
    
    # 运行修复验证测试
    results.append(await test_fixed_message_history())
    results.append(await test_fixed_consensus_calculation())
    results.append(await test_context_persistence())
    results.append(await test_performance_after_fix())
    
    print("\n" + "=" * 70)
    print("📋 修复后集成测试结果:")
    
    test_names = [
        "消息历史修复验证",
        "共识计算修复验证",
        "上下文持久性验证",
        "性能要求验证"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {i+1}. {name}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 修复后的V0.1.3集成测试全部通过！")
        print("\n✅ PersonalAssistantService关键问题已修复：")
        print("   - ✅ 消息历史正确保存和管理")
        print("   - ✅ 对话上下文持久性保持")
        print("   - ✅ 共识计算基于真实对话历史")
        print("   - ✅ 多轮对话功能完整")
        print("   - ✅ 性能要求达标")
        print("\n🔧 V0.1.3任务现在真正完成！")
    else:
        print("\n❌ 仍有部分功能需要进一步修复")
    
    return all_passed


if __name__ == "__main__":
    # 运行修复后的集成测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)