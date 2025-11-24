"""
测试TUI中的任务可视化功能
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from daip_live.task_decomposition.task_decomposition_engine import TaskDecompositionEngine, SequentialTaskExecutor, DecomposedTask, TaskStatus
from daip_live.task_decomposition.task_decomposition_integrator import TaskDecompositionIntegrator
from daip_live.task_decomposition.task_visualization import get_task_visualization_manager


class MockModelProvider:
    async def generate(self, prompt: str):
        if "分解为多个具体的、可执行的子任务" in prompt or "TASKS:" in prompt:
            return """TASKS:
1. 需求分析: 分析AI聊天机器人系统的具体需求和目标
2. 技术选型: 选择适合的技术栈和框架
3. 架构设计: 设计聊天机器人的整体架构
4. 核心模块开发: 开发对话理解、响应生成等核心功能
5. 集成测试: 进行系统集成和功能测试
6. 部署上线: 将机器人部署到目标平台"""
        elif "执行以下子任务" in prompt:
            return f"模拟执行结果: {prompt.split('子任务标题:')[1].split()[0] if '子任务标题:' in prompt else '任务完成'}"
        else:
            return "综合回答：这是对原始请求的完整回答。"


async def test_tui_integration():
    """测试与TUI的集成"""
    print("="*60)
    print("🔍 测试任务可视化与TUI集成")
    print("="*60)

    # 创建集成器
    integrator = TaskDecompositionIntegrator(MockModelProvider())

    # 测试复杂请求
    test_request = "请帮我创建一个具备多语言支持的AI聊天机器人系统"
    
    print(f"\n📝 测试请求: {test_request}")

    # 检查是否需要分解
    should_decompose = await integrator.should_decompose_request(test_request)
    print(f"   需要任务分解: {should_decompose}")

    if should_decompose:
        # 分解任务
        tasks = await integrator.decomposer.decompose_task(test_request)
        print(f"   生成子任务数: {len(tasks)}")

        # 显示初始任务清单
        print(f"\n📋 初始任务清单:")
        integrator.visualization_manager.update_and_display(tasks, test_request)

        # 模拟执行任务并更新状态
        print(f"\n🔄 模拟执行任务并更新状态:")
        executor = integrator.executor

        # 更新第一个任务为进行中
        integrator.visualization_manager.update_task_status(tasks[0].id, TaskStatus.IN_PROGRESS)
        print(f"\n   - 任务1 '{tasks[0].title}' 设为进行中")
        integrator.visualization_manager.update_and_display(tasks, test_request)

        # 模拟执行时间
        await asyncio.sleep(0.5)

        # 更新第一个任务为完成
        integrator.visualization_manager.update_task_status(tasks[0].id, TaskStatus.COMPLETED, "需求分析完成，明确了系统功能和性能要求")
        print(f"\n   - 任务1 '{tasks[0].title}' 完成")
        integrator.visualization_manager.update_and_display(tasks, test_request)

        # 模拟执行时间
        await asyncio.sleep(0.5)

        # 更新第二个任务为进行中
        integrator.visualization_manager.update_task_status(tasks[1].id, TaskStatus.IN_PROGRESS)
        print(f"\n   - 任务2 '{tasks[1].title}' 设为进行中")
        integrator.visualization_manager.update_and_display(tasks, test_request)

        # 模拟执行时间
        await asyncio.sleep(0.5)

        # 更新第二个任务为完成
        integrator.visualization_manager.update_task_status(tasks[1].id, TaskStatus.COMPLETED, "选择Python + Transformers库作为核心技术栈")
        print(f"\n   - 任务2 '{tasks[1].title}' 完成")
        integrator.visualization_manager.update_and_display(tasks, test_request)

        # 完整执行整个任务序列
        print(f"\n🏁 完整执行任务序列 (模拟):")
        results = await executor.execute_decomposed_tasks_with_visualization(tasks, test_request, integrator.visualization_manager)

        print(f"\n✅ 最终结果 - 成功: {results['completed_tasks']}, 失败: {results['failed_tasks']}")

    print("\n✅ TUI集成测试完成!")


if __name__ == "__main__":
    asyncio.run(test_tui_integration())