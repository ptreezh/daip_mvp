"""
Command processing system for TUI
"""

from typing import Any

from daip_live.tui_v1.command.parser import CommandParser
from daip_live.tui_v1.command.ppt_survey_handler import PPTSurveyCommandHandler
from daip_live.tui_v1.command.registry import CommandRegistry
from daip_live.tui_v1.command.skill_handler import SkillCommandHandler


class TUICommandProcessor:
    """Process commands in TUI and integrate with skill system."""

    def __init__(self, skill_manager, claude_integration_service=None):
        self.skill_manager = skill_manager
        self.claude_integration_service = claude_integration_service
        self.parser = CommandParser()
        self.registry = CommandRegistry()

        # Initialize command handlers
        self.skill_handler = SkillCommandHandler(
            skill_manager=skill_manager,
            claude_integration_service=claude_integration_service,
        )
        self.ppt_survey_handler = PPTSurveyCommandHandler(skill_manager=skill_manager)

        # Register commands
        self._register_commands()

    def _register_commands(self):
        """Register essential commands only (avoid command clutter)."""
        self.registry.register("skill", self._handle_skill_command)
        # Removed ppt and survey commands - they will be handled through natural language processing  # noqa: E501

    def process_command(self, command_str: str) -> str:
        """Process a command string and return result."""
        command = self.parser.parse(command_str)

        # Check if this is a skill command
        if command.command.startswith("/"):
            command_name = command.command[1:]  # Remove leading slash
            handler = self.registry.get_handler(command_name)

            if handler:
                # Prepare parameters from command
                params = {
                    "action": command.action,
                    "args": command.args,
                    "options": command.options,
                }

                # Add arguments as options for easier access
                for i, arg in enumerate(command.args):
                    params[f"arg_{i}"] = arg

                # Try to interpret arguments as specific parameters
                if command_name == "skill":
                    # For skill command, first arg could be the action
                    if command.args:
                        params["action"] = command.args[0]
                        if len(command.args) > 1:
                            # If we have a second argument, treat as URL for download or skill name for info  # noqa: E501
                            if params["action"] == "download":
                                params["url"] = command.args[1]
                            elif params["action"] == "info":
                                params["name"] = command.args[1]
                elif command_name == "ppt":
                    # For PPT command, use all text content as input
                    params["action"] = "create"  # Default to create
                    # Combine all arguments as content
                    if command.args:
                        params["content"] = " ".join(command.args)
                    # Use options for additional parameters
                    for key, value in command.options.items():
                        params[key] = value
                elif command_name == "survey":
                    # For survey command, use all text content as input
                    params["action"] = "create"  # Default to create
                    # Combine all arguments as content
                    if command.args:
                        params["content"] = " ".join(command.args)
                    # Use options for additional parameters
                    for key, value in command.options.items():
                        params[key] = value

                return handler(params)
            else:
                if command_name == "help":
                    return self._show_help()
                else:
                    return f"❌ 未知命令: {command.command}. 输入 /help 查看可用命令。"
        else:
            # Not a command - treat as natural language input
            # This is where we handle automatic skill discovery based on content
            return self._process_natural_language(command_str)

    def _process_natural_language(self, input_text: str) -> str:
        """Process natural language input and automatically discover appropriate skills."""  # noqa: E501
        # Check if the input suggests PPT creation
        ppt_keywords = [
            "ppt",
            "powerpoint",
            "演示文稿",
            "幻灯片",
            "slide",
            "deck",
            "presentation",
            "报告",
            "汇报",
        ]
        survey_keywords = [
            "调查",
            "问卷",
            "poll",
            "survey",
            "question",
            "问题",
            "满意度",
            "反馈",
        ]

        input_lower = input_text.lower()

        # Check for PPT-related requests
        for keyword in ppt_keywords:
            if keyword in input_lower:
                # Try to extract title and content
                import re

                title_match = re.search(
                    r'--title\s+["\']([^"\']+)["\']|标题\s*[:：]\s*([^\n\r]+)',
                    input_text,
                )
                title = (
                    title_match.group(1)
                    if title_match and title_match.group(1)
                    else title_match.group(2)
                    if title_match
                    else "演示文稿"
                )

                # Extract content (simplified approach)
                content = input_text

                # Check if skills are available
                from daip_live.tui_v1.command.ppt_survey_handler import (
                    PPTSurveyCommandHandler,
                )

                ppt_handler = PPTSurveyCommandHandler(self.skill_manager)

                ppt_skills = [
                    skill
                    for skill in self.skill_manager.list_skills()
                    if any(
                        k in skill.lower()
                        for k in [
                            "ppt",
                            "powerpoint",
                            "presentation",
                            "slide",
                            "deck",
                            "document",
                        ]
                    )
                ]

                if not ppt_skills:
                    return (
                        "⚠️ 未找到PPT生成技能，正在尝试自动下载...\n"
                        "请先运行: /skill download\n"
                        "或告诉我您需要什么内容的PPT"
                    )

                skill_name = ppt_skills[0]
                params = {"action": "create", "content": content, "title": title}
                return ppt_handler.handle_claude_skill_command(skill_name, params)

        # Check for survey-related requests
        for keyword in survey_keywords:
            if keyword in input_lower:
                # Check if skills are available
                from daip_live.tui_v1.command.ppt_survey_handler import (
                    PPTSurveyCommandHandler,
                )

                survey_handler = PPTSurveyCommandHandler(self.skill_manager)

                survey_skills = [
                    skill
                    for skill in self.skill_manager.list_skills()
                    if any(
                        k in skill.lower()
                        for k in [
                            "survey",
                            "question",
                            "quiz",
                            "poll",
                            "feedback",
                            "form",
                        ]
                    )
                ]

                if not survey_skills:
                    return (
                        "⚠️ 未找到问卷调查技能，正在尝试自动下载...\n"
                        "请先运行: /skill download\n"
                        "或直接提供您的问题内容"
                    )

                skill_name = survey_skills[0]
                params = {"action": "create", "content": input_text}
                return survey_handler.handle_claude_skill_command(skill_name, params)

        # If no specific skill found, return a friendly response
        return f"💡 我理解您想表达: {input_text[:50]}...\n如需特定功能，请尝试 /skill download 获取技能，或使用 /help 查看可用命令。"  # noqa: E501

    def _handle_skill_command(self, params: dict[str, Any]) -> str:
        """Handle skill commands."""
        return self.skill_handler.handle_skill_command(params)

    # Removed individual command handlers as they're now handled through natural language processing  # noqa: E501
    # The PPT and Survey functionality is still available through the PPTSurveyCommandHandler  # noqa: E501
    # but accessed via natural language interpretation instead of direct commands

    def _show_help(self) -> str:
        """Show help information."""
        help_text = """
🎮 DAIP-LIVE TUI 功能帮助:

核心命令:
  /skill list                    - 查看所有可用技能
  /skill download                - 自动搜索并下载技能（推荐）
  /skill download <repo_url>     - 从指定仓库下载技能
  /skill reload                  - 重新加载本地技能

智能功能 (自然语言):
  直接输入需求即可，系统自动识别:
  - "生成一个关于AI的PPT" 或 "创建演示文稿..."
  - "创建一个满意度调查" 或 "问卷: 您觉得...?"
  - 系统会自动调用最适合的技能

实用命令:
  /help                          - 显示此帮助信息

示例:
  /skill download              # 自动搜索并下载官方技能
  "帮我生成一个项目汇报PPT"     # 系统自动识别并处理
  "创建一个产品满意度问卷"      # 自动处理调查创建
        """.strip()
        return help_text


# Example usage function
def setup_command_processing(tui_app, skill_manager, claude_integration_service=None):
    """
    Setup command processing for a TUI application.

    Args:
        tui_app: The TUI application instance
        skill_manager: The skill manager instance
        claude_integration_service: Claude integration service instance
    """
    command_processor = TUICommandProcessor(
        skill_manager=skill_manager,
        claude_integration_service=claude_integration_service,
    )

    # Store the command processor in the app for later use
    tui_app.command_processor = command_processor
    return command_processor
