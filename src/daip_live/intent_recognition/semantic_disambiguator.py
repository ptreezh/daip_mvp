"""
语义消歧算法

专门负责语义层面的意图消歧，解决多意图候选时的消歧问题
特别是防止普通对话被误识别为论文意图
遵循SOLID原则中的单一职责原则
"""

import logging
from typing import Any, Union

from daip_live.agent_engine.enhanced_intent_recognizer import Intent
from daip_live.intent_recognition.contextual_intent_recognizer import ContextualIntent


class SemanticDisambiguator:
    """
    语义消歧器

    专门负责语义层面的意图消歧
    遵循SOLID原则：
    - SRP: 仅负责语义消歧
    - OCP: 可扩展更多消歧策略
    """

    def __init__(self):
        """
        初始化语义消歧器
        """
        self.logger = logging.getLogger(__name__)

        # 定义意图相关性权重
        self.intent_relevance_weights = {
            "chat": {
                "greeting_words": [
                    "你好",
                    "hello",
                    "hi",
                    "您好",
                    "您好啊",
                    "早上好",
                    "下午好",
                    "晚上好",
                    "谢谢",
                    "再见",
                    "拜拜",
                ],
                "question_words": [
                    "为什么",
                    "为啥",
                    "如何",
                    "怎么",
                    "怎样",
                    "什么",
                    "吗",
                    "呢",
                    "啊",
                    "呀",
                ],
                "casual_words": ["随便", "聊", "聊天", "闲聊", "说", "说说", "谈谈"],
            },
            "question": {
                "question_indicators": [
                    "？",
                    "?",
                    "什么",
                    "为什么",
                    "如何",
                    "怎么",
                    "怎样",
                    "是否",
                    "能否",
                    "可否",
                ],
                "inquiry_words": ["问", "询问", "请教", "请问", "咨询"],
            },
            "search_papers": {
                "academic_keywords": [
                    "论文",
                    "arxiv",
                    "学术",
                    "研究",
                    "期刊",
                    "文献",
                    "下载",
                    "获取",
                    "搜索",
                    "查找",
                    "papers",
                    "paper",
                ]
            },
            "download_paper": {
                "paper_indicators": [
                    "下载",
                    "获取",
                    "pdf",
                    "arxiv",
                    "id",
                    "1234.",
                    "v\\d",
                    "paper",
                    "论文",
                ],
                "format_indicators": ["pdf", "格式", "文件", "文档"],
            },
            "start_debate": {
                "debate_keywords": [
                    "辩论",
                    "讨论",
                    "辩",
                    "论",
                    "观点",
                    "argue",
                    "debate",
                    "opinion",
                ],
                "topic_indicators": ["关于", "针对", "就", "话题", "主题", "topic"],
            },
            "create_wiki": {
                "wiki_keywords": [
                    "维基",
                    "百科",
                    "词条",
                    "创建",
                    "新建",
                    "编辑",
                    "撰写",
                    "wiki",
                    "百科全书",
                ],
                "content_indicators": ["写", "制作", "建立", "制作"],
            },
            "execute_skill": {
                "skill_keywords": [
                    "技能",
                    "执行",
                    "运行",
                    "使用",
                    "help",
                    "分析",
                    "处理",
                    "搜索",
                    "总结",
                ],
                "action_indicators": ["帮我", "请帮我", "帮我", "请求", "运行", "启动"],
            },
        }

    def disambiguate_intent(
        self,
        candidate_intents: list[Union[Intent, ContextualIntent]],
        context: dict[str, Any],
    ) -> Union[Intent, ContextualIntent]:
        """
        对多个候选意图进行语义消歧，选择最合适的意图

        Args:
            candidate_intents: 候选意图列表
            context: 上下文信息

        Returns:
            经语义消歧后选择的最佳意图
        """
        if not candidate_intents:
            return None

        if len(candidate_intents) == 1:
            return candidate_intents[0]

        # 基于上下文信息对候选意图进行评分
        scored_intents = []
        for intent in candidate_intents:
            score = self._calculate_contextual_score(intent, context)
            scored_intents.append((intent, score))

        # 选择评分最高的意图
        best_intent, best_score = max(scored_intents, key=lambda x: x[1])

        self.logger.info(
            f"Semantic disambiguation selected intent '{best_intent.name}' with score {best_score:.3f}"  # noqa: E501
        )

        return best_intent

    def disambiguate_with_text(
        self,
        text: str,
        candidate_intents: list[Union[Intent, ContextualIntent]],
        context: dict[str, Any],
    ) -> Union[Intent, ContextualIntent]:
        """
        结合文本内容对候选意图进行语义消歧

        Args:
            text: 原始输入文本
            candidate_intents: 候选意图列表
            context: 上下文信息

        Returns:
            经语义消歧后选择的最佳意图
        """
        if not candidate_intents:
            return None

        if len(candidate_intents) == 1:
            return candidate_intents[0]

        # 结合文本内容和上下文对候选意图进行评分
        scored_intents = []
        for intent in candidate_intents:
            score = self._calculate_text_and_context_score(intent, text, context)
            scored_intents.append((intent, score))

        # 选择评分最高的意图
        best_intent, best_score = max(scored_intents, key=lambda x: x[1])

        self.logger.info(
            f"Text-based semantic disambiguation selected intent '{best_intent.name}' with score {best_score:.3f}"  # noqa: E501
        )

        return best_intent

    def _calculate_contextual_score(
        self, intent: Union[Intent, ContextualIntent], context: dict[str, Any]
    ) -> float:
        """
        基于上下文计算意图的匹配分数
        """
        base_score = getattr(intent, "confidence", 0.0)

        if not context:
            return base_score

        # 获取上下文信息
        current_topic = context.get("current_topic", "").lower()
        intent_history = context.get("intent_history", [])
        parameters = context.get("parameters", {})
        context.get("conversation_history", [])

        # 根据上下文调整分数

        # 聊天意图在非学术上下文中得分增加
        if intent.name in ["chat", "question"] and any(
            keyword in current_topic
            for keyword in [
                "你好",
                "hi",
                "hello",
                "谢谢",
                "帮助",
                "助手",
                "聊天",
                "问题",
                "为什么",
                "为啥",
            ]
        ):
            base_score += 0.2

        # 论文意图在非学术上下文中得分降低
        elif intent.name in ["search_papers", "download_paper"] and not any(
            keyword in current_topic
            for keyword in [
                "论文",
                "arxiv",
                "学术",
                "研究",
                "paper",
                "download",
                "文献",
                "期刊",
            ]
        ):
            base_score -= 0.3

        # 辩论意图在相关话题上下文中得分增加
        elif intent.name == "start_debate" and any(
            keyword in current_topic
            for keyword in ["辩论", "讨论", "观点", "argue", "debate"]
        ):
            base_score += 0.15

        # 检查意图历史连续性
        if intent_history and intent.name == intent_history[-1]:
            # 连续相同的意图，稍微增加分数
            base_score += 0.05
        elif (
            intent_history
            and intent.name in ["chat", "question"]
            and intent_history[-1] in ["chat", "question"]
        ):
            # 聊天类意图的连续性
            base_score += 0.05

        # 检查参数相关性
        for param_name, param_value in parameters.items():
            param_str = str(param_value).lower()
            if (
                param_str
                and intent.name in ["search_papers", "download_paper"]
                and any(kw in param_str for kw in ["role", "roles", "助手"])
            ):
                # 如果参数包含"role"等词，论文意图得分降低
                base_score -= 0.2

        return max(0.0, min(base_score, 1.0))  # 限制分数在0.0-1.0之间

    def _calculate_text_and_context_score(
        self,
        intent: Union[Intent, ContextualIntent],
        text: str,
        context: dict[str, Any],
    ) -> float:
        """
        结合文本内容和上下文计算意图匹配分数
        """
        base_score = getattr(intent, "confidence", 0.0)
        text_score = self._calculate_text_score(intent, text)

        # 综合基础置信度、文本匹配度和上下文匹配度
        combined_score = (
            base_score * 0.4
            + text_score * 0.4
            + self._calculate_contextual_score(intent, context) * 0.2
        )

        # 针对特定消歧场景的调整
        adjusted_score = self._apply_disambiguation_adjustments(
            intent, text, combined_score
        )

        return max(0.0, min(adjusted_score, 1.0))

    def _calculate_text_score(
        self, intent: Union[Intent, ContextualIntent], text: str
    ) -> float:
        """
        基于文本内容计算意图匹配分数
        """
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # 根据意图类型检查文本中的关键词
        if intent.name in self.intent_relevance_weights:
            intent_rules = self.intent_relevance_weights[intent.name]

            # 检查各类关键词
            for category, keywords in intent_rules.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        # 根据关键词重要性给予不同权重
                        if category in [
                            "greeting_words",
                            "question_indicators",
                            "inquiry_words",
                        ]:
                            score += 0.15  # 问候和问题词权重较高
                        elif category in ["academic_keywords", "paper_indicators"]:
                            score += 0.12  # 学术关键词权重中等
                        else:
                            score += 0.10  # 其他关键词权重一般

        # 检查特殊模式
        if intent.name == "chat":
            # 检查是否为问候语
            greeting_patterns = [
                "你好",
                "hello",
                "hi",
                "谢谢",
                "help",
                "helping",
                "啊",
                "呀",
                "哦",
                "嗯",
            ]
            greeting_matches = sum(
                1 for pattern in greeting_patterns if pattern in text_lower
            )
            score += greeting_matches * 0.1

        elif intent.name == "question":
            # 检查是否为疑问句
            if any(char in text for char in ["？", "?"]):
                score += 0.2
            if any(
                word in text_lower
                for word in ["为什么", "为啥", "如何", "怎么", "怎样"]
            ):
                score += 0.15

        elif intent.name == "download_paper":
            # 检查是否包含论文ID格式
            import re

            paper_id_match = re.search(r"\d{4}\.\d{4,5}", text)
            if paper_id_match:
                score += 0.25

        # 防止分数过高
        return min(score, 1.0)

    def _apply_disambiguation_adjustments(
        self, intent: Union[Intent, ContextualIntent], text: str, base_score: float
    ) -> float:
        """
        应用特定的消歧调整规则
        """
        text_lower = text.lower()

        # 核心消歧规则：防止将普通对话误识别为论文意图
        if intent.name in ["search_papers", "download_paper"]:
            # 检查文本是否包含聊天/问题特征
            chat_indicators = [
                "你好",
                "为啥",
                "为什么",
                "如何",
                "怎么",
                "谢谢",
                "help",
                "helping",
                "role",
                "roles",
            ]
            chat_indicators_present = any(
                indicator in text_lower for indicator in chat_indicators
            )

            question_indicators = ["？", "?", "呢", "啊", "呀"]
            question_present = any(
                indicator in text for indicator in question_indicators
            )

            # 如果文本包含聊天特征，降低论文意图分数
            if chat_indicators_present or question_present:
                adjustment = -0.3
                self.logger.info(
                    f"Applying negative adjustment ({adjustment}) to paper intent due to chat/question indicators in text: '{text}'"  # noqa: E501
                )
                return max(0.1, base_score + adjustment)  # 确保最低分不低于0.1

        # 如果是聊天意图且文本包含聊天特征，提高分数
        elif intent.name in ["chat", "question"]:
            chat_indicators = [
                "你好",
                "hello",
                "help",
                "？",
                "?",
                "啊",
                "呀",
                "哦",
                "嗯",
                "谢谢",
                "拜拜",
            ]
            chat_indicators_present = sum(
                1 for indicator in chat_indicators if indicator in text_lower
            )

            if chat_indicators_present > 0:
                adjustment = min(chat_indicators_present * 0.05, 0.2)  # 最多增加0.2
                self.logger.info(
                    f"Applying positive adjustment (+{adjustment}) to chat intent due to chat indicators in text: '{text}'"  # noqa: E501
                )
                return min(1.0, base_score + adjustment)

        return base_score

    def resolve_intent_conflict(
        self,
        primary_intent: Union[Intent, ContextualIntent],
        secondary_intent: Union[Intent, ContextualIntent],
        text: str,
        context: dict[str, Any],
    ) -> Union[Intent, ContextualIntent]:
        """
        解决主要意图和次要意图之间的冲突

        Args:
            primary_intent: 主要意图
            secondary_intent: 次要意图
            text: 原始输入文本
            context: 上下文信息

        Returns:
            解决冲突后的最终意图
        """
        primary_score = self._calculate_text_and_context_score(
            primary_intent, text, context
        )
        secondary_score = self._calculate_text_and_context_score(
            secondary_intent, text, context
        )

        self.logger.info(
            f"Intent conflict resolution: {primary_intent.name} (score: {primary_score:.3f}) vs {secondary_intent.name} (score: {secondary_score:.3f})"  # noqa: E501
        )

        if primary_score > secondary_score:
            return primary_intent
        else:
            return secondary_intent

    def validate_disambiguation_rules(
        self, test_cases: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        验证消歧规则的有效性

        Args:
            test_cases: 测试用例列表

        Returns:
            验证结果
        """
        results = {
            "total_cases": len(test_cases),
            "correctly_disambiguated": 0,
            "errors": [],
            "details": [],
        }

        for i, test_case in enumerate(test_cases):
            try:
                text = test_case["text"]
                candidate_intents = test_case["candidates"]
                expected_intent = test_case["expected"]
                context = test_case.get("context", {})

                selected_intent = self.disambiguate_with_text(
                    text, candidate_intents, context
                )

                is_correct = selected_intent.name == expected_intent
                result_detail = {
                    "text": text,
                    "expected": expected_intent,
                    "selected": selected_intent.name,
                    "is_correct": is_correct,
                    "candidates": [intent.name for intent in candidate_intents],
                }

                results["details"].append(result_detail)

                if is_correct:
                    results["correctly_disambiguated"] += 1
                else:
                    results["errors"].append(result_detail)

            except Exception as e:
                error_detail = {
                    "index": i,
                    "text": test_case.get("text", "unknown"),
                    "error": str(e),
                }
                results["errors"].append(error_detail)

        results["accuracy"] = results["correctly_disambiguated"] / max(
            1, results["total_cases"]
        )
        return results
