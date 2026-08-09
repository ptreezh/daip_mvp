"""
上下文感知意图识别集成模块
将现有的上下文管理系统与意图识别器连接
"""

from typing import Any, Optional

from daip_live.agent_engine.enhanced_intent_recognizer import Intent


class ContextAwareEnhancedRecognizer:
    """
    将上下文感知功能集成到增强意图识别器中
    """

    def __init__(self, base_recognizer, context_manager=None):
        self.base_recognizer = base_recognizer
        self.context_manager = context_manager

        # 导入必要的上下文管理组件
        if context_manager is None:
            try:
                from daip_live.intent_recognition.enhanced_context_manager import (
                    EnhancedContextManager,
                )

                self.context_manager = EnhancedContextManager()
            except ImportError:
                try:
                    from daip_live.intent_recognition.context_manager import (
                        ContextManager,
                    )

                    self.context_manager = ContextManager()
                except ImportError:
                    # 如果都没有则设置为None，使用基础识别
                    self.context_manager = None

    def recognize_intent_with_context(
        self, text: str, session_id: str = "default"
    ) -> Optional[Intent]:
        """
        使用上下文感知的意图识别

        Args:
            text: 用户输入文本
            session_id: 会话ID

        Returns:
            识别到的意图对象
        """
        # 如果没有上下文管理器，使用基础识别
        if not self.context_manager:
            return self.base_recognizer.recognize_intent(text)

        # 首先检查是否有活跃的上下文/任务
        if self.context_manager.is_in_task(session_id):
            # 如果有活跃任务，使用上下文相关逻辑
            context = self.context_manager.get_context(session_id)
            if context:
                task_type = context.get("task_type", "")

                # 如果在Wiki创建任务中，尝试提取参数
                if task_type == "create_wiki":
                    return self._handle_wiki_continuation(text, session_id, context)
                elif task_type == "download_paper":
                    return self._handle_paper_continuation(text, session_id, context)

        # 如果没有活跃上下文或上下文处理失败，使用基础识别器
        return self.base_recognizer.recognize_intent(text, session_id=session_id)

    def _handle_wiki_continuation(
        self, text: str, session_id: str, context: dict[str, Any]
    ) -> Optional[Intent]:
        """处理Wiki创建任务的延续"""
        # 获取当前任务的缺失参数
        if hasattr(self.context_manager, "get_session_state"):
            session_state = self.context_manager.get_session_state(session_id)
            if session_state and hasattr(session_state, "current_task"):
                task = session_state.current_task
                if hasattr(task, "get_missing_params"):
                    missing_params = task.get_missing_params()

                    if missing_params:
                        # 尝试作为缺失参数的值
                        first_missing = missing_params[0]

                        # 更新任务参数
                        if hasattr(self.context_manager, "add_task_parameter"):
                            self.context_manager.add_task_parameter(
                                session_id, first_missing, text
                            )

                        # 创建一个参数填充意图
                        intent = Intent(
                            name=f"fill_{first_missing}_param",
                            confidence=0.8,
                            parameters={first_missing: text},
                            tool_name="wiki_tool",
                            description=f"填充Wiki任务参数: {first_missing}",
                            intent_type="contextual",
                            requires_confidence_check=False,
                        )

                        # 检查任务是否已完成
                        if hasattr(task, "is_complete") and task.is_complete():
                            intent.task_completed = True

                        return intent

        # 如果上下文处理失败，使用基础识别
        return self.base_recognizer.recognize_intent(text)

    def _handle_paper_continuation(
        self, text: str, session_id: str, context: dict[str, Any]
    ) -> Optional[Intent]:
        """处理论文下载任务的延续"""
        # 获取当前任务的缺失参数
        if hasattr(self.context_manager, "get_session_state"):
            session_state = self.context_manager.get_session_state(session_id)
            if session_state and hasattr(session_state, "current_task"):
                task = session_state.current_task
                if hasattr(task, "get_missing_params"):
                    missing_params = task.get_missing_params()

                    if missing_params:
                        # 尝试作为缺失参数的值
                        first_missing = missing_params[0]

                        # 更新任务参数
                        if hasattr(self.context_manager, "add_task_parameter"):
                            self.context_manager.add_task_parameter(
                                session_id, first_missing, text
                            )

                        # 创建一个参数填充意图
                        intent = Intent(
                            name=f"fill_{first_missing}_param",
                            confidence=0.8,
                            parameters={first_missing: text},
                            tool_name="paper_tool",
                            description=f"填充论文任务参数: {first_missing}",
                            intent_type="contextual",
                            requires_confidence_check=False,
                        )

                        # 检查任务是否已完成
                        if hasattr(task, "is_complete") and task.is_complete():
                            intent.task_completed = True

                        return intent

        # 如果上下文处理失败，使用基础识别
        return self.base_recognizer.recognize_intent(text)

    def recognize_intent(
        self, text: str, session_id: str = "default"
    ) -> Optional[Intent]:
        """
        主要的意图识别方法，集成上下文感知
        """
        # 使用带上下文的识别方法
        return self.recognize_intent_with_context(text, session_id)

    def start_task_session(
        self,
        session_id: str,
        task_type: str,
        required_params: list = None,
        initial_params: dict = None,
    ):
        """
        开始一个任务会话

        Args:
            session_id: 会话ID
            task_type: 任务类型
            required_params: 所需参数列表
            initial_params: 初始参数
        """
        if not self.context_manager:
            return

        if not required_params:
            required_params = []

        if not initial_params:
            initial_params = {}

        # 使用上下文管理器启动任务
        if hasattr(self.context_manager, "set_context") and hasattr(
            self.context_manager, "add_task_parameter"
        ):
            context_data = {
                "task_type": task_type,
                "required_params": required_params,
                "filled_params": initial_params,
            }
            self.context_manager.set_context(session_id, context_data)

            # 为每个初始参数设置值
            for param_name, param_value in initial_params.items():
                self.context_manager.add_task_parameter(
                    session_id, param_name, param_value
                )

    def get_session_context(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取会话上下文"""
        if self.context_manager:
            return self.context_manager.get_context(session_id)
        return None

    def is_in_task(self, session_id: str) -> bool:
        """检查会话是否在任务中"""
        if self.context_manager:
            if hasattr(self.context_manager, "is_in_task"):
                return self.context_manager.is_in_task(session_id)
            else:
                # 尝试使用另一种方式检查
                context = self.get_session_context(session_id)
                return context is not None and context.get("task_type") is not None
        return False
