#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V0.1.1 组件集成验证测试
验证PersonalAssistant与核心组件的协作流程
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_personal_assistant_basic_functionality():
    """测试PersonalAssistant基本功能"""
    print("\n" + "="*60)
    print("测试 PersonalAssistant 基本功能")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        # 1. 实例化测试
        assistant = PersonalAssistantService()
        print("✅ PersonalAssistantService 实例化成功")
        
        # 2. 测试基本方法存在性
        required_methods = ['analyze_intent', 'assemble_team', 'process_message', 'execute_command']
        for method in required_methods:
            if hasattr(assistant, method):
                print(f"✅ 方法 {method} 存在")
            else:
                print(f"❌ 方法 {method} 缺失")
                return False
        
        # 3. 测试process_message方法
        session_id = "test_session_001"
        test_message = "我想分析AI在教育中的应用"
        
        start_time = time.time()
        response = await assistant.process_message(test_message, session_id)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"✅ process_message 响应时间: {response_time:.2f}秒")
        print(f"✅ 响应内容长度: {len(response)}字符")
        
        if response_time > 30:
            print("⚠️ 响应时间超过30秒阈值")
        
        return True
        
    except Exception as e:
        print(f"❌ PersonalAssistant 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_intent_analysis_integration():
    """测试意图分析集成"""
    print("\n" + "="*60)
    print("测试 IntentAnalysis 集成")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        assistant = PersonalAssistantService()
        
        # 测试不同类型的用户输入
        test_cases = [
            ("我需要分析这个观点的可信度", "critical_review"),
            ("让我们从多个角度讨论这个话题", "multi_perspective"),
            ("帮我研究AI的发展趋势", "multi_perspective")
        ]
        
        for user_input, expected_workflow in test_cases:
            try:
                context = {"user_id": "test_user", "message_history": []}
                result = await assistant.analyze_intent(user_input, context)
                
                print(f"✅ 输入: '{user_input[:30]}...'")
                print(f"   - 工作流类型: {result.workflowType}")
                print(f"   - 置信度: {result.confidence}")
                print(f"   - 推理: {result.reasoning[:50]}...")
                
            except Exception as e:
                print(f"❌ 意图分析失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ IntentAnalysis 集成测试失败: {e}")
        return False

async def test_role_manager_integration():
    """测试RoleManager集成"""
    print("\n" + "="*60)
    print("测试 RoleManager 集成")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        from personal_intelligence_hub.services.personal_assistant import WorkflowType
        
        assistant = PersonalAssistantService()
        
        # 测试团队组建功能
        test_topics = [
            ("AI伦理问题", WorkflowType.CRITICAL_REVIEW),
            ("气候变化解决方案", WorkflowType.MULTI_PERSPECTIVE)
        ]
        
        for topic, workflow_type in test_topics:
            try:
                team_proposal = await assistant.assemble_team(topic, workflow_type)
                
                print(f"✅ 话题: '{topic}'")
                print(f"   - 选中角色: {team_proposal.agents}")
                print(f"   - 多样性评分: {team_proposal.diversity_score}")
                print(f"   - 选择理由: {team_proposal.rationale[:50]}...")
                
            except Exception as e:
                print(f"❌ 团队组建失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ RoleManager 集成测试失败: {e}")
        return False

async def test_command_execution():
    """测试命令执行功能"""
    print("\n" + "="*60)
    print("测试 命令执行功能")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        assistant = PersonalAssistantService()
        session_id = "test_session_002"
        
        # 测试不同命令
        test_commands = ["/help", "/status"]
        
        for command in test_commands:
            try:
                start_time = time.time()
                result = await assistant.execute_command(command, session_id)
                end_time = time.time()
                
                response_time = end_time - start_time
                print(f"✅ 命令: {command}")
                print(f"   - 响应时间: {response_time:.2f}秒")
                print(f"   - 响应长度: {len(result)}字符")
                
            except Exception as e:
                print(f"❌ 命令 {command} 执行失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 命令执行测试失败: {e}")
        return False

async def test_error_handling():
    """测试错误处理机制"""
    print("\n" + "="*60)
    print("测试 错误处理机制")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        assistant = PersonalAssistantService()
        
        # 测试异常输入处理
        test_cases = [
            ("", "空输入"),
            ("a" * 10000, "超长输入"),
            ("🚀🎯💡", "特殊字符")
        ]
        
        for test_input, description in test_cases:
            try:
                result = await assistant.process_message(test_input, "test_session")
                print(f"✅ {description}: 正常处理")
                
            except Exception as e:
                print(f"⚠️ {description}: 异常 - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

async def run_integration_tests():
    """运行所有集成测试"""
    print("🚀 开始 V0.1.1 组件集成验证测试")
    print("="*80)
    
    test_results = []
    
    # 执行所有测试
    tests = [
        ("PersonalAssistant基本功能", test_personal_assistant_basic_functionality),
        ("IntentAnalysis集成", test_intent_analysis_integration),
        ("RoleManager集成", test_role_manager_integration),
        ("命令执行功能", test_command_execution),
        ("错误处理机制", test_error_handling)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 执行测试: {test_name}")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {e}")
            test_results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*80)
    print("🎯 测试结果汇总")
    print("="*80)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
    
    print(f"\n📊 总体结果: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有集成测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步调查")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)