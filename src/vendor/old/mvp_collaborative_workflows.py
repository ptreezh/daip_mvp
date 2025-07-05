"""MVP版本多种协同流程管理器
快速实现多种协同流程的聊天室和文档处理功能
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from src.document_parser import DocumentParser
from src.enhanced_collaborative_analysis import (
    EnhancedCollaborativeAnalysis,
)
from src.expert_library import ExpertLibrary
from src.multi_role_chat import MultiRoleChatEngine


class WorkflowType(Enum):
    """工作流类型枚举"""

    BRAINSTORMING = "brainstorming"  # 头脑风暴
    DOCUMENT_REVIEW = "document_review"  # 文档评审
    DECISION_MAKING = "decision_making"  # 决策制定
    PROBLEM_SOLVING = "problem_solving"  # 问题解决
    CREATIVE_WRITING = "creative_writing"  # 创意写作
    TECHNICAL_DISCUSSION = "technical_discussion"  # 技术讨论
    STRATEGIC_PLANNING = "strategic_planning"  # 战略规划


class WorkflowPhase(Enum):
    """工作流阶段枚举"""

    INITIALIZATION = "initialization"
    PARTICIPANT_ASSIGNMENT = "participant_assignment"
    DISCUSSION = "discussion"
    COLLABORATION = "collaboration"
    DECISION = "decision"
    DOCUMENTATION = "documentation"
    COMPLETED = "completed"


@dataclass
class WorkflowConfig:
    """工作流配置数据结构"""

    workflow_type: WorkflowType
    name: str
    description: str
    required_roles: list[str] = field(default_factory=list)
    optional_roles: list[str] = field(default_factory=list)
    max_participants: int = 0
    estimated_duration: int = 0  # 分钟
    phases: list[WorkflowPhase] = field(default_factory=list)
    auto_progression: bool = True


@dataclass
class WorkflowSession:
    """工作流会话数据结构"""

    session_id: str
    workflow_type: WorkflowType
    topic: str
    description: str
    participants: list[str] = field(default_factory=list)
    chat_room_id: Optional[str] = None
    document_tasks: list[str] = field(default_factory=list)
    current_phase: WorkflowPhase = WorkflowPhase.INITIALIZATION
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    session_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.session_data is None:
            self.session_data = {}


class MVPCollaborativeWorkflows:
    """MVP协同工作流管理器，负责多种协同流程的会话、聊天室、文档等全流程管理。"""

    def __init__(self, data_dir: str = "data/mvp_workflows"):
        """初始化协同工作流管理器。
        :param data_dir: 会话数据持久化目录，自动创建。
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)  # 自动创建目录

        # 初始化核心组件
        self.expert_library = ExpertLibrary()
        self.multi_role_chat = MultiRoleChatEngine(self.expert_library)
        self.collaborative_analysis = EnhancedCollaborativeAnalysis()
        self.document_parser = DocumentParser()

        # 加载工作流配置
        self.workflow_configs = self._load_workflow_configs()

        # 活跃会话池
        self.active_sessions: dict[str, WorkflowSession] = {}

        # 加载历史会话
        self._load_existing_sessions()

    def _load_workflow_configs(self) -> dict[WorkflowType, WorkflowConfig]:
        """加载所有支持的工作流配置。"""
        configs = {
            WorkflowType.BRAINSTORMING: WorkflowConfig(
                workflow_type=WorkflowType.BRAINSTORMING,
                name="头脑风暴",
                description="多角色创意发散和方案生成",
                required_roles=["创意专家", "领域专家"],
                optional_roles=["批判性思维专家", "创新专家", "市场专家"],
                max_participants=8,
                estimated_duration=60,
                phases=[
                    WorkflowPhase.INITIALIZATION,
                    WorkflowPhase.PARTICIPANT_ASSIGNMENT,
                    WorkflowPhase.DISCUSSION,
                    WorkflowPhase.COLLABORATION,
                    WorkflowPhase.DOCUMENTATION,
                    WorkflowPhase.COMPLETED,
                ],
            ),
            WorkflowType.DOCUMENT_REVIEW: WorkflowConfig(
                workflow_type=WorkflowType.DOCUMENT_REVIEW,
                name="文档评审",
                description="多角色协同文档分析和评审",
                required_roles=["文档分析专家", "领域专家"],
                optional_roles=["质量专家", "技术专家", "法律专家"],
                max_participants=6,
                estimated_duration=90,
                phases=[
                    WorkflowPhase.INITIALIZATION,
                    WorkflowPhase.PARTICIPANT_ASSIGNMENT,
                    WorkflowPhase.DISCUSSION,
                    WorkflowPhase.COLLABORATION,
                    WorkflowPhase.DECISION,
                    WorkflowPhase.DOCUMENTATION,
                    WorkflowPhase.COMPLETED,
                ],
            ),
            WorkflowType.DECISION_MAKING: WorkflowConfig(
                workflow_type=WorkflowType.DECISION_MAKING,
                name="决策制定",
                description="多角色决策分析和共识达成",
                required_roles=["决策专家", "分析专家"],
                optional_roles=["风险评估专家", "利益相关者代表", "执行专家"],
                max_participants=10,
                estimated_duration=120,
                phases=[
                    WorkflowPhase.INITIALIZATION,
                    WorkflowPhase.PARTICIPANT_ASSIGNMENT,
                    WorkflowPhase.DISCUSSION,
                    WorkflowPhase.COLLABORATION,
                    WorkflowPhase.DECISION,
                    WorkflowPhase.DOCUMENTATION,
                    WorkflowPhase.COMPLETED,
                ],
            ),
            WorkflowType.PROBLEM_SOLVING: WorkflowConfig(
                workflow_type=WorkflowType.PROBLEM_SOLVING,
                name="问题解决",
                description="多角色问题分析和解决方案制定",
                required_roles=["问题分析专家", "解决方案专家"],
                optional_roles=["技术专家", "实施专家", "评估专家"],
                max_participants=8,
                estimated_duration=90,
                phases=[
                    WorkflowPhase.INITIALIZATION,
                    WorkflowPhase.PARTICIPANT_ASSIGNMENT,
                    WorkflowPhase.DISCUSSION,
                    WorkflowPhase.COLLABORATION,
                    WorkflowPhase.DECISION,
                    WorkflowPhase.DOCUMENTATION,
                    WorkflowPhase.COMPLETED,
                ],
            ),
            WorkflowType.CREATIVE_WRITING: WorkflowConfig(
                workflow_type=WorkflowType.CREATIVE_WRITING,
                name="创意写作",
                description="多角色协同创意内容创作",
                required_roles=["创意写作专家", "内容专家"],
                optional_roles=["编辑专家", "市场专家", "技术专家"],
                max_participants=6,
                estimated_duration=120,
                phases=[
                    WorkflowPhase.INITIALIZATION,
                    WorkflowPhase.PARTICIPANT_ASSIGNMENT,
                    WorkflowPhase.DISCUSSION,
                    WorkflowPhase.COLLABORATION,
                    WorkflowPhase.DOCUMENTATION,
                    WorkflowPhase.COMPLETED,
                ],
            ),
            WorkflowType.TECHNICAL_DISCUSSION: WorkflowConfig(
                workflow_type=WorkflowType.TECHNICAL_DISCUSSION,
                name="技术讨论",
                description="多角色技术问题讨论和方案设计",
                required_roles=["技术专家", "架构专家"],
                optional_roles=["安全专家", "性能专家", "用户体验专家"],
                max_participants=8,
                estimated_duration=90,
                phases=[
                    WorkflowPhase.INITIALIZATION,
                    WorkflowPhase.PARTICIPANT_ASSIGNMENT,
                    WorkflowPhase.DISCUSSION,
                    WorkflowPhase.COLLABORATION,
                    WorkflowPhase.DECISION,
                    WorkflowPhase.DOCUMENTATION,
                    WorkflowPhase.COMPLETED,
                ],
            ),
            WorkflowType.STRATEGIC_PLANNING: WorkflowConfig(
                workflow_type=WorkflowType.STRATEGIC_PLANNING,
                name="战略规划",
                description="多角色战略分析和规划制定",
                required_roles=["战略专家", "市场专家"],
                optional_roles=["财务专家", "运营专家", "风险专家"],
                max_participants=10,
                estimated_duration=180,
                phases=[
                    WorkflowPhase.INITIALIZATION,
                    WorkflowPhase.PARTICIPANT_ASSIGNMENT,
                    WorkflowPhase.DISCUSSION,
                    WorkflowPhase.COLLABORATION,
                    WorkflowPhase.DECISION,
                    WorkflowPhase.DOCUMENTATION,
                    WorkflowPhase.COMPLETED,
                ],
            ),
        }
        return configs

    def create_workflow_session(
        self,
        workflow_type: WorkflowType,
        topic: str,
        description: str,
        requester_id: str,
        custom_participants: Optional[list[str]] = None,
    ) -> str:
        """创建新的工作流会话。
        :param workflow_type: 工作流类型
        :param topic: 主题
        :param description: 描述
        :param requester_id: 发起人ID
        :param custom_participants: 可选自定义参与者ID列表
        :return: 新会话ID
        """
        session_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        config = self.workflow_configs.get(workflow_type)
        if not config:
            raise ValueError(f"不支持的工作流类型: {workflow_type}")
        participants = self._assign_participants(config, custom_participants)
        session = WorkflowSession(
            session_id=session_id,
            workflow_type=workflow_type,
            topic=topic,
            description=description,
            participants=participants,
        )
        chat_room_name = f"[{config.name}] {topic}"
        chat_room_id = self.multi_role_chat.create_chat_room(
            room_name=chat_room_name,
            topic=description,
            initial_participants=participants,
        )
        session.chat_room_id = chat_room_id
        self.active_sessions[session_id] = session
        self._save_session(session)
        # 假定外部有事件循环
        asyncio.create_task(self._execute_workflow(session_id))
        self.logger.info(f"Created workflow session: {session_id}")
        return session_id

    def _assign_participants(
        self,
        config: WorkflowConfig,
        custom_participants: Optional[list[str]] = None,
    ) -> list[str]:
        """分配参与者，包括必需角色、可选角色和自定义参与者。
        :param config: 工作流配置
        :param custom_participants: 可选自定义参与者ID列表
        :return: 参与者ID列表
        """
        participants = []
        for role_name in config.required_roles:
            expert = self._find_expert_by_role(role_name)
            if expert:
                participants.append(expert["id"])
        remaining_slots = config.max_participants - len(participants)
        if remaining_slots > 0:
            for role_name in config.optional_roles[:remaining_slots]:
                expert = self._find_expert_by_role(role_name)
                if expert and expert["id"] not in participants:
                    participants.append(expert["id"])
        if custom_participants:
            for participant_id in custom_participants:
                if (
                    participant_id not in participants
                    and len(participants) < config.max_participants
                ):
                    participants.append(participant_id)
        return participants

    def _find_expert_by_role(self, role_name: str) -> Optional[dict[str, Any]]:
        """根据角色名称查找专家。"""
        experts = self.expert_library.experts
        for expert_id, expert in experts.items():
            if (
                role_name in expert.name
                or role_name in expert.title
                or any(role_name in specialty for specialty in expert.specialties)
            ):
                return expert.to_dict()
        return None

    async def _execute_workflow(self, session_id: str):
        """执行指定会话的完整工作流。
        :param session_id: 会话ID
        """
        try:
            session = self.active_sessions[session_id]
            config = self.workflow_configs[session.workflow_type]
            session.started_at = datetime.now().isoformat()
            session.current_phase = WorkflowPhase.INITIALIZATION
            self._save_session(session)
            await self._send_welcome_message(session)
            for phase in config.phases[1:]:
                if phase == WorkflowPhase.COMPLETED:
                    break
                session.current_phase = phase
                self._save_session(session)
                await self._execute_phase(session, phase)
                await asyncio.sleep(2)
            session.current_phase = WorkflowPhase.COMPLETED
            session.completed_at = datetime.now().isoformat()
            self._save_session(session)
            await self._send_completion_message(session)
            self.logger.info(f"Workflow completed: {session_id}")
        except Exception as e:
            self.logger.error(
                f"Workflow execution failed for session {session_id}: {e}",
            )

    async def _send_welcome_message(self, session: WorkflowSession):
        """发送欢迎消息到聊天室。
        :param session: 会话对象
        """
        config = self.workflow_configs[session.workflow_type]
        if session.chat_room_id is None:
            raise ValueError("chat_room_id is required for sending welcome message.")
        welcome_message = f"""
🎉 欢迎来到 {config.name} 工作流！

📋 **工作流信息**
- 主题: {session.topic}
- 描述: {session.description}
- 预计时长: {config.estimated_duration} 分钟
- 参与者: {len(session.participants)} 人

🚀 **工作流阶段**
{self._format_phases(config.phases)}

💡 **开始协作**
请各位专家根据各自的专业领域，积极参与讨论和协作。系统将自动引导工作流进展。
        """
        await self.multi_role_chat.send_user_message(
            session.chat_room_id,
            welcome_message,
            "系统",
        )

    async def _execute_phase(self, session: WorkflowSession, phase: WorkflowPhase):
        """执行特定阶段的业务逻辑。
        :param session: 会话对象
        :param phase: 当前阶段
        """
        phase_messages = {
            WorkflowPhase.PARTICIPANT_ASSIGNMENT: "👥 参与者分配完成，开始专业讨论...",
            WorkflowPhase.DISCUSSION: "💬 进入深入讨论阶段，请各位专家发表观点...",
            WorkflowPhase.COLLABORATION: "🤝 进入协作阶段，请专家们协同工作...",
            WorkflowPhase.DECISION: "⚖️ 进入决策阶段，请专家们达成共识...",
            WorkflowPhase.DOCUMENTATION: "📝 进入文档化阶段，整理讨论成果...",
        }
        if session.chat_room_id is None:
            raise ValueError("chat_room_id is required for phase execution.")
        if phase in phase_messages:
            await self.multi_role_chat.send_user_message(
                session.chat_room_id,
                phase_messages[phase],
                "系统",
            )

    async def _send_completion_message(self, session: WorkflowSession):
        """发送工作流完成消息到聊天室。
        :param session: 会话对象
        """
        if session.chat_room_id is None:
            raise ValueError("chat_room_id is required for sending completion message.")
        completion_message = f"""
✅ **工作流完成**

🎯 主题: {session.topic}
📅 开始时间: {session.started_at}
⏰ 完成时间: {session.completed_at}

📊 **工作流统计**
- 总消息数: {self._get_message_count(session.chat_room_id)}
- 参与者数: {len(session.participants)}
- 工作流类型: {self.workflow_configs[session.workflow_type].name}

📋 **下一步**
工作流已完成，您可以：
1. 查看聊天记录和讨论成果
2. 导出协作文档
3. 创建新的工作流会话

感谢各位专家的参与和贡献！
        """
        await self.multi_role_chat.send_user_message(
            session.chat_room_id,
            completion_message,
            "系统",
        )

    def _format_phases(self, phases: list[WorkflowPhase]) -> str:
        """格式化阶段列表为可读字符串。"""
        phase_names = {
            WorkflowPhase.INITIALIZATION: "初始化",
            WorkflowPhase.PARTICIPANT_ASSIGNMENT: "参与者分配",
            WorkflowPhase.DISCUSSION: "讨论",
            WorkflowPhase.COLLABORATION: "协作",
            WorkflowPhase.DECISION: "决策",
            WorkflowPhase.DOCUMENTATION: "文档化",
            WorkflowPhase.COMPLETED: "完成",
        }
        return "\n".join([f"- {phase_names[phase]}" for phase in phases])

    def _get_message_count(self, chat_room_id: str) -> int:
        """获取聊天室消息数量。
        :param chat_room_id: 聊天室ID，必须为str
        :return: 消息数量
        """
        if chat_room_id is None:
            raise ValueError("chat_room_id is required for message count.")
        chat_room = self.multi_role_chat.get_chat_room(chat_room_id)
        return len(chat_room.messages) if chat_room else 0

    def get_workflow_types(self) -> list[dict[str, Any]]:
        """获取所有可用的工作流类型信息。"""
        return [
            {
                "type": config.workflow_type.value,
                "name": config.name,
                "description": config.description,
                "max_participants": config.max_participants,
                "estimated_duration": config.estimated_duration,
                "phases": [phase.value for phase in config.phases],
            }
            for config in self.workflow_configs.values()
        ]

    def get_session_info(self, session_id: str) -> dict[str, Any]:
        """获取指定会话的详细信息。
        :param session_id: 会话ID
        :return: 会话信息字典
        :raises KeyError: 如果会话不存在
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found.")
        config = self.workflow_configs[session.workflow_type]
        chat_room = (
            self.multi_role_chat.get_chat_room(session.chat_room_id)
            if session.chat_room_id
            else None
        )
        if session.current_phase == WorkflowPhase.COMPLETED:
            status = "completed"
        elif session.current_phase == WorkflowPhase.INITIALIZATION:
            status = "initializing"
        elif session.started_at:
            status = "active"
        else:
            status = "created"
        return {
            "session_id": session.session_id,
            "workflow_type": session.workflow_type.value,
            "workflow_name": config.name,
            "topic": session.topic,
            "description": session.description,
            "current_phase": session.current_phase.value,
            "status": status,
            "participants": len(session.participants),
            "chat_room_id": session.chat_room_id,
            "message_count": len(chat_room.messages) if chat_room else 0,
            "created_at": session.created_at,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "is_active": session.current_phase != WorkflowPhase.COMPLETED,
        }

    def get_all_sessions(self) -> list[dict[str, Any]]:
        """获取所有活跃会话的信息列表。
        :return: 会话信息字典列表
        """
        return [
            info
            for session_id in self.active_sessions.keys()
            for info in [self.get_session_info(session_id)]
            if info is not None
        ]

    def _save_session(self, session: WorkflowSession):
        """持久化保存会话信息到本地JSON文件。
        :param session: 会话对象
        """
        session_file = os.path.join(self.data_dir, f"{session.session_id}.json")
        session_dict = {
            "session_id": session.session_id,
            "workflow_type": session.workflow_type.value,
            "topic": session.topic,
            "description": session.description,
            "participants": session.participants,
            "chat_room_id": session.chat_room_id,
            "document_tasks": session.document_tasks,
            "current_phase": session.current_phase.value,
            "created_at": session.created_at,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "session_data": session.session_data,
        }
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_dict, f, ensure_ascii=False, indent=2)

    def _load_existing_sessions(self):
        """启动时加载历史会话。
        """
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                session_file = os.path.join(self.data_dir, filename)
                try:
                    with open(session_file, encoding="utf-8") as f:
                        session_data = json.load(f)
                    workflow_type = WorkflowType(session_data["workflow_type"])
                    current_phase = WorkflowPhase(session_data["current_phase"])
                    session = WorkflowSession(
                        session_id=session_data["session_id"],
                        workflow_type=workflow_type,
                        topic=session_data["topic"],
                        description=session_data["description"],
                        participants=session_data.get("participants", []),
                        chat_room_id=session_data.get("chat_room_id"),
                        document_tasks=session_data.get("document_tasks", []),
                        current_phase=current_phase,
                        created_at=session_data.get("created_at"),
                        started_at=session_data.get("started_at"),
                        completed_at=session_data.get("completed_at"),
                        session_data=session_data.get("session_data", {}),
                    )
                    self.active_sessions[session.session_id] = session
                except Exception as e:
                    self.logger.error(f"Failed to load session {filename}: {e}")
