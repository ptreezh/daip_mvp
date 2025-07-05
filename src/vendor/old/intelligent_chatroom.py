"""智能聊天室系统
实现高情商接待员 -> 任务分解大师 -> 动态角色加载的完整流程
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from src.dynamic_role_manager import DynamicRoleManager
from src.expert_library import ExpertLibrary
from src.hybrid_chat_engine import HybridChatEngine
from src.multi_role_chat import MultiRoleChatEngine


@dataclass
class UserRequest:
    """用户请求数据结构"""

    content: str
    user_id: str
    timestamp: str
    session_id: str
    context: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class TaskDecomposition:
    """任务分解结果"""

    analysis: str
    tasks: list[dict[str, Any]]
    recommended_roles: list[dict[str, Any]]
    priority_order: list[str]


@dataclass
class ChatSession:
    """聊天会话"""

    session_id: str
    user_id: str
    created_at: str
    current_stage: str  # "reception", "decomposition", "collaboration"
    active_roles: list[str]
    conversation_history: list[dict[str, Any]]
    user_needs_analysis: dict[str, Any]
    task_decomposition: Optional[TaskDecomposition]


class IntelligentChatroom:
    """智能聊天室核心服务"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 初始化核心组件
        self.expert_library = ExpertLibrary()
        self.dynamic_role_manager = DynamicRoleManager(self.expert_library)
        self.chat_engine = HybridChatEngine()
        self.multi_role_manager = MultiRoleChatEngine(self.expert_library)

        # 会话管理
        self.active_sessions: dict[str, ChatSession] = {}

        # 核心角色ID
        self.receptionist_id = "emotional_intelligence_receptionist_001"
        self.task_master_id = "task_decomposition_master_001"

        # 加载专家库
        self._initialize_system()

    def _initialize_system(self):
        """初始化系统"""
        try:
            # 加载专家库
            stats = self.expert_library.load_experts_from_directory()
            self.logger.info(f"专家库加载完成: {stats}")

            # 确保核心角色存在
            self._ensure_core_roles()

        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")

    def _ensure_core_roles(self):
        """确保核心角色存在"""
        # 检查高情商接待员
        receptionist = self.expert_library.get_expert_by_id(self.receptionist_id)
        if not receptionist:
            self.logger.warning("高情商接待员角色未找到，使用默认配置")

        # 检查任务分解大师
        task_master = self.expert_library.get_expert_by_id(self.task_master_id)
        if not task_master:
            self.logger.warning("任务分解大师角色未找到，使用默认配置")

    async def create_session(self, user_id: str) -> str:
        """创建新的聊天会话"""
        session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now().isoformat(),
            current_stage="reception",
            active_roles=[self.receptionist_id],
            conversation_history=[],
            user_needs_analysis={},
            task_decomposition=None,
        )

        self.active_sessions[session_id] = session

        # 发送欢迎消息
        welcome_message = await self._generate_welcome_message(session)
        session.conversation_history.append(
            {
                "role": self.receptionist_id,
                "content": welcome_message,
                "timestamp": datetime.now().isoformat(),
                "type": "welcome",
            },
        )

        self.logger.info(f"创建新会话: {session_id}")
        return session_id

    async def _generate_welcome_message(self, session: ChatSession) -> str:
        """生成欢迎消息"""
        receptionist = self.expert_library.get_expert_by_id(self.receptionist_id)
        if not receptionist:
            return "您好！我是您的专属助手，很高兴为您服务！请告诉我您需要什么帮助？"

        try:
            response = await self.chat_engine.generate_response(
                role_name=receptionist.get("name", "接待员"),
                role_data=receptionist,
                prompt="请生成一个温暖的欢迎消息，邀请用户分享他们的需求",
                context="",
            )
            return response.get("content", "您好！我是小暖，很高兴为您服务！")
        except Exception as e:
            self.logger.error(f"生成欢迎消息失败: {e}")
            return "您好！我是小暖，很高兴为您服务！请告诉我您需要什么帮助？"

    async def process_user_message(
        self,
        session_id: str,
        user_message: str,
    ) -> dict[str, Any]:
        """处理用户消息的主要入口"""
        if session_id not in self.active_sessions:
            return {"error": "会话不存在"}

        session = self.active_sessions[session_id]

        # 记录用户消息
        session.conversation_history.append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat(),
                "type": "message",
            },
        )

        # 根据当前阶段处理消息
        if session.current_stage == "reception":
            return await self._handle_reception_stage(session, user_message)
        elif session.current_stage == "decomposition":
            return await self._handle_decomposition_stage(session, user_message)
        elif session.current_stage == "collaboration":
            return await self._handle_collaboration_stage(session, user_message)
        else:
            return {"error": "未知的会话阶段"}

    async def _handle_reception_stage(
        self,
        session: ChatSession,
        user_message: str,
    ) -> dict[str, Any]:
        """处理接待阶段"""
        receptionist = self.expert_library.get_expert_by_id(self.receptionist_id)
        if not receptionist:
            return {"error": "接待员角色未找到"}

        # 构建对话上下文
        context = self._build_conversation_context(session)

        try:
            # 生成接待员回复
            response = await self.chat_engine.generate_response(
                role_name=receptionist.get("name", "接待员"),
                role_data=receptionist,
                prompt=f"用户说：{user_message}\n\n请分析用户的需求和情绪，提供温暖的回应，并判断是否已经充分了解用户需求。如果需求明确，请总结用户的核心需求。",
                context=context,
            )

            receptionist_reply = response.get("content", "我理解您的需求，让我为您安排最合适的专家来帮助您。")

            # 记录接待员回复
            session.conversation_history.append(
                {
                    "role": self.receptionist_id,
                    "content": receptionist_reply,
                    "timestamp": datetime.now().isoformat(),
                    "type": "response",
                },
            )

            # 判断是否需要进入任务分解阶段
            needs_analysis = await self._analyze_user_needs(session, user_message)

            if needs_analysis.get("ready_for_decomposition", False):
                # 进入任务分解阶段
                session.current_stage = "decomposition"
                session.user_needs_analysis = needs_analysis

                # 触发任务分解（对用户不可见）
                decomposition_result = await self._perform_task_decomposition(session)

                if decomposition_result:
                    # 进入协作阶段
                    session.current_stage = "collaboration"
                    session.task_decomposition = decomposition_result

                    # 加载推荐的角色
                    await self._load_recommended_roles(session)

                    # 生成协作开始消息
                    collaboration_message = (
                        await self._generate_collaboration_start_message(session)
                    )

                    return {
                        "success": True,
                        "stage": "collaboration",
                        "receptionist_reply": receptionist_reply,
                        "collaboration_message": collaboration_message,
                        "active_roles": session.active_roles,
                        "conversation_history": session.conversation_history[
                            -5:
                        ],  # 返回最近5条消息
                    }

            return {
                "success": True,
                "stage": "reception",
                "reply": receptionist_reply,
                "conversation_history": session.conversation_history[-3:],  # 返回最近3条消息
            }

        except Exception as e:
            self.logger.error(f"处理接待阶段失败: {e}")
            return {"error": f"处理失败: {e!s}"}

    async def _analyze_user_needs(
        self,
        session: ChatSession,
        user_message: str,
    ) -> dict[str, Any]:
        """分析用户需求是否足够明确"""
        # 简单的需求分析逻辑
        conversation_length = len(
            [msg for msg in session.conversation_history if msg["role"] == "user"],
        )

        # 如果用户已经说了2轮以上，或者消息较长，认为需求比较明确
        if conversation_length >= 2 or len(user_message) > 50:
            return {
                "ready_for_decomposition": True,
                "user_intent": user_message,
                "conversation_summary": self._summarize_conversation(session),
                "emotional_state": "neutral",  # 可以后续增强情绪分析
                "urgency_level": "medium",
            }

        return {"ready_for_decomposition": False, "reason": "需要更多信息"}

    def _summarize_conversation(self, session: ChatSession) -> str:
        """总结对话内容"""
        user_messages = [
            msg["content"]
            for msg in session.conversation_history
            if msg["role"] == "user"
        ]
        return " ".join(user_messages)

    def _build_conversation_context(self, session: ChatSession) -> str:
        """构建对话上下文"""
        recent_messages = session.conversation_history[-6:]  # 最近6条消息
        context_parts = []

        for msg in recent_messages:
            role_name = "用户" if msg["role"] == "user" else "助手"
            context_parts.append(f"{role_name}: {msg['content']}")

        return "\n".join(context_parts)

    async def _perform_task_decomposition(
        self,
        session: ChatSession,
    ) -> Optional[TaskDecomposition]:
        """执行任务分解"""
        task_master = self.expert_library.get_expert_by_id(self.task_master_id)
        if not task_master:
            self.logger.error("任务分解大师角色未找到")
            return None

        try:
            # 构建任务分解提示
            decomposition_prompt = f"""
            用户需求分析：
            {json.dumps(session.user_needs_analysis, ensure_ascii=False, indent=2)}

            对话历史：
            {self._build_conversation_context(session)}

            请分析用户需求并进行任务分解，返回JSON格式的结果。
            """

            response = await self.chat_engine.generate_response(
                role_name=task_master.get("name", "任务分解大师"),
                role_data=task_master,
                prompt=decomposition_prompt,
                context="",
            )

            # 解析任务分解结果
            content = response.get("content", "")
            decomposition_data = self._parse_decomposition_result(content)

            if decomposition_data:
                return TaskDecomposition(
                    analysis=decomposition_data.get("analysis", ""),
                    tasks=decomposition_data.get("tasks", []),
                    recommended_roles=decomposition_data.get("recommended_roles", []),
                    priority_order=[
                        task["id"] for task in decomposition_data.get("tasks", [])
                    ],
                )

        except Exception as e:
            self.logger.error(f"任务分解失败: {e}")

        return None

    def _parse_decomposition_result(self, content: str) -> Optional[dict[str, Any]]:
        """解析任务分解结果"""
        try:
            # 尝试从内容中提取JSON
            import re

            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            self.logger.error(f"解析任务分解结果失败: {e}")

        # 如果解析失败，返回默认结构
        return {
            "analysis": "用户需求分析",
            "tasks": [
                {
                    "id": "task_1",
                    "name": "需求处理",
                    "description": "处理用户的主要需求",
                    "priority": "高",
                    "estimated_time": "10分钟",
                    "required_roles": ["通用助手"],
                    "dependencies": [],
                },
            ],
            "recommended_roles": [
                {
                    "role_name": "通用助手",
                    "reason": "能够处理一般性问题",
                    "tasks_assigned": ["task_1"],
                },
            ],
        }

    async def _load_recommended_roles(self, session: ChatSession):
        """加载推荐的角色"""
        if not session.task_decomposition:
            return

        # 获取推荐角色名称
        recommended_role_names = [
            role["role_name"] for role in session.task_decomposition.recommended_roles
        ]

        # 从专家库中查找匹配的角色
        loaded_roles = []
        for role_name in recommended_role_names:
            # 尝试精确匹配
            expert = self.expert_library.search_experts(role_name, limit=1)
            if expert:
                loaded_roles.append(expert[0]["id"])
            else:
                # 尝试模糊匹配
                experts = self.expert_library.search_experts(role_name, limit=3)
                if experts:
                    loaded_roles.append(experts[0]["id"])

        # 如果没有找到合适的角色，使用默认角色
        if not loaded_roles:
            # 获取一些通用角色
            general_experts = self.expert_library.get_experts_by_category("技术")[:2]
            loaded_roles = [expert["id"] for expert in general_experts]

        # 更新会话中的活跃角色
        session.active_roles = [self.receptionist_id] + loaded_roles[:3]  # 限制最多3个专业角色

        self.logger.info(f"为会话 {session.session_id} 加载角色: {session.active_roles}")

    async def _generate_collaboration_start_message(self, session: ChatSession) -> str:
        """生成协作开始消息"""
        if not session.task_decomposition:
            return "我已经为您安排了专业团队来帮助您解决问题。"

        role_names = []
        for role_id in session.active_roles[1:]:  # 排除接待员
            expert = self.expert_library.get_expert_by_id(role_id)
            if expert:
                role_names.append(expert.get("name", role_id))

        if role_names:
            return f"我已经为您安排了专业团队：{', '.join(role_names)}。他们将协作为您提供最佳解决方案。"
        else:
            return "我已经为您安排了专业团队来帮助您解决问题。"

    async def _handle_collaboration_stage(
        self,
        session: ChatSession,
        user_message: str,
    ) -> dict[str, Any]:
        """处理协作阶段"""
        try:
            # 生成多角色响应
            responses = []

            # 为每个活跃角色生成响应
            for role_id in session.active_roles[1:]:  # 排除接待员
                expert = self.expert_library.get_expert_by_id(role_id)
                if expert:
                    response = await self._generate_role_response(
                        expert,
                        user_message,
                        session,
                    )
                    if response:
                        responses.append(response)

                        # 记录角色回复
                        session.conversation_history.append(
                            {
                                "role": role_id,
                                "content": response["content"],
                                "timestamp": datetime.now().isoformat(),
                                "type": "collaboration_response",
                                "role_name": response["role_name"],
                            },
                        )

            return {
                "success": True,
                "stage": "collaboration",
                "responses": responses,
                "active_roles": session.active_roles,
                "conversation_history": session.conversation_history[-10:],  # 返回最近10条消息
            }

        except Exception as e:
            self.logger.error(f"处理协作阶段失败: {e}")
            return {"error": f"协作处理失败: {e!s}"}

    async def _generate_role_response(
        self,
        expert: dict[str, Any],
        user_message: str,
        session: ChatSession,
    ) -> Optional[dict[str, Any]]:
        """为特定角色生成响应"""
        try:
            # 构建角色特定的上下文
            context = self._build_role_context(expert, session)

            # 构建提示词
            prompt = f"""
            用户最新消息：{user_message}

            任务背景：{session.user_needs_analysis.get('user_intent', '')}

            请基于你的专业领域，为用户提供有价值的建议或解决方案。
            """

            response = await self.chat_engine.generate_response(
                role_name=expert.get("name", "专家"),
                role_data=expert,
                prompt=prompt,
                context=context,
            )

            if response.get("success", False):
                return {
                    "role_id": expert["id"],
                    "role_name": expert.get("name", "专家"),
                    "content": response.get("content", ""),
                    "specialties": expert.get("specialties", []),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            self.logger.error(f"生成角色响应失败 {expert.get('name', 'unknown')}: {e}")

        return None

    def _build_role_context(self, expert: dict[str, Any], session: ChatSession) -> str:
        """构建角色特定的上下文"""
        context_parts = []

        # 添加用户需求分析
        if session.user_needs_analysis:
            context_parts.append(f"用户需求分析：{session.user_needs_analysis}")

        # 添加相关的对话历史
        recent_messages = session.conversation_history[-4:]
        for msg in recent_messages:
            if msg["role"] == "user":
                context_parts.append(f"用户：{msg['content']}")

        return "\n".join(context_parts)

    async def _handle_decomposition_stage(
        self,
        session: ChatSession,
        user_message: str,
    ) -> dict[str, Any]:
        """处理分解阶段（通常这个阶段对用户不可见）"""
        # 这个阶段通常在接待阶段内部完成，但保留接口以备扩展
        return await self._handle_reception_stage(session, user_message)

    def get_session_info(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取会话信息"""
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]

        # 获取活跃角色信息
        active_role_info = []
        for role_id in session.active_roles:
            expert = self.expert_library.get_expert_by_id(role_id)
            if expert:
                active_role_info.append(
                    {
                        "id": role_id,
                        "name": expert.get("name", role_id),
                        "category": expert.get("category", ""),
                        "specialties": expert.get("specialties", []),
                    },
                )

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "current_stage": session.current_stage,
            "active_roles": active_role_info,
            "conversation_length": len(session.conversation_history),
            "created_at": session.created_at,
            "user_needs_analysis": session.user_needs_analysis,
            "has_task_decomposition": session.task_decomposition is not None,
        }

    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """获取对话历史"""
        if session_id not in self.active_sessions:
            return []

        session = self.active_sessions[session_id]
        history = (
            session.conversation_history[-limit:]
            if limit > 0
            else session.conversation_history
        )

        # 为每条消息添加角色名称
        enriched_history = []
        for msg in history:
            enriched_msg = msg.copy()
            if msg["role"] != "user":
                expert = self.expert_library.get_expert_by_id(msg["role"])
                if expert:
                    enriched_msg["role_name"] = expert.get("name", msg["role"])
            enriched_history.append(enriched_msg)

        return enriched_history

    def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.logger.info(f"会话已关闭: {session_id}")
            return True
        return False

    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        return len(self.active_sessions)
