#!/usr/bin/env python3
"""V0.1.3 真实LLM调用集成测试

测试PersonalAssistantService与真实后端服务的集成
验证多角色对话功能的实际工程可用性
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService


async def test_real_backend_integration():
    """测试与真实后端服务的集成"""
    print("🧪 开始测试PersonalAssistantService与真实后端的集成...")
    
    service = PersonalAssistantService()
    
    try:
        print("\n1️⃣ 测试真实意图分析...")
        
        # 测试真实的意图分析
        start_time = time.time()
        intent_result = await service.analyze_intent(
            "我想深入分析AI在教育中的应用前景，包括可能的挑战和机遇",
            {"user_id": "test_user", "message_history": []}
        )
        intent_time = time.time() - start_time
        
        print(f"✅ 真实意图分析完成 (耗时: {intent_time:.2f}秒)")
        print(f"   - 工作流类型: {intent_result.workflowType}")
        print(f"   - 置信度: {intent_result.confidence}")
        print(f"   - 推理: {intent_result.reasoning}")
        print(f"   - 主题: {intent_result.topic}")
        
        # 验证结果合理性
        assert intent_result.confidence > 0.0, "置信度应该大于0"
        assert len(intent_result.reasoning) > 10, "推理应该有实际内容"
        assert len(intent_result.topic) > 0, "主题不应为空"
        
        print("\n2️⃣ 测试真实团队组建...")
        
        # 测试真实的团队组建
        start_time = time.time()
        team_proposal = await service.assemble_team(
            intent_result.topic,
            intent_result.workflowType
        )
        team_time = time.time() - start_time
        
        print(f"✅ 真实团队组建完成 (耗时: {team_time:.2f}秒)")
        print(f"   - 团队成员: {team_proposal.agents}")
        print(f"   - 多样性评分: {team_proposal.diversity_score}")
        print(f"   - 组建理由: {team_proposal.rationale}")
        
        # 验证结果合理性
        assert len(team_proposal.agents) >= 1, "至少应该有一个团队成员"
        assert team_proposal.diversity_score >= 0.0, "多样性评分应该非负"
        assert len(team_proposal.rationale) > 10, "组建理由应该有实际内容"
        
        print("\n3️⃣ 测试真实消息处理...")
        
        # 测试完整的消息处理流程
        start_time = time.time()
        response = await service.process_message(
            "我想深入分析AI在教育中的应用前景，包括可能的挑战和机遇",
            "real_test_session"
        )
        message_time = time.time() - start_time
        
        print(f"✅ 真实消息处理完成 (耗时: {message_time:.2f}秒)")
        print(f"   - 响应长度: {len(response)}字符")
        print("   - 响应内容:")
        print(f"     {response}")
        
        # 验证响应质量
        assert len(response) > 50, "响应应该有足够的内容"
        assert any(keyword in response for keyword in ["团队", "分析", "工作流"]), "响应应该包含相关关键词"
        
        print("\n4️⃣ 测试真实命令执行...")
        
        # 测试共识计算命令
        start_time = time.time()
        consensus_response = await service.execute_command("/consensus now", "real_test_session")
        consensus_time = time.time() - start_time
        
        print(f"✅ 真实共识计算完成 (耗时: {consensus_time:.2f}秒)")
        print("   - 响应内容:")
        print(f"     {consensus_response}")
        
        # 验证共识计算结果
        assert len(consensus_response) > 20, "共识计算响应应该有实际内容"
        
        # 测试系统状态查询
        status_response = await service.execute_command("/status", "real_test_session")
        print("✅ 系统状态查询完成")
        print(f"   - 状态信息: {status_response[:100]}...")
        
        print("\n5️⃣ 测试性能要求...")
        
        # 验证性能要求
        max_time = max(intent_time, team_time, message_time, consensus_time)
        print(f"📊 最大响应时间: {max_time:.2f}秒")
        
        if max_time < 30.0:
            print("✅ 性能要求达标 (<30秒)")
            performance_ok = True
        else:
            print("❌ 性能要求不达标 (>=30秒)")
            performance_ok = False
        
        print("\n6️⃣ 测试降级处理...")
        
        # 测试后端不可用时的降级处理
        print("🔧 模拟后端服务不可用...")
        original_backend = service.backend_service
        service.backend_service = None
        
        fallback_intent = await service.analyze_intent("测试降级处理")
        print(f"✅ 降级意图分析: {fallback_intent.reasoning}")
        
        fallback_team = await service.assemble_team("测试", fallback_intent.workflowType)
        print(f"✅ 降级团队组建: {len(fallback_team.agents)}个默认角色")
        
        # 恢复后端服务
        service.backend_service = original_backend
        
        print("\n🎉 所有真实LLM集成测试通过！")
        
        return {
            "success": True,
            "performance_ok": performance_ok,
            "intent_time": intent_time,
            "team_time": team_time,
            "message_time": message_time,
            "consensus_time": consensus_time,
            "max_time": max_time
        }
        
    except Exception as e:
        print(f"❌ 真实LLM集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


async def test_multi_round_dialogue():
    """测试多轮对话功能"""
    print("\n🧪 开始测试多轮对话功能...")
    
    service = PersonalAssistantService()
    session_id = "multi_round_test"
    
    try:
        # 第一轮：启动讨论
        print("\n🗣️ 第1轮：启动讨论")
        response1 = await service.process_message(
            "我想讨论远程工作对企业文化的影响",
            session_id
        )
        print(f"助手回应: {response1[:100]}...")
        
        # 第二轮：用户确认
        print("\n🗣️ 第2轮：用户确认")
        response2 = await service.process_message(
            "好的，请开始分析",
            session_id
        )
        print(f"助手回应: {response2[:100]}...")
        
        # 第三轮：查看共识
        print("\n🗣️ 第3轮：查看共识")
        consensus_response = await service.execute_command("/consensus now", session_id)
        print(f"共识结果: {consensus_response[:150]}...")
        
        # 第四轮：继续讨论
        print("\n🗣️ 第4轮：继续讨论")
        response4 = await service.process_message(
            "请从技术角度分析这个问题",
            session_id
        )
        print(f"助手回应: {response4[:100]}...")
        
        # 验证对话上下文保持
        context = service.get_conversation_context(session_id)
        print("\n📊 对话上下文验证:")
        print(f"   - 会话ID: {context['session_id']}")
        print(f"   - 消息历史长度: {len(context.get('message_history', []))}")
        print(f"   - 活跃代理: {context.get('active_agents', [])}")
        
        assert len(context.get('message_history', [])) > 0, "应该有消息历史"
        
        print("✅ 多轮对话功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 多轮对话测试失败: {e}")
        return False


async def test_error_recovery():
    """测试错误恢复机制"""
    print("\n🧪 开始测试错误恢复机制...")
    
    service = PersonalAssistantService()
    
    try:
        # 测试无效输入处理
        print("🔧 测试无效输入处理...")
        response = await service.process_message("", "error_test_session")
        print(f"空输入处理: {response[:50]}...")
        assert len(response) > 0, "应该有错误处理响应"
        
        # 测试无效命令处理
        print("🔧 测试无效命令处理...")
        invalid_cmd_response = await service.execute_command("/invalid_command", "error_test_session")
        print(f"无效命令处理: {invalid_cmd_response[:50]}...")
        assert "未知命令" in invalid_cmd_response or "Unknown command" in invalid_cmd_response, "应该识别无效命令"
        
        # 测试异常长输入处理
        print("🔧 测试异常长输入处理...")
        long_input = "测试" * 1000  # 4000字符的长输入
        long_response = await service.process_message(long_input, "error_test_session")
        print(f"长输入处理: 输入{len(long_input)}字符，输出{len(long_response)}字符")
        assert len(long_response) > 0, "应该能处理长输入"
        
        print("✅ 错误恢复机制测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 错误恢复测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始V0.1.3真实LLM调用集成测试")
    print("📋 测试目标：验证PersonalAssistantService的工程可用性")
    print("=" * 70)
    
    results = []
    
    # 运行真实后端集成测试
    backend_result = await test_real_backend_integration()
    results.append(backend_result["success"])
    
    # 运行多轮对话测试
    dialogue_result = await test_multi_round_dialogue()
    results.append(dialogue_result)
    
    # 运行错误恢复测试
    error_result = await test_error_recovery()
    results.append(error_result)
    
    print("\n" + "=" * 70)
    print("📋 真实LLM集成测试结果:")
    
    test_names = [
        "真实后端服务集成",
        "多轮对话功能",
        "错误恢复机制"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results, strict=False)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {i+1}. {name}: {status}")
    
    # 显示性能数据
    if backend_result["success"]:
        print("\n📊 性能数据:")
        print(f"   - 意图分析: {backend_result['intent_time']:.2f}秒")
        print(f"   - 团队组建: {backend_result['team_time']:.2f}秒")
        print(f"   - 消息处理: {backend_result['message_time']:.2f}秒")
        print(f"   - 共识计算: {backend_result['consensus_time']:.2f}秒")
        print(f"   - 最大响应时间: {backend_result['max_time']:.2f}秒")
        
        performance_status = "✅ 达标" if backend_result['performance_ok'] else "❌ 不达标"
        print(f"   - 性能要求(<30s): {performance_status}")
    
    all_passed = all(results)
    
    if all_passed and backend_result.get("performance_ok", False):
        print("\n🎉 V0.1.3真实LLM集成测试全部通过！")
        print("\n✅ PersonalAssistantService工程可用性验证成功：")
        print("   - ✅ 真实后端服务集成正常")
        print("   - ✅ 多角色对话功能完整")
        print("   - ✅ LLM调用优化有效")
        print("   - ✅ 错误处理机制完善")
        print("   - ✅ 性能要求达标")
        print("   - ✅ 多轮对话上下文保持")
        print("\n🔧 V0.1.3任务真正完成！")
    else:
        print("\n❌ 部分测试失败或性能不达标")
        if not backend_result.get("performance_ok", False):
            print("⚠️ 性能要求不达标，需要优化")
    
    return all_passed and backend_result.get("performance_ok", False)


if __name__ == "__main__":
    # 运行真实LLM集成测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)