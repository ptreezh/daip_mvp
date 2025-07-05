"""统一服务层实现
整合现有组件，提供统一的服务接口
"""

import logging
from typing import Any, Optional

from src.expert_library import ExpertLibrary
from src.interfaces import (
    ConversationContext,
    IChatService,
    IMemoryService,
    IModelService,
    IRecommendationService,
    IRoleService,
    MemoryEntry,
    MemoryFilters,
    RecommendationContext,
    SearchCriteria,
    UnifiedRole,
)
from src.multi_model_adapter import MultiModelManager
from src.multi_role_chat import MultiRoleChatEngine
from src.role_memory_bank import RoleMemoryBank


class UnifiedMemoryService(IMemoryService):
    """统一记忆服务"""

    def __init__(self, memory_bank: RoleMemoryBank):
        self.memory_bank = memory_bank
        self.logger = logging.getLogger(__name__)

    def add_memory(
        self,
        role_id: str,
        content: str,
        memory_type: str,
        importance: float = 0.5,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """添加记忆"""
        return self.memory_bank.add_memory(
            role_id=role_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            project_id=project_id,
            session_id=session_id,
            tags=tags,
            metadata=metadata,
        )

    def retrieve_memories(
        self,
        role_id: str,
        filters: MemoryFilters,
    ) -> list[MemoryEntry]:
        """检索记忆"""
        memories = self.memory_bank.retrieve_memories(
            role_id=role_id,
            query=filters.query,
            memory_types=filters.memory_types,
            project_id=filters.project_id,
            session_id=filters.session_id,
            limit=filters.limit,
            min_importance=filters.min_importance,
        )

        # 转换为统一格式
        unified_memories = []
        for memory in memories:
            unified_memory = MemoryEntry(
                id=memory.id,
                role_id=memory.role_id,
                content=memory.content,
                memory_type=memory.memory_type,
                importance=memory.importance,
                timestamp=memory.timestamp,
                project_id=memory.project_id,
                session_id=memory.session_id,
                tags=memory.tags,
                metadata=memory.metadata,
            )
            unified_memories.append(unified_memory)

        return unified_memories

    def build_context(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
    ) -> ConversationContext:
        """构建对话上下文"""
        context = self.memory_bank.build_context_for_conversation(
            role_id=role_id,
            current_question=current_question,
            project_id=project_id,
            session_id=session_id,
            conversation_history=conversation_history,
        )

        return ConversationContext(
            role_identity=context["role_identity"],
            relevant_memories=context["relevant_memories"],
            project_context=context["project_context"],
            conversation_summary=context["conversation_summary"],
            prompt=context["prompt"],
        )

    def add_dialogue_memory(
        self,
        role_id: str,
        user_message: str,
        role_response: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """添加对话记忆"""
        self.memory_bank.add_dialogue_memory(
            role_id=role_id,
            user_message=user_message,
            role_response=role_response,
            project_id=project_id,
            session_id=session_id,
        )

    def create_project_context(
        self,
        project_name: str,
        description: str,
        participants: list[str],
    ) -> str:
        """创建项目上下文"""
        return self.memory_bank.create_project_context(
            project_name=project_name,
            description=description,
            participants=participants,
        )


class UnifiedRoleService(IRoleService):
    """统一角色服务"""

    def __init__(
        self,
        expert_library: ExpertLibrary,
        memory_service: UnifiedMemoryService,
    ):
        self.expert_library = expert_library
        self.memory_service = memory_service
        self.logger = logging.getLogger(__name__)

    def get_role(self, role_id: str) -> Optional[UnifiedRole]:
        """获取角色信息"""
        expert = self.expert_library.get_expert_by_id(role_id)
        if not expert:
            return None

        return self._convert_expert_to_unified_role(expert)

    def search_roles(self, criteria: SearchCriteria) -> list[UnifiedRole]:
        """搜索角色"""
        experts = self.expert_library.search_experts(
            query=criteria.query or "",
            category=criteria.category,
            limit=criteria.limit,
        )

        # 应用额外过滤条件
        filtered_experts = []
        for expert in experts:
            if criteria.skills:
                expert_skills = set(expert.get("skills", []))
                required_skills = set(criteria.skills)
                if not required_skills.intersection(expert_skills):
                    continue

            if (
                criteria.min_experience
                and expert.get("experience_years", 0) < criteria.min_experience
            ):
                continue

            if (
                criteria.min_reputation
                and expert.get("reputation_score", 0) < criteria.min_reputation
            ):
                continue

            filtered_experts.append(expert)

        return [
            self._convert_expert_to_unified_role(expert) for expert in filtered_experts
        ]

    def get_all_roles(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[UnifiedRole]:
        """获取所有角色"""
        experts = self.expert_library.get_all_experts(category=category, limit=limit)
        return [self._convert_expert_to_unified_role(expert) for expert in experts]

    def create_role_identity(self, role_data: dict[str, Any]) -> str:
        """创建角色身份"""
        # 创建记忆银行中的角色身份
        identity = self.memory_service.memory_bank.create_role_identity(role_data)
        return identity.role_id

    def update_role(self, role_id: str, updates: dict[str, Any]) -> bool:
        """更新角色信息"""
        # 更新专家库
        success = self.expert_library.update_expert(role_id, updates)

        # 更新记忆银行中的身份信息
        if success:
            self.memory_service.memory_bank.update_role_identity(role_id, updates)

        return success

    def _convert_expert_to_unified_role(self, expert: dict[str, Any]) -> UnifiedRole:
        """转换专家数据为统一角色格式"""
        return UnifiedRole(
            id=expert.get("id", ""),
            name=expert.get("name", ""),
            title=expert.get("title", ""),
            category=expert.get("category", ""),
            specialties=expert.get("specialties", []),
            description=expert.get("description", ""),
            bio=expert.get("bio", ""),
            skills=expert.get("skills", []),
            experience_years=expert.get("experience_years", 0),
            reputation_score=expert.get("reputation_score", 0.0),
            contact_info=expert.get("contact_info", {}),
            languages=expert.get("languages", []),
            availability=expert.get("availability", ""),
            location=expert.get("location", ""),
            education=expert.get("education", []),
            certifications=expert.get("certifications", []),
            projects=expert.get("projects", []),
            hourly_rate=expert.get("hourly_rate"),
            source_file=expert.get("source_file", ""),
            created_at=expert.get("created_at", ""),
            updated_at=expert.get("updated_at", ""),
            metadata=expert.get("metadata", {}),
        )


class UnifiedRecommendationService(IRecommendationService):
    """统一推荐服务"""

    def __init__(
        self,
        role_service: UnifiedRoleService,
        chat_engine: MultiRoleChatEngine,
    ):
        self.role_service = role_service
        self.chat_engine = chat_engine
        self.logger = logging.getLogger(__name__)

    def recommend_roles(self, context: RecommendationContext) -> list[UnifiedRole]:
        """推荐角色"""
        recommendations = self.chat_engine.recommendation_engine.recommend_roles(
            topic=context.topic,
            current_participants=context.current_participants,
            desired_expertise=context.desired_expertise,
        )

        # 转换为统一格式
        unified_roles = []
        for rec in recommendations[: context.count]:
            role = self.role_service.get_role(rec["id"])
            if role:
                unified_roles.append(role)

        return unified_roles

    def get_random_roles(
        self,
        count: int = 6,
        category: Optional[str] = None,
    ) -> list[UnifiedRole]:
        """获取随机角色"""
        random_experts = self.chat_engine.recommendation_engine.get_random_roles(
            count,
            category,
        )

        unified_roles = []
        for expert in random_experts:
            role = self.role_service.get_role(expert["id"])
            if role:
                unified_roles.append(role)

        return unified_roles

    def calculate_role_relevance(self, role: UnifiedRole, topic: str) -> float:
        """计算角色相关性"""
        # 简单的相关性计算
        relevance = 0.0
        topic_words = set(topic.lower().split())

        # 检查专长匹配
        for specialty in role.specialties:
            specialty_words = set(specialty.lower().split())
            if topic_words.intersection(specialty_words):
                relevance += 0.3

        # 检查技能匹配
        for skill in role.skills:
            skill_words = set(skill.lower().split())
            if topic_words.intersection(skill_words):
                relevance += 0.2

        # 检查描述匹配
        desc_words = set(role.description.lower().split())
        if topic_words.intersection(desc_words):
            relevance += 0.1

        return min(relevance, 1.0)


class UnifiedModelService(IModelService):
    """统一模型服务"""

    def __init__(
        self,
        model_manager: MultiModelManager,
        memory_service: UnifiedMemoryService,
    ):
        self.model_manager = model_manager
        self.memory_service = memory_service
        self.logger = logging.getLogger(__name__)

    async def generate_response(
        self,
        role_id: str,
        user_message: str,
        model_name: Optional[str] = None,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """生成角色响应"""
        response = await self.model_manager.generate_response(
            role_id=role_id,
            user_message=user_message,
            model_name=model_name,
            project_id=project_id,
            session_id=session_id,
            conversation_history=conversation_history,
            **kwargs,
        )

        return {
            "content": response.content,
            "role_id": response.role_id,
            "model_type": response.model_type,
            "usage_info": response.usage_info,
            "metadata": response.metadata,
        }

    def get_available_models(self) -> list[str]:
        """获取可用模型列表"""
        return self.model_manager.get_available_models()

    def setup_model(self, model_name: str, config: dict[str, Any]) -> bool:
        """设置模型"""
        try:
            if model_name == "ollama":
                self.model_manager.setup_ollama(
                    base_url=config.get("base_url", "http://localhost:11434"),
                    model_name=config.get("model_name", "gemma3:latest"),
                    is_default=config.get("is_default", False),
                )
            elif model_name == "openai":
                self.model_manager.setup_openai(
                    api_key=config["api_key"],
                    model_name=config.get("model_name", "gpt-3.5-turbo"),
                    is_default=config.get("is_default", False),
                )
            elif model_name == "anthropic":
                self.model_manager.setup_anthropic(
                    api_key=config["api_key"],
                    model_name=config.get("model_name", "claude-3-sonnet-20240229"),
                    is_default=config.get("is_default", False),
                )
            elif model_name == "siliconflow":
                self.model_manager.setup_siliconflow(
                    api_key=config["api_key"],
                    model_name=config.get("model_name", "internlm/internlm2_5-7b-chat"),
                    is_default=config.get("is_default", False),
                )
            else:
                return False

            return True
        except Exception as e:
            self.logger.error(f"Failed to setup model {model_name}: {e}")
            return False


class UnifiedChatService(IChatService):
    """统一聊天服务 - 集成记忆功能"""

    def __init__(
        self,
        chat_engine: MultiRoleChatEngine,
        memory_service: UnifiedMemoryService,
        model_service: UnifiedModelService,
    ):
        self.chat_engine = chat_engine
        self.memory_service = memory_service
        self.model_service = model_service
        self.logger = logging.getLogger(__name__)

    def create_room(
        self,
        room_name: str,
        topic: str,
        initial_participants: Optional[list[str]] = None,
    ) -> str:
        """创建聊天室"""
        room_id = self.chat_engine.create_chat_room(
            room_name=room_name,
            topic=topic,
            initial_participants=initial_participants,
        )

        # 为聊天室创建项目上下文
        if initial_participants:
            project_id = self.memory_service.create_project_context(
                project_name=f"聊天室: {room_name}",
                description=f"主题: {topic}",
                participants=initial_participants,
            )

            # 将项目ID存储到聊天室配置中
            chat_room = self.chat_engine.get_chat_room(room_id)
            if chat_room:
                chat_room.room_config["project_id"] = project_id

        return room_id

    def add_participant(self, room_id: str, role_id: str) -> bool:
        """添加参与者"""
        success = self.chat_engine.add_participant(room_id, role_id)

        if success:
            # 更新项目参与者
            chat_room = self.chat_engine.get_chat_room(room_id)
            if chat_room and "project_id" in chat_room.room_config:
                project_id = chat_room.room_config["project_id"]

                # 为新参与者添加项目记忆
                self.memory_service.add_memory(
                    role_id=role_id,
                    content=f"加入聊天室: {chat_room.room_name}，讨论主题: {chat_room.topic}",
                    memory_type="project",
                    importance=0.6,
                    project_id=project_id,
                    tags=["聊天室", "加入"],
                )

        return success

    def remove_participant(self, room_id: str, role_id: str) -> bool:
        """移除参与者"""
        return self.chat_engine.remove_participant(room_id, role_id)

    async def send_message(
        self,
        room_id: str,
        content: str,
        sender_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """发送消息并获取角色响应（集成记忆功能）"""
        chat_room = self.chat_engine.get_chat_room(room_id)
        if not chat_room:
            return []

        # 获取项目ID
        project_id = chat_room.room_config.get("project_id")
        session_id = f"room_{room_id}"

        # 生成角色响应（使用增强的记忆功能）
        responses = []

        for participant in chat_room.participants:
            if participant.role_id == sender_id:
                continue  # 跳过发送者

            try:
                # 构建带记忆的上下文
                context = self.memory_service.build_context(
                    role_id=participant.role_id,
                    current_question=content,
                    project_id=project_id,
                    session_id=session_id,
                    conversation_history=self._get_recent_chat_history(chat_room),
                )

                # 使用增强的提示词生成响应
                model_response = await self.model_service.generate_response(
                    role_id=participant.role_id,
                    user_message=content,
                    project_id=project_id,
                    session_id=session_id,
                    conversation_history=self._get_recent_chat_history(chat_room),
                )

                # 创建响应消息
                response_message = {
                    "id": self._generate_message_id(),
                    "role_id": participant.role_id,
                    "role_name": participant.role_name,
                    "content": model_response["content"],
                    "timestamp": self._get_current_timestamp(),
                    "message_type": "text",
                    "metadata": {
                        "model_type": model_response["model_type"],
                        "context_memories": len(context.relevant_memories),
                        "project_id": project_id,
                    },
                }

                responses.append(response_message)

                # 保存对话记忆
                self.memory_service.add_dialogue_memory(
                    role_id=participant.role_id,
                    user_message=content,
                    role_response=model_response["content"],
                    project_id=project_id,
                    session_id=session_id,
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to generate response for {participant.role_name}: {e}",
                )

                # 添加错误响应
                error_response = {
                    "id": self._generate_message_id(),
                    "role_id": participant.role_id,
                    "role_name": participant.role_name,
                    "content": "[抱歉，我暂时无法回应，请稍后再试]",
                    "timestamp": self._get_current_timestamp(),
                    "message_type": "text",
                    "metadata": {"error": str(e)},
                }
                responses.append(error_response)

        return responses

    def get_room_info(self, room_id: str) -> Optional[dict[str, Any]]:
        """获取聊天室信息"""
        chat_room = self.chat_engine.get_chat_room(room_id)
        if not chat_room:
            return None

        return {
            "room_id": chat_room.room_id,
            "room_name": chat_room.room_name,
            "topic": chat_room.topic,
            "participants": [
                {
                    "role_id": p.role_id,
                    "role_name": p.role_name,
                    "message_count": p.message_count,
                    "last_activity": p.last_activity,
                }
                for p in chat_room.participants
            ],
            "message_count": len(chat_room.messages),
            "created_at": chat_room.created_at,
            "last_activity": chat_room.last_activity,
            "is_active": chat_room.is_active,
            "project_id": chat_room.room_config.get("project_id"),
        }

    def get_room_history(self, room_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """获取聊天历史"""
        chat_room = self.chat_engine.get_chat_room(room_id)
        if not chat_room:
            return []

        messages = chat_room.messages[-limit:] if limit > 0 else chat_room.messages

        return [
            {
                "id": msg.id,
                "role_id": msg.role_id,
                "role_name": msg.role_name,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "message_type": msg.message_type,
                "metadata": msg.metadata,
            }
            for msg in messages
        ]

    def _get_recent_chat_history(self, chat_room) -> list[dict[str, str]]:
        """获取最近的聊天历史"""
        recent_messages = chat_room.messages[-10:]  # 最近10条消息

        history = []
        for msg in recent_messages:
            if msg.message_type == "text":
                history.append(
                    {
                        "role": "assistant" if msg.role_id else "user",
                        "content": f"{msg.role_name}: {msg.content}",
                    },
                )

        return history

    def _generate_message_id(self) -> str:
        """生成消息ID"""
        import hashlib
        import random
        import time

        return hashlib.md5(f"{time.time()}_{random.random()}".encode()).hexdigest()[:16]

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime

        return datetime.now().isoformat()
