"""
端到端测试交互式AI角色创建功能
"""

import os
import sys

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.tui.interactive_role_creation import (
    InteractiveRoleCreationService,
)


class MockLLMProvider:
    """模拟LLM提供者用于测试"""

    def generate(self, prompt):
        if "数据科学家" in prompt or "数据分析师" in prompt:
            return """
            {
                "name": "数据分析专家",
                "persona": "专业的数据分析师，擅长数据处理、统计分析和可视化",
                "tools": ["pandas", "numpy", "matplotlib"]
            }
            """
        else:
            return """
            {
                "name": "自定义助手",
                "persona": "多用途AI助手，可根据需求调整功能",
                "tools": ["搜索", "计算", "分析"]
            }
            """


def test_end_to_end_role_creation():
    """端到端测试角色创建流程"""

    # 创建依赖项
    role_manager = RoleManager()
    llm_provider = MockLLMProvider()

    # 创建服务
    service = InteractiveRoleCreationService(role_manager, llm_provider)

    # 测试1：创建数据科学家角色
    response = service.start_creation(
        "创建一个数据分析专家角色，擅长数据可视化和统计分析"
    )

    if response.status == "success":
        # 测试2：确认角色创建
        confirm_response = service.continue_creation(
            response.session_id, {"confirm": True}
        )

        if confirm_response.status == "success":
            pass
        else:
            pass
    else:
        pass

    # 测试3：创建其他类型角色
    response2 = service.start_creation("创建一个法律咨询助手，擅长合同审查")

    if response2.status == "success":
        # 测试4：自定义角色配置
        custom_role = {
            "name": "高级法律顾问",
            "persona": "资深法律专家，专精企业合同审查与风险评估",
            "tools": ["合同分析", "法规数据库", "风险评估"],
        }

        modify_response = service.continue_creation(
            response2.session_id, {"updated_role": custom_role}
        )

        if modify_response.status == "success":
            # 确认自定义角色
            final_confirm = service.continue_creation(
                response2.session_id, {"confirm": True}
            )
            if final_confirm.status == "success":
                pass
            else:
                pass
        else:
            pass
    else:
        pass


if __name__ == "__main__":
    test_end_to_end_role_creation()
