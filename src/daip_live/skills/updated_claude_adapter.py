"""
Updated Claude Skill Adapter to handle both the traditional manifest.json/tools.json
format and the newer SKILL.md format used by Claude Code Skills
"""

import json
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from daip_live.skills.base import Skill, SkillInput, SkillMetadata, SkillOutput
from daip_live.skills.manager import SkillManager


class ClaudeSkillDefinition(BaseModel):
    """Claude Skill Definition - Supports both traditional and new format"""

    name: str
    version: str = "1.0"
    description: str
    manifest_version: str = "1.0"
    author: Optional[str] = None
    api: Optional[dict[str, Any]] = None
    tags: list[str] = Field(default_factory=list)
    tools: list[dict[str, Any]] = Field(default_factory=list)  # tools.json content
    skill_content: Optional[str] = None  # Content from SKILL.md


class ClaudeSkillAdapter(Skill):
    """Claude Skill Adapter - Handles both traditional and new format"""

    def __init__(
        self,
        skill_name: str,
        manifest_data: Optional[dict] = None,
        skill_content: Optional[str] = None,
        skill_manager: SkillManager = None,
    ):
        # Create metadata based on available data
        description = "Claude Skill"
        if manifest_data:
            description = manifest_data.get("description", description)
        elif skill_content:
            # Try to extract description from YAML frontmatter in SKILL.md
            try:
                if skill_content.startswith("---"):
                    # Extract YAML frontmatter
                    end_frontmatter = skill_content.find("---", 3)
                    if end_frontmatter != -1:
                        yaml_content = skill_content[3:end_frontmatter].strip()
                        frontmatter = yaml.safe_load(yaml_content)
                        if frontmatter and isinstance(frontmatter, dict):
                            description = frontmatter.get("description", description)
            except Exception:
                pass  # If YAML parsing fails, use default description

        metadata = SkillMetadata(
            name=skill_name,
            description=description,
            version=manifest_data.get("version", "1.0") if manifest_data else "1.0",
            author=manifest_data.get("author", "Claude Community")
            if manifest_data
            else "Claude Community",
            tags=manifest_data.get("tags", ["claude"]) if manifest_data else ["claude"],
        )

        super().__init__(metadata)
        self.manifest_data = manifest_data
        self.skill_content = skill_content
        self.skill_manager = skill_manager
        self.tools = manifest_data.get("tools", []) if manifest_data else []

    def execute(self, input: SkillInput) -> SkillOutput:
        """Execute Claude skill - handle both formats"""
        if self.skill_content:
            # Handle new SKILL.md format
            return self._execute_skill_md(input)
        elif self.manifest_data:
            # Handle traditional format
            return self._execute_traditional_format(input)
        else:
            return SkillOutput(
                result=f"[模拟技能执行] {self.metadata.name}: {input.data[:100]}...",
                confidence=0.8,
                execution_time=0.1,
                metadata={"skill_type": "claude_adapter"},
            )

    def _execute_skill_md(self, input: SkillInput) -> SkillOutput:
        """Execute skill in new SKILL.md format"""
        try:
            # Process the skill content and apply it to the input
            result = f"""
Claude Skill (MD Format) executed: {self.metadata.name}
Input received: {input.data[:100]}...

Skill Content Preview:
{self.skill_content[:200]}...

Note: This skill uses the newer SKILL.md format. In production, this would apply the skill instructions to the input.
            """.strip()  # noqa: E501

            return SkillOutput(
                result=result,
                confidence=0.8,
                execution_time=0.1,
                metadata={
                    "skill_type": "claude_skill_md",
                    "input_length": len(input.data),
                    "content_length": len(self.skill_content)
                    if self.skill_content
                    else 0,
                },
            )
        except Exception as e:
            return SkillOutput(
                result=f"Error executing skill: {str(e)}",
                confidence=0.0,
                execution_time=0.1,
                metadata={"error": str(e)},
            )

    def _execute_traditional_format(self, input: SkillInput) -> SkillOutput:
        """Execute skill in traditional manifest.json/tools.json format"""
        try:
            tool_info = []
            for tool in self.tools:
                tool_info.append(
                    f"  - {tool.get('name', 'unnamed')}: {tool.get('description', 'No description')}"  # noqa: E501
                )

            result_text = f"""
Claude Skill (Traditional Format): {self.metadata.name}
Description: {self.metadata.description}
Version: {self.metadata.version}
Tags: {", ".join(self.metadata.tags)}

Available Tools:
{chr(10).join(tool_info)}

Input received: {input.data[:100]}...

Note: This is a Claude Skills format adapter. In production, this would call the actual Claude skill endpoints.
            """.strip()  # noqa: E501

            return SkillOutput(
                result=result_text,
                confidence=0.8,
                execution_time=0.05,
                metadata={
                    "skill_type": "claude_adapter",
                    "input_length": len(input.data),
                    "tools_count": len(self.tools),
                    "claude_format": True,
                },
            )
        except Exception as e:
            return SkillOutput(
                result=f"Error executing skill: {str(e)}",
                confidence=0.0,
                execution_time=0.1,
                metadata={"error": str(e)},
            )


