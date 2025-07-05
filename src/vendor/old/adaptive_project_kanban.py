"""自适应项目看板系统
支持动态任务分解、项目看板、DAG管理和自动推进
"""

import asyncio
import base64
import io
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import matplotlib.pyplot as plt
import networkx as nx

from src.expert_library import ExpertLibrary
from src.shor_task_decomposer import ShorTaskDecomposer, TaskComplexity, TaskNode


class TaskStatus(Enum):
    """任务状态枚举"""

    BACKLOG = "backlog"
    ANALYSIS = "analysis"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """任务优先级枚举"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """任务数据结构"""

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    dependencies: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    risk_level: str = "low"

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.risk_level is None:
            self.risk_level = "low"


@dataclass
class KanbanColumn:
    """看板列数据结构"""

    name: str
    type: str
    tasks: list[Task]
    limit: Optional[int] = None
    auto_populate: bool = True
    auto_assign: bool = False
    auto_trigger: bool = False
    auto_archive: bool = False


@dataclass
class ProjectMetrics:
    """项目指标数据结构"""

    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    cycle_time: float
    throughput: float
    quality_score: float
    team_satisfaction: float
    critical_path_length: int
    resource_utilization: float


class AdaptiveProjectKanban:
    """自适应项目看板系统"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 初始化核心组件
        self.expert_library = ExpertLibrary()
        self.task_decomposer = ShorTaskDecomposer()

        # 看板状态
        self.columns: dict[str, KanbanColumn] = {}
        self.tasks: dict[str, Task] = {}
        self.dag: nx.DiGraph = nx.DiGraph()
        self.project_metrics = ProjectMetrics(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0)

        # 自动推进配置
        self.auto_progression_enabled = True
        self.continuous_monitoring = True

        # 初始化看板
        self._initialize_kanban()

        # 启动监控任务
        if self.continuous_monitoring:
            asyncio.create_task(self._monitor_project_progress())

    def _initialize_kanban(self):
        """初始化看板列"""
        self.columns = {
            "backlog": KanbanColumn(
                name="Backlog",
                type="input_queue",
                tasks=[],
                auto_populate=True,
            ),
            "analysis": KanbanColumn(
                name="Analysis",
                type="processing",
                tasks=[],
                auto_assign=True,
            ),
            "in_progress": KanbanColumn(
                name="In Progress",
                type="active_work",
                tasks=[],
                limit=5,  # 限制在制品数量
            ),
            "review": KanbanColumn(
                name="Review",
                type="quality_gate",
                tasks=[],
                auto_trigger=True,
            ),
            "done": KanbanColumn(
                name="Done",
                type="output_queue",
                tasks=[],
                auto_archive=True,
            ),
        }

    async def create_project_from_description(
        self,
        project_description: str,
        user_requirements: dict[str, Any],
    ) -> str:
        """从项目描述创建项目"""
        project_id = f"project_{int(datetime.now().timestamp())}"
        try:
            # 使用ShorTaskDecomposer进行智能分解
            # 构造TaskNode
            skills = user_requirements.get("skills")
            if not isinstance(skills, list):
                skills = []
            task = TaskNode(
                id=project_id,
                name=project_description,
                description=project_description,
                complexity=TaskComplexity.MODERATE,  # 可根据user_requirements调整
                dependencies=[],
                estimated_time=40.0,  # 可根据user_requirements调整
                required_skills=skills,
                priority=5,
            )
            result = self.task_decomposer.decompose_task(task)
            # 转换为通用分解结果格式
            decomposition_result = {
                "tasks": [
                    {
                        "id": subtask.id,
                        "title": subtask.name,
                        "description": subtask.description,
                        "priority": subtask.priority,
                        "estimated_hours": subtask.estimated_time,
                        "dependencies": subtask.dependencies,
                        "tags": subtask.required_skills,
                        "risk_level": "low",
                    }
                    for subtask in result.subtasks
                ],
            }
            # 创建任务
            tasks = await self._create_tasks_from_decomposition(decomposition_result)
            # 构建DAG
            await self._build_dag_from_tasks(tasks)
            # 初始化看板
            await self._populate_kanban_with_tasks(tasks)
            # 计算初始指标
            await self._calculate_project_metrics()
            self.logger.info(f"项目创建成功: {project_id}, 任务数量: {len(tasks)}")
            return project_id
        except Exception as e:
            self.logger.error(f"项目创建失败: {e}")
            raise

    async def _create_tasks_from_decomposition(
        self,
        decomposition_result: dict[str, Any],
    ) -> list[Task]:
        """从分解结果创建任务"""
        tasks: list[Task] = []
        for task_data in decomposition_result.get("tasks", []):
            # 兼容优先级为int或str，内部转为TaskPriority
            priority_val = task_data.get("priority", "medium")
            if isinstance(priority_val, int):
                # 简单映射：1-3=LOW, 4-6=MEDIUM, 7-8=HIGH, 9-10=CRITICAL
                if priority_val <= 3:
                    priority = TaskPriority.LOW
                elif priority_val <= 6:
                    priority = TaskPriority.MEDIUM
                elif priority_val <= 8:
                    priority = TaskPriority.HIGH
                else:
                    priority = TaskPriority.CRITICAL
            else:
                try:
                    priority = TaskPriority(priority_val)
                except Exception:
                    priority = TaskPriority.MEDIUM
            task = Task(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data["description"],
                status=TaskStatus.BACKLOG,
                priority=priority,
                estimated_hours=task_data.get("estimated_hours"),
                dependencies=task_data.get("dependencies", []),
                tags=task_data.get("tags", []),
                risk_level=task_data.get("risk_level", "low"),
            )
            tasks.append(task)
            self.tasks[task.id] = task
        return tasks

    async def _build_dag_from_tasks(self, tasks: list[Task]):
        """从任务构建DAG"""
        self.dag.clear()

        # 添加节点
        for task in tasks:
            self.dag.add_node(task.id, task=task)

        # 添加边（依赖关系）
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in self.dag.nodes:
                    self.dag.add_edge(dep_id, task.id)

        # 检测并处理循环依赖
        try:
            cycles = list(nx.simple_cycles(self.dag))
            if cycles:
                self.logger.warning(f"检测到循环依赖: {cycles}")
                # 移除循环依赖
                for cycle in cycles:
                    for i in range(len(cycle)):
                        self.dag.remove_edge(cycle[i], cycle[(i + 1) % len(cycle)])
        except nx.NetworkXNoCycle:
            pass  # 没有循环依赖

    async def _populate_kanban_with_tasks(self, tasks: list[Task]):
        """将任务填充到看板"""
        # 清空看板
        for column in self.columns.values():
            column.tasks.clear()

        # 根据依赖关系分配任务到合适的列
        for task in tasks:
            if not task.dependencies:
                # 没有依赖的任务直接进入分析阶段
                self.columns["analysis"].tasks.append(task)
                task.status = TaskStatus.ANALYSIS
            else:
                # 有依赖的任务进入待办
                self.columns["backlog"].tasks.append(task)
                task.status = TaskStatus.BACKLOG

    async def move_task(self, task_id: str, target_status: TaskStatus) -> bool:
        """移动任务到新状态"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        old_status = task.status

        # 检查是否可以移动
        if not await self._can_move_task(task, target_status):
            return False

        # 从原列移除
        for column in self.columns.values():
            if task in column.tasks:
                column.tasks.remove(task)
                break

        # 添加到新列
        target_column = self._get_column_by_status(target_status)
        if target_column:
            target_column.tasks.append(task)
            task.status = target_status

            # 更新任务时间
            if target_status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.now().isoformat()
            elif target_status == TaskStatus.DONE and not task.completed_at:
                task.completed_at = datetime.now().isoformat()

            # 触发自动推进
            if self.auto_progression_enabled:
                await self._trigger_auto_progression(task)

            self.logger.info(
                f"任务移动: {task_id} {old_status.value} -> {target_status.value}",
            )
            return True

        return False

    async def _can_move_task(self, task: Task, target_status: TaskStatus) -> bool:
        """检查任务是否可以移动到目标状态"""
        # 检查依赖是否满足
        if target_status in [TaskStatus.IN_PROGRESS, TaskStatus.REVIEW]:
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.status != TaskStatus.DONE:
                        return False

        # 检查列限制
        target_column = self._get_column_by_status(target_status)
        if target_column and target_column.limit:
            if len(target_column.tasks) >= target_column.limit:
                return False

        return True

    def _get_column_by_status(self, status: TaskStatus) -> Optional[KanbanColumn]:
        """根据状态获取对应的列"""
        status_to_column = {
            TaskStatus.BACKLOG: "backlog",
            TaskStatus.ANALYSIS: "analysis",
            TaskStatus.IN_PROGRESS: "in_progress",
            TaskStatus.REVIEW: "review",
            TaskStatus.DONE: "done",
        }
        column_key = status_to_column.get(status)
        if column_key is None:
            return None
        return self.columns.get(column_key)

    async def _trigger_auto_progression(self, completed_task: Task):
        """触发自动推进"""
        # 检查是否有任务可以因为依赖完成而推进
        for task_id, task in self.tasks.items():
            if (
                task.status == TaskStatus.BACKLOG
                and completed_task.id in task.dependencies
            ):
                # 检查所有依赖是否完成
                all_deps_complete = True
                for dep_id in task.dependencies:
                    if dep_id in self.tasks:
                        dep_task = self.tasks[dep_id]
                        if dep_task.status != TaskStatus.DONE:
                            all_deps_complete = False
                            break

                if all_deps_complete:
                    # 自动推进到分析阶段
                    await self.move_task(task_id, TaskStatus.ANALYSIS)

    async def get_kanban_board(self) -> dict[str, Any]:
        """获取看板状态"""
        board_data = {
            "columns": {},
            "metrics": asdict(self.project_metrics),
            "critical_path": await self._get_critical_path(),
            "bottlenecks": await self._identify_bottlenecks(),
        }

        for column_key, column in self.columns.items():
            board_data["columns"][column_key] = {
                "name": column.name,
                "type": column.type,
                "limit": column.limit,
                "tasks": [asdict(task) for task in column.tasks],
            }

        return board_data

    async def get_dag_visualization(self) -> str:
        """获取DAG可视化图像"""
        try:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.dag)

            # 绘制节点
            nx.draw_networkx_nodes(
                self.dag,
                pos,
                node_color="lightblue",
                node_size=2000,
            )

            # 绘制边
            nx.draw_networkx_edges(
                self.dag,
                pos,
                edge_color="gray",
                arrows=True,
                arrowsize=20,
            )

            # 添加标签
            labels = {
                node: self.tasks[node].title[:15] + "..."
                if len(self.tasks[node].title) > 15
                else self.tasks[node].title
                for node in self.dag.nodes()
            }
            nx.draw_networkx_labels(self.dag, pos, labels, font_size=8)

            plt.title("Project Task Dependencies")
            plt.axis("off")

            # 转换为base64字符串
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", bbox_inches="tight")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return f"data:image/png;base64,{image_base64}"

        except Exception as e:
            self.logger.error(f"DAG可视化生成失败: {e}")
            return ""

    async def _get_critical_path(self) -> list[str]:
        """获取关键路径"""
        try:
            if not self.dag.nodes():
                return []

            # 计算最长路径（关键路径）
            critical_path = nx.dag_longest_path(self.dag)
            return critical_path

        except Exception as e:
            self.logger.error(f"关键路径计算失败: {e}")
            return []

    async def _identify_bottlenecks(self) -> list[str]:
        """识别瓶颈任务"""
        bottlenecks: list[str] = []
        try:
            # 计算每个节点的入度和出度
            for node in self.dag.nodes():
                # networkx.DiGraph.in_degree[node] 返回int
                try:
                    in_degree = int(self.dag.in_degree[node])
                except Exception:
                    in_degree = 0
                try:
                    out_degree = int(self.dag.out_degree[node])
                except Exception:
                    out_degree = 0
                # 高入度低出度的节点可能是瓶颈
                if in_degree > 2 and out_degree < 2:
                    bottlenecks.append(node)
            return bottlenecks
        except Exception as e:
            self.logger.error(f"瓶颈识别失败: {e}")
            return []

    async def _calculate_project_metrics(self):
        """计算项目指标"""
        total_tasks = len(self.tasks)
        completed_tasks = len(
            [t for t in self.tasks.values() if t.status == TaskStatus.DONE],
        )
        in_progress_tasks = len(
            [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS],
        )
        blocked_tasks = len(
            [t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED],
        )
        # 计算周期时间（平均完成时间）
        completed_tasks_with_time = [
            t
            for t in self.tasks.values()
            if t.status == TaskStatus.DONE
            and t.started_at is not None
            and t.completed_at is not None
        ]
        if completed_tasks_with_time:
            total_cycle_time = 0.0
            for task in completed_tasks_with_time:
                # 类型安全：断言不为None
                assert task.started_at is not None and task.completed_at is not None
                start_time = datetime.fromisoformat(task.started_at)
                end_time = datetime.fromisoformat(task.completed_at)
                cycle_time = (end_time - start_time).total_seconds() / 3600  # 小时
                total_cycle_time += cycle_time
            self.project_metrics.cycle_time = total_cycle_time / len(
                completed_tasks_with_time
            )
        else:
            self.project_metrics.cycle_time = 0.0
        # 计算吞吐量（每小时完成的任务数）
        if self.project_metrics.cycle_time > 0:
            self.project_metrics.throughput = (
                completed_tasks / self.project_metrics.cycle_time
            )
        else:
            self.project_metrics.throughput = 0.0
        # 更新其他指标
        self.project_metrics.total_tasks = total_tasks
        self.project_metrics.completed_tasks = completed_tasks
        self.project_metrics.in_progress_tasks = in_progress_tasks
        self.project_metrics.blocked_tasks = blocked_tasks
        # 计算关键路径长度
        critical_path = await self._get_critical_path()
        self.project_metrics.critical_path_length = len(critical_path)
        # 计算资源利用率
        if total_tasks > 0:
            self.project_metrics.resource_utilization = (
                in_progress_tasks + completed_tasks
            ) / total_tasks
        else:
            self.project_metrics.resource_utilization = 0.0

    async def _monitor_project_progress(self):
        """监控项目进度"""
        while self.continuous_monitoring:
            try:
                # 更新指标
                await self._calculate_project_metrics()

                # 检查瓶颈
                bottlenecks = await self._identify_bottlenecks()
                if bottlenecks:
                    self.logger.warning(f"检测到瓶颈任务: {bottlenecks}")

                # 检查阻塞任务
                blocked_tasks = [
                    t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED
                ]
                if blocked_tasks:
                    self.logger.warning(f"检测到阻塞任务: {[t.id for t in blocked_tasks]}")

                # 每30秒检查一次
                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"项目监控失败: {e}")
                await asyncio.sleep(60)  # 出错时等待更长时间

    async def add_task(self, task: Task) -> bool:
        """添加新任务"""
        try:
            self.tasks[task.id] = task
            self.dag.add_node(task.id, task=task)

            # 添加到看板
            target_column = self._get_column_by_status(task.status)
            if target_column:
                target_column.tasks.append(task)

            # 更新指标
            await self._calculate_project_metrics()

            return True

        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return False

    async def update_task(self, task_id: str, updates: dict[str, Any]) -> bool:
        """更新任务"""
        if task_id not in self.tasks:
            return False

        try:
            task = self.tasks[task_id]

            # 更新任务属性
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            # 如果更新了依赖关系，重新构建DAG
            if "dependencies" in updates:
                await self._build_dag_from_tasks(list(self.tasks.values()))

            # 更新指标
            await self._calculate_project_metrics()

            return True

        except Exception as e:
            self.logger.error(f"更新任务失败: {e}")
            return False

    async def get_project_summary(self) -> dict[str, Any]:
        """获取项目摘要"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.DONE],
            ),
            "in_progress_tasks": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS],
            ),
            "blocked_tasks": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED],
            ),
            "metrics": asdict(self.project_metrics),
            "critical_path": await self._get_critical_path(),
            "bottlenecks": await self._identify_bottlenecks(),
            "estimated_completion": await self._estimate_completion_time(),
        }

    async def _estimate_completion_time(self) -> Optional[str]:
        """估算完成时间"""
        try:
            if not self.tasks:
                return None

            # 计算剩余工作量
            remaining_tasks = [
                t for t in self.tasks.values() if t.status != TaskStatus.DONE
            ]
            total_remaining_hours = sum(t.estimated_hours or 0 for t in remaining_tasks)

            # 基于当前吞吐量估算
            if self.project_metrics.throughput > 0:
                estimated_hours = (
                    total_remaining_hours / self.project_metrics.throughput
                )
                estimated_completion = datetime.now() + timedelta(hours=estimated_hours)
                return estimated_completion.isoformat()

            return None

        except Exception as e:
            self.logger.error(f"完成时间估算失败: {e}")
            return None
