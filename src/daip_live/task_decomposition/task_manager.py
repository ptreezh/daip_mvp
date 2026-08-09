"""
任务管理器
负责管理复杂任务的分解、执行和监控
"""

import asyncio
import uuid
from typing import Any

from daip_live.task_decomposition.advanced_context_manager import (
    AdvancedTaskOrchestrator,
    SubTaskContext,
    TaskStatus,
    get_context_manager,
)
from daip_live.task_decomposition.advanced_context_manager import (
    TaskContext as EnhancedTaskContext,
)
from daip_live.task_decomposition.task_decomposition_engine import (
    SequentialTaskExecutor,
    TaskDecompositionEngine,
)


class TaskManager:
    """任务管理器 - 管理复杂任务的分解、执行和监控"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.decomposer = TaskDecompositionEngine(model_provider)
        self.context_manager = get_context_manager()
        self.orchestrator = AdvancedTaskOrchestrator(
            self.context_manager, model_provider
        )
        self.executor = SequentialTaskExecutor(model_provider)

    async def handle_complex_task(self, user_request: str) -> dict[str, Any]:
        """
        处理复杂任务的完整流程
        :param user_request: 用户请求
        :return: 执行结果
        """

        # 使用高级编排器处理任务
        result = await self.orchestrator.execute_task_with_context(user_request)

        return result

    async def _decompose_task(self, user_request: str) -> list[SubTaskContext]:
        """分解任务为子任务"""

        # 使用任务分解引擎分解任务
        decomposed_tasks = await self.decomposer.decompose_task(user_request)

        # 转换为SubTaskContext格式
        subtasks = []
        for i, task in enumerate(decomposed_tasks):
            subtask = SubTaskContext(
                id=f"subtask_{i}_{uuid.uuid4().hex[:8]}",  # 生成唯一的子任务ID
                parent_task_id="pending_assignment",  # 会在添加到任务中时更新
                title=getattr(task, "title", f"子任务 {i + 1}"),
                description=getattr(task, "description", user_request),
                dependencies=[],  # 目前假设所有任务都是顺序执行
                status=TaskStatus.PENDING,
            )
            subtasks.append(subtask)

        return subtasks

    async def _create_task_context(
        self, user_request: str, subtasks: list[SubTaskContext]
    ) -> EnhancedTaskContext:
        """创建任务上下文"""
        task_id = f"task_{uuid.uuid4().hex[:12]}"

        # 创建增强的任务上下文
        task_context = EnhancedTaskContext(
            id=task_id, original_request=user_request, description=user_request
        )

        # 添加子任务
        for subtask in subtasks:
            subtask.parent_task_id = task_id
            task_context.subtasks.append(subtask)

        task_context.total_subtasks = len(subtasks)

        return task_context

    async def _execute_task_list(
        self, task_context: EnhancedTaskContext
    ) -> dict[str, Any]:
        """执行任务列表"""

        execution_results = {
            "original_request": task_context.original_request,
            "total_subtasks": len(task_context.subtasks),
            "completed_subtasks": 0,
            "failed_subtasks": 0,
            "subtask_results": [],
            "summary": "",
            "task_id": task_context.id,
        }

        # 按顺序执行子任务
        for i, subtask in enumerate(task_context.subtasks):
            # 更新子任务状态为进行中
            await self.context_manager.update_subtask_status(
                task_context.id, subtask.id, TaskStatus.IN_PROGRESS
            )

            # 执行子任务
            subtask_result = await self._execute_single_subtask(subtask, task_context)

            if subtask_result["success"]:
                execution_results["completed_subtasks"] += 1
                await self.context_manager.update_subtask_status(
                    task_context.id,
                    subtask.id,
                    TaskStatus.COMPLETED,
                    result=subtask_result.get("result"),
                )
            else:
                execution_results["failed_subtasks"] += 1
                await self.context_manager.update_subtask_status(
                    task_context.id,
                    subtask.id,
                    TaskStatus.FAILED,
                    error=subtask_result.get("error", "Unknown error"),
                )

            # 记录子任务结果
            execution_results["subtask_results"].append(
                {
                    "subtask_id": subtask.id,
                    "title": subtask.title,
                    "description": subtask.description,
                    "success": subtask_result["success"],
                    "result": subtask_result.get("result"),
                    "error": subtask_result.get("error"),
                }
            )

        # 生成最终结果
        execution_results["summary"] = await self._synthesize_final_result(
            execution_results
        )

        return execution_results

    async def _execute_single_subtask(
        self, subtask: SubTaskContext, task_context: EnhancedTaskContext
    ) -> dict[str, Any]:
        """执行单个子任务"""
        try:
            # 构建执行上下文，包含父任务信息
            execution_context = f"""
