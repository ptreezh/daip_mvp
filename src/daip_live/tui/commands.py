"""增强的TUI辩论命令处理模块 - 完全对齐原始辩论系统功能"""

import argparse
import shlex
from typing import Any


class DebateCommands:
    """增强的辩论相关命令 - 完全对齐原始辩论系统"""

    def __init__(self, tui_instance):
        self.tui = tui_instance
        self._debate_is_running = False
        self._debate_is_paused = False

    def handle_debate_command(self, args: str) -> None:
        """辩论系统命令处理 - 支持增强功能"""
        args_list = args.split()
        if not args_list:
            self._show_help()
            return

        subcommand = args_list[0]
        remaining_args = " ".join(args_list[1:])

        if subcommand == "start":
            self._handle_start_command(remaining_args)
        elif subcommand == "history":
            self._handle_debate_history_command(remaining_args)
        elif subcommand == "search":
            self._handle_search_command(remaining_args)
        elif subcommand == "pause":
            self._handle_pause_command()
        elif subcommand == "resume":
            self._handle_resume_command()
        elif subcommand == "export":
            self._handle_export_command(remaining_args)
        elif subcommand == "status":
            self._handle_status_command()
        elif subcommand == "switch-model":
            self._handle_switch_model_command(remaining_args)
        elif subcommand == "memory-stats":
            self._handle_memory_stats_command()
        elif subcommand == "stop":
            self._handle_stop_command()
        else:
            self.tui._update_log_view(
                f"[bold red]> Unknown debate subcommand: {subcommand}[/bold red]"
            )
            self._show_help()

    def _show_help(self) -> None:
        """显示详细的辩论命令帮助"""
        help_text = """
[bold cyan]🎯 DAIP-LIVE 辩论系统命令帮助[/bold cyan]

[dim]基础命令：[/dim]
  [yellow]/debate start <topic> [options][/yellow]     [dim]启动新辩论[/dim]
    [dim]示例: /debate start AI伦理问题 --roles philosopher,engineer --rounds 3[/dim]

[dim]增强选项：[/dim]
  [cyan]--roles <role1,role2,...>[/cyan]         [dim]指定参与角色（默认：philosopher,engineer）[/dim]
  [cyan]--rounds <number>[/cyan]                  [dim]辩论轮次（默认：3）[/dim]
  [cyan]--models <role=model,...>[/cyan]           [dim]自定义角色模型配置[/dim]
  [cyan]--optimization <level>[/cyan]              [dim]优化级别（basic|standard|full）[/dim]
  [cyan]--memory-system <type>[/cyan]             [dim]记忆系统类型（basic|advanced）[/dim]

[dim]控制命令：[/dim]
  [yellow]/debate pause[/yellow]                          [dim]暂停当前辩论[/dim]
  [yellow]/debate resume[/yellow]                         [dim]恢复辩论[/dim]
  [yellow]/debate status[/yellow]                         [dim]查看辩论状态[/dim]
  [yellow]/debate stop[/yellow]                          [dim]停止辩论[/dim]
  [yellow]/debate export <format>[/yellow]               [dim]导出辩论结果（json|markdown|text）[/dim]
  [yellow]/debate switch-model <role=model>[/yellow]      [dim]动态切换角色模型[/dim]
  [yellow]/debate memory-stats[/yellow]                   [dim]查看记忆系统统计[/dim]

[dim]查询命令：[/dim]
  [yellow]/debate history list[/yellow]                     [dim]列出辩论历史[/dim]
  [yellow]/debate history view <session_id>[/yellow]     [dim]查看特定辩论详情[/dim]
  [yellow]/debate search <keywords>[/yellow]                [dim]搜索辩论记录[/dim]

[dim]增强功能示例：[/dim]
  [green]/debate start AI伦理 --models philosopher=ollama/llama3:instruct,engineer=ollama/qwen:latest[/green]
  [green]/debate start 技术 --optimization full --memory-system advanced[/green]
  [green]/debate export json --include-memory[/green]
        """  # noqa: E501
        self.tui._update_log_view(help_text)

    def _handle_start_command(self, args: str) -> None:
        """处理辩论开始命令 - 增强参数解析"""
        try:
            # 使用shlex正确解析参数
            parser = argparse.ArgumentParser(description="启动辩论", add_help=False)
            parser.add_argument("topic", nargs="*", help="辩论主题")
            parser.add_argument("--roles", type=str, help="参与角色")
            parser.add_argument("--rounds", type=int, help="辩论轮次")
            parser.add_argument("--models", type=str, help="模型配置")
            parser.add_argument(
                "--optimization",
                type=str,
                choices=["basic", "standard", "full"],
                help="优化级别",
                default="standard",
            )
            parser.add_argument(
                "--memory-system",
                type=str,
                choices=["basic", "advanced"],
                help="记忆系统类型",
                default="standard",
            )

            # 解析参数
            parsed_args = parser.parse_args(shlex.split(args) if args else [])

            topic = " ".join(parsed_args.topic) if parsed_args.topic else ""
            if not topic.strip():
                self.tui._update_log_view(
                    "[bold red]> 错误: 必须提供辩论主题[/bold red]"
                )
                return

            # 设置参数
            roles = parsed_args.roles or "philosopher,engineer"
            rounds = parsed_args.rounds or 3
            models = parsed_args.models
            optimization = parsed_args.optimization
            memory_system = parsed_args.memory_system

            # 显示配置信息
            self.tui._update_log_view(f"[bold cyan]🚀 启动辩论：{topic}[/bold cyan]")
            self.tui._update_log_view(f"[dim]角色：{roles}[/dim]")
            self.tui._update_log_view(f"[dim]轮次：{rounds}[/dim]")
            self.tui._update_log_view(f"[dim]优化级别：{optimization}[/dim]")
            if models:
                self.tui._update_log_view(f"[dim]模型配置：{models}[/dim]")
            self.tui._update_log_view(f"[dim]记忆系统：{memory_system}[/dim]")

            # 启动增强辩论
            self._start_enhanced_debate(
                topic,
                roles,
                rounds,
                {
                    "models": models,
                    "optimization": optimization,
                    "memory_system": memory_system,
                },
            )

        except Exception as e:
            self.tui._update_log_view(f"[bold red]> 参数解析错误: {e}[/bold red]")
            self.tui._update_log_view(
                "[dim]使用 /debate start --help 查看详细帮助[/dim]"
            )

    def _handle_pause_command(self) -> None:
        """处理暂停命令"""
        if hasattr(self.tui, "_debate_manager") and self.tui._debate_manager:
            if hasattr(self.tui._debate_manager, "pause_debate"):
                self.tui._debate_manager.pause_debate()
                self.tui._update_log_view("[yellow]⏸️ 辩论已暂停[/yellow]")
            else:
                self.tui._update_log_view("[red]❌ 当前辩论管理器不支持暂停功能[/red]")
        else:
            self.tui._update_log_view("[red]❌ 没有进行中的辩论[/red]")

    def _handle_resume_command(self) -> None:
        """处理恢复命令"""
        if hasattr(self.tui, "_debate_manager") and self.tui._debate_manager:
            if hasattr(self.tui._debate_manager, "resume_debate"):
                self.tui._debate_manager.resume_debate()
                self.tui._update_log_view("[green]▶️ 辩论已恢复[/green]")
            else:
                self.tui._update_log_view("[red]❌ 当前辩论管理器不支持恢复功能[/red]")
        else:
            self.tui._update_log_view("[red]❌ 没有暂停的辩论[/red]")

    def _handle_stop_command(self) -> None:
        """处理停止命令"""
        if hasattr(self.tui, "_debate_manager") and self.tui._debate_manager:
            if hasattr(self.tui._debate_manager, "stop_debate"):
                self.tui._debate_manager.stop_debate()
                self.tui._update_log_view("[red]⏹️ 辩论已停止[/red]")
                self._debate_is_running = False
            else:
                self.tui._update_log_view("[red]❌ 当前辩论管理器不支持停止功能[/red]")
        else:
            self.tui._update_log_view("[red]❌ 没有进行中的辩论[/red]")

    def _handle_export_command(self, args: str) -> None:
        """处理导出命令"""
        args_list = args.split() if args else []
        format_type = args_list[0] if args_list else "text"

        valid_formats = ["json", "markdown", "text"]
        if format_type not in valid_formats:
            self.tui._update_log_view(f"[red]❌ 不支持的导出格式: {format_type}[/red]")
            self.tui._update_log_view(
                f"[dim]支持的格式: {', '.join(valid_formats)}[/dim]"
            )
            return

        self.tui._update_log_view(
            f"[cyan]📤 准备导出辩论结果为 {format_type} 格式...[/cyan]"
        )

        # TODO: 实现实际的导出逻辑
        self.tui._update_log_view("[yellow]⚠️ 导出功能开发中...[/yellow]")

    def _handle_status_command(self) -> None:
        """处理状态命令"""
        if hasattr(self.tui, "_debate_manager") and self.tui._debate_manager:
            if hasattr(self.tui._debate_manager, "get_debate_status"):
                status = self.tui._debate_manager.get_debate_status()
                self._display_debate_status(status)
            else:
                self.tui._update_log_view("[red]❌ 当前辩论管理器不支持状态查询[/red]")
        else:
            self.tui._update_log_view("[red]❌ 没有进行中的辩论[/red]")

    def _handle_switch_model_command(self, args: str) -> None:
        """处理模型切换命令"""
        if not args.strip():
            self.tui._update_log_view(
                "[red]❌ 请提供模型切换配置，例如: philosopher=ollama/llama3:instruct[/red]"  # noqa: E501
            )
            return

        try:
            # 解析模型配置
            model_config = {}
            for pair in args.split(","):
                if "=" in pair:
                    role, model = pair.split("=", 1)
                    model_config[role.strip()] = model.strip()

            if hasattr(self.tui, "_debate_manager") and self.tui._debate_manager:
                if hasattr(self.tui._debate_manager, "switch_role_model"):
                    self.tui._debate_manager.switch_role_model(model_config)
                    self.tui._update_log_view("[green]🔄 模型切换成功[/green]")
                    for role, model in model_config.items():
                        self.tui._update_log_view(f"[dim]  {role}: {model}[/dim]")
                else:
                    self.tui._update_log_view(
                        "[red]❌ 当前辩论管理器不支持动态模型切换[/red]"
                    )
            else:
                self.tui._update_log_view("[red]❌ 没有进行中的辩论[/red]")

        except Exception as e:
            self.tui._update_log_view(f"[red]❌ 模型切换失败: {e}[/red]")

    def _handle_memory_stats_command(self) -> None:
        """处理记忆统计命令"""
        if hasattr(self.tui, "_debate_manager") and self.tui._debate_manager:
            if hasattr(self.tui._debate_manager, "get_memory_statistics"):
                stats = self.tui._debate_manager.get_memory_statistics()
                self._display_memory_stats(stats)
            else:
                self.tui._update_log_view("[red]❌ 当前辩论管理器不支持记忆统计[/red]")
        else:
            self.tui._update_log_view("[red]❌ 没有活跃的辩论系统[/red]")

    def _start_enhanced_debate(
        self, topic: str, roles: str, rounds: int, options: dict
    ) -> None:
        """启动增强辩论"""
        try:
            # 检查TUI是否有辩论管理器
            if not hasattr(self.tui, "_debate_manager") or not self.tui._debate_manager:
                self.tui._update_log_view("[red]❌ 辩论管理器未初始化[/red]")
                return

            # 设置优化选项
            if hasattr(self.tui._debate_manager, "set_optimization_options"):
                self.tui._debate_manager.set_optimization_options(options)

            # 启动辩论（通过TUI的异步方法）
            if hasattr(self.tui, "_start_debate") and callable(self.tui._start_debate):
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.tui._start_debate(topic, roles, rounds))
                else:
                    loop.run_until_complete(
                        self.tui._start_debate(topic, roles, rounds)
                    )
            else:
                self.tui._update_log_view("[red]❌ TUI辩论启动方法不可用[/red]")

        except Exception as e:
            self.tui._update_log_view(f"[red]❌ 辩论启动失败: {e}[/red]")

    def _display_debate_status(self, status: dict[str, Any]) -> None:
        """显示辩论状态"""
        self.tui._update_log_view("[bold cyan]📊 辩论状态信息[/bold cyan]")

        if "is_running" in status:
            status_text = "运行中" if status["is_running"] else "已停止"
            self.tui._update_log_view(f"[dim]状态: {status_text}[/dim]")

        if "current_round" in status:
            self.tui._update_log_view(f"[dim]当前轮次: {status['current_round']}[/dim]")

        if "total_rounds" in status:
            self.tui._update_log_view(f"[dim]总轮次: {status['total_rounds']}[/dim]")

        if "participants" in status:
            participants = ", ".join(status["participants"])
            self.tui._update_log_view(f"[dim]参与者: {participants}[/dim]")

        if "optimization_level" in status:
            self.tui._update_log_view(
                f"[dim]优化级别: {status['optimization_level']}[/dim]"
            )

    def _display_memory_stats(self, stats: dict[str, Any]) -> None:
        """显示记忆统计"""
        self.tui._update_log_view("[bold cyan]🧠 记忆系统统计[/bold cyan]")

        if "total_entries" in stats:
            self.tui._update_log_view(f"[dim]总条目: {stats['total_entries']}[/dim]")

        if "shared_facts" in stats:
            self.tui._update_log_view(f"[dim]共享事实: {stats['shared_facts']}[/dim]")

        if "role_memories" in stats:
            for role, count in stats["role_memories"].items():
                self.tui._update_log_view(f"[dim]{role}: {count} 条记忆[/dim]")

        if "consensus_level" in stats:
            consensus = stats["consensus_level"]
            self.tui._update_log_view(f"[dim]共识度: {consensus:.2%}[/dim]")


