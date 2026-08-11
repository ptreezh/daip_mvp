"""
简化协作引擎
绕过复杂的辩论系统，提供直接的多角色协作功能
支持实时进度展示和用户界面集成
"""

import asyncio
from datetime import datetime
from typing import Any, Callable, Optional

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

from .manager import WikiManager


class CollaborationProgress:
    """协作进度信息"""

    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
        self.current_role = None
        self.current_action = "准备中..."
        self.generated_content = []
        self.errors = []
        self.start_time = datetime.now()
        self.is_complete = False

    def update(self, role: str, action: str, content: Optional[str] = None):
        """更新进度"""
        self.current_step += 1
        self.current_role = role
        self.current_action = action

        if content:
            self.generated_content.append(
                {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append({"error": error, "timestamp": datetime.now().isoformat()})

    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        return (
            (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_steps": self.total_steps,
            "current_step": self.current_step,
            "progress_percentage": self.get_progress_percentage(),
            "current_role": self.current_role,
            "current_action": self.current_action,
            "generated_content": self.generated_content,
            "errors": self.errors,
            "start_time": self.start_time.isoformat(),
            "is_complete": self.is_complete,
            "elapsed_seconds": (datetime.now() - self.start_time).total_seconds(),
        }


class SimpleCollaborationEngine:
    """简化协作引擎"""

    def __init__(
        self,
        role_model_manager: RoleModelManager,
        model_provider: LiteLLMProvider,
        wiki_manager: WikiManager,
        progress_callback: Optional[Callable[[CollaborationProgress], None]] = None,
    ):
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider
        self.wiki_manager = wiki_manager
        self.progress_callback = progress_callback
        self.current_progress = None

        # 默认角色提示模板
        self.role_prompts = {
            "domain_expert": "作为领域专家，请从专业角度提供关于'{topic}'的核心知识点和关键技术。",  # noqa: E501
            "researcher": "作为研究员，请为'{topic}'提供可靠的研究依据、数据支撑和引用来源。",  # noqa: E501
            "editor": "作为编辑，请为'{topic}'构建清晰的结构、规范的格式和流畅的表述。",
            "critic": "作为批评家，请审视'{topic}'的不足之处，提出改进意见和反驳观点。",
            "analyst": "作为分析师，请分析'{topic}'的市场前景、发展趋势和商业价值。",
            "teacher": "作为教师，请用通俗易懂的方式解释'{topic}'的基础概念和应用实例。",  # noqa: E501
        }

    async def create_collaborative_wiki(
        self, title: str, topic: str, roles: Optional[list[str]] = None, rounds: int = 1
    ) -> tuple:
        """创建协作维基页面

        Args:
            title: 维基页面标题
            topic: 协作主题
            roles: 参与协作的角色列表，如果为None则使用默认角色
            rounds: 协作轮数

        Returns:
            tuple: (WikiPage对象, 格式化内容字符串)
        """
        if roles is None:
            # 默认使用 roles/ 目录中真实存在的角色
            roles = ["pro_arguer", "con_arguer", "research_analyst"]

        total_steps = len(roles) * rounds
        progress = CollaborationProgress(total_steps)

        try:
            # 收集各角色的贡献
            contributions = {}

            for round_num in range(1, rounds + 1):
                for role in roles:
                    # 更新进度
                    progress.update(role, f"正在生成{role}的贡献（第{round_num}轮）")

                    if self.progress_callback:
                        self.progress_callback(progress)

                    # 生成角色贡献
                    try:
                        contribution = await self._generate_role_contribution(
                            role, topic
                        )

                        if role not in contributions:
                            contributions[role] = []
                        contributions[role].append(contribution)

                        # 更新进度
                        progress.update(
                            role, f"{role}贡献完成（第{round_num}轮）", contribution
                        )

                        if self.progress_callback:
                            self.progress_callback(progress)

                        # 添加小延迟以便UI更新
                        await asyncio.sleep(0.1)

                    except Exception as e:
                        error_msg = f"{role}生成贡献时出错: {str(e)}"
                        progress.add_error(error_msg)
                        if self.progress_callback:
                            self.progress_callback(progress)

            # 所有角色都失败时不得创建空页面（避免假成功）
            if not contributions:
                raise RuntimeError(
                    f"所有角色（{', '.join(roles)}）的贡献生成均失败，"
                    f"未创建任何 wiki 内容"
                ) from None

            # 整合内容
            progress.update("系统", "正在整合所有角色的贡献...")
            if self.progress_callback:
                self.progress_callback(progress)

            wiki_content = self._synthesize_collaborative_content(
                title, contributions, topic
            )

            # 创建维基页面
            tags = self._extract_tags_from_content(title, wiki_content)
            wiki_page = self.wiki_manager.create_page(title, wiki_content, tags)

            progress.update("系统", "协作完成！")
            progress.is_complete = True
            self.current_progress = progress
            if self.progress_callback:
                self.progress_callback(progress)

            return wiki_page, wiki_content

        except Exception as e:
            progress.add_error(f"协作过程失败: {str(e)}")
            if self.progress_callback:
                self.progress_callback(progress)
            raise

    async def _generate_role_contribution(self, role: str, topic: str) -> str:
        """生成单个角色的贡献"""
        # 获取角色模型配置
        try:
            mapping = self.role_model_manager.get_role_model_mapping(
                role, use_debate_config=True
            )
            if not mapping:
                # 使用默认配置
                mapping = self.role_model_manager.get_role_model_mapping(
                    role, use_debate_config=False
                )
        except Exception:
            # 如果无法获取角色映射，使用默认配置
            mapping = None

        if mapping:
            model_config = mapping.role_model_config
            model_name = model_config.model_name
            temperature = getattr(model_config, "temperature", 0.7)
            max_tokens = getattr(model_config, "max_tokens", 1000)
        else:
            # 默认模型配置
            model_name = "ollama/llama3:instruct"
            temperature = 0.7
            max_tokens = 1000

        # 构建提示
        prompt_template = self.role_prompts.get(
            role, self.role_prompts["domain_expert"]
        )
        prompt = prompt_template.format(topic=topic)

        prompt += f"""

请提供详细、专业的贡献内容，长度控制在200-500字之间。
你的贡献将与其他角色的内容整合，创建一个完整的维基词条。
主题：{topic}
角色：{role}

请直接提供内容，不需要包含角色说明或格式标记。"""

        # 生成内容 - 实现智能模型回退机制
        from daip_live.utils.model_availability import (
            PREFERRED_MODELS,
        )

        # 如果原模型不可用，尝试查找可用模型
        if model_name not in PREFERRED_MODELS:
            # 将当前模型加入首选列表的开始
            all_models_to_try = [model_name] + PREFERRED_MODELS
        else:
            # 当前模型已经在首选列表中，直接使用
            all_models_to_try = [model_name] + [
                m for m in PREFERRED_MODELS if m != model_name
            ]

        for idx, attempt_model in enumerate(all_models_to_try):
            try:
                # 契约: agenerate(prompt, model=..., temperature=..., max_tokens=...)
                # 返回 (content, metadata)；generate 是 async generator 不能解包
                content, _ = await self.model_provider.agenerate(
                    prompt,
                    model=attempt_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return content.strip()
            except Exception:
                if idx < len(all_models_to_try) - 1:  # 不是最后一个模型
                    continue
                else:
                    # 所有模型都失败：明确报错（不返回模拟假内容）
                    raise RuntimeError(
                        f"所有候选模型均调用失败（角色 {role}，主题 {topic[:50]}），"
                        f"已尝试: {', '.join(all_models_to_try)}"
                    ) from None

    def _synthesize_collaborative_content(
        self, title: str, contributions: dict[str, list[str]], topic: str
    ) -> str:
        """整合协作内容为完整的维基词条"""

        # 定义内容结构
        sections = {
            "## 概述": [],
            "## 核心概念": [],
            "## 技术要点": [],
            "## 应用场景": [],
            "## 研究进展": [],
            "## 挑战与展望": [],
            "## 参考资料": [],
        }

        # 按角色分配内容到不同章节（映射真实角色，未知角色按内容关键词路由）
        for role_name, role_contributions in contributions.items():
            combined_content = "\n\n".join(role_contributions)

            if role_name == "domain_expert":
                sections["## 核心概念"].append(
                    f"### {role_name.title()}视角\n{combined_content}"
                )
                sections["## 技术要点"].append(
                    f"### {role_name.title()}技术分析\n{combined_content}"
                )
            elif role_name in ("researcher", "research_analyst"):
                sections["## 研究进展"].append(f"### 研究数据\n{combined_content}")
                sections["## 参考资料"].append(f"### {combined_content}")
            elif role_name in ("editor", "creative_writer"):
                sections["## 概述"].append(f"### 结构化概述\n{combined_content}")
            elif role_name in ("critic", "con_arguer"):
                sections["## 挑战与展望"].append(f"### 批判性分析\n{combined_content}")
            elif role_name in ("analyst", "pro_arguer"):
                sections["## 应用场景"].append(f"### 市场分析\n{combined_content}")
                sections["## 技术要点"].append(f"### 技术分析\n{combined_content}")
            elif role_name == "teacher":
                sections["## 核心概念"].append(f"### 基础概念解释\n{combined_content}")
            else:
                # 未知角色：按内容关键词路由到相关章节
                routed = False
                for keyword, section in (
                    ("技术", "## 技术要点"),
                    ("研究", "## 研究进展"),
                    ("应用", "## 应用场景"),
                    ("挑战", "## 挑战与展望"),
                    ("参考", "## 参考资料"),
                ):
                    if keyword in combined_content:
                        sections[section].append(
                            f"### {role_name.title()}观点\n{combined_content}"
                        )
                        routed = True
                        break
                if not routed:
                    # 其他角色添加到概述
                    sections["## 概述"].append(
                        f"### {role_name.title()}观点\n{combined_content}"
                    )

        # 构建完整内容
        content_parts = [
            f"# {title}",
            f"\n> 协作创建于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n本词条由多个AI角色协作创建，融合了不同领域的专业见解。",
            f"\n## 协作主题\n{topic}\n",
        ]

        # 添加各部分内容
        for section_title, section_contents in sections.items():
            if section_contents:  # 只添加非空部分
                content_parts.append(f"\n{section_title}")
                for content in section_contents:
                    content_parts.append(f"\n{content}")

        # 添加协作说明
        participating_roles = ", ".join(contributions.keys())
        content_parts.extend(
            [
                "\n## 协作说明",
                "\n此词条由以下角色协作完成:",
                f"- {participating_roles}",
                "\n协作方式: 多角色AI协作",
                f"\n总贡献数: {sum(len(contribs) for contribs in contributions.values())}",  # noqa: E501
            ]
        )

        return "\n".join(content_parts)

    def _extract_tags_from_content(self, title: str, content: str) -> list[str]:
        """从内容中提取标签"""
        import re

        tags = [title.lower().replace(" ", "_")]

        # 提取关键词
        potential_tags = re.findall(r"\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b", content)
        potential_tags = [tag.lower() for tag in potential_tags if len(tag) > 2]
        tags.extend(potential_tags[:8])  # 只取前8个

        # 去重
        unique_tags = []
        for tag in tags:
            if tag not in unique_tags:
                unique_tags.append(tag)

        return unique_tags[:12]  # 最多12个标签


class CollaborationEngineWithUI:
    """带UI展示的协作引擎"""

    def __init__(self, simple_engine: SimpleCollaborationEngine):
        self.simple_engine = simple_engine
        self.current_progress = None
        self.progress_history = []

    def progress_callback(self, progress: CollaborationProgress):
        """进度回调函数"""
        self.current_progress = progress
        self.progress_history.append(progress.to_dict())

        # 这里可以添加UI更新逻辑
        self._update_ui_display(progress)

    def _update_ui_display(self, progress: CollaborationProgress):
        """更新UI显示（可以扩展为具体的TUI更新）"""
        self._create_progress_bar(progress.get_progress_percentage())

        if progress.errors:
            for error in progress.errors[-1:]:  # 只显示最新错误
                pass

    def _create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """创建进度条"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

    async def create_collaborative_wiki_with_display(
        self, title: str, topic: str, roles: Optional[list[str]] = None, rounds: int = 1
    ) -> tuple:
        """创建协作维基页面并显示进度"""

        # 临时替换进度回调
        original_callback = self.simple_engine.progress_callback
        self.simple_engine.progress_callback = self.progress_callback

        try:
            result = await self.simple_engine.create_collaborative_wiki(
                title, topic, roles, rounds
            )

            if self.current_progress and self.current_progress.is_complete:
                pass

            return result

        finally:
            # 恢复原始回调
            self.simple_engine.progress_callback = original_callback
