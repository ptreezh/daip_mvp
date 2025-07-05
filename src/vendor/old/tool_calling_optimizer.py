"""工具调用优化器
基于第一性原理设计的智能工具调用决策系统
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ToolCallIntent(Enum):
    """工具调用意图分类"""

    TASK_MANAGEMENT = "task_management"
    DATA_RETRIEVAL = "data_retrieval"
    COMPUTATION = "computation"
    COLLABORATION = "collaboration"
    MEMORY_OPERATION = "memory_operation"
    PROTOCOL_VALIDATION = "protocol_validation"
    NONE = "none"


@dataclass
class ToolCallDecision:
    """工具调用决策结果"""

    should_call_tools: bool
    confidence: float
    intent: ToolCallIntent
    suggested_tools: list[str]
    reasoning: str


class ToolCallingOptimizer:
    """工具调用优化器

    基于第一性原理的设计思路：
    1. 意图识别：分析用户输入的真实意图
    2. 上下文理解：结合对话历史和系统状态
    3. 工具匹配：智能匹配最相关的工具
    4. 决策优化：基于置信度和成本效益做决策
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.max_tools_per_call = self.config.get("max_tools_per_call", 5)
        self.logger = logging.getLogger(__name__)

        # 意图识别关键词映射（使用更简单的关键词匹配）
        self.intent_keywords = {
            ToolCallIntent.TASK_MANAGEMENT: [
                "创建",
                "任务",
                "task",
                "todo",
                "项目",
                "进度",
                "分配",
                "删除",
                "更新",
                "查看",
            ],
            ToolCallIntent.DATA_RETRIEVAL: [
                "查询",
                "搜索",
                "获取",
                "读取",
                "检索",
                "数据",
                "报告",
                "文档",
                "wiki",
                "信息",
            ],
            ToolCallIntent.COMPUTATION: [
                "计算",
                "统计",
                "分析",
                "处理",
                "转换",
                "math",
                "算法",
                "公式",
                "共识",
            ],
            ToolCallIntent.COLLABORATION: [
                "协作",
                "讨论",
                "投票",
                "共识",
                "角色",
                "专家",
                "团队",
                "协同",
                "列出",
                "角色",
            ],
            ToolCallIntent.MEMORY_OPERATION: [
                "记住",
                "保存",
                "存储",
                "记录",
                "回忆",
                "memory",
                "记忆",
                "历史",
            ],
            ToolCallIntent.PROTOCOL_VALIDATION: [
                "验证",
                "检查",
                "校验",
                "协议",
                "格式",
                "yaml",
                "json",
                "validate",
            ],
        }

        # 工具能力映射
        self.tool_capabilities = {
            "create_task": [ToolCallIntent.TASK_MANAGEMENT],
            "get_task_info": [
                ToolCallIntent.TASK_MANAGEMENT,
                ToolCallIntent.DATA_RETRIEVAL,
            ],
            "delete_task": [ToolCallIntent.TASK_MANAGEMENT],
            "list_tasks": [
                ToolCallIntent.TASK_MANAGEMENT,
                ToolCallIntent.DATA_RETRIEVAL,
            ],
            "update_task": [ToolCallIntent.TASK_MANAGEMENT],
            "list_roles": [ToolCallIntent.COLLABORATION, ToolCallIntent.DATA_RETRIEVAL],
            "set_active_role": [ToolCallIntent.COLLABORATION],
            "save_role_memory": [
                ToolCallIntent.MEMORY_OPERATION,
                ToolCallIntent.COLLABORATION,
            ],
            "read_role_memory": [
                ToolCallIntent.MEMORY_OPERATION,
                ToolCallIntent.DATA_RETRIEVAL,
            ],
            "read_wiki": [ToolCallIntent.DATA_RETRIEVAL, ToolCallIntent.COLLABORATION],
            "write_wiki": [
                ToolCallIntent.COLLABORATION,
                ToolCallIntent.MEMORY_OPERATION,
            ],
            "edit_wiki": [ToolCallIntent.COLLABORATION],
            "vote_wiki_edit": [ToolCallIntent.COLLABORATION],
            "consensus_calculation": [
                ToolCallIntent.COLLABORATION,
                ToolCallIntent.COMPUTATION,
            ],
            "decompose_task": [
                ToolCallIntent.TASK_MANAGEMENT,
                ToolCallIntent.COMPUTATION,
            ],
            "validate_protocol": [ToolCallIntent.PROTOCOL_VALIDATION],
            "prompt_optimization": [ToolCallIntent.COMPUTATION],
        }

    def analyze_intent(self, user_input: str) -> tuple[ToolCallIntent, float]:
        """分析用户输入的意图"""
        user_input_lower = user_input.lower()
        intent_scores = {}

        for intent, keywords in self.intent_keywords.items():
            score = 0
            matched_keywords = 0

            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    score += 1
                    matched_keywords += 1

            if matched_keywords > 0:
                # 计算匹配度：匹配的关键词数 / 总关键词数
                match_ratio = matched_keywords / len(keywords)
                # 考虑输入长度的影响
                length_factor = min(len(user_input_lower.split()) / 10, 1.0)
                # 综合评分
                intent_scores[intent] = match_ratio * 0.7 + length_factor * 0.3

        if not intent_scores:
            return ToolCallIntent.NONE, 0.0

        # 返回得分最高的意图
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], best_intent[1]

    def suggest_tools_for_intent(
        self,
        intent: ToolCallIntent,
        user_input: str,
    ) -> list[str]:
        """根据意图推荐工具"""
        if intent == ToolCallIntent.NONE:
            return []

        suggested_tools = []
        for tool_name, tool_intents in self.tool_capabilities.items():
            if intent in tool_intents:
                suggested_tools.append(tool_name)

        # 根据用户输入进一步筛选
        filtered_tools = self._filter_tools_by_context(suggested_tools, user_input)

        return filtered_tools[: self.max_tools_per_call]

    def _filter_tools_by_context(self, tools: list[str], user_input: str) -> list[str]:
        """根据上下文进一步筛选工具"""
        user_input_lower = user_input.lower()
        scored_tools = []

        for tool in tools:
            score = 0

            # 基于工具名称的相关性评分
            tool_keywords = tool.split("_")
            for keyword in tool_keywords:
                if keyword in user_input_lower:
                    score += 2

            # 基于特定关键词的评分
            if "create" in tool and any(
                word in user_input_lower for word in ["创建", "新建", "添加", "create", "add"]
            ):
                score += 3
            elif "delete" in tool and any(
                word in user_input_lower for word in ["删除", "移除", "delete", "remove"]
            ):
                score += 3
            elif "update" in tool and any(
                word in user_input_lower for word in ["更新", "修改", "update", "modify"]
            ):
                score += 3
            elif "list" in tool and any(
                word in user_input_lower for word in ["列表", "查看", "显示", "list", "show"]
            ):
                score += 3

            scored_tools.append((tool, score))

        # 按分数排序
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in scored_tools if score > 0]

    def should_use_tools(
        self,
        user_input: str,
        context: dict[str, Any] = None,
    ) -> ToolCallDecision:
        """决策是否应该使用工具

        Args:
        ----
            user_input: 用户输入
            context: 上下文信息（对话历史、系统状态等）

        Returns:
        -------
            ToolCallDecision: 决策结果

        """
        context = context or {}

        # 1. 意图分析
        intent, intent_confidence = self.analyze_intent(user_input)

        # 2. 工具推荐
        suggested_tools = self.suggest_tools_for_intent(intent, user_input)

        # 3. 决策逻辑
        should_call = False
        reasoning = ""

        if intent == ToolCallIntent.NONE:
            reasoning = "未检测到明确的工具调用意图，建议使用对话模式"
        elif intent_confidence < self.confidence_threshold:
            reasoning = f"意图置信度({intent_confidence:.2f})低于阈值({self.confidence_threshold})，不建议调用工具"
        elif not suggested_tools:
            reasoning = f"检测到意图{intent.value}，但没有匹配的工具"
        else:
            should_call = True
            reasoning = f"检测到{intent.value}意图(置信度:{intent_confidence:.2f})，推荐使用工具: {', '.join(suggested_tools)}"

        # 4. 上下文调整
        if context.get("force_tools", False):
            should_call = True
            reasoning += " (强制启用工具调用)"
        elif context.get("disable_tools", False):
            should_call = False
            reasoning += " (工具调用已禁用)"

        return ToolCallDecision(
            should_call_tools=should_call,
            confidence=intent_confidence,
            intent=intent,
            suggested_tools=suggested_tools,
            reasoning=reasoning,
        )

    def optimize_tool_selection(
        self,
        available_tools: list[dict[str, Any]],
        user_input: str,
    ) -> list[dict[str, Any]]:
        """优化工具选择

        Args:
        ----
            available_tools: 可用工具列表
            user_input: 用户输入

        Returns:
        -------
            优化后的工具列表

        """
        decision = self.should_use_tools(user_input)

        if not decision.should_call_tools:
            return []

        # 筛选推荐的工具
        optimized_tools = []
        suggested_names = set(decision.suggested_tools)

        for tool in available_tools:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name in suggested_names:
                optimized_tools.append(tool)

        self.logger.info(f"工具选择优化: {len(available_tools)} -> {len(optimized_tools)}")
        self.logger.info(f"决策理由: {decision.reasoning}")

        return optimized_tools
