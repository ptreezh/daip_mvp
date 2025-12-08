"""TUI自动补全系统 - 渐进式信息披露实现"""

from typing import List


class TUIAutocomplete:
    """TUI自动补全系统，支持渐进式信息披露"""

    def __init__(self, tui_instance):
        self.tui = tui_instance

    def get_command_suggestions(self, parts: List[str]) -> List[str]:
        """获取命令自动补全建议"""
        if not parts:
            return []

        # Case 1: General command completion
        if len(parts) == 1:
            return self._get_main_command_suggestions(parts[0])

        # Case 2: Subcommand completion for specific commands
        return self._get_subcommand_suggestions(parts)

    def _get_main_command_suggestions(self, prefix: str) -> List[str]:
        """获取主要命令的建议"""
        suggestions = [
            cmd for cmd, help_text in self.tui._available_commands
            if cmd.startswith(prefix)
        ]
        return suggestions

    def _get_subcommand_suggestions(self, parts: List[str]) -> List[str]:
        """获取子命令的建议，支持渐进式信息披露"""
        command = parts[0]

        if command == "/debate":
            return self._get_debate_suggestions(parts)
        elif command == "/doc":
            return self._get_doc_suggestions(parts)
        elif command == "/wiki":
            return self._get_wiki_suggestions(parts)
        elif command == "/role":
            return self._get_role_suggestions(parts)
        elif command == "/knowledge":
            return self._get_knowledge_suggestions(parts)
        elif command == "/compact":
            return self._get_compact_suggestions(parts)
        elif command == "/permission":
            return self._get_permission_suggestions(parts)
        elif command == "/model":
            return self._get_model_suggestions(parts)
        elif command == "/help":
            return self._get_help_suggestions(parts)
        elif command == "/search":
            return self._get_search_suggestions(parts)

        return []

    def _get_debate_suggestions(self, parts: List[str]) -> List[str]:
        """辩论命令的渐进式建议"""
        if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
            # Phase 1: Show only main subcommands
            subcommands = ["start", "history", "search"]
            if len(parts) >= 2:
                prefix = parts[1] if len(parts) == 2 else ""
                suggestions = [f"/debate {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                return suggestions
            else:
                return [f"/debate {cmd}" for cmd in subcommands]

        # Phase 2: Handle subcommand-specific suggestions
        elif len(parts) >= 2:
            subcommand = parts[1]

            if subcommand == "start":
                # For /debate start, ask for topic first, don't show options yet
                if len(parts) == 2:
                    return ["/debate start <辩论主题>"]
                elif len(parts) == 3:
                    # User has entered subcommand but no topic yet
                    if not parts[2]:
                        return ["/debate start <辩论主题>"]
                    # User has entered topic, now show options
                    else:
                        return [
                            f"/debate start {parts[2]}",
                            f"/debate start {parts[2]} --roles <角色配置>",
                            f"/debate start {parts[2]} --rounds <轮次数>"
                        ]
                elif len(parts) >= 4:
                    # User is adding options, provide completion
                    if parts[3] == "--roles" or (len(parts) == 4 and parts[3].startswith("--")):
                        if len(parts) == 4:
                            return [f"/debate start {parts[2]} --roles <角色1,角色2>"]
                        elif len(parts) == 5 and not parts[4]:
                            return [f"/debate start {parts[2]} --roles philosopher,engineer"]
                    elif parts[3] == "--rounds" or (len(parts) == 4 and parts[3].startswith("--")):
                        if len(parts) == 4:
                            return [f"/debate start {parts[2]} --rounds <1-10>"]
                        elif len(parts) == 5 and not parts[4]:
                            return [f"/debate start {parts[2]} --rounds 3"]

            elif subcommand == "history":
                # Phase 2 for history: show subcommands
                if len(parts) == 2:
                    subcommands = ["list", "view"]
                    return [f"/debate history {cmd}" for cmd in subcommands]
                elif len(parts) == 3:
                    if parts[2] == "view":
                        # Show session ID prompt
                        return ["/debate history view <会话ID>"]

            elif subcommand == "search":
                # Phase 2 for search: show query prompt
                if len(parts) == 2:
                    return ["/debate search <搜索关键词>"]

        return []

    def _get_doc_suggestions(self, parts: List[str]) -> List[str]:
        """文档命令的渐进式建议"""
        if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
            # Phase 1: Show only main subcommands
            subcommands = ["search", "download", "list"]
            if len(parts) >= 2:
                prefix = parts[1] if len(parts) == 2 else ""
                suggestions = [f"/doc {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                return suggestions
            else:
                return [f"/doc {cmd}" for cmd in subcommands]

        # Phase 2: Handle subcommand-specific suggestions
        elif len(parts) >= 2:
            subcommand = parts[1]

            if subcommand == "search":
                if len(parts) == 2:
                    return ["/doc search <论文关键词>"]
                elif len(parts) == 3 and not parts[2]:
                    return ["/doc search <论文关键词>"]

            elif subcommand == "download":
                if len(parts) == 2:
                    return ["/doc download <论文ID>"]
                elif len(parts) == 3 and not parts[2]:
                    return ["/doc download <论文ID>"]
                elif len(parts) == 3:
                    # User provided paper ID, now show format option
                    return [
                        f"/doc download {parts[2]}",
                        f"/doc download {parts[2]} --format <格式>"
                    ]
                elif len(parts) >= 4 and parts[3] == "--format":
                    if len(parts) == 4:
                        formats = ["pdf", "docx", "html", "txt"]
                        return [f"/doc download {parts[2]} --format {fmt}" for fmt in formats]

            elif subcommand == "list":
                if len(parts) == 2:
                    return ["/doc list", "/doc list --limit <数量>"]

        return []

    def _get_wiki_suggestions(self, parts: List[str]) -> List[str]:
        """Wiki命令的渐进式建议"""
        if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
            # Phase 1: Show only main subcommands
            subcommands = ["create", "search", "list", "export"]
            if len(parts) >= 2:
                prefix = parts[1] if len(parts) == 2 else ""
                suggestions = [f"/wiki {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                return suggestions
            else:
                return [f"/wiki {cmd}" for cmd in subcommands]

        # Phase 2: Handle subcommand-specific suggestions
        elif len(parts) >= 2:
            subcommand = parts[1]

            if subcommand == "create":
                if len(parts) == 2:
                    return ["/wiki create <页面标题>"]

            elif subcommand == "search":
                if len(parts) == 2:
                    return ["/wiki search <搜索关键词>"]

            elif subcommand == "list":
                if len(parts) == 2:
                    return ["/wiki list", "/wiki list --limit <数量>"]

            elif subcommand == "export":
                if len(parts) == 2:
                    formats = ["markdown", "html", "obsidian", "json"]
                    return [f"/wiki export {fmt}" for fmt in formats]

        return []

    def _get_role_suggestions(self, parts: List[str]) -> List[str]:
        """角色命令的建议"""
        if parts[0] == "/role":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                subcommands = ["list", "view"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/role {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/role {cmd}" for cmd in subcommands]

            elif len(parts) >= 3 and parts[1] == "view":
                # Suggest role names for /role view
                if len(parts) == 3 or (len(parts) == 4 and parts[3] == ""):
                    prefix = parts[2] if len(parts) >= 3 else ""
                    try:
                        roles = self.tui._role_manager.list_roles()
                        role_names = [role.name for role in roles if role.name.startswith(prefix)]
                        return [f"/role view {name}" for name in role_names]
                    except:
                        return []

        return []

    def _get_knowledge_suggestions(self, parts: List[str]) -> List[str]:
        """知识库命令的建议"""
        if parts[0] == "/knowledge":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                subcommands = ["sync", "search"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/knowledge {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/knowledge {cmd}" for cmd in subcommands]

        return []

    def _get_compact_suggestions(self, parts: List[str]) -> List[str]:
        """压缩命令的建议"""
        if parts[0] == "/compact":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                subcommands = ["current", "full", "aggressive"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/compact {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/compact {cmd}" for cmd in subcommands]

        return []

    def _get_permission_suggestions(self, parts: List[str]) -> List[str]:
        """权限命令的建议"""
        if parts[0] == "/permission":
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
                subcommands = ["list", "grant", "revoke", "check", "reset"]
                if len(parts) >= 2:
                    prefix = parts[1] if len(parts) == 2 else ""
                    suggestions = [f"/permission {cmd}" for cmd in subcommands if cmd.startswith(prefix)]
                    return suggestions
                else:
                    return [f"/permission {cmd}" for cmd in subcommands]

        return []

    def _get_model_suggestions(self, parts: List[str]) -> List[str]:
        """模型命令的建议"""
        if parts[0] == "/model":
            # No auto-completion for /model command
            return []

        return []

    def _get_help_suggestions(self, parts: List[str]) -> List[str]:
        """帮助命令的建议"""
        return []

    def _get_search_suggestions(self, parts: List[str]) -> List[str]:
        """搜索命令的建议"""
        if parts[0] == "/search":
            if len(parts) == 1 or (len(parts) == 2 and not parts[1]):
                return ["/search <搜索关键词>"]

        return []