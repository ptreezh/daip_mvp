"""
端到端测试交互式AI角色创建功能
"""

import asyncio
import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.interactive_role_creation import (
    InteractiveRoleCreationService,
    AIRoleGenerator,
    RoleManagerAdapter
)
from daip_live.p4_role_manager_tools.role_manager import RoleManager


class MockLLMProvider:
    """模拟LLM提供者用于测试"""
    
    def generate(self, prompt):
        if "数据科学家" in prompt or "数据分析师" in prompt:
            return '''
            {
                "name": "数据分析专家",
                "persona": "专业的数据分析师，擅长数据处理、统计分析和可视化",
                "tools": ["pandas", "numpy", "matplotlib"]
            }
            '''
        else:
            return '''
            {
                "name": "自定义助手",
                "persona": "多用途AI助手，可根据需求调整功能",
                "tools": ["搜索", "计算", "分析"]
            }
            '''


def test_end_to_end_role_creation():
    """端到端测试角色创建流程"""
    print("开始端到端角色创建测试...")
    
    # 创建依赖项
    role_manager = RoleManager()
    llm_provider = MockLLMProvider()
    
    # 创建服务
    service = InteractiveRoleCreationService(role_manager, llm_provider)
    
    # 测试1：创建数据科学家角色
    print("测试1: 创建数据科学家角色")
    response = service.start_creation("创建一个数据分析专家角色，擅长数据可视化和统计分析")
    
    if response.status == 'success':
        print(f"  ✅ 角色创建建议成功: {response.suggested_role['name']}")
        print(f"  人设: {response.suggested_role['persona'][:50]}...")
        print(f"  工具: {response.suggested_role['tools']}")
        
        # 测试2：确认角色创建
        print("\n测试2: 确认角色创建")
        confirm_response = service.continue_creation(response.session_id, {"confirm": True})
        
        if confirm_response.status == 'success':
            print(f"  ✅ 角色已成功保存: {confirm_response.message}")
        else:
            print(f"  ❌ 角色保存失败: {confirm_response.message}")
    else:
        print(f"  ❌ 角色创建失败: {response.message}")
    
    # 测试3：创建其他类型角色
    print("\n测试3: 创建法律咨询助手角色")
    response2 = service.start_creation("创建一个法律咨询助手，擅长合同审查")
    
    if response2.status == 'success':
        print(f"  ✅ 角色创建建议成功: {response2.suggested_role['name']}")
        
        # 测试4：自定义角色配置
        print("\n测试4: 自定义角色配置")
        custom_role = {
            "name": "高级法律顾问",
            "persona": "资深法律专家，专精企业合同审查与风险评估",
            "tools": ["合同分析", "法规数据库", "风险评估"]
        }
        
        modify_response = service.continue_creation(response2.session_id, {"updated_role": custom_role})
        
        if modify_response.status == 'success':
            print(f"  ✅ 角色配置已更新: {modify_response.suggested_role['name']}")
            
            # 确认自定义角色
            final_confirm = service.continue_creation(response2.session_id, {"confirm": True})
            if final_confirm.status == 'success':
                print(f"  ✅ 自定义角色已保存: {final_confirm.message}")
            else:
                print(f"  ❌ 自定义角色保存失败: {final_confirm.message}")
        else:
            print(f"  ❌ 角色配置更新失败: {modify_response.message}")
    else:
        print(f"  ❌ 角色创建失败: {response2.message}")
    
    print("\n端到端测试完成！")


if __name__ == "__main__":
    test_end_to_end_role_creation()