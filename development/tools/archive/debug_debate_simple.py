#!/usr/bin/env python3
"""
简单的辩论系统调试脚本
快速定位问题所在
"""
import asyncio
import sys
sys.path.insert(0, 'src')

from daip_live.p8_debate_system.model_availability_checker import perform_model_check
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

async def debug_debate():
    print("=== 辩论系统调试开始 ===")

    try:
        print("1. 测试模型可用性检查...")
        is_model_ok, check_message = await perform_model_check()
        print(f"   模型检查结果: {is_model_ok}")
        print(f"   检查消息: {check_message}")

        print("\n2. 测试角色管理器...")
        role_manager = RoleManager("roles/")
        roles = role_manager.get_all_roles()
        print(f"   可用角色: {list(roles.keys())}")

        print("\n3. 测试角色模型管理器...")
        model_manager = RoleModelManager()
        role_names = ["pro_arguer", "con_arguer"]
        mappings = model_manager.get_debate_model_mappings(role_names)
        print(f"   角色模型映射: {mappings}")

        print("\n=== 调试完成 ===")

    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_debate())