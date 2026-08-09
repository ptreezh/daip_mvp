"""
敏捷任务分解系统核心实现
包含任务分解、执行、记忆管理等功能
"""

import json
import re
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class TaskStatus(Enum):
    """任务状态枚举"""

    BACKLOG = "backlog"  # 待办
    READY = "ready"  # 准备就绪
    IN_PROGRESS = "in_progress"  # 进行中
    TESTING = "testing"  # 测试中
    DONE = "done"  # 已完成
    BLOCKED = "blocked"  # 已阻塞
    CANCELLED = "cancelled"  # 已取消


@dataclass
class AgileTask:
    """敏捷任务项"""

    id: str
    title: str
    description: str
    status: str = TaskStatus.BACKLOG.value
    priority: int = 3  # 1-5, 5最高
    assignee: Optional[str] = None
    sprint_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: list[str] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Sprint:
    """冲刺/迭代"""

    id: str
    name: str
    goal: str
    tasks: list[AgileTask] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "planning"  # planning, active, completed, cancelled


class AgileTaskMemory:
    """敏捷任务记忆系统 - 持久化存储和状态追踪"""

    def __init__(self, storage_path: str = "./agile_projects"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sessions_path = self.storage_path / "sprints"
        self.sessions_path.mkdir(exist_ok=True)
        self.documents_path = self.storage_path / "documents"
        self.documents_path.mkdir(exist_ok=True)
        self.history_path = self.storage_path / "history"
        self.history_path.mkdir(exist_ok=True)

    def save_sprint(self, sprint: Sprint) -> str:
        """保存冲刺到持久化存储"""
        sprint_file = self.sessions_path / f"{sprint.id}.json"

        sprint_data = {
            "id": sprint.id,
            "name": sprint.name,
            "goal": sprint.goal,
            "created_at": sprint.created_at.isoformat()
            if isinstance(sprint.created_at, datetime)
            else sprint.created_at,
            "started_at": sprint.started_at.isoformat() if sprint.started_at else None,
            "completed_at": sprint.completed_at.isoformat()
            if sprint.completed_at
            else None,
            "status": sprint.status,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "assignee": task.assignee,
                    "sprint_id": task.sprint_id,
                    "created_at": task.created_at.isoformat()
                    if isinstance(task.created_at, datetime)
                    else task.created_at,
                    "started_at": task.started_at.isoformat()
                    if task.started_at
                    else None,
                    "completed_at": task.completed_at.isoformat()
                    if task.completed_at
                    else None,
                    "dependencies": task.dependencies,
                    "result": task.result,
                    "error": task.error,
                    "metadata": task.metadata,
                }
                for task in sprint.tasks
            ],
        }

        with open(sprint_file, "w", encoding="utf-8") as f:
            json.dump(sprint_data, f, ensure_ascii=False, indent=2)

        return str(sprint_file)

    def load_sprint(self, sprint_id: str) -> Optional[Sprint]:
        """从持久化存储加载冲刺"""
        sprint_file = self.sessions_path / f"{sprint_id}.json"

        if not sprint_file.exists():
            return None

        try:
            with open(sprint_file, encoding="utf-8") as f:
                sprint_data = json.load(f)

            tasks = []
            for task_data in sprint_data.get("tasks", []):
                task = AgileTask(
                    id=task_data["id"],
                    title=task_data["title"],
                    description=task_data["description"],
                    status=task_data["status"],
                    priority=task_data["priority"],
                    assignee=task_data["assignee"],
                    sprint_id=task_data["sprint_id"],
                    created_at=datetime.fromisoformat(task_data["created_at"]),
                    started_at=datetime.fromisoformat(task_data["started_at"])
                    if task_data["started_at"]
                    else None,
                    completed_at=datetime.fromisoformat(task_data["completed_at"])
                    if task_data["completed_at"]
                    else None,
                    dependencies=task_data["dependencies"],
                    result=task_data["result"],
                    error=task_data["error"],
                    metadata=task_data["metadata"],
                )
                tasks.append(task)

            sprint = Sprint(
                id=sprint_data["id"],
                name=sprint_data["name"],
                goal=sprint_data["goal"],
                tasks=tasks,
                created_at=datetime.fromisoformat(sprint_data["created_at"]),
                started_at=datetime.fromisoformat(sprint_data["started_at"])
                if sprint_data["started_at"]
                else None,
                completed_at=datetime.fromisoformat(sprint_data["completed_at"])
                if sprint_data["completed_at"]
                else None,
                status=sprint_data["status"],
            )

            return sprint

        except Exception:
            return None

    def save_intermediate_document(self, document_name: str, content: str) -> str:
        """保存中间文档"""
        doc_file = (
            self.documents_path
            / f"{document_name.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.md"
        )

        with open(doc_file, "w", encoding="utf-8") as f:
            f.write(f"# 中间文档: {document_name}\n")
            f.write(f"生成时间: {datetime.now().isoformat()}\n\n")
            f.write(f"## 内容:\n{content}")

        return str(doc_file)

    def save_execution_history(
        self, session_id: str, history: list[dict[str, Any]]
    ) -> str:
        """保存执行历史"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.history_path / f"history_{session_id}_{timestamp}.json"

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2, default=str)

        return str(history_file)

    def get_latest_sprint_for_goal(self, goal: str) -> Optional[Sprint]:
        """获取指定目标的最新会话"""
        # 搜索与目标相似的sprint文件
        matching_files = []
        for file in self.sessions_path.glob("*.json"):
            try:
                with open(file, encoding="utf-8") as f:
                    data = json.load(f)
                    # 检查是否与目标匹配（简单的文本匹配）
                    if (
                        goal.lower() in data["goal"].lower()
                        or goal.lower() in data["name"].lower()
                    ):
                        matching_files.append((file, data["created_at"]))
            except Exception:
                continue

        if matching_files:
            # 按创建时间排序，返回最新的
            latest_file = max(matching_files, key=lambda x: x[1])[0]
            sprint_id = latest_file.name.replace(".json", "")
            return self.load_sprint(sprint_id)

        return None


class TaskDecomposer:
    """任务分解引擎"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        # 复杂任务关键词
        self.complexity_keywords = [
            # 动词类
            "分析",
            "研究",
            "调查",
            "评估",
            "比较",
            "设计",
            "构建",
            "开发",
            "创建",
            "实现",
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
            "执行",
            "解决",
            # 形容词类
            "复杂",
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
            "广泛",
            "长远",
            "持续",
            "多阶段",
            "多步骤",
            "多环节",
        ]

        # 复杂任务模式
        self.complexity_patterns = [
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
        for pattern in self.complexity_patterns:
            if re.search(pattern, user_lower, re.IGNORECASE):
                return True

        # 检查复杂性关键词数量
        keyword_count = sum(
            1 for keyword in self.complexity_keywords if keyword in user_lower
        )

        # 检查长度和动作词数量
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

        # 如果多个复杂关键词 或 多个动作词 或 句子长度较长且包含动作词，则为复杂任务
        return (
            (keyword_count >= 2)
            or (action_count >= 2)
            or (word_count > 10 and action_count >= 1)
        )

    async def decompose_task(self, original_goal: str) -> Sprint:
        """将复杂任务分解为Sprint和Tasks"""
        sprint_id = f"sprint_{uuid.uuid4().hex[:8]}"
        sprint_name = f"分解任务: {original_goal[:30]}..."

        if self.model_provider:
            # 使用大模型进行智能分解
            prompt = f"""请将以下复杂目标分解为敏捷开发中的冲刺任务。

目标: {original_goal}

请按照敏捷开发方式，将其分解为3-8个具体可执行的任务。
每个任务应包含:
- 标题: 简洁的任务标题
- 描述: 详细的任务描述
- 优先级: 1-5的优先级（5最高）

请返回JSON格式:
{{
    "sprint_name": "冲刺名称",
    "sprint_goal": "冲刺目标",
    "tasks": [
        {{
            "title": "任务标题",
            "description": "任务详细描述",
            "priority": 优先级数值
        }}
    ]
}}"""

            try:
                response = await self.model_provider.generate(prompt)
                response_text = (
                    str(response) if isinstance(response, dict) else response
                )

                parsed = json.loads(response_text)

                sprint = Sprint(
                    id=sprint_id,
                    name=parsed.get("sprint_name", sprint_name),
                    goal=parsed.get("sprint_goal", original_goal),
                )

                for task_data in parsed.get("tasks", []):
                    task = AgileTask(
                        id=f"task_{uuid.uuid4().hex[:8]}",
                        title=task_data.get("title", "未命名任务"),
                        description=task_data.get("description", ""),
                        priority=task_data.get("priority", 3),
                        status=TaskStatus.BACKLOG.value,
                    )
                    sprint.tasks.append(task)

                if not sprint.tasks:  # 如果AI分解失败，使用规则分解
                    sprint = self._decompose_by_rules(
                        original_goal, sprint_id, sprint_name
                    )

                return sprint

            except Exception:
                pass

        # 使用规则分解（备份方案）
        return self._decompose_by_rules(original_goal, sprint_id, sprint_name)

    def _decompose_by_rules(
        self, original_goal: str, sprint_id: str, sprint_name: str
    ) -> Sprint:
        """基于规则的任务分解"""
        sprint = Sprint(id=sprint_id, name=sprint_name, goal=original_goal)

        # 根据任务类型进行智能分解
        goal_lower = original_goal.lower()

        if any(word in goal_lower for word in ["分析", "研究", "探讨", "调查"]):
            # 分析类任务
            steps = [
                ("信息收集", "收集与分析目标相关的背景信息和数据", 4),
                ("现状分析", "分析当前状况和主要问题", 5),
                ("深入研究", "对关键问题进行深入研究", 5),
                ("结果汇总", "汇总研究结果并提出建议", 3),
            ]
        elif any(word in goal_lower for word in ["设计", "构建", "开发", "创建"]):
            # 设计/开发类任务
            steps = [
                ("需求分析", "明确设计或开发的具体需求", 5),
                ("方案设计", "设计具体的实施方案", 4),
                ("实现执行", "执行设计方案", 5),
                ("验证测试", "验证实现结果", 4),
            ]
        elif any(word in goal_lower for word in ["比较", "评估", "对比"]):
            # 比较评估类任务
            steps = [
                ("标准制定", "确定比较或评估的标准", 4),
                ("信息收集", "收集各选项的相关信息", 4),
                ("对比分析", "进行详细的对比分析", 5),
                ("结论总结", "总结比较结果和建议", 3),
            ]
        else:
            # 通用分解
            steps = [
                ("理解任务", "深入理解任务的具体要求", 5),
                ("准备阶段", "准备执行任务所需的资源", 4),
                ("执行过程", "执行任务的主要过程", 5),
                ("结果整理", "整理和总结执行结果", 3),
            ]

        for title, description, priority in steps:
            task = AgileTask(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title=title,
                description=f"{original_goal} -> {description}",
                priority=priority,
                status=TaskStatus.BACKLOG.value,
            )
            sprint.tasks.append(task)

        return sprint


class TaskExecutor:
    """任务执行器"""

    def __init__(self, model_provider=None, skill_manager=None):
        self.model_provider = model_provider
        self.skill_manager = skill_manager

    async def execute_task(
        self,
        task: AgileTask,
        original_goal: str,
        previous_results: list[dict[str, Any]],
        task_memory: AgileTaskMemory,
    ) -> str:
        """执行单个任务"""
        if self.model_provider:
            # 构建任务上下文（包含前期结果）
            context_parts = []
            for prev_result in previous_results[-3:]:  # 只取最后3个结果
                context_parts.append(
                    f"已完成任务: {prev_result.get('task_title', '')} - 结果: {prev_result.get('result', '')[:200]}..."  # noqa: E501
                )

            context_str = (
                "\\n".join(context_parts) if context_parts else "无前置任务结果"
            )

            prompt = f"""请完成以下子任务:

原始目标: {original_goal}

当前任务: {task.title}
任务描述: {task.description}

上下文信息:
{context_str}

请专注完成当前任务，并提供具体、详细的执行结果。"""

            try:
                response = await self.model_provider.generate(prompt)
                result = str(response) if isinstance(response, dict) else response

                # 保存中间文档
                doc_name = f"{task.title.replace(' ', '_')}_{task.id[:8]}"
                task_memory.save_intermediate_document(doc_name, result)

                return result
            except Exception as e:
                error_result = f"任务执行失败: {str(e)}"

                # 保存错误文档
                doc_name = f"error_{task.title.replace(' ', '_')}_{task.id[:8]}"
                task_memory.save_intermediate_document(doc_name, error_result)

                return error_result
        else:
            # 模拟执行
            result = f"模拟执行结果: {task.title} - 已完成"

            # 模拟保存中间文档
            doc_name = f"{task.title.replace(' ', '_')}_{task.id[:8]}"
            task_memory.save_intermediate_document(doc_name, result)

            return result


class SprintExecutor:
    """冲刺执行器"""

    def __init__(self, model_provider=None, skill_manager=None):
        self.model_provider = model_provider
        self.skill_manager = skill_manager
        self.executor = TaskExecutor(model_provider, skill_manager)
        self.task_memory = AgileTaskMemory()
        self.execution_history: list[dict[str, Any]] = []

    async def execute_sprint(self, sprint: Sprint) -> dict[str, Any]:
        """执行整个冲刺"""
        sprint.started_at = datetime.now()
        sprint.status = "active"

        execution_results = []
        previous_results = []

        for i, task in enumerate(sprint.tasks):
            # 更新任务状态
            task.status = TaskStatus.IN_PROGRESS.value
            task.started_at = datetime.now()

            # 执行任务
            result = await self.executor.execute_task(
                task, sprint.goal, previous_results, self.task_memory
            )

            # 更新任务状态
            task.result = result
            task.status = TaskStatus.DONE.value
            task.completed_at = datetime.now()

            # 记录执行历史
            task_result = {
                "task_id": task.id,
                "task_title": task.title,
                "task_description": task.description,
                "result": result,
                "status": task.status,
                "execution_order": i,
                "executed_at": datetime.now().isoformat(),
            }
            execution_results.append(task_result)
            previous_results.append(task_result)

            # 保存当前进度
            self.task_memory.save_sprint(sprint)

            # 记录历史
            self.execution_history.append(task_result)

        sprint.completed_at = datetime.now()
        sprint.status = "completed"

        # 保存最终冲刺状态
        sprint_file = self.task_memory.save_sprint(sprint)

        # 保存执行历史
        history_file = self.task_memory.save_execution_history(
            sprint.id, self.execution_history
        )

        # 合成最终结果
        final_result = await self._synthesize_final_result(sprint, execution_results)

        return {
            "sprint_id": sprint.id,
            "original_goal": sprint.goal,
            "total_tasks": len(sprint.tasks),
            "completed_tasks": len(
                [t for t in sprint.tasks if t.status == TaskStatus.DONE.value]
            ),
            "execution_results": execution_results,
            "final_result": final_result,
            "sprint_summary_file": sprint_file,
            "history_file": history_file,
        }

    async def _synthesize_final_result(
        self, sprint: Sprint, execution_results: list[dict[str, Any]]
    ) -> str:
        """合成最终结果"""
        if not execution_results:
            return f"没有执行任何任务。原始目标: {sprint.goal}"

        if self.model_provider:
            # 构造任务执行摘要
            task_summaries = []
            for result in execution_results:
                summary = f"任务: {result['task_title']}"
                result_preview = (
                    result["result"][:300] if result["result"] else "无结果"
                )  # 截取前300字符
                task_summaries.append(
                    f"{summary}\\n结果: {result_preview}{'...' if len(result['result']) > 300 else ''}"  # noqa: E501
                )

            summaries_block = "\n\n".join(task_summaries)
            prompt = f"""请根据以下子任务执行结果，生成对原始目标的完整回答。

原始目标: {sprint.goal}

子任务执行结果摘要:
{summaries_block}

请提供一个完整、连贯、结构化的最终回答。"""

            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception:
                pass

        # 规则合成（备选）
        results_text = []
        for result in execution_results:
            results_text.append(
                f"## {result['task_title']}\\n{result['result'] or '无结果'}\\n"
            )

        return f"# {sprint.goal}\\n\\n## 执行结果摘要\\n\\n" + "\\n".join(results_text)


class AgileTaskSystemCore:
    """敏捷任务系统核心实现"""

    def __init__(self, model_provider=None, skill_manager=None):
        self.model_provider = model_provider
        self.skill_manager = skill_manager
        self.decomposer = TaskDecomposer(model_provider)
        self.executor = SprintExecutor(model_provider, skill_manager)
        self.complexity_detector = self.decomposer  # 重用复杂性检测逻辑

    async def should_decompose_request(self, user_request: str) -> bool:
        """判断请求是否需要任务分解"""
        return await self.complexity_detector.should_decompose_task(user_request)

    async def process_request(self, user_request: str) -> AsyncGenerator[str, None]:
        """处理用户请求 - 完整的敏捷流程"""

        # 检查是否已有相关会话
        existing_sprint = self.executor.task_memory.get_latest_sprint_for_goal(
            user_request
        )

        if existing_sprint and existing_sprint.status != "completed":
            # 继续之前的会话
            yield f"[YELLOW]🔄 检测到进行中的相关任务: {existing_sprint.name}[/YELLOW]"

            # 计算进度
            total_tasks = len(existing_sprint.tasks)
            completed_tasks = len(
                [t for t in existing_sprint.tasks if t.status == TaskStatus.DONE.value]
            )

            yield f"[BLUE]📋 当前进度: {completed_tasks}/{total_tasks} 任务完成[/BLUE]"

            # 继续执行未完成的任务
            incomplete_tasks = [
                task
                for task in existing_sprint.tasks
                if task.status != TaskStatus.DONE.value
            ]

            if incomplete_tasks:
                yield f"[BLUE]🚀 继续执行 {len(incomplete_tasks)} 个未完成任务...[/BLUE]"  # noqa: E501

                for i, task in enumerate(incomplete_tasks, 1):
                    task.status = TaskStatus.IN_PROGRESS.value
                    task.started_at = datetime.now()

                    yield f"[CYAN]🔄 执行任务 {i}/{len(incomplete_tasks)}: {task.title}[/CYAN]"  # noqa: E501

                    # 执行任务
                    result = await self.executor.executor.execute_task(
                        task, existing_sprint.goal, [], self.executor.task_memory
                    )

                    task.result = result
                    task.status = TaskStatus.DONE.value
                    task.completed_at = datetime.now()

                    yield f"[GREEN]✅ 任务完成: {task.title}[/GREEN]"

                    # 保存更新
                    self.executor.task_memory.save_sprint(existing_sprint)

                # 合成最终结果
                completed_tasks_data = [
                    {"task_title": t.title, "result": t.result}
                    for t in existing_sprint.tasks
                    if t.status == TaskStatus.DONE.value
                ]

                final_result = await self.executor._synthesize_final_result(
                    existing_sprint, completed_tasks_data
                )

                yield f"\\n[FINAL]🎉 任务完成!\\n{final_result}"
            else:
                # 所有任务已完成
                final_task = (
                    existing_sprint.tasks[-1] if existing_sprint.tasks else None
                )
                yield f"[INFO] 所有相关任务已完成。最终结果:\\n{final_task.result if final_task and final_task.result else '无结果'}"  # noqa: E501
        else:
            # 创建新会话
            yield f"[INFO] 🆕 开始新任务分解流程: {user_request[:50]}..."

            # 1. 分解任务
            sprint = await self.decomposer.decompose_task(user_request)
            yield f"[INFO] 📋 任务分解完成，生成 {len(sprint.tasks)} 个敏捷任务"

            # 显示任务清单
            task_list_display = self._generate_task_list_display(sprint.tasks)
            yield f"\\n[INFO] **敏捷任务清单**:\\n{task_list_display}"

            # 2. 执行任务
            yield "[INFO] 🚀 开始顺序执行任务列表..."

            # 执行冲刺并生成进度更新
            async for event in self._execute_sprint_with_updates(sprint):
                yield event

    async def _execute_sprint_with_updates(
        self, sprint: Sprint
    ) -> AsyncGenerator[str, None]:
        """执行冲刺并生成进度更新事件"""
        sprint.started_at = datetime.now()
        sprint.status = "active"

        execution_results = []
        previous_results = []

        for i, task in enumerate(sprint.tasks):
            # 更新任务状态为进行中
            task.status = TaskStatus.IN_PROGRESS.value
            task.started_at = datetime.now()

            # 发送进度更新
            task_progress = self._generate_task_list_display(sprint.tasks)
            yield f"\\n[PROGRESS] 🔄 **正在执行任务 {i + 1}/{len(sprint.tasks)}: {task.title}**\\n\\n{task_progress}"  # noqa: E501

            # 执行任务
            result = await self.executor.executor.execute_task(
                task, sprint.goal, previous_results, self.executor.task_memory
            )

            # 更新任务状态
            task.result = result
            task.status = TaskStatus.DONE.value
            task.completed_at = datetime.now()

            # 记录结果
            task_result = {
                "task_id": task.id,
                "task_title": task.title,
                "task_description": task.description,
                "result": result,
                "status": task.status,
                "execution_order": i,
                "executed_at": datetime.now().isoformat(),
            }
            execution_results.append(task_result)
            previous_results.append(task_result)

            # 保存当前进度
            self.executor.task_memory.save_sprint(sprint)

            # 发送完成通知
            completed_progress = self._generate_task_list_display(sprint.tasks)
            yield f"\\n[COMPLETE] ✅ **任务完成**: {task.title}\\n\\n{completed_progress}"  # noqa: E501

        sprint.completed_at = datetime.now()
        sprint.status = "completed"

        # 保存最终状态
        sprint_file = self.executor.task_memory.save_sprint(sprint)

        # 合成最终结果
        yield "[INFO] 🎯 **开始合成功能** - 整合所有子任务结果..."

        final_result = await self.executor._synthesize_final_result(
            sprint, execution_results
        )
        yield f"\\n[FINAL] 🎉 **最终结果**:\\n{final_result}"

        yield f"\\n[SAVED] 💾 任务记录已保存到: {sprint_file}"

    def _generate_task_list_display(self, tasks: list[AgileTask]) -> str:
        """生成任务清单的显示文本"""
        if not tasks:
            return "当前没有任务清单"

        display = ""
        status_emojis = {
            TaskStatus.BACKLOG.value: "📋",
            TaskStatus.READY.value: "✅",
            TaskStatus.IN_PROGRESS.value: "🔄",
            TaskStatus.TESTING.value: "🔍",
            TaskStatus.DONE.value: "🎉",
            TaskStatus.BLOCKED.value: "🚫",
            TaskStatus.CANCELLED.value: "❌",
        }

        for i, task in enumerate(tasks, 1):
            emoji = status_emojis.get(task.status, "❓")
            status_text = {
                TaskStatus.BACKLOG.value: "待办",
                TaskStatus.READY.value: "待执行",
                TaskStatus.IN_PROGRESS.value: "执行中",
                TaskStatus.TESTING.value: "测试中",
                TaskStatus.DONE.value: "已完成",
                TaskStatus.BLOCKED.value: "已阻塞",
                TaskStatus.CANCELLED.value: "已取消",
            }.get(task.status, "未知")

            display += f"{i}. {emoji} **{task.title}** ({status_text})\\n"
            display += f"   - {task.description}\\n"
            if task.result:
                result_preview = (
                    task.result[:100] if len(task.result) > 100 else task.result
                )
                display += f"   - 结果: {result_preview}...\\n"
            if task.error:
                display += f"   - 错误: {task.error}\\n"
            display += "\\n"

        # 添加进度统计
        total = len(tasks)
        completed = len([t for t in tasks if t.status == TaskStatus.DONE.value])
        in_progress = len(
            [t for t in tasks if t.status == TaskStatus.IN_PROGRESS.value]
        )
        pending = len(
            [
                t
                for t in tasks
                if t.status in [TaskStatus.BACKLOG.value, TaskStatus.READY.value]
            ]
        )
        blocked = len([t for t in tasks if t.status == TaskStatus.BLOCKED.value])

        display += f"📈 **进度统计**: 总计 {total} | 已完成 {completed} | 进行中 {in_progress} | 待办 {pending} | 阻塞 {blocked}\\n"  # noqa: E501

        return display
