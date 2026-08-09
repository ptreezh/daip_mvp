"""
TUI兼容的任务分解集成器
"""

import re
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DecomposedTask:
    """分解后的任务项"""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 3  # 1-5, 5最高
    result: Optional[str] = None
    error: Optional[str] = None


class TaskDecompositionIntegrator:
    """TUI兼容的任务分解集成器"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.decomposer = TaskDecompositionEngine(model_provider)
        self.executor = SequentialTaskExecutor(model_provider)

    async def should_decompose_request(self, user_request: str) -> bool:
        """判断用户请求是否需要分解"""
        return await self.decomposer.should_decompose_task(user_request)

    async def decompose_and_execute_task(
        self, user_request: str
    ) -> AsyncGenerator[str, None]:
        """分解并执行任务，返回字符串事件流"""
        yield f"[bold magenta]🧩 开始处理复杂任务:[/bold magenta]\\n'{user_request[:100]}{'...' if len(user_request) > 100 else ''}'"  # noqa: E501

        try:
            # 1. 分解任务
            tasks = await self.decomposer.decompose_task(user_request)

            if not tasks:
                yield f"[bold yellow]⚠️ 无法分解任务，使用常规处理方式:[/bold yellow]\\n{user_request}"  # noqa: E501
                return

            # 生成任务清单显示
            task_list_display = self._generate_task_list_display(tasks)
            yield f"[bold cyan]📋 任务分解完成，生成 {len(tasks)} 个待办任务:[/bold cyan]\\n\\n{task_list_display}"  # noqa: E501

            # 2. 执行任务
            yield "[bold blue]🚀 开始顺序执行任务列表...[/bold blue]"

            execution_results = await self.executor.execute_decomposed_tasks(
                tasks, user_request
            )

            # 3. 汇报执行结果
            completed_count = execution_results.get("completed_tasks", 0)
            total_count = execution_results.get("total_tasks", len(tasks))
            success_rate = (
                (completed_count / total_count * 100) if total_count > 0 else 0
            )

            yield f"[bold green]✅ 任务执行完成: {completed_count}/{total_count} 个任务成功执行 ({success_rate:.1f}%)[/bold green]"  # noqa: E501

            # 4. 生成最终结果
            final_result = execution_results.get("final_result", "")
            if final_result:
                yield f"\\n[bold yellow]🎯 最终结果:[/bold yellow]\\n{final_result}"

        except Exception as e:
            yield f"[bold red]❌ 任务分解执行出错: {str(e)}[/bold red]"
            import traceback

            traceback.print_exc()
            # 错误发生时仍然返回原始请求，以便常规处理
            yield f"[bold yellow]🔄 发生错误，使用常规处理方式:[/bold yellow]\\n{user_request}"  # noqa: E501

    def _generate_task_list_display(self, tasks: list[DecomposedTask]) -> str:
        """生成任务列表的显示文本"""
        if not tasks:
            return "当前没有任务清单"

        display = ""
        status_emojis = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️",
        }

        for i, task in enumerate(tasks, 1):
            emoji = status_emojis.get(task.status, "❓")
            status_text = task.status.value.replace("_", " ").title()

            display += f"{i}. {emoji} **{task.title}** ({status_text})\\n"
            display += f"   - {task.description}\\n"
            if task.result:
                display += f"   - 结果: {task.result[:100]}{'...' if len(task.result) > 100 else ''}\\n"  # noqa: E501
            if task.error:
                display += f"   - 错误: {task.error}\\n"
            display += "\\n"

        return display


class TaskDecompositionEngine:
    """任务分解引擎"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        # 复杂任务模式
        self.complexity_indicators = [
            r".*(分析|研究|调查).*方法",
            r".*(分析|研究|调查).*技术",
            r".*(分析|研究|调查).*原因",
            r".*(分析|研究|调查).*机制",
            r".*(设计|构建|开发).*系统",
            r".*(设计|构建|开发).*框架",
            r".*(开发|实现).*模块",
            r".*(制定|创建).*策略",
            r".*(评估|比较).*影响",
            r".*(评估|比较).*优劣",
            r".*(探索|探讨).*趋势",
            r".*(分析|研究).*前景",
            r".*(创建|实现).*解决方案",
            r".*(实现|开发).*功能",
            r".*(构建|建立).*平台",
            r".*(开发|构建).*架构",
            r".*(撰写|编写).*报告",
            r".*(编写|撰写).*方案",
            r".*(制定|创建).*计划",
            r".*(建立|构建).*机制",
        ]

    async def should_decompose_task(self, user_request: str) -> bool:
        """判断是否需要分解任务"""
        user_lower = user_request.lower()

        # 检查复杂任务模式
        for pattern in self.complexity_indicators:
            if re.search(pattern, user_lower, re.IGNORECASE):
                return True

        # 检查长度和复杂度
        word_count = len(user_request.split())
        action_words = [
            "分析",
            "研究",
            "设计",
            "开发",
            "实现",
            "制定",
            "评估",
            "比较",
            "撰写",
            "构建",
            "建立",
            "创建",
            "探索",
            "探讨",
        ]
        action_count = sum(1 for word in action_words if word in user_lower)

        # 如果包含多个动作词且长度超过一定范围，认为是复杂任务
        return word_count > 8 and action_count >= 2

    async def decompose_task(self, user_request: str) -> list[DecomposedTask]:
        """分解任务"""
        import json

        if self.model_provider:
            # 使用大模型分解任务
            prompt = f"""请将以下复杂任务分解为3-8个具体的、可执行的子任务。

任务：{user_request}

请按照以下JSON格式返回结果，每项需要包含标题和描述：
{{
    "tasks": [
        {{
            "title": "子任务标题",
            "description": "子任务详细描述"
        }}
    ]
}}"""

            try:
                response = await self.model_provider.generate(prompt)
                response_text = (
                    str(response) if isinstance(response, dict) else response
                )

                # 解析JSON
                parsed = json.loads(response_text)
                tasks_data = parsed.get("tasks", [])

                tasks = []
                for task_data in tasks_data:
                    task = DecomposedTask(
                        id=f"task_{uuid.uuid4().hex[:8]}",
                        title=task_data.get("title", "未命名任务"),
                        description=task_data.get("description", ""),
                        status=TaskStatus.PENDING,
                    )
                    tasks.append(task)

                return tasks

            except Exception:
                # 使用规则分解作为备份
                pass

        # 使用规则分解（备份方案）
        return self._decompose_by_rules(user_request)

    def _decompose_by_rules(self, user_request: str) -> list[DecomposedTask]:
        """基于规则分解任务"""
        tasks = []

        if any(word in user_request for word in ["分析", "研究", "探讨", "调查"]):
            steps = [
                ("信息收集", "收集相关信息和背景资料"),
                ("现状分析", "分析当前状况和主要问题"),
                ("深入研究", "深入研究关键问题和挑战"),
                ("结论总结", "总结研究结果并提出建议"),
            ]
        elif any(word in user_request for word in ["设计", "构建", "开发", "创建"]):
            steps = [
                ("需求分析", "明确设计或开发的具体需求"),
                ("方案设计", "设计具体的实施方案"),
                ("实现执行", "执行设计方案"),
                ("验证测试", "验证实现结果"),
            ]
        elif any(word in user_request for word in ["比较", "评估"]):
            steps = [
                ("标准制定", "确定比较或评估的标准"),
                ("信息收集", "收集各选项的相关信息"),
                ("对比分析", "进行详细的对比分析"),
                ("结论总结", "总结比较结果"),
            ]
        else:
            # 通用分解
            steps = [
                ("理解任务", "深入理解任务的具体要求"),
                ("准备阶段", "准备执行任务所需的资源"),
                ("执行过程", "执行任务的主要过程"),
                ("结果整理", "整理和总结执行结果"),
            ]

        for title, description in steps:
            task = DecomposedTask(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title=title,
                description=f"{user_request} -> {description}",
                status=TaskStatus.PENDING,
            )
            tasks.append(task)

        return tasks


