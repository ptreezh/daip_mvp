"""
增强的上下文管理器

扩展原有ContextManager功能，提供：
1. 智能会话状态管理
2. 参数继承和推导
3. 上下文持久化
4. 会话生命周期管理
"""

import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from .context_manager import ContextManager
    from .session_state import SessionState
    from .task_context import TaskContext
    from .contextual_intent_recognizer import ConversationTurn, ContextualIntent
except ImportError:
    from daip_live.intent_recognition.context_manager import ContextManager
    from daip_live.intent_recognition.session_state import SessionState
    from daip_live.intent_recognition.task_context import TaskContext
    from daip_live.intent_recognition.contextual_intent_recognizer import ConversationTurn, ContextualIntent


class SessionStatus(Enum):
    """会话状态枚举"""
    ACTIVE = "active"           # 活跃中
    IDLE = "idle"             # 空闲
    COMPLETED = "completed"     # 已完成
    TIMEOUT = "timeout"         # 超时
    ERROR = "error"             # 错误状态


class ParameterSource(Enum):
    """参数来源枚举"""
    USER_INPUT = "user_input"           # 用户直接输入
    CONTEXT_INHERIT = "context_inherit"  # 从上下文继承
    INFERENCE = "inference"             # 推导得出
    DEFAULT = "default"                 # 默认值
    HISTORICAL = "historical"          # 历史记录


@dataclass
class ParameterMetadata:
    """参数元数据"""
    value: Any
    source: ParameterSource
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    context: str = ""


@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str
    topic: str = ""
    current_intent: str = ""
    intent_history: List[str] = field(default_factory=list)
    parameters: Dict[str, ParameterMetadata] = field(default_factory=dict)
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    timeout_minutes: int = 30
    related_entities: Set[str] = field(default_factory=set)
    conversation_summary: str = ""

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return datetime.now() - self.last_accessed > timedelta(minutes=self.timeout_minutes)

    def update_access(self):
        """更新访问时间"""
        self.last_accessed = datetime.now()

    def get_parameter(self, param_name: str) -> Optional[ParameterMetadata]:
        """获取参数元数据"""
        return self.parameters.get(param_name)

    def set_parameter(self, param_name: str, value: Any, source: ParameterSource,
                     confidence: float = 1.0, context: str = ""):
        """设置参数"""
        self.parameters[param_name] = ParameterMetadata(
            value=value, source=source, confidence=confidence, context=context
        )
        self.update_access()

    def get_filled_parameters(self) -> Dict[str, Any]:
        """获取已填充的参数值"""
        return {name: meta.value for name, meta in self.parameters.items()}

    def get_parameter_value(self, param_name: str) -> Optional[Any]:
        """获取参数值"""
        meta = self.get_parameter(param_name)
        return meta.value if meta else None


