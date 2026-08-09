"""
第一性原理设计：大模型驱动的自动任务分解系统

核心设计理念：
1. 识别复杂任务 - 智能判断何时需要任务分解
2. 生成任务清单 - 创建可视化的Todo列表
3. 顺序执行 - 按照清单逐步完成任务
4. 状态更新 - 实时反馈任务进展
5. 与现有状态循环协调
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from daip_live.core.models import AgentEvent, ThoughtEvent


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskItem:
    """任务清单中的单项"""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1  # 1-5, 5最高
    estimated_time: Optional[str] = None  # 预估耗时
    dependencies: list[str] = field(default_factory=list)  # 依赖的其他任务ID
    result: Optional[str] = None  # 完成后的结果
    error: Optional[str] = None  # 错误信息
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class TaskListManager:
    """任务清单管理器 - 管理任务列表和状态"""

    def __init__(self):
        self.tasks: list[TaskItem] = []
        self.task_mapping: dict[str, TaskItem] = {}  # ID到任务的映射
        self._lock = asyncio.Lock()  # 线程安全锁

    async def add_task(
        self, title: str, description: str, priority: int = 3
    ) -> TaskItem:
        """添加任务到清单"""
        async with self._lock:
            task = TaskItem(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title=title,
                description=description,
                priority=priority,
            )
            self.tasks.append(task)
            self.task_mapping[task.id] = task
            return task

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """更新任务状态"""
        async with self._lock:
            if task_id in self.task_mapping:
                task = self.task_mapping[task_id]
                task.status = status
                task.result = result
                task.error = error
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.now()

    async def get_pending_tasks(self) -> list[TaskItem]:
        """获取待执行任务"""
        async with self._lock:
            return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    async def get_completed_tasks(self) -> list[TaskItem]:
        """获取已完成任务"""
        async with self._lock:
            return [task for task in self.tasks if task.status == TaskStatus.COMPLETED]

    async def get_task_by_id(self, task_id: str) -> Optional[TaskItem]:
        """根据ID获取任务"""
        async with self._lock:
            return self.task_mapping.get(task_id)

    async def get_progress(self) -> dict[str, int]:
        """获取任务进度统计"""
        async with self._lock:
            total = len(self.tasks)
            completed = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
            in_progress = len(
                [t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS]
            )
            pending = len([t for t in self.tasks if t.status == TaskStatus.PENDING])
            failed = len([t for t in self.tasks if t.status == TaskStatus.FAILED])

            return {
                "total": total,
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "failed": failed,
            }

    def generate_task_list_display(self) -> str:
        """生成任务清单的显示文本"""
        if not self.tasks:
            return "当前没有任务清单"

        display = "📋 **任务清单**\n\n"
        status_emojis = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️",
        }

        for i, task in enumerate(self.tasks, 1):
            emoji = status_emojis.get(task.status, "❓")
            status_text = {
                TaskStatus.PENDING: "待执行",
                TaskStatus.IN_PROGRESS: "执行中",
                TaskStatus.COMPLETED: "已完成",
                TaskStatus.FAILED: "已失败",
                TaskStatus.SKIPPED: "已跳过",
            }.get(task.status, "未知")

            display += f"{i}. {emoji} **{task.title}** ({status_text})\n"
            display += f"   - {task.description}\n"
            if task.result:
                display += f"   - 结果: {task.result[:100]}{'...' if len(task.result) > 100 else ''}\n"  # noqa: E501
            if task.error:
                display += f"   - 错误: {task.error}\n"
            display += "\n"

        # 添加进度统计
        stats = {
            "total": len(self.tasks),
            "completed": len(
                [t for t in self.tasks if t.status == TaskStatus.COMPLETED]
            ),
            "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            "failed": len([t for t in self.tasks if t.status == TaskStatus.FAILED]),
        }
        display += (
            f"📈 **进度**: {stats['completed']}/{stats['total']} 任务完成 ({stats['completed'] / stats['total'] * 100:.1f}%)"  # noqa: E501
            if stats["total"] > 0
            else ""
        )

        return display


class ComplexityDetector:
    """复杂任务检测器"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        # 复杂任务关键词
        self.complexity_keywords = [
            # 动词类
            "分析",
            "研究",
            "调查",
            "评估",
            "设计",
            "构建",
            "开发",
            "创建",
            "实现",
            "比较",
            "总结",
            "撰写",
            "制定",
            "规划",
            "探索",
            "审查",
            "验证",
            "测试",
            "优化",
            "改进",
            "建立",
            "组织",
            "管理",
            # 形容词/副词类
            "复杂",
            "困难",
            "详细",
            "深入",
            "全面",
            "系统",
            "整体",
            "多方面",
            "多层次",
            "多维度",
            "综合性",
            "战略性",
            "创新性",
            "重要",
            "关键",
            "核心",
            "主要",
            "显著",
            "深入",
            "广泛",
            "长远",
            "持续",
        ]

        # 复杂任务模式
        self.complex_task_patterns = [
            r".*(分析|研究|评估).*(方法|技术|策略|机制|趋势)",
            r".*(设计|构建|创建).*(系统|框架|模型|平台|解决方案)",
            r".*(比较|对比|评估).*(优劣|性能|效果|差异)",
            r".*(撰写|编写|制定).*(报告|方案|计划|政策|战略)",
            r".*(实现|开发).*(功能|特性|模块|系统)",
            r".*(探索|调查).*(可能性|潜力|应用场景|挑战)",
        ]

    async def is_complex_task(self, user_request: str) -> bool:
        """判断用户请求是否是复杂任务"""
        # 方法1: 基于关键词和模式
        if await self._detect_by_rules(user_request):
            return True

        # 方法2: 基于大模型判断（如果可用）
        if self.model_provider:
            return await self._detect_by_model(user_request)

        return False

    async def _detect_by_rules(self, user_request: str) -> bool:
        """基于规则检测复杂任务"""
        user_text_lower = user_request.lower()

        # 检查复杂性关键词
        complexity_count = sum(
            1 for keyword in self.complexity_keywords if keyword in user_request
        )

        # 检查复杂任务模式
        pattern_match = any(
            __import__("re").search(pattern, user_text_lower)
            for pattern in self.complex_task_patterns
        )

        # 检查句子复杂度
        action_words = [
            "分析",
            "设计",
            "实现",
            "开发",
            "研究",
            "评估",
            "验证",
            "比较",
            "总结",
            "制定",
            "构建",
        ]
        action_count = sum(1 for word in action_words if word in user_request)

        # 如果有多于2个动作词，或有多个复杂性关键词，或匹配复杂任务模式，则认为是复杂任务  # noqa: E501
        return (complexity_count >= 2) or (action_count >= 2) or pattern_match

    async def _detect_by_model(self, user_request: str) -> bool:
        """基于大模型检测复杂任务"""
        try:
            prompt = f"""请判断以下用户请求是否属于复杂任务，需要分解为多个子步骤来完成。

用户请求：{user_request}

复杂任务的特点：
- 需要多个步骤才能完成
- 涉及多个方面或领域
- 需要详细分析或深入研究
- 涉及系统性工作
- 包含多项具体要求

如果是复杂任务请回复 "COMPLEX"，如果是简单任务请回复 "SIMPLE"。

回复格式：COMPLEX 或 SIMPLE"""  # noqa: E501

            response = await self.model_provider.generate(prompt)
            response_text = str(response) if isinstance(response, dict) else response

            return "COMPLEX" in response_text.upper() or "复杂" in response_text

        except Exception:
            # 如果模型调用失败，回退到规则检测
            return await self._detect_by_rules(user_request)