class SearchCommands:
    """搜索相关命令 - 保持原有功能"""

    def __init__(self, tui_instance):
        self.tui = tui_instance

    def search_conversation_history(self, query: str) -> None:
        """搜索历史对话记录中的相关信息"""
        try:
            self.tui._update_log_view(
                "[bold cyan]🔍 正在搜索历史对话中的相关信息...[/bold cyan]"
            )
            self.tui._update_log_view(f"[dim]📝 搜索关键词: {query}[/dim]")
            self.tui._update_log_view("")

            # 获取所有会话
            all_sessions = (
                self.tui._session_manager.list_sessions()
                if hasattr(self.tui, "_session_manager")
                else []
            )
            if not all_sessions:
                self.tui._update_log_view("[yellow]📚 未找到任何历史会话记录[/yellow]")
                return

            # 搜索相关的会话和对话
            found_results = []
            query_lower = query.lower()

            for session in all_sessions:
                relevance = 0

                # 检查会话目标/主题的相关性
                if session.goal and query_lower in session.goal.lower():
                    relevance += 10

                # 检查会话摘要的相关性
                if session.summary and query_lower in session.summary.lower():
                    relevance += 8

                # 如果相关性大于0，添加到结果中
                if relevance > 0:
                    found_results.append({"session": session, "relevance": relevance})

            # 按相关性排序
            found_results.sort(key=lambda x: x["relevance"], reverse=True)

            # 显示搜索结果
            if found_results:
                self.tui._update_log_view(
                    f"[bold green]📋 找到 {len(found_results)} 个相关会话：[/bold green]"  # noqa: E501
                )
                self.tui._update_log_view("")

                for i, result in enumerate(found_results[:10], 1):  # 最多显示前10个结果
                    session = result["session"]
                    relevance = result["relevance"]

                    self.tui._update_log_view(
                        f"[bold cyan]{i}. 会话 {session.id[:8]}...[/bold cyan] (相关性: {relevance})"  # noqa: E501
                    )
                    if session.goal:
                        self.tui._update_log_view(f"[dim]   目标: {session.goal}[/dim]")
                    if session.summary:
                        self.tui._update_log_view(
                            f"[dim]   摘要: {session.summary}[/dim]"
                        )
                    self.tui._update_log_view("")
            else:
                self.tui._update_log_view("[yellow]📚 未找到相关的历史会话[/yellow]")

        except Exception as e:
            self.tui._update_log_view(
                f"[bold red]❌ 搜索历史对话时发生错误: {str(e)}[/bold red]"
            )


