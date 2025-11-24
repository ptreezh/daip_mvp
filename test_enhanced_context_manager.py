"""
测试增强版任务上下文管理系统
"""
import asyncio
from daip_live.task_decomposition.advanced_context_manager import (
    get_context_manager, get_task_orchestrator, TaskContext, SubTaskContext, TaskStatus
)


class MockModelProvider:
    """模拟模型提供者"""
    
    async def generate(self, prompt: str):
        if "分解为3-8个具体的、可执行的子任务" in prompt or "TASKS:" in prompt:
            if "聊天机器人" in prompt or "AI助手" in prompt:
                return '''{
    "subtasks": [
        {
            "title": "需求分析",
            "description": "分析AI聊天机器人的功能需求和用户场景",
            "priority": 5,
            "dependencies": []
        },
        {
            "title": "技术选型",
            "description": "选择适合的技术栈和AI模型",
            "priority": 4,
            "dependencies": ["需求分析"]
        },
        {
            "title": "架构设计",
            "description": "设计系统整体架构和模块划分",
            "priority": 4,
            "dependencies": ["技术选型"]
        },
        {
            "title": "核心开发",
            "description": "开发核心对话功能模块",
            "priority": 5,
            "dependencies": ["架构设计"]
        },
        {
            "title": "测试验证",
            "description": "对系统进行全面测试",
            "priority": 3,
            "dependencies": ["核心开发"]
        }
    ]
}'''
            elif "分析" in prompt or "研究" in prompt:
                return '''{
    "subtasks": [
        {
            "title": "文献调研",
            "description": "收集相关领域的研究文献和资料",
            "priority": 4,
            "dependencies": []
        },
        {
            "title": "数据收集",
            "description": "收集和整理相关数据",
            "priority": 3,
            "dependencies": ["文献调研"]
        },
        {
            "title": "方法研究",
            "description": "研究适用的分析方法",
            "priority": 4,
            "dependencies": ["数据收集"]
        },
        {
            "title": "执行分析",
            "description": "对数据进行分析处理",
            "priority": 5,
            "dependencies": ["方法研究"]
        },
        {
            "title": "结果总结",
            "description": "总结分析结果并形成报告",
            "priority": 3,
            "dependencies": ["执行分析"]
        }
    ]
}'''
            else:
                return '''{
    "subtasks": [
        {
            "title": "需求理解",
            "description": "深入理解任务的具体需求",
            "priority": 4,
            "dependencies": []
        },
        {
            "title": "方案设计",
            "description": "设计解决方案的详细方案",
            "priority": 4,
            "dependencies": ["需求理解"]
        },
        {
            "title": "执行实施",
            "description": "按照方案执行任务",
            "priority": 5,
            "dependencies": ["方案设计"]
        },
        {
            "title": "结果验证",
            "description": "验证执行结果",
            "priority": 3,
            "dependencies": ["执行实施"]
        }
    ]
}'''
        elif "专注于完成当前子任务" in prompt:
            import re
            match = re.search(r'当前子任务: ([^\n]+)', prompt)
            if match:
                current_task = match.group(1)
                return f"已成功完成子任务: {current_task}。具体结果为：根据任务要求，我已完成了{current_task}的相关工作，并达到了预期目标。"
        elif "合成对原始请求的完整回答" in prompt:
            return "综合所有子任务结果，已成功完成复杂任务。通过需求分析、技术选型、架构设计、核心开发和测试验证等步骤，系统性地完成了AI聊天机器人的设计与实现。各模块均按计划执行，整体进展顺利，最终形成了完整的解决方案。"
        else:
            return f"模拟AI响应：处理请求内容"


