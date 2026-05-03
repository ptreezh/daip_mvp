"""
增强的连续对话上下文感知意图识别器

核心功能：
1. 维护对话历史和上下文状态
2. 支持槽位逐步填充
3. 智能参数补全和推导
4. 上下文感知的意图识别和澄清
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# 导入现有组件
from daip_live.agent_engine.enhanced_intent_recognizer import Intent, IntentType, EnhancedIntentRecognizer
try:
    from .context_manager import ContextManager
    from .session_state import SessionState
    from .task_context import TaskContext
except ImportError:
    try:
        from daip_live.intent_recognition.context_manager import ContextManager
        from daip_live.intent_recognition.session_state import SessionState
        from daip_live.intent_recognition.task_context import TaskContext
    except ImportError:
        try:
            # 使用备用导入路径
            from src.daip_live.intent_recognition.context_manager import ContextManager
            from src.daip_live.intent_recognition.session_state import SessionState
            from src.daip_live.intent_recognition.task_context import TaskContext
        except ImportError:
            # 最后的备用路径
            from ..intent_recognition.context_manager import ContextManager
            from ..intent_recognition.session_state import SessionState
            from ..intent_recognition.task_context import TaskContext


class DialogueStrategy(Enum):
    """对话策略枚举"""
    SLOT_FILLING = "slot_filling"      # 槽位填充策略
    CLARIFICATION = "clarification"       # 澄清策略
    CONTEXT_INFERENCE = "context_inference"  # 上下文推导策略
    HYBRID = "hybrid"                   # 混合策略


@dataclass
class ConversationTurn:
    """对话轮次数据结构"""
    user_input: str
    intent: Optional[Intent] = None
    extracted_params: Dict[str, Any] = field(default_factory=dict)
    missing_params: List[str] = field(default_factory=list)
    filled_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    strategy_used: Optional[DialogueStrategy] = None
    context_summary: str = ""


@dataclass
class ContextualIntent:
    """上下文增强的意图结果"""
    intent: Intent
    conversation_context: Dict[str, Any]
    missing_slots: List[str] = field(default_factory=list)
    filled_slots: Dict[str, Any] = field(default_factory=dict)
    inferred_params: Dict[str, Any] = field(default_factory=dict)
    clarification_needed: bool = False
    clarification_message: str = ""
    next_step: str = ""  # 下一步行动建议
    confidence_boost: float = 0.0  # 基于上下文的置信度提升

    @property
    def name(self):
        """通过属性访问intent的name"""
        return self.intent.name if self.intent else "unknown"

    @property
    def confidence(self):
        """通过属性访问intent的confidence"""
        return self.intent.confidence if self.intent else 0.0

    @property
    def parameters(self):
        """通过属性访问intent的parameters"""
        return self.intent.parameters if self.intent else {}

    @property
    def tool_name(self):
        """通过属性访问intent的tool_name"""
        return self.intent.tool_name if self.intent else None

    @property
    def description(self):
        """通过属性访问intent的description"""
        return self.intent.description if self.intent else ""

    @property
    def intent_type(self):
        """通过属性访问intent的intent_type"""
        return self.intent.intent_type if self.intent else None

    @property
    def requires_confidence_check(self):
        """通过属性访问intent的requires_confidence_check"""
        return self.intent.requires_confidence_check if self.intent else False


class ContextualIntentRecognizer:
    """
    上下文感知意图识别器

    核心能力：
    1. 多轮对话意图追踪
    2. 槽位逐步填充
    3. 上下文参数推导
    4. 智能澄清生成
    """

    def __init__(self, base_recognizer: EnhancedIntentRecognizer = None):
        self.base_recognizer = base_recognizer or EnhancedIntentRecognizer()
        self.context_manager = ContextManager()

        # 对话状态管理
        self.conversation_sessions: Dict[str, List[ConversationTurn]] = {}
        self.session_last_activity: Dict[str, datetime] = {}

        # 意图-参数映射（用于槽位填充）
        self.intent_parameter_schema = self._initialize_parameter_schemas()

        # 上下文推导规则
        self.inference_rules = self._initialize_inference_rules()

        # 会话超时设置（分钟）
        self.session_timeout = 60

        # 常见澄清模板
        self.clarification_templates = self._initialize_clarification_templates()

    def recognize_intent(self, user_input: str, session_id: str = "default") -> ContextualIntent:
        """
        识别用户意图，考虑对话上下文

        Args:
            user_input: 用户输入
            session_id: 会话ID

        Returns:
            ContextualIntent: 上下文增强的意图识别结果
        """
        # 清理过期会话
        self._cleanup_expired_sessions()

        # 获取或创建会话历史
        if session_id not in self.conversation_sessions:
            self.conversation_sessions[session_id] = []

        session_history = self.conversation_sessions[session_id]

        # 步骤1: 基础意图识别
        base_intent = self.base_recognizer.recognize_intent(user_input, session_id)

        # 步骤2: 上下文分析
        context_analysis = self._analyze_conversation_context(user_input, session_id, session_history)

        # 步骤3: 槽位填充和参数提取
        filled_params, missing_params = self._extract_and_fill_parameters(
            user_input, base_intent, session_id, session_history
        )

        # 步骤4: 上下文推导
        inferred_params = self._infer_missing_parameters(
            user_input, base_intent, session_id, session_history, filled_params, missing_params
        )

        # 步骤5: 更新缺失参数列表
        missing_params = [p for p in missing_params if p not in inferred_params]

        # 步骤6: 置信度计算
        confidence_boost = self._calculate_context_confidence_boost(
            base_intent, filled_params, inferred_params, session_history
        )

        # 步骤7: 生成澄清和下一步建议
        clarification_needed, clarification_message, next_step = self._generate_clarification(
            base_intent, missing_params, filled_params, inferred_params, session_history
        )

        # 步骤8: 创建上下文增强意图
        contextual_intent = ContextualIntent(
            intent=base_intent,
            conversation_context=context_analysis,
            missing_slots=missing_params,
            filled_slots=filled_params,
            inferred_params=inferred_params,
            clarification_needed=clarification_needed,
            clarification_message=clarification_message,
            next_step=next_step,
            confidence_boost=confidence_boost
        )

        # 步骤9: 更新会话历史
        self._update_conversation_history(session_id, user_input, contextual_intent)

        # 步骤10: 更新上下文管理器
        self._update_context_manager(session_id, contextual_intent)

        return contextual_intent

    def _analyze_conversation_context(self, user_input: str, session_id: str,
                                   history: List[ConversationTurn]) -> Dict[str, Any]:
        """分析对话上下文"""
        context = {
            "session_id": session_id,
            "current_turn": len(history) + 1,
            "has_active_task": self.context_manager.is_in_task(session_id),
            "active_task_context": self.context_manager.get_context(session_id),
            "recent_intents": [],
            "recent_parameters": {},
            "conversation_flow": "continuation" if history else "initiation",
            "time_since_last_turn": self._calculate_time_since_last_turn(session_id),
            "topic_continuity": self._analyze_topic_continuity(user_input, history)
        }

        # 分析最近的意图模式
        if history:
            recent_turns = history[-3:]  # 最近3轮对话
            context["recent_intents"] = [turn.intent.name for turn in recent_turns if turn.intent]
            context["recent_parameters"] = {
                param: value
                for turn in recent_turns
                for param, value in turn.filled_params.items()
            }

        return context

    def _extract_and_fill_parameters(self, user_input: str, intent: Intent,
                                   session_id: str, history: List[ConversationTurn]) -> Tuple[Dict[str, Any], List[str]]:
        """提取并填充参数"""
        # 获取意图的参数模式
        if not intent or intent.name not in self.intent_parameter_schema:
            return {}, []

        schema = self.intent_parameter_schema[intent.name]
        required_params = schema.get("required", [])
        optional_params = schema.get("optional", [])

        filled_params = {}
        missing_params = []

        # 从基础意图参数开始
        if intent and intent.parameters:
            filled_params.update(intent.parameters)

        # 分析用户输入中的参数信息
        extracted_params = self._extract_parameters_from_input(user_input, intent, schema)
        filled_params.update(extracted_params)

        # 检查历史对话中的参数
        historical_params = self._extract_historical_parameters(user_input, intent, history, schema)
        filled_params.update(historical_params)

        # 确定缺失参数
        for param in required_params:
            if param not in filled_params:
                missing_params.append(param)

        return filled_params, missing_params

    def _extract_parameters_from_input(self, user_input: str, intent: Intent, schema: Dict[str, Any]) -> Dict[str, Any]:
        """从用户输入中提取参数"""
        params = {}

        # 使用正则表达式提取特定参数
        if intent and intent.name in schema:
            extraction_patterns = schema.get("extraction_patterns", {})

            for param_name, patterns in extraction_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match:
                        if match.groups():
                            params[param_name] = match.group(1).strip()
                        else:
                            params[param_name] = match.group(0).strip()
                        break

        return params

    def _extract_historical_parameters(self, user_input: str, intent: Intent,
                                   history: List[ConversationTurn], schema: Dict[str, Any]) -> Dict[str, Any]:
        """从历史对话中提取参数"""
        historical_params = {}

        if not history:
            return historical_params

        # 查找最近的相同意图或相关意图的对话
        recent_relevant_turns = []
        for turn in reversed(history[-5:]):  # 最近5轮
            if turn.intent and (
                turn.intent.name == intent.name or
                self._are_intents_related(turn.intent.name, intent.name)
            ):
                recent_relevant_turns.append(turn)

        # 提取相关参数
        for turn in recent_relevant_turns:
            for param_name, param_value in turn.filled_params.items():
                if param_name in schema.get("required", []) + schema.get("optional", []):
                    historical_params[param_name] = param_value

        return historical_params

    def _infer_missing_parameters(self, user_input: str, intent: Intent, session_id: str,
                               history: List[ConversationTurn], filled_params: Dict[str, Any],
                               missing_params: List[str]) -> Dict[str, Any]:
        """推导缺失的参数"""
        inferred = {}

        if not intent or not missing_params:
            return inferred

        # 应用推导规则
        for param in missing_params:
            if intent.name in self.inference_rules and param in self.inference_rules[intent.name]:
                rule = self.inference_rules[intent.name][param]

                # 基于上下文的推导
                if rule["type"] == "context":
                    context_value = self._infer_from_context(param, session_id, history, filled_params)
                    if context_value:
                        inferred[param] = context_value

                # 基于对话历史的推导
                elif rule["type"] == "history":
                    history_value = self._infer_from_history(param, intent, history)
                    if history_value:
                        inferred[param] = history_value

                # 基于输入内容的推导
                elif rule["type"] == "content":
                    content_value = self._infer_from_content(param, user_input, filled_params)
                    if content_value:
                        inferred[param] = content_value

        return inferred

    def _infer_from_context(self, param: str, session_id: str, history: List[ConversationTurn],
                           filled_params: Dict[str, Any]) -> Optional[Any]:
        """从上下文推导参数"""
        # 获取活跃任务上下文
        task_context = self.context_manager.get_context(session_id)
        if not task_context:
            return None

        # 检查任务上下文中的参数
        if param == "title" and "topic" in task_context.get("parameters", {}):
            return task_context["parameters"]["topic"]

        # 检查最近对话中的主题
        if history and param in ["topic", "title", "query"]:
            recent_topics = [turn.filled_params.get("topic") or turn.filled_params.get("title")
                           for turn in history[-3:]]
            recent_topics = [t for t in recent_topics if t]
            if recent_topics:
                # 返回最近提到的主题
                return recent_topics[-1]

        return None

    def _infer_from_history(self, param: str, intent: Intent, history: List[ConversationTurn]) -> Optional[Any]:
        """从历史对话推导参数"""
        if not history:
            return None

        # 查找相同意图的历史参数
        for turn in reversed(history[-3:]):
            if turn.intent and turn.intent.name == intent.name:
                if param in turn.filled_params:
                    return turn.filled_params[param]

        return None

    def _infer_from_content(self, param: str, user_input: str, filled_params: Dict[str, Any]) -> Optional[Any]:
        """从用户输入内容推导参数"""
        # 基于关键词的推导
        if param == "rounds" and any(word in user_input.lower() for word in ["轮", "round", "次"]):
            # 尝试提取数字
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                return int(numbers[0])

        # 如果用户提到"辩论"但没有指定轮数，默认3轮
        if param == "rounds" and "辩论" in user_input:
            return 3

        return None

    def _calculate_context_confidence_boost(self, intent: Intent, filled_params: Dict[str, Any],
                                       inferred_params: Dict[str, Any], history: List[ConversationTurn]) -> float:
        """计算基于上下文的置信度提升"""
        boost = 0.0

        if not intent:
            return boost

        # 基础意图置信度
        base_confidence = intent.confidence if hasattr(intent, 'confidence') else 0.0

        # 参数完整性提升
        if intent.name in self.intent_parameter_schema:
            schema = self.intent_parameter_schema[intent.name]
            required_count = len(schema.get("required", []))
            filled_count = len([p for p in schema.get("required", []) if p in filled_params or p in inferred_params])

            if required_count > 0:
                completeness_ratio = filled_count / required_count
                boost += completeness_ratio * 0.2  # 最多提升0.2

        # 话题一致性提升
        if history and history[-1].intent:
            if self._are_intents_related(intent.name, history[-1].intent.name):
                boost += 0.1  # 话题一致，提升0.1

        # 推导参数提升
        boost += len(inferred_params) * 0.05  # 每个推导参数提升0.05

        return min(boost, 0.5)  # 最多提升0.5

    def _generate_clarification(self, intent: Intent, missing_params: List[str],
                              filled_params: Dict[str, Any], inferred_params: Dict[str, Any],
                              history: List[ConversationTurn]) -> Tuple[bool, str, str]:
        """生成澄清和下一步建议"""
        if not intent or not missing_params:
            return False, "", self._generate_next_step(intent, filled_params, inferred_params)

        # 选择澄清策略
        if len(missing_params) == 1:
            # 单个参数缺失，直接询问
            param = missing_params[0]
            clarification = self._generate_single_param_clarification(param, intent, filled_params)
            next_step = f"等待用户提供{param}参数"
        else:
            # 多个参数缺失，询问所有
            clarification = self._generate_multi_param_clarification(missing_params, intent)
            next_step = "等待用户提供缺失的参数"

        return True, clarification, next_step

    def _generate_single_param_clarification(self, param: str, intent: Intent, filled_params: Dict[str, Any]) -> str:
        """生成单个参数的澄清"""
        templates = self.clarification_templates.get(intent.name, {}).get(param, [])

        if templates:
            # 选择最合适的模板
            template = templates[0]  # 可以基于上下文选择更好的模板

            # 替换模板中的变量
            if "{filled_params}" in template:
                filled_summary = ", ".join([f"{k}: {v}" for k, v in filled_params.items()])
                template = template.replace("{filled_params}", filled_summary)

            return template

        # 默认澄清
        return f"请提供{param}参数"

    def _generate_multi_param_clarification(self, missing_params: List[str], intent: Intent) -> str:
        """生成多个参数的澄清"""
        if intent.name in self.clarification_templates:
            multi_template = self.clarification_templates[intent.name].get("multi", "")
            if multi_template:
                return multi_template.format(params=", ".join(missing_params))

        return f"请提供以下参数：{', '.join(missing_params)}"

    def _generate_next_step(self, intent: Intent, filled_params: Dict[str, Any],
                          inferred_params: Dict[str, Any]) -> str:
        """生成下一步行动建议"""
        if not intent:
            return "请提供更具体的指令"

        # 合并所有参数
        all_params = {**filled_params, **inferred_params}

        # 基于意图类型生成下一步建议
        if intent.name == "start_debate":
            topic = all_params.get("topic", "未指定主题")
            rounds = all_params.get("rounds", 3)
            return f"准备开始关于'{topic}'的辩论，共{rounds}轮"

        elif intent.name == "create_wiki":
            title = all_params.get("title", "未指定标题")
            return f"准备创建维基页面：{title}"

        elif intent.name == "search_papers":
            query = all_params.get("query", "未指定查询")
            return f"准备搜索论文：{query}"

        elif intent.name == "download_paper":
            if all_params.get("paper_id"):
                return f"准备下载论文：{all_params['paper_id']}"
            else:
                query = all_params.get("search_query", "未指定查询")
                return f"准备搜索并下载论文：{query}"

        elif intent.name == "execute_skill":
            skill_type = all_params.get("target_skill", "通用技能")
            content = all_params.get("content", "未指定内容")
            return f"准备执行{skill_type}技能：{content}"

        return "继续处理您的请求"

    def _update_conversation_history(self, session_id: str, user_input: str,
                                  contextual_intent: ContextualIntent):
        """更新对话历史"""
        # 修复timedelta对象不能JSON序列化的问题
        import datetime
        safe_context = {}
        for key, value in contextual_intent.conversation_context.items():
            if isinstance(value, datetime.timedelta):
                safe_context[key] = str(value)
            else:
                safe_context[key] = value

        turn = ConversationTurn(
            user_input=user_input,
            intent=contextual_intent.intent,
            extracted_params=contextual_intent.intent.parameters if contextual_intent.intent else {},
            missing_params=contextual_intent.missing_slots,
            filled_params={**contextual_intent.filled_slots, **contextual_intent.inferred_params},
            strategy_used=self._determine_strategy(contextual_intent),
            context_summary=json.dumps(safe_context, ensure_ascii=False, default=str)
        )

        self.conversation_sessions[session_id].append(turn)
        self.session_last_activity[session_id] = datetime.datetime.now()

    def _update_context_manager(self, session_id: str, contextual_intent: ContextualIntent):
        """更新上下文管理器"""
        if contextual_intent.intent and contextual_intent.intent.name in self.intent_parameter_schema:
            # 如果有活跃任务，更新任务参数
            if self.context_manager.is_in_task(session_id):
                for param, value in contextual_intent.filled_slots.items():
                    self.context_manager.add_task_parameter(session_id, param, value)

                for param, value in contextual_intent.inferred_params.items():
                    self.context_manager.add_task_parameter(session_id, param, value)

    def _determine_strategy(self, contextual_intent: ContextualIntent) -> DialogueStrategy:
        """确定使用的对话策略"""
        if contextual_intent.clarification_needed:
            return DialogueStrategy.CLARIFICATION
        elif contextual_intent.inferred_params:
            return DialogueStrategy.CONTEXT_INFERENCE
        elif contextual_intent.missing_slots:
            return DialogueStrategy.SLOT_FILLING
        else:
            return DialogueStrategy.HYBRID

    def _are_intents_related(self, intent1: str, intent2: str) -> bool:
        """判断两个意图是否相关"""
        # 定义意图相关性映射
        related_groups = [
            {"start_debate", "view_debate_history", "view_specific_debate"},
            {"create_wiki", "knowledge_search"},
            {"search_papers", "download_paper"},
            {"execute_skill", "personal_assistant"},
            {"complex_task", "execute_skill"}
        ]

        for group in related_groups:
            if intent1 in group and intent2 in group:
                return True

        return False

    def _calculate_time_since_last_turn(self, session_id: str) -> Optional[timedelta]:
        """计算距离上次对话的时间"""
        if session_id not in self.session_last_activity:
            return None

        return datetime.now() - self.session_last_activity[session_id]

    def _analyze_topic_continuity(self, user_input: str, history: List[ConversationTurn]) -> str:
        """分析话题连续性"""
        if not history:
            return "new_topic"

        # 简单的关键词重叠分析
        current_words = set(re.findall(r'\w+', user_input.lower()))

        recent_turns = history[-3:]
        for turn in recent_turns:
            past_words = set(re.findall(r'\w+', turn.user_input.lower()))
            overlap = len(current_words & past_words)

            if overlap > 0 and overlap / max(len(current_words), len(past_words)) > 0.3:
                return "continuation"

        return "new_topic"

    def _cleanup_expired_sessions(self):
        """清理过期会话"""
        now = datetime.now()
        expired_sessions = []

        for session_id, last_activity in self.session_last_activity.items():
            if now - last_activity > timedelta(minutes=self.session_timeout):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.conversation_sessions[session_id]
            del self.session_last_activity[session_id]
            self.context_manager.clear_context(session_id)

    def get_conversation_history(self, session_id: str) -> List[ConversationTurn]:
        """获取对话历史"""
        return self.conversation_sessions.get(session_id, [])

    def clear_session_history(self, session_id: str):
        """清除会话历史"""
        if session_id in self.conversation_sessions:
            del self.conversation_sessions[session_id]
        if session_id in self.session_last_activity:
            del self.session_last_activity[session_id]
        self.context_manager.clear_context(session_id)

    def _initialize_parameter_schemas(self) -> Dict[str, Dict[str, Any]]:
        """初始化意图参数模式"""
        return {
            "start_debate": {
                "required": ["topic"],
                "optional": ["rounds", "roles"],
                "extraction_patterns": {
                    "topic": [
                        r"辩论\s*[:：]\s*(.+)",
                        r"关于\s*(.+?)\s*的辩论",
                        r"辩论\s*(.+)$",
                        r"(.+?)\s*辩论"
                    ],
                    "rounds": [
                        r"(\d+)\s*轮",
                        r"轮\s*(\d+)",
                        r"rounds?\s*(\d+)"
                    ]
                }
            },
            "create_wiki": {
                "required": ["title"],
                "optional": ["content", "tags"],
                "extraction_patterns": {
                    "title": [
                        r"创建.*?[维基|wiki|百科|词条]\s*[:：]\s*(.+)",
                        r"[维基|wiki|百科|词条]\s*[:：]\s*(.+)",
                        r"创建\s*(.+?)\s*[维基|wiki|百科|词条]",
                        r"(.+?)\s*[维基|wiki|百科|词条]"
                    ]
                }
            },
            "search_papers": {
                "required": ["query"],
                "optional": ["max_results", "source"],
                "extraction_patterns": {
                    "query": [
                        r"搜索.*?[论文|paper]\s*[:：]\s*(.+)",
                        r"[论文|paper]\s*[:：]\s*(.+)",
                        r"搜索\s*(.+?)\s*[论文|paper]",
                        r"(.+?)\s*[论文|paper]"
                    ]
                }
            },
            "download_paper": {
                "required": [],  # 可以是paper_id或search_query
                "optional": ["paper_id", "search_query"],
                "extraction_patterns": {
                    "paper_id": [
                        r"(\d{4}\.\d{4,5}(v\d+)?)",
                        r"arxiv\s*[:：]\s*(\d{4}\.\d{4,5}(v\d+)?)"
                    ],
                    "search_query": [
                        r"下载.*?[论文|paper]\s*[:：]\s*(.+)",
                        r"(.+?)\s*[论文|paper]"
                    ]
                }
            },
            "execute_skill": {
                "required": ["content"],
                "optional": ["target_skill", "skill_type"],
                "extraction_patterns": {
                    "content": [
                        r"[帮我|请帮我]\s*(.+)",
                        r"分析\s*(.+)",
                        r"处理\s*(.+)",
                        r"搜索\s*(.+)",
                        r"总结\s*(.+)",
                        r"(.+)"
                    ]
                }
            }
        }

    def _initialize_inference_rules(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """初始化推导规则"""
        return {
            "start_debate": {
                "rounds": {
                    "type": "content",
                    "default": 3
                },
                "topic": {
                    "type": "context",
                    "sources": ["history", "current_input"]
                }
            },
            "create_wiki": {
                "title": {
                    "type": "context",
                    "sources": ["history", "current_input"]
                }
            },
            "search_papers": {
                "query": {
                    "type": "content",
                    "sources": ["current_input"]
                }
            },
            "execute_skill": {
                "content": {
                    "type": "content",
                    "sources": ["current_input"]
                }
            }
        }

    def _initialize_clarification_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """初始化澄清模板"""
        return {
            "start_debate": {
                "topic": [
                    "请告诉我您想辩论的主题是什么？",
                    "您希望辩论什么话题？",
                    "请提供辩论的具体主题"
                ],
                "multi": "请提供辩论主题和轮数（可选，默认3轮）"
            },
            "create_wiki": {
                "title": [
                    "请告诉我您想创建的维基页面标题？",
                    "您希望创建什么主题的维基页面？",
                    "请提供维基页面的标题"
                ],
                "multi": "请提供维基页面的标题和内容（可选）"
            },
            "search_papers": {
                "query": [
                    "请告诉我您想搜索什么主题的论文？",
                    "您希望搜索哪个领域的论文？",
                    "请提供搜索关键词"
                ],
                "multi": "请提供搜索关键词和其他搜索参数"
            },
            "download_paper": {
                "paper_id": [
                    "请提供论文的arXiv ID（如：1234.56789）",
                    "请提供您想下载的论文ID"
                ],
                "search_query": [
                    "请告诉我您想下载什么主题的论文？",
                    "请提供论文的标题或搜索关键词"
                ],
                "multi": "请提供论文ID或搜索关键词"
            },
            "execute_skill": {
                "content": [
                    "请告诉我您想处理什么内容？",
                    "您希望我分析什么内容？",
                    "请提供要处理的具体内容"
                ],
                "multi": "请提供要处理的内容和技能类型（可选）"
            }
        }