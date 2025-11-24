"""
测试复杂任务意图识别和执行流程
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from daip_live.task_decomposition.task_manager import ComplexTaskIntegrator, TaskManager
from daip_live.task_decomposition.persistent_memory_service import get_memory_service


class MockModelProvider:
    async def generate(self, prompt: str):
        if "分解为多个具体的、可执行的子任务" in prompt or "TASKS:" in prompt:
            if "AI聊天机器人" in prompt:
                return """TASKS:
1. 需求分析: 分析AI聊天机器人的功能需求和技术要求
2. 技术选型: 选择适合的AI模型和开发框架
3. 系统架构设计: 设计整体系统架构和模块划分
4. 核心功能开发: 实现对话理解、响应生成等核心功能
5. 用户界面开发: 开发用户交互界面
6. 测试和优化: 进行系统测试和性能优化"""
            elif "分析" in prompt or "研究" in prompt:
                return """TASKS:
1. 文献调研: 收集相关领域的研究文献和资料
2. 数据分析: 分析现有数据和研究成果
3. 方法研究: 研究适用的分析方法和技术
4. 结果整理: 整理分析结果并形成结论
5. 报告撰写: 撰写详细分析报告"""
            else:
                return """TASKS:
1. 任务理解: 深入理解任务目标和要求
2. 方案设计: 设计实现方案和步骤
3. 执行实施: 按照方案执行任务
4. 结果验证: 验证执行结果
5. 总结归纳: 总结任务执行情况"""
        elif "执行以下子任务" in prompt:
            return f"执行结果: 完成了子任务"
        elif "合成对原始请求的完整回答" in prompt:
            return f"综合回答：这是对原始请求的完整回答。"
        else:
            return f"模拟AI响应结果"


async def test_complex_task_management():
    """测试复杂任务管理流程"""
    print("="*60)
    print("🔍 测试复杂任务管理流程")
    print("="*60)

    # 创建复杂任务集成器
    integrator = ComplexTaskIntegrator(MockModelProvider())

    # 测试复杂任务识别
    test_requests = [
        "请帮我设计一个具备多语言支持的AI聊天机器人系统",
        "帮我深入分析人工智能在教育领域的应用前景",
        "创建一个综合性的数据分析和可视化平台",
        "帮我制定一个完整的项目管理方案"
    ]

    for request in test_requests:
        print(f"\n📝 测试复杂任务: {request}")

        # 检查是否为复杂任务
        is_complex = await integrator.should_process_as_complex_task(request)
        print(f"   是否为复杂任务: {is_complex}")

        if is_complex:
            # 处理复杂任务
            result = await integrator.process_complex_task(request)
            
            print(f"   任务执行结果:")
            print(f"   - 总子任务数: {result['total_subtasks']}")
            print(f"   - 成功子任务: {result['completed_subtasks']}")
            print(f"   - 失败子任务: {result['failed_subtasks']}")
            print(f"   - 任务ID: {result['task_id']}")
            print(f"   - 摘要: {result['summary'][:100]}...")
            
            # 检查任务进度
            progress = integrator.get_task_progress(result['task_id'])
            print(f"   任务进度: {progress}")
        else:
            print("   任务不够复杂，无需分解")

    print("\n✅ 复杂任务管理流程测试完成!")


async def test_persistence_service():
    """测试持久化记忆服务"""
    print("\n" + "="*60)
    print("💾 测试持久化记忆服务")
    print("="*60)

    memory_service = get_memory_service()

    # 创建一个测试任务上下文
    from daip_live.task_decomposition.persistent_memory_service import TaskContext, SubTask, TaskStatus
    
    subtasks = [
        SubTask(
            subtask_id="test_subtask_1",
            parent_task_id="test_task_1",
            title="测试子任务1",
            description="这是第一个测试子任务",
            dependencies=[],
            status=TaskStatus.PENDING
        ),
        SubTask(
            subtask_id="test_subtask_2", 
            parent_task_id="test_task_1",
            title="测试子任务2",
            description="这是第二个测试子任务",
            dependencies=["test_subtask_1"],
            status=TaskStatus.PENDING
        )
    ]

    task_context = TaskContext(
        task_id="test_task_1",
        parent_task_id=None,
        task_description="测试任务",
        subtasks=subtasks
    )

    # 保存任务上下文
    success = memory_service.save_task_context(task_context)
    print(f"   保存任务上下文: {'✅' if success else '❌'}")

    # 加载任务上下文
    loaded_context = memory_service.load_task_context("test_task_1")
    print(f"   加载任务上下文: {'✅' if loaded_context is not None else '❌'}")
    if loaded_context:
        print(f"   原始描述: {loaded_context.task_description}")
        print(f"   子任务数: {len(loaded_context.subtasks)}")

    # 更新子任务状态
    success = memory_service.update_subtask_status("test_subtask_1", TaskStatus.COMPLETED, "测试子任务1已完成")
    print(f"   更新子任务状态: {'✅' if success else '❌'}")

    # 获取任务进度
    progress = memory_service.get_task_progress("test_task_1")
    print(f"   任务进度: {progress}")

    print("\n✅ 持久化记忆服务测试完成!")


if __name__ == "__main__":
    asyncio.run(test_persistence_service())
    asyncio.run(test_complex_task_management())