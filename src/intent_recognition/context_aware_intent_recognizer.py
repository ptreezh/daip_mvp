"""
上下文感知意图识别器实现
遵循依赖倒置原则 - 依赖于抽象而非具体实现
"""

from typing import Dict, Any
from .context_interfaces import IIntentRecognizer, IContextManager
from .task_context import TaskContext


class ContextAwareIntentRecognizer(IIntentRecognizer):
    """
    上下文感知意图识别器实现
    遵循依赖倒置原则 - 依赖于IContextManager抽象而非具体实现
    """

    def __init__(self, context_manager: IContextManager, base_intent_recognizer: Any = None):
        """
        初始化上下文感知意图识别器

        Args:
            context_manager: 上下文管理器实例
            base_intent_recognizer: 基础意图识别器（可选）
        """
        self.context_manager = context_manager
        self.base_intent_recognizer = base_intent_recognizer

        # 导入参数提取器
        try:
            from .enhanced_parameter_extraction import ParameterExtractor
            self.parameter_extractor = ParameterExtractor()
        except ImportError:
            self.parameter_extractor = None

        # 导入对话历史分析器
        # 如果context_manager支持历史分析功能，直接使用
        if hasattr(context_manager, 'get_relevant_content_for_task'):
            self.history_analyzer = context_manager
        else:
            try:
                from .conversation_history_analyzer import ConversationHistoryAnalyzer
                self.history_analyzer = ConversationHistoryAnalyzer()
            except ImportError:
                self.history_analyzer = None

    def recognize_intent(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        识别用户输入的意图，考虑上下文

        Args:
            session_id: 会话标识符
            user_input: 用户输入

        Returns:
            包含意图识别结果的字典
        """
        # 检查当前会话是否正在进行任务
        if self.context_manager.is_in_task(session_id):
            # 如果在任务中，尝试从输入中提取参数
            return self._handle_contextual_input_with_extraction(session_id, user_input)
        else:
            # 如果不在任务中，使用基础意图识别
            if self.base_intent_recognizer:
                # EnhancedIntentRecognizer使用recognize_intent方法
                if hasattr(self.base_intent_recognizer, 'recognize_intent'):
                    result = self.base_intent_recognizer.recognize_intent(user_input)
                else:
                    result = self.base_intent_recognizer.recognize(user_input)

                # 处理EnhancedIntentRecognizer返回的Intent对象
                if hasattr(result, 'name'):  # 如果是Intent对象
                    return {
                        "intent": result.name,
                        "confidence": result.confidence,
                        "user_input": user_input,
                        "parameters": result.parameters,
                        "tool_name": result.tool_name,
                        "description": result.description,
                        "intent_type": result.intent_type.value if hasattr(result.intent_type, 'value') else result.intent_type
                    }
                else:  # 如果已经是字典
                    # 确保user_input正确传递
                    if "user_input" not in result:
                        result["user_input"] = user_input
                    return result
            else:
                # 默认返回常规意图识别结果
                return {
                    "intent": "general_chat",
                    "confidence": 1.0,
                    "user_input": user_input,
                    "context": None
                }

    def _handle_contextual_input_with_extraction(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        处理上下文相关的输入，包含参数提取逻辑

        Args:
            session_id: 会话标识符
            user_input: 用户输入

        Returns:
            包含处理结果的字典
        """
        # 获取当前任务上下文
        context = self.context_manager.get_context(session_id)
        if not context:
            return {
                "intent": "general_chat",
                "confidence": 1.0,
                "user_input": user_input,
                "error": "No active task context found"
            }

        task_context = self.context_manager.get_session_state(session_id).current_task
        missing_params = task_context.get_missing_params()

        # 如果有缺失参数，尝试从用户输入中提取
        extracted_params = None
        if missing_params and self.parameter_extractor:
            extracted_params = self.parameter_extractor.extract_from_input(
                user_input, context['task_type']
            )

        # 优先使用提取的参数，如果没有提取到，则使用整个输入作为第一个缺失参数
        filled_params = []

        if extracted_params:
            # 根据任务类型和缺失参数，尝试填充提取的参数
            task_type = context['task_type']

            # 论文下载任务的参数填充
            if task_type == 'download_paper' or 'paper' in task_type:
                if 'arxiv_id' in missing_params and extracted_params.arxiv_id:
                    self.context_manager.add_task_parameter(session_id, 'arxiv_id', extracted_params.arxiv_id)
                    filled_params.append(('arxiv_id', extracted_params.arxiv_id))

                if 'topic' in missing_params and extracted_params.topic:
                    self.context_manager.add_task_parameter(session_id, 'topic', extracted_params.topic)
                    filled_params.append(('topic', extracted_params.topic))

            # Wiki创建任务的参数填充
            elif task_type == 'create_wiki' and 'title' in missing_params and extracted_params.title:
                self.context_manager.add_task_parameter(session_id, 'title', extracted_params.title)
                filled_params.append(('title', extracted_params.title))

        # 如果没有通过直接提取填充参数，尝试从历史记录中提取相关信息
        if not filled_params and missing_params and self.history_analyzer:
            # 特别针对Wiki创建任务，尝试从历史中提取辩论结果
            if context['task_type'] == 'create_wiki':
                # 检查历史分析器类型并相应调用
                if hasattr(self.history_analyzer, 'get_relevant_content_for_task'):
                    # 使用上下文管理器的分析方法
                    history_content = self.history_analyzer.get_relevant_content_for_task(
                        session_id, context['task_type']
                    )
                else:
                    # 使用独立的分析器
                    history_content = self.history_analyzer.extract_debate_content_from_history(
                        self.context_manager.get_session_state(session_id).history
                    )

                # 根据缺失参数尝试使用历史内容
                for param_name in missing_params:
                    if param_name == 'title' and history_content.get('topic'):
                        self.context_manager.add_task_parameter(session_id, 'title', history_content['topic'])
                        filled_params.append(('title', history_content['topic']))
                        break
                    elif param_name == 'content' and history_content.get('content'):
                        self.context_manager.add_task_parameter(session_id, 'content', history_content['content'])
                        filled_params.append(('content', history_content['content']))
                        break
                    elif param_name == 'summary' and history_content.get('summary'):
                        self.context_manager.add_task_parameter(session_id, 'summary', history_content['summary'])
                        filled_params.append(('summary', history_content['summary']))
                        break

        # 如果仍然没有填充参数，或者对应参数不在缺失列表中，则使用原始逻辑
        if not filled_params and missing_params:
            next_param = missing_params[0]
            # 检查是否已经有该参数，避免重复填充
            if next_param not in task_context.filled_params:
                self.context_manager.add_task_parameter(session_id, next_param, user_input)
                filled_params.append((next_param, user_input))

        # 构建结果
        result = {
            "intent": f"contextual_{context['task_type']}_param",
            "confidence": 1.0,
            "user_input": user_input,
            "context": context,
            "extracted_params": vars(extracted_params) if extracted_params else None,
            "history_content": history_content if 'history_content' in locals() else None,
            "filled_params": filled_params
        }

        # 为了向后兼容，如果只填充了一个参数，添加旧的字段
        if len(filled_params) == 1:
            param_name, param_value = filled_params[0]
            result["param_name"] = param_name
            result["param_value"] = param_value
        elif len(filled_params) > 1:
            # 如果填充了多个参数，使用第一个作为主要参数（用于向后兼容）
            param_name, param_value = filled_params[0]
            result["param_name"] = param_name
            result["param_value"] = param_value

        # 检查任务是否已完成
        if task_context.is_complete():
            result["task_completed"] = True
            result["completed_task"] = {
                "task_type": context['task_type'],
                "parameters": task_context.parameters
            }

            # 清除上下文
            self.context_manager.clear_context(session_id)
        else:
            result["task_completed"] = False
            result["remaining_params"] = task_context.get_missing_params()

        return result

    def _handle_contextual_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        原始的处理上下文相关输入方法（保留向后兼容性）
        """
        return self._handle_contextual_input_with_extraction(session_id, user_input)