"""通用TUI工具命令处理模块"""

from typing import Any  # noqa: E402


class UtilityCommands:
    """TUI通用工具命令处理器"""

    def __init__(self, tui_instance):
        """初始化工具命令处理器"""
        self.tui = tui_instance

    def handle_clear_command(self) -> None:
        """处理清屏命令"""
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view("[dim]屏幕已清空[/dim]")

    def handle_help_command(self, topic: str = None) -> None:
        """处理帮助命令"""
        if hasattr(self.tui, "_update_log_view"):
            if topic:
                self.tui._update_log_view(
                    f"[bold cyan]📚 帮助主题: {topic}[/bold cyan]"
                )
            else:
                self.tui._update_log_view("[bold cyan]💡 可用命令:[/bold cyan]")
                self.tui._update_log_view("[dim]  /debate - 辩论系统[/dim]")
                self.tui._update_log_view("[dim]  /search - 搜索历史[/dim]")
                self.tui._update_log_view("[dim]  /clear - 清空屏幕[/dim]")
                self.tui._update_log_view("[dim]  /help - 显示帮助[/dim]")

    def handle_theme_command(self, theme: str) -> None:
        """处理主题切换命令"""
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view(f"[cyan]🎨 主题切换到: {theme}[/cyan]")

    def handle_status_command(self) -> None:
        """处理状态查询命令"""
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view("[bold blue]📊 系统状态[/bold blue]")
            if hasattr(self.tui, "_debate_manager") and self.tui._debate_manager:
                self.tui._update_log_view("[dim]  辩论管理器: 已连接[/dim]")
            else:
                self.tui._update_log_view("[dim]  辩论管理器: 未连接[/dim]")


