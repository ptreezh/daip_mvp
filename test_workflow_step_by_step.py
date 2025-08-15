#!/usr/bin/env python3
"""逐步验证工作流引擎功能
"""

import sys

sys.path.append('src')

def test_role_manager():
    """测试角色管理器"""
    try:
        from src.core_services.role_manager import RoleManager
        
        role_manager = RoleManager()
        
        # 验证基本属性
        assert hasattr(role_manager, 'roles_directory'), "RoleManager缺少roles_directory属性"
        assert hasattr(role_manager, '_roles'), "RoleManager缺少_roles属性"
        
        # 验证基本方法
        assert hasattr(role_manager, 'get_role_by_id'), "RoleManager缺少get_role_by_id方法"
        assert hasattr(role_manager, 'list_roles'), "RoleManager缺少list_roles方法"
        
        # 验证角色加载
        roles = role_manager.list_roles()
        assert len(roles) > 0, f"未加载任何角色，当前数量: {len(roles)}"
        
        print("✅ RoleManager验证通过")
        return True
        
    except Exception as e:
        print(f"❌ RoleManager验证失败: {e}")
        return False

def test_execution_context():
    """测试执行上下文"""
    try:
        from src.institutional_primitives.base import ExecutionContext
        
        # 创建执行上下文
        context = ExecutionContext(
            execution_id="test_001",
            workflow_id="test_workflow",
            node_id="test_node",
            services={},
            state={}
        )
        
        # 验证基本属性
        assert context.execution_id == "test_001", "execution_id不匹配"
        assert context.workflow_id == "test_workflow", "workflow_id不匹配"
        assert context.node_id == "test_node", "node_id不匹配"
        assert context.status == "pending", "初始状态应为pending"
        
        # 验证状态管理
        context.mark_started()
        assert context.status == "running", "启动后状态应为running"
        
        context.mark_completed()
        assert context.status == "completed", "完成后状态应为completed"
        
        print("✅ ExecutionContext验证通过")
        return True
        
    except Exception as e:
        print(f"❌ ExecutionContext验证失败: {e}")
        return False

def test_critical_review_workflow():
    """测试批判性审查工作流"""
    try:
        from src.workflows.critical_review_workflow import CriticalReviewWorkflow
        
        # 创建工作流
        workflow = CriticalReviewWorkflow(
            workflow_id="test_critical",
            config={}
        )
        
        # 验证基本属性
        assert workflow.workflow_id == "test_critical", "workflow_id不匹配"
        assert hasattr(workflow, 'config'), "缺少config属性"
        assert len(workflow.config) > 0, "config为空"
        
        # 验证节点存在
        nodes = [
            'generation_node',
            'fact_extraction_node', 
            'parallel_review_node',
            'evidence_aggregation_node',
            'consensus_node',
            'revision_node'
        ]
        
        for node_name in nodes:
            assert hasattr(workflow, node_name), f"缺少节点: {node_name}"
            node = getattr(workflow, node_name)
            assert node is not None, f"节点{node_name}为None"
            assert hasattr(node, 'primitive_id'), f"节点{node_name}缺少primitive_id"
        
        # 验证execute方法
        assert hasattr(workflow, 'execute'), "缺少execute方法"
        assert callable(workflow.execute), "execute不可调用"
        
        print("✅ CriticalReviewWorkflow验证通过")
        return True
        
    except Exception as e:
        print(f"❌ CriticalReviewWorkflow验证失败: {e}")
        return False

def test_multi_perspective_workflow():
    """测试多视角工作流"""
    try:
        from src.workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow
        
        # 创建工作流
        workflow = MultiPerspectiveSynthesisWorkflow(
            workflow_id="test_multi",
            config={}
        )
        
        # 验证基本属性
        assert workflow.workflow_id == "test_multi", "workflow_id不匹配"
        assert hasattr(workflow, 'config'), "缺少config属性"
        assert len(workflow.config) > 0, "config为空"
        
        # 验证节点存在
        nodes = [
            'task_decomposition_node',
            'parallel_exploration_node',
            'viewpoint_collection_node', 
            'enhanced_synthesis_node',
            'iterative_refinement_node'
        ]
        
        for node_name in nodes:
            assert hasattr(workflow, node_name), f"缺少节点: {node_name}"
            node = getattr(workflow, node_name)
            assert node is not None, f"节点{node_name}为None"
            assert hasattr(node, 'primitive_id'), f"节点{node_name}缺少primitive_id"
        
        # 验证execute方法
        assert hasattr(workflow, 'execute'), "缺少execute方法"
        assert callable(workflow.execute), "execute不可调用"
        
        print("✅ MultiPerspectiveSynthesisWorkflow验证通过")
        return True
        
    except Exception as e:
        print(f"❌ MultiPerspectiveSynthesisWorkflow验证失败: {e}")
        return False

def test_workflow_engine():
    """测试工作流引擎"""
    try:
        from src.institutional_primitives.registry import PrimitiveRegistry
        from src.institutional_primitives.workflow_engine import WorkflowEngine
        
        # 创建注册表和引擎
        registry = PrimitiveRegistry()
        engine = WorkflowEngine(registry)
        
        # 验证基本属性
        assert hasattr(engine, 'primitive_registry'), "缺少primitive_registry属性"
        assert engine.primitive_registry is registry, "registry不匹配"
        
        # 验证基本方法
        assert hasattr(engine, 'execute_workflow'), "缺少execute_workflow方法"
        assert callable(engine.execute_workflow), "execute_workflow不可调用"
        
        print("✅ WorkflowEngine验证通过")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowEngine验证失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🚀 开始逐步验证工作流引擎功能")
    
    tests = [
        ("RoleManager", test_role_manager),
        ("ExecutionContext", test_execution_context), 
        ("CriticalReviewWorkflow", test_critical_review_workflow),
        ("MultiPerspectiveWorkflow", test_multi_perspective_workflow),
        ("WorkflowEngine", test_workflow_engine)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break
    
    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)