class ClaudeSkillAdapterManager:
    """Enhanced Claude Skill Adapter Manager - Supports both formats"""

    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager
        self._claude_skills: dict[str, ClaudeSkillDefinition] = {}
        self._skill_adapters: dict[str, Any] = {}

    async def load_claude_skills_from_directory(self, directory_path: str) -> list[str]:
        """Load Claude Skills from directory - supports both formats"""
        skills_dir = Path(directory_path)
        loaded_skills = []

        if not skills_dir.exists():
            return loaded_skills

        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                # Check for traditional format (manifest.json + tools.json)
                manifest_file = skill_dir / "manifest.json"
                tools_file = skill_dir / "tools.json"

                if manifest_file.exists() and tools_file.exists():
                    # Traditional format
                    loaded_skills.extend(
                        await self._load_traditional_format_skill(
                            skill_dir, manifest_file, tools_file
                        )
                    )
                else:
                    # Check for new format (SKILL.md files)
                    skill_md_files = list(skill_dir.glob("SKILL.md"))
                    if not skill_md_files:
                        skill_md_files = list(
                            skill_dir.glob("*.md")
                        )  # Look for any markdown file

                    for skill_md in skill_md_files:
                        loaded_skills.extend(
                            await self._load_new_format_skill(skill_dir, skill_md)
                        )

        return loaded_skills

    async def _load_traditional_format_skill(
        self, skill_dir: Path, manifest_file: Path, tools_file: Path
    ) -> list[str]:
        """Load traditional format skill (manifest.json + tools.json)"""
        loaded_skills = []

        try:
            # Read manifest.json
            with open(manifest_file, encoding="utf-8") as f:
                manifest_data = json.load(f)

            # Read tools.json
            with open(tools_file, encoding="utf-8") as f:
                tools_data = json.load(f)

            # Create Claude skill definition
            skill_def = ClaudeSkillDefinition(
                name=manifest_data.get("name", skill_dir.name),
                version=manifest_data.get("version", "1.0"),
                description=manifest_data.get(
                    "description", f"Skill from {skill_dir.name}"
                ),
                manifest_version=manifest_data.get("manifest_version", "1.0"),
                author=manifest_data.get("author"),
                api=manifest_data.get("api"),
                tags=manifest_data.get("tags", []),
                tools=tools_data.get("tools", []),
            )

            self._claude_skills[skill_def.name] = skill_def

            # Create adapter and register
            adapter = ClaudeSkillAdapter(
                skill_name=skill_def.name,
                manifest_data=manifest_data,
                skill_manager=self.skill_manager,
            )

            self.skill_manager.register_skill(adapter)
            self._skill_adapters[skill_def.name] = adapter
            loaded_skills.append(skill_def.name)

        except Exception:
            pass

        return loaded_skills

    async def _load_new_format_skill(
        self, skill_dir: Path, skill_md_file: Path
    ) -> list[str]:
        """Load new format skill (SKILL.md)"""
        loaded_skills = []

        try:
            # Read the SKILL.md file
            with open(skill_md_file, encoding="utf-8") as f:
                skill_content = f.read()

            # Extract skill name from directory name or filename
            skill_name = (
                skill_dir.name
                if skill_dir.name != skill_md_file.stem
                else skill_md_file.stem
            )
            skill_name = f"{skill_name}_{skill_md_file.stem}".replace(
                "SKILL", ""
            ).strip("_")

            # If there's YAML frontmatter, extract metadata
            description = f"Skill from {skill_name}"
            if skill_content.startswith("---"):
                try:
                    # Extract YAML frontmatter
                    end_frontmatter = skill_content.find("---", 3)
                    if end_frontmatter != -1:
                        yaml_content = skill_content[3:end_frontmatter].strip()
                        frontmatter = yaml.safe_load(yaml_content)
                        if frontmatter and isinstance(frontmatter, dict):
                            description = frontmatter.get("description", description)
                            skill_name = frontmatter.get("name", skill_name)
                except Exception:
                    pass  # If YAML parsing fails, use default values

            # Create Claude skill definition for new format
            skill_def = ClaudeSkillDefinition(
                name=skill_name, description=description, skill_content=skill_content
            )

            self._claude_skills[skill_name] = skill_def

            # Create adapter and register
            adapter = ClaudeSkillAdapter(
                skill_name=skill_name,
                skill_content=skill_content,
                skill_manager=self.skill_manager,
            )

            self.skill_manager.register_skill(adapter)
            self._skill_adapters[skill_name] = adapter
            loaded_skills.append(skill_name)

        except Exception:
            pass

        return loaded_skills

    def get_claude_skill_by_name(self, name: str) -> Optional[ClaudeSkillDefinition]:
        """Get Claude Skill by name"""
        return self._claude_skills.get(name)

    def list_claude_skills(self) -> list[ClaudeSkillDefinition]:
        """List all Claude Skills"""
        return list(self._claude_skills.values())

    def has_claude_skills(self) -> bool:
        """Check if there are Claude Skills"""
        return len(self._claude_skills) > 0

    async def execute_skill(
        self, skill_name: str, parameters: dict[str, Any] = None
    ) -> str:
        """Execute a Claude skill by name - for compatibility with TUI"""
        if parameters is None:
            parameters = {}

        # Find the skill adapter by name
        if skill_name in self._skill_adapters:
            adapter = self._skill_adapters[skill_name]
            # Create a basic input from the parameters
            input_data = parameters.get(
                "input", parameters.get("content", str(parameters))
            )
            skill_input = SkillInput(data=input_data, context=parameters)

            # Execute the skill
            result = adapter.execute(skill_input)
            return result.result
        else:
            # If the skill doesn't exist, return error message
            available_skills = list(self._skill_adapters.keys())
            return f"技能 '{skill_name}' 未找到。可用技能: {', '.join(available_skills) if available_skills else '无可用技能'}"  # noqa: E501

    def execute_claude_skill(self, skill_name: str, input_text: str) -> str:
        """Execute a Claude skill - direct method for backward compatibility"""
        if skill_name in self._skill_adapters:
            adapter = self._skill_adapters[skill_name]
            skill_input = SkillInput(data=input_text)
            result = adapter.execute(skill_input)
            return result.result
        else:
            return f"技能 '{skill_name}' 未找到"
