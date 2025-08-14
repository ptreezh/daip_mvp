"""Personal Intelligence Hub - Task Panel Component

任务管理面板组件
"""

from datetime import datetime
from typing import List

from lona import Component
from lona.html import H3, H4, HTML, Button, Div, Option, P, Select, TextInput

from personal_intelligence_hub.models.task_models import (
    Task,
    TaskDecompositionNode,
    TaskPriority,
    TaskStatus,
)


class TaskPanel(Component):
    """任务面板组件"""

    def __init__(self):
        self.tasks: List[Task] = []
        self.selected_project = None
        self.task_decompositions: List[TaskDecompositionNode] = []

        # 创建UI元素
        self.refresh_button = Button("刷新任务", _class="task-refresh-button")
        self.refresh_button.onclick = self.handle_refresh

        # 创建任务表单元素
        self.new_task_input = TextInput(placeholder="新任务标题...", _class="new-task-input")
        self.add_task_button = Button("添加任务", _class="add-task-button")
        self.add_task_button.onclick = self.handle_add_task

    async def handle_refresh(self, event=None):
        """处理刷新任务"""
        # 模拟任务数据
        await self.load_sample_tasks()
        await self.refresh()

    async def load_sample_tasks(self):
        """加载示例任务数据"""
        self.tasks = [
            Task(
                id="task1",
                title="分析用户需求",
                description="收集和分析用户反馈，理解核心需求",
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                parent_id=None,
                assigned_agent="Analyst-AI",
                dependencies=[],
                subtasks=["task3", "task4"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=None,
                estimated_hours=4.0,
                actual_hours=2.5,
                progress=0.6,
                metadata={"type": "analysis", "source": "user_input"}
            ),
            Task(
                id="task2",
                title="设计解决方案",
                description="基于需求分析设计技术方案",
                status=TaskStatus.NOT_STARTED,
                priority=TaskPriority.MEDIUM,
                parent_id=None,
                assigned_agent="Designer-AI",
                dependencies=["task1"],
                subtasks=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=None,
                estimated_hours=6.0,
                actual_hours=0.0,
                progress=0.0,
                metadata={"type": "design", "source": "system"}
            ),
            Task(
                id="task3",
                title="收集用户反馈",
                description="通过问卷和访谈收集用户反馈",
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.HIGH,
                parent_id="task1",
                assigned_agent="Research-AI",
                dependencies=[],
                subtasks=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=None,
                estimated_hours=2.0,
                actual_hours=2.0,
                progress=1.0,
                metadata={"type": "research", "source": "task_decomposition"}
            ),
            Task(
                id="task4",
                title="分析反馈数据",
                description="分析收集到的用户反馈数据",
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.MEDIUM,
                parent_id="task1",
                assigned_agent="Analyst-AI",
                dependencies=["task3"],
                subtasks=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=None,
                estimated_hours=2.0,
                actual_hours=1.0,
                progress=0.5,
                metadata={"type": "analysis", "source": "task_decomposition"}
            )
        ]

    async def handle_add_task(self, event):
        """处理添加新任务"""
        title = self.new_task_input.value.strip()
        if title:
            new_task = Task(
                id=f"task{len(self.tasks) + 1}",
                title=title,
                description=f"新任务: {title}",
                status=TaskStatus.NOT_STARTED,
                priority=TaskPriority.MEDIUM,
                parent_id=None,
                assigned_agent=None,
                dependencies=[],
                subtasks=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=None,
                estimated_hours=None,
                actual_hours=0.0,
                progress=0.0,
                metadata={"type": "user_created"}
            )
            self.tasks.append(new_task)
            self.new_task_input.value = ""
            await self.refresh()

    async def handle_task_status_update(self, task_id: str, new_status: TaskStatus):
        """处理任务状态更新"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = new_status
                task.updated_at = datetime.now()

                # 更新进度
                if new_status == TaskStatus.COMPLETED:
                    task.progress = 1.0
                elif new_status == TaskStatus.NOT_STARTED:
                    task.progress = 0.0

                break
        await self.refresh()

    async def handle_task_decomposition_update(self, decomposition: TaskDecompositionNode):
        """处理任务分解更新"""
        self.task_decompositions.append(decomposition)

        # 添加分解产生的子任务
        for subtask in decomposition.subtasks:
            if not any(t.id == subtask.id for t in self.tasks):
                self.tasks.append(subtask)

        await self.refresh()

    def get_root_tasks(self) -> List[Task]:
        """获取根任务（没有父任务的任务）"""
        return [task for task in self.tasks if task.parent_id is None]

    def get_subtasks(self, parent_id: str) -> List[Task]:
        """获取子任务"""
        return [task for task in self.tasks if task.parent_id == parent_id]

    def get_task_dependencies(self, task_id: str) -> List[Task]:
        """获取任务依赖"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            return [t for t in self.tasks if t.id in task.dependencies]
        return []

    def render_task(self, task: Task, level: int = 0) -> Div:
        """渲染单个任务"""
        status_colors = {
            TaskStatus.NOT_STARTED: "gray",
            TaskStatus.IN_PROGRESS: "blue",
            TaskStatus.COMPLETED: "green",
            TaskStatus.BLOCKED: "red",
            TaskStatus.CANCELLED: "orange"
        }

        status_labels = {
            TaskStatus.NOT_STARTED: "未开始",
            TaskStatus.IN_PROGRESS: "进行中",
            TaskStatus.COMPLETED: "已完成",
            TaskStatus.BLOCKED: "阻塞",
            TaskStatus.CANCELLED: "已取消"
        }

        priority_labels = {
            TaskPriority.LOW: "低",
            TaskPriority.MEDIUM: "中",
            TaskPriority.HIGH: "高",
            TaskPriority.CRITICAL: "紧急"
        }

        status_color = status_colors.get(task.status, "gray")
        status_label = status_labels.get(task.status, "未知")
        priority_label = priority_labels.get(task.priority, "未知")

        # 创建状态选择器
        status_select = Select(
            *[Option(label, value=status.value)
              for status, label in status_labels.items()],
            value=task.status.value,
            _class="task-status-select"
        )

        # 绑定状态更改事件
        async def handle_status_change(event):
            new_status = TaskStatus(event.target.value)
            await self.handle_task_status_update(task.id, new_status)

        status_select.onchange = handle_status_change

        # 计算进度条
        progress_bar = Div(
            Div(
                _class="progress-fill",
                _style=f"width: {task.progress * 100}%"
            ),
            _class="progress-bar"
        )

        subtasks = self.get_subtasks(task.id)
        dependencies = self.get_task_dependencies(task.id)

        return Div(
            Div(
                Div(
                    task.title,
                    _class="task-title"
                ),
                Div(
                    f"{status_label} | {priority_label}",
                    _class=f"task-meta status-{status_color}"
                ),
                status_select,
                _class="task-header"
            ),

            Div(
                P(task.description, _class="task-description"),
                progress_bar,
                P(f"进度: {task.progress * 100:.0f}%", _class="task-progress"),

                Div(
                    P(f"负责代理: {task.assigned_agent}", _class="task-agent") if task.assigned_agent else Div(),
                    P(f"预计时间: {task.estimated_hours}h", _class="task-estimate") if task.estimated_hours else Div(),
                    P(f"实际时间: {task.actual_hours}h", _class="task-actual") if task.actual_hours else Div(),
                    _class="task-metrics"
                ),

                Div(
                    *[P(f"依赖: {dep.title}", _class="task-dependency") for dep in dependencies],
                    _class="task-dependencies"
                ) if dependencies else Div(),

                _class="task-details"
            ),

            # 子任务
            Div(
                *[self.render_task(subtask, level + 1) for subtask in subtasks],
                _class="subtasks"
            ) if subtasks else Div(),

            _class=f"task-item level-{level}"
        )

    def render_task_summary(self) -> Div:
        """渲染任务摘要"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS])
        blocked_tasks = len([t for t in self.tasks if t.status == TaskStatus.BLOCKED])

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return Div(
            H4("📊 任务摘要", _class="task-summary-title"),
            Div(
                P(f"总任务: {total_tasks}", _class="summary-item"),
                P(f"已完成: {completed_tasks}", _class="summary-item completed"),
                P(f"进行中: {in_progress_tasks}", _class="summary-item in-progress"),
                P(f"阻塞: {blocked_tasks}", _class="summary-item blocked"),
                P(f"完成率: {completion_rate:.1f}%", _class="summary-item completion-rate"),
                _class="task-summary"
            ),
            _class="task-summary-container"
        )

    def render_task_decompositions(self) -> Div:
        """渲染任务分解"""
        if not self.task_decompositions:
            return Div()

        return Div(
            H4("🔄 任务分解", _class="decomposition-title"),
            *[Div(
                Div(
                    f"原始任务: {decomp.original_task}",
                    _class="decomp-original"
                ),
                Div(
                    f"策略: {decomp.decomposition_strategy}",
                    _class="decomp-strategy"
                ),
                Div(
                    f"置信度: {decomp.confidence:.2f}",
                    _class="decomp-confidence"
                ),
                _class="decomposition-item"
            ) for decomp in self.task_decompositions[-3:]],  # 显示最近3个
            _class="task-decompositions"
        )

    def render(self) -> HTML:
        """渲染任务面板"""
        return Div(
            H3("📋 任务管理", _class="task-title"),

            # 任务摘要
            self.render_task_summary(),

            # 添加新任务区域
            Div(
                self.new_task_input,
                self.add_task_button,
                _class="add-task-area"
            ),

            # 刷新按钮
            self.refresh_button,

            # 任务分解
            self.render_task_decompositions(),

            # 任务层次结构
            Div(
                *[self.render_task(task) for task in self.get_root_tasks()],
                _class="task-hierarchy"
            ) if self.tasks else Div(
                P("暂无任务"),
                _class="no-tasks"
            ),

            _class="task-panel"
        )