"""统一TUI命令处理器模块"""

from typing import Any  # noqa: E402


class TUICommandHandler:
    """统一TUI命令处理模块"""

    def __init__(self, tui_instance):
        """初始化命令处理器"""
        from .commands import SearchCommands, UtilityCommands
        from .enhanced_commands import DebateCommands

        self.tui = tui_instance
        self.debate_commands = DebateCommands(tui_instance)
        self.search_commands = SearchCommands(tui_instance)
        self.utility_commands = UtilityCommands(tui_instance)

    def process_command(self, command_text: str) -> bool:
        """处理TUI命令，返回是否处理成功"""
        if not command_text or not command_text.strip():
            return False

        command_text = command_text.strip()

        # 辩论相关命令
        if command_text.startswith("/debate "):
            args = command_text[8:].strip()
            self.debate_commands.handle_debate_command(args)
            return True

        # 搜索相关命令
        elif command_text.startswith("/search "):
            args = command_text[8:].strip()
            self.search_commands.search_conversation_history(args)
            return True

        # 清屏命令
        elif command_text == "/clear":
            self.utility_commands.handle_clear_command()
            return True

        # 帮助命令
        elif command_text.startswith("/help"):
            topic = command_text[6:].strip() if len(command_text) > 6 else None
            self.utility_commands.handle_help_command(topic)
            return True

        # 主题命令
        elif command_text.startswith("/theme "):
            theme = command_text[7:].strip()
            self.utility_commands.handle_theme_command(theme)
            return True

        # 状态命令
        elif command_text == "/status":
            self.utility_commands.handle_status_command()
            return True

        return False

    def get_available_commands(self) -> list[str]:
        """获取可用命令列表"""
        return [
            "/debate start <topic> - 启动辩论",
            "/debate status - 查看辩论状态",
            "/debate pause - 暂停辩论",
            "/debate resume - 恢复辩论",
            "/debate stop - 停止辩论",
            "/search <query> - 搜索历史",
            "/clear - 清空屏幕",
            "/help [topic] - 显示帮助",
            "/theme <name> - 切换主题",
            "/status - 系统状态",
        ]


