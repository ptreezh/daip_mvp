"""
Skill Command Handlers for DAIP TUI
"""
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from daip_live.skills.enhanced_integration import EnhancedClaudeSkillsManager


class SkillCommandHandler:
    """Handles commands related to skills management in TUI."""
    
    def __init__(self, skill_manager, claude_integration_service: Optional[EnhancedClaudeSkillsManager] = None):
        self.skill_manager = skill_manager
        self.claude_integration_service = claude_integration_service
    
    def handle_skill_command(self, params: Dict[str, Any]) -> str:
        """Handle skill-related commands."""
        action = params.get('action', '').lower() if params else 'list'
        
        if action == 'list':
            return self._list_skills()
        elif action == 'download':
            return self._download_skills(params)
        elif action == 'reload':
            return self._reload_skills()
        elif action == 'info':
            return self._skill_info(params)
        else:
            return self._show_help()
    
    def _list_skills(self) -> str:
        """List all available skills."""
        skills = self.skill_manager.list_skills()
        
        if not skills:
            return "🔍 没有找到任何技能"
        
        result = f"📋 共找到 {len(skills)} 个技能:\n"
        for i, skill_name in enumerate(skills, 1):
            metadata = self.skill_manager.get_metadata(skill_name)
            description = metadata.description if metadata else "无描述"
            result += f"  {i:2d}. {skill_name} - {description}\n"
        
        return result.rstrip()
    
    def _download_skills(self, params: Dict[str, Any]) -> str:
        """Download skills from GitHub with automatic repository discovery."""
        if not self.claude_integration_service:
            return "❌ Claude Skills服务未初始化"

        # Get the repository URL from parameters or use default
        repo_url = params.get('url') or params.get('repo_url')

        # If no URL provided, use auto-discovery
        if not repo_url:
            # Try the default official repository first
            default_repos = [
                "https://github.com/anthropics/skills",  # Official Anthropic repository
                "https://github.com/anthropics/claude-computer-use-tools",  # Another official
                "https://github.com/meetrais/claude-agent-skills",  # Community skills
                "https://github.com/robanderson/claude-my-skills"  # Custom skills
            ]
            return self._discover_and_download_skills(default_repos)

        # Normalize and download from specified URL
        normalized_url = self.claude_integration_service.github_downloader._prepare_repo_url(repo_url)

        try:
            # Run async download function
            async def download_async():
                return await self.claude_integration_service.load_skills_from_github(normalized_url)

            downloaded_skills = asyncio.run(download_async())
            if downloaded_skills:
                return f"✅ 成功从 {normalized_url} 下载并加载了 {len(downloaded_skills)} 个技能: {', '.join(downloaded_skills)}"
            else:
                return f"⚠️ 从 {normalized_url} 未能下载到任何技能（可能该仓库不包含有效的Claude Skills）"
        except Exception as e:
            return f"❌ 下载技能时出错: {str(e)}"

    def _discover_and_download_skills(self, repo_urls: list) -> str:
        """Automatically try to download from default repositories."""
        results = []

        for repo_url in repo_urls:
            try:
                async def download_async():
                    return await self.claude_integration_service.load_skills_from_github(repo_url)

                downloaded_skills = asyncio.run(download_async())
                if downloaded_skills:
                    result = f"✅ 成功从 {repo_url} 下载并加载了 {len(downloaded_skills)} 个技能: {', '.join(downloaded_skills)}"
                    results.append(result)
                    # Return immediately when we find skills
                    return result
                else:
                    results.append(f"⚠️ {repo_url} 中没有找到合适的技能")
            except Exception as e:
                results.append(f"❌ 无法从 {repo_url} 下载: {str(e)}")

        # If no skills found in any repository
        return "❌ 未能在任何默认仓库中找到可用技能:\n" + "\n".join(results)
    
    def _reload_skills(self) -> str:
        """Reload skills from the skills directory."""
        try:
            # Load Claude skills from directory
            loaded_count = self.skill_manager.load_claude_skills_from_directory("./claude_skills")
            return f"🔄 从 ./claude_skills 目录重新加载了 {loaded_count} 个Claude技能"
        except Exception as e:
            return f"❌ 重新加载技能时出错: {str(e)}"
    
    def _skill_info(self, params: Dict[str, Any]) -> str:
        """Show detailed information about a specific skill."""
        skill_name = params.get('skill_name') or params.get('name')
        if not skill_name:
            return "❌ 请指定技能名称，例如: /skill info skill_name"
        
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            return f"❌ 未找到技能: {skill_name}"
        
        metadata = skill.metadata if hasattr(skill, 'metadata') else None
        if not metadata:
            return f"⚠️ 技能 {skill_name} 没有元数据"
        
        result = f"📋 技能信息: {skill_name}\n"
        result += f"   描述: {metadata.description}\n"
        result += f"   版本: {metadata.version}\n"
        result += f"   作者: {metadata.author}\n"
        result += f"   标签: {', '.join(metadata.tags)}\n"
        
        # 如果是Claude技能，显示更多详细信息
        if hasattr(skill, 'manifest_data'):
            manifest = skill.manifest_data
            result += f"   Manifest版本: {manifest.get('manifest_version', 'N/A')}\n"
            tools = manifest.get('tools', [])
            result += f"   工具数量: {len(tools)}\n"
        
        return result.rstrip()
    
    def _show_help(self) -> str:
        """Show help information for skill commands."""
        help_text = """
📋 技能命令帮助:

/skill list                    - 列出所有可用技能
/skill download <repo_url>     - 从GitHub仓库下载Claude技能
/skill reload                  - 从本地目录重新加载技能
/skill info <skill_name>       - 显示特定技能的详细信息

示例:
  /skill download https://github.com/user/claude-skills-repo
  /skill info text_analyzer
        """.strip()
        return help_text