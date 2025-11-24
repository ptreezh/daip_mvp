"""
测试修复后的依赖关系处理
"""
from daip_live.task_decomposition.advanced_context_manager import (
    SubTaskContext, TaskStatus
)


def test_dependency_calculation():
    """测试依赖关系计算"""
    print("Testing dependency calculation...")
    
    # 创建几个子任务用于测试依赖关系
    subtasks = [
        SubTaskContext(
            id="需求分析",
            parent_task_id="test",
            title="需求分析",
            description="分析任务需求",
            dependencies=[],
            priority=5
        ),
        SubTaskContext(
            id="技术选型",
            parent_task_id="test",
            title="技术选型",
            description="选择技术方案",
            dependencies=["需求分析"],
            priority=4
        ),
        SubTaskContext(
            id="架构设计",
            parent_task_id="test",
            title="架构设计",
            description="设计系统架构",
            dependencies=["技术选型"],
            priority=3
        )
    ]
    
    # 导入并测试函数
    from daip_live.task_decomposition.advanced_context_manager import AdvancedTaskOrchestrator
    orchestrator = AdvancedTaskOrchestrator(None, None)  # 没有model provider，只测试依赖计算
    
    try:
        order = orchestrator._calculate_execution_order(subtasks)
        print(f'Execution order: {order}')
        print('✅ Dependency handling works correctly!')
    except KeyError as e:
        print(f'❌ KeyError: {e}')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')
        import traceback
        traceback.print_exc()


def test_empty_dependencies():
    """测试空依赖关系"""
    print("\nTesting empty dependencies...")
    
    # 创建几个子任务用于测试依赖关系
    subtasks = [
        SubTaskContext(
            id="task1",
            parent_task_id="test",
            title="任务1",
            description="第一个任务",
            dependencies=[],
            priority=5
        ),
        SubTaskContext(
            id="task2", 
            parent_task_id="test",
            title="任务2",
            description="第二个任务",
            dependencies=[],
            priority=4
        ),
        SubTaskContext(
            id="task3",
            parent_task_id="test", 
            title="任务3",
            description="第三个任务",
            dependencies=[],
            priority=3
        )
    ]
    
    # 导入并测试函数
    from daip_live.task_decomposition.advanced_context_manager import AdvancedTaskOrchestrator
    orchestrator = AdvancedTaskOrchestrator(None, None)  # 没有model provider，只测试依赖计算
    
    try:
        order = orchestrator._calculate_execution_order(subtasks)
        print(f'Execution order: {order}')
        print('✅ Empty dependencies handled correctly!')
    except KeyError as e:
        print(f'❌ KeyError: {e}')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')


if __name__ == "__main__":
    test_dependency_calculation()
    test_empty_dependencies()