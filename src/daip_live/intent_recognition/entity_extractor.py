"""
实体提取器

专门负责从对话历史和上下文中提取实体
遵循SOLID原则中的单一职责原则
"""

import logging
import re
from typing import TYPE_CHECKING, Any, Optional

from .query_rewriter import Entity

if TYPE_CHECKING:
    from daip_live.agent_engine.session_manager import SessionManager
    from daip_live.intent_recognition.enhanced_context_manager import (
        EnhancedContextManager,
    )


class EntityExtractor:
    """
    实体提取器

    专门负责从对话历史和上下文中提取实体
    遵循SOLID原则：
    - SRP: 仅负责实体提取
    - DIP: 依赖SessionManager和ContextManager抽象
    """

    def __init__(
        self,
        session_manager: Optional["SessionManager"] = None,
        context_manager: Optional["EnhancedContextManager"] = None,
    ):
        """
        构造函数

        Args:
            session_manager: 会话管理器
            context_manager: 上下文管理器
        """
        self.session_manager = session_manager
        self.context_manager = context_manager
        self.logger = logging.getLogger(__name__)

    def extract_entities_from_context(self, session_id: str) -> list[Entity]:
        """
        从会话上下文中提取实体

        Args:
            session_id: 会话ID

        Returns:
            实体列表
        """
        entities = []

        # 从参数中提取实体
        if self.context_manager:
            try:
                conversation_context = self.context_manager.get_conversation_context(
                    session_id
                )
                if conversation_context:
                    # 从参数中提取实体
                    for (
                        param_name,
                        param_value,
                    ) in conversation_context.get_filled_parameters().items():
                        entities.append(
                            Entity(
                                name=param_name,
                                value=param_value,
                                position=(0, len(str(param_value))),
                                confidence=0.9,
                                entity_type=self._infer_entity_type(
                                    param_name, param_value
                                ),
                            )
                        )

                    # 从已填充的参数中提取
                    for param_name, meta in conversation_context.parameters.items():
                        entities.append(
                            Entity(
                                name=param_name,
                                value=meta.value,
                                position=(0, len(str(meta.value))),
                                confidence=meta.confidence,
                                entity_type=meta.source.value
                                if hasattr(meta.source, "value")
                                else "parameter",
                            )
                        )
            except Exception as e:
                self.logger.warning(
                    f"Failed to extract entities from EnhancedContextManager: {e}"
                )

        # 从会话历史中提取实体
        if self.session_manager:
            try:
                session_history_entities = self._extract_entities_from_session_history(
                    session_id
                )
                entities.extend(session_history_entities)
            except Exception as e:
                self.logger.warning(
                    f"Failed to extract entities from session history: {e}"
                )

        # 从基础上下文管理器中提取
        if self.context_manager:
            try:
                base_context = self.context_manager.get_context(session_id)
                if base_context and isinstance(base_context, dict):
                    for param_name, param_value in base_context.items():
                        if isinstance(param_value, (str, int, float)):
                            entities.append(
                                Entity(
                                    name=param_name,
                                    value=param_value,
                                    position=(0, len(str(param_value))),
                                    confidence=0.8,
                                    entity_type=self._infer_entity_type(
                                        param_name, param_value
                                    ),
                                )
                            )
            except Exception as e:
                self.logger.warning(
                    f"Failed to extract entities from base context: {e}"
                )

        return entities

    def _extract_entities_from_session_history(self, session_id: str) -> list[Entity]:
        """
        从会话历史中提取实体

        Args:
            session_id: 会话ID

        Returns:
            从会话历史提取的实体列表
        """
        entities = []

        # 尝试从通用会话管理器获取历史
        if hasattr(self.session_manager, "get_session_context"):
            try:
                session_context = self.session_manager.get_session_context(session_id)
                if session_context:
                    dialogue_history = session_context.get("dialogue_history", [])
                    for turn in dialogue_history[-10:]:  # 最近10次对话
                        if isinstance(turn, dict):
                            content = turn.get("content", "")
                            turn_entities = self._extract_entities_from_text(content)
                            entities.extend(turn_entities)
            except Exception as e:
                self.logger.warning(
                    f"Failed to extract entities from universal session context: {e}"
                )

        # 尝试从传统会话管理器获取历史
        try:
            session = (
                self.session_manager.get_session(session_id)
                if hasattr(self.session_manager, "get_session")
                else None
            )
            if session and hasattr(session, "history"):
                for turn in session.history[-5:]:  # 最近5次对话
                    if hasattr(turn, "content"):
                        turn_entities = self._extract_entities_from_text(turn.content)
                        entities.extend(turn_entities)
        except Exception as e:
            self.logger.warning(
                f"Failed to extract entities from traditional session: {e}"
            )

        return entities

    def _extract_entities_from_text(self, text: str) -> list[Entity]:
        """
        从文本中提取实体

        Args:
            text: 输入文本

        Returns:
            从文本提取的实体列表
        """
        entities = []

        if not text:
            return entities

        # 提取arXiv论文ID (如 arXiv ID: 1234.56789)
        paper_id_matches = re.finditer(r"\b(\d{4}\.\d{4,5}(v\d+)?)\b", text)
        for match in paper_id_matches:
            entities.append(
                Entity(
                    name="paper_id",
                    value=match.group(1),
                    position=match.span(),
                    confidence=1.0,
                    entity_type="paper_id",
                )
            )

        # 提取URL
        url_matches = re.finditer(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
        for match in url_matches:
            entities.append(
                Entity(
                    name="url",
                    value=match.group(0),
                    position=match.span(),
                    confidence=0.95,
                    entity_type="url",
                )
            )

        # 提取邮箱地址
        email_matches = re.finditer(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
        )
        for match in email_matches:
            entities.append(
                Entity(
                    name="email",
                    value=match.group(0),
                    position=match.span(),
                    confidence=0.9,
                    entity_type="email",
                )
            )

        # 提取数字（可能表示轮数、数量等）
        number_matches = re.finditer(r"\b\d+\b", text)
        for match in number_matches:
            num_value = int(match.group(0))
            # 如果数字在合理范围内（如轮数），则认为是实体
            if 1 <= num_value <= 100:  # 轮数等通常不会超过100
                entities.append(
                    Entity(
                        name="number",
                        value=num_value,
                        position=match.span(),
                        confidence=0.7,
                        entity_type="number",
                    )
                )

        # 提取可能的主题词或标题
        # 匹配引号中的内容（如"人工智能"、'机器学习'）
        quoted_matches = re.finditer(r'["""]([^"""]+)["""]|[' "](.*?)[" "]", text)
        for match in quoted_matches:
            content = match.group(1) or match.group(2)  # 获取引号内的内容
            if len(content) >= 2:  # 至少2个字符才认为是有效内容
                entities.append(
                    Entity(
                        name="quoted_content",
                        value=content,
                        position=match.span(),
                        confidence=0.8,
                        entity_type="topic",
                    )
                )

        # 提取可能的学术主题（包含特定关键词的短语）
        academic_keywords = [
            "算法",
            "模型",
            "系统",
            "方法",
            "技术",
            "理论",
            "应用",
            "研究",
            "分析",
            "设计",
            "实现",
        ]
        for keyword in academic_keywords:
            if keyword in text:
                # 提取包含关键词的短语
                phrase_pattern = r"[\w\s]*" + keyword + r"[\w\s]*"
                phrase_matches = re.finditer(phrase_pattern, text)
                for match in phrase_matches:
                    phrase = match.group(0).strip()
                    if len(phrase) >= 4:  # 短语长度至少4个字符
                        entities.append(
                            Entity(
                                name="academic_topic",
                                value=phrase,
                                position=match.span(),
                                confidence=0.75,
                                entity_type="topic",
                            )
                        )

        # 提取使用冒号定义的内容（如"主题：AI伦理"）
        colon_pattern = r"(\w+(?:\s+\w+)?)\s*[:：]\s*([^\s，。,.\n]+)"
        colon_matches = re.finditer(colon_pattern, text)
        for match in colon_matches:
            field_name = match.group(1).strip()
            field_value = match.group(2).strip()
            entities.append(
                Entity(
                    name=field_name,
                    value=field_value,
                    position=match.span(),
                    confidence=0.85,
                    entity_type=self._infer_entity_type(field_name, field_value),
                )
            )

        return entities

    def _infer_entity_type(self, param_name: str, param_value: Any) -> str:
        """
        推断实体类型

        Args:
            param_name: 参数名称
            param_value: 参数值

        Returns:
            实体类型
        """
        # 基于参数名称推断类型
        name_lower = param_name.lower()
        str(param_value).lower()

        # 论文相关实体
        if any(keyword in name_lower for keyword in ["paper", "id", "arxiv"]):
            return "paper_id"
        elif any(keyword in name_lower for keyword in ["query", "search", "topic"]):
            return "topic"
        elif any(keyword in name_lower for keyword in ["title", "name", "subject"]):
            return "title"
        elif any(keyword in name_lower for keyword in ["round", "count", "number"]):
            return "number"
        elif any(
            keyword in name_lower for keyword in ["content", "text", "description"]
        ):
            return "content"

        # 基于参数值的特征推断
        if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", str(param_value)):
            return "paper_id"
        elif len(str(param_value)) <= 3 and str(param_value).isdigit():
            return "number"
        elif len(str(param_value)) > 50:  # 长文本
            return "content"

        # 默认类型
        return "parameter"

    def extract_entities_by_type(
        self, session_id: str, entity_type: str
    ) -> list[Entity]:
        """
        按类型提取实体

        Args:
            session_id: 会话ID
            entity_type: 实体类型

        Returns:
            指定类型的实体列表
        """
        all_entities = self.extract_entities_from_context(session_id)
        return [entity for entity in all_entities if entity.entity_type == entity_type]

    def find_most_recent_entity(
        self, session_id: str, entity_type: str
    ) -> Optional[Entity]:
        """
        查找最近的指定类型实体

        Args:
            session_id: 会话ID
            entity_type: 实体类型

        Returns:
            最近的实体或None
        """
        entities = self.extract_entities_by_type(session_id, entity_type)
        return entities[-1] if entities else None
