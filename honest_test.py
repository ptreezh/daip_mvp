#!/usr/bin/env python3
"""
真实的Forum组件测试
"""
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=== DAIP-LIVE Forum 组件真实测试 ===")
print(f"当前目录: {current_dir}")
print(f"Python路径: {sys.path[0]}")

# 测试1: 基本模块导入
print("\n1. 测试基本模块导入...")
try:
    import logging
    print("✓ logging 模块导入成功")
except Exception as e:
    print(f"✗ logging 模块导入失败: {e}")

try:
    from lona.html import Div, HTML
    print("✓ lona.html 模块导入成功")
except Exception as e:
    print(f"✗ lona.html 模块导入失败: {e}")

# 测试2: ForumService
print("\n2. 测试 ForumService...")
try:
    from src.core_services.forum_service import forum_service
    stats = forum_service.get_session_statistics()
    print("✓ ForumService 导入成功")
    print(f"✓ ForumService 功能正常: {stats}")
except Exception as e:
    print(f"✗ ForumService 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: ForumUserInputPanel
print("\n3. 测试 ForumUserInputPanel...")
try:
    from frontend.components.forum_user_input_panel import ForumUserInputPanel
    input_panel = ForumUserInputPanel(session_id='test_session')
    print("✓ ForumUserInputPanel 导入成功")
    print("✓ ForumUserInputPanel 实例化成功")
except Exception as e:
    print(f"✗ ForumUserInputPanel 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: ForumContextPanel
print("\n4. 测试 ForumContextPanel...")
try:
    from frontend.components.forum_context_panel import ForumContextPanel
    context_panel = ForumContextPanel(session_id='test_session')
    print("✓ ForumContextPanel 导入成功")
    print("✓ ForumContextPanel 实例化成功")
    
    # 测试基本功能
    context_panel.set_topic("测试话题")
    print("✓ ForumContextPanel set_topic 方法正常")
except Exception as e:
    print(f"✗ ForumContextPanel 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")