async def test_advanced_context_manager():
    """测试高级上下文管理器"""
    print("="*60)
    print("🧪 测试高级任务上下文管理器")
    print("="*60)

    # 创建上下文管理器和编排器
    context_manager = get_context_manager()
    orchestrator = get_task_orchestrator(MockModelProvider())

    # 测试任务创建
    print("\n📝 创建任务上下文...")
    task_context = await context_manager.create_task_context(
        "帮我设计一个AI聊天机器人系统",
        "设计一个多语言支持的AI聊天机器人系统"
    )
    print(f"   ✅ 任务ID: {task_context.id}")
    print(f"   📄 原始请求: {task_context.original_request}")

    # 测试子任务添加
    print("\n➕ 添加子任务...")
    subtask1 = SubTaskContext(
        id="sub1",
        parent_task_id=task_context.id,
        title="需求分析",
        description="分析AI聊天机器人的功能需求"
    )
    await context_manager.add_subtask(task_context.id, subtask1)

    subtask2 = SubTaskContext(
        id="sub2",
        parent_task_id=task_context.id,
        title="技术选型",
        description="选择合适的技术栈"
    )
    await context_manager.add_subtask(task_context.id, subtask2)

    print(f"   ✅ 已添加 {len(task_context.subtasks)} 个子任务")

    # 测试状态更新
    print(f"\n🔄 测试子任务状态更新...")
    await context_manager.update_subtask_status(task_context.id, "sub1", TaskStatus.IN_PROGRESS)
    print(f"   状态更新: sub1 -> IN_PROGRESS")

    await context_manager.update_subtask_status(
        task_context.id, "sub1", TaskStatus.COMPLETED, 
        result="需求分析完成，确定了核心功能模块"
    )
    print(f"   状态更新: sub1 -> COMPLETED")

    # 测试进度查询
    print(f"\n📊 查询任务进度...")
    progress = await context_manager.get_task_progress(task_context.id)
    print(f"   任务ID: {progress['task_id']}")
    print(f"   进度: {progress['progress']:.1%}")
    print(f"   状态: {progress['status']}")
    print(f"   已完成: {progress['completed_subtasks']}/{progress['total_subtasks']}")

    print(f"\n✅ 高级上下文管理器测试完成!")


async def test_task_orchestrator():
    """测试任务编排器"""
    print(f"\n" + "="*60)
    print("⚙️  测试任务编排器")
    print("="*60)

    orchestrator = get_task_orchestrator(MockModelProvider())

    test_requests = [
        "请帮我设计一个支持多语言的AI聊天机器人",
        "帮我分析人工智能在医疗行业的应用前景"
    ]

    for request in test_requests:
        print(f"\n📝 测试请求: {request}")
        
        try:
            result = await orchestrator.execute_task_with_context(request)
            print(f"   ✅ 任务执行完成")
            print(f"   ID: {result['task_id']}")
            print(f"   结果摘要: {result['final_result'][:100]}...")
        except Exception as e:
            print(f"   ❌ 任务执行失败: {e}")

    print(f"\n✅ 任务编排器测试完成!")


async def test_full_integration():
    """测试完整集成"""
    print(f"\n" + "="*60)
    print("🔗 测试完整集成")
    print("="*60)

    from daip_live.task_decomposition.task_manager import ComplexTaskIntegrator
    
    # 创建集成器
    integrator = ComplexTaskIntegrator(MockModelProvider())

    test_request = "帮我创建一个智能文档分析系统，需要支持PDF解析和内容总结功能"
    
    print(f"\n📝 测试完整流程: {test_request}")

    # 检查是否为复杂任务
    is_complex = await integrator.should_process_as_complex_task(test_request)
    print(f"   是否为复杂任务: {is_complex}")

    if is_complex:
        # 处理复杂任务
        print(f"\n🔄 执行复杂任务...")
        result = await integrator.process_complex_task(test_request)
        
        print(f"   ✅ 任务执行完成:")
        print(f"   - 任务ID: {result['task_id']}")
        print(f"   - 结果: {result['final_result'][:150]}...")
        
        # 获取进度
        print(f"\n📊 获取任务进度...")
        # 由于get_task_progress是同步的，我们使用内部异步方法
        progress = await integrator._get_task_progress_async(result['task_id'])
        print(f"   - 进度: {progress['progress']:.1%}")
        print(f"   - 状态: {progress['status']}")
        print(f"   - 完成子任务: {progress['completed_subtasks']}/{progress['total_subtasks']}")

    print(f"\n✅ 完整集成测试完成!")


if __name__ == "__main__":
    asyncio.run(test_advanced_context_manager())
    asyncio.run(test_task_orchestrator())
    asyncio.run(test_full_integration())