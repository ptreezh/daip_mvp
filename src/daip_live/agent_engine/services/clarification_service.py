"""
Clarification service for context-aware intent recognition.
Handles missing parameters, ambiguous intents, and missing keywords.
"""

from typing import Any, Optional

from daip_live.agent_engine.models.clarification_models import (
    ClarificationOption,
    ClarificationRequest,
    ClarificationType,
)
from daip_live.core.models import ClarificationRequestEvent


class ClarificationService:
    """Service to handle intent clarification and missing parameter detection."""

    def __init__(self):
        self.session_contexts: dict[str, dict[str, Any]] = {}

    def check_missing_keywords(
        self, intent_name: str, parameters: dict[str, Any]
    ) -> Optional[ClarificationRequest]:
        """Check if required keywords are missing for certain intents."""

        # Define intents that require keywords
        keyword_required_intents = {
            "search_papers": {
                "param": "query",
                "message": "请输入您想搜索的论文主题或关键词",
                "example": "如：论文 人工智能 或 搜索 深度学习",
            },
            "download_paper": {
                "param": "paper_id",
                "message": "请提供arXiv ID或论文标题/主题进行下载",
                "example": "如：下载论文 1234.5678 或 下载论文 量子计算",
            },
            "start_debate": {
                "param": "topic",
                "message": "请输入辩论主题",
                "example": "如：辩论 AI伦理 或 讨论 机器学习",
            },
            "create_wiki": {
                "param": "title",
                "message": "请输入Wiki页面标题",
                "example": "如：创建Wiki 项目计划 或 Wiki 人工智能",
            },
        }

        if intent_name in keyword_required_intents:
            config = keyword_required_intents[intent_name]
            param_name = config["param"]

            # Check if parameter is missing or empty
            param_value = parameters.get(param_name, "")

            # 对于create_wiki意图，检查标题是否看起来像完整的命令而不是实际标题
            if intent_name == "create_wiki" and param_value:
                # 如果标题包含命令关键词，说明参数提取不完整，需要澄清
                command_keywords = [
                    "创建",
                    "新建",
                    "编辑",
                    "写个",
                    "做个",
                    "协同编辑",
                    "协作编辑",
                    "词条",
                    "维基",
                    "百科",
                    "wiki",
                    "Wiki",
                ]
                if any(keyword in param_value for keyword in command_keywords):
                    message = f"{config['message']}\n例如: {config['example']}"
                    return ClarificationRequest(
                        type=ClarificationType.MISSING_KEYWORDS,
                        message=message,
                        required_parameters=[param_name],
                    )

            if not param_value or param_value.strip() == "":
                message = f"{config['message']}\n例如: {config['example']}"
                return ClarificationRequest(
                    type=ClarificationType.MISSING_KEYWORDS,
                    message=message,
                    required_parameters=[param_name],
                )

        return None

    def check_missing_parameters(
        self, intent_name: str, parameters: dict[str, Any]
    ) -> Optional[ClarificationRequest]:
        """Check if required parameters are missing for an intent."""

        # Define intents with required parameters
        parameter_requirements = {
            "search_papers": {
                "required": ["max_results", "source"],
                "defaults": {"max_results": 5, "source": "arxiv"},
            },
            "convert_document": {
                "required": ["source_format", "target_format"],
                "defaults": {},
            },
            "create_ppt": {
                "required": ["content", "title"],
                "defaults": {"title": "Generated Presentation"},
            },
        }

        if intent_name in parameter_requirements:
            req_info = parameter_requirements[intent_name]
            required_params = req_info["required"]
            defaults = req_info["defaults"]

            missing_params = []
            for param in required_params:
                if param not in parameters or parameters[param] is None:
                    # Only mark as missing if no default exists
                    if param not in defaults:
                        missing_params.append(param)

            if missing_params:
                message = f"需要补充信息: {', '.join(missing_params)}"
                return ClarificationRequest(
                    type=ClarificationType.MISSING_PARAMETERS,
                    message=message,
                    required_parameters=missing_params,
                )

        return None

    def check_ambiguous_intent(
        self, original_input: str, intent_confidence: float, possible_intents: list[str]
    ) -> Optional[ClarificationRequest]:
        """Check if intent is ambiguous and requires user clarification."""

        # If we have multiple possible intents with similar confidence, ask for clarification  # noqa: E501
        if (
            len(possible_intents) > 1 and intent_confidence < 0.8
        ):  # Low confidence with multiple options
            options = []
            for i, intent in enumerate(possible_intents):
                option_text = self._get_intent_description(intent)
                options.append(
                    ClarificationOption(
                        id=f"option_{i}", text=option_text, intent_action=intent
                    )
                )

            return ClarificationRequest(
                type=ClarificationType.AMBIGUOUS_INTENT,
                message="您的请求有多种可能的解释，请选择您想执行的操作：",
                options=options,
            )

        # Check for ambiguous inputs like "find", "show", "do" without clear context
        ambiguous_patterns = [
            ("find", "搜索", ["search_papers", "find_wiki", "locate_tool"]),
            ("show", "显示", ["show_history", "show_wiki", "show_status"]),
            ("convert", "转换", ["convert_doc", "convert_code", "transform"]),
        ]

        input_lower = original_input.lower()
        for pattern, desc, possible_actions in ambiguous_patterns:
            if pattern in input_lower:
                options = []
                for i, action in enumerate(possible_actions):
                    options.append(
                        ClarificationOption(
                            id=f"action_{i}",
                            text=f"{desc} {action.replace('_', ' ').title()}",
                            intent_action=action,
                        )
                    )

                if options:  # Only return if we have options
                    return ClarificationRequest(
                        type=ClarificationType.AMBIGUOUS_INTENT,
                        message=f"您是想{desc}什么内容？请选择：",
                        options=options,
                    )

        return None

    def _get_intent_description(self, intent_name: str) -> str:
        """Get a user-friendly description of an intent."""
        descriptions = {
            "search_papers": "搜索学术论文",
            "download_paper": "下载论文",
            "start_debate": "开始辩论",
            "create_wiki": "创建Wiki页面",
            "convert_document": "转换文档格式",
            "create_ppt": "生成PPT演示文稿",
            "show_history": "查看历史记录",
            "question": "回答问题",
            "chat": "普通聊天",
        }
        return descriptions.get(intent_name, intent_name.replace("_", " ").title())

    def create_clarification_event(
        self, session_id: str, clarification_request: ClarificationRequest
    ) -> ClarificationRequestEvent:
        """Create a clarification request event."""
        options_data = []
        if clarification_request.options:
            for option in clarification_request.options:
                options_data.append(
                    {
                        "id": option.id,
                        "text": option.text,
                        "intent_action": option.intent_action,
                        "parameters": option.parameters,
                    }
                )

        return ClarificationRequestEvent(
            session_id=session_id,
            clarification_type=clarification_request.type.value,
            message=clarification_request.message,
            options=options_data,
            required_parameters=clarification_request.required_parameters or [],
        )

    def process_user_clarification(
        self,
        session_id: str,
        user_response: str,
        pending_clarification: ClarificationRequest,
    ) -> dict[str, Any]:
        """Process user's clarification response and return updated parameters."""

        result_params = {}

        if pending_clarification.type == ClarificationType.MISSING_KEYWORDS:
            # For missing keywords, treat the user response as the keyword
            result_params[pending_clarification.required_parameters[0]] = (
                user_response.strip()
            )

        elif pending_clarification.type == ClarificationType.MISSING_PARAMETERS:
            # For missing parameters, need to parse the response or provide defaults
            # For now, we'll just add the user response as the main parameter
            if pending_clarification.required_parameters:
                result_params[pending_clarification.required_parameters[0]] = (
                    user_response.strip()
                )

        elif pending_clarification.type == ClarificationType.AMBIGUOUS_INTENT:
            # User should have selected an option ID
            # In a real implementation, we'd map the selected option back to intent
            selected_option = None
            for option in pending_clarification.options:
                if option.id == user_response or option.text in user_response:
                    selected_option = option
                    break

            if selected_option:
                result_params["selected_intent"] = selected_option.intent_action
                result_params["clarification_answer"] = user_response

        return result_params