原始任务: {task_context.original_request}
当前子任务: {subtask.title}
子任务描述: {subtask.description}
任务上下文ID: {task_context.id}

请专注于完成当前子任务，并提供具体的结果或答案。
"""

            # 使用模型执行子任务
            if self.model_provider:
                response = await self.model_provider.generate(execution_context)
                result = str(response) if isinstance(response, dict) else response

                return {"success": True, "result": result}
            else:
                # 模拟执行
                return {
                    "success": True,
                    "result": f"模拟执行结果: {subtask.title} - 完成",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _synthesize_final_result(self, execution_results: dict[str, Any]) -> str:
        """合成最终结果"""
        if self.model_provider:
            # 使用AI合成最终结果
            subtask_results = execution_results["subtask_results"]

            task_summaries = "\\n".join(
                [
                    f"- {sr['title']}: {sr['result'][:100] if sr['result'] else 'N/A'}"
                    for sr in subtask_results
                    if sr["success"]
                ]
            )

            prompt = f"""请根据以下子任务执行结果，合成对原始请求的完整回答。

原始请求: {execution_results["original_request"]}

子任务执行结果:
{task_summaries}

请提供一个完整、连贯的回答，整合所有子任务的结果。"""

            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception:
                # 如果AI合成失败，返回任务结果摘要
                return f"任务分解执行完成。\\n\\n执行了 {execution_results['total_subtasks']} 个子任务，其中 {execution_results['completed_subtasks']} 个成功，{execution_results['failed_subtasks']} 个失败。\\n\\n子任务结果摘要:\\n{task_summaries}"  # noqa: E501
        else:
            # 简单合成结果
            return f"任务分解执行完成。总共执行了 {execution_results['total_subtasks']} 个子任务，其中 {execution_results['completed_subtasks']} 个成功，{execution_results['failed_subtasks']} 个失败。"  # noqa: E501

    def get_task_progress(self, task_id: str) -> dict[str, Any]:
        """获取任务进度"""
        return self.memory_service.get_task_progress(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task_context = self.memory_service.load_task_context(task_id)
        if task_context:
            # 将所有未完成的任务标记为取消
            for subtask in task_context.subtasks:
                if subtask.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                    self.memory_service.update_subtask_status(
                        subtask.subtask_id, TaskStatus.SKIPPED
                    )

            # 更新父任务状态
            self.memory_service.update_task_status(task_id, TaskStatus.SKIPPED)
            return True
        return False


# 为集成器创建一个更高级别的接口
class ComplexTaskIntegrator:
    """复杂任务集成器 - 将复杂任务处理集成到现有系统中"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.task_manager = TaskManager(model_provider)
        self.decomposer = TaskDecompositionEngine(model_provider)

    async def should_process_as_complex_task(self, user_request: str) -> bool:
        """判断是否应该作为复杂任务处理"""
        return await self.decomposer.should_decompose_task(user_request)

    async def process_complex_task(self, user_request: str) -> dict[str, Any]:
        """处理复杂任务"""
        return await self.task_manager.handle_complex_task(user_request)

    def get_task_progress(self, task_id: str) -> dict[str, Any]:
        """获取任务进度"""
        # 使用新的上下文管理器获取进度
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(self._get_task_progress_async(task_id))

    async def _get_task_progress_async(self, task_id: str) -> dict[str, Any]:
        """异步获取任务进度"""
        context_manager = get_context_manager()
        return await context_manager.get_task_progress(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 将任务状态更新为取消
        context_manager = get_context_manager()
        return await context_manager.update_task_status(task_id, TaskStatus.CANCELLED)
