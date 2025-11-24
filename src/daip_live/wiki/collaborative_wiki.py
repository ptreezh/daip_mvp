"""
多角色协作维基词条创作服务
使用多模型辩论机制协同创建高质量维基词条
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from daip_live.core.models import (
    Role, DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent,
    ThoughtEvent
)
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.wiki.manager import WikiManager
from daip_live.wiki.models import WikiPage
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from .role_intelligence_selector import RoleIntelligenceSelector


class MultiRoleWikiCollaborator:
    """多角色协作维基词条创建器"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        role_manager: RoleManager,
        role_model_manager: RoleModelManager,
        model_provider: LiteLLMProvider,
        wiki_manager: WikiManager
    ):
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider
        self.wiki_manager = wiki_manager

        # 定义维基协作的主要角色类型
        self.default_roles = [
            "domain_expert",      # 领域专家 - 提供专业知识
            "researcher",         # 研究员 - 提供研究依据
            "editor",             # 编辑 - 负责结构和表述
            "critic",             # 批评家 - 挑剔和完善
        ]

        # 初始化智能角色选择器
        self.role_intelligence_selector = RoleIntelligenceSelector(
            role_manager=self.role_manager
        )
    
    async def create_collaborative_wiki(
        self,
        title: str,
        initial_topic: str,
        roles: Optional[List[str]] = None,
        rounds: int = 3
    ) -> Tuple[WikiPage, str]:
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
                    topic=initial_topic,
                    max_roles=4
                )
                print(f"[WIKI COLLAB] 基于主题 '{initial_topic}' 智能选择了角色: {roles}")
            except Exception as e:
                # 如果智能选择失败，回退到默认角色
                print(f"[WIKI COLLAB] 智能角色选择失败，使用默认角色: {e}")
                roles = self.default_roles

        print(f"[WIKI COLLAB] 使用角色列表: {roles}")

        # 创建一个临时的增强辩论管理器用于协作
        debate_manager = EnhancedDebateManager(
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            role_model_manager=self.role_model_manager,
            model_provider=self.model_provider,
            debate_history_tracker=None,
            use_optimized_architecture=True
        )

        # 收集各角色对维基词条的贡献
        contributions = {}

        # 提示模板 - 每个角色从自己的角度贡献内容
        role_prompts = {
            "domain_expert": f"作为领域专家，请从专业角度提供关于'{title}'的核心知识点和关键技术。",
            "researcher": f"作为研究员，请为'{title}'提供可靠的研究依据、数据支撑和引用来源。",
            "editor": f"作为编辑，请为'{title}'构建清晰的结构、规范的格式和流畅的表述。",
            "critic": f"作为批评家，请审视'{title}'的不足之处，提出改进意见和反驳观点。",
        }

        # 让每个角色依次贡献内容
        async for event in debate_manager.run_debate(initial_topic, roles, rounds):
            if isinstance(event, DebateTurnCompleteEvent):
                role_name = event.participant
                contribution = event.content_preview

                if role_name not in contributions:
                    contributions[role_name] = []

                contributions[role_name].append(contribution)

                # 发布思考事件以更新UI
                thought_event = ThoughtEvent(content=f"{role_name} 为'{title}'贡献了内容")

        # 整合所有角色的贡献
        wiki_content = await self._synthesize_wiki_content(title, contributions, initial_topic)

        # 创建维基页面
        tags = self._extract_tags_from_content(title, wiki_content)
        wiki_page = self.wiki_manager.create_page(
            title=title,
            content=wiki_content,
            tags=tags
        )

        return wiki_page, wiki_content
    
    async def _synthesize_wiki_content(self, title: str, contributions: Dict[str, List[str]], topic: str) -> str:
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
            "## 参考资料": []
        }
        
        for role_name, role_contributions in contributions.items():
            combined_content = "\n\n".join(role_contributions)
            
            # 根据角色类型将贡献分配到相应部分
            if role_name == "domain_expert":
                sections["## 定义与背景"].append(f"### {role_name.title()}观点\n{combined_content}")
                sections["## 关键特点"].append(f"### {role_name.title()}提供的技术细节\n{combined_content}")
            elif role_name == "researcher":
                sections["## 发展现状"].append(f"### 研究数据支撑\n{combined_content}")
                sections["## 参考资料"].append(f"### {combined_content}")
            elif role_name == "editor":
                sections["## 概述"].append(f"### 结构化概述\n{combined_content}")
            elif role_name == "critic":
                sections["## 优缺点分析"].append(f"### 批评与改进意见\n{combined_content}")
            else:
                # 其他角色添加到概述部分
                sections["## 概述"].append(f"### {role_name.title()}观点\n{combined_content}")
        
        # 组合成完整维基内容
        content_parts = [
            f"# {title}",
            f"\n> 协作创建于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n本词条由多个AI角色协作创建，融合了不同领域的专业见解。\n",
        ]
        
        # 添加各部分内容
        for section_title, section_contents in sections.items():
            if section_contents:  # 只添加非空部分
                content_parts.append(f"\n{section_title}")
                for content in section_contents:
                    content_parts.append(f"\n{content}")
        
        # 添加协作说明
        content_parts.extend([
            "\n## 协作说明",
            f"\n此词条由以下角色协作完成:",
            f"- domain_expert: 提供专业知识",
            f"- researcher: 提供研究依据", 
            f"- editor: 负责结构和表述",
            f"- critic: 负责审视和完善",
            f"\n协作主题: {topic}",
        ])
        
        return "\n".join(content_parts)
    
    def _extract_tags_from_content(self, title: str, content: str) -> List[str]:
        """从内容中提取标签"""
        import re
        
        # 提取关键词作为标签
        tags = [title.lower().replace(" ", "_")]
        
        # 从内容中提取可能的关键词
        # 简单提取包含大写字母的单词或技术术语
        potential_tags = re.findall(r'\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b', content)
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
        role_manager: Optional[RoleManager] = None
    ):
        super().__init__(wiki_root, role_model_manager, model_provider)
        
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.collaborator = None
        
        if all([session_manager, role_manager, role_model_manager, model_provider]):
            self.collaborator = MultiRoleWikiCollaborator(
                session_manager=session_manager,
                role_manager=role_manager,
                role_model_manager=role_model_manager,
                model_provider=model_provider,
                wiki_manager=self
            )
    
    async def create_collaborative_wiki(
        self,
        title: str,
        topic: str,
        roles: Optional[List[str]] = None,
        rounds: int = 3
    ) -> Tuple[WikiPage, str]:
        """创建协作维基词条

        Returns:
            Tuple[WikiPage, str]: (维基页面对象, 格式化内容字符串)
        """
        if not self.collaborator:
            raise RuntimeError("Cannot create collaborative wiki without required dependencies")

        return await self.collaborator.create_collaborative_wiki(
            title=title,
            initial_topic=topic,
            roles=roles,
            rounds=rounds
        )