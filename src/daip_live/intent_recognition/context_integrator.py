"""
上下文集成器

专门负责从现有系统获取上下文并为意图识别服务
遵循SOLID原则中的单一职责和依赖倒置原则
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class ContextIntegrator:
    """
    上下文集成器

    专门负责从现有系统获取上下文并为意图识别服务
    遵循SOLID原则：
    - SRP: 仅负责上下文获取和注入
    - OCP: 可扩展处理更多上下文类型
    - DIP: 依赖会话和上下文管理器的抽象接口
    """

    def __init__(self, session_manager: Optional['SessionManager'] = None,
                 context_manager: Optional['EnhancedContextManager'] = None):
        """
        构造函数，注入依赖

        Args:
            session_manager: 会话管理器
            context_manager: 上下文管理器
        """
        self.session_manager = session_manager
        self.context_manager = context_manager
        self.logger = logging.getLogger(__name__)

    def get_context_for_intent_recognition(self, session_id: str) -> Dict[str, Any]:
        """
        获取用于意图识别的上下文信息

        Args:
            session_id: 会话ID

        Returns:
            包含上下文信息的字典
        """
        context_info = {
            'session_id': session_id,
            'current_topic': '',
            'current_intent': '',
            'intent_history': [],
            'parameters': {},
            'conversation_history': [],
            'related_entities': [],
            'context_signals': {},
            'last_accessed': datetime.now().isoformat()
        }

        # 获取现有上下文
        if self.context_manager:
            try:
                context = self.context_manager.get_conversation_context(session_id)
                if context:
                    context_info['current_topic'] = getattr(context, 'topic', '')
                    context_info['current_intent'] = getattr(context, 'current_intent', '')
                    context_info['intent_history'] = getattr(context, 'intent_history', [])
                    context_info['parameters'] = context.get_filled_parameters()
                    context_info['related_entities'] = list(getattr(context, 'related_entities', set()))
            except Exception as e:
                self.logger.warning(f"Failed to get conversation context from EnhancedContextManager: {e}")

            # 也尝试从基础上下文管理器获取
            try:
                base_context = self.context_manager.get_context(session_id)
                if base_context and isinstance(base_context, dict):
                    context_info['parameters'].update(base_context.get('parameters', {}))
                    context_info['current_topic'] = base_context.get('topic', context_info['current_topic'])
                    context_info['current_intent'] = base_context.get('current_intent', context_info['current_intent'])
            except Exception as e:
                self.logger.warning(f"Failed to get base context from EnhancedContextManager: {e}")

        # 获取会话历史
        if self.session_manager:
            try:
                # 尝试从通用会话管理器获取会话上下文
                if hasattr(self.session_manager, 'get_session_context'):
                    session_context = self.session_manager.get_session_context(session_id)
                    if session_context:
                        context_info['conversation_history'] = session_context.get('dialogue_history', [])
                        context_info['parameters'].update(session_context.get('personal_context', {}))
            except Exception as e:
                self.logger.warning(f"Failed to get session context from UniversalSessionManager: {e}")

            # 尝试从传统会话管理器获取
            try:
                session = self.session_manager.get_session(session_id) if hasattr(self.session_manager, 'get_session') else None
                if session and hasattr(session, 'history'):
                    # 限制历史长度以提高性能
                    session_history = session.history[-5:] if len(session.history) > 5 else session.history
                    context_info['conversation_history'] = self._format_dialogue_history(session_history)
            except Exception as e:
                self.logger.warning(f"Failed to get session from SessionManager: {e}")

        # 提取上下文信号
        context_info['context_signals'] = self._extract_context_signals(context_info)

        return context_info

    def inject_context_to_query(self, text: str, context: Dict[str, Any]) -> str:
        """
        将上下文信息注入到查询文本中，增强语义理解

        Args:
            text: 原始查询文本
            context: 上下文信息

        Returns:
            注入上下文后的文本
        """
        if not context:
            return text

        # 处理代词消解
        resolved_text = self._resolve_pronouns(text, context)

        # 如果当前话题与上下文相关，增强文本
        current_topic = context.get('current_topic', '')
        if current_topic and self._is_topic_relevant(resolved_text, current_topic):
            # 添加上下文话题信息
            return f"关于{current_topic}，{resolved_text}"

        return resolved_text

    def extract_context_signals(self, query: str, context: Dict[str, Any]) -> Dict[str, float]:
        """
        从查询和上下文中提取上下文信号，用于意图识别

        Args:
            query: 查询文本
            context: 上下文信息

        Returns:
            信号名称到权重的映射
        """
        signals = {}

        # 话题连续性信号
        current_topic = context.get('current_topic', '')
        if current_topic:
            # 检查查询是否与当前话题相关
            if self._calculate_topic_relevance(query, current_topic) > 0.7:
                signals['topic_continuity'] = 1.0
            else:
                signals['topic_continuity'] = 0.3

        # 会话连续性信号
        intent_history = context.get('intent_history', [])
        if intent_history:
            last_intent = intent_history[-1] if intent_history else ''
            if last_intent and self._is_intent_relevant(query, last_intent):
                signals['intent_continuity'] = 0.8

        # 实体相关性信号
        parameters = context.get('parameters', {})
        for param_name, param_value in parameters.items():
            param_str = str(param_value)
            if param_str in query or param_name in query:
                signals[f'entity_{param_name}_relevance'] = 0.9

        return signals

    def _format_dialogue_history(self, session_history: List[Any]) -> List[Dict[str, str]]:
        """
        格式化对话历史

        Args:
            session_history: 原始会话历史

        Returns:
            格式化后的对话历史
        """
        formatted_history = []
        for turn in session_history:
            if isinstance(turn, dict):
                # 如果已经是字典格式
                formatted_history.append({
                    'role': turn.get('role', 'unknown'),
                    'content': turn.get('content', ''),
                    'intent': turn.get('intent', ''),
                    'timestamp': turn.get('timestamp', '')
                })
            else:
                # 尝试从对象中提取信息
                role = getattr(turn, 'role', 'unknown')
                content = getattr(turn, 'content', str(turn)) if hasattr(turn, 'content') else str(turn)
                formatted_history.append({
                    'role': role,
                    'content': content,
                    'intent': getattr(turn, 'intent', ''),
                    'timestamp': getattr(turn, 'timestamp', '')
                })

        return formatted_history

    def _resolve_pronouns(self, text: str, context: Dict[str, Any]) -> str:
        """
        处理代词消解

        Args:
            text: 输入文本
            context: 上下文信息

        Returns:
            消解代词后的文本
        """
        # 常见代词映射
        pronouns = {
            '它': '当前讨论的对象',
            '这': '当前讨论的内容',
            '那': '之前提到的内容',
            '这个': '当前讨论的对象',
            '那个': '之前提到的对象',
            '这些': '当前讨论的内容',
            '那些': '之前提到的内容'
        }

        # 从上下文中提取可能的实体
        entities = context.get('related_entities', [])
        parameters = context.get('parameters', {})

        # 如果有明确实体，优先使用实体替换代词
        for entity in entities:
            if f'它' in text and entity and entity in text:
                # 避免过度替换，只在合适情况下替换
                text = re.sub(r'它(?=.*' + re.escape(entity) + ')', entity, text)
            elif f'这' in text and entity and len(str(entity)) > 1 and str(entity) in text:
                text = re.sub(r'这(?=.*' + re.escape(entity) + ')', entity, text)

        # 替换参数中的值
        for param_name, param_value in parameters.items():
            param_str = str(param_value)
            if param_str and '它' in text and param_str in text:
                text = re.sub(r'它(?=.*' + re.escape(param_str) + ')', param_str, text)

        # 一般性代词替换
        for pronoun, replacement in pronouns.items():
            text = text.replace(pronoun, replacement)

        return text

    def _is_topic_relevant(self, query: str, topic: str) -> bool:
        """
        检查查询是否与话题相关

        Args:
            query: 查询文本
            topic: 话题

        Returns:
            是否相关
        """
        if not topic:
            return False

        # 简单的关键字匹配
        query_lower = query.lower()
        topic_lower = topic.lower()

        # 检查话题是否在查询中
        if topic_lower in query_lower:
            return True

        # 检查查询是否在话题中
        if query_lower in topic_lower:
            return True

        # 检查是否有共同词汇（简单的相似度）
        query_words = set(query_lower.split())
        topic_words = set(topic_lower.split())
        common_words = query_words.intersection(topic_words)

        return len(common_words) > 0

    def _calculate_topic_relevance(self, query: str, topic: str) -> float:
        """
        计算查询与话题的关联度

        Args:
            query: 查询文本
            topic: 话题

        Returns:
            关联度（0-1）
        """
        if not topic or not query:
            return 0.0

        query_lower = query.lower()
        topic_lower = topic.lower()

        # 完全匹配
        if query_lower == topic_lower:
            return 1.0

        # 包含匹配
        if topic_lower in query_lower or query_lower in topic_lower:
            return 0.8

        # 词汇重叠
        query_words = set(query_lower.split())
        topic_words = set(topic_lower.split())
        if len(query_words) == 0 or len(topic_words) == 0:
            return 0.0

        common_words = query_words.intersection(topic_words)
        overlap_ratio = len(common_words) / max(len(query_words), len(topic_words))

        return min(overlap_ratio, 0.8)

    def _is_intent_relevant(self, query: str, last_intent: str) -> bool:
        """
        检查查询是否与上一个意图相关

        Args:
            query: 查询文本
            last_intent: 上一个意图

        Returns:
            是否相关
        """
        # 检查是否是延续操作（如"继续"、"然后呢"等）
        continuation_words = ['继续', '然后', '接下来', '下一步', '然后呢', '然后呢？', '继续吧', '继续进行']
        if any(word in query for word in continuation_words):
            return True

        # 基于意图类型的相关性
        query_lower = query.lower()
        if last_intent == 'start_debate' and any(word in query_lower for word in ['辩论', '辩', '观点', '讨论']):
            return True
        elif last_intent == 'create_wiki' and any(word in query_lower for word in ['维基', '百科', '词条', '页面', '编辑']):
            return True
        elif last_intent == 'search_papers' and any(word in query_lower for word in ['论文', '搜索', '查找', '资料']):
            return True
        elif last_intent == 'download_paper' and any(word in query_lower for word in ['下载', '论文', '获取', '文件']):
            return True

        return False

    def _extract_context_signals(self, context_info: Dict[str, Any]) -> Dict[str, float]:
        """
        从上下文信息中提取信号

        Args:
            context_info: 上下文信息

        Returns:
            上下文信号
        """
        signals = {}

        # 话题连续性信号
        current_topic = context_info.get('current_topic', '')
        if current_topic:
            signals['topic_continuity'] = 0.9 if current_topic else 0.1

        # 意图连续性信号
        intent_history = context_info.get('intent_history', [])
        if len(intent_history) > 0:
            signals['intent_continuity'] = 0.8
        else:
            signals['intent_continuity'] = 0.2

        # 实体相关性信号
        entity_count = len(context_info.get('related_entities', []))
        signals['entity_relevance'] = min(entity_count * 0.2, 0.8)

        # 参数完整性信号
        param_count = len(context_info.get('parameters', {}))
        signals['param_completeness'] = min(param_count * 0.1, 0.5)

        return signals