"""
回归测试：验证原有功能未被破坏
"""
import sys
import os
from pathlib import Path
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """测试基本导入是否正常"""
    print("🔍 测试基本导入...")
    try:
        from src.daip_live.tui.simplified_main import SimplifiedTUI
        print("✅ SimplifiedTUI 导入成功")
        
        from src.daip_live.wiki.manager import WikiManager
        print("✅ WikiManager 导入成功")
        
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager, MultiRoleWikiCollaborator
        print("✅ EnhancedWikiManager 和 MultiRoleWikiCollaborator 导入成功")
        
        from src.daip_live.tui.commands import TUICommandHandler, WikiCommands
        print("✅ TUI命令处理模块导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_syntax_validity():
    """测试文件语法是否有效"""
    print("\n🔍 测试文件语法有效性...")
    files_to_test = [
        "src/daip_live/tui/simplified_main.py",
        "src/daip_live/tui/commands.py",
        "src/daip_live/wiki/collaborative_wiki.py"
    ]
    
    import ast
    for file_path in files_to_test:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            print(f"✅ {file_path} 语法正确")
        except SyntaxError as e:
            print(f"❌ {file_path} 语法错误: {e}")
            return False
        except Exception as e:
            print(f"❌ {file_path} 读取错误: {e}")
            return False
    
    return True

def test_wiki_manager_basic_functionality():
    """测试WikiManager基本功能"""
    print("\n🔍 测试WikiManager基本功能...")
    try:
        import tempfile
        import shutil
        from pathlib import Path
        from src.daip_live.wiki.manager import WikiManager
        
        # 创建临时目录进行测试
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # 测试基础WikiManager
            wiki_manager = WikiManager(wiki_root=temp_dir)
            
            # 测试页面创建
            test_page = wiki_manager.create_page("测试页面", "# 测试\n这是测试内容")
            print("✅ WikiManager.create_page() 功能正常")
            
            # 测试页面列表
            pages = wiki_manager.list_all_pages()
            page_titles = [page.title for page in pages]
            assert "测试页面" in page_titles, "页面应该在列表中"
            print("✅ WikiManager.list_all_pages() 功能正常")
            
            # 测试页面获取
            retrieved_page = wiki_manager.get_page_by_title("测试页面")
            assert retrieved_page is not None, "页面应该能被获取"
            print("✅ WikiManager.get_page_by_title() 功能正常")
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            print("✅ WikiManager基础功能测试通过")
            
        except Exception as e:
            # 清理临时文件
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            print(f"❌ WikiManager基础功能测试失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ WikiManager测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_original_tui_functionality():
    """测试TUI原有功能是否正常"""
    print("\n🔍 测试TUI原有功能...")
    try:
        # 仅测试导入和基本属性，不启动完整TUI应用
        from src.daip_live.tui.simplified_main import SimplifiedTUI
        import inspect
        
        # 检查关键方法是否存在
        methods_to_check = [
            '_initialize_tui_modules',
            '_initialize_role_manager', 
            '_initialize_debate_manager',
            '_initialize_knowledge_manager',
            '_initialize_wiki_manager',  # 新添加的
            '_handle_wiki_command',      # 修改的
        ]
        
        for method_name in methods_to_check:
            method_exists = hasattr(SimplifiedTUI, method_name) or \
                           method_name in dir(SimplifiedTUI)
            if method_exists:
                print(f"✅ {method_name} 方法存在")
            else:
                print(f"❌ {method_name} 方法不存在")
                return False
        
        print("✅ TUI关键方法存在性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ TUI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_handler_compatibility():
    """测试命令处理器兼容性"""
    print("\n🔍 测试命令处理器兼容性...")
    try:
        from src.daip_live.tui.commands import TUICommandHandler, WikiCommands
        from unittest.mock import Mock
        
        # 创建模拟TUI实例
        mock_tui = Mock()
        mock_tui._available_commands = []
        
        # 测试WikiCommands初始化
        wiki_commands = WikiCommands(mock_tui)
        print("✅ WikiCommands初始化成功")
        
        # 验证方法是否存在
        assert hasattr(wiki_commands, 'handle_wiki_command'), "handle_wiki_command方法应存在"
        print("✅ WikiCommands.handle_wiki_command方法存在")
        
        # 验证方法是否为异步
        import asyncio
        assert asyncio.iscoroutinefunction(wiki_commands.handle_wiki_command), "handle_wiki_command应为异步方法"
        print("✅ WikiCommands.handle_wiki_command为异步方法")
        
        # 测试TUICommandHandler初始化
        command_handler = TUICommandHandler(mock_tui)
        print("✅ TUICommandHandler初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 命令处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_regression_tests():
    """运行所有回归测试"""
    print("🚀 开始回归测试")
    print("="*50)
    
    tests = [
        ("基本导入测试", test_basic_imports),
        ("语法有效性测试", test_syntax_validity),
        ("WikiManager功能测试", test_wiki_manager_basic_functionality),
        ("TUI功能测试", test_original_tui_functionality),
        ("命令处理器兼容性测试", test_command_handler_compatibility)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🧪 运行 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 所有回归测试通过！原有功能未被破坏")
        return True
    else:
        print("❌ 部分回归测试失败！")
        return False

if __name__ == "__main__":
    success = run_regression_tests()
    if not success:
        sys.exit(1)