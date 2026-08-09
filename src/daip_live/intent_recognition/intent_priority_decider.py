"""
意图优先级决策器

根据上下文相关性、会话连续性、用户历史偏好等确定意图优先级
遵循SOLID原则中的单一职责原则
"""

import logging
from typing import Any, Union

from daip_live.agent_engine.enhanced_intent_recognizer import Intent
from daip_live.intent_recognition.contextual_intent_recognizer import ContextualIntent


class IntentPriorityDecider:
    """
    意图优先级决策器

    根据上下文相关性、会话连续性、用户历史偏好等确定意图优先级
    遵循SOLID原则：
    - SRP: 仅负责意图优先级决策
    - OCP: 可扩展更多决策策略
    """

    def __init__(self):
        """
        初始化意图优先级决策器
        """
        self.logger = logging.getLogger(__name__)

        # 定义意图优先级规则
        self.priority_rules = {
            # 高优先级：明确的命令意图
            "execute_skill": 100,
            "start_debate": 95,
            "create_wiki": 90,
            "search_papers": 85,
            "download_paper": 80,
            # 中优先级：查询和问题
            "question": 70,
            "knowledge_search": 65,
            # 低优先级：一般聊天
            "chat": 50,
        }

        # 定义上下文匹配权重
        self.context_weights = {
            "topic_continuity": 0.3,  # 话题连续性
            "intent_continuity": 0.25,  # 意图连续性
            "entity_relevance": 0.2,  # 实体相关性
            "time_proximity": 0.15,  # 时间接近性
            "user_preference": 0.1,  # 用户偏好
        }

    def decide_intent_priority(
        self,
        intents: list[Union[Intent, ContextualIntent]],
        context: dict[str, Any],
        user_input: str = "",
    ) -> list[Union[Intent, ContextualIntent]]:
        """
        根据多种因素决定意图优先级

        Args:
            intents: 意图列表
            context: 上下文信息
            user_input: 用户输入文本

        Returns:
            按优先级排序的意图列表
        """
        if not intents:
            return intents

        if len(intents) <= 1:
            return intents

        # 计算每个意图的综合得分
        scored_intents = []
        for intent in intents:
            score = self._calculate_comprehensive_score(intent, context, user_input)
            scored_intents.append((intent, score))

        # 按得分降序排序
        sorted_scored = sorted(scored_intents, key=lambda x: x[1], reverse=True)

        # 提取排序后的意图列表
        sorted_intents = [intent for intent, score in sorted_scored]

        # 记录排序结果
        intent_names = [intent.name for intent in sorted_intents]
        self.logger.debug(f"Intent priority ranking: {intent_names}")

        return sorted_intents

    def _calculate_comprehensive_score(
        self,
        intent: Union[Intent, ContextualIntent],
        context: dict[str, Any],
        user_input: str,
    ) -> float:
        """
        计算意图的综合得分

        Args:
            intent: 意图对象
            context: 上下文信息
            user_input: 用户输入

        Returns:
            综合得分
        """
        # 基础优先级得分
        base_priority = self._get_base_priority(intent.name)

        # 上下文相关性得分
        context_relevance = self._calculate_context_relevance(
            intent, context, user_input
        )

        # 意图置信度得分
        confidence_score = getattr(intent, "confidence", 0.5)

        # 综合计算
        comprehensive_score = (
            base_priority * 0.3  # 基础优先级占30%
            + context_relevance * 0.4  # 上下文相关性占40%
            + confidence_score * 0.3  # 置信度占30%
        )

        return comprehensive_score

    def _get_base_priority(self, intent_name: str) -> float:
        """
        获取意图的基础优先级

        Args:
            intent_name: 意图名称

        Returns:
            基础优先级得分 (0-1)
        """
        priority = self.priority_rules.get(intent_name, 50)  # 默认50分
        return min(priority / 100.0, 1.0)  # 转换为0-1范围

    def _calculate_context_relevance(
        self,
        intent: Union[Intent, ContextualIntent],
        context: dict[str, Any],
        user_input: str,
    ) -> float:
        """
        计算意图与上下文的相关性得分

        Args:
            intent: 意图对象
            context: 上下文信息
            user_input: 用户输入

        Returns:
            上下文相关性得分 (0-1)
        """
        if not context:
            return 0.5  # 无上下文时返回中性得分

        relevance_score = 0.0
        total_weight = sum(self.context_weights.values())

        # 1. 话题连续性
        topic_continuity_score = self._calculate_topic_continuity_score(
            intent, context, user_input
        )
        relevance_score += (
            topic_continuity_score * self.context_weights["topic_continuity"]
        )

        # 2. 意图连续性
        intent_continuity_score = self._calculate_intent_continuity_score(
            intent, context
        )
        relevance_score += (
            intent_continuity_score * self.context_weights["intent_continuity"]
        )

        # 3. 实体相关性
        entity_relevance_score = self._calculate_entity_relevance_score(intent, context)
        relevance_score += (
            entity_relevance_score * self.context_weights["entity_relevance"]
        )

        # 4. 时间接近性
        time_proximity_score = self._calculate_time_proximity_score(context)
        relevance_score += time_proximity_score * self.context_weights["time_proximity"]

        # 5. 用户偏好（如果有）
        user_preference_score = self._calculate_user_preference_score(intent, context)
        relevance_score += (
            user_preference_score * self.context_weights["user_preference"]
        )

        # 标准化得分到0-1范围
        return relevance_score / total_weight if total_weight > 0 else 0.5

    def _calculate_topic_continuity_score(
        self,
        intent: Union[Intent, ContextualIntent],
        context: dict[str, Any],
        user_input: str,
    ) -> float:
        """
        计算话题连续性得分

        Args:
            intent: 意图对象
            context: 上下文信息
            user_input: 用户输入

        Returns:
            话题连续性得分 (0-1)
        """
        current_topic = context.get("current_topic", "").lower()
        if not current_topic:
            return 0.5  # 无当前话题时返回中性得分

        user_input_lower = user_input.lower()

        # 如果用户输入包含当前话题关键词，得分较高
        if current_topic in user_input_lower:
            return 1.0

        # 如果意图与当前话题相关，得分中等偏上
        topic_related_intents = [
            "search_papers",
            "download_paper",
            "start_debate",
            "create_wiki",
        ]
        if intent.name in topic_related_intents and current_topic:
            return 0.7

        # 检查用户输入是否与话题有语义相关性
        topic_words = set(current_topic.split())
        input_words = set(user_input_lower.split())
        common_words = topic_words.intersection(input_words)

        if common_words:
            overlap_ratio = len(common_words) / max(len(topic_words), 1)
            return min(0.6 + overlap_ratio * 0.4, 1.0)

        return 0.3  # 不相关得分较低

    def _calculate_intent_continuity_score(
        self, intent: Union[Intent, ContextualIntent], context: dict[str, Any]
    ) -> float:
        """
        计算意图连续性得分

        Args:
            intent: 意图对象
            context: 上下文信息

        Returns:
            意图连续性得分 (0-1)
        """
        intent_history = context.get("intent_history", [])
        if not intent_history:
            return 0.5  # 无历史时返回中性得分

        last_intent = intent_history[-1]

        # 如果当前意图与上一个意图相同，得分较高
        if intent.name == last_intent:
            return 1.0

        # 如果是连续操作意图（如继续、然后等）
        continuation_intents = ["chat", "question"]  # 这些意图可能延续之前的会话
        if intent.name in continuation_intents:
            return 0.8

        # 检查意图类别连续性
        intent_categories = {
            "search": ["search_papers", "download_paper", "knowledge_search"],
            "creation": ["create_wiki", "execute_skill"],
            "discussion": ["start_debate", "chat", "question"],
        }

        current_category = None
        last_category = None

        for category, intent_list in intent_categories.items():
            if intent.name in intent_list:
                current_category = category
            if last_intent in intent_list:
                last_category = category

        if current_category and last_category and current_category == last_category:
            return 0.7

        return 0.3  # 不连续得分较低

    def _calculate_entity_relevance_score(
        self, intent: Union[Intent, ContextualIntent], context: dict[str, Any]
    ) -> float:
        """
        计算实体相关性得分

        Args:
            intent: 意图对象
            context: 上下文信息

        Returns:
            实体相关性得分 (0-1)
        """
        parameters = context.get("parameters", {})
        related_entities = context.get("related_entities", [])

        if not parameters and not related_entities:
            return 0.5  # 无实体时返回中性得分

        # 检查意图参数是否与上下文实体匹配
        intent_params = getattr(intent, "parameters", {})

        matches = 0
        total_params = len(intent_params)

        for param_name, param_value in intent_params.items():
            param_str = str(param_value).lower()

            # 检查参数值是否在上下文参数中
            for ctx_param_name, ctx_param_value in parameters.items():
                if param_str in str(ctx_param_value).lower():
                    matches += 1
                    break

            # 检查参数值是否在相关实体中
            for entity in related_entities:
                if param_str in entity.lower():
                    matches += 1
                    break

        if total_params > 0:
            entity_match_ratio = matches / total_params
            return min(0.5 + entity_match_ratio * 0.5, 1.0)

        return 0.5  # 无参数时返回中性得分

    def _calculate_time_proximity_score(self, context: dict[str, Any]) -> float:
        """
        计算时间接近性得分

        Args:
            context: 上下文信息

        Returns:
            时间接近性得分 (0-1)
        """
        last_accessed = context.get("last_accessed", None)
        if not last_accessed:
            return 0.5  # 无时间信息时返回中性得分

        # 这里可以实现基于时间间隔的逻辑
        # 暂时返回中性得分，因为需要解析ISO格式的时间戳
        return 0.5

    def _calculate_user_preference_score(
        self, intent: Union[Intent, ContextualIntent], context: dict[str, Any]
    ) -> float:
        """
        计算用户偏好得分

        Args:
            intent: 意图对象
            context: 上下文信息

        Returns:
            用户偏好得分 (0-1)
        """
        # 检查用户偏好设置
        preferences = context.get("preferences", {})

        if not preferences:
            return 0.5  # 无偏好时返回中性得分

        # 检查特定意图的偏好
        intent_preference = preferences.get(intent.name, {}).get(
            "preference_score", 0.5
        )
        return intent_preference

    def adjust_priority_for_misrecognition_protection(
        self, intents: list[Union[Intent, ContextualIntent]], context: dict[str, Any]
    ) -> list[Union[Intent, ContextualIntent]]:
        """
        为防止误识别调整意图优先级，特别是降低论文意图在非学术上下文中的优先级

        Args:
            intents: 意图列表
            context: 上下文信息

        Returns:
            调整后的意图列表
        """
        if not intents:
            return intents

        current_topic = context.get("current_topic", "").lower()
        non_academic_context = any(
            keyword in current_topic
            for keyword in [
                "你好",
                "hi",
                "hello",
                "谢谢",
                "帮助",
                "助手",
                "聊天",
                "闲聊",
                "随便",
                "问题",
                "为什么",
                "为啥",
                "啥",
                "啊",
            ]
        )

        # 如果在非学术上下文中，降低论文相关意图的优先级
        if non_academic_context:
            adjusted_intents = []
            for intent in intents:
                if intent.name in ["search_papers", "download_paper"]:
                    # 创建一个新的意图对象，降低置信度
                    adjusted_intent = self._create_adjusted_intent(intent, factor=0.5)
                    adjusted_intents.append(adjusted_intent)
                    self.logger.debug(
                        f"Reduced priority for paper intent '{intent.name}' in non-academic context"  # noqa: E501
                    )
                else:
                    adjusted_intents.append(intent)
            return adjusted_intents

        return intents

    def _create_adjusted_intent(
        self, intent: Union[Intent, ContextualIntent], factor: float
    ) -> Union[Intent, ContextualIntent]:
        """
        创建调整后的意图对象

        Args:
            intent: 原始意图对象
            factor: 调整因子

        Returns:
            调整后的意图对象
        """
        # 降低置信度
        adjusted_confidence = max(intent.confidence * factor, 0.1)  # 确保不低于0.1

        # 根据意图类型创建对应的调整后意图
        if isinstance(intent, ContextualIntent):
            adjusted_intent = ContextualIntent(
                intent=Intent(
                    name=intent.intent.name,
                    confidence=adjusted_confidence,
                    parameters=intent.intent.parameters,
                    tool_name=intent.intent.tool_name,
                    description=intent.intent.description,
                    intent_type=intent.intent.intent_type,
                    requires_confidence_check=intent.intent.requires_confidence_check,
                ),
                conversation_context=intent.conversation_context,
                missing_slots=intent.missing_slots,
                filled_slots=intent.filled_slots,
                inferred_params=intent.inferred_params,
                clarification_needed=intent.clarification_needed,
                clarification_message=intent.clarification_message,
                next_step=intent.next_step,
                confidence_boost=intent.confidence_boost,
            )
        else:
            adjusted_intent = Intent(
                name=intent.name,
                confidence=adjusted_confidence,
                parameters=intent.parameters,
                tool_name=intent.tool_name,
                description=intent.description,
                intent_type=intent.intent_type,
                requires_confidence_check=intent.requires_confidence_check,
            )

        return adjusted_intent

    def ensure_chat_priority_in_greeting_context(
        self, intents: list[Union[Intent, ContextualIntent]], user_input: str
    ) -> list[Union[Intent, ContextualIntent]]:
        """
        在问候语境中确保聊天意图的优先级

        Args:
            intents: 意图列表
            user_input: 用户输入

        Returns:
            调整后的意图列表
        """
        if not intents or not user_input:
            return intents

        # 检查是否为问候语
        greeting_indicators = [
            "你好",
            "hello",
            "hi",
            "您好",
            "谢谢",
            "再见",
            "拜拜",
            "嗯",
            "哦",
            "啊",
            "哈",
        ]
        is_greeting = any(
            indicator in user_input.lower() for indicator in greeting_indicators
        )

        if is_greeting:
            # 将聊天意图移到前面
            chat_intents = [intent for intent in intents if intent.name == "chat"]
            other_intents = [intent for intent in intents if intent.name != "chat"]

            # 确保聊天意图在前
            prioritized_intents = chat_intents + other_intents
            return prioritized_intents

        return intents

    def get_priority_analysis(
        self,
        intents: list[Union[Intent, ContextualIntent]],
        context: dict[str, Any],
        user_input: str = "",
    ) -> dict[str, Any]:
        """
        获取优先级分析详情

        Args:
            intents: 意图列表
            context: 上下文信息
            user_input: 用户输入

        Returns:
            优先级分析详情
        """
        analysis = {
            "original_order": [intent.name for intent in intents],
            "detailed_scores": [],
        }

        for intent in intents:
            score = self._calculate_comprehensive_score(intent, context, user_input)
            base_priority = self._get_base_priority(intent.name)
            context_relevance = self._calculate_context_relevance(
                intent, context, user_input
            )
            confidence_score = getattr(intent, "confidence", 0.5)

            analysis["detailed_scores"].append(
                {
                    "intent_name": intent.name,
                    "comprehensive_score": score,
                    "base_priority": base_priority,
                    "context_relevance": context_relevance,
                    "confidence_score": confidence_score,
                }
            )

        # 获取排序后的结果
        sorted_intents = self.decide_intent_priority(intents, context, user_input)
        analysis["final_order"] = [intent.name for intent in sorted_intents]

        return analysis
