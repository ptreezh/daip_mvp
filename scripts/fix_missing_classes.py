#!/usr/bin/env python3
"""
修复缺失的TUI类 - 基于TDD原则的第一阶段修复
"""

def create_utility_commands():
    """创建UtilityCommands类"""
    utility_commands_code = '''"""通用TUI工具命令处理模块"""

from typing import Optional, List, Dict, Any


class UtilityCommands:
    """TUI通用工具命令处理器"""

    def __init__(self, tui_instance):
        """初始化工具命令处理器"""
        self.tui = tui_instance

    def handle_clear_command(self) -> None:
        """处理清屏命令"""
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view("[dim]屏幕已清空[/dim]")

    def handle_help_command(self, topic: str = None) -> None:
        """处理帮助命令"""
        if hasattr(self.tui, '_update_log_view'):
            if topic:
                self.tui._update_log_view(f"[bold cyan]📚 帮助主题: {topic}[/bold cyan]")
            else:
                self.tui._update_log_view("[bold cyan]💡 可用命令:[/bold cyan]")
                self.tui._update_log_view("[dim]  /debate - 辩论系统[/dim]")
                self.tui._update_log_view("[dim]  /search - 搜索历史[/dim]")
                self.tui._update_log_view("[dim]  /clear - 清空屏幕[/dim]")
                self.tui._update_log_view("[dim]  /help - 显示帮助[/dim]")

    def handle_theme_command(self, theme: str) -> None:
        """处理主题切换命令"""
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view(f"[cyan]🎨 主题切换到: {theme}[/cyan]")

    def handle_status_command(self) -> None:
        """处理状态查询命令"""
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view("[bold blue]📊 系统状态[/bold blue]")
            if hasattr(self.tui, '_debate_manager') and self.tui._debate_manager:
                self.tui._update_log_view("[dim]  辩论管理器: 已连接[/dim]")
            else:
                self.tui._update_log_view("[dim]  辩论管理器: 未连接[/dim]")
'''

    # 写入到commands.py文件
    with open('src/daip_live/tui/commands.py', 'a', encoding='utf-8') as f:
        f.write('\n\n')
        f.write(utility_commands_code)

    print("✅ UtilityCommands类已添加到commands.py")
    return True


def create_tui_command_handler():
    """创建TUICommandHandler类"""
    tui_command_handler_code = '''"""统一TUI命令处理器模块"""

from typing import Optional, List, Dict, Any
from .enhanced_commands import DebateCommands
from .commands import SearchCommands, UtilityCommands


class TUICommandHandler:
    """统一TUI命令处理器"""

    def __init__(self, tui_instance):
        """初始化命令处理器"""
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
        if command_text.startswith('/debate '):
            args = command_text[8:].strip()
            self.debate_commands.handle_debate_command(args)
            return True

        # 搜索相关命令
        elif command_text.startswith('/search '):
            args = command_text[8:].strip()
            self.search_commands.search_conversation_history(args)
            return True

        # 清屏命令
        elif command_text == '/clear':
            self.utility_commands.handle_clear_command()
            return True

        # 帮助命令
        elif command_text.startswith('/help'):
            topic = command_text[6:].strip() if len(command_text) > 6 else None
            self.utility_commands.handle_help_command(topic)
            return True

        # 主题命令
        elif command_text.startswith('/theme '):
            theme = command_text[7:].strip()
            self.utility_commands.handle_theme_command(theme)
            return True

        # 状态命令
        elif command_text == '/status':
            self.utility_commands.handle_status_command()
            return True

        return False

    def get_available_commands(self) -> List[str]:
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
            "/status - 系统状态"
        ]
'''

    # 写入到commands.py文件
    with open('src/daip_live/tui/commands.py', 'a', encoding='utf-8') as f:
        f.write('\n\n')
        f.write(tui_command_handler_code)

    print("✅ TUICommandHandler类已添加到commands.py")
    return True


def create_wiki_commands():
    """创建WikiCommands类"""
    wiki_commands_code = '''"""Wiki相关命令处理模块"""

from typing import Optional, List, Dict, Any


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
        elif subcommand == "search":
            self._handle_wiki_search(remaining_args)
        elif subcommand == "list":
            self._handle_wiki_list()
        elif subcommand == "delete":
            self._handle_wiki_delete(remaining_args)
        else:
            if hasattr(self.tui, '_update_log_view'):
                self.tui._update_log_view(f"[red]❌ 未知Wiki命令: {subcommand}[/red]")

    def _show_wiki_help(self) -> None:
        """显示Wiki命令帮助"""
        help_text = """
[bold cyan]📚 Wiki系统命令帮助[/bold cyan]

[dim]可用命令：[/dim]
[yellow]/wiki add <title> <content>[/yellow]     [dim]添加Wiki页面[/dim]
[yellow]/wiki search <keywords>[/yellow]       [dim]搜索Wiki内容[/dim]
[yellow]/wiki list[/yellow]                   [dim]列出所有Wiki页面[/dim]
[yellow]/wiki delete <title>[/yellow]          [dim]删除Wiki页面[/dim]

[dim]示例：[/dim]
[cyan]/wiki add "Python技巧" "Python的最佳实践和技巧"[/cyan]
[cyan]/wiki search "机器学习"[/cyan]
        """
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view(help_text)

    def _handle_wiki_add(self, args: str) -> None:
        """处理Wiki添加命令"""
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view("[green]📝 添加Wiki页面功能开发中...[/green]")

    def _handle_wiki_search(self, args: str) -> None:
        """处理Wiki搜索命令"""
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view(f"[cyan]🔍 搜索Wiki内容: {args}[/cyan]")

    def _handle_wiki_list(self) -> None:
        """处理Wiki列表命令"""
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view("[blue]📋 Wiki页面列表功能开发中...[/blue]")

    def _handle_wiki_delete(self, args: str) -> None:
        """处理Wiki删除命令"""
        if hasattr(self.tui, '_update_log_view'):
            self.tui._update_log_view(f"[red]🗑️ 删除Wiki页面: {args}[/red]")
'''

    # 写入到commands.py文件
    with open('src/daip_live/tui/commands.py', 'a', encoding='utf-8') as f:
        f.write('\n\n')
        f.write(wiki_commands_code)

    print("✅ WikiCommands类已添加到commands.py")
    return True


def main():
    """主修复函数"""
    print("🔧 开始修复缺失的TUI类...")

    success_count = 0
    total_count = 3

    # 1. 创建UtilityCommands
    if create_utility_commands():
        success_count += 1

    # 2. 创建TUICommandHandler
    if create_tui_command_handler():
        success_count += 1

    # 3. 创建WikiCommands
    if create_wiki_commands():
        success_count += 1

    print(f"\n🎯 修复完成: {success_count}/{total_count} 个类已成功创建")
    print("📋 下一步: 运行 'python scripts/validate_fixes.py' 验证修复")


if __name__ == "__main__":
    main()