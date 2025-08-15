#!/usr/bin/env python3
"""修复PersonalAssistantService初始化参数的脚本
"""

import re


def fix_personal_assistant_init():
    """修复PersonalAssistantService初始化参数"""
    file_path = "frontend/test_task_3_1_1.py"
    
    # 读取文件内容
    with open(file_path, encoding='utf-8') as f:
        content = f.read()
    
    # 定义要替换的模式
    old_pattern = r'''PersonalAssistantService\(
                intent_analysis_service=backend_connector\.intent_analysis_service,
                role_manager=backend_connector\.role_manager,
                workflow_integrator=backend_connector\.workflow_integrator,
                consensus_selector=backend_connector\.consensus_selector
            \)'''
    
    new_pattern = '''PersonalAssistantService(
                backend_connector=backend_connector
            )'''
    
    # 执行替换
    fixed_content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ PersonalAssistantService初始化参数已修复")

if __name__ == "__main__":
    fix_personal_assistant_init()