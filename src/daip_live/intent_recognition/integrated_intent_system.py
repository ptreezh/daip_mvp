"""
集成的意图识别系统

将上下文感知意图识别器无缝集成到现有DAIP系统中
提供统一的入口点和向后兼容性
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict

try:
    from .contextual_intent_recognizer import (
        ContextualIntent, ContextualIntentRecognizer, ConversationTurn
    )
    from .enhanced_context_manager import EnhancedContextManager
    from .context_manager import ContextManager
    from .session_state import SessionState
except ImportError:
    from daip_live.intent_recognition.contextual_intent_recognizer import (
        ContextualIntent, ContextualIntentRecognizer, ConversationTurn
    )
    from daip_live.intent_recognition.enhanced_context_manager import EnhancedContextManager
    from daip_live.intent_recognition.context_manager import ContextManager
    from daip_live.intent_recognition.session_state import SessionState

# 原有系统组件
from daip_live.agent_engine.enhanced_intent_recognizer import (
    Intent, IntentType, EnhancedIntentRecognizer
)
from daip_live.agent_engine.services.clarification_service import ClarificationService


logger = logging.getLogger(__name__)


class IntegratedIntentSystem:
    """
    集成的意图识别系统

    特性：
    1. 完全向后兼容现有接口
    2. 自动启用上下文感知功能
    3. 智能槽位填充和参数推导
    4. 增强的澄清生成
    5. 详细的调试和监控信息
    """

    def __init__(self, enable_context_aware: bool = True, enable_debug: bool = False):
        """
        初始化集成意图系统

        Args:
            enable_context_aware: 是否启用上下文感知功能
            enable_debug: 是否启用调试模式
        """
        self.enable_context_aware = enable_context_aware
        self.enable_debug = enable_debug

        # 原有组件
        self.base_recognizer = EnhancedIntentRecognizer()
        self.clarification_service = ClarificationService()

        # 增强组件
        if enable_context_aware:
            self.context_manager = EnhancedContextManager()
            self.contextual_recognizer = ContextualIntentRecognizer(self.base_recognizer)
        else:
            self.context_manager = ContextManager()
            self.contextual_recognizer = None

        # 性能统计
        self.recognition_stats = {
            "total_requests": 0,
            "context_aware_hits": 0,
            "slot_filling_successes": 0,
            "clarification_requests": 0,
            "inference_successes": 0
        }

        # 配置
        self.max_conversation_history = 10
        self.confidence_threshold = 0.3
        self.auto_complete_threshold = 0.8

        logger.info(f"IntegratedIntentSystem initialized (context_aware={enable_context_aware})")

    def recognize_intent(self, user_input: str, session_id: str = "default") -> Union[Intent, ContextualIntent]:
        """
        统一的意图识别入口

        Args:
            user_input: 用户输入
            session_id: 会话ID

        Returns:
            Intent 或 ContextualIntent 对象
        """
        self.recognition_stats["total_requests"] += 1

        if self.enable_debug:
            logger.debug(f"Recognizing intent for session {session_id}: '{user_input}'")

        try:
            # 使用上下文感知识别器
            if self.contextual_recognizer:
                contextual_intent = self.contextual_recognizer.recognize_intent(user_input, session_id)

                # 更新统计
                if contextual_intent.filled_slots or contextual_intent.inferred_params:
                    self.recognition_stats["slot_filling_successes"] += 1
                if contextual_intent.clarification_needed:
                    self.recognition_stats["clarification_requests"] += 1
                if contextual_intent.inferred_params:
                    self.recognition_stats["inference_successes"] += 1
                if contextual_intent.confidence_boost > 0:
                    self.recognition_stats["context_aware_hits"] += 1

                # 记录调试信息
                if self.enable_debug:
                    self._log_contextual_intent(contextual_intent, session_id)

                return contextual_intent

            # 回退到基础识别器
            else:
                base_intent = self.base_recognizer.recognize_intent(user_input, session_id)
                if self.enable_debug:
                    self._log_base_intent(base_intent, session_id)
                return base_intent

        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            # 创建错误意图
            return Intent(
                name="error",
                confidence=0.0,
                parameters={"error": str(e), "original_input": user_input},
                description="Intent recognition error",
                intent_type=IntentType.CHAT,
                requires_confidence_check=False
            )

    def start_contextual_task(self, session_id: str, task_type: str,
                             required_params: List[str] = None,
                             initial_params: Dict[str, Any] = None) -> bool:
        """
        开始上下文感知的任务

        Args:
            session_id: 会话ID
            task_type: 任务类型
            required_params: 必需参数列表
            initial_params: 初始参数

        Returns:
            是否成功启动任务
        """
        if not self.enable_context_aware:
            # 回退到基础管理器
            if required_params is None:
                required_params = []
            if initial_params is None:
                initial_params = {}

            context_data = {
                "task_type": task_type,
                "required_params": required_params,
                "filled_params": initial_params
            }
            self.context_manager.set_context(session_id, context_data)

            for param_name, param_value in initial_params.items():
                self.context_manager.add_task_parameter(session_id, param_name, param_value)

            return True

        # 使用增强上下文管理器
        from .enhanced_context_manager import ParameterSource

        # 创建或获取对话上下文
        context = self.context_manager.get_conversation_context(session_id)
        if not context:
            topic = initial_params.get("topic", "") or initial_params.get("title", "") or task_type
            context = self.context_manager.create_conversation_context(session_id, task_type, topic)

        # 设置必需参数
        if required_params is None:
            required_params = []

        # 添加初始参数
        if initial_params:
            for param_name, param_value in initial_params.items():
                self.context_manager.add_parameter_with_source(
                    session_id, param_name, param_value, ParameterSource.USER_INPUT
                )

        # 尝试参数继承
        inherited_params = self.context_manager.inherit_parameters(session_id, task_type, required_params)
        for param_name, param_value in inherited_params.items():
            self.context_manager.add_parameter_with_source(
                session_id, param_name, param_value, ParameterSource.CONTEXT_INHERIT
            )

        # 同步到基础管理器
        context_data = {
            "task_type": task_type,
            "required_params": required_params,
            "filled_params": {**initial_params, **inherited_params}
        }
        self.context_manager.base_manager.set_context(session_id, context_data)

        logger.info(f"Started contextual task: {task_type} for session {session_id}")
        return True

    def is_session_in_task(self, session_id: str) -> bool:
        """检查会话是否在任务中"""
        return self.context_manager.is_in_task(session_id)

    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话上下文"""
        if self.enable_context_aware:
            context = self.context_manager.get_conversation_context(session_id)
            if context:
                return {
                    "session_id": context.session_id,
                    "topic": context.topic,
                    "current_intent": context.current_intent,
                    "intent_history": context.intent_history,
                    "parameters": context.get_filled_parameters(),
                    "status": context.status.value,
                    "related_entities": list(context.related_entities),
                    "conversation_summary": context.conversation_summary
                }

        return self.context_manager.get_context(session_id)

    def clear_session_context(self, session_id: str):
        """清除会话上下文"""
        self.context_manager.clear_context(session_id)
        if self.contextual_recognizer:
            self.contextual_recognizer.clear_session_history(session_id)
        logger.info(f"Cleared context for session {session_id}")

    def get_conversation_history(self, session_id: str) -> List[ConversationTurn]:
        """获取对话历史"""
        if self.contextual_recognizer:
            return self.contextual_recognizer.get_conversation_history(session_id)
        return []

    def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话统计信息"""
        if self.enable_context_aware:
            stats = self.context_manager.get_session_statistics(session_id)
            if stats:
                # 添加系统统计
                stats.update({
                    "system_stats": self.recognition_stats.copy(),
                    "context_aware_enabled": True
                })
                return stats

        return {
            "system_stats": self.recognition_stats.copy(),
            "context_aware_enabled": False
        }

    def generate_clarification_message(self, intent: Union[Intent, ContextualIntent],
                                    session_id: str = "default") -> Optional[str]:
        """
        生成澄清消息

        Args:
            intent: 意图对象
            session_id: 会话ID

        Returns:
            澄清消息或None
        """
        # 如果是上下文增强意图，直接使用其澄清消息
        if isinstance(intent, ContextualIntent) and intent.clarification_needed:
            return intent.clarification_message

        # 对于基础意图，使用原有澄清服务
        if isinstance(intent, Intent) and intent.requires_clarification:
            if intent.clarification_needed:
                if isinstance(intent.clarification_needed, dict):
                    return intent.clarification_needed.get("message", "")
                return str(intent.clarification_needed)

        return None

    def get_next_step_suggestion(self, intent: Union[Intent, ContextualIntent],
                                session_id: str = "default") -> str:
        """
        获取下一步行动建议

        Args:
            intent: 意图对象
            session_id: 会话ID

        Returns:
            下一步行动建议
        """
        if isinstance(intent, ContextualIntent):
            return intent.next_step

        # 对于基础意图，生成基本建议
        if isinstance(intent, Intent):
            if intent.name == "start_debate":
                topic = intent.parameters.get("topic", "未指定主题")
                rounds = intent.parameters.get("rounds", 3)
                return f"准备开始关于'{topic}'的辩论，共{rounds}轮"
            elif intent.name == "create_wiki":
                title = intent.parameters.get("title", "未指定标题")
                return f"准备创建维基页面：{title}"
            elif intent.name == "search_papers":
                query = intent.parameters.get("query", "未指定查询")
                return f"准备搜索论文：{query}"
            elif intent.name == "execute_skill":
                content = intent.parameters.get("content", "未指定内容")
                return f"准备执行技能：{content}"
            else:
                return f"继续处理：{intent.description}"

        return "请提供更具体的指令"

    def is_task_complete(self, session_id: str) -> bool:
        """检查任务是否完成"""
        if not self.context_manager.is_in_task(session_id):
            return False

        # 获取任务上下文
        task_context = self.context_manager.get_context(session_id)
        if not task_context:
            return False

        # 检查是否所有必需参数都已填充
        required_params = task_context.get("required_params", [])
        filled_params = task_context.get("filled_params", {})

        return all(param in filled_params for param in required_params)

    def get_missing_parameters(self, session_id: str) -> List[str]:
        """获取缺失的参数列表"""
        if not self.context_manager.is_in_task(session_id):
            return []

        task_context = self.context_manager.get_context(session_id)
        if not task_context:
            return []

        required_params = task_context.get("required_params", [])
        filled_params = task_context.get("filled_params", {})

        return [param for param in required_params if param not in filled_params]

    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """导出会话数据"""
        data = {
            "session_id": session_id,
            "timestamp": str(self.context_manager.conversation_contexts.get(session_id, {}).get("last_accessed", "")),
            "statistics": self.get_session_statistics(session_id),
            "context": self.get_session_context(session_id),
            "conversation_history": [
                {
                    "user_input": turn.user_input,
                    "intent_name": turn.intent.name if turn.intent else None,
                    "parameters": turn.filled_params,
                    "timestamp": turn.timestamp.isoformat(),
                    "strategy_used": turn.strategy_used.value if turn.strategy_used else None
                }
                for turn in self.get_conversation_history(session_id)
            ]
        }

        return data

    def reset_statistics(self):
        """重置统计信息"""
        self.recognition_stats = {
            "total_requests": 0,
            "context_aware_hits": 0,
            "slot_filling_successes": 0,
            "clarification_requests": 0,
            "inference_successes": 0
        }

    def _log_contextual_intent(self, intent: ContextualIntent, session_id: str):
        """记录上下文意图调试信息"""
        logger.debug(f"Session {session_id} contextual intent result:")
        logger.debug(f"  Intent: {intent.intent.name if intent.intent else 'None'}")
        logger.debug(f"  Base Confidence: {intent.intent.confidence if intent.intent else 0:.3f}")
        logger.debug(f"  Context Boost: {intent.confidence_boost:.3f}")
        logger.debug(f"  Filled Slots: {list(intent.filled_slots.keys())}")
        logger.debug(f"  Missing Slots: {intent.missing_slots}")
        logger.debug(f"  Inferred Params: {list(intent.inferred_params.keys())}")
        logger.debug(f"  Clarification Needed: {intent.clarification_needed}")
        logger.debug(f"  Next Step: {intent.next_step}")

    def _log_base_intent(self, intent: Intent, session_id: str):
        """记录基础意图调试信息"""
        logger.debug(f"Session {session_id} base intent result:")
        logger.debug(f"  Intent: {intent.name}")
        logger.debug(f"  Confidence: {intent.confidence:.3f}")
        logger.debug(f"  Parameters: {list(intent.parameters.keys())}")
        logger.debug(f"  Requires Clarification: {intent.requires_clarification}")

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": "IntegratedIntentSystem",
            "context_aware_enabled": self.enable_context_aware,
            "debug_enabled": self.enable_debug,
            "max_conversation_history": self.max_conversation_history,
            "confidence_threshold": self.confidence_threshold,
            "auto_complete_threshold": self.auto_complete_threshold,
            "statistics": self.recognition_stats.copy(),
            "active_sessions": len(self.context_manager.conversation_contexts) if self.enable_context_aware else 0
        }

    def cleanup_expired_sessions(self):
        """清理过期会话"""
        if self.enable_context_aware:
            self.context_manager.cleanup_expired_contexts()
            logger.debug("Cleaned up expired contexts")

    def health_check(self) -> Dict[str, Any]:
        """系统健康检查"""
        return {
            "status": "healthy",
            "context_aware_working": self.enable_context_aware and self.contextual_recognizer is not None,
            "base_recognizer_working": self.base_recognizer is not None,
            "clarification_service_working": self.clarification_service is not None,
            "active_sessions": len(self.context_manager.conversation_contexts) if self.enable_context_aware else 0,
            "total_requests_processed": self.recognition_stats["total_requests"],
            "context_aware_hit_rate": (
                self.recognition_stats["context_aware_hits"] / max(1, self.recognition_stats["total_requests"])
            ),
            "last_cleanup": str(self.context_manager.conversation_contexts) if self.enable_context_aware else "N/A"
        }