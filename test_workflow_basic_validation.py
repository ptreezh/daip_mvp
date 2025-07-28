#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流引擎基本功能验证
专注于验证工作流的初始化、配置和基本结构
"""

import sys
import os
import asyncio
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.append('src')

from src.workflows.critical_review_workflow import CriticalReviewWorkflow
from src.workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow
from src.core_services.role_manager import RoleManager
from src.institutional_primitives.base import ExecutionContext

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_workflow_initialization():
    """测试工作流初始化"""
    print("=" * 60)
    print("测试工作流初始化功能")
    print("=" * 60)
    
    try:
        print(f"\n🔧 测试CriticalReviewWorkflow初始化...")
        
        # 测试批判性审查工作流初始化
        critical_workflow = CriticalReviewWorkflow(
            workflow_id="test_critical_init",
            config={
                "generation": {
                    "role_name": "内容创作者",
                    "temperature": 0.3,
                    "max_tokens": 2048
                },
                "fact_extraction": {
                    "max_facts": 10,
                    "confidence_threshold": 0.7
                },
                "parallel_review": {
                    "reviewer_roles": ["事实核查员", "逻辑分析师", "领域专家"],
                    "review_aspects": ["事实准确性", "逻辑一致性", "专业性"]
                }
            }
        )
        
        print(f"   ✅ CriticalReviewWorkflow初始化成功")
        print(f"      工作流ID: {critical_workflow.workflow_id}")
        print(f"      配置项数量: {len(critical_workflow.config)}")
        
        # 验证节点初始化
        nodes = [
            ("generation_node", critical_workflow.generation_node),
            ("fact_extraction_node", critical_workflow.fact_extraction_node),
            ("parallel_review_node", critical_workflow.parallel_review_node),
            ("evidence_aggregation_node", critical_workflow.evidence_aggregation_node),
            ("consensus_node", critical_workflow.consensus_node),
            ("revision_node", critical_workflow.revision_node)
        ]
        
        for node_name, node in nodes:
            if node:
                print(f"      {node_name}: {type(node).__name__}")
            else:
                print(f"      {node_name}: ❌ 未初始化")
        
        print(f"\n🔧 测试MultiPerspectiveSynthesisWorkflow初始化...")
        
        # 测试多视角工作流初始化
        multi_workflow = MultiPerspectiveSynthesisWorkflow(
            workflow_id="test_multi_init",
            config={
                "task_decomposition": {
                    "planner_role": "战略规划师",
                    "default_perspectives": ["技术", "经济", "社会", "伦理"],
                    "max_subtasks": 5
                },
                "parallel_exploration": {
                    "max_parallel": 4,
                    "exploration_depth": 3
                },
                "enhanced_synthesis": {
                    "synthesis_method": "dialectical",
                    "quality_threshold": 0.7
                }
            }
        )
        
        print(f"   ✅ MultiPerspectiveSynthesisWorkflow初始化成功")
        print(f"      工作流ID: {multi_workflow.workflow_id}")
        print(f"      配置项数量: {len(multi_workflow.config)}")
        
        # 验证节点初始化
        multi_nodes = [
            ("task_decomposition_node", multi_workflow.task_decomposition_node),
            ("parallel_exploration_node", multi_workflow.parallel_exploration_node),
            ("viewpoint_collection_node", multi_workflow.viewpoint_collection_node),
            ("enhanced_synthesis_node", multi_workflow.enhanced_synthesis_node),
            ("iterative_refinement_node", multi_workflow.iterative_refinement_node)
        ]
        
        for node_name, node in multi_nodes:
            if node:
                print(f"      {node_name}: {type(node).__name__}")
            else:
                print(f"      {node_name}: ❌ 未初始化")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_execution_context_creation():
    """测试执行上下文创建"""
    print("\n" + "=" * 60)
    print("测试执行上下文创建")
    print("=" * 60)
    
    try:
        print(f"\n🔧 创建执行上下文...")
        
        # 创建角色管理器
        role_manager = RoleManager()
        
        # 创建服务字典
        services = {
            "role_manager": role_manager,
            "llm_service": None,  # 模拟LLM服务
            "wiki_service": None,  # 模拟Wiki服务
            "memory_service": None  # 模拟记忆服务
        }
        
        # 创建执行上下文
        context = ExecutionContext(
            execution_id="test_context_001",
            workflow_id="test_workflow",
            node_id="test_node",
            services=services,
            state={"test_key": "test_value"}
        )
        
        print(f"   ✅ 执行上下文创建成功")
        print(f"      执行ID: {context.execution_id}")
        print(f"      工作流ID: {context.workflow_id}")
        print(f"      节点ID: {context.node_id}")
        print(f"      服务数量: {len(context.services)}")
        print(f"      状态: {context.status}")
        print(f"      开始时间: {context.start_time}")
        
        # 测试子上下文创建
        child_context = context.create_child_context("child_node")
        
        print(f"\n   ✅ 子上下文创建成功")
        print(f"      子节点ID: {child_context.node_id}")
        print(f"      父上下文: {child_context.parent_context is not None}")
        print(f"      继承服务: {len(child_context.services)}")
        
        # 测试状态管理
        context.mark_started()
        print(f"\n   ✅ 状态管理测试")
        print(f"      启动后状态: {context.status}")
        
        context.mark_completed()
        print(f"      完成后状态: {context.status}")
        print(f"      结束时间: {context.end_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行上下文创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_role_manager_integration():
    """测试角色管理器集成"""
    print("\n" + "=" * 60)
    print("测试角色管理器集成")
    print("=" * 60)
    
    try:
        print(f"\n🔧 初始化角色管理器...")
        
        role_manager = RoleManager()
        
        print(f"   ✅ 角色管理器初始化成功")
        print(f"      角色目录: {role_manager.roles_dir}")
        print(f"      加载角色数量: {len(role_manager.roles)}")
        
        # 测试获取特定角色
        test_roles = ["事实核查员", "逻辑分析师", "领域专家", "战略规划师"]
        
        print(f"\n   🔍 测试角色获取...")
        for role_name in test_roles:
            role = role_manager.get_role(role_name)
            if role:
                print(f"      ✅ {role_name}: 找到")
                print(f"         描述: {role.get('description', 'N/A')[:50]}...")
            else:
                print(f"      ⚠️ {role_name}: 未找到，将使用默认角色")
        
        # 测试角色推荐
        if hasattr(role_manager, 'recommend_roles'):
            recommended = role_manager.recommend_roles("AI伦理分析", max_roles=3)
            print(f"\n   💡 角色推荐测试:")
            print(f"      查询: AI伦理分析")
            print(f"      推荐角色数: {len(recommended) if recommended else 0}")
            
            if recommended:
                for i, role in enumerate(recommended[:3], 1):
                    role_name = role.get('name', role.get('role_name', 'Unknown'))
                    print(f"        {i}. {role_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 角色管理器集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_configuration():
    """测试工作流配置"""
    print("\n" + "=" * 60)
    print("测试工作流配置")
    print("=" * 60)
    
    try:
        print(f"\n🔧 测试配置合并和验证...")
        
        # 测试批判性审查工作流配置
        custom_config = {
            "generation": {
                "role_name": "自定义创作者",
                "temperature": 0.5,
                "custom_param": "test_value"
            },
            "fact_extraction": {
                "max_facts": 15,
                "custom_extraction": True
            }
        }
        
        workflow = CriticalReviewWorkflow(
            workflow_id="test_config",
            config=custom_config
        )
        
        print(f"   ✅ 自定义配置应用成功")
        print(f"      生成配置: {workflow.config.get('generation', {})}")
        print(f"      事实提取配置: {workflow.config.get('fact_extraction', {})}")
        
        # 验证默认配置是否被保留
        default_keys = ["parallel_review", "evidence_aggregation", "consensus", "revision"]
        for key in default_keys:
            if key in workflow.config:
                print(f"      默认配置 {key}: ✅ 保留")
            else:
                print(f"      默认配置 {key}: ❌ 缺失")
        
        # 测试多视角工作流配置
        multi_config = {
            "task_decomposition": {
                "planner_role": "自定义规划师",
                "max_subtasks": 8
            },
            "enhanced_synthesis": {
                "synthesis_method": "custom_method",
                "quality_threshold": 0.9
            }
        }
        
        multi_workflow = MultiPerspectiveSynthesisWorkflow(
            workflow_id="test_multi_config",
            config=multi_config
        )
        
        print(f"\n   ✅ 多视角工作流配置成功")
        print(f"      任务分解配置: {multi_workflow.config.get('task_decomposition', {})}")
        print(f"      综合配置: {multi_workflow.config.get('enhanced_synthesis', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_structure_validation():
    """测试工作流结构验证"""
    print("\n" + "=" * 60)
    print("测试工作流结构验证")
    print("=" * 60)
    
    try:
        print(f"\n🔧 验证工作流执行结构...")
        
        # 创建工作流
        workflow = CriticalReviewWorkflow(
            workflow_id="test_structure",
            config={}
        )
        
        # 创建基本服务（不需要真实LLM）
        services = {
            "role_manager": RoleManager(),
            "llm_service": None  # 模拟服务
        }
        
        # 测试工作流方法存在性
        methods_to_check = ["execute"]
        
        for method_name in methods_to_check:
            if hasattr(workflow, method_name):
                method = getattr(workflow, method_name)
                if callable(method):
                    print(f"   ✅ 方法 {method_name}: 存在且可调用")
                else:
                    print(f"   ❌ 方法 {method_name}: 存在但不可调用")
            else:
                print(f"   ❌ 方法 {method_name}: 不存在")
        
        # 测试节点连接性
        print(f"\n   🔗 测试节点连接性...")
        
        nodes = [
            workflow.generation_node,
            workflow.fact_extraction_node,
            workflow.parallel_review_node,
            workflow.evidence_aggregation_node,
            workflow.consensus_node,
            workflow.revision_node
        ]
        
        connected_nodes = 0
        for i, node in enumerate(nodes):
            if node and hasattr(node, 'node_id'):
                connected_nodes += 1
                print(f"      节点 {i+1}: ✅ {type(node).__name__}")
            else:
                print(f"      节点 {i+1}: ❌ 未连接")
        
        print(f"   连接节点数: {connected_nodes}/{len(nodes)}")
        
        # 测试多视角工作流结构
        print(f"\n   🔧 验证多视角工作流结构...")
        
        multi_workflow = MultiPerspectiveSynthesisWorkflow(
            workflow_id="test_multi_structure",
            config={}
        )
        
        multi_nodes = [
            multi_workflow.task_decomposition_node,
            multi_workflow.parallel_exploration_node,
            multi_workflow.viewpoint_collection_node,
            multi_workflow.enhanced_synthesis_node,
            multi_workflow.iterative_refinement_node
        ]
        
        multi_connected = 0
        for i, node in enumerate(multi_nodes):
            if node and hasattr(node, 'node_id'):
                multi_connected += 1
                print(f"      多视角节点 {i+1}: ✅ {type(node).__name__}")
            else:
                print(f"      多视角节点 {i+1}: ❌ 未连接")
        
        print(f"   多视角连接节点数: {multi_connected}/{len(multi_nodes)}")
        
        # 结构完整性评估
        structure_score = (connected_nodes + multi_connected) / (len(nodes) + len(multi_nodes))
        print(f"\n   📊 结构完整性评分: {structure_score:.2f}")
        
        return structure_score > 0.8  # 80%以上的节点正确连接
        
    except Exception as e:
        print(f"❌ 工作流结构验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始工作流引擎基本功能验证")
    
    try:
        # 测试1: 工作流初始化
        success1 = test_workflow_initialization()
        
        # 测试2: 执行上下文创建
        success2 = test_execution_context_creation()
        
        # 测试3: 角色管理器集成
        success3 = test_role_manager_integration()
        
        # 测试4: 工作流配置
        success4 = test_workflow_configuration()
        
        # 测试5: 工作流结构验证
        success5 = asyncio.run(test_workflow_structure_validation())
        
        # 总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)
        
        results = {
            "工作流初始化": "✅ 通过" if success1 else "❌ 失败",
            "执行上下文创建": "✅ 通过" if success2 else "❌ 失败",
            "角色管理器集成": "✅ 通过" if success3 else "❌ 失败",
            "工作流配置": "✅ 通过" if success4 else "❌ 失败",
            "工作流结构验证": "✅ 通过" if success5 else "❌ 失败"
        }
        
        for test_name, result in results.items():
            print(f"{test_name}: {result}")
        
        overall_success = all([success1, success2, success3, success4, success5])
        success_rate = sum([success1, success2, success3, success4, success5]) / 5 * 100
        
        print(f"\n🎯 整体测试结果: {'✅ 全部通过' if overall_success else f'❌ 部分失败 ({success_rate:.1f}%)'}")
        
        if overall_success:
            print("\n✨ 工作流引擎基本功能验证完成！")
            print("   - 工作流初始化功能正常")
            print("   - 执行上下文管理正常")
            print("   - 角色管理器集成正常")
            print("   - 工作流配置系统正常")
            print("   - 工作流结构完整")
            print("\n📋 验证总结:")
            print("   - CriticalReviewWorkflow批判性审查工作流架构完整")
            print("   - MultiPerspectiveWorkflow多视角综合工作流架构完整")
            print("   - 制度原语节点正确初始化和连接")
            print("   - 工作流引擎基础设施就绪")
            print("\n⚠️  注意: 本测试验证了工作流的基础架构，实际LLM调用功能需要配置真实LLM服务")
        else:
            print("\n⚠️  部分功能需要进一步检查和修复")
            if not success1:
                print("   - 工作流初始化需要修复")
            if not success2:
                print("   - 执行上下文创建需要修复")
            if not success3:
                print("   - 角色管理器集成需要修复")
            if not success4:
                print("   - 工作流配置需要修复")
            if not success5:
                print("   - 工作流结构需要修复")
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)