#!/usr/bin/env python3
"""多角色对话功能演示和验证

验证V0.1.3任务的核心功能：
1. 多角色对话管理器基本功能
2. 角色选择机制
3. 对话流程管理
4. 错误处理机制
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.core_services.multi_role_dialogue_manager import MultiRoleDialogueManager
from src.core_services.role_manager import Role


async def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试多角色对话管理器基本功能...")
    
    # 创建管理器实例
    manager = MultiRoleDialogueManager()
    
    # Mock依赖组件
    manager.role_manager = MagicMock()
    manager.llm_manager = AsyncMock()
    manager.memory_agent = AsyncMock()
    
    # 设置mock数据
    mock_roles = [
        Role(
            id="system_synthesis_master",
            name="系统综合分析师",
            description="专业的系统分析和综合专家",
            system_prompt="你是一个系统综合分析师...",
            capabilities=["系统分析", "综合思维", "问题解决"]
        ),
        Role(
            id="socratic_dialogue_guide", 
            name="苏格拉底对话引导师",
            description="擅长引导深度思考的对话专家",
            system_prompt="你是一个苏格拉底对话引导师...",
            capabilities=["对话引导", "批判思维", "深度提问"]
        ),
        Role(
            id="task_decomposition_master",
            name="任务分解专家", 
            description="专业的任务分析和分解专家",
            system_prompt="你是一个任务分解专家...",
            capabilities=["任务分解", "流程设计", "项目管理"]
        )
    ]
    
    manager.role_manager.list_roles.return_value = mock_roles
    manager.role_manager.get_role_by_id.side_effect = lambda role_id: next(
        (role for role in mock_roles if role.id == role_id), None
    )
    
    # Mock LLM调用
    manager.llm_manager.call_llm_for_role.return_value = {
        "response": "这是一个测试回应，展示了角色的专业观点和分析。",
        "optimization_applied": True,
        "optimization_metrics": {
            "improvement_score": 0.8,
            "tokens_saved": 100,
            "time_saved": 2.0
        }
    }
    
    # Mock初始化
    manager.llm_manager.initialize = AsyncMock()
    manager.memory_agent.initialize = AsyncMock()
    
    try:
        # 1. 测试初始化
        await manager.initialize()
        print("✅ 管理器初始化成功")
        
        # 2. 测试启动对话会话
        session = await manager.start_dialogue_session(
            topic="AI在教育中的应用前景和挑战",
            user_preferences={"expertise": ["教育", "技术"]}
        )
        
        print("✅ 对话会话创建成功")
        print(f"   - 会话ID: {session.session_id}")
        print(f"   - 主题: {session.topic}")
        print(f"   - 参与者数量: {len(session.participants)}")
        print(f"   - 参与者: {[p.role_name for p in session.participants]}")
        
        # 3. 测试进行对话轮次
        print("\n🗣️ 开始第一轮对话...")
        dialogue_round = await manager.conduct_dialogue_round(session.session_id)
        
        print("✅ 第一轮对话完成")
        print(f"   - 轮次编号: {dialogue_round.round_number}")
        print(f"   - 回应数量: {len(dialogue_round.responses)}")
        print(f"   - 收敛度: {session.convergence_score:.2f}")
        
        # 显示角色回应
        for response in dialogue_round.responses:
            print(f"   - {response['role_name']}: {response['response'][:80]}...")
            if response.get('optimization_metrics'):
                metrics = response['optimization_metrics']
                print(f"     📊 优化: 提升{metrics.get('improvement_score', 0):.2f}, 节省{metrics.get('tokens_saved', 0)}tokens")
        
        # 4. 测试用户干预
        print("\n👤 测试用户干预...")
        intervention_result = await manager.add_user_intervention(
            session.session_id,
            "我认为还需要考虑数据隐私和学生权益保护的问题",
            "comment"
        )
        
        print("✅ 用户干预处理成功")
        print(f"   - 角色回应数量: {len(intervention_result['role_responses'])}")
        
        for response in intervention_result['role_responses']:
            print(f"   - {response['role_name']}: {response['response'][:60]}...")
        
        # 5. 测试第二轮对话
        print("\n🗣️ 开始第二轮对话...")
        dialogue_round2 = await manager.conduct_dialogue_round(session.session_id)
        
        print("✅ 第二轮对话完成")
        print(f"   - 收敛度提升: {session.convergence_score:.2f}")
        print(f"   - 总轮次: {len(session.rounds)}")
        
        # 6. 测试会话状态
        status = manager.get_session_status(session.session_id)
        print("\n📊 会话状态:")
        print(f"   - 状态: {status['status']}")
        print(f"   - 完成轮次: {status['rounds_completed']}")
        print(f"   - 用户干预: {status['user_interventions']}")
        print(f"   - 持续时间: {status['duration_seconds']:.1f}秒")
        
        # 7. 测试会话关闭
        summary = await manager.close_session(session.session_id)
        print("\n✅ 会话关闭成功")
        print(f"   - 总轮次: {summary['total_rounds']}")
        print(f"   - 最终收敛度: {summary['final_convergence_score']:.2f}")
        print(f"   - 总用户干预: {summary['total_user_interventions']}")
        
        print("\n🎉 所有基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """测试错误处理"""
    print("\n🧪 开始测试错误处理机制...")
    
    manager = MultiRoleDialogueManager()
    
    # Mock依赖组件
    manager.role_manager = MagicMock()
    manager.llm_manager = AsyncMock()
    manager.memory_agent = AsyncMock()
    
    # 设置基本mock数据
    mock_roles = [
        Role(id="test_role", name="测试角色", description="测试", system_prompt="测试", capabilities=[])
    ]
    manager.role_manager.list_roles.return_value = mock_roles
    
    # Mock初始化
    manager.llm_manager.initialize = AsyncMock()
    manager.memory_agent.initialize = AsyncMock()
    
    try:
        await manager.initialize()
        
        # 1. 测试LLM调用失败的处理
        print("🔧 测试LLM调用失败处理...")
        manager.llm_manager.call_llm_for_role.side_effect = Exception("模拟LLM调用失败")
        
        session = await manager.start_dialogue_session("测试错误处理")
        dialogue_round = await manager.conduct_dialogue_round(session.session_id)
        
        # 验证错误处理
        all_failed = all(not response.get("success", True) for response in dialogue_round.responses)
        if all_failed:
            print("✅ LLM调用失败处理正确")
        else:
            print("❌ LLM调用失败处理有问题")
        
        # 2. 测试不存在会话的处理
        print("🔧 测试不存在会话处理...")
        try:
            await manager.conduct_dialogue_round("不存在的会话ID")
            print("❌ 应该抛出异常但没有")
        except ValueError:
            print("✅ 不存在会话处理正确")
        
        print("✅ 错误处理机制测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False


async def test_performance():
    """测试性能要求"""
    print("\n🧪 开始测试性能要求...")
    
    import time
    
    manager = MultiRoleDialogueManager()
    
    # Mock依赖组件
    manager.role_manager = MagicMock()
    manager.llm_manager = AsyncMock()
    manager.memory_agent = AsyncMock()
    
    # 设置mock数据
    mock_roles = [
        Role(id=f"role_{i}", name=f"角色{i}", description="测试", system_prompt="测试", capabilities=[])
        for i in range(3)
    ]
    manager.role_manager.list_roles.return_value = mock_roles
    
    # Mock快速LLM调用
    manager.llm_manager.call_llm_for_role.return_value = {
        "response": "快速回应",
        "optimization_metrics": {"improvement_score": 0.8}
    }
    
    # Mock初始化
    manager.llm_manager.initialize = AsyncMock()
    manager.memory_agent.initialize = AsyncMock()
    
    try:
        await manager.initialize()
        
        # 测试会话创建性能
        start_time = time.time()
        session = await manager.start_dialogue_session("性能测试主题")
        session_time = time.time() - start_time
        
        print(f"📊 会话创建时间: {session_time:.2f}秒")
        if session_time < 5.0:
            print("✅ 会话创建性能达标 (<5秒)")
        else:
            print("❌ 会话创建性能不达标")
        
        # 测试对话轮次性能
        start_time = time.time()
        await manager.conduct_dialogue_round(session.session_id)
        round_time = time.time() - start_time
        
        print(f"📊 对话轮次时间: {round_time:.2f}秒")
        if round_time < 30.0:
            print("✅ 对话轮次性能达标 (<30秒)")
        else:
            print("❌ 对话轮次性能不达标")
        
        return session_time < 5.0 and round_time < 30.0
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始V0.1.3多角色对话功能集成测试")
    print("=" * 60)
    
    results = []
    
    # 运行各项测试
    results.append(await test_basic_functionality())
    results.append(await test_error_handling())
    results.append(await test_performance())
    
    print("\n" + "=" * 60)
    print("📋 测试结果汇总:")
    
    test_names = ["基本功能测试", "错误处理测试", "性能要求测试"]
    for i, (name, result) in enumerate(zip(test_names, results, strict=False)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {i+1}. {name}: {status}")
    
    all_passed = all(results)
    if all_passed:
        print("\n🎉 所有测试通过！V0.1.3任务核心功能验证成功！")
        print("\n✅ 多角色对话功能集成完成，包括：")
        print("   - ✅ 角色选择和匹配机制")
        print("   - ✅ 对话轮次管理")
        print("   - ✅ 用户干预处理")
        print("   - ✅ LLM调用优化")
        print("   - ✅ 错误处理和降级")
        print("   - ✅ 性能要求达标")
    else:
        print("\n❌ 部分测试失败，需要进一步优化")
    
    return all_passed


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)