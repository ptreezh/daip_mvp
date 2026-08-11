"""
多角色协作维基词条创作服务
使用多模型辩论机制协同创建高质量维基词条
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from daip_live.core.models import (
    DebateTurnCompleteEvent,
    ThoughtEvent,
)
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.wiki.manager import WikiManager
from daip_live.wiki.models import WikiPage

from .role_intelligence_selector import RoleIntelligenceSelector


class MultiRoleWikiCollaborator:
    """多角色协作维基词条创建器"""

    def __init__(
        self,
        session_manager: SessionManager,
        role_manager: RoleManager,
        role_model_manager: RoleModelManager,
        model_provider: LiteLLMProvider,
        wiki_manager: WikiManager,
    ):
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider
        self.wiki_manager = wiki_manager

        # 定义维基协作的主要角色类型（使用 roles/ 目录中真实存在的角色）
        self.default_roles = [
            "pro_arguer",  # 正方 - 提供专业知识与论证
            "con_arguer",  # 反方 - 提供批判性观点
            "research_analyst",  # 研究员 - 提供研究依据
            "creative_writer",  # 创意作者 - 负责结构与表述
        ]

        # 初始化智能角色选择器
        self.role_intelligence_selector = RoleIntelligenceSelector(
            role_manager=self.role_manager
        )

    async def create_collaborative_wiki(
        self,
        title: str,
        initial_topic: str,
        roles: Optional[list[str]] = None,
        rounds: int = 3,
    ) -> tuple[WikiPage, str]:
        """使用多角色协作创建维基词条

        Args:
            title: 维基词条标题
            initial_topic: 初始主题/话题
            roles: 指定的角色列表，如果为None则使用智能选择
            rounds: 辩论轮数

        Returns:
            Tuple[WikiPage, str]: (维基页面对象, 格式化内容字符串)
        """
        # 如果没有提供角色列表，则使用智能选择器
        if roles is None:
            try:
                roles = self.role_intelligence_selector.analyze_topic_for_roles(
                    topic=initial_topic, max_roles=4
                )
            except Exception:
                # 如果智能选择失败，回退到默认角色
                roles = self.default_roles

        # 创建一个临时的增强辩论管理器用于协作
        debate_manager = EnhancedDebateManager(
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            role_model_manager=self.role_model_manager,
            model_provider=self.model_provider,
            debate_history_tracker=None,
            use_optimized_architecture=True,
        )

        # 收集各角色对维基词条的贡献
        contributions = {}

        # 提示模板 - 每个角色从自己的角度贡献内容

        # 让每个角色依次贡献内容
        async for event in debate_manager.run_debate(initial_topic, roles, rounds):
            if isinstance(event, DebateTurnCompleteEvent):
                role_name = event.participant
                contribution = event.content_preview

                if role_name not in contributions:
                    contributions[role_name] = []

                contributions[role_name].append(contribution)

                # 发布思考事件以更新UI
                ThoughtEvent(content=f"{role_name} 为'{title}'贡献了内容")

        # 整合所有角色的贡献
        wiki_content = await self._synthesize_wiki_content(
            title, contributions, initial_topic
        )

        # 创建维基页面
        tags = self._extract_tags_from_content(title, wiki_content)
        wiki_page = self.wiki_manager.create_page(
            title=title, content=wiki_content, tags=tags
        )

        return wiki_page, wiki_content

    async def _synthesize_wiki_content(
        self, title: str, contributions: dict[str, list[str]], topic: str
    ) -> str:
        """合成来自多个角色的贡献为一个完整的维基词条"""

        # 合成策略：按角色类型组织内容，确保全面性
        sections = {
            "## 概述": [],
            "## 定义与背景": [],
            "## 关键特点": [],
            "## 应用领域": [],
            "## 发展现状": [],
            "## 优缺点分析": [],
            "## 未来展望": [],
            "## 参考资料": [],
        }

        role_display_names = {
            "domain_expert": "领域专家",
            "researcher": "研究员",
            "editor": "编辑",
            "critic": "批评家",
        }

        for role_name, role_contributions in contributions.items():
            combined_content = "\n\n".join(role_contributions)
            display_name = role_display_names.get(role_name, role_name)

            # 根据角色类型将贡献分配到相应部分
            if role_name == "domain_expert":
                sections["## 定义与背景"].append(
                    f"### {display_name}观点\n{combined_content}"
                )
                sections["## 关键特点"].append(
                    f"### {display_name}提供的技术细节\n{combined_content}"
                )
            elif role_name == "researcher":
                sections["## 发展现状"].append(f"### 研究数据支撑\n{combined_content}")
                sections["## 参考资料"].append(f"### {combined_content}")
            elif role_name == "editor":
                sections["## 概述"].append(
                    f"### {display_name}的结构化概述\n{combined_content}"
                )
            elif role_name == "critic":
                sections["## 优缺点分析"].append(
                    f"### 批评与改进意见\n{combined_content}"
                )
            else:
                # 其他角色添加到概述部分
                sections["## 概述"].append(
                    f"### {role_name.title()}观点\n{combined_content}"
                )

        # 组合成完整维基内容
        content_parts = [
            f"# {title}",
            f"\n> 协作创建于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n本词条由多个AI角色协作创建，融合了不同领域的专业见解。\n",
        ]

        # 添加各部分内容
        for section_title, section_contents in sections.items():
            if section_contents:  # 只添加非空部分
                content_parts.append(f"\n{section_title}")
                for content in section_contents:
                    content_parts.append(f"\n{content}")

        # 添加协作说明
        content_parts.extend(
            [
                "\n## 协作说明",
                "\n此词条由以下角色协作完成:",
                "- domain_expert: 提供专业知识",
                "- researcher: 提供研究依据",
                "- editor: 负责结构和表述",
                "- critic: 负责审视和完善",
                f"\n协作主题: {topic}",
            ]
        )

        return "\n".join(content_parts)

    def _extract_tags_from_content(self, title: str, content: str) -> list[str]:
        """从内容中提取标签"""
        import re

        # 提取关键词作为标签
        tags = [title.lower().replace(" ", "_")]

        # 从内容中提取可能的关键词
        # 简单提取包含大写字母的单词或技术术语
        potential_tags = re.findall(r"\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b", content)
        potential_tags = [tag.lower() for tag in potential_tags if len(tag) > 2]
        tags.extend(potential_tags[:5])  # 只取前5个

        # 去重
        unique_tags = []
        for tag in tags:
            if tag not in unique_tags:
                unique_tags.append(tag)

        return unique_tags[:10]  # 最多10个标签


class EnhancedWikiManager(WikiManager):
    """增强的维基管理器，集成多角色协作功能"""

    def __init__(
        self,
        wiki_root: Path,
        role_model_manager: Optional[RoleModelManager] = None,
        model_provider: Optional[LiteLLMProvider] = None,
        session_manager: Optional[SessionManager] = None,
        role_manager: Optional[RoleManager] = None,
    ):
        # 验证使用真实模型提供者，拒绝模拟
        if model_provider is not None:
            self._validate_real_model_provider(model_provider)

        if role_model_manager is not None:
            self._validate_real_role_manager(role_model_manager)

        super().__init__(wiki_root, role_model_manager, model_provider)

        self.session_manager = session_manager
        self.role_manager = role_manager
        self.collaborator = None
        self.simple_collaboration_engine = None

        # 优先使用简化协作引擎
        if all([role_model_manager, model_provider]):
            from .simple_collaboration_engine import SimpleCollaborationEngine

            self.simple_collaboration_engine = SimpleCollaborationEngine(
                role_model_manager=role_model_manager,
                model_provider=model_provider,
                wiki_manager=self,
            )

        # 如果所有依赖都可用，也保留原有的协作器
        if all([session_manager, role_manager, role_model_manager, model_provider]):
            self.collaborator = MultiRoleWikiCollaborator(
                session_manager=session_manager,
                role_manager=role_manager,
                role_model_manager=role_model_manager,
                model_provider=model_provider,
                wiki_manager=self,
            )

    async def create_collaborative_wiki(
        self,
        title: str,
        topic: str,
        roles: Optional[list[str]] = None,
        rounds: int = 1,
        show_progress: bool = True,
    ) -> WikiPage:
        """创建协作维基词条

        Args:
            title: 页面标题
            topic: 讨论话题
            roles: 指定的角色列表
            rounds: 讨论轮数
            show_progress: 是否显示进度

        Returns:
            WikiPage: 创建的维基页面对象
        """
        # 优先使用简化协作引擎（不依赖复杂的辩论系统）
        if self.simple_collaboration_engine:
            if show_progress:
                from .auto_progress_display import (
                    create_enhanced_engine_with_auto_display,
                )

                enhanced_engine = create_enhanced_engine_with_auto_display(
                    self.simple_collaboration_engine
                )
                (
                    page,
                    content,
                ) = await enhanced_engine.create_collaborative_wiki_with_auto_display(
                    title=title, topic=topic, roles=roles, rounds=rounds
                )
            else:
                # 即使show_progress=False，也提供基础的进度信息
                (
                    page,
                    content,
                ) = await self.simple_collaboration_engine.create_collaborative_wiki(
                    title=title, topic=topic, roles=roles, rounds=rounds
                )
            return page

        # 如果简化引擎不可用，尝试使用原有的协作器
        if self.collaborator:
            try:
                page, content = await self.collaborator.create_collaborative_wiki(
                    title=title, initial_topic=topic, roles=roles, rounds=rounds
                )
                return page
            except Exception:
                # 降级到简单协作
                return self._fallback_simple_collaboration(title, topic)

        raise RuntimeError(
            "Cannot create collaborative wiki - no working collaboration engine available"  # noqa: E501
        )

    def _fallback_simple_collaboration(self, title: str, topic: str) -> WikiPage:
        """简单协作降级方案"""
        content = f"""# {title}

