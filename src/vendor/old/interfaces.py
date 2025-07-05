"""系统统一接口定义
定义各组件间的标准接口，实现解耦和一致性
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class UnifiedRole:
    """统一的角色数据模型"""

    id: str
    name: str
    title: str
    category: str
    specialties: list[str]
    description: str
    bio: str
    skills: list[str]
    experience_years: int
    reputation_score: float
    contact_info: dict[str, str]
    languages: list[str]
    availability: str
    location: str
    education: list[str]
    certifications: list[str]
    projects: list[str]
    hourly_rate: Optional[float] = None
    source_file: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        from dataclasses import asdict

        return asdict(self)

    def to_expert_dict(self) -> dict[str, Any]:
        """转换为ExpertLibrary兼容的字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "category": self.category,
            "specialties": self.specialties,
            "description": self.description,
            "experience_years": self.experience_years,
            "reputation_score": self.reputation_score,
            "contact_info": self.contact_info,
            "skills": self.skills,
            "languages": self.languages,
            "availability": self.availability,
            "hourly_rate": self.hourly_rate,
            "location": self.location,
            "education": self.education,
            "certifications": self.certifications,
            "projects": self.projects,
            "bio": self.bio,
            "source_file": self.source_file,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_role_identity_data(self) -> dict[str, Any]:
        """转换为RoleIdentity兼容的数据格式"""
        return {
            "id": self.id,
            "role_id": self.id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "bio": self.bio,
            "specialties": self.specialties,
            "skills": self.skills,
            "category": self.category,
            "experience_years": self.experience_years,
            "reputation_score": self.reputation_score,
        }


@dataclass
class MemoryEntry:
    """统一的记忆条目"""

    id: str
    role_id: str
    content: str
    memory_type: str  # identity, project, dialogue, experience, knowledge
    importance: float  # 0.0-1.0
    timestamp: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConversationContext:
    """对话上下文"""

    role_identity: dict[str, Any]
    relevant_memories: list[dict[str, Any]]
    project_context: Optional[dict[str, Any]]
    conversation_summary: str
    prompt: str
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchCriteria:
    """搜索条件"""

    query: Optional[str] = None
    category: Optional[str] = None
    skills: Optional[list[str]] = None
    min_experience: Optional[int] = None
    min_reputation: Optional[float] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    limit: int = 10
    offset: int = 0


@dataclass
class MemoryFilters:
    """记忆过滤条件"""

    memory_types: Optional[list[str]] = None
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    min_importance: float = 0.0
    tags: Optional[list[str]] = None
    limit: int = 10
    query: Optional[str] = None


@dataclass
class RecommendationContext:
    """推荐上下文"""

    topic: str
    current_participants: list[str] = None
    desired_expertise: list[str] = None
    exclude_recent: bool = True
    diversity_factor: float = 0.7
    count: int = 6

    def __post_init__(self):
        if self.current_participants is None:
            self.current_participants = []
        if self.desired_expertise is None:
            self.desired_expertise = []


class IMemoryService(ABC):
    """记忆服务接口"""

    @abstractmethod
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

    @abstractmethod
    def retrieve_memories(
        self,
        role_id: str,
        filters: MemoryFilters,
    ) -> list[MemoryEntry]:
        """检索记忆"""

    @abstractmethod
    def build_context(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
    ) -> ConversationContext:
        """构建对话上下文"""

    @abstractmethod
    def add_dialogue_memory(
        self,
        role_id: str,
        user_message: str,
        role_response: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """添加对话记忆"""

    @abstractmethod
    def create_project_context(
        self,
        project_name: str,
        description: str,
        participants: list[str],
    ) -> str:
        """创建项目上下文"""


class IRoleService(ABC):
    """角色服务接口"""

    @abstractmethod
    def get_role(self, role_id: str) -> Optional[UnifiedRole]:
        """获取角色信息"""

    @abstractmethod
    def search_roles(self, criteria: SearchCriteria) -> list[UnifiedRole]:
        """搜索角色"""

    @abstractmethod
    def get_all_roles(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[UnifiedRole]:
        """获取所有角色"""

    @abstractmethod
    def create_role_identity(self, role_data: dict[str, Any]) -> str:
        """创建角色身份"""

    @abstractmethod
    def update_role(self, role_id: str, updates: dict[str, Any]) -> bool:
        """更新角色信息"""


class IRecommendationService(ABC):
    """推荐服务接口"""

    @abstractmethod
    def recommend_roles(self, context: RecommendationContext) -> list[UnifiedRole]:
        """推荐角色"""

    @abstractmethod
    def get_random_roles(
        self,
        count: int = 6,
        category: Optional[str] = None,
    ) -> list[UnifiedRole]:
        """获取随机角色"""

    @abstractmethod
    def calculate_role_relevance(self, role: UnifiedRole, topic: str) -> float:
        """计算角色相关性"""


class IChatService(ABC):
    """聊天服务接口"""

    @abstractmethod
    def create_room(
        self,
        room_name: str,
        topic: str,
        initial_participants: Optional[list[str]] = None,
    ) -> str:
        """创建聊天室"""

    @abstractmethod
    def add_participant(self, room_id: str, role_id: str) -> bool:
        """添加参与者"""

    @abstractmethod
    def remove_participant(self, room_id: str, role_id: str) -> bool:
        """移除参与者"""

    @abstractmethod
    async def send_message(
        self,
        room_id: str,
        content: str,
        sender_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """发送消息并获取角色响应"""

    @abstractmethod
    def get_room_info(self, room_id: str) -> Optional[dict[str, Any]]:
        """获取聊天室信息"""

    @abstractmethod
    def get_room_history(self, room_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """获取聊天历史"""


class IModelService(ABC):
    """模型服务接口"""

    @abstractmethod
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

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """获取可用模型列表"""

    @abstractmethod
    def setup_model(self, model_name: str, config: dict[str, Any]) -> bool:
        """设置模型"""
