"""
完整的技能集成服务
用于将Claude Skills与DAIP-LIVE系统完全集成
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.skills.base import SkillInput, SkillMetadata, SkillOutput
from daip_live.skills.manager import SkillManager
from daip_live.skills.text_analysis import TextAnalysisSkill


class ClaudeSkillsIntegrationService:
    """Claude Skills 与 DAIP-LIVE 系统的集成服务"""

    def __init__(
        self, skill_manager: SkillManager, model_provider: LiteLLMProvider = None
    ):
        self.skill_manager = skill_manager
        self.model_provider = model_provider
        self._initialized = False
        self.claude_skills = {}

    async def initialize(self):
        """初始化 Claude Skills 集成"""
        if self._initialized:
            return

        # 检查并注册内置技能，如果尚未注册
        try:
            text_analysis_skill = TextAnalysisSkill()
            self.skill_manager.register_skill(text_analysis_skill)
            self.claude_skills["text_analysis"] = text_analysis_skill
        except ValueError:
            # 技能已注册，从技能管理器中获取
            self.claude_skills["text_analysis"] = self.skill_manager.get_skill(
                "text_analysis"
            )

        # 尝试加载来自GitHub的外部技能
        await self._load_external_skills()

        self._initialized = True

    async def _load_external_skills(self):
        """从外部源加载技能"""
        # 这里可以实现从GitHub等外部源加载技能的逻辑
        # 目前主要是预留接口
        skills_dir = Path("./claude_skills")
        if skills_dir.exists():
            # 从本地目录加载 Claude Skills
            skill_files = list(skills_dir.rglob("manifest.json"))
            for skill_file in skill_files:
                await self._load_skill_from_manifest(skill_file)

    async def _load_skill_from_manifest(self, manifest_path: Path):
        """从manifest.json加载技能"""
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest_data = json.load(f)

            # 目前我们创建一个模拟的Claude技能适配器来处理外部技能
            skill_name = manifest_data.get(
                "name", f"external_skill_{manifest_path.parent.name}"
            )
            manifest_data.get("description", "External Claude-compatible skill")

            # 这里我们创建一个适配器来处理Claude格式的技能
            claude_adapter = ClaudeSkillAdapter(
                skill_name=skill_name,
                manifest_data=manifest_data,
                skill_manager=self.skill_manager,
            )

            self.claude_skills[skill_name] = claude_adapter

        except Exception:
            pass

    async def find_appropriate_skill(self, user_input: str) -> Optional[str]:
        """基于用户输入找到合适的技能"""
        if not self._initialized:
            await self.initialize()

        # 基于关键词匹配找到最合适技能
        input_lower = user_input.lower()

        # 技能匹配规则
        skill_matchers = {
            "text_analysis": [
                r"分析.*文本",
                r"分析.*内容",
                r"文本.*分析",
                r"内容.*分析",
                r"帮我.*分析",
                r"分析.*",
                r"解读.*",
                r"理解.*文本",
                r"理解.*内容",
                r"评价.*文本",
                r"评价.*内容",
                r"总结.*文本",
                r"总结.*内容",
            ],
            "search_papers": [
                r"搜索.*",
                r"查找.*",
                r"查询.*",
                r"找.*",
                r"搜.*",
                r"检索.*",
                r"寻找.*",
                r"论文.*",
                r"文章.*",
                r"资料.*",
            ],
            "personal_assistant": [
                r"助手",
                r"助理",
                r"帮我",
                r"请.*",
                r"我想.*",
                r"可以.*",
                r"能够.*",
                r"怎么办",
                r"如何.*",
                r"怎么.*",
            ],
            "create_wiki": [
                r"创建.*wiki",
                r"写.*wiki",
                r"新建.*wiki",
                r"创建.*维基",
                r"写.*维基",
                r"新建.*维基",
                r"创建.*百科",
                r"写.*百科",
                r"新建.*百科",
            ],
        }

        for skill_name, patterns in skill_matchers.items():
            for pattern in patterns:
                if re.search(pattern, input_lower, re.IGNORECASE):
                    return skill_name

        # 如果没有找到具体匹配，尝试从技能管理器查找
        available_skills = self.skill_manager.list_skills()
        if available_skills:
            # 简单模糊匹配
            input_keywords = set(input_lower.split())
            best_match = None
            best_score = 0

            for skill_name in available_skills:
                skill_meta = self.skill_manager.get_metadata(skill_name)
                if skill_meta:
                    meta_keywords = set(
                        skill_meta.description.lower().split() + skill_meta.tags
                    )
                    score = len(input_keywords.intersection(meta_keywords))
                    if score > best_score:
                        best_score = score
                        best_match = skill_name

            return best_match

        return None

    async def execute_skill_with_context(
        self, skill_name: str, input_text: str, context: dict[str, Any] = None
    ) -> Optional[SkillOutput]:
        """在上下文中执行技能"""
        if not self._initialized:
            await self.initialize()

        skill = self.claude_skills.get(skill_name)
        if not skill:
            # 尝试从技能管理器获取
            skill = self.skill_manager.get_skill(skill_name)
            if not skill:
                # 尝试通过模糊匹配
                self.skill_manager.list_skills()
                skill_name = await self.find_appropriate_skill(input_text)
                if skill_name:
                    skill = self.skill_manager.get_skill(skill_name)

        if skill:
            try:
                skill_input = SkillInput(
                    data=input_text,
                    context=context or {},
                    metadata={
                        "source": "claude_integration",
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                # 执行技能
                result = skill.execute(skill_input)
                return result
            except Exception as e:
                return SkillOutput(
                    result=f"技能执行错误: {str(e)}",
                    confidence=0.0,
                    execution_time=0.0,
                    metadata={"error": str(e)},
                )

        return SkillOutput(
            result=f"找不到技能: {skill_name}",
            confidence=0.0,
            execution_time=0.0,
            metadata={"error": "Skill not found"},
        )

    async def get_skill_recommendations(self, user_input: str) -> list[dict[str, str]]:
        """获取技能推荐列表"""
        if not self._initialized:
            await self.initialize()

        recommendations = []

        # 查找可能适用的技能
        available_skills = self.skill_manager.list_skills()

        for skill_name in available_skills:
            skill = self.skill_manager.get_skill(skill_name)
            if skill and hasattr(skill, "metadata"):
                # 计算与用户输入的相关性
                similarity = self._calculate_similarity(
                    user_input.lower(), skill.metadata.description.lower()
                )
                if similarity > 0.3:  # 阈值
                    recommendations.append(
                        {
                            "name": skill_name,
                            "description": skill.metadata.description,
                            "similarity": similarity,
                        }
                    )

        # 按相似度排序
        recommendations.sort(key=lambda x: x["similarity"], reverse=True)
        return recommendations[:5]  # 返回前5个推荐

    def _calculate_similarity(self, input_text: str, skill_description: str) -> float:
        """计算输入与技能描述的相似度"""
        input_words = set(input_text.split())
        desc_words = set(skill_description.split())

        if not input_words or not desc_words:
            return 0.0

        intersection = input_words.intersection(desc_words)
        union = input_words.union(desc_words)

        return len(intersection) / len(union)  # Jaccard相似度


class ClaudeSkillAdapter:
    """Claude Skill 适配器 - 将 Claude 格式转换为 DAIP-LIVE 格式"""

    def __init__(
        self,
        skill_name: str,
        manifest_data: dict[str, Any],
        skill_manager: SkillManager,
    ):
        self.skill_name = skill_name
        self.manifest_data = manifest_data
        self.skill_manager = skill_manager

        # 创建适配的元数据
        self.metadata = SkillMetadata(
            name=skill_name,
            description=manifest_data.get(
                "description", f"External skill: {skill_name}"
            ),
            version=manifest_data.get("version", "1.0"),
            author=manifest_data.get("author", "Claude Skills Community"),
            tags=manifest_data.get("tags", ["external", "claude"]),
        )

    def execute(self, input: "SkillInput") -> "SkillOutput":
        """执行 Claude 技能适配器"""
        return SkillOutput(
            result=f"[模拟外部技能执行] {self.skill_name}: {input.data[:100]}...",
            confidence=0.8,
            execution_time=0.1,
            metadata={"skill_type": "claude_external"},
        )


# 集成到现有的意图识别器
def integrate_with_intent_recognizer(
    recognizer, skill_manager: SkillManager, model_provider: LiteLLMProvider
):
    """将 Claude Skills 集成到意图识别器"""
    # 创建集成服务
    integration_service = ClaudeSkillsIntegrationService(skill_manager, model_provider)

    # 添加方法到识别器
    recognizer.claude_integration_service = integration_service

    return integration_service
