#!/usr/bin/env python3
"""
测试Forum组件修复状态
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_forum_context_panel():
    """测试ForumContextPanel"""
    print("Testing ForumContextPanel...")
    
    try:
        from frontend.components.forum_context_panel import ForumContextPanel
        
        # 测试实例化
        context_panel = ForumContextPanel(session_id='test_session')
        print("✓ ForumContextPanel instantiation successful")
        
        # 测试set_topic方法
        context_panel.set_topic('Test Topic')
        print("✓ ForumContextPanel set_topic successful")
        
        # 测试上下文更新
        context_data = {
            "topic": "Test Topic Updated",
            "consensus_level": 0.75,
            "active_agents": ["agent1", "agent2"],
            "key_arguments": [{"content": "argument 1", "sender": "agent1"}],
            "status": "active",
            "message_count": 5,
            "user_intervention_count": 2,
            "duration": 120
        }
        context_panel.update_context(context_data)
        print("✓ ForumContextPanel update_context successful")
        
        return True
        
    except Exception as e:
        print(f"✗ ForumContextPanel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forum_user_input_panel():
    """测试ForumUserInputPanel"""
    print("\nTesting ForumUserInputPanel...")
    
    try:
        from frontend.components.forum_user_input_panel import ForumUserInputPanel
        
        # 测试实例化
        input_panel = ForumUserInputPanel(session_id='test_session')
        print("✓ ForumUserInputPanel instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"✗ ForumUserInputPanel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forum_service():
    """测试ForumService"""
    print("\nTesting ForumService...")
    
    try:
        from src.core_services.forum_service import forum_service
        
        # 测试基本功能
        stats = forum_service.get_session_statistics()
        print("✓ ForumService get_session_statistics successful")
        print(f"  Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ ForumService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=== Forum Component Repair Test ===\n")
    
    results = []
    
    # 测试各个组件
    results.append(test_forum_context_panel())
    results.append(test_forum_user_input_panel())
    results.append(test_forum_service())
    
    # 汇总结果
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All Forum components are working correctly!")
        return 0
    else:
        print("❌ Some components still need repair.")
        return 1

if __name__ == "__main__":
    exit(main())