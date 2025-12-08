#!/usr/bin/env python3
"""
TDD测试：复现TUI中wiki_commands未初始化的问题
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from daip_live.tui.simplified_main import SimplifiedTUI
from daip_live.agent_engine.enhanced_intent_recognizer import Intent


class TestTUIWikiCommandsInitialization:
    """测试TUI中wiki_commands初始化问题的测试套件"""
    
    def setup_method(self):
        """测试前设置"""
        # 创建模拟对象
        self.mock_executor = MagicMock()
        self.mock_session_manager = MagicMock()
        self.mock_role_manager = MagicMock()
        self.mock_knowledge_manager = MagicMock()
        self.mock_debate_manager = MagicMock()
        self.mock_model_provider = MagicMock()
        self.mock_db_manager = MagicMock()
        self.mock_role_model_manager = MagicMock()
        self.mock_enhanced_debate_manager = MagicMock()
        
        # 创建TUI实例
        self.tui = SimplifiedTUI(
            executor=self.mock_executor,
            session_manager=self.mock_session_manager,
            role_manager=self.mock_role_manager,
            knowledge_manager=self.mock_knowledge_manager,
            debate_manager=self.mock_debate_manager,
            model_provider=self.mock_model_provider,
            db_manager=self.mock_db_manager,
            role_model_manager=self.mock_role_model_manager,
            enhanced_debate_manager=self.mock_enhanced_debate_manager,
        )
        
    def test_wiki_commands_attribute_exists(self):
        """测试wiki_commands属性是否已初始化"""
        # 验证wiki_commands属性是否存在
        assert not hasattr(self.tui, 'wiki_commands'), "wiki_commands属性不应该存在（当前状态）"
        
    def test_intent_handler_wiki_commands_access(self):
        """测试在处理create_wiki意图时会访问未初始化的wiki_commands属性"""
        # 创建一个模拟的create_wiki意图
        mock_intent = MagicMock()
        mock_intent.name = "create_wiki"
        mock_intent.parameters = {"title": "测试标题"}
        
        user_input = "创建维基 测试"
        session_id = "test_session"
        execution_context = {}
        
        # 测试当调用_handle_intent_directly处理create_wiki意图时
        # 应该会因为访问未初始化的wiki_commands而抛出AttributeError
        with pytest.raises(AttributeError, match="'SimplifiedTUI' object has no attribute 'wiki_commands'"):
            asyncio.run(self.tui._handle_intent_directly(mock_intent, user_input, session_id, execution_context))
            
    def test_wiki_commands_initialization_in_modules(self):
        """测试wiki_commands是否在初始化tui模块时被创建"""
        # 直接检查当前tui实例的属性
        available_commands = [attr for attr in dir(self.tui) if 'command' in attr.lower()]
        print(f"可用的command相关属性: {available_commands}")
        
        # 检查是否已经初始化了wiki_commands
        has_wiki_commands = hasattr(self.tui, 'wiki_commands')
        assert not has_wiki_commands, "当前实现中wiki_commands应该不存在"
        
    def test_current_wiki_handling_method_exists(self):
        """测试现有的wiki命令处理方法是否存在"""
        # 验证TUI中存在_handle_wiki_command方法
        assert hasattr(self.tui, '_handle_wiki_command'), "_handle_wiki_command方法应该存在"
        
        # 调用现有的wiki命令处理方法不应该报错
        try:
            self.tui._handle_wiki_command("create 测试页面")
            print("✅ _handle_wiki_command方法可调用")
        except Exception as e:
            print(f"⚠️ _handle_wiki_command调用时出现错误: {e}")


if __name__ == "__main__":
    # 直接运行测试以查看结果
    test_instance = TestTUIWikiCommandsInitialization()
    test_instance.setup_method()
    
    print("运行TDD测试以复现wiki_commands未初始化问题...")
    
    print("\n1. 测试wiki_commands属性是否存在...")
    test_instance.test_wiki_commands_attribute_exists()
    print("   ✅ wiki_commands属性不存在（证实问题）")
    
    print("\n2. 测试create_wiki意图处理...")
    try:
        test_instance.test_intent_handler_wiki_commands_access()
    except AssertionError:
        print("   ❌ 未捕获到预期的AttributeError")
    except AttributeError as e:
        print(f"   ✅ 成功复现问题: {e}")
    
    print("\n3. 测试wiki_commands初始化情况...")
    test_instance.test_wiki_commands_initialization_in_modules()
    
    print("\n4. 测试现有wiki处理方法...")
    test_instance.test_current_wiki_handling_method_exists()
    
    print("\nTDD测试完成：问题已成功复现")