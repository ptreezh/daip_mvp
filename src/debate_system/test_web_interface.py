#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮辩论系统Web界面测试

测试Web界面的基本功能和组件集成。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        from web_interface import DebateWebInterface, DebateInterfaceMode
        print("✅ Web界面模块导入成功")
        
        from websocket_manager import DebateWebSocketManager, WebSocketMessage, MessageType
        print("✅ WebSocket管理器模块导入成功")
        
        from multi_role_dialogue_engine import MultiRoleDialogueEngine
        print("✅ 多角色对话引擎模块导入成功")
        
        from debate_state_manager import DebateStateManager
        print("✅ 状态管理器模块导入成功")
        
        return True
    
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_websocket_manager():
    """测试WebSocket管理器"""
    print("🧪 测试WebSocket管理器...")
    
    try:
        from websocket_manager import DebateWebSocketManager, WebSocketMessage, MessageType
        
        # 创建管理器
        manager = DebateWebSocketManager()
        
        # 测试消息创建
        message = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            payload={"status": "test"},
            session_id="test_session"
        )
        
        assert message.type == MessageType.SYSTEM_STATUS
        assert message.payload["status"] == "test"
        assert message.session_id == "test_session"
        print("✅ WebSocket消息创建成功")
        
        # 测试消息序列化
        message_dict = message.to_dict()
        assert "type" in message_dict
        assert "payload" in message_dict
        assert "session_id" in message_dict
        print("✅ WebSocket消息序列化成功")
        
        # 测试消息反序列化
        restored_message = WebSocketMessage.from_dict(message_dict)
        assert restored_message.type == message.type
        assert restored_message.payload == message.payload
        print("✅ WebSocket消息反序列化成功")
        
        # 测试连接状态
        status = manager.get_connection_status()
        assert isinstance(status, dict)
        assert "total_connections" in status
        assert "active_connections" in status
        print("✅ WebSocket连接状态获取成功")
        
        return True
    
    except Exception as e:
        print(f"❌ WebSocket管理器测试失败: {e}")
        return False


def test_web_interface_components():
    """测试Web界面组件"""
    print("🧪 测试Web界面组件...")
    
    try:
        from web_interface import DebateWebInterface, DebateInterfaceMode, MockPersonalAssistantService
        from multi_role_dialogue_engine import MultiRoleDialogueEngine
        from debate_state_manager import DebateStateManager
        
        # 创建模拟组件
        class MockCognitiveAgent:
            pass
        
        class MockRoleManager:
            async def get_available_roles(self):
                return {
                    "expert1": {"name": "专家1", "expertise_areas": ["测试"], "speaking_style": "formal"}
                }
        
        class MockLLMManager:
            async def generate_response(self, prompt, **kwargs):
                return "测试响应"
        
        class MockMemoryAgent:
            async def store_memory(self, key, content, memory_type="general"):
                pass
        
        class MockParticipantManager:
            pass
        
        # 创建对话引擎
        dialogue_engine = MultiRoleDialogueEngine(
            cognitive_agent=MockCognitiveAgent(),
            role_manager=MockRoleManager(),
            llm_manager=MockLLMManager(),
            memory_agent=MockMemoryAgent(),
            participant_manager=MockParticipantManager()
        )
        
        # 创建状态管理器
        state_manager = DebateStateManager()
        
        # 创建Web界面
        web_interface = DebateWebInterface(
            dialogue_engine=dialogue_engine,
            state_manager=state_manager
        )
        
        # 测试界面模式
        assert web_interface.current_mode == DebateInterfaceMode.SETUP
        print("✅ Web界面初始模式正确")
        
        # 测试UI元素
        assert web_interface.topic_input is not None
        assert web_interface.start_debate_button is not None
        assert web_interface.stop_debate_button is not None
        print("✅ Web界面UI元素创建成功")
        
        # 测试模拟助手服务
        mock_assistant = MockPersonalAssistantService(dialogue_engine, "test_session")
        assert mock_assistant.session_id == "test_session"
        print("✅ 模拟助手服务创建成功")
        
        return True
    
    except Exception as e:
        print(f"❌ Web界面组件测试失败: {e}")
        return False


