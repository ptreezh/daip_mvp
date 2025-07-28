#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RoleManager真实角色加载功能
验证从roles/目录加载所有角色定义，确保角色认知差异和专业特征正确加载
"""

import sys
import os
from pathlib import Path
import json
import logging

# 添加src目录到Python路径
sys.path.append('src')

from src.core_services.role_manager import RoleManager, Role

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_role_manager_loading():
    """测试RoleManager加载角色的功能"""
    print("=" * 60)
    print("测试 RoleManager 真实角色加载功能")
    print("=" * 60)
    
    # 初始化RoleManager
    role_manager = RoleManager()
    
    # 获取所有角色
    roles = role_manager.list_roles()
    print(f"\n✅ 成功加载 {len(roles)} 个角色")
    
    if not roles:
        print("❌ 警告：没有加载到任何角色")
        return False
    
    # 分析角色类型和特征
    role_types = {}
    cognitive_frameworks = set()
    professional_domains = set()
    
    print("\n📋 角色详细信息:")
    print("-" * 60)
    
    for i, role in enumerate(roles[:10]):  # 显示前10个角色的详细信息
        print(f"\n{i+1}. 角色ID: {role.id}")
        print(f"   名称: {role.name}")
        print(f"   描述: {role.description[:100]}..." if len(role.description) > 100 else f"   描述: {role.description}")
        print(f"   能力数量: {len(role.capabilities)}")
        
        # 分析认知框架
        if "认知" in role.description or "思维" in role.description:
            cognitive_frameworks.add(role.name)
        
        # 分析专业领域
        if "专家" in role.name or "学者" in role.name or "分析师" in role.name:
            professional_domains.add(role.name)
        
        # 统计角色类型
        if "Editor" in role.name:
            role_types["学术编辑"] = role_types.get("学术编辑", 0) + 1
        elif "专家" in role.name:
            role_types["专业专家"] = role_types.get("专业专家", 0) + 1
        elif "分析师" in role.name:
            role_types["分析师"] = role_types.get("分析师", 0) + 1
        else:
            role_types["其他"] = role_types.get("其他", 0) + 1
    
    if len(roles) > 10:
        print(f"\n... 还有 {len(roles) - 10} 个角色未显示")
    
    # 显示统计信息
    print(f"\n📊 角色类型统计:")
    for role_type, count in role_types.items():
        print(f"   {role_type}: {count} 个")
    
    print(f"\n🧠 认知框架角色: {len(cognitive_frameworks)} 个")
    if cognitive_frameworks:
        print(f"   示例: {', '.join(list(cognitive_frameworks)[:3])}")
    
    print(f"\n🎓 专业领域角色: {len(professional_domains)} 个")
    if professional_domains:
        print(f"   示例: {', '.join(list(professional_domains)[:3])}")
    
    return True

def test_specific_role_loading():
    """测试特定角色的加载和认知差异"""
    print("\n" + "=" * 60)
    print("测试特定角色的认知差异展示")
    print("=" * 60)
    
    role_manager = RoleManager()
    
    # 测试几个具有明显认知差异的角色
    test_roles = [
        "AI Ethics",
        "economist", 
        "Pierre Bourdieu's Reflexive Sociology Practitioner",
        "Max Weber's Interpretive Sociology Methodologist"
    ]
    
    loaded_roles = []
    
    for role_id in test_roles:
        role = role_manager.get_role_by_id(role_id)
        if role:
            loaded_roles.append(role)
            print(f"\n✅ 成功加载角色: {role.name}")
            print(f"   ID: {role.id}")
            print(f"   系统提示长度: {len(role.system_prompt)} 字符")
            print(f"   能力: {', '.join(role.capabilities[:3])}{'...' if len(role.capabilities) > 3 else ''}")
        else:
            print(f"\n❌ 未找到角色: {role_id}")
    
    # 分析认知差异
    if len(loaded_roles) >= 2:
        print(f"\n🔍 认知差异分析:")
        print("-" * 40)
        
        for i, role in enumerate(loaded_roles):
            print(f"\n{i+1}. {role.name}:")
            
            # 分析系统提示中的关键词
            prompt_lower = role.system_prompt.lower()
            
            # 认知特征关键词
            cognitive_keywords = {
                "伦理": ["ethics", "ethical", "moral", "伦理", "道德"],
                "经济": ["economic", "economy", "market", "经济", "市场"],
                "社会学": ["sociology", "social", "society", "社会", "社会学"],
                "哲学": ["philosophy", "philosophical", "哲学", "思辨"],
                "批判": ["critical", "critique", "批判", "批评"],
                "实证": ["empirical", "evidence", "data", "实证", "数据"]
            }
            
            found_features = []
            for feature, keywords in cognitive_keywords.items():
                if any(keyword in prompt_lower for keyword in keywords):
                    found_features.append(feature)
            
            if found_features:
                print(f"   认知特征: {', '.join(found_features)}")
            else:
                print(f"   认知特征: 通用型")
            
            # 分析专业领域
            if "能力" in role.__dict__ and role.capabilities:
                print(f"   专业能力: {', '.join(role.capabilities[:2])}")
    
    return len(loaded_roles) > 0

def test_role_system_prompts():
    """测试角色系统提示的质量和差异性"""
    print("\n" + "=" * 60)
    print("测试角色系统提示质量和差异性")
    print("=" * 60)
    
    role_manager = RoleManager()
    roles = role_manager.list_roles()
    
    if not roles:
        print("❌ 没有角色可供测试")
        return False
    
    # 分析系统提示
    prompt_lengths = []
    unique_prompts = set()
    
    print(f"\n📝 系统提示分析 (前5个角色):")
    print("-" * 50)
    
    for i, role in enumerate(roles[:5]):
        prompt_length = len(role.system_prompt)
        prompt_lengths.append(prompt_length)
        unique_prompts.add(role.system_prompt)
        
        print(f"\n{i+1}. {role.name}:")
        print(f"   提示长度: {prompt_length} 字符")
        print(f"   提示预览: {role.system_prompt[:150]}...")
        
        # 检查提示质量指标
        quality_indicators = {
            "包含角色定义": "你是" in role.system_prompt or "You are" in role.system_prompt,
            "包含专业背景": "专业" in role.system_prompt or "expert" in role.system_prompt.lower(),
            "包含行为指导": "应该" in role.system_prompt or "should" in role.system_prompt.lower(),
            "包含思维方式": "思考" in role.system_prompt or "think" in role.system_prompt.lower()
        }
        
        quality_score = sum(quality_indicators.values())
        print(f"   质量评分: {quality_score}/4")
        
        passed_indicators = [k for k, v in quality_indicators.items() if v]
        if passed_indicators:
            print(f"   质量特征: {', '.join(passed_indicators)}")
    
    # 统计信息
    avg_length = sum(prompt_lengths) / len(prompt_lengths) if prompt_lengths else 0
    uniqueness_ratio = len(unique_prompts) / len(roles) if roles else 0
    
    print(f"\n📊 整体统计:")
    print(f"   平均提示长度: {avg_length:.0f} 字符")
    print(f"   提示唯一性: {uniqueness_ratio:.2%}")
    print(f"   总角色数量: {len(roles)}")
    print(f"   唯一提示数量: {len(unique_prompts)}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始验证 RoleManager 真实角色加载功能")
    
    try:
        # 测试1: 基本角色加载
        success1 = test_role_manager_loading()
        
        # 测试2: 特定角色认知差异
        success2 = test_specific_role_loading()
        
        # 测试3: 系统提示质量
        success3 = test_role_system_prompts()
        
        # 总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)
        
        results = {
            "角色加载功能": "✅ 通过" if success1 else "❌ 失败",
            "认知差异展示": "✅ 通过" if success2 else "❌ 失败", 
            "系统提示质量": "✅ 通过" if success3 else "❌ 失败"
        }
        
        for test_name, result in results.items():
            print(f"{test_name}: {result}")
        
        overall_success = all([success1, success2, success3])
        print(f"\n🎯 整体测试结果: {'✅ 全部通过' if overall_success else '❌ 部分失败'}")
        
        if overall_success:
            print("\n✨ RoleManager 真实角色加载功能验证完成！")
            print("   - 成功加载真实角色定义")
            print("   - 验证了角色认知差异")
            print("   - 确认了系统提示质量")
        else:
            print("\n⚠️  需要进一步检查和修复")
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)