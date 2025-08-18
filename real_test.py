#!/usr/bin/env python3
"""
真实的Forum组件测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_forum_service():
    """测试ForumService"""
    print("=== 测试 ForumService ===")
    try:
        from src.core_services.forum_service import forum_service
        stats = forum_service.get_session_statistics()
        print("✓ ForumService 导入成功")
        print(f"✓ ForumService 基本功能正常: {stats}")
        return True
    except Exception as e:
        print(f"✗ ForumService 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forum_user_input_panel():
    """测试ForumUserInputPanel"""
    print("\n=== 测试 ForumUserInputPanel ===")
    try:
        from frontend.components.forum_user_input_panel import ForumUserInputPanel
        input_panel = ForumUserInputPanel(session_id='test_session')
        print("✓ ForumUserInputPanel 导入成功")
        print("✓ ForumUserInputPanel 实例化成功")
        return True
    except Exception as e:
        print(f"✗ ForumUserInputPanel 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_original_forum_context_panel():
    """测试原始ForumContextPanel"""
    print("\n=== 测试 原始 ForumContextPanel ===")
    try:
        from frontend.components.forum_context_panel import ForumContextPanel
        context_panel = ForumContextPanel(session_id='test_session')
        print("✓ 原始ForumContextPanel 导入成功")
        print("✓ 原始ForumContextPanel 实例化成功")
        
        # 测试基本功能
        context_panel.set_topic("测试话题")
        print("✓ 原始ForumContextPanel set_topic 方法正常")
        
        return True
    except Exception as e:
        print(f"✗ 原始ForumContextPanel 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_new_forum_context_panel():
    """测试新版本ForumContextPanel"""
    print("\n=== 测试 新版本 ForumContextPanel ===")
    try:
        from frontend.components.forum_context_panel_new import ForumContextPanel as NewContextPanel
        new_context_panel = NewContextPanel(session_id='test_session')
        print("✓ 新版本ForumContextPanel 导入成功")
        print("✓ 新版本ForumContextPanel 实例化成功")
        
        # 测试基本功能
        new_context_panel.set_topic("测试话题")
        print("✓ 新版本ForumContextPanel set_topic 方法正常")
        
        return True
    except Exception as e:
        print(f"✗ 新版本ForumContextPanel 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_debate_stream():
    """测试DebateStream"""
    print("\n=== 测试 DebateStream ===")
    try:
        from frontend.components.debate_stream import DebateStream
        debate_stream = DebateStream(session_id='test_session', topic='测试话题')
        print("✓ DebateStream 导入成功")
        print("✓ DebateStream 实例化成功")
        return True
    except Exception as e:
        print(f"✗ DebateStream 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consensus_visualizer():
    """测试共识可视化组件"""
    print("\n=== 测试 ConsensusVisualizer ===")
    try:
        from frontend.components.consensus_visualizer import ConsensusVisualizer
        consensus_viz = ConsensusVisualizer(session_id='test_session')
        print("✓ ConsensusVisualizer 导入成功")
        print("✓ ConsensusVisualizer 实例化成功")
        return True
    except Exception as e:
        print(f"✗ ConsensusVisualizer 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("DAIP-LIVE Forum 组件真实测试")
    print("=" * 50)
    
    # 执行所有测试
    results = []
    results.append(("ForumService", test_forum_service()))
    results.append(("ForumUserInputPanel", test_forum_user_input_panel()))
    results.append(("原始ForumContextPanel", test_original_forum_context_panel()))
    results.append(("新版本ForumContextPanel", test_new_forum_context_panel()))
    results.append(("DebateStream", test_debate_stream()))
    results.append(("ConsensusVisualizer", test_consensus_visualizer()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有组件测试通过！")
        return 0
    else:
        print("❌ 部分组件测试失败")
        return 1

if __name__ == "__main__":
    exit(main())