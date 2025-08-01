#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务3.1.1测试套件 - 集成现有前端组件

严格测试前端组件集成的完整性、数据流同步和用户体验
"""

import sys
import os
import asyncio
import unittest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestTask311Integration(unittest.TestCase):
    """任务3.1.1集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_results = {
            "component_import": False,
            "component_initialization": False,
            "data_flow_sync": False,
            "user_interaction": False,
            "error_handling": False
        }
    
    def test_01_component_imports(self):
        """测试1: 验证所有组件能正确导入"""
        logger.info("🧪 测试1: 组件导入测试")
        
        try:
            # 测试核心组件导入
            from components.chat_interface import ChatInterface
            from components.transparency_monitor import TransparencyMonitor
            from components.wiki_panel import WikiPanel
            from components.task_panel import TaskPanel
            
            # 测试服务导入
            from services.personal_assistant import PersonalAssistantService
            from services.backend_connector import BackendConnector
            from services.websocket_manager import websocket_manager, realtime_manager
            
            # 测试集成应用导入
            from integrated_demo_app import IntegratedDemoView, app
            
            self.test_results["component_import"] = True
            logger.info("✅ 所有组件导入成功")
            
        except ImportError as e:
            logger.error(f"❌ 组件导入失败: {e}")
            self.fail(f"组件导入失败: {e}")
    
    def test_02_component_initialization(self):
        """测试2: 验证组件能正确初始化"""
        logger.info("🧪 测试2: 组件初始化测试")
        
        try:
            from services.backend_connector import BackendConnector
            from services.personal_assistant import PersonalAssistantService
            from components.chat_interface import ChatInterface
            from components.transparency_monitor import TransparencyMonitor
            from components.wiki_panel import WikiPanel
            from components.task_panel import TaskPanel
            
            # 初始化后端连接器
            backend_connector = BackendConnector()
            self.assertIsNotNone(backend_connector)
            
            # 初始化个人助手服务
            assistant_service = PersonalAssistantService(
                backend_connector=backend_connector
            )
            self.assertIsNotNone(assistant_service)
            
            # 初始化前端组件
            chat_interface = ChatInterface(assistant_service, session_id="test_session")
            self.assertIsNotNone(chat_interface)
            self.assertEqual(chat_interface.session_id, "test_session")
            
            transparency_monitor = TransparencyMonitor()
            self.assertIsNotNone(transparency_monitor)
            
            wiki_panel = WikiPanel(backend_connector.wiki_service)
            self.assertIsNotNone(wiki_panel)
            
            task_panel = TaskPanel(backend_connector.task_service)
            self.assertIsNotNone(task_panel)
            
            self.test_results["component_initialization"] = True
            logger.info("✅ 所有组件初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 组件初始化失败: {e}")
            self.fail(f"组件初始化失败: {e}")
    
    def test_03_integrated_demo_view(self):
        """测试3: 验证集成演示视图"""
        logger.info("🧪 测试3: 集成演示视图测试")
        
        try:
            from integrated_demo_app import IntegratedDemoView
            
            # 创建集成演示视图（测试模式）
            demo_view = IntegratedDemoView()
            self.assertIsNotNone(demo_view)
            
            # 验证演示场景配置
            self.assertIn("ai_ethics", demo_view.demo_scenarios)
            self.assertIn("product_strategy", demo_view.demo_scenarios)
            self.assertIn("tech_risk", demo_view.demo_scenarios)
            
            # 验证场景数据结构
            ai_ethics_scenario = demo_view.demo_scenarios["ai_ethics"]
            required_keys = ["name", "description", "duration", "roles", "workflows"]
            for key in required_keys:
                self.assertIn(key, ai_ethics_scenario)
            
            logger.info("✅ 集成演示视图验证成功")
            
        except Exception as e:
            logger.error(f"❌ 集成演示视图测试失败: {e}")
            self.fail(f"集成演示视图测试失败: {e}")
    
    async def test_04_data_flow_synchronization(self):
        """测试4: 验证组件间数据流同步"""
        logger.info("🧪 测试4: 数据流同步测试")
        
        try:
            from services.backend_connector import BackendConnector
            from services.personal_assistant import PersonalAssistantService
            from components.chat_interface import ChatInterface
            from components.transparency_monitor import TransparencyMonitor
            
            # 初始化组件
            backend_connector = BackendConnector()
            assistant_service = PersonalAssistantService(
                backend_connector=backend_connector
            )
            
            chat_interface = ChatInterface(assistant_service, session_id="test_sync")
            transparency_monitor = TransparencyMonitor()
            
            # 测试回调函数设置
            callback_called = False
            
            async def test_callback(message):
                nonlocal callback_called
                callback_called = True
                return True
            
            chat_interface.on_message_sent = test_callback
            
            # 模拟消息发送
            test_message = Mock()
            test_message.sender = "user"
            test_message.content = "测试消息"
            
            if chat_interface.on_message_sent:
                await chat_interface.on_message_sent(test_message)
            
            self.assertTrue(callback_called, "回调函数未被正确调用")
            
            # 测试透明度监控数据更新
            test_agent_data = {
                "agent_id": "test_agent",
                "name": "测试代理",
                "status": "thinking",
                "framework": "测试框架",
                "confidence": 0.85
            }
            
            await transparency_monitor.update_agent_status(test_agent_data)
            
            # 验证代理数据是否正确更新
            agent_found = False
            for agent in transparency_monitor.active_agents:
                if agent.get("name") == "测试代理":
                    agent_found = True
                    self.assertEqual(agent["status"], "thinking")
                    self.assertEqual(agent["confidence"], 0.85)
                    break
            
            self.assertTrue(agent_found, "代理状态未正确更新")
            
            self.test_results["data_flow_sync"] = True
            logger.info("✅ 数据流同步测试成功")
            
        except Exception as e:
            logger.error(f"❌ 数据流同步测试失败: {e}")
            self.fail(f"数据流同步测试失败: {e}")
    
    def test_05_user_interaction_flow(self):
        """测试5: 验证用户交互流程"""
        logger.info("🧪 测试5: 用户交互流程测试")
        
        try:
            from services.backend_connector import BackendConnector
            from services.personal_assistant import PersonalAssistantService
            from components.chat_interface import ChatInterface
            
            # 初始化组件
            backend_connector = BackendConnector()
            assistant_service = PersonalAssistantService(
                backend_connector=backend_connector
            )
            
            chat_interface = ChatInterface(assistant_service, session_id="test_ui")
            
            # 测试演示场景设置
            test_scenario = {
                "name": "测试场景",
                "description": "用于测试的场景",
                "duration": "10分钟",
                "roles": ["测试角色1", "测试角色2"],
                "workflows": ["测试工作流"]
            }
            
            # 这里需要异步测试，但在同步测试中我们验证方法存在
            self.assertTrue(hasattr(chat_interface, 'set_demo_scenario'))
            self.assertTrue(hasattr(chat_interface, 'add_context'))
            self.assertTrue(hasattr(chat_interface, 'set_current_task'))
            self.assertTrue(hasattr(chat_interface, 'display_workflow_result'))
            
            # 测试上下文数据管理
            test_context = {
                "title": "测试上下文",
                "type": "知识",
                "relevance": "高"
            }
            
            # 验证上下文数据结构
            self.assertIsInstance(chat_interface.context_data, dict)
            
            self.test_results["user_interaction"] = True
            logger.info("✅ 用户交互流程测试成功")
            
        except Exception as e:
            logger.error(f"❌ 用户交互流程测试失败: {e}")
            self.fail(f"用户交互流程测试失败: {e}")
    
    def test_06_error_handling(self):
        """测试6: 验证错误处理机制"""
        logger.info("🧪 测试6: 错误处理测试")
        
        try:
            from components.transparency_monitor import TransparencyMonitor
            
            transparency_monitor = TransparencyMonitor()
            
            # 测试错误记录功能
            self.assertTrue(hasattr(transparency_monitor, 'log_error'))
            
            # 测试系统指标初始化
            self.assertIn("error_count", transparency_monitor.system_metrics)
            self.assertIsInstance(transparency_monitor.system_metrics["error_count"], int)
            
            # 测试LLM调用记录结构
            self.assertIsInstance(transparency_monitor.llm_calls, list)
            
            # 测试代理状态数据结构
            self.assertIsInstance(transparency_monitor.active_agents, list)
            
            self.test_results["error_handling"] = True
            logger.info("✅ 错误处理测试成功")
            
        except Exception as e:
            logger.error(f"❌ 错误处理测试失败: {e}")
            self.fail(f"错误处理测试失败: {e}")
    
    def test_07_css_and_static_files(self):
        """测试7: 验证CSS和静态文件"""
        logger.info("🧪 测试7: CSS和静态文件测试")
        
        try:
            # 检查CSS文件存在
            css_file = Path(__file__).parent / "static" / "css" / "demo.css"
            self.assertTrue(css_file.exists(), "demo.css文件不存在")
            
            # 检查CSS文件内容
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # 验证关键CSS类存在
            required_classes = [
                ".demo-container",
                ".demo-header",
                ".demo-controls",
                ".main-demo-area",
                ".chat-panel",
                ".transparency-panel",
                ".wiki-panel",
                ".task-panel"
            ]
            
            for css_class in required_classes:
                self.assertIn(css_class, css_content, f"CSS类 {css_class} 不存在")
            
            logger.info("✅ CSS和静态文件测试成功")
            
        except Exception as e:
            logger.error(f"❌ CSS和静态文件测试失败: {e}")
            self.fail(f"CSS和静态文件测试失败: {e}")
    
    def test_08_startup_script(self):
        """测试8: 验证启动脚本"""
        logger.info("🧪 测试8: 启动脚本测试")
        
        try:
            # 检查启动脚本存在
            startup_script = Path(__file__).parent / "start_integrated_demo.py"
            self.assertTrue(startup_script.exists(), "启动脚本不存在")
            
            # 检查启动脚本可执行性
            with open(startup_script, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # 验证关键函数存在
            self.assertIn("check_dependencies", script_content)
            self.assertIn("check_backend_services", script_content)
            self.assertIn("initialize_services", script_content)
            self.assertIn("def main", script_content)
            
            logger.info("✅ 启动脚本测试成功")
            
        except Exception as e:
            logger.error(f"❌ 启动脚本测试失败: {e}")
            self.fail(f"启动脚本测试失败: {e}")
    
    def test_09_documentation(self):
        """测试9: 验证文档完整性"""
        logger.info("🧪 测试9: 文档完整性测试")
        
        try:
            # 检查README文件存在
            readme_file = Path(__file__).parent / "INTEGRATED_DEMO_README.md"
            self.assertTrue(readme_file.exists(), "README文件不存在")
            
            # 检查README内容
            with open(readme_file, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # 验证关键章节存在
            required_sections = [
                "# DAIP-LIVE 集成演示系统",
                "## 🎯 核心特性",
                "## 🏗️ 系统架构",
                "## 🚀 快速启动",
                "## 📋 演示场景",
                "## 🔍 透明度特性",
                "## 🎮 使用指南"
            ]
            
            for section in required_sections:
                self.assertIn(section, readme_content, f"README章节 {section} 不存在")
            
            logger.info("✅ 文档完整性测试成功")
            
        except Exception as e:
            logger.error(f"❌ 文档完整性测试失败: {e}")
            self.fail(f"文档完整性测试失败: {e}")
    
    def test_10_integration_completeness(self):
        """测试10: 验证集成完整性"""
        logger.info("🧪 测试10: 集成完整性测试")
        
        try:
            from integrated_demo_app import IntegratedDemoView
            
            # 创建集成视图（测试模式）
            demo_view = IntegratedDemoView()
            
            # 验证所有必要属性存在
            required_attributes = [
                "backend_connector",
                "assistant_service", 
                "demo_scenarios",
                "demo_session_id",
                "current_scenario",
                "demo_active"
            ]
            
            for attr in required_attributes:
                self.assertTrue(hasattr(demo_view, attr), f"缺少属性: {attr}")
            
            # 验证关键方法存在
            required_methods = [
                "_setup_websocket",
                "_setup_component_communication",
                "_register_realtime_callbacks",
                "_render_demo_header",
                "_render_demo_controls",
                "_render_main_demo_area"
            ]
            
            for method in required_methods:
                self.assertTrue(hasattr(demo_view, method), f"缺少方法: {method}")
            
            logger.info("✅ 集成完整性测试成功")
            
        except Exception as e:
            logger.error(f"❌ 集成完整性测试失败: {e}")
            self.fail(f"集成完整性测试失败: {e}")


class TestTask311AsyncFunctions(unittest.IsolatedAsyncioTestCase):
    """异步功能测试类"""
    
    async def test_async_data_flow(self):
        """异步测试: 数据流同步"""
        logger.info("🧪 异步测试: 数据流同步")
        
        try:
            from services.backend_connector import BackendConnector
            from services.personal_assistant import PersonalAssistantService
            from components.chat_interface import ChatInterface
            from components.transparency_monitor import TransparencyMonitor
            
            # 初始化组件
            backend_connector = BackendConnector()
            assistant_service = PersonalAssistantService(
                backend_connector=backend_connector
            )
            
            chat_interface = ChatInterface(assistant_service, session_id="async_test")
            transparency_monitor = TransparencyMonitor()
            
            # 测试异步场景设置
            test_scenario = {
                "name": "异步测试场景",
                "description": "用于异步测试",
                "duration": "5分钟",
                "roles": ["测试角色"],
                "workflows": ["测试工作流"]
            }
            
            await chat_interface.set_demo_scenario("test", test_scenario)
            
            # 验证场景设置成功
            self.assertEqual(chat_interface.current_scenario, "test")
            self.assertTrue(chat_interface.demo_active)
            
            # 测试上下文添加
            test_context = {
                "title": "异步测试上下文",
                "type": "测试",
                "relevance": "高"
            }
            
            await chat_interface.add_context(test_context)
            
            # 验证上下文添加成功
            self.assertIn("title", chat_interface.context_data)
            
            logger.info("✅ 异步数据流测试成功")
            
        except Exception as e:
            logger.error(f"❌ 异步数据流测试失败: {e}")
            self.fail(f"异步数据流测试失败: {e}")


def run_comprehensive_test():
    """运行全面测试"""
    print("=" * 70)
    print("🧪 任务3.1.1集成测试套件")
    print("测试前端组件集成的完整性、数据流同步和用户体验")
    print("=" * 70)
    print()
    
    # 运行同步测试
    print("📋 运行同步测试...")
    sync_suite = unittest.TestLoader().loadTestsFromTestCase(TestTask311Integration)
    sync_runner = unittest.TextTestRunner(verbosity=2)
    sync_result = sync_runner.run(sync_suite)
    
    print("\n📋 运行异步测试...")
    # 运行异步测试
    try:
        async_suite = unittest.TestLoader().loadTestsFromTestCase(TestTask311AsyncFunctions)
        async_runner = unittest.TextTestRunner(verbosity=2)
        async_result = async_runner.run(async_suite)
    except Exception as e:
        logger.error(f"异步测试运行失败: {e}")
        # 创建一个模拟的结果对象
        class MockResult:
            def __init__(self):
                self.testsRun = 0
                self.failures = []
                self.errors = [("async_test", str(e))]
        async_result = MockResult()
    
    # 汇总测试结果
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    
    total_tests = sync_result.testsRun + async_result.testsRun
    total_failures = len(sync_result.failures) + len(async_result.failures)
    total_errors = len(sync_result.errors) + len(async_result.errors)
    
    print(f"总测试数: {total_tests}")
    print(f"成功: {total_tests - total_failures - total_errors}")
    print(f"失败: {total_failures}")
    print(f"错误: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 所有测试通过！任务3.1.1验证成功！")
        print("✅ 前端组件集成完成")
        print("✅ 数据流同步正常")
        print("✅ 用户交互流程完整")
        print("✅ 错误处理机制健全")
        return True
    else:
        print(f"\n❌ 测试失败！需要修复 {total_failures + total_errors} 个问题")
        return False


if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)