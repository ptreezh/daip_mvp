"""
TUI中嵌套待办列表功能的实现
"""

# 首先创建一个全局的TUI Todo管理器
from daip_live.todo.nested_todo_system import (
    NestedTodoItem,
    TaskPriority,
    TaskStatus,
    TodoManager,
)


class TUITodoManager(TodoManager):
    """TUI专用的Todo管理器，提供命令处理功能"""

    def __init__(self, tui_app):
        super().__init__()
        self.tui_app = tui_app  # TUI应用引用，用于更新界面

    def _update_tui_log(self, message: str):
        """更新TUI日志视图"""
        if hasattr(self.tui_app, "_update_log_view"):
            self.tui_app._update_log_view(message)

    def _format_task_display(self, task: NestedTodoItem, depth: int = 0) -> str:
        """格式化任务显示"""
        indent = "  " * depth
        status_symbols = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.CANCELLED: "🚫",
            TaskStatus.FAILED: "❌",
        }

        symbol = status_symbols.get(task.status, "❓")
        priority_symbols = {
            TaskPriority.LOW: "🟢",
            TaskPriority.MEDIUM: "🟡",
            TaskPriority.HIGH: "🔴",
            TaskPriority.CRITICAL: "🚨",
        }
        priority_symbol = priority_symbols.get(task.priority, "⚪")

        display = f"{indent}{symbol} {priority_symbol} {task.title}"
        if task.description:
            display += f"\\n{indent}   📝 {task.description[:100]}{'...' if len(task.description) > 100 else ''}"  # noqa: E501

        return display

    def _format_task_with_subtasks(
        self, task: NestedTodoItem, depth: int = 0, show_details: bool = True
    ) -> str:
        """格式化任务及子任务显示"""
        result = self._format_task_display(task, depth)

        if task.subtasks:
            result += (
                f"\\n{self._format_task_list(task.subtasks, depth + 1, show_details)}"
            )

        if show_details and task.details:
            result += f"\\n{self._format_task_list(task.details, depth + 1, False)}"

        return result

    def _format_task_list(
        self, tasks: list[NestedTodoItem], depth: int = 0, show_details: bool = True
    ) -> str:
        """格式化任务列表显示"""
        result = ""
        for task in tasks:
            result += f"\\n{self._format_task_with_subtasks(task, depth, show_details)}"
        return result

    def handle_todo_command(self, args: str) -> None:
        """处理/todo命令"""
        args_list = args.split() if args else []

        if not args_list:
            # 显示帮助信息
            self.show_todo_help()
            return

        command = args_list[0].lower()
        remaining_args = " ".join(args_list[1:]) if len(args_list) > 1 else ""

        if command == "list" or command == "ls":
            self.list_tasks(remaining_args)
        elif command == "add":
            self.add_task(remaining_args)
        elif command == "complete" or command == "done":
            self.complete_task(remaining_args)
        elif command == "inprogress" or command == "start":
            self.start_task(remaining_args)
        elif command == "cancel":
            self.cancel_task(remaining_args)
        elif command == "status":
            self.show_status()
        elif command == "clear":
            self.clear_completed_tasks()
        elif command == "context":
            self.manage_context(remaining_args)
        elif command == "decompose":
            self.decompose_task(remaining_args)
        elif command == "help":
            self.show_todo_help()
        else:
            self._update_tui_log(f"[bold red]> 未知的todo命令: {command}[/bold red]")
            self.show_todo_help()

    def show_todo_help(self) -> None:
        """显示todo命令帮助"""
        help_text = """[bold blue]> TODO命令帮助:[/bold blue]
  /todo list [pending|completed|in_progress] - 列出任务
  /todo add <title>[:<description>] - 添加任务
  /todo complete <task_id> - 完成任务
  /todo start <task_id> - 开始任务
  /todo cancel <task_id> - 取消任务
  /todo status - 显示整体状态
  /todo clear - 清除已完成任务
  /todo context <name> - 管理上下文
  /todo decompose <description> - 分解任务
  /todo help - 显示帮助"""

        self._update_tui_log(help_text)

    def list_tasks(self, filter_type: str = "") -> None:
        """列出任务"""
        context = self.get_current_context()
        if not context:
            self._update_tui_log(
                "[bold yellow]> 没有激活的待办列表上下文[/bold yellow]"
            )
            return

        if filter_type.lower() == "completed":
            tasks = context.get_completed_tasks()
            title = "已完成任务"
        elif filter_type.lower() == "pending":
            # 获取所有未完成的任务
            all_tasks = []

            def collect_pending(tasks_list):
                for task in tasks_list:
                    if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                        all_tasks.append(task)
                        collect_pending(task.subtasks)
                        collect_pending(task.details)

            collect_pending(context.root_tasks)
            tasks = all_tasks
            title = "待处理任务"
        elif filter_type.lower() == "in_progress":
            # 获取进行中的任务
            all_tasks = []

            def collect_in_progress(tasks_list):
                for task in tasks_list:
                    if task.status == TaskStatus.IN_PROGRESS:
                        all_tasks.append(task)
                        collect_in_progress(task.subtasks)
                        collect_in_progress(task.details)

            collect_in_progress(context.root_tasks)
            tasks = all_tasks
            title = "进行中任务"
        else:
            # 显示所有根任务
            tasks = context.root_tasks
            title = "所有根任务"

        if not tasks:
            self._update_tui_log(f"[bold blue]> {title}: 没有找到任务[/bold blue]")
            return

        self._update_tui_log(f"[bold blue]> {title}列表:[/bold blue]")

        for i, task in enumerate(tasks[:20]):  # 限制显示前20个任务
            try:
                task_display = self._format_task_with_subtasks(task)
                self._update_tui_log(f"  {task_display}")
            except Exception as e:
                self._update_tui_log(
                    f"  📝 任务 {task.title[:50]}... (无法完全显示: {e})"
                )

        if len(tasks) > 20:
            self._update_tui_log(f"  ... 还有 {len(tasks) - 20} 个任务未显示")

    def add_task(self, task_spec: str) -> None:
        """添加任务"""
        if not task_spec.strip():
            self._update_tui_log("[bold red]> 请提供任务标题[/bold red]")
            return

        # 解析任务规格: "标题:描述" 或只是标题
        if ":" in task_spec:
            title, desc = task_spec.split(":", 1)
            title = title.strip()
            desc = desc.strip()
        else:
            title = task_spec.strip()
            desc = ""

        # 创建新任务
        new_task = NestedTodoItem(
            title=title, description=desc, priority=TaskPriority.MEDIUM
        )

        # 添加到上下文
        if self.add_task_to_current_context(new_task):
            self._update_tui_log(
                f"[bold green]> ✅ 任务已添加: {new_task.title}[/bold green]"
            )
            self._update_tui_log(f"   ID: {new_task.id}")
        else:
            self._update_tui_log("[bold red]> ❌ 无法添加任务[/bold red]")

    def complete_task(self, task_id: str) -> None:
        """完成任务"""
        if not task_id.strip():
            self._update_tui_log("[bold red]> 请提供任务ID[/bold red]")
            return

        context = self.get_current_context()
        if not context:
            self._update_tui_log(
                "[bold yellow]> 没有激活的待办列表上下文[/bold yellow]"
            )
            return

        task = context.get_task(task_id.strip())
        if task:
            task.mark_completed()
            self._update_tui_log(
                f"[bold green]> ✅ 任务已完成: {task.title}[/bold green]"
            )
        else:
            self._update_tui_log(f"[bold red]> ❌ 未找到任务: {task_id}[/bold red]")

    def start_task(self, task_id: str) -> None:
        """开始任务"""
        if not task_id.strip():
            self._update_tui_log("[bold red]> 请提供任务ID[/bold red]")
            return

        context = self.get_current_context()
        if not context:
            self._update_tui_log(
                "[bold yellow]> 没有激活的待办列表上下文[/bold yellow]"
            )
            return

        task = context.get_task(task_id.strip())
        if task:
            task.mark_in_progress()
            self._update_tui_log(f"[bold blue]> 🔄 任务开始: {task.title}[/bold blue]")
        else:
            self._update_tui_log(f"[bold red]> ❌ 未找到任务: {task_id}[/bold red]")

    def cancel_task(self, task_id: str) -> None:
        """取消任务"""
        if not task_id.strip():
            self._update_tui_log("[bold red]> 请提供任务ID[/bold red]")
            return

        context = self.get_current_context()
        if not context:
            self._update_tui_log(
                "[bold yellow]> 没有激活的待办列表上下文[/bold yellow]"
            )
            return

        task = context.get_task(task_id.strip())
        if task:
            task.mark_cancelled()
            self._update_tui_log(
                f"[bold yellow]> 🚫 任务已取消: {task.title}[/bold yellow]"
            )
        else:
            self._update_tui_log(f"[bold red]> ❌ 未找到任务: {task_id}[/bold red]")

    def show_status(self) -> None:
        """显示状态"""
        context = self.get_current_context()
        if not context:
            self._update_tui_log(
                "[bold yellow]> 没有激活的待办列表上下文[/bold yellow]"
            )
            return

        stats = context.get_task_hierarchy()

        self._update_tui_log("[bold blue]> 📊 待办列表状态:[/bold blue]")
        self._update_tui_log(f"  名称: {stats['name']}")
        self._update_tui_log(f"  描述: {stats['description']}")
        self._update_tui_log(f"  总任务数: {stats['total_tasks']}")
        self._update_tui_log(f"  活跃任务: {stats['active_tasks']}")
        self._update_tui_log(f"  已完成: {stats['completed_tasks']}")

    def clear_completed_tasks(self) -> None:
        """清除已完成任务"""
        context = self.get_current_context()
        if not context:
            self._update_tui_log(
                "[bold yellow]> 没有激活的待办列表上下文[/bold yellow]"
            )
            return

        context.get_completed_tasks()
        cleared_count = 0

        # 从后往前遍历，避免删除时索引变化问题
        for task in reversed(context.root_tasks):
            if task.status == TaskStatus.COMPLETED:
                context.remove_task(task.id)
                cleared_count += 1

        self._update_tui_log(
            f"[bold green]> 🗑️ 清除已完成任务: {cleared_count} 个[/bold green]"
        )

    def manage_context(self, args: str) -> None:
        """管理上下文"""
        args_list = args.split() if args else []

        if not args_list:
            # 显示当前上下文
            if self.current_context:
                context = self.get_current_context()
                if context:
                    self._update_tui_log(
                        f"[bold blue]> 当前上下文: {context.name}[/bold blue]"
                    )
                    self._update_tui_log(f"  ID: {self.current_context}")
                    self._update_tui_log(f"  描述: {context.description}")
            else:
                self._update_tui_log("[bold yellow]> 没有激活的上下文[/bold yellow]")
            return

        command = args_list[0].lower()
        if command == "list":
            self._update_tui_log("[bold blue]> 可用上下文:[/bold blue]")
            for ctx_id, ctx in self.contexts.items():
                active = " (当前)" if ctx_id == self.current_context else ""
                self._update_tui_log(f"  {ctx_id[:8]}... {ctx.name}{active}")
        elif command == "switch" and len(args_list) > 1:
            target_ctx = args_list[1]
            if self.switch_context(target_ctx):
                self._update_tui_log(
                    f"[bold green]> ✅ 上下文切换到: {target_ctx}[/bold green]"
                )
            else:
                self._update_tui_log(
                    f"[bold red]> ❌ 未找到上下文: {target_ctx}[/bold red]"
                )
        elif command == "create" and len(args_list) > 1:
            name = " ".join(args_list[1:])
            new_ctx = self.create_context(name)
            self._update_tui_log(
                f"[bold green]> ✅ 创建新上下文: {name} (ID: {new_ctx.owner_id})[/bold green]"  # noqa: E501
            )
        else:
            self._update_tui_log(
                "[bold red]> 用法: /todo context [list|switch <id>|create <name>][/bold red]"  # noqa: E501
            )

    def decompose_task(self, task_desc: str) -> None:
        """分解任务"""
        if not task_desc.strip():
            self._update_tui_log("[bold red]> 请提供要分解的任务描述[/bold red]")
            return

        from daip_live.todo.nested_todo_system import HierarchicalTaskDecomposer

        # 分解任务
        subtasks = HierarchicalTaskDecomposer.decompose_task(task_desc.strip())

        if not subtasks:
            self._update_tui_log(
                f"[bold yellow]> ⚠️ 无法分解任务: {task_desc}[/bold yellow]"
            )
            return

        # 创建主任务
        main_task = NestedTodoItem(
            title=f"主任务: {task_desc}",
            description=f"通过任务分解创建的主任务: {task_desc}",
            priority=TaskPriority.HIGH,
        )

        # 添加子任务
        for subtask in subtasks:
            main_task.add_subtask(subtask)

        # 添加到上下文
        if self.add_task_to_current_context(main_task):
            self._update_tui_log(
                f"[bold green]> ✅ 任务分解完成: {main_task.title}[/bold green]"
            )
            self._update_tui_log(f"   创建了 {len(subtasks)} 个子任务")

            # 显示分解结果
            for i, subtask in enumerate(subtasks[:5]):  # 只显示前5个
                self._update_tui_log(f"   {i + 1}. {subtask.title}")
            if len(subtasks) > 5:
                self._update_tui_log(f"   ... 还有 {len(subtasks) - 5} 个子任务")
        else:
            self._update_tui_log("[bold red]> ❌ 无法添加分解后的任务[/bold red]")


# 创建全局实例
tui_todo_manager = None


def initialize_tui_todo_manager(tui_app):
    """初始化TUI Todo管理器"""
    global tui_todo_manager
    tui_todo_manager = TUITodoManager(tui_app)
    # 创建一个默认上下文
    tui_todo_manager.create_context("默认任务列表", "用户创建的默认任务列表")
    return tui_todo_manager


if __name__ == "__main__":
    # 示例：创建一个简单的管理器实例
    class MockTUIApp:
        def _update_log_view(self, message):
            pass

    mock_app = MockTUIApp()
    manager = initialize_tui_todo_manager(mock_app)
