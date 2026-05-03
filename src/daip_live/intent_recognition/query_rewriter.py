"""
查询重写器

专门负责查询文本的预处理和上下文注入
基于现有session_context_recognizer扩展理念
遵循SOLID原则中的单一职责原则
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Entity:
    """实体数据类"""
    name: str
    value: str
    position: Tuple[int, int]
    confidence: float
    entity_type: str


class QueryRewriter:
    """
    查询重写器

    专门负责查询文本的预处理和上下文注入
    遵循SOLID原则：
    - SRP: 仅处理查询重写
    - OCP: 可扩展更多重写规则
    """

    def __init__(self, entity_extractor: Optional['EntityExtractor'] = None):
        """
        构造函数

        Args:
            entity_extractor: 实体提取器，用于指代消解
        """
        self.entity_extractor = entity_extractor
        self.logger = logging.getLogger(__name__)

    def rewrite_query_with_context(self, text: str, session_id: str) -> str:
        """
        基于会话上下文重写查询

        Args:
            text: 原始查询文本
            session_id: 会话ID

        Returns:
            重写后的查询文本
        """
        # 获取会话中的相关实体
        entities = []
        if self.entity_extractor:
            entities = self.entity_extractor.extract_entities_from_context(session_id)

        # 执行代词消解
        resolved_text = self.resolve_pronouns(text, entities)

        # 执行省略表达补全
        completed_text = self.expand_ellipsis(resolved_text, entities)

        return completed_text

    def resolve_pronouns(self, text: str, entities: List[Entity]) -> str:
        """
        执行代词消解

        Args:
            text: 输入文本
            entities: 上下文中的实体列表

        Returns:
            消解代词后的文本
        """
        # 定义代词消解规则
        pronoun_rules = [
            # 规则格式：(代词模式, 对应实体类型, 替换逻辑)
            ('它', ['paper_id', 'topic', 'title', 'query'], self._resolve_it_pronoun),
            ('这', ['topic', 'argument', 'concept', 'title'], self._resolve_this_pronoun),
            ('那', ['topic', 'argument', 'concept', 'title'], self._resolve_that_pronoun),
            ('这个', ['topic', 'argument', 'concept', 'title'], self._resolve_this_pronoun),
            ('那个', ['topic', 'argument', 'concept', 'title'], self._resolve_that_pronoun),
            ('这些', ['topics', 'arguments', 'concepts', 'titles'], self._resolve_these_pronoun),
            ('那些', ['topics', 'arguments', 'concepts', 'titles'], self._resolve_those_pronoun),
        ]

        result_text = text

        for pronoun, entity_types, resolver_func in pronoun_rules:
            # 查找文本中的代词
            if pronoun in result_text:
                # 在实体中找到最相关的实体进行替换
                relevant_entity = self._find_most_relevant_entity(entities, entity_types)
                if relevant_entity:
                    # 应用消解规则
                    result_text = resolver_func(result_text, pronoun, relevant_entity.value)

        return result_text

    def _resolve_it_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
        """
        解析"它"代词
        """
        # 使用正则替换，确保上下文准确性
        return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

    def _resolve_this_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
        """
        解析"这/这个"代词
        """
        return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

    def _resolve_that_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
        """
        解析"那/那个"代词
        """
        return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

    def _resolve_these_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
        """
        解析"这些"代词
        """
        return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

    def _resolve_those_pronoun(self, text: str, pronoun: str, entity_value: str) -> str:
        """
        解析"那些"代词
        """
        return re.sub(r'\b' + re.escape(pronoun) + r'\b', entity_value, text)

    def _find_most_relevant_entity(self, entities: List[Entity],
                                   target_types: List[str]) -> Optional[Entity]:
        """
        根据类型查找最相关的实体
        """
        # 按类型匹配优先级查找
        for entity_type in target_types:
            for entity in entities:
                if entity.entity_type == entity_type:
                    return entity

        # 如果没有精确匹配，返回第一个匹配的实体
        for entity in entities:
            if entity.entity_type in target_types:
                return entity

        return None

    def expand_ellipsis(self, text: str, entities: List[Entity]) -> str:
        """
        补全省略表达

        Args:
            text: 输入文本
            entities: 上下文实体

        Returns:
            补全后的文本
        """
        # 常见省略表达映射
        ellipsis_patterns = [
            (r'是\s*[\uff0c\uff1a\u002c\u003a]?', r'是(上文提到的内容)'),  # "是：" -> "是(上文提到的内容)"
            (r'好\s*[\uff0c\uff1a\u002c\u003a]?', r'好(按你说的)'),  # "好：" -> "好(按你说的)"
            (r'行\s*[\uff0c\uff1a\u002c\u003a]?', r'行(按计划)'),  # "行：" -> "行(按计划)"
            (r'对\s*[\uff0c\uff1a\u002c\u003a]?', r'对(你说的)'),  # "对：" -> "对(你说的)"
        ]

        result_text = text

        for pattern, replacement in ellipsis_patterns:
            result_text = re.sub(pattern, replacement, result_text)

        # 检查是否包含上下文引用
        context_reference_patterns = [
            r'它\s+怎么样',      # "它怎么样"
            r'这个\s+如何',      # "这个如何"
            r'那\s+呢',         # "那呢"
            r'那个\s+呢',       # "那个呢"
        ]

        for pattern in context_reference_patterns:
            if re.search(pattern, result_text):
                # 如果是上下文引用，保留实体引用
                for entity in entities:
                    if entity.entity_type in ['paper_id', 'topic', 'title', 'query']:
                        # 在上下文引用中明确提及实体
                        if '它怎么样' in result_text:
                            result_text = result_text.replace('它怎么样', f'{entity.value}怎么样')
                        elif '这个如何' in result_text:
                            result_text = result_text.replace('这个如何', f'{entity.value}如何')
                        elif '那呢' in result_text:
                            result_text = result_text.replace('那呢', f'{entity.value}呢')
                        elif '那个呢' in result_text:
                            result_text = result_text.replace('那个呢', f'{entity.value}呢')

        return result_text

    def enhance_with_context(self, text: str, context: Dict[str, Any]) -> str:
        """
        使用上下文信息增强查询

        Args:
            text: 原始查询文本
            context: 上下文信息

        Returns:
            增强后的查询文本
        """
        enhanced_text = text

        # 添加话题上下文
        current_topic = context.get('current_topic', '')
        if current_topic and self._is_topic_relevant(text, current_topic):
            enhanced_text = f"关于{current_topic}，{text}"

        # 添加参数上下文
        parameters = context.get('parameters', {})
        for param_name, param_value in parameters.items():
            if str(param_value) in text:
                # 参数已经在文本中，不需要额外处理
                continue
            elif self._should_add_parameter_context(text, param_name, param_value):
                enhanced_text = f"{param_value} 相关的 {text}"

        return enhanced_text

    def _is_topic_relevant(self, query: str, topic: str) -> bool:
        """
        检查查询是否与话题相关
        """
        if not topic:
            return False

        query_lower = query.lower()
        topic_lower = topic.lower()

        # 检查话题是否在查询中或有词汇重叠
        if topic_lower in query_lower:
            return True

        query_words = set(query_lower.split())
        topic_words = set(topic_lower.split())
        common_words = query_words.intersection(topic_words)

        return len(common_words) > 0

    def _should_add_parameter_context(self, query: str, param_name: str, param_value: Any) -> bool:
        """
        判断是否应该添加参数上下文
        """
        # 检查参数是否与查询相关
        query_lower = query.lower()
        param_lower = str(param_value).lower()

        # 参数值在查询中出现
        if param_lower in query_lower:
            return False  # 已经包含，不需要添加

        # 参数名称与查询主题相关
        related_param_names = ['topic', 'title', 'query', 'search_term', 'paper_id']
        if param_name in related_param_names:
            return True

        return False

    def process_query_for_padatious(self, text: str, session_id: str, context: Dict[str, Any]) -> str:
        """
        为Padatious处理查询文本

        Args:
            text: 原始查询文本
            session_id: 会话ID
            context: 上下文信息

        Returns:
            为Padatious优化的查询文本
        """
        # 1. 基于上下文重写查询
        rewritten_query = self.rewrite_query_with_context(text, session_id)

        # 2. 使用上下文信息增强
        enhanced_query = self.enhance_with_context(rewritten_query, context)

        # 3. 清理并规范化文本
        normalized_query = self._normalize_query(enhanced_query)

        return normalized_query

    def _normalize_query(self, text: str) -> str:
        """
        规范化查询文本

        Args:
            text: 输入文本

        Returns:
            规范化后的文本
        """
        # 移除多余的空格
        normalized = re.sub(r'\s+', ' ', text.strip())

        # 标准化标点符号
        normalized = normalized.replace('，', ',').replace('。', '.').replace('？', '?').replace('！', '!')

        # 移除多余的标点
        normalized = re.sub(r'[.!?]+', '.', normalized)  # 将多个标点替换为单个句号

        return normalized