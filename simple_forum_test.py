#!/usr/bin/env python3
"""@Time    : 2025-08-06 16:00:00
@Author  : DAIP-LIVE Team
@File    : simple_forum_test.py
@Description:
    简单Forum测试 - 验证Forum服务基本功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.app_state import AppState


async def test_forum_service():
    """测试Forum服务基本功能"""
    print("测试Forum服务基本功能...")
    
    try:
        # 初始化应用状态
        print("  [OK] 初始化应用状态")
        app_state_instance = AppState()
        
        # 设置全局应用状态
        import src.api.dependencies as deps
        deps.app_state = app_state_instance
        
        # 导入Forum服务
        from src.core_services.forum_service import forum_service
        
        # 1. 测试服务初始化
        print("  [OK] 服务初始化")
        assert forum_service is not None
        
        # 2. 测试会话创建
        print("  [OK] 创建测试会话")
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
        print("  [OK] 获取会话上下文")
        context = await forum_service.get_session_context(session_id)
        assert context is not None
        assert context["session_id"] == session_id
        assert context["topic"] == session.topic
        
        # 4. 测试用户干预
        print("  [OK] 处理用户干预")
        user_message = {
            "content": "AI将改变我们的生活",
            "intent": "comment"
        }
        
        result = await forum_service.handle_user_intervention(session_id, user_message)
        assert result["status"] == "integrated"
        assert "optimized_input" in result
        
        # 5. 测试会话控制
        print("  [OK] 会话控制测试")
        
        # 暂停
        pause_result = await forum_service.pause_session(session_id)
        assert pause_result is True
        
        # 恢复
        resume_result = await forum_service.resume_session(session_id)
        assert resume_result is True
        
        # 6. 测试统计信息
        print("  [OK] 获取统计信息")
        stats = forum_service.get_session_statistics()
        assert "total_sessions" in stats
        assert "active_sessions" in stats
        assert "average_consensus" in stats
        
        # 7. 测试会话结束
        print("  [OK] 结束会话")
        end_result = await forum_service.end_session(session_id)
        assert end_result is not None
        assert end_result["session_id"] == session_id
        
        print("Forum服务基本功能测试通过!")
        return True
        
    except Exception as e:
        print(f"Forum服务基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_forum_components():
    """测试Forum组件"""
    print("测试Forum组件...")
    
    try:
        # 初始化应用状态
        app_state_instance = AppState()
        
        # 设置全局应用状态
        import src.api.dependencies as deps
        deps.app_state = app_state_instance
        
        from src.core_services.forum_service import ConsensusTracker, UserInterventionManager
        
        # 1. 测试UserInterventionManager
        print("  [OK] UserInterventionManager")
        intervention_manager = UserInterventionManager()
        
        optimized = await intervention_manager.optimize_input(
            "AI很重要", "comment", "测试话题"
        )
        assert isinstance(optimized, str)
        assert len(optimized) > 0
        
        # 2. 测试ConsensusTracker
        print("  [OK] ConsensusTracker")
        consensus_tracker = ConsensusTracker()
        
        # 添加测试消息
        test_message = {
            "type": "agent",
            "content": "这是一个测试消息",
            "sender": "test_agent",
            "timestamp": "2025-08-06T16:00:00"
        }
        
        await consensus_tracker.update_with_message("test_session", test_message)
        
        consensus_level = await consensus_tracker.get_consensus_level("test_session")
        assert isinstance(consensus_level, float)
        assert 0.0 <= consensus_level <= 1.0
        
        print("Forum组件测试通过!")
        return True
        
    except Exception as e:
        print(f"Forum组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("Forum模式简单验证测试")
    print("=" * 50)
    
    results = []
    
    # 运行所有测试
    tests = [
        test_forum_service,
        test_forum_components
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
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过! Forum模式功能正常!")
        return True
    else:
        print("部分测试失败，请检查上述错误信息")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)