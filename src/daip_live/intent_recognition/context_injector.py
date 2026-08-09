"""
上下文注入器

将上下文信息注入到Padatious意图识别过程中
确保上下文信息与现有ContextManager保持一致
遵循SOLID原则中的单一职责原则
"""

import logging
import time
from typing import Any, Optional

from daip_live.intent_recognition.context_integrator import ContextIntegrator


class ContextInjector:
    """
    上下文注入器

    将上下文信息注入到Padatious意图识别过程中
    确保上下文信息与现有ContextManager保持一致
    遵循SOLID原则：
    - SRP: 仅负责上下文注入
    - OCP: 可扩展更多注入策略
    """

    def __init__(self, context_integrator: Optional[ContextIntegrator] = None):
        """
        初始化上下文注入器

        Args:
            context_integrator: 上下文集成器
        """
        self.context_integrator = context_integrator
        self.logger = logging.getLogger(__name__)

        # 性能监控
        self.last_injection_time = 0
        self.injection_count = 0

    def inject_context_to_padatious_query(
        self, text: str, session_id: str = "default"
    ) -> str:
        """
        将上下文信息注入到Padatious查询中

        Args:
            text: 原始查询文本
            session_id: 会话ID

        Returns:
            注入上下文后的查询文本
        """
        start_time = time.time()

        # 获取上下文信息
        context = {}
        if self.context_integrator:
            context = self.context_integrator.get_context_for_intent_recognition(
                session_id
            )

        # 执行上下文注入
        injected_text = self._inject_context(text, context)

        # 性能监控
        injection_time = time.time() - start_time
        self.last_injection_time = injection_time
        self.injection_count += 1

        if injection_time > 0.02:  # 如果注入时间超过20ms，记录警告
            self.logger.warning(
                f"Context injection took {injection_time:.3f}s for session {session_id}"
            )

        self.logger.debug(
            f"Context injected for session {session_id}: '{text}' -> '{injected_text}'"
        )

        return injected_text

    def _inject_context(self, text: str, context: dict[str, Any]) -> str:
        """
        执行上下文注入逻辑

        Args:
            text: 原始文本
            context: 上下文信息

        Returns:
            注入上下文后的文本
        """
        if not context or not text:
            return text

        injected_parts = [text]

        # 1. 注入当前话题上下文
        current_topic = context.get("current_topic", "")
        if current_topic and current_topic.lower() not in text.lower():
            injected_parts.insert(0, f"[话题: {current_topic}]")

        # 2. 注入最近的参数上下文
        parameters = context.get("parameters", {})
        for param_name, param_value in list(parameters.items())[
            -3:
        ]:  # 只使用最近3个参数
            if str(param_value).lower() not in text.lower():
                injected_parts.insert(0, f"[{param_name}: {param_value}]")

        # 3. 注入相关实体上下文
        related_entities = context.get("related_entities", [])
        for entity in related_entities[-2:]:  # 只使用最近2个实体
            if entity.lower() not in text.lower():
                injected_parts.insert(0, f"[实体: {entity}]")

        # 4. 根据意图历史添加上下文标记
        intent_history = context.get("intent_history", [])
        if intent_history:
            last_intent = intent_history[-1]
            injected_parts.append(f"[最近意图: {last_intent}]")

        return " ".join(injected_parts)

    def format_context_for_padatious(self, context: dict[str, Any]) -> str:
        """
        为Padatious格式化上下文信息

        Args:
            context: 上下文信息

        Returns:
            格式化后的上下文字符串
        """
        if not context:
            return ""

        formatted_parts = []

        # 添加话题信息
        current_topic = context.get("current_topic", "")
        if current_topic:
            formatted_parts.append(f"TOPIC: {current_topic}")

        # 添加参数信息
        parameters = context.get("parameters", {})
        if parameters:
            param_strs = [f"{k}={v}" for k, v in parameters.items() if v is not None]
            if param_strs:
                formatted_parts.append(f"PARAMS: {'; '.join(param_strs)}")

        # 添加实体信息
        related_entities = context.get("related_entities", [])
        if related_entities:
            formatted_parts.append(f"ENTITIES: {', '.join(related_entities)}")

        # 添加意图历史
        intent_history = context.get("intent_history", [])
        if intent_history:
            formatted_parts.append(
                f"HISTORY: {' -> '.join(intent_history[-5:])}"
            )  # 最近5个意图

        return " | ".join(formatted_parts)

    def inject_context_selectively(
        self, text: str, session_id: str, injection_types: list[str] = None
    ) -> str:
        """
        选择性地注入特定类型的上下文

        Args:
            text: 原始文本
            session_id: 会话ID
            injection_types: 要注入的上下文类型列表

        Returns:
            注入选择性上下文后的文本
        """
        if injection_types is None:
            injection_types = ["topic", "parameters", "entities", "history"]

        context = {}
        if self.context_integrator:
            context = self.context_integrator.get_context_for_intent_recognition(
                session_id
            )

        if not context or not text:
            return text

        injected_parts = [text]

        # 根据指定类型注入上下文
        if "topic" in injection_types:
            current_topic = context.get("current_topic", "")
            if current_topic and current_topic.lower() not in text.lower():
                injected_parts.insert(0, f"[话题: {current_topic}]")

        if "parameters" in injection_types:
            parameters = context.get("parameters", {})
            for param_name, param_value in list(parameters.items())[-3:]:
                if str(param_value).lower() not in text.lower():
                    injected_parts.insert(0, f"[{param_name}: {param_value}]")

        if "entities" in injection_types:
            related_entities = context.get("related_entities", [])
            for entity in related_entities[-2:]:
                if entity.lower() not in text.lower():
                    injected_parts.insert(0, f"[实体: {entity}]")

        if "history" in injection_types:
            intent_history = context.get("intent_history", [])
            if intent_history:
                last_intent = intent_history[-1]
                injected_parts.append(f"[最近意图: {last_intent}]")

        return " ".join(injected_parts)

    def get_context_summary(self, session_id: str) -> str:
        """
        获取会话的上下文摘要，用于调试和监控

        Args:
            session_id: 会话ID

        Returns:
            上下文摘要字符串
        """
        if not self.context_integrator:
            return "Context integrator not available"

        context = self.context_integrator.get_context_for_intent_recognition(session_id)

        if not context:
            return f"No context available for session {session_id}"

        summary_parts = [
            f"Session: {session_id}",
            f"Topic: {context.get('current_topic', 'N/A')}",
            f"Intent History: {', '.join(context.get('intent_history', [])[-3:]) or 'N/A'}",  # noqa: E501
            f"Parameters Count: {len(context.get('parameters', {}))}",
            f"Entities Count: {len(context.get('related_entities', []))}",
            f"Last Accessed: {context.get('last_accessed', 'N/A')}",
        ]

        return " | ".join(summary_parts)

    def validate_injection_performance(
        self, test_queries: list[str], session_id: str = "test"
    ) -> dict[str, Any]:
        """
        验证注入性能是否符合要求（≤20ms）

        Args:
            test_queries: 测试查询列表
            session_id: 测试会话ID

        Returns:
            性能验证结果
        """
        results = {
            "total_queries": len(test_queries),
            "total_time": 0,
            "avg_time": 0,
            "max_time": 0,
            "min_time": float("inf"),
            "within_threshold": 0,  # 在阈值内（≤20ms）的查询数
            "threshold_exceeded": 0,  # 超出阈值的查询数
            "threshold": 0.02,  # 20ms阈值（以秒为单位）
        }

        for query in test_queries:
            start_time = time.time()
            try:
                self.inject_context_to_padatious_query(query, session_id)
            except Exception as e:
                self.logger.error(f"Error during performance test: {e}")
                continue

            query_time = time.time() - start_time
            results["total_time"] += query_time

            if query_time > results["max_time"]:
                results["max_time"] = query_time
            if query_time < results["min_time"]:
                results["min_time"] = query_time

            if query_time <= results["threshold"]:
                results["within_threshold"] += 1
            else:
                results["threshold_exceeded"] += 1

        if results["total_queries"] > 0:
            results["avg_time"] = results["total_time"] / results["total_queries"]
            results["performance_ok"] = (
                results["within_threshold"] / results["total_queries"] >= 0.95
            )  # 95%的查询应在阈值内

        results["min_time"] = (
            results["min_time"] if results["min_time"] != float("inf") else 0
        )

        return results

    def get_injection_stats(self) -> dict[str, Any]:
        """
        获取注入统计信息

        Returns:
            注入统计信息
        """
        return {
            "injection_count": self.injection_count,
            "last_injection_time": self.last_injection_time,
            "avg_injection_time": getattr(self, "_avg_time", 0),
        }
