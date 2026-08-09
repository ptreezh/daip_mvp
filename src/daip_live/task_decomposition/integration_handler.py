"""
任务分解系统与现有Agent流程的集成器
确保与现有状态循环兼容，不产生冲突
"""

import asyncio
from collections.abc import AsyncGenerator

from daip_live.core.models import AgentEvent, FinalResponseEvent, ThoughtEvent
from daip_live.task_decomposition.automatic_task_decomposition_engine import (
    AutoTaskDecompositionEngine,
    TaskListManager,
)


class IntegratedTaskDecompositionHandler:
    """集成任务分解处理器 - 与现有Agent流程兼容"""

    def __init__(self, model_provider=None, memory_service=None):
        self.model_provider = model_provider
        self.memory_service = memory_service
        self.auto_decomposition_engine = AutoTaskDecompositionEngine(model_provider)
        self.active_task_list_managers: dict[
            str, TaskListManager
        ] = {}  # 按会话跟踪任务清单

    async def should_handle_with_task_decomposition(self, user_request: str) -> bool:
        """判断是否应该使用任务分解处理此请求"""
        return (
            await self.auto_decomposition_engine.should_process_with_task_decomposition(
                user_request
            )
        )

    async def process_with_task_decomposition(
        self, user_request: str, session_id: str = "default"
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        使用任务分解处理复杂请求
        与现有状态循环兼容，按顺序生成事件
        """

        # 为当前会话创建任务清单管理器
        task_list_manager = TaskListManager()
        self.active_task_list_managers[session_id] = task_list_manager

        # 通知用户开始任务分解
        yield ThoughtEvent(content="🔍 正在分析任务复杂性...")

        # 1. 分解任务
        tasks = await self.auto_decomposition_engine.task_decomposer.decompose_task(
            user_request
        )

        # 添加任务到管理器
        for task in tasks:
            await task_list_manager.add_task(
                task.title, task.description, task.priority
            )

        # 2. 显示初始任务清单
        initial_display = task_list_manager.generate_task_list_display()
        yield ThoughtEvent(content=f"📋 **任务分解完成！**\n\n{initial_display}")

        # 3. 执行任务清单中的任务

        for i, task in enumerate(task_list_manager.tasks):
            # 更新任务状态为进行中
            await task_list_manager.update_task_status(task.id, "in_progress")

            # 通知用户当前执行任务
            current_status = f"""🔄 **执行任务 {i + 1}/{len(task_list_manager.tasks)}**
**任务**: {task.title}
**描述**: {task.description}
**进度**: {i + 1}/{len(task_list_manager.tasks)} 任务完成"""

            yield ThoughtEvent(content=current_status)

            try:
                # 执行单个任务
                result = await self._execute_single_task(
                    task, user_request, task_list_manager
                )

                # 更新任务状态为完成
                await task_list_manager.update_task_status(task.id, "completed", result)

                # 显示任务完成状态
                task_completion_msg = f"✅ **任务完成**: {task.title}\n结果: {result[:200] if result else '无结果'}"  # noqa: E501
                yield ThoughtEvent(content=task_completion_msg)

            except Exception as e:
                # 更新任务状态为失败
                error_msg = f"❌ **任务失败**: {task.title}\n错误: {str(e)}"
                await task_list_manager.update_task_status(
                    task.id, "failed", error=str(e)
                )
                yield ThoughtEvent(content=error_msg)

            # 每完成一个任务，都更新整个任务清单的显示
            updated_display = task_list_manager.generate_task_list_display()
            yield ThoughtEvent(content=updated_display)

        # 4. 所有任务完成后，生成最终结果
        yield ThoughtEvent(content="🎉 **所有子任务执行完成！**\n\n正在生成最终总结...")

        final_summary = await self._generate_summary(task_list_manager, user_request)
        yield FinalResponseEvent(content=final_summary)

        # 清理会话特定的任务清单管理器
        if session_id in self.active_task_list_managers:
            del self.active_task_list_managers[session_id]

    async def _execute_single_task(self, task, original_request, task_list_manager):
        """执行单个任务"""
        if self.model_provider:
            # 构建上下文
            context_parts = []
            completed_tasks = [
                t
                for t in task_list_manager.tasks
                if t.status == "completed" and t.result
            ]
            for prev_task in completed_tasks[-2:]:  # 包含最近2个已完成任务的上下文
                context_parts.append(
                    f"已完成: {prev_task.title} -> {prev_task.result[:100]}..."
                )

            context_str = "; ".join(context_parts) if context_parts else "无前置任务"

            prompt = f"""请执行以下子任务：

原请求: {original_request}

当前子任务: {task.title}
任务描述: {task.description}

上下文: {context_str}

请专注完成当前子任务，并提供具体的结果。"""

            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                return f"任务执行错误: {str(e)}"
        else:
            return f"模拟执行结果: {task.title}"

    async def _generate_summary(self, task_list_manager, original_request):
        """生成执行总结"""
        if self.model_provider:
            completed_results = []
            for task in task_list_manager.tasks:
                if task.status == "completed" and task.result:
                    completed_results.append(f"- {task.title}: {task.result[:200]}...")

            results_summary = (
                "\\n".join(completed_results)
                if completed_results
                else "无完成的任务结果"
            )

            prompt = f"""请根据以下任务执行结果，为原请求生成最终总结。

原请求: {original_request}

执行结果:
{results_summary}

请提供一个完整、连贯的最终回答。"""

            try:
                response = await self.model_provider.generate(prompt)
                return f"### 任务分解执行总结\n\n{str(response) if isinstance(response, dict) else response}"  # noqa: E501
            except Exception as e:
                return f"### 任务分解执行总结\n\n执行完成，生成总结时出错: {e}"
        else:
            progress = await task_list_manager.get_progress()
            return f"### 任务分解执行总结\n\n- 原始请求: {original_request[:100]}...\n- 总任务数: {progress['total']}\n- 完成任务: {progress['completed']}\n- 失败任务: {progress['failed']}\n\n所有任务已执行完毕。"  # noqa: E501


# 集成到现有执行器的增强器
def enhance_agent_executor_with_task_decomposition(agent_executor, model_provider=None):
    """
    为现有AgentExecutor增强任务分解功能
    保持与现有状态循环的兼容性
    """
    # 创建任务分解处理器
    task_handler = IntegratedTaskDecompositionHandler(
        model_provider, agent_executor.memory_service
    )

    # 保存原始执行方法
    original_run = agent_executor.run

    # 创建增强的运行方法
    async def enhanced_run(
        goal: str, workflow_definition=None
    ) -> AsyncGenerator[AgentEvent, None]:
        """增强的运行方法，支持任务分解"""

        # 首先检测是否是复杂任务
        should_decompose = await task_handler.should_handle_with_task_decomposition(
            goal
        )

        if should_decompose:
            # 使用任务分解处理
            async for event in task_handler.process_with_task_decomposition(
                goal,
                getattr(agent_executor, "session", {}).get("session_id", "default"),
            ):
                yield event
        else:
            # 使用原始流程
            async for event in original_run(goal, workflow_definition):
                yield event

    # 替换原运行方法
    agent_executor.run = enhanced_run
    agent_executor.task_decomposition_handler = task_handler

    return agent_executor


# 集成到意图识别器
def enhance_intent_recognizer_for_task_decomposition(
    intent_recognizer, model_provider=None
):
    """
    增强意图识别器以支持任务分解
    """
    # 保存原始识别方法
    original_recognize_intent = intent_recognizer.recognize_intent

    def enhanced_recognize_intent(text: str, session_id: str = "default"):
        """增强的意图识别，支持任务分解标记"""
        intent = original_recognize_intent(text, session_id)

        # 检查是否需要任务分解
        # 注：这里我们不能直接调用异步函数，所以通过标记来表示
        if hasattr(intent_recognizer, "task_decomposition_handler"):
            # 为后续处理添加标记
            if not hasattr(intent, "may_need_task_decomposition"):
                intent.may_need_task_decomposition = True

        return intent

    intent_recognizer.recognize_intent = enhanced_recognize_intent

    # 保存任务分解处理器
    if model_provider:
        from daip_live.task_decomposition.automatic_task_decomposition_engine import (
            AutoTaskDecompositionEngine,
        )

        intent_recognizer.task_decomposition_engine = AutoTaskDecompositionEngine(
            model_provider
        )

    return intent_recognizer


# 测试集成
async def test_integration():
    """测试集成后的功能"""

    # 创建模拟模型提供者
    class MockModelProvider:
        async def generate(self, prompt: str):
            if "分解为3-8个具体的、可执行的子任务" in prompt:
                import json

                return json.dumps(
                    {
                        "tasks": [
                            {
                                "title": "信息收集",
                                "description": "收集相关信息进行初步分析",
                                "priority": 4,
                            },
                            {
                                "title": "深入分析",
                                "description": "对收集的信息进行深入分析",
                                "priority": 5,
                            },
                            {
                                "title": "结果整理",
                                "description": "整理分析结果并得出结论",
                                "priority": 3,
                            },
                        ]
                    }
                )
            elif "请执行以下子任务" in prompt:
                import re

                # 从提示中提取任务标题
                title_match = re.search(r"当前子任务:\s*(.+?)\n", prompt)
                task_title = title_match.group(1) if title_match else "未知任务"
                return f"完成任务: {task_title} - 这是详细执行结果..."
            elif "生成最终总结" in prompt:
                return "根据各项任务的执行结果，已完成了对原始请求的全面分析和处理。各项子任务均已按计划完成，达到了预期目标。"  # noqa: E501
            else:
                return f"处理结果：{prompt[:100]}..."

    mock_provider = MockModelProvider()

    # 测试处理器
    handler = IntegratedTaskDecompositionHandler(mock_provider)

    test_request = "请帮我深入分析大数据技术在金融风控中的应用价值"

    # 检查是否需要任务分解
    should_decompose = await handler.should_handle_with_task_decomposition(test_request)

    if should_decompose:
        # 模拟执行
        events = []
        async for event in handler.process_with_task_decomposition(test_request):
            events.append(event)
            if hasattr(event, "content"):
                content = str(event.content)
                if "📋 **任务分解完成**" in content:
                    pass
                elif "🔄 **执行任务" in content:
                    pass
                elif "✅ **任务完成**" in content:
                    pass
                elif "🎉 **所有子任务执行完成**" in content:
                    pass


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_integration())
