#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试角色专业领域匹配算法
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core_services.role_domain_matcher import RoleDomainMatcher


def test_role_matching():
    """测试角色匹配算法"""
    print("测试角色专业领域匹配算法...")
    
    # 创建匹配器
    matcher = RoleDomainMatcher()
    
    # 测试用例
    test_cases = [
        ("创建一个关于基因编辑技术的Wiki词条", ["bioinformatics_researcher", "genomics_data_analyst", "biomaterials_scientist"]),
        ("分析气候变化对金融市场的影响", ["climate_change_economic_modeler", "environmental_policy_analyst", "financial_risk_manager"]),
        ("设计一个智能交通管理系统", ["smart_city_planner", "transportation_systems_analyst", "online_learning_platform_architect"]),
        ("开发新的抗癌药物", ["tissue_engineering_researcher", "biosignal_processing_expert", "medical_device_design_engineer"]),
        ("评估人工智能在教育中的应用", ["ai_ethicist", "learning_experience_designer", "educational_data_scientist"]),
        ("研究大脑如何处理语言信息", ["cognitive_neuroscientist", "language_cognition_researcher", "computational_neuroscientist"]),
        ("分析区块链技术在供应链中的应用", ["algorithmic_trading_engineer", "cybersecurity_architect", "financial_risk_manager"]),
        ("设计新型纳米材料用于太阳能电池", ["nanomaterials_engineer", "energy_materials_researcher", "computational_biology_methodologist"]),
        ("评估城市社区发展项目", ["community_development_expert", "smart_city_planner", "natural_resources_economist"]),
        ("分析网络安全威胁对金融系统的影响", ["cybersecurity_architect", "penetration_tester", "financial_risk_manager"])
    ]
    
    print(f"\n运行 {len(test_cases)} 个测试用例:")
    print("-" * 50)
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, (task, expected_roles) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {task}")
        
        # 获取匹配结果
        matched_roles = matcher.match_roles_to_task(task, 3)
        print(f"  匹配结果: {matched_roles}")
        print(f"  期望结果: {expected_roles}")
        
        # 检查是否有重叠
        matched_set = set(matched_roles)
        expected_set = set(expected_roles)
        overlap = matched_set & expected_set
        
        if overlap:
            print(f"  [PASS] 匹配到 {len(overlap)} 个期望角色: {list(overlap)}")
            passed_tests += 1
        else:
            print(f"  [FAIL] 未匹配到任何期望角色")
        
        # 显示详细匹配信息
        details = matcher.get_role_matching_details(task, 3)
        print(f"  关键词: {details['task_keywords']}")
        for role in details['matched_roles']:
            print(f"    {role['name']} (匹配度: {role['score']:.3f})")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed_tests}/{total_tests} 个测试通过")
    
    # 测试边界情况
    print("\n测试边界情况:")
    print("-" * 30)
    
    # 空任务描述
    empty_result = matcher.match_roles_to_task("", 3)
    print(f"空任务描述结果: {empty_result}")
    
    # 无匹配任务描述
    no_match_result = matcher.match_roles_to_task("这是一个完全不相关的任务描述", 3)
    print(f"无匹配任务描述结果: {no_match_result}")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = test_role_matching()
    if success:
        print("\n[SUCCESS] 所有测试通过！")
        sys.exit(0)
    else:
        print("\n[ERROR] 部分测试失败！")
        sys.exit(1)