class SequentialTaskExecutor:
    """顺序任务执行器"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider

    async def execute_decomposed_tasks(
        self, tasks: list[DecomposedTask], original_request: str
    ) -> dict[str, Any]:
        """执行分解后的任务"""
        results = {
            "original_request": original_request,
            "total_tasks": len(tasks),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "task_results": [],
            "final_result": "",
        }

        for i, task in enumerate(tasks):
            try:
                # 更新任务状态为进行中
                task.status = TaskStatus.IN_PROGRESS

                # 执行单个任务
                task_result = await self._execute_single_task(task, original_request)

                results["task_results"].append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "result": task_result,
                        "status": "completed",
                    }
                )
                results["completed_tasks"] += 1

                # 更新任务状态为完成
                task.status = TaskStatus.COMPLETED
                task.result = task_result

            except Exception as e:
                results["task_results"].append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "result": f"执行失败: {str(e)}",
                        "status": "failed",
                    }
                )
                results["failed_tasks"] += 1

                # 更新任务状态为失败
                task.status = TaskStatus.FAILED
                task.error = str(e)

        # 生成最终结果
        results["final_result"] = await self._synthesize_final_result(results)

        return results

    async def _execute_single_task(
        self, task: DecomposedTask, original_request: str
    ) -> str:
        """执行单个任务"""
        if self.model_provider:
            prompt = f"""请执行以下子任务：

原请求: {original_request}

当前子任务: {task.title}
任务描述: {task.description}

请专注于完成当前子任务，并提供具体的结果。"""

            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                return f"任务执行失败: {str(e)}"
        else:
            # 模拟执行
            return f"模拟执行: {task.title} - 已完成"

    async def _synthesize_final_result(self, execution_results: dict[str, Any]) -> str:
        """合成最终结果"""
        if self.model_provider:
            task_results = execution_results["task_results"]
            completed_results = [
                tr for tr in task_results if tr.get("status") == "completed"
            ]

            if completed_results:
                # 构造已完成的任务摘要
                result_summary = []
                for tr in completed_results:
                    result_preview = tr.get("result", "")[:200]  # 截取前200字符
                    result_summary.append(f"{tr['title']}: {result_preview}...")

                result_summary_block = "\n".join(result_summary)
                prompt = f"""请根据以下子任务执行结果，生成对原始请求的完整回答。

原始请求: {execution_results["original_request"]}

子任务执行结果摘要:
{result_summary_block}

请提供一个完整、连贯、结构化的最终回答。"""

                try:
                    response = await self.model_provider.generate(prompt)
                    return str(response) if isinstance(response, dict) else response
                except Exception:
                    # 返回执行结果摘要
                    pass

        # 默认合成
        task_results = execution_results["task_results"]
        completed_results = [
            tr for tr in task_results if tr.get("status") == "completed"
        ]

        summary = "任务分解执行摘要:\\n\\n"
        for tr in completed_results:
            summary += f"- {tr['title']}: {tr['result'][:100]}...\\n"

        return summary
