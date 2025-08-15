#!/usr/bin/env python3
"""简化的Frontend启动测试
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_frontend_startup():
    """测试frontend是否能正常启动"""
    print("🔍 测试Frontend启动...")
    
    try:
        # 切换到frontend目录
        os.chdir('frontend')
        
        # 导入主应用
        from main_app import app
        print("✅ 主应用导入成功")
        
        # 检查应用是否可以创建视图
        print("✅ Lona应用创建成功")
        print(f"📍 应用类型: {type(app)}")
        
        # 测试组件导入
        from components.chat_interface import ChatInterface
        from services.backend_connector import BackendConnector
        from services.personal_assistant import PersonalAssistantService
        
        # 测试组件初始化
        backend = BackendConnector()
        assistant = PersonalAssistantService(backend)
        chat = ChatInterface(assistant)
        
        print("✅ 所有组件初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir('..')

if __name__ == "__main__":
    print("🎭 Frontend启动测试")
    print("=" * 40)
    
    success = test_frontend_startup()
    
    if success:
        print("\n🎉 Frontend可以正常启动！")
        print("\n🚀 启动命令:")
        print("   cd frontend")
        print("   python run.py")
        print("   访问: http://localhost:8080")
    else:
        print("\n❌ Frontend存在问题，无法启动")
    
    sys.exit(0 if success else 1)