"""Wiki相关命令处理模块"""

from typing import Any  # noqa: E402


class WikiCommands:
    """Wiki相关命令处理器"""

    def __init__(self, tui_instance):
        """初始化Wiki命令处理器"""
        self.tui = tui_instance

    def handle_wiki_command(self, args: str) -> None:
        """处理Wiki命令"""
        if not args.strip():
            self._show_wiki_help()
            return

        args_list = args.split() if args else []
        if not args_list:
            self._show_wiki_help()
            return

        subcommand = args_list[0]
        remaining_args = " ".join(args_list[1:])

        if subcommand == "add":
            self._handle_wiki_add(remaining_args)
        elif subcommand == "create":
            self._handle_wiki_create(remaining_args)
        elif subcommand == "search":
            self._handle_wiki_search(remaining_args)
        elif subcommand == "list":
            self._handle_wiki_list()
        elif subcommand == "delete":
            self._handle_wiki_delete(remaining_args)
        else:
            if hasattr(self.tui, "_update_log_view"):
                self.tui._update_log_view(f"[red]❌ 未知Wiki命令: {subcommand}[/red]")

    def _show_wiki_help(self) -> None:
        """显示Wiki命令帮助"""
        help_text = """
[bold cyan]📚 Wiki系统命令帮助[/bold cyan]

[dim]可用命令：[/dim]
[yellow]/wiki add <title> <content>[/yellow]     [dim]添加Wiki页面[/dim]
[yellow]/wiki create <title>[/yellow]           [dim]创建Wiki页面（多角色协作）[/dim]
[yellow]/wiki search <keywords>[/yellow]       [dim]搜索Wiki内容[/dim]
[yellow]/wiki list[/yellow]                   [dim]列出所有Wiki页面[/dim]
[yellow]/wiki delete <title>[/yellow]          [dim]删除Wiki页面[/dim]

[dim]示例：[/dim]
[cyan]/wiki add "Python技巧" "Python的最佳实践和技巧"[/cyan]
[cyan]/wiki create "人工智能基础"[/cyan]
[cyan]/wiki search "机器学习"[/cyan]
        """
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view(help_text)

    def _handle_wiki_add(self, args: str) -> None:
        """处理Wiki添加命令"""
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view("[green]📝 添加Wiki页面功能开发中...[/green]")

    def _handle_wiki_search(self, args: str) -> None:
        """处理Wiki搜索命令"""
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view(f"[cyan]🔍 搜索Wiki内容: {args}[/cyan]")

    def _handle_wiki_list(self) -> None:
        """处理Wiki列表命令"""
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view("[blue]📋 Wiki页面列表功能开发中...[/blue]")

    def _handle_wiki_delete(self, args: str) -> None:
        """处理Wiki删除命令"""
        if hasattr(self.tui, "_update_log_view"):
            self.tui._update_log_view(f"[red]🗑️ 删除Wiki页面: {args}[/red]")

    def _handle_wiki_create(self, title: str) -> None:
        """处理Wiki创建命令"""
        # 调用TUI主类的异步Wiki创建方法
        if hasattr(self.tui, "_handle_wiki_create"):
            # 在Textual应用中，使用call_later来调度异步方法
            import asyncio

            if hasattr(self.tui, "call_later"):
                # 使用TUI的call_later方法来调度异步操作
                async def call_create():
                    await self.tui._handle_wiki_create(title)

                self.tui.call_later(call_create)
            else:
                # 直接使用异步任务
                try:
                    asyncio.create_task(self.tui._handle_wiki_create(title))
                except RuntimeError:
                    # 如果没有运行事件循环，直接显示错误
                    if hasattr(self.tui, "_update_log_view"):
                        self.tui._update_log_view(
                            f"[yellow]⚠️ 无法启动Wiki创建任务: {title}[/yellow]"
                        )
        else:
            if hasattr(self.tui, "_update_log_view"):
                self.tui._update_log_view(
                    f"[yellow]⚠️ Wiki创建功能未找到: {title}[/yellow]"
                )
