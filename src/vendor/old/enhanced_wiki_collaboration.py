"""增强的Wiki协同编辑系统
集成智能专家推荐、角色权限管理、编辑历史追踪等功能
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from src.dynamic_role_manager import DynamicRoleManager, TaskContext
from src.enhanced_recommendation_engine import EnhancedRecommendationEngine
from src.expert_library import ExpertLibrary


class WikiPermission(Enum):
    """Wiki权限类型"""

    READ = "read"
    COMMENT = "comment"
    EDIT = "edit"
    REVIEW = "review"
    ADMIN = "admin"


class EditStatus(Enum):
    """编辑状态"""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


@dataclass
class WikiRole:
    """Wiki角色定义"""

    role_id: str
    expert_id: str
    expert_name: str
    permissions: list[WikiPermission]
    specialties: list[str]
    reputation_score: float
    contribution_count: int = 0
    last_activity: Optional[str] = None


@dataclass
class WikiEdit:
    """Wiki编辑记录"""

    edit_id: str
    entry_name: str
    editor_id: str
    editor_name: str
    content: str
    edit_type: str  # create, update, delete
    timestamp: str
    status: EditStatus
    review_comments: list[dict[str, Any]]
    version: int
    diff_summary: str
    tags: list[str]


@dataclass
class WikiEntry:
    """Wiki条目"""

    entry_id: str
    name: str
    current_content: str
    current_version: int
    created_by: str
    created_at: str
    last_modified: str
    last_editor: str
    status: str
    tags: list[str]
    category: str
    edit_history: list[WikiEdit]
    permissions: dict[str, list[WikiPermission]]
    collaboration_metadata: dict[str, Any]


class EnhancedWikiCollaboration:
    """增强的Wiki协同编辑系统"""

    def __init__(self, data_dir: str = "data/wiki"):
        self.data_dir = data_dir
        self.entries_dir = os.path.join(data_dir, "entries")
        self.roles_dir = os.path.join(data_dir, "roles")
        self.permissions_file = os.path.join(data_dir, "permissions.json")

        # 确保目录存在
        os.makedirs(self.entries_dir, exist_ok=True)
        os.makedirs(self.roles_dir, exist_ok=True)

        # 初始化组件
        self.expert_library = ExpertLibrary()
        self.dynamic_role_manager = DynamicRoleManager(self.expert_library)
        self.recommendation_engine = EnhancedRecommendationEngine(self.expert_library)

        # 加载数据
        self.wiki_entries: dict[str, WikiEntry] = self._load_wiki_entries()
        self.wiki_roles: dict[str, WikiRole] = self._load_wiki_roles()
        self.global_permissions = self._load_global_permissions()

        self.logger = logging.getLogger(__name__)

    def _load_wiki_entries(self) -> dict[str, WikiEntry]:
        """加载Wiki条目"""
        entries = {}
        if os.path.exists(self.entries_dir):
            for filename in os.listdir(self.entries_dir):
                if filename.endswith(".json"):
                    entry_path = os.path.join(self.entries_dir, filename)
                    try:
                        with open(entry_path, encoding="utf-8") as f:
                            data = json.load(f)

                        # 转换为WikiEntry对象
                        entry = WikiEntry(**data)
                        entries[entry.entry_id] = entry
                    except Exception as e:
                        self.logger.error(f"Failed to load wiki entry {filename}: {e}")
        return entries

    def _load_wiki_roles(self) -> dict[str, WikiRole]:
        """加载Wiki角色"""
        roles = {}
        if os.path.exists(self.roles_dir):
            for filename in os.listdir(self.roles_dir):
                if filename.endswith(".json"):
                    role_path = os.path.join(self.roles_dir, filename)
                    try:
                        with open(role_path, encoding="utf-8") as f:
                            data = json.load(f)

                        # 转换权限枚举
                        data["permissions"] = [
                            WikiPermission(p) for p in data["permissions"]
                        ]
                        role = WikiRole(**data)
                        roles[role.role_id] = role
                    except Exception as e:
                        self.logger.error(f"Failed to load wiki role {filename}: {e}")
        return roles

    def _load_global_permissions(self) -> dict[str, Any]:
        """加载全局权限配置"""
        if os.path.exists(self.permissions_file):
            try:
                with open(self.permissions_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load permissions: {e}")

        # 默认权限配置
        return {
            "default_permissions": {
                "expert": [
                    WikiPermission.READ.value,
                    WikiPermission.COMMENT.value,
                    WikiPermission.EDIT.value,
                ],
                "reviewer": [
                    WikiPermission.READ.value,
                    WikiPermission.COMMENT.value,
                    WikiPermission.REVIEW.value,
                ],
                "admin": [p.value for p in WikiPermission],
            },
            "entry_specific_permissions": {},
            "role_hierarchy": {
                "admin": 5,
                "reviewer": 4,
                "expert": 3,
                "contributor": 2,
                "reader": 1,
            },
        }

    def recommend_experts_for_entry(
        self,
        entry_name: str,
        topic: str,
        required_skills: list[str] = None,
        max_experts: int = 5,
    ) -> list[dict[str, Any]]:
        """为Wiki条目推荐合适的专家"""
        if required_skills is None:
            required_skills = []

        # 创建任务上下文
        task_context = TaskContext(
            task_id=f"wiki_edit_{entry_name}",
            task_type="编辑",
            domain="知识管理",
            complexity="中等",
            required_skills=required_skills,
            preferred_skills=[],
            collaboration_type="协同编辑",
        )

        # 获取推荐专家
        recommended_experts = self.dynamic_role_manager.load_roles_for_task(
            task_context,
            max_roles=max_experts,
        )

        # 增强推荐信息
        enhanced_recommendations = []
        for expert in recommended_experts:
            # 计算专家与主题的相关性
            relevance_score = self.recommendation_engine.calculate_relevance_score(
                expert,
                topic,
            )

            expert_info = {
                "expert_id": expert["id"],
                "name": expert["name"],
                "title": expert.get("title", ""),
                "specialties": expert.get("specialties", []),
                "skills": expert.get("skills", []),
                "relevance_score": relevance_score,
                "reputation_score": expert.get("reputation_score", 0.5),
                "recommended_permissions": self._suggest_permissions_for_expert(
                    expert,
                    topic,
                ),
                "contribution_potential": self._calculate_contribution_potential(
                    expert,
                    topic,
                ),
            }
            enhanced_recommendations.append(expert_info)

        return enhanced_recommendations

    def _suggest_permissions_for_expert(
        self,
        expert: dict[str, Any],
        topic: str,
    ) -> list[str]:
        """为专家建议合适的权限"""
        permissions = [WikiPermission.READ.value, WikiPermission.COMMENT.value]

        # 基于专家经验和声誉建议权限
        reputation = expert.get("reputation_score", 0.5)
        experience_years = expert.get("experience_years", 0)

        if reputation >= 0.8 or experience_years >= 10:
            permissions.extend([WikiPermission.EDIT.value, WikiPermission.REVIEW.value])
        elif reputation >= 0.6 or experience_years >= 5:
            permissions.append(WikiPermission.EDIT.value)

        return permissions

    def _calculate_contribution_potential(
        self,
        expert: dict[str, Any],
        topic: str,
    ) -> float:
        """计算专家的贡献潜力"""
        # 基于多个因素计算贡献潜力
        factors = {
            "relevance": self.recommendation_engine.calculate_relevance_score(
                expert,
                topic,
            ),
            "reputation": expert.get("reputation_score", 0.5),
            "activity": min(expert.get("recent_activity_score", 0.5), 1.0),
            "collaboration": expert.get("collaboration_score", 0.5),
        }

        # 加权计算
        weights = {
            "relevance": 0.4,
            "reputation": 0.3,
            "activity": 0.2,
            "collaboration": 0.1,
        }
        potential = sum(factors[key] * weights[key] for key in factors)

        return min(potential, 1.0)

    def create_wiki_entry(
        self,
        name: str,
        initial_content: str,
        creator_id: str,
        category: str = "general",
        tags: list[str] = None,
    ) -> str:
        """创建新的Wiki条目"""
        if tags is None:
            tags = []

        entry_id = f"wiki_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()

        # 创建初始编辑记录
        initial_edit = WikiEdit(
            edit_id=f"edit_{uuid.uuid4().hex[:8]}",
            entry_name=name,
            editor_id=creator_id,
            editor_name=self._get_expert_name(creator_id),
            content=initial_content,
            edit_type="create",
            timestamp=timestamp,
            status=EditStatus.PUBLISHED,
            review_comments=[],
            version=1,
            diff_summary="Initial creation",
            tags=tags,
        )

        # 创建Wiki条目
        wiki_entry = WikiEntry(
            entry_id=entry_id,
            name=name,
            current_content=initial_content,
            current_version=1,
            created_by=creator_id,
            created_at=timestamp,
            last_modified=timestamp,
            last_editor=creator_id,
            status="active",
            tags=tags,
            category=category,
            edit_history=[initial_edit],
            permissions={},
            collaboration_metadata={
                "total_edits": 1,
                "contributors": [creator_id],
                "last_activity": timestamp,
            },
        )

        # 保存条目
        self.wiki_entries[entry_id] = wiki_entry
        self._save_wiki_entry(wiki_entry)

        self.logger.info(f"Created wiki entry: {name} (ID: {entry_id})")
        return entry_id

    def edit_wiki_entry(
        self,
        entry_id: str,
        new_content: str,
        editor_id: str,
        edit_summary: str = "",
        tags: list[str] = None,
    ) -> bool:
        """编辑Wiki条目"""
        if entry_id not in self.wiki_entries:
            return False

        if not self._check_permission(editor_id, entry_id, WikiPermission.EDIT):
            self.logger.warning(
                f"User {editor_id} lacks edit permission for entry {entry_id}",
            )
            return False

        if tags is None:
            tags = []

        entry = self.wiki_entries[entry_id]
        timestamp = datetime.now().isoformat()

        # 创建编辑记录
        edit_record = WikiEdit(
            edit_id=f"edit_{uuid.uuid4().hex[:8]}",
            entry_name=entry.name,
            editor_id=editor_id,
            editor_name=self._get_expert_name(editor_id),
            content=new_content,
            edit_type="update",
            timestamp=timestamp,
            status=EditStatus.PENDING_REVIEW
            if self._requires_review(entry_id, editor_id)
            else EditStatus.PUBLISHED,
            review_comments=[],
            version=entry.current_version + 1,
            diff_summary=edit_summary
            or self._generate_diff_summary(entry.current_content, new_content),
            tags=tags,
        )

        # 更新条目
        if edit_record.status == EditStatus.PUBLISHED:
            entry.current_content = new_content
            entry.current_version += 1

        entry.edit_history.append(edit_record)
        entry.last_modified = timestamp
        entry.last_editor = editor_id

        # 更新协作元数据
        if editor_id not in entry.collaboration_metadata["contributors"]:
            entry.collaboration_metadata["contributors"].append(editor_id)
        entry.collaboration_metadata["total_edits"] += 1
        entry.collaboration_metadata["last_activity"] = timestamp

        # 保存更新
        self._save_wiki_entry(entry)

        self.logger.info(
            f"Wiki entry {entry.name} edited by {self._get_expert_name(editor_id)}",
        )
        return True

    def review_edit(
        self,
        entry_id: str,
        edit_id: str,
        reviewer_id: str,
        decision: str,
        comments: str = "",
    ) -> bool:
        """审核编辑"""
        if entry_id not in self.wiki_entries:
            return False

        if not self._check_permission(reviewer_id, entry_id, WikiPermission.REVIEW):
            return False

        entry = self.wiki_entries[entry_id]
        edit_record = None

        # 找到对应的编辑记录
        for edit in entry.edit_history:
            if edit.edit_id == edit_id:
                edit_record = edit
                break

        if not edit_record or edit_record.status != EditStatus.PENDING_REVIEW:
            return False

        # 添加审核评论
        review_comment = {
            "reviewer_id": reviewer_id,
            "reviewer_name": self._get_expert_name(reviewer_id),
            "decision": decision,
            "comments": comments,
            "timestamp": datetime.now().isoformat(),
        }
        edit_record.review_comments.append(review_comment)

        # 更新状态
        if decision == "approve":
            edit_record.status = EditStatus.APPROVED
            # 应用编辑到当前内容
            entry.current_content = edit_record.content
            entry.current_version = edit_record.version
        elif decision == "reject":
            edit_record.status = EditStatus.REJECTED

        self._save_wiki_entry(entry)
        return True

    def get_edit_history(self, entry_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """获取编辑历史"""
        if entry_id not in self.wiki_entries:
            return []

        entry = self.wiki_entries[entry_id]
        history = []

        for edit in sorted(entry.edit_history, key=lambda x: x.timestamp, reverse=True)[
            :limit
        ]:
            history.append(
                {
                    "edit_id": edit.edit_id,
                    "editor_name": edit.editor_name,
                    "timestamp": edit.timestamp,
                    "edit_type": edit.edit_type,
                    "status": edit.status.value,
                    "version": edit.version,
                    "diff_summary": edit.diff_summary,
                    "tags": edit.tags,
                    "review_comments": edit.review_comments,
                },
            )

        return history

    def get_collaboration_stats(self, entry_id: str) -> dict[str, Any]:
        """获取协作统计信息"""
        if entry_id not in self.wiki_entries:
            return {}

        entry = self.wiki_entries[entry_id]

        # 计算贡献者统计
        contributor_stats = {}
        for edit in entry.edit_history:
            editor_id = edit.editor_id
            if editor_id not in contributor_stats:
                contributor_stats[editor_id] = {
                    "name": edit.editor_name,
                    "edit_count": 0,
                    "first_contribution": edit.timestamp,
                    "last_contribution": edit.timestamp,
                }

            contributor_stats[editor_id]["edit_count"] += 1
            if edit.timestamp > contributor_stats[editor_id]["last_contribution"]:
                contributor_stats[editor_id]["last_contribution"] = edit.timestamp

        return {
            "total_contributors": len(contributor_stats),
            "total_edits": len(entry.edit_history),
            "current_version": entry.current_version,
            "created_at": entry.created_at,
            "last_modified": entry.last_modified,
            "contributor_details": list(contributor_stats.values()),
            "collaboration_metadata": entry.collaboration_metadata,
        }

    def _get_expert_name(self, expert_id: str) -> str:
        """获取专家姓名"""
        expert = self.expert_library.get_expert_by_id(expert_id)
        return expert["name"] if expert else f"Unknown_{expert_id}"

    def _check_permission(
        self,
        user_id: str,
        entry_id: str,
        required_permission: WikiPermission,
    ) -> bool:
        """检查用户权限"""
        # 检查用户是否有Wiki角色
        user_role = None
        for role in self.wiki_roles.values():
            if role.expert_id == user_id:
                user_role = role
                break

        if not user_role:
            return False

        # 检查全局权限
        if required_permission in user_role.permissions:
            return True

        # 检查条目特定权限
        if entry_id in self.wiki_entries:
            entry = self.wiki_entries[entry_id]
            if user_id in entry.permissions:
                return required_permission in entry.permissions[user_id]

        return False

    def _requires_review(self, entry_id: str, editor_id: str) -> bool:
        """判断编辑是否需要审核"""
        # 新用户或低声誉用户需要审核
        user_role = None
        for role in self.wiki_roles.values():
            if role.expert_id == editor_id:
                user_role = role
                break

        if not user_role:
            return True

        # 高声誉用户可以直接发布
        if user_role.reputation_score >= 0.8:
            return False

        # 有审核权限的用户可以直接发布
        if WikiPermission.REVIEW in user_role.permissions:
            return False

        return True

    def _generate_diff_summary(self, old_content: str, new_content: str) -> str:
        """生成差异摘要"""
        # 简单的差异检测
        old_lines = old_content.split("\n")
        new_lines = new_content.split("\n")

        added_lines = len(new_lines) - len(old_lines)

        if added_lines > 0:
            return f"Added {added_lines} lines"
        elif added_lines < 0:
            return f"Removed {abs(added_lines)} lines"
        else:
            return "Content modified"

    def _save_wiki_entry(self, entry: WikiEntry):
        """保存Wiki条目到文件"""
        entry_path = os.path.join(self.entries_dir, f"{entry.entry_id}.json")

        # 转换为可序列化的格式
        entry_data = asdict(entry)

        # 处理枚举类型
        for edit in entry_data["edit_history"]:
            edit["status"] = (
                edit["status"].value
                if hasattr(edit["status"], "value")
                else edit["status"]
            )

        with open(entry_path, "w", encoding="utf-8") as f:
            json.dump(entry_data, f, ensure_ascii=False, indent=2)

    def assign_role_to_entry(
        self,
        entry_id: str,
        expert_id: str,
        permissions: list[WikiPermission],
    ) -> bool:
        """为条目分配专家角色"""
        if entry_id not in self.wiki_entries:
            return False

        expert = self.expert_library.get_expert_by_id(expert_id)
        if not expert:
            return False

        # 创建或更新Wiki角色
        role_id = f"wiki_role_{expert_id}_{entry_id}"

        wiki_role = WikiRole(
            role_id=role_id,
            expert_id=expert_id,
            expert_name=expert["name"],
            permissions=permissions,
            specialties=expert.get("specialties", []),
            reputation_score=expert.get("reputation_score", 0.5),
            contribution_count=0,
            last_activity=datetime.now().isoformat(),
        )

        self.wiki_roles[role_id] = wiki_role

        # 更新条目权限
        entry = self.wiki_entries[entry_id]
        entry.permissions[expert_id] = permissions

        self._save_wiki_entry(entry)
        self._save_wiki_role(wiki_role)

        return True

    def _save_wiki_role(self, role: WikiRole):
        """保存Wiki角色"""
        role_path = os.path.join(self.roles_dir, f"{role.role_id}.json")

        role_data = asdict(role)
        role_data["permissions"] = [p.value for p in role.permissions]

        with open(role_path, "w", encoding="utf-8") as f:
            json.dump(role_data, f, ensure_ascii=False, indent=2)

    def get_recommended_workflow(self, entry_name: str, topic: str) -> dict[str, Any]:
        """获取推荐的协作工作流"""
        # 推荐专家
        recommended_experts = self.recommend_experts_for_entry(entry_name, topic)

        # 生成工作流步骤
        workflow_steps = [
            {
                "step": "expert_assignment",
                "description": "分配专家角色",
                "recommended_experts": recommended_experts[:3],
                "estimated_time": "1-2 hours",
            },
            {
                "step": "collaborative_editing",
                "description": "协同编辑阶段",
                "participants": "all_assigned_experts",
                "estimated_time": "2-5 days",
            },
            {
                "step": "peer_review",
                "description": "同行评议",
                "reviewers": recommended_experts[3:5]
                if len(recommended_experts) > 3
                else [],
                "estimated_time": "1-2 days",
            },
            {
                "step": "consensus_building",
                "description": "共识建立",
                "method": "discussion_and_voting",
                "estimated_time": "1 day",
            },
            {
                "step": "final_publication",
                "description": "最终发布",
                "approver": "senior_expert",
                "estimated_time": "1 hour",
            },
        ]

        return {
            "entry_name": entry_name,
            "topic": topic,
            "recommended_experts": recommended_experts,
            "workflow_steps": workflow_steps,
            "estimated_total_time": "5-10 days",
            "collaboration_mode": "asynchronous_with_sync_checkpoints",
        }
