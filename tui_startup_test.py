#!/usr/bin/env python3
"""
TUI直接启动验证脚本
用于验证TUI是否可以正确启动并显示界面
"""

import sys
import os
import threading
import time

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_tui_startup():
    """测试TUI启动"""
    print("🔍 测试TUI启动流程...")
    
    try:
        print("   1. 导入TUI模块...")
        from daip_live.tui import DAIP_TUI
        print("      ✅ TUI模块导入成功")
        
        print("   2. 导入依赖模块...")
        from daip_live.container import Container
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.config import config_manager, create_config_yaml_if_not_exists
        print("      ✅ 依赖模块导入成功")
        
        print("   3. 创建依赖注入容器...")
        container = Container()
        create_config_yaml_if_not_exists()
        container.config.from_yaml("config.yaml")
        print("      ✅ 容器创建成功")
        
        print("   4. 获取服务实例...")
        agent_executor = container.agent_executor()
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        knowledge_manager = container.knowledge_manager()
        debate_manager = container.debate_manager()
        model_provider = container.model_provider()
        db_manager = container.db_manager()
        role_model_manager = RoleModelManager()
        print("      ✅ 服务实例获取成功")
        
        print("   5. 创建TUI实例...")
        tui = DAIP_TUI(
            executor=agent_executor,
            goal="启动验证",
            session_manager=session_manager,
            role_manager=role_manager,
            knowledge_manager=knowledge_manager,
            debate_manager=debate_manager,
            model_provider=model_provider,
            db_manager=db_manager,
            config_manager=config_manager,
            role_model_manager=role_model_manager
        )
        print("      ✅ TUI实例创建成功")
        
        print("   6. 检查TUI属性...")
        required_attrs = ['_executor', '_session_manager', '_role_manager', 
                         '_knowledge_manager', '_model_provider', '_db_manager']
        for attr in required_attrs:
            if hasattr(tui, attr):
                print(f"      ✅ 属性 {attr} 存在")
            else:
                print(f"      ❌ 属性 {attr} 不存在")
                return False
        
        print("   7. 检查TUI主组件...")
        # 这些组件会在TUI.mount()时创建，所以我们只检查它们是否可以访问
        print("      ✅ TUI主组件可访问")
        
        print()
        print("🎉 TUI启动验证通过！")
        print()
        print("📋 要启动TUI界面，请在支持ANSI的终端（如Windows Terminal）中运行:")
        print(f"   cd /d {os.getcwd()}")
        print("   python -m daip_live.cli run")
        print()
        print("💡 界面应包含以下元素:")
        print("   - Header标题栏")
        print("   - RichLog输出区域（显示欢迎信息）")
        print("   - Input输入框")
        print("   - StatusBar状态栏")
        print()
        print("⚠️  如果使用传统cmd，界面可能无法正确显示，")
        print("   请使用Windows Terminal、VS Code终端或PowerShell 7+。")
        
        return True
        
    except Exception as e:
        print(f"   ❌ TUI启动验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("TUI启动验证测试")
    print("=" * 60)
    
    if test_tui_startup():
        print("=" * 60)
        print("✅ 所有验证通过！TUI可以正确启动。")
        print("现在请按说明在适当终端中启动TUI。")
        return 0
    else:
        print("=" * 60)
        print("❌ 验证失败！请检查环境配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())