class TaskDecomposer:
    """任务分解器 - 将复杂任务分解为子任务"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider

    async def decompose_task(self, user_request: str) -> list[TaskItem]:
        """将复杂任务分解为多个子任务"""

        if self.model_provider:
            # 使用大模型进行智能分解
            return await self._decompose_with_model(user_request)
        else:
            # 使用基于规则的分解（简化版）
            return self._decompose_with_rules(user_request)

    async def _decompose_with_model(self, user_request: str) -> list[TaskItem]:
        """使用大模型分解任务"""
        prompt = f"""请将以下任务分解为3-8个具体的、可执行的子任务。

任务：{user_request}

请按照以下JSON格式返回结果：
{{
    "tasks": [
        {{
            "title": "任务标题",
            "description": "任务详细描述",
            "priority": 数字(1-5, 5最高)
        }}
    ]
}}

要求：
1. 每个子任务应该是具体的、可执行的
2. 任务之间应该有逻辑顺序
3. 标题简洁明了
4. 描述详细具体
5. 优先级按重要性排序"""

        try:
            response = await self.model_provider.generate(prompt)
            response_text = str(response) if isinstance(response, dict) else response

            # 解析JSON响应
            import json

            try:
                parsed = json.loads(response_text)
                tasks_data = parsed.get("tasks", [])
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试其他格式
                import re

                matches = re.findall(r"(\d+)\.\s*([^:\n]+):\s*([^\n]+)", response_text)
                tasks_data = []
                for idx, title, desc in matches:
                    tasks_data.append(
                        {
                            "title": title.strip(),
                            "description": desc.strip(),
                            "priority": 3,
                        }
                    )

            tasks = []
            for task_data in tasks_data:
                task = TaskItem(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    title=task_data.get("title", "未命名任务"),
                    description=task_data.get("description", ""),
                    priority=task_data.get("priority", 3),
                )
                tasks.append(task)

            return tasks

        except Exception:
            return self._decompose_with_rules(user_request)

    def _decompose_with_rules(self, user_request: str) -> list[TaskItem]:
        """使用规则分解任务（简化版）"""
        tasks = []

        # 根据任务类型生成通用的分解步骤
        if any(
            word in user_request.lower()
            for word in ["分析", "research", "study", "investigate"]
        ):
            steps = [
                ("信息收集", "收集与主题相关的背景信息和数据", 4),
                ("现状分析", "分析当前状况和存在的问题", 5),
                ("深入研究", "对关键问题进行深入研究", 4),
                ("总结归纳", "总结研究成果并提出见解", 3),
            ]
        elif any(
            word in user_request.lower()
            for word in ["设计", "design", "develop", "create"]
        ):
            steps = [
                ("需求分析", "明确设计或开发的具体需求", 5),
                ("方案设计", "设计实施方案或架构", 4),
                ("实现执行", "执行设计方案", 5),
                ("验证测试", "验证实现结果", 4),
            ]
        elif any(
            word in user_request.lower()
            for word in ["比较", "compare", "evaluate", "assess"]
        ):
            steps = [
                ("标准制定", "确定比较或评估的标准", 4),
                ("信息收集", "收集各选项的相关信息", 4),
                ("对比分析", "进行详细的对比分析", 5),
                ("结论总结", "总结比较结果和建议", 4),
            ]
        else:
            # 通用分解
            steps = [
                ("任务理解", "深入理解任务的具体要求", 5),
                ("信息准备", "准备执行任务所需的信息", 4),
                ("执行过程", "执行任务的主要过程", 5),
                ("结果整理", "整理和总结执行结果", 3),
            ]

        for title, description, priority in steps:
            task = TaskItem(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title=title,
                description=f"{user_request} -> {description}",
                priority=priority,
            )
            tasks.append(task)

        return tasks


class TaskExecutionCoordinator:
    """任务执行协调器 - 按清单顺序执行任务"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.current_task_index = 0
        self.execution_context = {}  # 任务间共享上下文

    async def execute_task_list(
        self, task_list_manager: TaskListManager, original_request: str
    ) -> AsyncGenerator[AgentEvent, None]:
        """执行任务清单中的所有任务"""

        # 发送初始任务清单给用户
        task_list_display = task_list_manager.generate_task_list_display()
        yield ThoughtEvent(content=task_list_display)

        # 顺序执行每个任务
        for i, task in enumerate(task_list_manager.tasks):
            # 更新任务状态为进行中
            await task_list_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)

            # 发送状态更新
            updated_display = task_list_manager.generate_task_list_display()
            yield ThoughtEvent(
                content=f"🔄 **正在执行任务 {i + 1}/{len(task_list_manager.tasks)}: {task.title}**\n\n{updated_display}"  # noqa: E501
            )

            try:
                # 执行单个任务
                result = await self._execute_single_task(
                    task, original_request, task_list_manager
                )

                # 更新任务状态为完成
                await task_list_manager.update_task_status(
                    task.id, TaskStatus.COMPLETED, result=result
                )

            except Exception as e:
                # 更新任务状态为失败
                error_msg = str(e)
                await task_list_manager.update_task_status(
                    task.id, TaskStatus.FAILED, error=error_msg
                )

                # 发送错误信息
                yield ThoughtEvent(
                    content=f"❌ **任务执行失败**: {task.title}\n错误: {error_msg}"
                )

            # 发送更新后的任务清单
            updated_display = task_list_manager.generate_task_list_display()
            yield ThoughtEvent(content=updated_display)

        # 所有任务执行完成后，生成总结
        yield ThoughtEvent(content="🎉 **所有任务执行完成！**\n\n正在生成最终总结...")

        final_summary = await self._generate_final_summary(
            task_list_manager, original_request
        )
        yield ThoughtEvent(content=final_summary)

    async def _execute_single_task(
        self, task: TaskItem, original_request: str, task_list_manager: TaskListManager
    ) -> str:
        """执行单个任务"""
        if self.model_provider:
            # 构建上下文
            context_str = self._build_context_string(task_list_manager)

            prompt = f"""请执行以下子任务：

原请求: {original_request}

当前子任务: {task.title}
任务描述: {task.description}

上下文信息: {context_str}

请专注完成当前子任务，并提供具体的结果或答案。"""

            response = await self.model_provider.generate(prompt)
            result = str(response) if isinstance(response, dict) else response

            return result
        else:
            # 模拟执行
            return f"模拟执行结果: {task.title} - 已完成"

    def _build_context_string(self, task_list_manager: TaskListManager) -> str:
        """构建任务执行上下文"""
        completed_tasks = [
            t for t in task_list_manager.tasks if t.status == TaskStatus.COMPLETED
        ]

        if not completed_tasks:
            return "暂无前置任务完成"

        context_parts = []
        for task in completed_tasks[-3:]:  # 只取最后3个已完成的任务
            result_preview = (
                task.result[:100]
                if task.result and len(task.result) > 100
                else (task.result or "无结果")
            )
            context_parts.append(f"已完成: {task.title} -> {result_preview}")

        return "; ".join(context_parts)

    async def _generate_final_summary(
        self, task_list_manager: TaskListManager, original_request: str
    ) -> str:
        """生成最终总结"""
        if self.model_provider:
            completed_results = []
            for task in task_list_manager.tasks:
                if task.status == TaskStatus.COMPLETED and task.result:
                    completed_results.append(f"- {task.title}: {task.result[:200]}...")

            results_summary = (
                "\n".join(completed_results)
                if completed_results
                else "无完成的任务结果"
            )

            prompt = f"""请根据以下任务执行结果，生成对原始请求的最终总结。

原始请求: {original_request}

任务执行结果:
{results_summary}

请提供一个完整、连贯的总结回答。"""

            response = await self.model_provider.generate(prompt)
            return f"### 最终总结\n\n{str(response) if isinstance(response, dict) else response}"  # noqa: E501
        else:
            # 简单总结
            progress = await task_list_manager.get_progress()
            return f"### 任务完成总结\n\n- 原始请求: {original_request[:100]}...\n- 总任务数: {progress['total']}\n- 完成任务: {progress['completed']}\n- 失败任务: {progress['failed']}\n\n执行完成。"  # noqa: E501


