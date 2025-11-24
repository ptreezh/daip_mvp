"""
Claude Skills Command Handler for DAIP TUI
This handles generic Claude skills commands without hard dependencies
"""
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
from daip_live.skills.base import SkillInput, SkillOutput


class PPTSurveyCommandHandler:
    """Handles commands for PPT generation and survey skills in TUI."""
    
    def __init__(self, skill_manager):
        self.skill_manager = skill_manager

    def handle_claude_skill_command(self, skill_name: str, params: Dict[str, Any]) -> str:
        """Handle Claude skill commands generically."""
        # Get the skill from manager
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            return f"❌ 未找到技能: {skill_name}"

        try:
            # Create skill input with all parameters
            skill_input = SkillInput(
                data=params.get('content', params.get('data', params.get('query', ''))),
                context=params.get('context', {}),
                metadata=params
            )

            result = skill.execute(skill_input)
            return result.result
        except Exception as e:
            return f"❌ 执行技能 {skill_name} 时出错: {str(e)}"

    def handle_ppt_command(self, params: Dict[str, Any]) -> str:
        """Handle PPT generation commands with automatic skill discovery."""
        # Check if PPT-related skills are available
        ppt_skills = [skill for skill in self.skill_manager.list_skills()
                     if any(keyword in skill.lower() for keyword in
                           ['ppt', 'powerpoint', 'presentation', 'slide', 'deck', 'document'])]

        if not ppt_skills:
            # No PPT skills available, try to download them
            return ("⚠️ 未找到PPT生成技能，正在尝试自动下载...\n"
                   "请先运行: /skill download\n"
                   "或: /skill download https://github.com/anthropics/skills")

        # Use the first available PPT skill
        skill_name = ppt_skills[0]
        return self.handle_claude_skill_command(skill_name, params)

    def handle_survey_command(self, params: Dict[str, Any]) -> str:
        """Handle survey commands with automatic skill discovery."""
        # Check if survey-related skills are available
        survey_skills = [skill for skill in self.skill_manager.list_skills()
                        if any(keyword in skill.lower() for keyword in
                              ['survey', 'question', 'quiz', 'poll', 'feedback', 'form'])]

        if not survey_skills:
            # No survey skills available, try to download them
            return ("⚠️ 未找到问卷调查技能，正在尝试自动下载...\n"
                   "请先运行: /skill download\n"
                   "或: /skill download https://github.com/meetrais/claude-agent-skills")

        # Use the first available survey skill
        skill_name = survey_skills[0]
        return self.handle_claude_skill_command(skill_name, params)

    def _show_ppt_help(self) -> str:
        """Show help for PPT commands."""
        help_text = """
📊 PPT生成命令帮助:

/ppt create --content "<content>" [--title "<title>"] [--output "<path>"]
  - 生成PowerPoint演示文稿 (需要先下载对应技能)

示例:
  /skill download https://github.com/user/ppt-skills-repo
  /ppt create --content "# Presentation Title\\n\\n## Slide 1\\nContent for slide 1\\n\\n## Slide 2\\nContent for slide 2" --title "My Presentation"
        """.strip()
        return help_text

    def _show_survey_help(self) -> str:
        """Show help for survey commands."""
        help_text = """
📋 问卷调查命令帮助:

/survey create --content "<questions>"
  - 创建问卷调查 (需要先下载对应技能)
/survey analyze --data "<responses>"
  - 分析调查结果
/survey summarize --data "<responses>"
  - 总结调查结果

示例:
  /skill download https://github.com/user/survey-skills-repo
  /survey create --content "1. 您对我们的服务满意吗？\\nA. 非常满意\\nB. 满意\\nC. 不满意"
        """.strip()
        return help_text