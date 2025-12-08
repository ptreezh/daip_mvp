"""
交互式AI角色创建功能演示
"""

import asyncio
from unittest.mock import Mock
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.interactive_role_creation import InteractiveRoleCreationService


class DemoLLMProvider:
    """演示用LLM提供者"""
    
    def generate(self, prompt):
        # 根据提示返回不同的角色配置
        if "数据科学家" in prompt or "数据分析师" in prompt or "数据" in prompt:
            return '''
            {
                "name": "数据分析专家",
                "persona": "专业的数据分析师，擅长数据处理、统计分析和可视化，具有丰富的Python和R编程经验",
                "tools": ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn"]
            }
            '''
        elif "法律顾问" in prompt or "法律" in prompt:
            return '''
            {
                "name": "企业法律顾问",
                "persona": "资深法律专家，专精企业合规、合同审查和知识产权保护",
                "tools": ["法规数据库", "合同分析工具", "风险评估系统"]
            }
            '''
        elif "编程导师" in prompt or "编程" in prompt:
            return '''
            {
                "name": "Python编程导师",
                "persona": "经验丰富的Python开发工程师，擅长Web开发、数据科学和自动化脚本编写",
                "tools": ["代码编辑器", "调试工具", "文档查询", "示例代码库"]
            }
            '''
        else:
            return '''
            {
                "name": "多领域专家",
                "persona": "跨领域AI助手，可以根据具体需求调整专业能力和工具配置",
                "tools": ["搜索", "计算", "分析", "推理"]
            }
            '''


def demo_interactive_role_creation():
    """演示交互式AI角色创建"""
    print("=" * 60)
    print("🎭 DAIP-LIVE 交互式AI角色创建功能演示")
    print("=" * 60)
    
    # 创建模拟依赖
    mock_role_manager = Mock()
    mock_role_manager.list_roles.return_value = []
    mock_role_manager.get_role_by_name.return_value = None
    mock_role_manager._load_roles_from_directory = Mock()
    
    # 创建演示用的LLM提供者
    llm_provider = DemoLLMProvider()
    
    # 创建服务
    service = InteractiveRoleCreationService(mock_role_manager, llm_provider)
    
    print("\n🚀 欢迎使用交互式AI角色创建向导！")
    print("您可以描述需要的角色类型，AI将为您生成专业配置。")
    print("\n示例描述：")
    print("  - '数据科学家' - 创建数据分析专家")
    print("  - '法律顾问' - 创建法律咨询助手") 
    print("  - '编程导师' - 创建编程教学助手")
    print("  - 或者自定义描述，如'项目管理专家'")
    
    # 示例1: 数据科学家
    print(f"\n{'-'*20} 示例1: 数据科学家 {'-'*20}")
    print("用户输入: 创建一个数据科学家角色，擅长机器学习")
    
    response = service.start_creation("创建一个数据科学家角色，擅长机器学习")
    if response.status == 'success':
        print(f"AI建议角色: {response.suggested_role['name']}")
        print(f"人设描述: {response.suggested_role['persona']}")
        print(f"推荐工具: {', '.join(response.suggested_role['tools'])}")
        
        print("\n确认创建...")
        confirm_response = service.continue_creation(response.session_id, {"confirm": True})
        print(f"结果: {confirm_response.message}")
    
    # 示例2: 法律顾问
    print(f"\n{'-'*20} 示例2: 法律顾问 {'-'*20}")
    print("用户输入: 企业法律顾问，专精合同审查")
    
    response = service.start_creation("企业法律顾问，专精合同审查")
    if response.status == 'success':
        print(f"AI建议角色: {response.suggested_role['name']}")
        print(f"人设描述: {response.suggested_role['persona']}")
        print(f"推荐工具: {', '.join(response.suggested_role['tools'])}")
        
        print("\n修改配置...")
        custom_role = {
            "name": "高级企业法律顾问",
            "persona": "资深法律专家，专精企业合规、合同审查和知识产权保护，具备丰富的商业法律实务经验",
            "tools": ["法规数据库", "合同分析工具", "风险评估系统", "案例检索"]
        }
        
        modify_response = service.continue_creation(response.session_id, {"updated_role": custom_role})
        if modify_response.status == 'success':
            print(f"更新后角色: {modify_response.suggested_role['name']}")
            print(f"更新后人设: {modify_response.suggested_role['persona']}")
            
            print("\n确认创建...")
            confirm_response = service.continue_creation(response.session_id, {"confirm": True})
            print(f"结果: {confirm_response.message}")
    
    # 示例3: 编程导师
    print(f"\n{'-'*20} 示例3: 编程导师 {'-'*20}")
    print("用户输入: Python编程导师，擅长Web开发教学")
    
    response = service.start_creation("Python编程导师，擅长Web开发教学")
    if response.status == 'success':
        print(f"AI建议角色: {response.suggested_role['name']}")
        print(f"人设描述: {response.suggested_role['persona']}")
        print(f"推荐工具: {', '.join(response.suggested_role['tools'])}")
        
        print("\n确认创建...")
        confirm_response = service.continue_creation(response.session_id, {"confirm": True})
        print(f"结果: {confirm_response.message}")
    
    print(f"\n{'='*60}")
    print("✅ 演示完成！交互式AI角色创建功能已成功验证。")
    print("📋 该功能可以：")
    print("   - 根据自然语言描述生成专业角色配置")
    print("   - 提供工具推荐和人设建议")
    print("   - 支持角色配置的自定义修改")
    print("   - 集成到TUI命令系统中")
    print("=" * 60)


if __name__ == "__main__":
    demo_interactive_role_creation()