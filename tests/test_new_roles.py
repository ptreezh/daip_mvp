#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新添加的角色是否能被正确加载
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core_services.role_manager import RoleManager

def test_new_roles():
    """测试新角色加载"""
    print("测试新角色加载...")
    
    # 创建RoleManager实例
    role_manager = RoleManager()
    
    # 获取所有角色
    roles = role_manager.list_roles()
    
    print(f"总共加载了 {len(roles)} 个角色")
    
    # 检查新添加的角色是否存在
    new_roles = [
        "bioinformatics_researcher",
        "genomics_data_analyst",
        "computational_biology_methodologist",
        "environmental_policy_analyst",
        "natural_resources_economist",
        "climate_change_economic_modeler",
        "cognitive_neuroscientist",
        "computational_neuroscientist",
        "clinical_neuroscientist",
        "nanomaterials_engineer",
        "energy_materials_researcher",
        "biomaterials_scientist",
        "quantitative_analyst",
        "algorithmic_trading_engineer",
        "financial_risk_manager",
        "cognitive_modeling_expert",
        "ai_ethicist",
        "language_cognition_researcher",
        "smart_city_planner",
        "transportation_systems_analyst",
        "community_development_expert",
        "cybersecurity_architect",
        "penetration_tester",
        "security_operations_analyst",
        "medical_device_design_engineer",
        "biosignal_processing_expert",
        "tissue_engineering_researcher",
        "learning_experience_designer",
        "educational_data_scientist",
        "online_learning_platform_architect"
    ]
    
    print("\n检查新角色是否加载成功:")
    loaded_count = 0
    for role_id in new_roles:
        role = role_manager.get_role(role_id)
        if role:
            print(f"  [OK] {role_id} - {role.name}")
            loaded_count += 1
        else:
            print(f"  [FAIL] {role_id} - 未找到")
    
    print(f"\n成功加载 {loaded_count}/{len(new_roles)} 个新角色")
    
    # 检查是否有重复的角色ID
    role_ids = [role.id for role in roles]
    duplicates = [role_id for role_id in set(role_ids) if role_ids.count(role_id) > 1]
    
    if duplicates:
        print(f"\n发现重复的角色ID: {duplicates}")
    else:
        print("\n没有发现重复的角色ID")
    
    return loaded_count == len(new_roles)

if __name__ == "__main__":
    success = test_new_roles()
    if success:
        print("\n[SUCCESS] 所有新角色都成功加载！")
        sys.exit(0)
    else:
        print("\n[ERROR] 部分新角色加载失败！")
        sys.exit(1)