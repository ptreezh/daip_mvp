"""
Claude Skills 适配器和仓库管理器
实现对 Claude Skills 格式的支持和自动集成
"""
import os
import json
import yaml
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ClaudeSkillDefinition(BaseModel):
    """Claude Skill 定义 - 表示 Claude 格式的技能"""
    name: str
    version: str
    description: str
    manifest_version: str
    author: Optional[str] = None
    api: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    tools: List[Dict[str, Any]] = Field(default_factory=list)  # tools.json 内容


class ClaudeSkillAdapterManager:
    """Claude Skills 适配器管理器 - 将 Claude 格式转换为 DAIP-LIVE 格式"""
    
    def __init__(self, skill_manager):
        self.skill_manager = skill_manager
        self._claude_skills: Dict[str, ClaudeSkillDefinition] = {}
        self._skill_adapters: Dict[str, Any] = {}
    
    async def load_claude_skills_from_directory(self, directory_path: str) -> List[str]:
        """从指定目录加载 Claude Skills"""
        skills_dir = Path(directory_path)
        loaded_skills = []
        
        if not skills_dir.exists():
            print(f"⚠️  Claude Skills 目录不存在: {directory_path}")
            return loaded_skills
        
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                manifest_file = skill_dir / "manifest.json" 
                tools_file = skill_dir / "tools.json"
                
                if manifest_file.exists() and tools_file.exists():
                    try:
                        # 读取 manifest.json
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest_data = json.load(f)
                        
                        # 读取 tools.json
                        with open(tools_file, 'r', encoding='utf-8') as f:
                            tools_data = json.load(f)
                        
                        # 创建 Claude 技能定义
                        skill_def = ClaudeSkillDefinition(
                            name=manifest_data.get("name", skill_dir.name),
                            version=manifest_data.get("version", "1.0"),
                            description=manifest_data.get("description", f"Skill from {skill_dir.name}"),
                            manifest_version=manifest_data.get("manifest_version", "1.0"),
                            author=manifest_data.get("author"),
                            api=manifest_data.get("api"),
                            tags=manifest_data.get("tags", []),
                            tools=tools_data.get("tools", [])
                        )
                        
                        self._claude_skills[skill_def.name] = skill_def
                        
                        # 创建适配器并将 Claude 技能转换为 DAIP-LIVE 技能格式
                        adapter = self._create_skill_adapter_from_claude_definition(skill_def)
                        if adapter:
                            self.skill_manager.register_skill(adapter)
                            self._skill_adapters[skill_def.name] = adapter
                            print(f"✅ 成功加载 Claude Skill: {skill_def.name}")
                            loaded_skills.append(skill_def.name)
                        else:
                            print(f"❌ 无法为 Claude Skill 创建适配器: {skill_def.name}")
                            
                    except Exception as e:
                        print(f"❌ 加载 Claude Skill {skill_dir.name} 失败: {e}")
        
        return loaded_skills
    
    async def load_claude_skills_from_github(self, repo_url: str) -> List[str]:
        """从 GitHub 仓库加载 Claude Skills"""
        try:
            # 解析 GitHub URL
            repo_parts = repo_url.rstrip('/').split('/')
            if len(repo_parts) >= 2:
                repo_name = repo_parts[-1]
            else:
                repo_name = "temp_repo"
            
            # 创建临时目录
            temp_dir = Path.cwd() / "temp_claude_skills"
            temp_dir.mkdir(exist_ok=True)
            skill_temp_dir = temp_dir / repo_name
            
            print(f"📥 从 GitHub 下载 Claude Skills: {repo_name}")
            
            # 使用 git clone 下载仓库 (需要先下载)
            try:
                result = subprocess.run(
                    ["git", "clone", repo_url, str(skill_temp_dir)],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode != 0:
                    print(f"⚠️  无法从 GitHub 克隆: {result.stderr}")
                    return []
            except subprocess.TimeoutExpired:
                print(f"⏰ GitHub 克试超时")
                return []
            except FileNotFoundError:
                print(f"❌ git 命令未找到，请安装 Git")
                return []
            
            # 在下载的仓库中查找包含 Claude Skills 的目录
            # 遍历所有子目录查找 manifest.json 和 tools.json
            found_skills = 0
            skill_dirs = []
            
            for path in skill_temp_dir.rglob("*"):
                if path.is_dir():
                    manifest_path = path / "manifest.json"
                    tools_path = path / "tools.json"
                    if manifest_path.exists() and tools_path.exists():
                        skill_dirs.append(path)
            
            # 检查每个找到的技能目录
            loaded_skills = []
            for skill_dir in skill_dirs:
                skill_dir_name = skill_dir.name
                manifest_file = skill_dir / "manifest.json"
                tools_file = skill_dir / "tools.json"
                
                try:
                    # 读取并加载技能
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        manifest_data = json.load(f)
                    
                    with open(tools_file, 'r', encoding='utf-8') as f:
                        tools_data = json.load(f)
                    
                    # 创建 Claude 技能定义
                    skill_def = ClaudeSkillDefinition(
                        name=manifest_data.get("name", skill_dir_name),
                        version=manifest_data.get("version", "1.0"),
                        description=manifest_data.get("description", f"Skill from {skill_dir_name}"),
                        manifest_version=manifest_data.get("manifest_version", "1.0"),
                        author=manifest_data.get("author"),
                        api=manifest_data.get("api"),
                        tags=manifest_data.get("tags", []),
                        tools=tools_data.get("tools", [])
                    )
                    
                    self._claude_skills[skill_def.name] = skill_def
                    
                    # 创建适配器
                    adapter = self._create_skill_adapter_from_claude_definition(skill_def)
                    if adapter:
                        self.skill_manager.register_skill(adapter)
                        self._skill_adapters[skill_def.name] = adapter
                        print(f"✅ 从 GitHub 成功加载 Claude Skill: {skill_def.name}")
                        loaded_skills.append(skill_def.name)
                        found_skills += 1
                    else:
                        print(f"❌ 无法为 GitHub Claude Skill 创建适配器: {skill_def.name}")
                        
                except Exception as e:
                    print(f"❌ 加载 GitHub Claude Skill {skill_dir_name} 失败: {e}")
            
            print(f"✅ 从 GitHub 加载 {found_skills} 个 Claude Skills")
            
            # 清理临时文件
            import shutil
            if skill_temp_dir.exists():
                shutil.rmtree(skill_temp_dir)
                
            return loaded_skills
            
        except Exception as e:
            print(f"❌ 从 GitHub 加载 Claude Skills 失败: {e}")
            return []
    
    def _create_skill_adapter_from_claude_definition(self, skill_def: ClaudeSkillDefinition):
        """从 Claude 技能定义创建适配器"""
        # 创建一个适配器类，将 Claude 技能转换为 DAIP-LIVE 技能格式
        from daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata
        import aiohttp
        
        class ClaudeSkillAdapter(Skill):
            def __init__(self, claude_skill_def: ClaudeSkillDefinition):
                # 创建DAIP-LIVE兼容的元数据
                metadata = SkillMetadata(
                    name=claude_skill_def.name,
                    description=claude_skill_def.description,
                    version=claude_skill_def.version,
                    author=claude_skill_def.author or "Claude Community",
                    tags=claude_skill_def.tags
                )
                super().__init__(metadata)
                self.claude_skill_def = claude_skill_def
                self.tools = claude_skill_def.tools
                self.api_config = claude_skill_def.api
                
            def execute(self, input: SkillInput) -> SkillOutput:
                """执行 Claude 技能适配器 - 实际上返回说明信息，因为需要真实的API接口"""
                # 在实际实现中，这应该通过API调用Claude技能
                # 但现在返回一个说明信息，告诉用户技能结构
                import json
                tool_info = []
                for tool in self.tools:
                    tool_info.append(f"  - {tool.get('name', 'unnamed')}: {tool.get('description', 'No description')}")
                
                result_text = f"""
Claude Skill Adapter: {self.metadata.name}
Description: {self.metadata.description}
Version: {self.metadata.version}
Tags: {', '.join(self.metadata.tags)}

Available Tools:
{chr(10).join(tool_info)}  # chr(10) is newline

Input received: {input.data[:100]}...

Note: This is a Claude Skills format adapter. In production, this would call the actual Claude skill endpoints.
                """.strip()
                
                return SkillOutput(
                    result=result_text,
                    confidence=0.8,
                    execution_time=0.05,
                    metadata={
                        "skill_type": "claude_adapter",
                        "input_length": len(input.data),
                        "tools_count": len(self.tools),
                        "claude_format": True
                    }
                )
        
        return ClaudeSkillAdapter(skill_def)
    
    def get_claude_skill_by_name(self, name: str) -> Optional[ClaudeSkillDefinition]:
        """根据名称获取 Claude Skill"""
        return self._claude_skills.get(name)
    
    def list_claude_skills(self) -> List[ClaudeSkillDefinition]:
        """列出所有 Claude Skills"""
        return list(self._claude_skills.values())
    
    def has_claude_skills(self) -> bool:
        """检查是否有 Claude Skills"""
        return len(self._claude_skills) > 0