"""
意图融合器

专门负责融合Padatious和原有意图识别的结果
遵循SOLID原则中的单一职责原则
"""

import logging
from typing import Any, Optional, Union

from daip_live.agent_engine.enhanced_intent_recognizer import Intent, IntentType
from daip_live.intent_recognition.contextual_intent_recognizer import ContextualIntent
from daip_live.intent_recognition.padatious_intent_recognizer import PadatiousResult


class IntentFuser:
    """
    意图融合器

    专门负责融合Padatious和原有意图识别的结果
    遵循SOLID原则：
    - SRP: 仅负责意图融合逻辑
    - OCP: 可扩展融合策略
    """

    def __init__(self):
        """
        定义不同来源意图的权重
        """
        self.intent_weights = {
            "padatious": 0.6,  # Padatious权重，考虑语义理解能力
            "original": 0.4,  # 原有意图识别权重，考虑精确匹配
        }

        self.logger = logging.getLogger(__name__)

    def fuse_intents(
        self,
        padatious_result: Optional[PadatiousResult],
        original_result: Optional[Union[Intent, ContextualIntent]],
        context: dict[str, Any],
    ) -> Optional[Union[Intent, ContextualIntent]]:
        """
        融合两个意图识别结果

        Args:
            padatious_result: Padatious识别结果
            original_result: 原有意图识别结果
            context: 上下文信息

        Returns:
            融合后的意图结果
        """
        if not padatious_result and not original_result:
            return None

        if not padatious_result:
            # 如果Padatious没有结果，返回原有意图并应用上下文调整
            if original_result:
                return self._adjust_confidence_with_context(original_result, context)
            return None

        if not original_result:
            # 如果原有意图识别没有结果，将Padatious结果转换为系统格式
            return self._convert_padatious_to_system_intent(padatious_result, context)

        # 两个都有结果，需要融合
        return self._perform_intent_fusion(padatious_result, original_result, context)

    def _adjust_confidence_with_context(
        self, intent: Union[Intent, ContextualIntent], context: dict[str, Any]
    ) -> Union[Intent, ContextualIntent]:
        """
        使用上下文调整意图置信度

        Args:
            intent: 意图对象
            context: 上下文信息

        Returns:
            调整后的意图对象
        """
        if not context or not hasattr(intent, "confidence"):
            return intent

        # 获取上下文信号
        context_signals = context.get("context_signals", {})

        base_confidence = intent.confidence

        # 应用上下文信号调整
        for signal_name, signal_weight in context_signals.items():
            if signal_name == "topic_continuity" and signal_weight > 0.7:
                # 话题连续性高，增加置信度
                base_confidence = min(base_confidence + 0.1 * signal_weight, 1.0)
            elif signal_name == "intent_continuity" and signal_weight > 0.7:
                # 意图连续性高，增加置信度
                base_confidence = min(base_confidence + 0.05 * signal_weight, 1.0)
            elif signal_name.startswith("entity_") and signal_name.endswith(
                "_relevance"
            ):
                # 实体相关性高，增加置信度
                base_confidence = min(base_confidence + 0.08 * signal_weight, 1.0)

        intent.confidence = base_confidence
        return intent

    def _convert_padatious_to_system_intent(
        self, padatious_result: PadatiousResult, context: dict[str, Any]
    ) -> Intent:
        """
        将Padatious结果转换为系统意图格式

        Args:
            padatious_result: Padatious结果
            context: 上下文信息

        Returns:
            系统意图对象
        """
        # 提取参数
        parameters = (
            padatious_result.entities.copy() if padatious_result.entities else {}
        )

        # 根据意图类型添加特定参数
        intent_type = self._map_intent_type(padatious_result.name)
        tool_name = self._get_tool_for_intent(padatious_result.name)

        # 尝试从上下文中获取额外参数
        context_params = context.get("parameters", {})
        for param_name, param_value in context_params.items():
            if param_name not in parameters:
                parameters[param_name] = param_value

        # 创建系统意图对象
        intent = Intent(
            name=padatious_result.name,
            confidence=padatious_result.confidence,
            parameters=parameters,
            tool_name=tool_name,
            description=f"Padatious识别的{padatious_result.name}意图",
            intent_type=intent_type,
            requires_confidence_check=False,
        )

        # 使用上下文调整置信度
        return self._adjust_confidence_with_context(intent, context)

    def _perform_intent_fusion(
        self,
        padatious_result: PadatiousResult,
        original_result: Union[Intent, ContextualIntent],
        context: dict[str, Any],
    ) -> Union[Intent, ContextualIntent]:
        """
        执行意图融合逻辑
        """
        # 获取上下文信号
        context_signals = context.get("context_signals", {})

        # 计算融合后的置信度
        fused_confidence = self._calculate_fused_confidence(
            padatious_result.confidence,
            original_result.confidence
            if hasattr(original_result, "confidence")
            else 0.5,
            context_signals,
        )

        # 获取最终参数（合并Padatious和原有意图的参数）
        fused_parameters = self._fuse_parameters(
            padatious_result.entities, getattr(original_result, "parameters", {})
        )

        # 根据上下文选择主要意图类型
        final_intent_type = self._select_intent_type(
            padatious_result.name, original_result.intent_type, context
        )

        # 根据置信度和上下文选择最终意图名称
        final_intent_name = self._select_intent_name(
            padatious_result.name, original_result.name, fused_confidence, context
        )

        # 确定最终工具名称
        final_tool_name = self._get_tool_for_intent(final_intent_name)

        # 创建融合后的意图
        final_intent = Intent(
            name=final_intent_name,
            confidence=fused_confidence,
            parameters=fused_parameters,
            tool_name=final_tool_name,
            description=f"Fused intent: {final_intent_name}",
            intent_type=final_intent_type,
            requires_confidence_check=getattr(
                original_result, "requires_confidence_check", False
            ),
        )

        # 处理ContextualIntent的特殊字段
        if isinstance(original_result, ContextualIntent):
            # 保留ContextualIntent的额外信息
            if not isinstance(final_intent, ContextualIntent):
                # 创建ContextualIntent而不是Intent
                final_intent = ContextualIntent(
                    intent=final_intent,
                    conversation_context=original_result.conversation_context,
                    missing_slots=getattr(original_result, "missing_slots", []),
                    filled_slots=getattr(original_result, "filled_slots", {}),
                    inferred_params=getattr(original_result, "inferred_params", {}),
                    clarification_needed=getattr(
                        original_result, "clarification_needed", False
                    ),
                    clarification_message=getattr(
                        original_result, "clarification_message", ""
                    ),
                    next_step=getattr(original_result, "next_step", ""),
                    confidence_boost=getattr(original_result, "confidence_boost", 0.0),
                )

        return final_intent

    def _calculate_fused_confidence(
        self,
        padatious_conf: float,
        original_conf: float,
        context_signals: dict[str, float],
    ) -> float:
        """
        基于上下文信号计算融合置信度
        """
        # 基础融合：加权平均，考虑上下文增强
        base_confidence = (
            padatious_conf * self.intent_weights["padatious"]
            + original_conf * self.intent_weights["original"]
        )

        # 应用上下文信号调整
        for signal_name, signal_weight in context_signals.items():
            if signal_name == "topic_continuity":
                # 话题连续性高，增加置信度
                base_confidence = min(base_confidence + 0.1 * signal_weight, 1.0)
            elif signal_name == "intent_continuity":
                # 意图连续性高，增加置信度
                base_confidence = min(base_confidence + 0.05 * signal_weight, 1.0)
            elif signal_name.startswith("entity_") and signal_name.endswith(
                "_relevance"
            ):
                # 实体相关性高，增加置信度
                base_confidence = min(base_confidence + 0.08 * signal_weight, 1.0)

        return base_confidence

    def _fuse_parameters(
        self, padatious_params: dict[str, str], original_params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        融合并参数
        """
        fused_params = original_params.copy() if original_params else {}

        # 合并Padatious参数，但不覆盖原有意图的参数
        for param_name, param_value in padatious_params.items():
            if param_name not in fused_params:
                fused_params[param_name] = param_value
            else:
                # 如果参数已存在，可以根据置信度或其他逻辑决定保留哪个
                # 这里我们保留原有意图的参数，因为可能更精确
                pass

        return fused_params

    def _select_intent_type(
        self,
        padatious_intent: str,
        original_intent_type: IntentType,
        context: dict[str, Any],
    ) -> IntentType:
        """
        根据上下文选择意图类型
        """
        # 默认使用原有意图类型
        selected_type = original_intent_type

        # 但如果上下文表明需要更改为其他类型
        if (
            padatious_intent in ["general_chat", "question_ask"]
            and "chat" in original_intent_type.name.lower()
        ):
            selected_type = IntentType.CHAT
        elif (
            padatious_intent in ["search_request", "paper_download"]
            and "workflow" not in original_intent_type.name.lower()
        ):
            selected_type = IntentType.WORKFLOW
        elif (
            padatious_intent == "question_ask"
            and "question" not in original_intent_type.name.lower()
        ):
            selected_type = IntentType.QUESTION

        return selected_type

    def _select_intent_name(
        self,
        padatious_intent: str,
        original_intent: str,
        fused_confidence: float,
        context: dict[str, Any],
    ) -> str:
        """
        根据置信度和上下文选择最终意图名称
        """
        # 检查上下文中的非学术话题，避免将普通对话误识别为论文相关意图
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
                "啥",
                "啊",
            ]
        )

        # 如果是论文相关意图但在非学术上下文中，则优先选择原始意图
        if (
            padatious_intent in ["paper_download", "search_request"]
            and non_academic_context
        ):
            return original_intent

        # 如果Padatious置信度明显更高，选择Padatious意图
        if padatious_intent != original_intent:
            # 检查是否是误识别
            is_likely_misrecognition = self._is_likely_misrecognition(
                padatious_intent, context
            )
            if is_likely_misrecognition:
                return original_intent
            else:
                # 在置信度显著更高时选择Padatious意图
                padatious_conf = context.get("padatious_result", {}).get(
                    "confidence", 0
                )
                original_conf = context.get("original_result", {}).get("confidence", 0)
                if padatious_conf > original_conf + 0.2:
                    return padatious_intent

        # 默认返回原始意图以保持稳定性
        return original_intent

    def _is_likely_misrecognition(
        self, intent_name: str, context: dict[str, Any]
    ) -> bool:
        """
        检查是否可能是误识别，特别是将普通对话误识别为论文意图
        """
        if intent_name in ["download_paper", "search_papers"]:
            # 检查上下文是否为非学术话题
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
                    "啥",
                    "啊",
                ]
            )

            # 检查是否在闲聊场景
            conversation_history = context.get("conversation_history", [])
            if non_academic_context or not conversation_history:
                return True

        return False

    def _map_intent_type(self, padatious_intent: str) -> IntentType:
        """
        将Padatious意图映射到IntentType
        """
        if padatious_intent in ["general_chat"]:
            return IntentType.CHAT
        elif padatious_intent in ["question_ask"]:
            return IntentType.QUESTION
        elif padatious_intent in [
            "search_request",
            "paper_download",
            "debate_start",
            "wiki_create",
            "skill_execute",
        ]:
            return IntentType.WORKFLOW
        else:
            return IntentType.CHAT

    def _get_tool_for_intent(self, intent_name: str) -> Optional[str]:
        """
        获取意图对应的工具
        """
        tool_mapping = {
            "chat": None,
            "question": None,
            "search_papers": "search_academic_papers",
            "download_paper": "download_paper",
            "start_debate": "debate",
            "create_wiki": "wiki",
            "execute_skill": "skill",
            "knowledge_search": "knowledge",
            "general_chat": None,
            "search_request": "search_academic_papers",
            "paper_download": "download_paper",
            "debate_start": "debate",
            "wiki_create": "wiki",
            "skill_execute": "skill",
            "question_ask": None,
        }
        return tool_mapping.get(intent_name)
