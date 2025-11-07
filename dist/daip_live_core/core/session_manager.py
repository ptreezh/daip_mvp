"""
通用会话管理器 - 集成优化组件
支持所有角色应用场景的统一会话管理
"""

from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from daip_live.core.models import Session, AgentState, DialogueTurn
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

# 导入通用优化组件
from daip_live.core.universal_model_manager import UniversalModelManager
from daip_live.core.universal_memory_system import UniversalMemorySystem, MemoryType


@dataclass
class UniversalRoleSession:
    """通用角色会话 - 适用于所有应用场景"""

    role_name: str
    role_persona: str
    model_config: RoleModelConfig
    session_type: str  # "debate", "conversation", "analysis", "creative", etc.
    system_prompt: str = ""

    # 会话历史
    dialogue_history: List[Dict[str, Any]] = field(default_factory=list)

    # 个人记忆和上下文
    personal_context: Dict[str, Any] = field(default_factory=dict)
    stance_memory: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)

    # 应用特定数据
    application_data: Dict[str, Any] = field(default_factory=dict)

    def add_dialogue_turn(self, role: str, content: str, turn_type: str = "dialogue", metadata: Optional[Dict] = None):
        """添加对话轮次"""
        self.dialogue_history.append({
            "role": role,
            "content": content,
            "type": turn_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })

    def update_context(self, key: str, value: Any):
        """更新角色上下文"""
        self.personal_context[key] = value

    def add_preference(self, key: str, value: Any, confidence: float = 1.0):
        """添加角色偏好"""
        self.preferences[key] = {"value": value, "confidence": confidence, "timestamp": datetime.now().isoformat()}

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的对话历史"""
        return self.dialogue_history[-limit:]

    def get_context_summary(self, current_round: int = 1) -> str:
        """获取角色上下文摘要"""
        context_parts = []

        # 基本信息
        context_parts.append(f"Role: {self.role_persona}")
        context_parts.append(f"Session Type: {self.session_type}")
        context_parts.append(f"Model: {self.model_config.model_name}")

        # 核心立场
        if self.stance_memory:
            core_stance = self.stance_memory.get("core_stance", "Developing...")
            context_parts.append(f"Core Stance: {core_stance}")

        # 最近对话
        recent_history = self.get_recent_history(3)
        if recent_history:
            context_parts.append("Recent Dialogue:")
            for turn in recent_history:
                context_parts.append(f"  {turn['role']}: {turn['content'][:100]}...")

        return "\n".join(context_parts)


class UniversalSessionManager:
    """通用会话管理器 - 集成所有优化组件"""

    def __init__(self, use_optimized_architecture: bool = True):
        self.use_optimized_architecture = use_optimized_architecture

        if use_optimized_architecture:
            # 核心优化组件
            self.model_manager = UniversalModelManager()
            self.memory_system = UniversalMemorySystem()

            # 通用角色会话
            self.role_sessions: Dict[str, UniversalRoleSession] = {}

            # 会话映射
            self.session_mapping: Dict[str, str] = {}  # session_id -> role_name

        # 传统会话管理（保持兼容性）
        self.legacy_sessions: Dict[str, Session] = {}

    async def create_universal_session(
        self,
        role_name: str,
        role_persona: str,
        model_config: RoleModelConfig,
        session_type: str = "conversation",
        system_prompt: str = "",
        session_id: Optional[str] = None
    ) -> str:
        """创建通用角色会话"""
        if not self.use_optimized_architecture:
            raise ValueError("Universal session requires optimized architecture")

        session_id = session_id or f"universal_{datetime.now().timestamp()}"

        # 创建通用角色会话
        self.role_sessions[role_name] = UniversalRoleSession(
            role_name=role_name,
            role_persona=role_persona,
            model_config=model_config,
            session_type=session_type,
            system_prompt=system_prompt
        )

        # 建立映射
        self.session_mapping[session_id] = role_name

        # 添加到记忆系统
        self.memory_system.add_memory(
            content=f"Session started for {role_name} - {session_type}",
            memory_type=MemoryType.SESSION_CONTEXT,
            source="system",
            confidence=1.0,
            session_id=session_id
        )

        return session_id

    async def generate_response(
        self,
        session_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """生成回复 - 适用于所有应用场景"""
        if not self.use_optimized_architecture:
            raise ValueError("Optimized architecture not enabled")

        if session_id not in self.session_mapping:
            raise ValueError(f"Session {session_id} not found")

        role_name = self.session_mapping[session_id]
        role_session = self.role_sessions[role_name]

        # 构建增强提示词
        enhanced_prompt = self._build_enhanced_prompt(role_session, prompt, context, **kwargs)

        # 使用通用模型管理器生成回复
        response_content, usage = await self.model_manager.generate_response(
            model_name=role_session.model_config.model_name,
            prompt=enhanced_prompt,
            session_type=role_session.session_type,
            session_id=session_id,
            temperature=role_session.model_config.temperature,
            max_tokens=role_session.model_config.max_tokens,
            top_p=role_session.model_config.top_p,
            frequency_penalty=role_session.model_config.frequency_penalty,
            presence_penalty=role_session.model_config.presence_penalty
        )

        # 记录对话
        role_session.add_dialogue_turn("assistant", response_content, "response", {
            "usage": usage,
            "context": context
        })

        # 更新记忆系统
        self.memory_system.add_memory(
            content=response_content,
            memory_type=MemoryType.PERSONAL_ARGUMENT,
            source=role_name,
            confidence=0.9,
            role_name=role_name,
            session_id=session_id,
            metadata={"turn_type": "response", "usage": usage}
        )

        # 转换usage格式
        token_info = None
        if usage:
            token_info = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }

        return response_content, token_info

    def _build_enhanced_prompt(
        self,
        role_session: UniversalRoleSession,
        user_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """构建增强提示词"""
        prompt_parts = []

        # 基本信息
        prompt_parts.append(f"Session Type: {role_session.session_type}")
        prompt_parts.append(f"Your Role: {role_session.role_persona}")
        prompt_parts.append(f"Your Model: {role_session.model_config.model_name}")

        if role_session.system_prompt:
            prompt_parts.append(f"System Instructions: {role_session.system_prompt}")

        # 添加上下文
        if context:
            prompt_parts.append("\nCurrent Context:")
            for key, value in context.items():
                prompt_parts.append(f"  {key}: {value}")

        # 添加角色历史和偏好
        context_summary = role_session.get_context_summary()
        if context_summary:
            prompt_parts.append(f"\n{context_summary}")

        # 添加通用记忆
        memory_context = self.memory_system.get_compressed_context(
            role_name=role_session.role_name,
            session_id=session_id,
            current_round=len(role_session.dialogue_history) + 1
        )
        if memory_context and memory_context != "No relevant memories found.":
            prompt_parts.append(f"\nRelevant Memory:\n{memory_context}")

        # 用户提示
        prompt_parts.append(f"\nUser Request:\n{user_prompt}")

        # 应用特定指令
        if role_session.session_type == "debate":
            prompt_parts.append("\nPlease maintain a balanced debate perspective and build upon previous arguments.")
        elif role_session.session_type == "analysis":
            prompt_parts.append("\nPlease provide thorough analysis with supporting evidence.")
        elif role_session.session_type == "creative":
            prompt_parts.append("\nPlease be creative and imaginative in your response.")

        return "\n".join(prompt_parts)

    def add_user_message(self, session_id: str, content: str, metadata: Optional[Dict] = None):
        """添加用户消息"""
        if not self.use_optimized_architecture:
            raise ValueError("Optimized architecture not enabled")

        if session_id not in self.session_mapping:
            raise ValueError(f"Session {session_id} not found")

        role_name = self.session_mapping[session_id]
        role_session = self.role_sessions[role_name]

        role_session.add_dialogue_turn("user", content, "user_input", metadata)

        # 更新记忆系统
        self.memory_system.add_memory(
            content=content,
            memory_type=MemoryType.PERSONAL_ARGUMENT,
            source="user",
            confidence=1.0,
            role_name=role_name,
            session_id=session_id,
            metadata={"turn_type": "user_input"}
        )

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """获取会话上下文"""
        if not self.use_optimized_architecture:
            raise ValueError("Optimized architecture not enabled")

        if session_id not in self.session_mapping:
            raise ValueError(f"Session {session_id} not found")

        role_name = self.session_mapping[session_id]
        role_session = self.role_sessions[role_name]

        return {
            "role_name": role_name,
            "session_type": role_session.session_type,
            "dialogue_history": role_session.get_recent_history(),
            "personal_context": role_session.personal_context,
            "preferences": role_session.preferences,
            "memory_context": self.memory_system.get_context(role_name=role_name, session_id=session_id, current_round=len(role_session.dialogue_history) + 1)
        }

    def update_role_preference(self, session_id: str, key: str, value: Any, confidence: float = 1.0):
        """更新角色偏好"""
        if not self.use_optimized_architecture:
            raise ValueError("Optimized architecture not enabled")

        if session_id not in self.session_mapping:
            raise ValueError(f"Session {session_id} not found")

        role_name = self.session_mapping[session_id]
        role_session = self.role_sessions[role_name]

        role_session.add_preference(key, value, confidence)

    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计信息"""
        if not self.use_optimized_architecture:
            raise ValueError("Optimized architecture not enabled")

        if session_id not in self.session_mapping:
            raise ValueError(f"Session {session_id} not found")

        role_name = self.session_mapping[session_id]
        role_session = self.role_sessions[role_name]

        return {
            "session_id": session_id,
            "role_name": role_name,
            "session_type": role_session.session_type,
            "dialogue_turns": len(role_session.dialogue_history),
            "preferences_count": len(role_session.preferences),
            "memory_entries": self.memory_system.get_memory_statistics().get("total_shared_facts", 0)
        }

    def list_active_sessions(self) -> List[str]:
        """列出活跃会话"""
        if self.use_optimized_architecture:
            return list(self.session_mapping.keys())
        else:
            return list(self.legacy_sessions.keys())

    def end_session(self, session_id: str):
        """结束会话"""
        if not self.use_optimized_architecture:
            raise ValueError("Optimized architecture not enabled")

        if session_id in self.session_mapping:
            role_name = self.session_mapping[session_id]

            # 记录会话结束
            self.memory_system.add_memory(
                content=f"Session ended for {role_name}",
                memory_type=MemoryType.SESSION_CONTEXT,
                source="system",
                confidence=1.0,
                session_id=session_id
            )

            # 清理资源
            del self.session_mapping[session_id]
            if role_name in self.role_sessions:
                del self.role_sessions[role_name]

    # 兼容性方法 - 保持与现有SessionManager的接口兼容
    def create_session(self, goal: str, session_type: str, participant_ids: List[str]) -> Session:
        """创建传统会话（保持兼容性）"""
        if self.use_optimized_architecture:
            # 如果使用优化架构，创建兼容的会话
            session = Session(
                session_id=f"legacy_{datetime.now().timestamp()}",
                goal=goal,
                session_type=session_type,
                participant_ids=participant_ids,
                status=AgentState.RUNNING
            )
            self.legacy_sessions[session.session_id] = session
            return session
        else:
            # 完全传统模式
            session = Session(
                session_id=f"legacy_{datetime.now().timestamp()}",
                goal=goal,
                session_type=session_type,
                participant_ids=participant_ids,
                status=AgentState.RUNNING
            )
            self.legacy_sessions[session.session_id] = session
            return session

    def save_session(self, session: Session):
        """保存会话"""
        if session.session_id in self.legacy_sessions:
            self.legacy_sessions[session.session_id] = session

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.legacy_sessions.get(session_id)

    def list_sessions(self) -> List[Session]:
        """列出所有会话"""
        return list(self.legacy_sessions.values())

    def get_optimization_benefits(self) -> Dict[str, Any]:
        """获取优化好处"""
        if not self.use_optimized_architecture:
            return {"message": "优化架构未启用"}

        return {
            "resource_usage": {
                "ollama_instances": 1,
                "memory_efficiency": "通用会话管理减少资源浪费",
                "model_switching": "分时复用避免资源竞争"
            },
            "memory_system": self.memory_system.get_memory_statistics(),
            "active_sessions": len(self.session_mapping),
            "supported_session_types": ["conversation", "debate", "analysis", "creative", "roleplay"]
        }