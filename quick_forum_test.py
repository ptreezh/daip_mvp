#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 15:45:00
@Author  : DAIP-LIVE Team
@File    : quick_forum_test.py
@Description:
    Forum模式快速验证测试 - 验证基本功能是否正常工作
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.core_services.forum_service import forum_service
from src.core_services.forum_service import ForumSession, DebateOrchestrator, UserInterventionManager, ConsensusTracker
from src.api.routers.forum import forum_router
from src.app_state import app_state


async def test_forum_service_basic():
    """测试Forum服务基本功能"""
    print("🧪 测试Forum服务基本功能...")
    
    try:
        # 1. 测试服务初始化
        print("  ✓ 服务初始化")
        assert forum_service is not None
        
        # 2. 测试会话创建
        print("  ✓ 创建测试会话")
        session = await forum_service.start_forum_session(
            topic="人工智能的发展趋势",
            user_id="test_user"
        )
        
        assert session is not None
        assert session.session_id is not None
        assert session.topic == "人工智能的发展趋势"
        assert session.status == "active"
        
        session_id = session.session_id
        print(f"    会话ID: {session_id}")
        
        # 3. 测试会话上下文
        print("  ✓ 获取会话上下文")
        context = await forum_service.get_session_context(session_id)
        assert context is not None
        assert context["session_id"] == session_id
        assert context["topic"] == session.topic
        
        # 4. 测试用户干预
        print("  ✓ 处理用户干预")
        user_message = {
            "content": "AI将改变我们的生活",
            "intent": "comment"
        }
        
        result = await forum_service.handle_user_intervention(session_id, user_message)
        assert result["status"] == "integrated"
        assert "optimized_input" in result
        
        # 5. 测试会话控制
        print("  ✓ 会话控制测试")
        
        # 暂停
        pause_result = await forum_service.pause_session(session_id)
        assert pause_result is True
        
        # 恢复
        resume_result = await forum_service.resume_session(session_id)
        assert resume_result is True
        
        # 6. 测试统计信息
        print("  ✓ 获取统计信息")
        stats = forum_service.get_session_statistics()
        assert "total_sessions" in stats
        assert "active_sessions" in stats
        assert "average_consensus" in stats
        
        # 7. 测试会话结束
        print("  ✓ 结束会话")
        end_result = await forum_service.end_session(session_id)
        assert end_result is not None
        assert end_result["session_id"] == session_id
        
        print("✅ Forum服务基本功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ Forum服务基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_forum_components():
    """测试Forum组件"""
    print("🧪 测试Forum组件...")
    
    try:
        # 1. 测试UserInterventionManager
        print("  ✓ UserInterventionManager")
        intervention_manager = UserInterventionManager()
        
        optimized = await intervention_manager.optimize_input(
            "AI很重要", "comment", "测试话题"
        )
        assert isinstance(optimized, str)
        assert len(optimized) > 0
        
        # 2. 测试ConsensusTracker
        print("  ✓ ConsensusTracker")
        consensus_tracker = ConsensusTracker()
        
        # 添加测试消息
        test_message = {
            "type": "agent",
            "content": "这是一个测试消息",
            "sender": "test_agent",
            "timestamp": "2025-08-06T15:45:00"
        }
        
        await consensus_tracker.update_with_message("test_session", test_message)
        
        consensus_level = await consensus_tracker.get_consensus_level("test_session")
        assert isinstance(consensus_level, float)
        assert 0.0 <= consensus_level <= 1.0
        
        # 3. 测试DebateOrchestrator
        print("  ✓ DebateOrchestrator")
        debate_orchestrator = DebateOrchestrator()
        assert debate_orchestrator is not None
        
        print("✅ Forum组件测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ Forum组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_forum_integration():
    """测试Forum集成"""
    print("🧪 测试Forum集成...")
    
    try:
        # 1. 测试多轮讨论
        print("  ✓ 多轮讨论测试")
        session = await forum_service.start_forum_session(
            topic="区块链技术应用",
            user_id="integration_user"
        )
        
        session_id = session.session_id
        
        # 模拟多轮讨论
        interventions = [
            {"content": "区块链在金融领域很有前景", "intent": "comment"},
            {"content": "如何解决扩展性问题？", "intent": "question"},
            {"content": "建议考虑Layer 2解决方案", "intent": "suggestion"},
            {"content": "需要平衡去中心化和效率", "intent": "comment"}
        ]
        
        for i, intervention in enumerate(interventions):
            result = await forum_service.handle_user_intervention(session_id, intervention)
            assert result["status"] == "integrated"
            
            # 检查上下文更新
            context = await forum_service.get_session_context(session_id)
            assert context["user_intervention_count"] == i + 1
        
        # 2. 测试共识发展
        print("  ✓ 共识发展测试")
        final_context = await forum_service.get_session_context(session_id)
        assert final_context["consensus_level"] >= 0.0
        assert final_context["message_count"] >= len(interventions)
        
        # 3. 测试会话状态
        print("  ✓ 会话状态测试")
        assert final_context["status"] == "active"
        assert final_context["active_agents"] is not None
        assert len(final_context["active_agents"]) > 0
        
        # 4. 结束会话
        await forum_service.end_session(session_id)
        
        print("✅ Forum集成测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ Forum集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_forum_performance():
    """测试Forum性能"""
    print("🧪 测试Forum性能...")
    
    try:
        import time
        
        # 1. 测试会话创建性能
        print("  ✓ 会话创建性能")
        start_time = time.time()
        
        sessions = []
        for i in range(3):
            session = await forum_service.start_forum_session(
                topic=f"性能测试话题 {i}",
                user_id=f"perf_user_{i}"
            )
            sessions.append(session)
        
        creation_time = time.time() - start_time
        print(f"    创建 {len(sessions)} 个会话耗时: {creation_time:.2f}秒")
        assert creation_time < 10.0  # 应该在10秒内完成
        
        # 2. 测试并发干预性能
        print("  ✓ 并发干预性能")
        start_time = time.time()
        
        intervention_tasks = []
        for session in sessions:
            for i in range(2):
                task = forum_service.handle_user_intervention(
                    session.session_id,
                    {"content": f"并发干预 {i}", "intent": "comment"}
                )
                intervention_tasks.append(task)
        
        results = await asyncio.gather(*intervention_tasks)
        intervention_time = time.time() - start_time
        
        print(f"    处理 {len(results)} 个干预耗时: {intervention_time:.2f}秒")
        assert intervention_time < 15.0  # 应该在15秒内完成
        
        # 3. 清理会话
        for session in sessions:
            await forum_service.end_session(session.session_id)
        
        print("✅ Forum性能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ Forum性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🏛️ Forum模式快速验证测试")
    print("=" * 50)
    
    results = []
    
    # 运行所有测试
    tests = [
        test_forum_service_basic,
        test_forum_components,
        test_forum_integration,
        test_forum_performance
    ]
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
        
        print()  # 添加空行分隔
    
    # 总结结果
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! Forum模式功能正常!")
        return True
    else:
        print("💥 部分测试失败，请检查上述错误信息")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)