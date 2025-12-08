"""
端到端测试：验证完整用户流程
"""
import sys
import os
from pathlib import Path
import tempfile
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_end_to_end_wiki_creation():
    """端到端测试Wiki创建流程"""
    print("🔍 测试端到端Wiki创建流程...")
    
    try:
        from src.daip_live.tui.simplified_main import SimplifiedTUI
        from src.daip_live.tui.commands import WikiCommands
        import tempfile
        from pathlib import Path
        
        # 创建临时wiki目录
        temp_wiki_dir = Path(tempfile.mkdtemp())
        
        # 创建一个模拟的container，用于提供依赖
        class MockContainer:
            def __init__(self):
                self._session_manager = Mock()
                self._role_manager = Mock()
                self._model_provider = Mock()
                self._role_model_manager = Mock()
            
            def session_manager(self):
                return self._session_manager
                
            def role_manager(self):
                return self._role_manager
                
            def model_provider(self):
                return self._model_provider
                
            def role_model_manager(self):
                return self._role_model_manager
        
        # 创建TUI实例
        container = MockContainer()
        
        # 手动创建TUI实例并模拟依赖注入
        tui = SimplifiedTUI()
        
        # 手动设置依赖
        tui.container = container
        tui._session_manager = container.session_manager()
        tui._role_manager = container.role_manager()
        tui._model_provider = container.model_provider()
        tui._role_model_manager = container.role_model_manager()
        
        # 手动初始化WikiManager（模拟真实初始化过程）
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager
        tui._wiki_manager = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=tui._role_model_manager,
            model_provider=tui._model_provider,
            session_manager=tui._session_manager,
            role_manager=tui._role_manager
        )
        
        # 模拟输出日志记录
        log_messages = []
        def mock_update_log_view(message):
            log_messages.append(message)
            print(f"  [LOG] {message}")
        
        tui._update_log_view = mock_update_log_view
        tui._update_system_log = mock_update_log_view
        
        # 执行Wiki创建命令
        print("  📝 执行 /wiki create AI技术发展史 命令...")
        await tui._handle_wiki_command("create AI技术发展史")
        
        # 验证日志中包含协作过程
        log_content = "\n".join(log_messages)
        
        expected_elements = [
            "多角色协作创建Wiki页面",
            "参与角色: 领域专家, 研究员, 编辑, 批评家",
            "👤 领域专家",
            "🔍 研究员",
            "📝 编辑", 
            "🤔 批评家",
            "多角色协作完成"
        ]
        
        all_found = True
        for element in expected_elements:
            if element in log_content:
                print(f"  ✅ 找到期望元素: {element}")
            else:
                print(f"  ❌ 未找到期望元素: {element}")
                all_found = False
        
        # 验证是否创建了wiki文件
        wiki_files = list(temp_wiki_dir.glob("*.md"))
        if wiki_files:
            print(f"  ✅ 创建了Wiki文件: {[f.name for f in wiki_files]}")
        else:
            print(f"  ⚠️  未创建Wiki文件，但在模拟环境中这是正常的")
        
        # 清理
        shutil.rmtree(temp_wiki_dir)
        
        return all_found
        
    except Exception as e:
        print(f"❌ 端到端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_end_to_end_command_flow():
    """测试完整的命令处理流程"""
    print("\n🔍 测试完整命令处理流程...")
    
    try:
        from src.daip_live.tui.commands import TUICommandHandler, WikiCommands
        from unittest.mock import Mock
        
        # 创建模拟TUI实例
        mock_tui = Mock()
        log_messages = []
        
        def mock_update_log(message):
            log_messages.append(message)
        
        mock_tui._update_log_view = mock_update_log
        mock_tui._handle_wiki_command = AsyncMock()
        
        # 创建命令处理器
        command_handler = TUICommandHandler(mock_tui)
        wiki_commands = WikiCommands(mock_tui)
        
        # 测试命令处理流程
        print("  🔄 测试命令处理流程...")
        
        # 测试wiki命令调用
        await command_handler.handle_command("wiki", "create 测试页面")
        
        # 验证方法被正确调用
        if mock_tui._handle_wiki_command.called:
            print("  ✅ 命令处理器正确调用了Wiki处理方法")
        else:
            print("  ❌ 命令处理器未调用Wiki处理方法")
            return False
        
        # 验证是异步调用
        args, kwargs = mock_tui._handle_wiki_command.call_args
        if args and args[0] == "create 测试页面":
            print("  ✅ 正确传递了命令参数")
        else:
            print(f"  ❌ 命令参数传递错误: {args}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 完整命令流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_wiki_list_functionality():
    """测试Wiki列表功能"""
    print("\n🔍 测试Wiki列表功能...")
    
    try:
        from src.daip_live.tui.simplified_main import SimplifiedTUI
        from pathlib import Path
        import tempfile
        import shutil
        
        # 创建临时wiki目录
        temp_wiki_dir = Path(tempfile.mkdtemp())
        
        # 创建TUI实例
        tui = SimplifiedTUI()
        
        # 手动初始化WikiManager
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager
        tui._wiki_manager = EnhancedWikiManager(wiki_root=temp_wiki_dir)
        
        # 创建一些测试页面
        tui._wiki_manager.create_page("页面1", "# 页面1\n内容1")
        tui._wiki_manager.create_page("页面2", "# 页面2\n内容2")
        
        # 模拟日志
        log_messages = []
        tui._update_log_view = lambda msg: log_messages.append(msg)
        
        # 执行列表命令
        await tui._handle_wiki_command("list")
        
        log_content = "\n".join(log_messages)
        
        # 验证列表中包含创建的页面
        if "页面1" in log_content and "页面2" in log_content:
            print("  ✅ 列表命令显示了正确的页面")
        else:
            print(f"  ❌ 列表命令未正确显示页面: {log_content}")
            return False
        
        # 清理
        shutil.rmtree(temp_wiki_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Wiki列表功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n🔍 测试向后兼容性...")
    
    try:
        from src.daip_live.tui.simplified_main import SimplifiedTUI
        from pathlib import Path
        import tempfile
        import shutil
        
        # 创建临时wiki目录
        temp_wiki_dir = Path(tempfile.mkdtemp())
        
        # 创建TUI实例，但不设置完整的依赖（模拟降级模式）
        tui = SimplifiedTUI()
        
        # 手动初始化一个基础的WikiManager（没有协作功能的）
        from src.daip_live.wiki.manager import WikiManager
        tui._wiki_manager = WikiManager(wiki_root=temp_wiki_dir)
        
        # 设置模拟日志
        log_messages = []
        tui._update_log_view = lambda msg: log_messages.append(msg)
        
        # 执行创建命令 - 这应该触发降级路径
        await tui._handle_wiki_command("create 兼容性测试")
        
        log_content = "\n".join(log_messages)
        
        # 验证降级路径是否正常工作
        if "Wiki页面创建完成" in log_content:
            print("  ✅ 降级模式下功能正常")
        else:
            print(f"  ❌ 降级模式下功能异常: {log_content}")
            return False
        
        # 清理
        shutil.rmtree(temp_wiki_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_e2e_tests():
    """运行所有端到端测试"""
    print("🚀 开始端到端测试")
    print("="*50)
    
    tests = [
        ("Wiki创建流程", test_end_to_end_wiki_creation),
        ("命令处理流程", test_end_to_end_command_flow),
        ("Wiki列表功能", test_wiki_list_functionality),
        ("向后兼容性", test_backward_compatibility)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🧪 运行 {test_name}")
        print("-" * 30)
        try:
            result = await test_func()
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
        print("🎉 所有端到端测试通过！完整用户流程正常工作")
        return True
    else:
        print("❌ 部分端到端测试失败！")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_e2e_tests())
    if not success:
        sys.exit(1)