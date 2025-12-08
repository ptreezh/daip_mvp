"""
TUI交互式角色创建功能的TUI集成
"""

from typing import Dict, Any
import asyncio
from .interactive_role_creation import InteractiveRoleCreationService


class TUIRoleCommandHandler:
    """
    TUI角色命令处理器
    职责：处理TUI中的角色相关命令
    """
    def __init__(self, tui_instance, role_creation_service: InteractiveRoleCreationService):
        self.tui = tui_instance
        self.role_creation_service = role_creation_service
        # 存储TUI实例的活动会话
        self.active_sessions = {}

    def handle_role_command(self, args: str) -> None:
        """处理角色命令"""
        args_list = args.split()
        if not args_list or args_list[0] in ["list", ""]:
            self._handle_role_list()
        elif args_list[0] == "interactive":
            self._handle_role_interactive(" ".join(args_list[1:]))
        elif args_list[0] == "switch":
            self._handle_role_switch(" ".join(args_list[1:]))
        elif args_list[0] == "show":
            self._handle_role_show(" ".join(args_list[1:]))
        elif args_list[0] == "create":
            self._handle_role_create(" ".join(args_list[1:]))
        else:
            self.tui._update_log_view("[bold red]❌ 未知的角色子命令[/bold red]")
            self._show_role_help()

    def _handle_role_list(self) -> None:
        """显示所有可用角色"""
        self.tui._update_log_view("[bold cyan]🎭 所有AI角色[/bold cyan]")
        try:
            roles = self.tui._role_manager.list_roles()
            if not roles:
                self.tui._update_log_view("[yellow]⚠️ 未找到任何角色，请先创建角色[/yellow]")
                return
                
            for role in roles:
                self.tui._update_log_view(f"[dim]  • {role.name} - {role.persona[:50]}...[/dim]")
                
            self.tui._update_log_view("[dim]使用 /role interactive 创建新角色[/dim]")
            self.tui._update_log_view("[dim]使用 /role switch <角色名> 切换角色[/dim]")
            self.tui._update_log_view("[dim]使用 /role show <角色名> 查看角色详细信息[/dim]")
        except Exception as e:
            self.tui._update_log_view(f"[red]❌ 加载角色列表失败: {e}[/red]")

    def _handle_role_interactive(self, user_query: str) -> None:
        """处理交互式角色创建"""
        if not user_query.strip():
            self.tui._update_log_view("[bold cyan]🎭 开始交互式角色创建向导...[/bold cyan]")
            self.tui._update_log_view("[dim]请输入您想要创建的角色描述：[/dim]")
            self.tui._update_log_view("[dim]例如：'数据科学家'、'法律顾问'、'编程导师'等[/dim]")
            # 设置TUI状态为角色创建模式
            self.tui._set_interactive_role_creation_mode()
            return

        # 直接启动角色创建流程
        self.tui._update_log_view(f"[bold cyan]🎭 正在分析您的角色需求: {user_query}[/bold cyan]")
        self.tui._update_log_view("[dim]🔄 AI正在生成角色建议...[/dim]")
        
        # 异步处理角色创建
        task = asyncio.create_task(self._process_role_creation(user_query))
        self.tui._background_tasks.add(task)
        task.add_done_callback(self.tui._background_tasks.discard)

    async def _process_role_creation(self, user_query: str) -> None:
        """异步处理角色创建"""
        try:
            # 启动角色创建流程
            response = self.role_creation_service.start_creation(user_query)
            
            # 更新UI反馈
            if response.status == 'success':
                self._display_role_suggestion(response.suggested_role, response.session_id)
            elif response.status == 'error':
                self.tui._update_log_view(f"[red]❌ {response.message}[/red]")
            else:
                self.tui._update_log_view(f"[yellow]⚠️ {response.message}[/yellow]")
                
        except Exception as e:
            self.tui._update_log_view(f"[red]❌ 角色创建过程中发生错误: {e}[/red]")

    def _display_role_suggestion(self, suggested_role: Dict[str, Any], session_id: str) -> None:
        """显示角色建议"""
        self.tui._update_log_view(f"[green]✅ AI生成的角色建议:[/green]")
        self.tui._update_log_view(f"[bold]角色名称:[/bold] {suggested_role['name']}")
        self.tui._update_log_view(f"[bold]角色人设:[/bold] {suggested_role['persona']}")
        self.tui._update_log_view(f"[bold]推荐工具:[/bold] {', '.join(suggested_role['tools']) if suggested_role['tools'] else '无'}")
        
        # 询问用户是否确认
        self.tui._update_log_view("[dim]----------[/dim]")
        self.tui._update_log_view("[dim]使用以下命令:[/dim]")
        self.tui._update_log_view(f"[dim]  /role confirm {session_id} - 确认创建此角色[/dim]")
        self.tui._update_log_view(f"[dim]  /role modify {session_id} - 修改角色配置[/dim]")

    def _handle_role_switch(self, role_name: str) -> None:
        """切换到指定角色"""
        if not role_name.strip():
            self.tui._update_log_view("[yellow]⚠️ 请提供角色名称[/yellow]")
            self.tui._update_log_view("[dim]用法: /role switch <角色名>[/dim]")
            return
            
        try:
            role = self.tui._role_manager.get_role_by_name(role_name)
            if role:
                # 在实际应用中，这里需要根据具体场景设置当前角色
                self.tui._current_role = role
                self.tui._update_log_view(f"[green]✅ 已切换到角色: {role.name}[/green]")
                self.tui._update_log_view(f"[dim]角色描述: {role.persona}[/dim]")
            else:
                self.tui._update_log_view(f"[red]❌ 角色 '{role_name}' 不存在[/red]")
                self.tui._update_log_view("[dim]使用 /role list 查看可用角色[/dim]")
        except Exception as e:
            self.tui._update_log_view(f"[red]❌ 切换角色失败: {e}[/red]")

    def _handle_role_show(self, role_name: str) -> None:
        """显示角色详细信息"""
        if not role_name.strip():
            self.tui._update_log_view("[yellow]⚠️ 请提供角色名称[/yellow]")
            self.tui._update_log_view("[dim]用法: /role show <角色名>[/dim]")
            return
            
        try:
            role = self.tui._role_manager.get_role_by_name(role_name)
            if role:
                self.tui._update_log_view(f"[bold cyan]👤 角色详情: {role.name}[/bold cyan]")
                self.tui._update_log_view(f"[dim]📋 人设: {role.persona}[/dim]")
                if role.tools:
                    self.tui._update_log_view(f"[dim]🛠️  工具: {', '.join(role.tools)}[/dim]")
            else:
                self.tui._update_log_view(f"[red]❌ 角色 '{role_name}' 不存在[/red]")
        except Exception as e:
            self.tui._update_log_view(f"[red]❌ 获取角色详情失败: {e}[/red]")

    def _handle_role_create(self, params: str) -> None:
        """处理角色创建命令"""
        if not params.strip():
            self.tui._update_log_view("[yellow]⚠️ 请提供角色描述[/yellow]")
            self.tui._update_log_view("[dim]用法: /role create <角色描述>[/dim]")
            self.tui._update_log_view("[dim]例如: /role create 数据科学家[/dim]")
            return

        self._handle_role_interactive(params)

    def handle_role_confirm(self, session_id: str) -> None:
        """处理角色确认"""
        if not session_id.strip():
            self.tui._update_log_view("[red]❌ 请提供会话ID[/red]")
            self.tui._update_log_view("[dim]用法: /role confirm <会话ID>[/dim]")
            return

        try:
            # 调用服务完成角色创建
            response = self.role_creation_service.continue_creation(session_id, {"confirm": True})
            
            if response.status == 'success':
                self.tui._update_log_view(f"[green]🎉 {response.message}[/green]")
            else:
                self.tui._update_log_view(f"[red]❌ {response.message}[/red]")
        except Exception as e:
            self.tui._update_log_view(f"[red]❌ 角色确认失败: {e}[/red]")

    def _show_role_help(self) -> None:
        """显示角色命令帮助"""
        self.tui._update_log_view("[bold blue]🎭 角色管理命令帮助:[/bold blue]")
        self.tui._update_log_view("[dim]  /role list - 列出所有可用角色[/dim]")
        self.tui._update_log_view("[dim]  /role interactive <描述> - 交互式创建角色[/dim]")
        self.tui._update_log_view("[dim]  /role create <描述> - 创建角色[/dim]")
        self.tui._update_log_view("[dim]  /role show <角色名> - 显示角色详情[/dim]")
        self.tui._update_log_view("[dim]  /role switch <角色名> - 切换当前角色[/dim]")
        self.tui._update_log_view("[dim]  /role confirm <会话ID> - 确认角色创建[/dim]")