class AutoTaskDecompositionEngine:
    """
    自动任务分解引擎
    检测复杂任务 -> 生成任务清单 -> 顺序执行 -> 状态更新
    """

    def __init__(self, model_provider=None):
        self.complexity_detector = ComplexityDetector(model_provider)
        self.task_decomposer = TaskDecomposer(model_provider)
        self.task_execution_coordinator = TaskExecutionCoordinator(model_provider)
        self.task_list_manager = TaskListManager()

    async def should_process_with_task_decomposition(self, user_request: str) -> bool:
        """判断是否应该使用任务分解处理"""
        return await self.complexity_detector.is_complex_task(user_request)

    async def process_with_task_decomposition(
        self, user_request: str
    ) -> AsyncGenerator[AgentEvent, None]:
        """使用任务分解处理复杂请求"""

        # 1. 分解任务
        tasks = await self.task_decomposer.decompose_task(user_request)

        # 2. 创建任务清单
        self.task_list_manager = TaskListManager()  # 重新创建
        for task in tasks:
            await self.task_list_manager.add_task(
                task.title, task.description, task.priority
            )

        # 3. 执行任务清单
        async for event in self.task_execution_coordinator.execute_task_list(
            self.task_list_manager, user_request
        ):
            yield event


# 测试
async def test_task_decomposition_engine():
    """测试任务分解引擎"""

    # 创建模拟模型提供者
    class MockModelProvider:
        async def generate(self, prompt: str):
            if "分解为3-8个具体的、可执行的子任务" in prompt:
                if "分析" in prompt:
                    return """{
    "tasks": [
        {
            "title": "信息收集",
            "description": "收集人工智能医疗应用的现状、技术特点和主要厂商信息",
            "priority": 4
        },
        {
            "title": "前景分析",
            "description": "分析AI在医疗领域的应用前景和市场潜力",
            "priority": 5
        },
        {
            "title": "挑战识别",
            "description": "识别AI在医疗领域面临的主要挑战和障碍",
            "priority": 4
        },
        {
            "title": "建议提出",
            "description": "基于分析结果提出发展建议和解决方案",
            "priority": 3
        }
    ]
}"""
                elif "设计" in prompt:
                    return """{
    "tasks": [
        {
            "title": "需求分析",
            "description": "明确客户服务平台的功能需求和技术要求",
            "priority": 5
        },
        {
            "title": "架构设计",
            "description": "设计平台的整体架构和技术栈选择",
            "priority": 4
        },
        {
            "title": "功能开发",
            "description": "开发核心功能模块",
            "priority": 5
        }
    ]
}"""
                else:
                    return """{
    "tasks": [
        {
            "title": "信息搜集",
            "description": "搜集相关信息和数据",
            "priority": 4
        },
        {
            "title": "分析处理",
            "description": "对信息进行分析处理",
            "priority": 5
        },
        {
            "title": "总结报告",
            "description": "生成分析总结报告",
            "priority": 3
        }
    ]
}"""
            elif "请执行以下子任务" in prompt:
                import re

                # 从提示中提取任务标题
                title_match = re.search(r"当前子任务:\s*(.+?)\n", prompt)
                task_title = title_match.group(1) if title_match else "未知任务"
                return f"完成任务: {task_title} - 这是详细执行结果..."
            elif "生成对原始请求的最终总结" in prompt:
                return "根据各项任务的执行结果，已完成了对原始请求的全面分析和处理。各项子任务均已按计划完成，达到了预期目标。"  # noqa: E501
            else:
                return f"执行结果：{prompt[:100]}..."

    # 创建引擎
    engine = AutoTaskDecompositionEngine(MockModelProvider())

    # 测试复杂任务
    test_requests = [
        "请帮我深入分析人工智能在医疗领域的应用前景、挑战和机遇",
        "设计一个AI驱动的智能客户服务系统",
        "比较三种主流深度学习框架的性能特点",
    ]

    for request in test_requests:
        # 检查是否需要任务分解
        should_decompose = await engine.should_process_with_task_decomposition(request)

        if should_decompose:
            # 模拟执行
            events = []
            async for event in engine.process_with_task_decomposition(request):
                events.append(event)
                if hasattr(event, "content"):
                    if "📋 **任务清单**" in str(
                        event.content
                    ) or "🔄 **正在执行任务" in str(event.content):
                        pass
                    elif "🎉 **所有任务执行完成**" in str(event.content):
                        pass


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_task_decomposition_engine())
