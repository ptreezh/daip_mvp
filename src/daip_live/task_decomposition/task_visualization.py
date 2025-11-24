"""
任务清单可视化组件
提供任务分解过程的实时可视化展示
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from daip_live.task_decomposition.task_decomposition_engine import DecomposedTask, TaskStatus


@dataclass
class TaskVisualizationData:
    """任务可视化数据"""
    task_id: str
    title: str
    description: str
    status: TaskStatus
    priority: str
    dependencies: List[str]
    result: Optional[str] = None
    progress: float = 0.0


class TaskVisualizationManager:
    """任务可视化管理器"""
    
    def __init__(self):
        self.console = Console()
        self.tasks_data: List[TaskVisualizationData] = []
        self.original_request: str = ""
        self.current_task_index: int = 0

    def update_tasks(self, tasks: List[DecomposedTask], original_request: str = ""):
        """更新任务列表数据"""
        self.original_request = original_request
        self.tasks_data = [
            TaskVisualizationData(
                task_id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=str(task.priority.name if hasattr(task.priority, 'name') else task.priority),
                dependencies=task.dependencies,
                result=task.result
            )
            for task in tasks
        ]

    def add_task(self, task: DecomposedTask):
        """添加单个任务"""
        task_data = TaskVisualizationData(
            task_id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=str(task.priority.name if hasattr(task.priority, 'name') else task.priority),
            dependencies=task.dependencies,
            result=task.result
        )
        self.tasks_data.append(task_data)

    def update_task_status(self, task_id: str, new_status: TaskStatus, result: Optional[str] = None):
        """更新指定任务的状态"""
        for task_data in self.tasks_data:
            if task_data.task_id == task_id:
                task_data.status = new_status
                if result:
                    task_data.result = result
                break

    def update_task_progress(self, task_id: str, progress: float):
        """更新任务进度"""
        for task_data in self.tasks_data:
            if task_data.task_id == task_id:
                task_data.progress = progress
                break

    def display_task_list(self):
        """显示任务列表"""
        if not self.tasks_data:
            self.console.print("[yellow]当前没有任务清单[/yellow]")
            return

        # 创建任务表格
        table = Table(title=f"任务清单 - 原始请求: {self.original_request[:50]}{'...' if len(self.original_request) > 50 else ''}",
                      box=box.ROUNDED,
                      show_header=True,
                      header_style="bold magenta")
        
        table.add_column("#", style="dim", width=3)
        table.add_column("任务标题", min_width=20)
        table.add_column("描述", min_width=30)
        table.add_column("状态", justify="center")
        table.add_column("优先级", justify="center")
        table.add_column("进度", justify="center")

        status_icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️"
        }

        status_colors = {
            TaskStatus.PENDING: "yellow",
            TaskStatus.IN_PROGRESS: "blue",
            TaskStatus.COMPLETED: "green",
            TaskStatus.FAILED: "red",
            TaskStatus.SKIPPED: "dim"
        }

        for i, task_data in enumerate(self.tasks_data, 1):
            status_icon = status_icons.get(task_data.status, "❓")
            status_color = status_colors.get(task_data.status, "white")
            
            # 截断描述以防止表格过宽
            desc = task_data.description[:50] + "..." if len(task_data.description) > 50 else task_data.description
            
            progress_bar = self._create_progress_bar(task_data.progress, 10) if task_data.progress > 0 else ""
            
            table.add_row(
                str(i),
                task_data.title,
                desc,
                f"[{status_color}]{status_icon} {task_data.status.value}[/{status_color}]",
                task_data.priority,
                progress_bar
            )

        self.console.print(table)

    def _create_progress_bar(self, progress: float, width: int = 10) -> str:
        """创建简单的进度条文本"""
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percent = f"{progress*100:.0f}%"
        return f"[{bar}] {percent}"

    def display_task_tree(self):
        """以树形结构显示任务"""
        if not self.tasks_data:
            self.console.print("[yellow]当前没有任务清单[/yellow]")
            return

        tree = Tree(f"任务分解树 - 总计 {len(self.tasks_data)} 个任务")

        status_icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️"
        }

        status_colors = {
            TaskStatus.PENDING: "yellow",
            TaskStatus.IN_PROGRESS: "blue",
            TaskStatus.COMPLETED: "green",
            TaskStatus.FAILED: "red",
            TaskStatus.SKIPPED: "dim"
        }

        for i, task_data in enumerate(self.tasks_data, 1):
            status_icon = status_icons.get(task_data.status, "❓")
            status_color = status_colors.get(task_data.status, "white")

            # 截断描述以防止过长
            desc = task_data.description[:50] + "..." if len(task_data.description) > 50 else task_data.description

            task_text = Text.assemble(
                f"{i}. ",
                (f"{status_icon} {task_data.title}", f"bold {status_color}"),
                f" - {desc} "
            )
            # 添加优先级信息，但不使用嵌套的格式标记
            priority_text = Text(f"({task_data.priority})", style="dim")
            task_text.append(priority_text)

            task_tree = tree.add(task_text)

            # 如果有依赖关系，显示依赖
            if task_data.dependencies:
                dep_text = Text("依赖任务:", style="yellow")
                dep_tree = task_tree.add(dep_text)
                for dep_id in task_data.dependencies:
                    dep_task = next((t for t in self.tasks_data if t.task_id == dep_id), None)
                    if dep_task:
                        dep_text = Text(dep_task.title, style="dim")
                        dep_tree.add(dep_text)

        self.console.print(Panel(tree, title="任务分解结构"))

    def display_progress_summary(self):
        """显示进度摘要"""
        if not self.tasks_data:
            self.console.print("[yellow]当前没有任务清单[/yellow]")
            return

        total = len(self.tasks_data)
        completed = len([t for t in self.tasks_data if t.status == TaskStatus.COMPLETED])
        in_progress = len([t for t in self.tasks_data if t.status == TaskStatus.IN_PROGRESS])
        failed = len([t for t in self.tasks_data if t.status == TaskStatus.FAILED])
        pending = len([t for t in self.tasks_data if t.status == TaskStatus.PENDING])
        skipped = len([t for t in self.tasks_data if t.status == TaskStatus.SKIPPED])

        summary_table = Table(box=box.ROUNDED, show_header=False, title="进度摘要")
        summary_table.add_column("信息", style="bold")
        summary_table.add_column("数量", justify="right")

        summary_table.add_row("总计任务数", str(total))
        summary_table.add_row("已完成", f"[green]{completed}[/]", style="green")
        summary_table.add_row("进行中", f"[blue]{in_progress}[/]", style="blue")
        summary_table.add_row("待处理", f"[yellow]{pending}[/]", style="yellow")
        summary_table.add_row("已失败", f"[red]{failed}[/]", style="red")
        summary_table.add_row("已跳过", f"[dim]{skipped}[/]", style="dim")

        # 计算完成百分比
        if total > 0:
            completion_rate = completed / total * 100
            progress_bar = self._create_progress_bar(completion_rate / 100, 20)
            summary_table.add_row("完成率", f"[bold]{completion_rate:.1f}%[/]")
            summary_table.add_row("进度", progress_bar)

        self.console.print(summary_table)

    def display_live_progress(self, task_callback=None):
        """显示实时进度（使用Rich的Progress组件）"""
        if not self.tasks_data:
            self.console.print("[yellow]当前没有任务清单[/yellow]")
            return

        # 创建进度跟踪器
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )

        task_trackers = {}
        for task_data in self.tasks_data:
            # 创建任务进度条
            task_id = progress.add_task(
                description=f"{task_data.title} ({task_data.status.value})",
                total=100,
                completed=task_data.progress * 100 if task_data.progress else 0
            )
            task_trackers[task_data.task_id] = task_id

        with progress:
            # 这里应该连接到实时任务执行状态
            if task_callback:
                # 执行回调以更新进度
                task_callback(progress, task_trackers)

    def update_and_display(self, tasks: List[DecomposedTask], original_request: str = ""):
        """更新任务数据并立即显示"""
        self.update_tasks(tasks, original_request)
        
        # 显示任务列表
        self.display_task_list()
        
        # 显示进度摘要
        self.display_progress_summary()
        
        # 显示任务树
        self.display_task_tree()


# 全局任务可视化实例
task_visualization_manager = TaskVisualizationManager()


def get_task_visualization_manager() -> TaskVisualizationManager:
    """获取任务可视化管理器实例"""
    return task_visualization_manager