## 概述
{topic}是一个重要的话题，需要多角度的深入分析。

## 协作内容
此页面由DAIP-LIVE系统通过多模型协作创建。由于技术限制，当前使用简化协作模式。

## 下一步
系统正在完善中，将提供更丰富的多角色协作功能。

---
*页面创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        tags = [title.lower().replace(" ", "_"), "协作", "ai"]
        return self.create_page(title, content, tags)

    def create_page(
        self, title: str, content: str, tags: Optional[list[str]] = None
    ) -> WikiPage:
        """重写页面创建方法，添加文件存在检查逻辑"""
        # 检查页面是否已存在
        if title in self._pages:
            existing_page = self._pages[title]

            # 检查文件是否为空或几乎为空
            if existing_page.file_path.exists():
                file_content = existing_page.file_path.read_text(encoding="utf-8")

                # 如果文件内容很少（小于50个字符），可以认为是空或几乎空
                if len(file_content.strip()) < 50:
                    # 更新页面内容并返回现有页面
                    self.update_page(title, content, tags)
                    return self._pages[title]
                else:
                    # 如果文件内容较多，应该将其视为已有内容，需要协同编辑
                    # 返回现有的页面对象，并提供协同编辑选项
                    return self._pages[title]
            else:
                # 文件不存在但条目存在，可能存在索引不一致的情况
                del self._pages[title]
                # 然后继续创建新页面
                return super().create_page(title, content, tags)
        else:
            # 页面不存在，正常创建
            return super().create_page(title, content, tags)

    def _validate_real_model_provider(self, model_provider):
        """验证使用真实的模型提供者，拒绝模拟"""
        # 检查是否是真实的LiteLLMProvider
        from daip_live.model_provider.provider import LiteLLMProvider

        if not isinstance(model_provider, LiteLLMProvider):
            raise ValueError(
                f"必须使用真实的LiteLLMProvider，不能使用模拟提供者: {type(model_provider)}"  # noqa: E501
            )

        # 检查是否配置了真实的模型
        if not hasattr(model_provider, "config") or not model_provider.config:
            raise ValueError("模型提供者未配置或配置无效")

        # 检查模型配置
        if (
            not hasattr(model_provider.config, "model")
            or not model_provider.config.model
        ):
            raise ValueError("模型提供者没有配置模型名称")

    def _validate_real_role_manager(self, role_model_manager):
        """验证使用真实的角色模型管理器"""
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

        if not isinstance(role_model_manager, RoleModelManager):
            raise ValueError(
                f"必须使用真实的RoleModelManager: {type(role_model_manager)}"
            )
