"""
测试任务清单可视化功能
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from daip_live.task_decomposition.task_visualization import TaskVisualizationManager, get_task_visualization_manager
from daip_live.task_decomposition.task_decomposition_engine import DecomposedTask, TaskStatus, TaskPriority


async def test_task_visualization():
    """测试任务可视化功能"""
    print("="*60)
    print("🔍 测试任务清单可视化功能")
    print("="*60)

    # 获取可视化管理器实例
    viz_manager = get_task_visualization_manager()

    # 创建一些测试任务
    test_tasks = [
        DecomposedTask(
            id="task_1",
            title="需求分析",
            description="分析任务的具体需求和目标",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            result="需求分析已完成，明确了任务目标和约束条件"
        ),
        DecomposedTask(
            id="task_2",
            title="方案设计",
            description="设计任务的实施方案",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH
        ),
        DecomposedTask(
            id="task_3",
            title="执行实现",
            description="执行任务的主要实现过程",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        ),
        DecomposedTask(
            id="task_4",
            title="验证测试",
            description="验证任务执行结果",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        ),
        DecomposedTask(
            id="task_5",
            title="结果总结",
            description="总结任务执行结果和经验",
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW
        )
    ]

    print("\n📋 初始任务状态:")
    viz_manager.update_and_display(test_tasks, "开发一个智能任务管理系统")

    # 模拟任务执行过程
    print("\n🔄 模拟任务执行过程...")

    # 模拟第二个任务完成
    await asyncio.sleep(0.5)  # 模拟执行时间
    viz_manager.update_task_status("task_2", TaskStatus.COMPLETED, "方案设计完成，确定了技术路线")
    print("\n📋 更新后的任务状态 (任务2完成):")
    viz_manager.update_and_display(test_tasks, "开发一个智能任务管理系统")

    # 模拟第三个任务开始进行中
    await asyncio.sleep(0.5)  # 模拟执行时间
    viz_manager.update_task_status("task_3", TaskStatus.IN_PROGRESS)
    print("\n📋 更新后的任务状态 (任务3进行中):")
    viz_manager.update_and_display(test_tasks, "开发一个智能任务管理系统")

    # 模拟第三个任务完成
    await asyncio.sleep(0.5)  # 模拟执行时间
    viz_manager.update_task_status("task_3", TaskStatus.COMPLETED, "任务实现完成，功能已开发完毕")
    print("\n📋 更新后的任务状态 (任务3完成):")
    viz_manager.update_and_display(test_tasks, "开发一个智能任务管理系统")

    # 模拟第四个任务失败
    await asyncio.sleep(0.5)  # 模拟执行时间
    viz_manager.update_task_status("task_4", TaskStatus.FAILED, "测试环境问题导致验证失败")
    print("\n📋 更新后的任务状态 (任务4失败):")
    viz_manager.update_and_display(test_tasks, "开发一个智能任务管理系统")

    print("\n✅ 任务可视化功能测试完成!")


# 创建一个模拟模型提供者用于测试
class MockModelProvider:
    async def generate(self, prompt: str):
        if "分解为多个具体的、可执行的子任务" in prompt:
            return """TASKS:
1. 需求分析: 分析AI系统开发的具体需求和目标
2. 技术选型: 选择适合的技术栈和框架
3. 架构设计: 设计AI系统的整体架构
4. 模块开发: 开发各个功能模块
5. 集成测试: 进行系统集成和测试
6. 部署上线: 将系统部署到生产环境"""
        elif "执行以下子任务" in prompt:
            return f"执行结果: 完成了任务"
        else:
            return "综合回答：这是对原始请求的完整回答。"


async def test_integration_with_decomposition():
    """测试与任务分解的集成"""
    print("\n" + "="*60)
    print("🔗 测试任务可视化与任务分解集成")
    print("="*60)

    from daip_live.task_decomposition.task_decomposition_engine import TaskDecompositionEngine
    from daip_live.task_decomposition.task_decomposition_integrator import TaskDecompositionIntegrator

    # 创建集成器并测试
    integrator = TaskDecompositionIntegrator(MockModelProvider())

    test_request = "请帮我设计一个人工智能聊天机器人系统"

    print(f"\n📝 测试复杂请求: {test_request}")

    # 检查是否需要分解
    should_decompose = await integrator.should_decompose_request(test_request)
    print(f"   需要任务分解: {should_decompose}")

    if should_decompose:
        # 分解任务
        tasks = await integrator.decomposer.decompose_task(test_request)
        print(f"   生成子任务数: {len(tasks)}")

        # 使用可视化管理器显示任务
        viz_manager = integrator.visualization_manager
        viz_manager.update_and_display(tasks, test_request)

        # 模拟执行一个任务
        if tasks:
            await asyncio.sleep(0.3)  # 模拟执行时间
            viz_manager.update_task_status(tasks[0].id, TaskStatus.COMPLETED, "已完成需求分析")
            print(f"\n   执行了第一个任务: {tasks[0].title}")
            viz_manager.update_and_display(tasks, test_request)

    print("\n✅ 集成测试完成!")


if __name__ == "__main__":
    asyncio.run(test_task_visualization())
    asyncio.run(test_integration_with_decomposition())