class EnhancedContextManager:
    """
    增强的上下文管理器

    扩展原有功能，提供更智能的上下文管理
    """

    def __init__(self, base_manager: Optional[ContextManager] = None):
        # 继承原有上下文管理器
        self.base_manager = base_manager or ContextManager()

        # 增强的上下文存储
        self.conversation_contexts: Dict[str, ConversationContext] = {}

        # 上下文继承规则
        self.inheritance_rules = self._initialize_inheritance_rules()

        # 会话清理配置
        self.cleanup_interval_minutes = 10
        self.default_timeout_minutes = 30

        # 上下文缓存
        self.context_cache: Dict[str, Dict[str, Any]] = {}

    def create_conversation_context(self, session_id: str, intent: Optional[str] = None,
                                topic: str = "", timeout_minutes: Optional[int] = None) -> ConversationContext:
        """创建新的对话上下文"""
        context = ConversationContext(
            session_id=session_id,
            topic=topic,
            current_intent=intent or "",
            timeout_minutes=timeout_minutes or self.default_timeout_minutes
        )

        if intent:
            context.intent_history.append(intent)

        self.conversation_contexts[session_id] = context
        return context

    def get_conversation_context(self, session_id: str) -> Optional[ConversationContext]:
        """获取对话上下文"""
        context = self.conversation_contexts.get(session_id)
        if context:
            if context.is_expired():
                context.status = SessionStatus.TIMEOUT
            else:
                context.update_access()
        return context

    def update_conversation_context(self, session_id: str, intent: ContextualIntent):
        """更新对话上下文"""
        context = self.get_conversation_context(session_id)
        if not context:
            # 创建新的上下文
            topic = intent.filled_slots.get("topic", "") or intent.inferred_params.get("topic", "")
            context = self.create_conversation_context(session_id, intent.intent.name if intent.intent else "", topic)

        # 更新当前意图
        if intent.intent:
            context.current_intent = intent.intent.name
            if not context.intent_history or context.intent_history[-1] != intent.intent.name:
                context.intent_history.append(intent.intent.name)

        # 更新主题
        for topic_key in ["topic", "title", "query"]:
            if topic_key in intent.filled_slots:
                context.topic = str(intent.filled_slots[topic_key])
                break
            elif topic_key in intent.inferred_params:
                context.topic = str(intent.inferred_params[topic_key])
                break

        # 更新参数
        for param_name, param_value in intent.filled_slots.items():
            context.set_parameter(param_name, param_value, ParameterSource.USER_INPUT)

        for param_name, param_value in intent.inferred_params.items():
            context.set_parameter(param_name, param_value, ParameterSource.INFERENCE, confidence=0.8)

        # 同步到基础管理器
        self._sync_to_base_manager(session_id, intent)

    def add_parameter_with_source(self, session_id: str, param_name: str, param_value: Any,
                                source: ParameterSource = ParameterSource.USER_INPUT,
                                confidence: float = 1.0, context: str = "") -> bool:
        """添加带来源信息的参数"""
        conversation_context = self.get_conversation_context(session_id)
        if not conversation_context:
            return False

        conversation_context.set_parameter(param_name, param_value, source, confidence, context)

        # 同步到基础管理器
        if self.base_manager.is_in_task(session_id):
            self.base_manager.add_task_parameter(session_id, param_name, param_value)

        return True

    def get_parameter_with_metadata(self, session_id: str, param_name: str) -> Optional[ParameterMetadata]:
        """获取带元数据的参数"""
        context = self.get_conversation_context(session_id)
        if context:
            return context.get_parameter(param_name)
        return None

    def inherit_parameters(self, session_id: str, target_intent: str,
                          required_params: List[str]) -> Dict[str, Any]:
        """从上下文继承参数"""
        inherited = {}
        context = self.get_conversation_context(session_id)

        if not context:
            return inherited

        # 应用继承规则
        for param in required_params:
            # 检查当前上下文是否已有该参数
            existing_meta = context.get_parameter(param)
            if existing_meta:
                inherited[param] = existing_meta.value
                continue

            # 应用继承规则
            if target_intent in self.inheritance_rules:
                rules = self.inheritance_rules[target_intent]
                if param in rules:
                    inheritance_rule = rules[param]

                    # 从历史意图继承
                    if "from_intent" in inheritance_rule:
                        source_intent = inheritance_rule["from_intent"]
                        if source_intent in context.intent_history:
                            # 查找历史上下文中的参数
                            inherited_value = self._find_historical_parameter(session_id, source_intent, param)
                            if inherited_value is not None:
                                inherited[param] = inherited_value
                                context.set_parameter(param, inherited_value, ParameterSource.CONTEXT_INHERIT)
                                continue

                    # 从相关参数继承
                    if "from_param" in inheritance_rule:
                        source_param = inheritance_rule["from_param"]
                        source_meta = context.get_parameter(source_param)
                        if source_meta:
                            inherited_value = self._transform_parameter(source_meta.value, param, inheritance_rule)
                            if inherited_value is not None:
                                inherited[param] = inherited_value
                                context.set_parameter(param, inherited_value, ParameterSource.CONTEXT_INHERIT)
                                continue

                    # 使用默认值
                    if "default" in inheritance_rule:
                        default_value = inheritance_rule["default"]
                        inherited[param] = default_value
                        context.set_parameter(param, default_value, ParameterSource.DEFAULT)

        return inherited

    def _find_historical_parameter(self, session_id: str, intent_name: str, param_name: str) -> Optional[Any]:
        """查找历史参数"""
        context = self.get_conversation_context(session_id)
        if not context:
            return None

        # 查找历史意图对应的参数
        # 这里需要扩展SessionState来支持历史参数查询
        if hasattr(self.base_manager, 'get_session_state'):
            session_state = self.base_manager.get_session_state(session_id)
            if session_state and hasattr(session_state, 'history'):
                for entry in reversed(session_state.history[-5:]):  # 查找最近5条
                    if isinstance(entry, dict) and entry.get('intent') == intent_name:
                        if 'parameters' in entry and param_name in entry['parameters']:
                            return entry['parameters'][param_name]

        return None

    def _transform_parameter(self, source_value: Any, target_param: str, rule: Dict[str, Any]) -> Any:
        """参数转换"""
        if "transform" in rule:
            transform_type = rule["transform"]

            if transform_type == "identity":
                return source_value
            elif transform_type == "string":
                return str(source_value)
            elif transform_type == "upper":
                return str(source_value).upper()
            elif transform_type == "lower":
                return str(source_value).lower()
            elif transform_type == "int":
                try:
                    return int(source_value)
                except (ValueError, TypeError):
                    return None
            elif transform_type == "default_if_none":
                return source_value if source_value is not None else rule.get("default_value")

        return source_value

    def _sync_to_base_manager(self, session_id: str, intent: ContextualIntent):
        """同步到基础上下文管理器"""
        if intent.intent and intent.intent.name:
            # 设置或更新任务上下文
            context_data = {
                "task_type": intent.intent.name,
                "required_params": intent.missing_slots,
                "filled_params": {**intent.filled_slots, **intent.inferred_params}
            }

            # 如果基础管理器中没有任务，创建新任务
            if not self.base_manager.is_in_task(session_id):
                self.base_manager.set_context(session_id, context_data)

            # 添加所有已填充的参数
            for param_name, param_value in intent.filled_slots.items():
                self.base_manager.add_task_parameter(session_id, param_name, param_value)

            for param_name, param_value in intent.inferred_params.items():
                self.base_manager.add_task_parameter(session_id, param_name, param_value)

    def is_in_task(self, session_id: str) -> bool:
        """检查会话是否在任务中"""
        # 基础管理器检查
        base_check = self.base_manager.is_in_task(session_id)

        # 增强上下文检查
        context = self.get_conversation_context(session_id)
        if context:
            return base_check or (context.current_intent != "" and context.status == SessionStatus.ACTIVE)

        return base_check

    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话上下文（兼容原接口）"""
        # 首先尝试从基础管理器获取
        base_context = self.base_manager.get_context(session_id)
        if base_context:
            return base_context

        # 从增强上下文获取
        context = self.get_conversation_context(session_id)
        if context:
            return {
                "task_type": context.current_intent,
                "parameters": context.get_filled_parameters(),
                "required_params": [],  # 需要从意图模式中获取
                "filled_params": context.get_filled_parameters(),
                "status": context.status.value,
                "topic": context.topic,
                "intent_history": context.intent_history,
                "conversation_summary": context.conversation_summary
            }

        return None

    def clear_context(self, session_id: str):
        """清除会话上下文"""
        # 清除基础管理器上下文
        self.base_manager.clear_context(session_id)

        # 清除增强上下文
        if session_id in self.conversation_contexts:
            del self.conversation_contexts[session_id]

    def add_task_parameter(self, session_id: str, param_name: str, param_value: Any) -> bool:
        """添加任务参数（兼容原接口）"""
        # 添加到增强上下文
        success = self.add_parameter_with_source(session_id, param_name, param_value, ParameterSource.USER_INPUT)

        # 添加到基础管理器
        if self.base_manager.is_in_task(session_id):
            return self.base_manager.add_task_parameter(session_id, param_name, param_value)

        return success

    def get_session_state(self, session_id: str) -> Optional[SessionState]:
        """获取会话状态（兼容原接口）"""
        return self.base_manager.get_session_state(session_id)

    def cleanup_expired_contexts(self):
        """清理过期的上下文"""
        expired_sessions = []
        for session_id, context in self.conversation_contexts.items():
            if context.is_expired():
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self.clear_context(session_id)

    def get_conversation_summary(self, session_id: str) -> str:
        """获取对话摘要"""
        context = self.get_conversation_context(session_id)
        if context:
            if context.conversation_summary:
                return context.conversation_summary

            # 生成基本摘要
            if context.topic and context.current_intent:
                return f"关于'{context.topic}'的{context.current_intent}对话"
            elif context.current_intent:
                return f"{context.current_intent}对话"
            elif context.topic:
                return f"关于'{context.topic}'的对话"

        return ""

    def update_conversation_summary(self, session_id: str, summary: str):
        """更新对话摘要"""
        context = self.get_conversation_context(session_id)
        if context:
            context.conversation_summary = summary
            context.update_access()

    def get_related_entities(self, session_id: str) -> Set[str]:
        """获取相关实体"""
        context = self.get_conversation_context(session_id)
        return context.related_entities if context else set()

    def add_related_entity(self, session_id: str, entity: str):
        """添加相关实体"""
        context = self.get_conversation_context(session_id)
        if context:
            context.related_entities.add(entity)
            context.update_access()

    def _initialize_inheritance_rules(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """初始化参数继承规则"""
        return {
            "start_debate": {
                "topic": {
                    "from_param": "title",
                    "transform": "identity"
                },
                "rounds": {
                    "default": 3,
                    "transform": "int"
                }
            },
            "create_wiki": {
                "title": {
                    "from_intent": "start_debate",
                    "from_param": "topic",
                    "transform": "identity"
                },
                "content": {
                    "from_intent": "start_debate",
                    "transform": "default_if_none",
                    "default_value": "辩论总结"
                }
            },
            "search_papers": {
                "query": {
                    "from_intent": "start_debate",
                    "from_param": "topic",
                    "transform": "identity"
                },
                "query": {
                    "from_intent": "create_wiki",
                    "from_param": "title",
                    "transform": "identity"
                }
            },
            "download_paper": {
                "search_query": {
                    "from_intent": "search_papers",
                    "from_param": "query",
                    "transform": "identity"
                },
                "paper_id": {
                    "from_intent": "search_papers",
                    "transform": "identity"
                }
            },
            "execute_skill": {
                "content": {
                    "from_intent": "start_debate",
                    "from_param": "topic",
                    "transform": "identity"
                },
                "content": {
                    "from_intent": "create_wiki",
                    "from_param": "title",
                    "transform": "identity"
                },
                "content": {
                    "from_intent": "search_papers",
                    "from_param": "query",
                    "transform": "identity"
                }
            }
        }

    def export_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """导出上下文数据"""
        context = self.get_conversation_context(session_id)
        if context:
            return {
                "session_id": context.session_id,
                "topic": context.topic,
                "current_intent": context.current_intent,
                "intent_history": context.intent_history,
                "parameters": {name: asdict(meta) for name, meta in context.parameters.items()},
                "status": context.status.value,
                "created_at": context.created_at.isoformat(),
                "last_accessed": context.last_accessed.isoformat(),
                "related_entities": list(context.related_entities),
                "conversation_summary": context.conversation_summary
            }
        return None

    def import_context(self, context_data: Dict[str, Any]) -> bool:
        """导入上下文数据"""
        try:
            session_id = context_data["session_id"]
            context = ConversationContext(
                session_id=session_id,
                topic=context_data.get("topic", ""),
                current_intent=context_data.get("current_intent", ""),
                intent_history=context_data.get("intent_history", []),
                status=SessionStatus(context_data.get("status", "active")),
                created_at=datetime.fromisoformat(context_data.get("created_at", datetime.now().isoformat())),
                last_accessed=datetime.fromisoformat(context_data.get("last_accessed", datetime.now().isoformat())),
                related_entities=set(context_data.get("related_entities", [])),
                conversation_summary=context_data.get("conversation_summary", "")
            )

            # 恢复参数
            for param_name, param_meta in context_data.get("parameters", {}).items():
                if isinstance(param_meta, dict):
                    context.parameters[param_name] = ParameterMetadata(
                        value=param_meta["value"],
                        source=ParameterSource(param_meta["source"]),
                        timestamp=datetime.fromisoformat(param_meta["timestamp"]),
                        confidence=param_meta.get("confidence", 1.0),
                        context=param_meta.get("context", "")
                    )

            self.conversation_contexts[session_id] = context
            return True
        except Exception as e:
            print(f"Failed to import context: {e}")
            return False

    def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话统计信息"""
        context = self.get_conversation_context(session_id)
        if context:
            duration = datetime.now() - context.created_at
            return {
                "session_duration_seconds": duration.total_seconds(),
                "intent_count": len(context.intent_history),
                "parameter_count": len(context.parameters),
                "unique_intents": len(set(context.intent_history)),
                "last_activity": context.last_accessed.isoformat(),
                "status": context.status.value,
                "has_topic": bool(context.topic),
                "related_entities_count": len(context.related_entities)
            }
        return None