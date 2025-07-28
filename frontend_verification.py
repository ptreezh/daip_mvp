#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frontend可用性验证脚本

全面测试frontend目录的可用性，包括：
1. 依赖检查
2. 模块导入测试
3. 服务连接测试
4. 基本功能测试
"""

import sys
import os
import traceback
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'frontend'))

def test_dependencies():
    """测试依赖包是否正确安装"""
    print("🔍 测试依赖包...")
    
    required_packages = [
        'lona',
        'requests', 
        'websockets',
        'pydantic',
        'markdown',
        'pygments'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ 缺失依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r frontend/requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def test_backend_services():
    """测试后端服务是否可用"""
    print("\n🔍 测试后端服务...")
    
    try:
        # 测试主要后端模块
        from src.main import app
        print("  ✅ FastAPI后端应用")
        
        from src.core_services.wiki_service import WikiService
        print("  ✅ WikiService")
        
        from src.core_services.role_manager import RoleManager
        print("  ✅ RoleManager")
        
        from src.core_services.intent_analysis_service import BasicIntentAnalysisService
        print("  ✅ IntentAnalysisService")
        
        print("✅ 后端服务可用")
        return True
        
    except Exception as e:
        print(f"❌ 后端服务导入失败: {e}")
        traceback.print_exc()
        return False

def test_frontend_components():
    """测试前端组件是否可用"""
    print("\n🔍 测试前端组件...")
    
    try:
        # 切换到frontend目录
        os.chdir('frontend')
        
        # 测试主应用
        from main_app import app
        print("  ✅ 主应用 (main_app)")
        
        # 测试组件
        from components.chat_interface import ChatInterface
        print("  ✅ 聊天界面组件")
        
        from components.transparency_monitor import TransparencyMonitor
        print("  ✅ 透明度监控组件")
        
        from components.wiki_panel import WikiPanel
        print("  ✅ Wiki面板组件")
        
        from components.task_panel import TaskPanel
        print("  ✅ 任务面板组件")
        
        # 测试服务
        from services.backend_connector import BackendConnector
        print("  ✅ 后端连接器")
        
        from services.personal_assistant import PersonalAssistantService
        print("  ✅ 个人助手服务")
        
        from services.websocket_manager import websocket_manager
        print("  ✅ WebSocket管理器")
        
        print("✅ 前端组件可用")
        return True
        
    except Exception as e:
        print(f"❌ 前端组件导入失败: {e}")
        traceback.print_exc()
        return False
    finally:
        # 切换回原目录
        os.chdir('..')

def test_component_initialization():
    """测试组件初始化"""
    print("\n🔍 测试组件初始化...")
    
    try:
        os.chdir('frontend')
        
        # 测试后端连接器初始化
        from services.backend_connector import BackendConnector
        backend = BackendConnector()
        print("  ✅ BackendConnector初始化成功")
        
        # 测试个人助手服务初始化
        from services.personal_assistant import PersonalAssistantService
        assistant = PersonalAssistantService(backend)
        print("  ✅ PersonalAssistantService初始化成功")
        
        # 测试聊天界面初始化
        from components.chat_interface import ChatInterface
        chat = ChatInterface(assistant)
        print("  ✅ ChatInterface初始化成功")
        
        # 测试透明度监控初始化
        from components.transparency_monitor import TransparencyMonitor
        monitor = TransparencyMonitor()
        print("  ✅ TransparencyMonitor初始化成功")
        
        print("✅ 组件初始化测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 组件初始化失败: {e}")
        traceback.print_exc()
        return False
    finally:
        os.chdir('..')

def test_lona_app():
    """测试Lona应用是否可以创建"""
    print("\n🔍 测试Lona应用...")
    
    try:
        os.chdir('frontend')
        
        from main_app import app
        
        # 检查应用配置
        print(f"  📍 应用类型: {type(app)}")
        print(f"  📍 路由数量: {len(app.routes) if hasattr(app, 'routes') else 'N/A'}")
        
        print("✅ Lona应用创建成功")
        return True
        
    except Exception as e:
        print(f"❌ Lona应用创建失败: {e}")
        traceback.print_exc()
        return False
    finally:
        os.chdir('..')

def test_static_files():
    """测试静态文件是否存在"""
    print("\n🔍 测试静态文件...")
    
    static_files = [
        'frontend/static/css/main.css',
        'frontend/static/css/components.css'
    ]
    
    all_exist = True
    for file_path in static_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")
            all_exist = False
    
    if all_exist:
        print("✅ 静态文件完整")
    else:
        print("⚠️ 部分静态文件缺失")
    
    return all_exist

def main():
    """主测试函数"""
    print("🎭 Frontend可用性验证")
    print("=" * 60)
    
    tests = [
        ("依赖包检查", test_dependencies),
        ("后端服务检查", test_backend_services),
        ("前端组件检查", test_frontend_components),
        ("组件初始化检查", test_component_initialization),
        ("Lona应用检查", test_lona_app),
        ("静态文件检查", test_static_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 总结报告
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 Frontend完全可用！")
        print("\n🚀 可以启动frontend:")
        print("   cd frontend")
        print("   python run.py")
        print("   访问: http://localhost:8080")
        return True
    else:
        print("⚠️ Frontend存在问题，需要修复")
        print("\n🔧 建议修复步骤:")
        
        for test_name, result in results:
            if not result:
                if "依赖" in test_name:
                    print("   1. 安装缺失的依赖包")
                elif "后端" in test_name:
                    print("   2. 检查后端服务配置")
                elif "前端" in test_name:
                    print("   3. 修复前端组件导入问题")
                elif "初始化" in test_name:
                    print("   4. 修复组件初始化问题")
                elif "Lona" in test_name:
                    print("   5. 修复Lona应用配置")
                elif "静态" in test_name:
                    print("   6. 补充缺失的静态文件")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)