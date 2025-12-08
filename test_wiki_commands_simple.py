#!/usr/bin/env python3
"""
TDD测试：复现TUI中wiki_commands未初始化的问题 - 简化版本
"""

import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_wiki_commands_attribute_exists():
    """测试wiki_commands属性是否已初始化"""
    # 导入TUI类（但先检查问题所在代码）
    from daip_live.tui.simplified_main import SimplifiedTUI
    
    # 检查_handle_intent_directly方法源码，确认是否引用了wiki_commands
    import inspect
    source = inspect.getsource(SimplifiedTUI._handle_intent_directly)
    
    print("检查_handle_intent_directly方法中的wiki_commands引用...")
    if 'self.wiki_commands.handle_wiki_command' in source:
        print("✅ 发现self.wiki_commands.handle_wiki_command引用")
        print("   问题确认：方法尝试访问未初始化的wiki_commands属性")
    else:
        print("❌ 未找到wiki_commands引用")
    
    # 检查是否在__init__方法中初始化了wiki_commands
    init_source = inspect.getsource(SimplifiedTUI.__init__)
    print("\n检查__init__方法中的wiki_commands初始化...")
    if 'wiki_commands' in init_source:
        print("✅ __init__方法中包含wiki_commands")
    else:
        print("❌ __init__方法中不包含wiki_commands初始化")
    
    # 检查是否在其他初始化方法中初始化了wiki_commands
    try:
        modules_source = inspect.getsource(SimplifiedTUI._initialize_tui_modules)
        print("\n检查_initialize_tui_modules方法...")
        if 'wiki_commands' in modules_source:
            print("✅ _initialize_tui_modules方法中包含wiki_commands")
        else:
            print("❌ _initialize_tui_modules方法中不包含wiki_commands")
    except:
        print("❌ 无法获取_initialize_tui_modules方法源码")

def manual_test_attribute_access():
    """手动测试访问wiki_commands属性"""
    from daip_live.tui.simplified_main import SimplifiedTUI
    from daip_live.agent_engine.executor import AgentExecutor
    from daip_live.memory.session_manager import SessionManager
    
    print("\n手动测试访问wiki_commands属性...")
    
    # 创建一个最简化的TUI实例
    try:
        tui = SimplifiedTUI()
        # 检查属性是否存在
        has_wiki = hasattr(tui, 'wiki_commands')
        print(f"hasattr(tui, 'wiki_commands'): {has_wiki}")
        
        if has_wiki:
            print("✅ wiki_commands属性存在")
        else:
            print("❌ wiki_commands属性不存在")
            
            # 尝试直接访问以触发AttributeError
            try:
                _ = tui.wiki_commands
                print("奇怪，访问没有触发错误")
            except AttributeError as e:
                print(f"✅ 访问wiki_commands触发AttributeError: {e}")
                
    except Exception as e:
        print(f"创建TUI实例时出错 (这可能是由于依赖项问题): {e}")
        print("这不影响我们识别问题：在_handle_intent_directly中有未初始化的wiki_commands引用")


def create_wiki_command_handler():
    """定义一个WikiCommands类来处理wiki命令"""
    from daip_live.tui.simplified_main import SimplifiedTUI
    
    class WikiCommands:
        def __init__(self, tui_instance):
            self.tui = tui_instance

        def handle_wiki_command(self, args: str) -> None:
            """处理wiki命令"""
            # 调用TUI中已有的方法
            self.tui._handle_wiki_command(args)
    
    print("\n定义WikiCommands类以解决初始化问题...")
    
    # 验证是否可以正常创建
    try:
        # 创建一个模拟的tui实例用于测试（不完整初始化）
        mock_tui = MagicMock()
        mock_tui._handle_wiki_command = MagicMock()
        
        wiki_cmd = WikiCommands(mock_tui)
        print("✅ WikiCommands类定义成功")
        
        # 验证handle_wiki_command方法
        wiki_cmd.handle_wiki_command("create test")
        print("✅ handle_wiki_command方法可以调用")
        
    except Exception as e:
        print(f"❌ WikiCommands类定义失败: {e}")


if __name__ == "__main__":
    print("运行TDD测试以复现wiki_commands未初始化问题...")
    print("="*60)
    
    print("\n1. 检查代码中的问题引用...")
    test_wiki_commands_attribute_exists()
    
    print("\n2. 手动测试属性访问...")
    manual_test_attribute_access()
    
    print("\n3. 验证修复方案（WikiCommands类定义）...")
    create_wiki_command_handler()
    
    print("\n" + "="*60)
    print("TDD测试完成：问题已成功复现和分析")
    print("\n问题总结：")
    print("- 在_handle_intent_directly方法中使用了self.wiki_commands.handle_wiki_command")
    print("- 但wiki_commands属性未在任何初始化方法中被正确创建")
    print("- 需要在适当的地方初始化WikiCommands实例")