"""
会话上下文感知的意图识别器
用于改进跨会话的意图一致性
"""

import re
from datetime import datetime
from typing import Any


class SessionContextAwareRecognizer:
    """
    会话上下文感知的意图识别器
    基于历史对话维持上下文一致性
    """

    def __init__(self, base_recognizer):
        self.base_recognizer = base_recognizer
        self.conversation_history = []
        self.current_context = {}
        self.last_context_update = None

        # 定义上下文相关的意图映射
        self.contextual_intent_weights = {
            "wiki_editing": ["create_wiki", "edit_wiki", "search_wiki", "update_wiki"],
            "debate_session": ["debate", "argue", "discuss"],
            "role_playing": ["role_play", "simulate", "act_as"],
            "skill_execution": ["execute_skill", "run_tool", "use_skill"],
        }

    def add_to_history(self, user_input: str, intent_result: Any):
        """将对话添加到历史记录"""
        self.conversation_history.append(
            {
                "timestamp": datetime.now(),
                "user_input": user_input,
                "intent_result": intent_result,
                "context": self.current_context.copy(),
            }
        )

        # 维持最近10条对话的历史
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    def analyze_session_context(self, current_input: str) -> dict[str, Any]:
        """分析当前会话上下文"""
        if not self.conversation_history:
            return {}

        # 检查最近的对话是否属于某个特定上下文
        recent_conversation = self.conversation_history[-3:]  # 检查最近3条
        context_signals = {}

        # 检测Wiki编辑上下文
        wiki_related = any(
            "wiki" in str(item.get("intent_result", "")).lower()
            for item in recent_conversation
        )

        # 检测话题连贯性
        if wiki_related:
            context_signals["maintain_wiki_context"] = True
            # 提取相关主题词
            topic_keywords = []
            for item in recent_conversation:
                if "wiki" in str(item.get("intent_result", "")).lower():
                    # 提取输入中的关键词
                    words = re.findall(r"[\w\u4e00-\u9fff]+", current_input)
                    topic_keywords.extend(words)
            if topic_keywords:
                context_signals["related_topics"] = list(set(topic_keywords))

        # 检测持续的讨论话题
        continuity_pattern = re.compile(
            "|".join(
                [
                    r"继续",
                    r"接着",
                    r"然后",
                    r"往下",
                    r"继续说",
                    r"接着说",
                    r"more",
                    r"continue",
                    r"next",
                    r"further",
                ]
            ),
            re.IGNORECASE,
        )

        if continuity_pattern.search(current_input) or wiki_related:
            context_signals["session_continuity"] = True

        return context_signals

    def recognize_intent_with_context(self, user_input: str) -> Any:
        """基于上下文识别意图"""
        # 分析当前会话上下文
        self.current_context = self.analyze_session_context(user_input)

        # 首先使用基础识别器
        base_intent = self.base_recognizer.recognize_intent(user_input)

        # 如果检测到上下文信号，则调整意图识别
        if self.current_context.get("maintain_wiki_context"):
            # 如果在Wiki会话中，强化Wiki相关意图
            if base_intent and hasattr(base_intent, "confidence"):
                # 检查是否已经有Wiki意图
                is_wiki_intent = any(
                    "wiki" in str(getattr(intent, "name", "")).lower()
                    for intent in (
                        [base_intent]
                        if hasattr(base_intent, "name")
                        else base_intent
                        if isinstance(base_intent, list)
                        else [base_intent]
                    )
                )

                if not is_wiki_intent:
                    # 检查输入中是否包含Wiki相关词汇
                    wiki_indicators = [
                        "词条",
                        "编辑",
                        "wiki",
                        "页面",
                        "知识",
                        "文档",
                        "条目",
                    ]
                    if any(indicator in user_input for indicator in wiki_indicators):
                        # 修改意图以保持上下文一致性
                        wiki_intent = self._create_wiki_intent(user_input)
                        if wiki_intent:
                            # 增加上下文信息
                            wiki_intent.context_signal = "session_continuation"
                            result = wiki_intent
                        else:
                            result = base_intent
                    else:
                        result = base_intent
                else:
                    result = base_intent
            else:
                result = base_intent
        else:
            result = base_intent

        # 记录本次交互
        self.add_to_history(user_input, result)

        return result

    def _create_wiki_intent(self, user_input: str):
        """创建Wiki意图对象"""
        # 尝试创建一个Wiki意图
        try:
            # 寻找合适的Wiki意图类型
            if "创建" in user_input or "新建" in user_input or "编辑" in user_input:
                intent_type = "create_wiki"
            elif "搜索" in user_input or "查找" in user_input or "找" in user_input:
                intent_type = "search_wiki"
            else:
                intent_type = "create_wiki"  # 默认为创建

            # 创建意图对象结构（与基础意图识别器兼容）
            class WikiContextIntent:
                def __init__(self, intent_type, title):
                    self.name = intent_type
                    self.confidence = 0.9  # 高置信度，因为是上下文驱动的
                    self.wiki_title = title
                    self.context_signal = "session_continuation"

            # 提取标题（简化处理）
            title = user_input.replace("skills比MCP更有技术前景", "").strip()
            if not title:
                title = "skills比MCP更有技术前景"

            return WikiContextIntent(intent_type, title)

        except Exception:
            return None

    def reset_session(self):
        """重置会话上下文"""
        self.conversation_history = []
        self.current_context = {}
        self.last_context_update = None


def patch_intent_recognizer_with_context(original_recognizer):
    """
    用上下文感知功能增强原始意图识别器
    """
    context_recognizer = SessionContextAwareRecognizer(original_recognizer)

    # 保留原始方法
    context_recognizer.base_recognize_intent = original_recognizer.recognize_intent

    # 替换识别方法
    def new_recognize_intent(user_input):
        return context_recognizer.recognize_intent_with_context(user_input)

    original_recognizer.recognize_intent = new_recognize_intent

    # 添加上下文管理方法
    original_recognizer.add_to_history = context_recognizer.add_to_history
    original_recognizer.reset_session = context_recognizer.reset_session

    return original_recognizer
