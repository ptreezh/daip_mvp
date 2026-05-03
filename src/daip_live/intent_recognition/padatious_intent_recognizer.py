"""
增强的Padatious意图识别器

基于现有意图识别系统，集成Padatious以提升语义理解能力
遵循SOLID原则，确保单一职责、开闭原则和依赖倒置
"""

import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Padatious库导入
try:
    from padatious import IntentContainer
    PADATIOUS_AVAILABLE = True
except ImportError:
    PADATIOUS_AVAILABLE = False
    IntentContainer = None

# 现有系统导入
from daip_live.agent_engine.enhanced_intent_recognizer import Intent, IntentType, EnhancedIntentRecognizer
from daip_live.intent_recognition.contextual_intent_recognizer import ContextualIntent


class PadatiousIntentType(Enum):
    """Padatious意图类型"""
    GENERAL_CHAT = "general_chat"
    SEARCH_REQUEST = "search_request"
    PAPER_DOWNLOAD = "paper_download"
    DEBATE_START = "debate_start"
    WIKI_CREATE = "wiki_create"
    SKILL_EXECUTE = "skill_execute"
    QUESTION_ASK = "question_ask"


@dataclass
class PadatiousResult:
    """Padatious识别结果数据类"""
    name: str
    confidence: float
    entities: Dict[str, str]
    source_text: str


