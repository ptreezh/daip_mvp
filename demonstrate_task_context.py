"""
演示持久化记忆如何组织上下文并完成子任务
"""
import asyncio
from datetime import datetime
from daip_live.task_decomposition.task_manager import TaskManager
from daip_live.task_decomposition.persistent_memory_service import (
    TaskContext, SubTask, TaskStatus, get_memory_service
)


class DemoModelProvider:
    """演示用的模型提供者"""
    
    async def generate(self, prompt: str):
        if "分解为多个具体的、可执行的子任务" in prompt:
            # 根据不同请求返回不同的子任务
            if "聊天机器人" in prompt:
                return """TASKS:
1. 需求分析: 分析AI聊天机器人的功能需求
2. 技术选型: 选择合适的技术栈
3. 系统设计: 设计系统架构和模块
4. 核心开发: 开发核心功能模块
5. 测试优化: 进行系统测试和优化"""
            elif "分析" in prompt or "研究" in prompt:
                return """TASKS:
1. 文献调研: 收集相关研究资料
2. 数据分析: 分析现有数据
3. 方法研究: 研究适用方法
4. 结果整理: 整理分析结果
5. 报告撰写: 撰写分析报告"""
            else:
                return """TASKS:
1. 需求理解: 理解任务需求
2. 方案设计: 设计实现方案
3. 执行实施: 执行任务
4. 结果验证: 验证执行结果
5. 总结报告: 总结任务完成情况"""
        elif "执行以下子任务" in prompt:
            # 模拟不同子任务的不同响应
            if "需求分析" in prompt:
                return "已完成AI聊天机器人的需求分析，主要功能包括：多语言支持、上下文理解、智能回复生成等"
            elif "技术选型" in prompt:
                return "选择Python + Transformers + FastAPI技术栈，使用GPT模型作为核心AI引擎"
            elif "系统设计" in prompt:
                return "设计了微服务架构，包含用户管理、对话引擎、上下文管理、知识库等模块"
            elif "核心开发" in prompt:
                return "完成核心功能开发，包括对话理解、回复生成、上下文管理等模块"
            elif "测试优化" in prompt:
                return "完成系统测试，性能优化效果显著，响应时间降低30%"
            elif "文献调研" in prompt:
                return "收集了50篇相关研究文献，涵盖机器学习、自然语言处理等领域的最新进展"
            elif "数据分析" in prompt:
                return "分析了现有数据集，发现关键特征和模式，为后续研究提供基础"
            elif "方法研究" in prompt:
                return "研究了深度学习、强化学习等多种方法，确定最优技术路线"
            else:
                return "已完成子任务"
        elif "合成对原始请求的完整回答" in prompt:
            return "综合所有子任务结果，已成功完成复杂任务。通过需求分析、技术选型、系统设计、核心开发和测试优化等步骤，系统性地完成了任务目标。"
        else:
            return "模拟的AI响应结果"