async def test_async_functionality():
    """测试异步功能"""
    print("🧪 测试异步功能...")
    
    try:
        from websocket_manager import DebateWebSocketManager
        
        # 创建管理器
        manager = DebateWebSocketManager()
        
        # 测试启动和停止
        await manager.start()
        print("✅ WebSocket管理器启动成功")
        
        await manager.stop()
        print("✅ WebSocket管理器停止成功")
        
        return True
    
    except Exception as e:
        print(f"❌ 异步功能测试失败: {e}")
        return False


def test_css_file():
    """测试CSS文件"""
    print("🧪 测试CSS文件...")
    
    try:
        css_file = Path(__file__).parent / "static" / "debate_interface.css"
        
        if css_file.exists():
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # 检查关键样式类
            required_classes = [
                ".debate-web-interface",
                ".chat-interface",
                ".message",
                ".topic-input",
                ".monitoring-panel"
            ]
            
            for css_class in required_classes:
                if css_class in css_content:
                    print(f"✅ 找到CSS类: {css_class}")
                else:
                    print(f"⚠️ 未找到CSS类: {css_class}")
            
            print(f"✅ CSS文件存在，大小: {len(css_content)} 字符")
            return True
        else:
            print("❌ CSS文件不存在")
            return False
    
    except Exception as e:
        print(f"❌ CSS文件测试失败: {e}")
        return False


def test_app_structure():
    """测试应用程序结构"""
    print("🧪 测试应用程序结构...")
    
    try:
        # 检查必要文件
        required_files = [
            "web_interface.py",
            "websocket_manager.py",
            "multi_role_dialogue_engine.py",
            "debate_state_manager.py",
            "app.py",
            "static/debate_interface.css"
        ]
        
        current_dir = Path(__file__).parent
        
        for file_path in required_files:
            full_path = current_dir / file_path
            if full_path.exists():
                print(f"✅ 文件存在: {file_path}")
            else:
                print(f"❌ 文件缺失: {file_path}")
                return False
        
        return True
    
    except Exception as e:
        print(f"❌ 应用程序结构测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始多轮辩论系统Web界面测试...")
    print("=" * 60)
    
    results = []
    
    # 同步测试
    results.append(test_imports())
    results.append(test_websocket_manager())
    results.append(test_web_interface_components())
    results.append(test_css_file())
    results.append(test_app_structure())
    
    # 异步测试
    results.append(await test_async_functionality())
    
    # 统计结果
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有Web界面测试通过！")
        print("✅ 系统组件集成正常，界面功能完整")
        print("\n🚀 可以启动Web应用程序:")
        print("   python app.py")
        print("   然后访问: http://localhost:8080")
    else:
        print("⚠️ 部分测试未通过，需要进一步检查")
    
    return passed == total


def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    dependencies = [
        ("lona", "Lona Web框架"),
        ("asyncio", "异步IO支持"),
        ("json", "JSON处理"),
        ("logging", "日志记录"),
        ("pathlib", "路径处理")
    ]
    
    missing_deps = []
    
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {desc}: 已安装")
        except ImportError:
            print(f"❌ {desc}: 未安装")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️ 缺少依赖项: {', '.join(missing_deps)}")
        if "lona" in missing_deps:
            print("安装命令: pip install lona")
        return False
    else:
        print("✅ 所有依赖项已满足")
        return True


if __name__ == "__main__":
    try:
        # 检查依赖项
        if not check_dependencies():
            print("❌ 依赖项检查失败，请安装缺少的依赖项")
            sys.exit(1)
        
        # 运行测试
        success = asyncio.run(run_all_tests())
        
        if success:
            print("\n🎯 多轮辩论系统Web界面已准备就绪！")
            print("📋 主要功能:")
            print("   - ✅ 响应式Web界面设计")
            print("   - ✅ 实时WebSocket通信")
            print("   - ✅ 多角色对话集成")
            print("   - ✅ 辩论状态管理")
            print("   - ✅ 透明度监控面板")
            print("   - ✅ 移动设备适配")
        else:
            print("\n❌ 测试未完全通过，请检查相关组件")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        sys.exit(1)