class PadatiousEnhancedIntentRecognizer:
    """
    Padatious增强意图识别器

    遵循SOLID原则：
    - SRP: 专门负责语义意图识别功能
    - OCP: 通过依赖注入可扩展
    - DIP: 依赖抽象而非具体实现
    """

    def __init__(self, base_recognizer: EnhancedIntentRecognizer,
                 context_integrator: Optional['ContextIntegrator'] = None):
        """
        构造函数，使用依赖注入实现控制反转

        Args:
            base_recognizer: 原有意图识别器
            context_integrator: 上下文集成器
        """
        if not PADATIOUS_AVAILABLE:
            raise ImportError(
                "Padatious is not installed. Please install it with 'pip install padatious'")

        self.base_recognizer = base_recognizer
        self.context_integrator = context_integrator
        self.intent_container = IntentContainer()  # Padatious容器

        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 初始化意图训练
        self._initialize_intents()

    def _initialize_intents(self):
        """初始化Padatious意图"""
        # 普通聊天意图
        self._add_intent('general_chat', [
            '你好',
            'hello',
            'hi',
            '你好吗',
            '怎么样',
            '最近怎么样',
            '谢谢',
            '谢谢你的帮助',
            '再见',
            '拜拜',
            '晚上好',
            '早上好',
            '下午好'
        ])

        # 搜索/论文请求意图
        self._add_intent('search_request', [
            '搜索[query:query]',
            '查找[query:query]',
            '找[query:query]',
            '帮我找[query:query]',
            '搜索论文[query:query]',
            '查找论文[query:query]',
            '找论文[query:query]'
        ])

        # 论文下载意图
        self._add_intent('paper_download', [
            '下载论文[query:query]',
            '下载[query:query]',
            '获取论文[query:query]',
            '下载arxiv[query:query]',
            '下载paper[query:query]'
        ])

        # 辩论意图
        self._add_intent('debate_start', [
            '辩论[topic:topic]',
            '开始辩论[topic:topic]',
            '发起辩论[topic:topic]',
            '让我们辩论[topic:topic]',
            '多模型辩论[topic:topic]'
        ])

        # Wiki创建意图
        self._add_intent('wiki_create', [
            '创建维基[title:title]',
            '新建维基[title:title]',
            '写维基[title:title]',
            '创建百科[title:title]',
            '新建百科[title:title]'
        ])

        # 技能执行意图
        self._add_intent('skill_execute', [
            '执行[skill:skill_type]技能',
            '运行[skill:skill_type]技能',
            '使用[skill:skill_type]技能',
            '帮我[task:task]',
            '请帮我[task:task]',
            '帮我分析[content:content]',
            '帮我处理[content:content]'
        ])

        # 问题意图
        self._add_intent('question_ask', [
            '什么是[concept:concept]',
            '如何[task:task]',
            '为什么[reason:reason]',
            '[question:question]?',
            '怎么[task:task]'
        ])

        # 训练意图
        try:
            self.intent_container.train()
            self.logger.info("Padatious intents trained successfully")
        except Exception as e:
            self.logger.error(f"Failed to train Padatious intents: {e}")

    def _add_intent(self, name: str, examples: list):
        """添加意图示例"""
        for example in examples:
            try:
                self.intent_container.add_intent(name, [example])
            except Exception as e:
                self.logger.warning(f"Could not add intent {name} with example '{example}': {e}")

    def recognize_intent(self, text: str, session_id: str = "default") -> Optional[Union[Intent, ContextualIntent]]:
        """
        识别用户意图，遵循现有接口但扩展功能

        Args:
            text: 用户输入文本
            session_id: 会话ID用于上下文获取

        Returns:
            意图对象或上下文意图对象
        """
        if not text.strip():
            return None

        # 从现有上下文管理器获取上下文信息（如果提供了context_integrator）
        context = {}
        if self.context_integrator:
            context = self.context_integrator.get_context_for_intent_recognition(session_id)

        # 执行Padatious语义识别
        padatious_result = self._recognize_with_padatious(text, context)

        # 执行原有意图识别
        original_result = self.base_recognizer.recognize_intent(text, session_id)

        # 融合两个结果
        return self._fuse_results(padatious_result, original_result, context)

    def _recognize_with_padatious(self, text: str, context: Dict[str, Any]) -> Optional[PadatiousResult]:
        """
        使用Padatious进行语义意图识别

        Args:
            text: 输入文本
            context: 上下文信息

        Returns:
            识别到的意图或None
        """
        if not text.strip():
            return None

        try:
            # 将上下文信息注入到查询中，增强语义理解
            enriched_text = text
            if context and self.context_integrator:
                enriched_text = self.context_integrator.inject_context_to_query(text, context)

            # 使用Padatious进行意图识别
            result = self.intent_container.calc_intent(enriched_text)

            if result and hasattr(result, 'conf') and result.conf > 0.5:  # 置信度阈值
                # 将Padatious结果转换为系统标准格式
                return self._convert_padatious_result(result, text, context)
        except Exception as e:
            self.logger.error(f"Padatious recognition failed: {e}")

        return None

    def _convert_padatious_result(self, padatious_result, original_text: str,
                                context: Dict[str, Any]) -> PadatiousResult:
        """
        将Padatious结果转换为系统标准格式

        Args:
            padatious_result: Padatious识别结果
            original_text: 原始输入文本
            context: 上下文信息

        Returns:
            系统标准结果对象
        """
        # 根据Padatious识别的意图名称映射到系统意图
        intent_name = self._map_padatious_intent_to_system(padatious_result.name)

        # 提取实体信息并转换为系统格式
        entities = getattr(padatious_result, 'entities', {})

        return PadatiousResult(
            name=intent_name,
            confidence=padatious_result.conf,
            entities=entities,
            source_text=original_text
        )

    def _map_padatious_intent_to_system(self, padatious_intent: str) -> str:
        """
        将Padatious意图名称映射到系统意图名称

        Args:
            padatious_intent: Padatious意图名称

        Returns:
            系统意图名称
        """
        mapping = {
            'general_chat': 'chat',
            'search_request': 'search_papers',
            'paper_download': 'download_paper',
            'debate_start': 'start_debate',
            'wiki_create': 'create_wiki',
            'skill_execute': 'execute_skill',
            'question_ask': 'question'
        }

        return mapping.get(padatious_intent, padatious_intent)

    def _fuse_results(self, padatious_result: Optional[PadatiousResult],
                     original_result: Optional[Union[Intent, ContextualIntent]],
                     context: Dict[str, Any]) -> Optional[Union[Intent, ContextualIntent]]:
        """
        融合Padatious和原有意图识别结果

        Args:
            padatious_result: Padatious识别结果
            original_result: 原有意图识别结果
            context: 上下文信息

        Returns:
            融合后的意图结果
        """
        if not padatious_result:
            # 如果Padatious没有结果，返回原有意图
            return self._adjust_result_with_context(original_result, context)

        if not original_result:
            # 如果原有意图识别没有结果，转换Padatious结果并返回
            return self._convert_padatious_to_system_intent(padatious_result, context)

        # 两个都有结果，需要融合
        return self._perform_intent_fusion(padatious_result, original_result, context)

    def _adjust_result_with_context(self, result: Optional[Union[Intent, ContextualIntent]],
                                   context: Dict[str, Any]) -> Optional[Union[Intent, ContextualIntent]]:
        """使用上下文调整意图结果"""
        if result and hasattr(result, 'confidence'):
            # 使用上下文信号调整置信度
            context_signals = context.get('context_signals', {})
            base_confidence = result.confidence

            # 应用上下文信号调整
            for signal_name, signal_weight in context_signals.items():
                if signal_name == 'topic_continuity' and signal_weight > 0.7:
                    # 话题连续性高，增加置信度
                    base_confidence = min(base_confidence + 0.1, 1.0)
                elif signal_name == 'intent_continuity' and signal_weight > 0.7:
                    # 意图连续性高，增加置信度
                    base_confidence = min(base_confidence + 0.05, 1.0)

            result.confidence = base_confidence

        return result

    def _convert_padatious_to_system_intent(self, padatious_result: PadatiousResult,
                                          context: Dict[str, Any]) -> Intent:
        """将Padatious结果转换为系统意图"""
        # 提取参数
        parameters = padatious_result.entities.copy() if padatious_result.entities else {}

        # 根据意图类型创建不同参数
        if padatious_result.name == 'chat':
            parameters['chat_content'] = padatious_result.source_text
        elif padatious_result.name == 'search_papers':
            query = parameters.get('query', padatious_result.source_text)
            parameters['query'] = query
        elif padatious_result.name == 'start_debate':
            topic = parameters.get('topic', padatious_result.source_text)
            parameters['topic'] = topic
        elif padatious_result.name == 'create_wiki':
            title = parameters.get('title', padatious_result.source_text)
            parameters['title'] = title
        elif padatious_result.name == 'execute_skill':
            content = parameters.get('content', parameters.get('task', padatious_result.source_text))
            parameters['content'] = content

        # 确定意图类型
        intent_type = IntentType.CHAT
        if padatious_result.name in ['search_papers', 'download_paper', 'start_debate', 'create_wiki', 'execute_skill']:
            intent_type = IntentType.WORKFLOW
        elif padatious_result.name == 'question':
            intent_type = IntentType.QUESTION

        return Intent(
            name=padatious_result.name,
            confidence=padatious_result.confidence,
            parameters=parameters,
            tool_name=self._get_tool_for_intent(padatious_result.name),
            description=f"Padatious识别的{padatious_result.name}意图",
            intent_type=intent_type,
            requires_confidence_check=False
        )

    def _get_tool_for_intent(self, intent_name: str) -> Optional[str]:
        """获取意图对应的工具"""
        tool_mapping = {
            'chat': None,
            'question': None,
            'search_papers': 'search_academic_papers',
            'download_paper': 'download_paper',
            'start_debate': 'debate',
            'create_wiki': 'wiki',
            'execute_skill': 'skill',
            'knowledge_search': 'knowledge'
        }
        return tool_mapping.get(intent_name)

    def _perform_intent_fusion(self, padatious_result: PadatiousResult,
                             original_result: Union[Intent, ContextualIntent],
                             context: Dict[str, Any]) -> Union[Intent, ContextualIntent]:
        """
        执行意图融合逻辑
        """
        # 获取上下文信号
        context_signals = context.get('context_signals', {})

        # 计算融合后的置信度
        fused_confidence = self._calculate_fused_confidence(
            padatious_result.confidence,
            original_result.confidence if hasattr(original_result, 'confidence') else 0.5,
            context_signals
        )

        # 选择主要意图（基于置信度和上下文相关性）
        if fused_confidence > 0.6:  # 使用融合后置信度作为判断标准
            # 基于上下文选择更好的意图
            if self._should_prefer_padatious(padatious_result, original_result, context):
                # 使用Padatious结果，但结合原有意图的参数
                final_parameters = {**getattr(original_result, 'parameters', {}),
                                  **padatious_result.entities}
                final_intent = Intent(
                    name=padatious_result.name,
                    confidence=fused_confidence,
                    parameters=final_parameters,
                    tool_name=getattr(original_result, 'tool_name', self._get_tool_for_intent(padatious_result.name)),
                    description=getattr(original_result, 'description', f"Fused intent: {padatious_result.name}"),
                    intent_type=getattr(original_result, 'intent_type', IntentType.CHAT),
                    requires_confidence_check=getattr(original_result, 'requires_confidence_check', False)
                )
            else:
                # 使用原有意图结果，但结合Padatious的语义理解
                final_parameters = {**getattr(original_result, 'parameters', {}),
                                  **padatious_result.entities}
                final_intent = Intent(
                    name=original_result.name,
                    confidence=fused_confidence,
                    parameters=final_parameters,
                    tool_name=getattr(original_result, 'tool_name'),
                    description=getattr(original_result, 'description', ""),
                    intent_type=getattr(original_result, 'intent_type', IntentType.CHAT),
                    requires_confidence_check=getattr(original_result, 'requires_confidence_check', False)
                )
        else:
            # 置信度太低，返回原有意图以保证稳定性
            final_intent = original_result
            if hasattr(final_intent, 'confidence'):
                final_intent.confidence = fused_confidence

        return final_intent

    def _calculate_fused_confidence(self, padatious_conf: float, original_conf: float,
                                  context_signals: Dict[str, float]) -> float:
        """
        基于上下文信号计算融合置信度
        """
        # 基础融合：加权平均
        # 给Padatious语义理解稍高权重，因为它在上下文理解方面更好
        base_confidence = (padatious_conf * 0.6 + original_conf * 0.4)

        # 应用上下文信号调整
        for signal_name, signal_weight in context_signals.items():
            if signal_name == 'topic_continuity':
                # 话题连续性高，增加置信度
                base_confidence = min(base_confidence + 0.1 * signal_weight, 1.0)
            elif signal_name == 'intent_continuity':
                # 意图连续性高，增加置信度
                base_confidence = min(base_confidence + 0.05 * signal_weight, 1.0)

        return base_confidence

    def _should_prefer_padatious(self, padatious_result: PadatiousResult,
                               original_result: Union[Intent, ContextualIntent],
                               context: Dict[str, Any]) -> bool:
        """
        判断是否应该优先选择Padatious结果
        """
        # 如果Padatious置信度明显更高，优先选择
        if padatious_result.confidence > original_result.confidence + 0.2:
            return True

        # 检查是否涉及论文意图但上下文是非学术话题
        if (padatious_result.name == 'download_paper' or original_result.name == 'download_paper'):
            # 检查上下文话题
            current_topic = context.get('current_topic', '').lower()
            non_academic_context = any(keyword in current_topic for keyword in
                                     ['你好', 'hi', 'hello', '谢谢', '帮助', '助手', '聊天', '闲聊', '随便', '问题', '为什么', '啥', '啊'])

            # 如果是学术意图但在非学术上下文中，优先考虑原有意图
            if non_academic_context and padatious_result.name == 'download_paper':
                return False

        # 如果上下文信号支持Padatious结果，优先选择
        context_signals = context.get('context_signals', {})
        if any('entity' in signal and signal.endswith('_relevance')
               for signal in context_signals.keys()):
            # 如果有实体相关性信号，倾向于使用语义理解更好的Padatious
            return True

        # 默认情况下，如果置信度接近，倾向于使用原有意图以保持稳定性
        return False

    def is_available(self) -> bool:
        """检查Padatious是否可用"""
        return PADATIOUS_AVAILABLE