async def demonstrate_task_context_organization():
    """演示任务上下文组织过程"""
    print("="*60)
    print("🔍 演示持久化记忆如何组织上下文并完成子任务")
    print("="*60)

    # 创建任务管理器
    task_manager = TaskManager(DemoModelProvider())
    memory_service = get_memory_service()

    # 模拟复杂任务处理流程
    user_request = "请帮我设计一个AI聊天机器人系统，需要支持多语言和智能对话功能"

    print(f"📝 用户请求: {user_request}")
    print(f"🔧 开始处理复杂任务...")

    # 1. 检查是否为复杂任务
    print(f"\n🔍 检查任务复杂性...")
    is_complex = await task_manager.decomposer.should_decompose_task(user_request)
    print(f"   是复杂任务: {is_complex}")

    if is_complex:
        # 2. 分解任务
        print(f"\n🧩 开始任务分解...")
        subtasks = await task_manager._decompose_task(user_request)
        print(f"   任务分解完成，生成 {len(subtasks)} 个子任务:")
        for i, st in enumerate(subtasks, 1):
            print(f"      {i}. {st.title}: {st.description}")

        # 3. 创建任务上下文
        print(f"\n📋 创建任务上下文...")
        task_context = await task_manager._create_task_context(user_request, subtasks)
        print(f"   任务ID: {task_context.task_id}")
        print(f"   任务描述: {task_context.task_description}")
        print(f"   子任务数量: {len(task_context.subtasks)}")
        print(f"   初始状态: {task_context.status.value}")

        # 4. 保存到持久化存储
        print(f"\n💾 保存到持久化记忆...")
        memory_service.save_task_context(task_context)
        print(f"   任务上下文已保存")

        # 5. 演示执行过程中的上下文维护
        print(f"\n🔄 模拟子任务执行过程...")
        for i, subtask in enumerate(task_context.subtasks):
            print(f"\n   执行子任务 {i+1}/{len(task_context.subtasks)}: {subtask.title}")
            print(f"   - 当前状态: {subtask.status.value}")
            print(f"   - 任务描述: {subtask.description}")
            print(f"   - 所属任务ID: {subtask.parent_task_id}")
            
            # 更新状态为进行中
            memory_service.update_subtask_status(subtask.subtask_id, TaskStatus.IN_PROGRESS)
            print(f"   - 状态更新: {TaskStatus.IN_PROGRESS.value}")
            
            # 模拟执行
            execution_result = await task_manager._execute_single_subtask(subtask, task_context)
            
            # 更新状态为完成
            memory_service.update_subtask_status(
                subtask.subtask_id, 
                TaskStatus.COMPLETED, 
                result=execution_result.get("result", "执行完成")
            )
            print(f"   - 状态更新: {TaskStatus.COMPLETED.value}")
            
            # 显示当前整体进度
            progress = memory_service.get_task_progress(task_context.task_id)
            print(f"   - 整体进度: {progress['completed']}/{progress['total_subtasks']} "
                  f"({progress['progress_percentage']:.1f}%)")

        # 6. 显示最终状态
        print(f"\n📊 最终任务状态:")
        final_progress = memory_service.get_task_progress(task_context.task_id)
        print(f"   总子任务数: {final_progress['total_subtasks']}")
        print(f"   已完成: {final_progress['completed']}")
        print(f"   执行中: {final_progress['in_progress']}")
        print(f"   已失败: {final_progress['failed']}")
        print(f"   待执行: {final_progress['pending']}")
        print(f"   完成率: {final_progress['progress_percentage']:.1f}%")
        print(f"   整体状态: {final_progress['overall_status']}")

        # 7. 演示上下文访问
        print(f"\n🔍 演示如何从持久化记忆中访问任务上下文:")
        loaded_context = memory_service.load_task_context(task_context.task_id)
        if loaded_context:
            print(f"   成功加载任务上下文")
            print(f"   任务描述: {loaded_context.task_description}")
            print(f"   子任务详情:")
            for subtask in loaded_context.subtasks:
                print(f"     - {subtask.title}: {subtask.status.value}")
                if subtask.result:
                    print(f"       结果预览: {subtask.result[:50]}...")

        print(f"\n✅ 持久化记忆组织上下文并完成子任务的流程演示完成！")


async def demonstrate_context_inheritance():
    """演示上下文如何在子任务间传递和继承"""
    print(f"\n" + "="*60)
    print("🔄 演示上下文传递和继承机制")
    print("="*60)

    memory_service = get_memory_service()
    
    # 创建一个包含多个相关子任务的任务上下文
    from daip_live.task_decomposition.persistent_memory_service import TaskContext, SubTask, TaskStatus
    
    # 创建有依赖关系的子任务
    subtasks = [
        SubTask(
            subtask_id="task_1_research",
            parent_task_id="demo_task",
            title="文献调研",
            description="收集相关研究文献",
            dependencies=[],
            status=TaskStatus.PENDING
        ),
        SubTask(
            subtask_id="task_2_analysis", 
            parent_task_id="demo_task",
            title="数据分析",
            description="分析调研结果",
            dependencies=["task_1_research"],  # 依赖第一个任务
            status=TaskStatus.PENDING
        ),
        SubTask(
            subtask_id="task_3_conclusion",
            parent_task_id="demo_task", 
            title="结论总结",
            description="总结分析结果",
            dependencies=["task_2_analysis"],  # 依赖第二个任务
            status=TaskStatus.PENDING
        )
    ]

    task_context = TaskContext(
        task_id="demo_task",
        parent_task_id=None,
        task_description="进行一项完整的研究分析",
        subtasks=subtasks
    )

    # 保存到内存服务
    memory_service.save_task_context(task_context)

    print("创建了有依赖关系的任务链:")
    print("  文献调研 → 数据分析 → 结论总结")
    
    # 演示依赖检查机制
    for subtask in task_context.subtasks:
        dependencies_satisfied = all(
            memory_service.get_subtask(dep_id).status == TaskStatus.COMPLETED 
            for dep_id in subtask.dependencies
        ) if subtask.dependencies else True
        
        print(f"  {subtask.title}: 依赖满足 = {dependencies_satisfied}")
        
        if dependencies_satisfied:
            # 执行任务
            memory_service.update_subtask_status(subtask.subtask_id, TaskStatus.COMPLETED)
            print(f"    → 状态更新为: {TaskStatus.COMPLETED.value}")
        else:
            print(f"    → 等待依赖任务完成")
    
    print(f"\n✅ 上下文传递和依赖管理机制演示完成！")


if __name__ == "__main__":
    asyncio.run(demonstrate_task_context_organization())
    asyncio.run(demonstrate_context_inheritance())