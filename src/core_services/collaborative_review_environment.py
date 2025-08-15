"""@Time: 2025-08-03
@Author: DAIP-LIVE
@File: collaborative_review_environment.py
@Description: V0.3.5 协作评审环境 - Zen Mode Design 实时协作评审环境
"""

import asyncio
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
    from ..core_services.memory_agent import MemAgent
    from ..core_services.smart_reviewer_allocator import SmartReviewerAllocator


class ReviewActionType(Enum):
    """评审操作类型"""
    ADD_COMMENT = "add_comment"           # 添加评论
    ADD_ANNOTATION = "add_annotation"     # 添加标注
    SUGGEST_EDIT = "suggest_edit"         # 建议编辑
    REQUEST_CLARIFICATION = "request_clarification"  # 请求澄清
    APPROVE_SECTION = "approve_section"   # 批准章节
    FLAG_ISSUE = "flag_issue"             # 标记问题
    START_DISCUSSION = "start_discussion" # 开始讨论


class AnnotationType(Enum):
    """标注类型"""
    HIGHLIGHT = "highlight"              # 高亮
    UNDERLINE = "underline"              # 下划线
    STRIKETHROUGH = "strikethrough"      # 删除线
    COMMENT = "comment"                  # 评论
    QUESTION = "question"                # 问题
    SUGGESTION = "suggestion"            # 建议


class DiscussionStatus(Enum):
    """讨论状态"""
    ACTIVE = "active"                    # 活跃
    RESOLVED = "resolved"                # 已解决
    ARCHIVED = "archived"                # 已归档


@dataclass
class ReviewComment:
    """评审评论"""
    id: str
    reviewer_id: str
    content: str
    timestamp: datetime
    position: dict[str, int]  # {line_start, line_end, char_start, char_end}
    type: ReviewActionType
    parent_id: Optional[str] = None  # 父评论ID
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewAnnotation:
    """评审标注"""
    id: str
    reviewer_id: str
    type: AnnotationType
    content: str
    position: dict[str, int]  # {line_start, line_end, char_start, char_end}
    color: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscussionThread:
    """讨论线程"""
    id: str
    title: str
    description: str
    initiator_id: str
    participants: set[str]
    comments: list[ReviewComment]
    status: DiscussionStatus
    created_at: datetime
    last_activity: datetime
    related_sections: list[str]  # 相关章节ID
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewSession:
    """评审会话"""
    id: str
    review_request_id: str
    participants: list[str]
    content: str
    comments: list[ReviewComment]
    annotations: list[ReviewAnnotation]
    discussions: list[DiscussionThread]
    created_at: datetime
    last_activity: datetime
    status: str = "active"
    version_control: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationEvent:
    """协作事件"""
    id: str
    session_id: str
    event_type: str
    data: dict[str, Any]
    timestamp: datetime
    reviewer_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class CollaborativeReviewEnvironment:
    """协作评审环境 - Zen Mode Implementation"""
    
    def __init__(self, sskg_manager: Optional[Any] = None, 
                 memory_agent: Optional[Any] = None,
                 allocator: Optional[Any] = None):
        self.sskg_manager = sskg_manager
        self.memory_agent = memory_agent
        self.allocator = allocator
        self.logger = logging.getLogger(__name__)
        
        # 活跃会话
        self.active_sessions: dict[str, ReviewSession] = {}
        
        # 事件队列
        self.event_queues: dict[str, deque] = defaultdict(deque)
        
        # 用户在线状态
        self.user_presence: dict[str, dict[str, Any]] = {}
        
        # 版本控制
        self.version_history: dict[str, list[dict]] = defaultdict(list)
        
        # 通知系统
        self.notification_system = NotificationSystem()
        
        # 冲突解决
        self.conflict_resolver = ConflictResolver()
        
        # 后台任务
        self._start_background_tasks()
    
    async def create_review_session(self, 
                                  review_request_id: str,
                                  participants: list[str],
                                  content: str) -> ReviewSession:
        """创建评审会话"""
        try:
            session_id = str(uuid.uuid4())
            
            # 获取参与者信息
            participant_profiles = []
            for participant_id in participants:
                if participant_id in self.allocator.reviewer_profiles:
                    participant_profiles.append(
                        self.allocator.reviewer_profiles[participant_id]
                    )
            
            session = ReviewSession(
                id=session_id,
                review_request_id=review_request_id,
                participants=participants,
                content=content,
                comments=[],
                annotations=[],
                discussions=[],
                created_at=datetime.now(),
                last_activity=datetime.now(),
                version_control={
                    "current_version": 1,
                    "versions": [{
                        "version": 1,
                        "content": content,
                        "timestamp": datetime.now().isoformat(),
                        "author": "system"
                    }]
                }
            )
            
            self.active_sessions[session_id] = session
            
            # 初始化事件队列
            self.event_queues[session_id] = deque(maxlen=1000)
            
            # 记录创建事件
            await self._record_event(session_id, "session_created", {
                "participants": participants,
                "content_length": len(content)
            }, "system")
            
            # 通知参与者
            await self.notification_system.notify_participants(
                participants, 
                f"评审会话已创建: {session_id}"
            )
            
            self.logger.info(f"创建评审会话: {session_id} ({len(participants)}位参与者)")
            return session
            
        except Exception as e:
            self.logger.error(f"创建评审会话失败: {e}")
            raise
    
    async def add_comment(self, 
                         session_id: str,
                         reviewer_id: str,
                         content: str,
                         position: dict[str, int],
                         comment_type: ReviewActionType = ReviewActionType.ADD_COMMENT,
                         parent_id: Optional[str] = None) -> ReviewComment:
        """添加评论"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 创建评论
            comment = ReviewComment(
                id=str(uuid.uuid4()),
                reviewer_id=reviewer_id,
                content=content,
                timestamp=datetime.now(),
                position=position,
                type=comment_type,
                parent_id=parent_id
            )
            
            session.comments.append(comment)
            session.last_activity = datetime.now()
            
            # 记录事件
            await self._record_event(session_id, "comment_added", {
                "comment_id": comment.id,
                "reviewer_id": reviewer_id,
                "content_preview": content[:100],
                "position": position
            }, reviewer_id)
            
            # 实时广播给其他参与者
            await self._broadcast_event(session_id, "new_comment", {
                "comment": asdict(comment)
            }, exclude_reviewer=reviewer_id)
            
            # 检查是否需要创建讨论线程
            if comment_type in [ReviewActionType.REQUEST_CLARIFICATION, 
                               ReviewActionType.FLAG_ISSUE]:
                await self._create_discussion_from_comment(session, comment)
            
            self.logger.info(f"添加评论: {comment.id} by {reviewer_id}")
            return comment
            
        except Exception as e:
            self.logger.error(f"添加评论失败: {e}")
            raise
    
    async def add_annotation(self,
                           session_id: str,
                           reviewer_id: str,
                           annotation_type: AnnotationType,
                           content: str,
                           position: dict[str, int],
                           color: str = "#FFD700") -> ReviewAnnotation:
        """添加标注"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 创建标注
            annotation = ReviewAnnotation(
                id=str(uuid.uuid4()),
                reviewer_id=reviewer_id,
                type=annotation_type,
                content=content,
                position=position,
                color=color,
                timestamp=datetime.now()
            )
            
            session.annotations.append(annotation)
            session.last_activity = datetime.now()
            
            # 记录事件
            await self._record_event(session_id, "annotation_added", {
                "annotation_id": annotation.id,
                "reviewer_id": reviewer_id,
                "type": annotation_type.value,
                "position": position
            }, reviewer_id)
            
            # 实时广播
            await self._broadcast_event(session_id, "new_annotation", {
                "annotation": asdict(annotation)
            }, exclude_reviewer=reviewer_id)
            
            self.logger.info(f"添加标注: {annotation.id} by {reviewer_id}")
            return annotation
            
        except Exception as e:
            self.logger.error(f"添加标注失败: {e}")
            raise
    
    async def start_discussion(self,
                             session_id: str,
                             initiator_id: str,
                             title: str,
                             description: str,
                             related_sections: list[str] = None) -> DiscussionThread:
        """开始讨论"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            discussion = DiscussionThread(
                id=str(uuid.uuid4()),
                title=title,
                description=description,
                initiator_id=initiator_id,
                participants={initiator_id},
                comments=[],
                status=DiscussionStatus.ACTIVE,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                related_sections=related_sections or []
            )
            
            session.discussions.append(discussion)
            session.last_activity = datetime.now()
            
            # 记录事件
            await self._record_event(session_id, "discussion_started", {
                "discussion_id": discussion.id,
                "initiator_id": initiator_id,
                "title": title
            }, initiator_id)
            
            # 通知所有参与者
            await self._broadcast_event(session_id, "new_discussion", {
                "discussion": asdict(discussion)
            })
            
            self.logger.info(f"开始讨论: {discussion.id} by {initiator_id}")
            return discussion
            
        except Exception as e:
            self.logger.error(f"开始讨论失败: {e}")
            raise
    
    async def add_discussion_comment(self,
                                   session_id: str,
                                   discussion_id: str,
                                   reviewer_id: str,
                                   content: str) -> ReviewComment:
        """添加讨论评论"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 查找讨论
            discussion = None
            for d in session.discussions:
                if d.id == discussion_id:
                    discussion = d
                    break
            
            if not discussion:
                raise ValueError(f"讨论不存在: {discussion_id}")
            
            # 添加评论到讨论
            comment = ReviewComment(
                id=str(uuid.uuid4()),
                reviewer_id=reviewer_id,
                content=content,
                timestamp=datetime.now(),
                position={},
                type=ReviewActionType.ADD_COMMENT
            )
            
            discussion.comments.append(comment)
            discussion.participants.add(reviewer_id)
            discussion.last_activity = datetime.now()
            session.last_activity = datetime.now()
            
            # 记录事件
            await self._record_event(session_id, "discussion_comment_added", {
                "discussion_id": discussion_id,
                "comment_id": comment.id,
                "reviewer_id": reviewer_id
            }, reviewer_id)
            
            # 广播讨论更新
            await self._broadcast_event(session_id, "discussion_updated", {
                "discussion_id": discussion_id,
                "comment": asdict(comment)
            })
            
            self.logger.info(f"添加讨论评论: {comment.id} to {discussion_id}")
            return comment
            
        except Exception as e:
            self.logger.error(f"添加讨论评论失败: {e}")
            raise
    
    async def get_session_state(self, session_id: str) -> dict[str, Any]:
        """获取会话状态"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 获取参与者在线状态
            participants_status = {}
            for participant_id in session.participants:
                participants_status[participant_id] = self.user_presence.get(
                    participant_id, {"online": False, "last_seen": None}
                )
            
            state = {
                "session_id": session_id,
                "participants": session.participants,
                "participants_status": participants_status,
                "comments_count": len(session.comments),
                "annotations_count": len(session.annotations),
                "discussions_count": len(session.discussions),
                "last_activity": session.last_activity.isoformat(),
                "version": session.version_control["current_version"],
                "active_discussions": [
                    {
                        "id": d.id,
                        "title": d.title,
                        "participants": list(d.participants),
                        "status": d.status.value,
                        "last_activity": d.last_activity.isoformat()
                    }
                    for d in session.discussions 
                    if d.status == DiscussionStatus.ACTIVE
                ]
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"获取会话状态失败: {e}")
            raise
    
    async def get_session_events(self, 
                               session_id: str,
                               since_timestamp: Optional[datetime] = None) -> list[dict]:
        """获取会话事件"""
        try:
            if session_id not in self.event_queues:
                return []
            
            events = list(self.event_queues[session_id])
            
            if since_timestamp:
                events = [e for e in events if e["timestamp"] > since_timestamp]
            
            return events
            
        except Exception as e:
            self.logger.error(f"获取会话事件失败: {e}")
            return []
    
    async def resolve_conflict(self,
                             session_id: str,
                             conflict_id: str,
                             resolution: dict[str, Any]) -> bool:
        """解决冲突"""
        try:
            return await self.conflict_resolver.resolve_conflict(
                session_id, conflict_id, resolution
            )
            
        except Exception as e:
            self.logger.error(f"解决冲突失败: {e}")
            return False
    
    async def export_session_data(self, 
                                session_id: str,
                                format_type: str = "json") -> dict[str, Any]:
        """导出会话数据"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            export_data = {
                "session_info": {
                    "id": session.id,
                    "review_request_id": session.review_request_id,
                    "participants": session.participants,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "status": session.status
                },
                "comments": [asdict(comment) for comment in session.comments],
                "annotations": [asdict(annotation) for annotation in session.annotations],
                "discussions": [
                    {
                        "id": d.id,
                        "title": d.title,
                        "description": d.description,
                        "initiator_id": d.initiator_id,
                        "participants": list(d.participants),
                        "status": d.status.value,
                        "created_at": d.created_at.isoformat(),
                        "last_activity": d.last_activity.isoformat(),
                        "comments": [asdict(c) for c in d.comments],
                        "related_sections": d.related_sections
                    }
                    for d in session.discussions
                ],
                "version_history": session.version_control,
                "statistics": {
                    "total_comments": len(session.comments),
                    "total_annotations": len(session.annotations),
                    "total_discussions": len(session.discussions),
                    "active_participants": len([
                        p for p in session.participants 
                        if self.user_presence.get(p, {}).get("online", False)
                    ])
                }
            }
            
            if format_type == "json":
                return export_data
            else:
                # 可以扩展支持其他格式
                return export_data
                
        except Exception as e:
            self.logger.error(f"导出会话数据失败: {e}")
            raise
    
    async def _record_event(self, 
                           session_id: str,
                           event_type: str,
                           data: dict[str, Any],
                           reviewer_id: str):
        """记录事件"""
        try:
            event = CollaborationEvent(
                id=str(uuid.uuid4()),
                session_id=session_id,
                event_type=event_type,
                data=data,
                timestamp=datetime.now(),
                reviewer_id=reviewer_id
            )
            
            self.event_queues[session_id].append(asdict(event))
            
        except Exception as e:
            self.logger.error(f"记录事件失败: {e}")
    
    async def _broadcast_event(self,
                             session_id: str,
                             event_type: str,
                             data: dict[str, Any],
                             exclude_reviewer: Optional[str] = None):
        """广播事件给参与者"""
        try:
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions[session_id]
            
            # 发送给所有参与者（除了排除的）
            for participant_id in session.participants:
                if participant_id != exclude_reviewer:
                    await self.notification_system.send_notification(
                        participant_id, event_type, data
                    )
                    
        except Exception as e:
            self.logger.error(f"广播事件失败: {e}")
    
    async def _create_discussion_from_comment(self, 
                                           session: ReviewSession,
                                           comment: ReviewComment):
        """从评论创建讨论"""
        try:
            # 检查是否已有相关讨论
            for discussion in session.discussions:
                if discussion.status == DiscussionStatus.ACTIVE:
                    # 简单的相似度检查
                    if (comment.content[:50] in discussion.description or
                        abs(comment.position.get("line_start", 0) - 
                            discussion.related_sections[0] if discussion.related_sections else 0) < 10):
                        # 添加到现有讨论
                        discussion.comments.append(comment)
                        discussion.participants.add(comment.reviewer_id)
                        discussion.last_activity = datetime.now()
                        return
            
            # 创建新讨论
            discussion = DiscussionThread(
                id=str(uuid.uuid4()),
                title=f"讨论: {comment.content[:50]}...",
                description=comment.content,
                initiator_id=comment.reviewer_id,
                participants={comment.reviewer_id},
                comments=[comment],
                status=DiscussionStatus.ACTIVE,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                related_sections=[comment.position.get("line_start", 0)]
            )
            
            session.discussions.append(discussion)
            
            # 记录事件
            await self._record_event(session.id, "discussion_auto_created", {
                "discussion_id": discussion.id,
                "comment_id": comment.id
            }, comment.reviewer_id)
            
        except Exception as e:
            self.logger.error(f"从评论创建讨论失败: {e}")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        def cleanup_inactive_sessions():
            """清理不活跃会话"""
            while True:
                time.sleep(3600)  # 每小时检查一次
                try:
                    self._cleanup_inactive_sessions()
                except Exception as e:
                    self.logger.error(f"清理不活跃会话失败: {e}")
        
        def update_user_presence():
            """更新用户在线状态"""
            while True:
                time.sleep(300)  # 每5分钟更新一次
                try:
                    self._update_user_presence()
                except Exception as e:
                    self.logger.error(f"更新用户在线状态失败: {e}")
        
        # 启动后台线程
        cleanup_thread = threading.Thread(target=cleanup_inactive_sessions, daemon=True)
        presence_thread = threading.Thread(target=update_user_presence, daemon=True)
        
        cleanup_thread.start()
        presence_thread.start()
    
    def _cleanup_inactive_sessions(self):
        """清理不活跃会话"""
        try:
            inactive_threshold = datetime.now() - timedelta(hours=24)
            
            inactive_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.last_activity < inactive_threshold
            ]
            
            for session_id in inactive_sessions:
                session = self.active_sessions[session_id]
                session.status = "archived"
                
                self.logger.info(f"归档不活跃会话: {session_id}")
                
                # 从活跃会话中移除
                del self.active_sessions[session_id]
                
                # 保存到历史记录
                self.version_history[session_id].append({
                    "action": "archived",
                    "timestamp": datetime.now().isoformat(),
                    "reason": "inactive"
                })
                
        except Exception as e:
            self.logger.error(f"清理不活跃会话失败: {e}")
    
    def _update_user_presence(self):
        """更新用户在线状态"""
        try:
            current_time = datetime.now()
            
            for user_id, presence in self.user_presence.items():
                if presence.get("online", False):
                    last_seen = presence.get("last_seen")
                    if last_seen and (current_time - last_seen) > timedelta(minutes=10):
                        presence["online"] = False
                        presence["last_seen"] = current_time
                        
        except Exception as e:
            self.logger.error(f"更新用户在线状态失败: {e}")
    
    async def get_environment_statistics(self) -> dict[str, Any]:
        """获取环境统计信息"""
        try:
            stats = {
                "active_sessions": len(self.active_sessions),
                "total_participants": sum(len(s.participants) for s in self.active_sessions.values()),
                "total_comments": sum(len(s.comments) for s in self.active_sessions.values()),
                "total_annotations": sum(len(s.annotations) for s in self.active_sessions.values()),
                "total_discussions": sum(len(s.discussions) for s in self.active_sessions.values()),
                "online_users": sum(1 for p in self.user_presence.values() if p.get("online", False)),
                "recent_events": sum(len(q) for q in self.event_queues.values()),
                "session_status": {
                    "active": len([s for s in self.active_sessions.values() if s.status == "active"]),
                    "archived": len(self.version_history)
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取环境统计失败: {e}")
            return {}


class NotificationSystem:
    """通知系统"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification_handlers = {}
    
    async def notify_participants(self, participants: list[str], message: str):
        """通知参与者"""
        for participant_id in participants:
            await self.send_notification(participant_id, "system_message", {
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
    
    async def send_notification(self, user_id: str, event_type: str, data: dict[str, Any]):
        """发送通知"""
        try:
            # 这里可以实现不同的通知方式
            # WebSocket, Email, SMS, etc.
            
            self.logger.info(f"发送通知给 {user_id}: {event_type}")
            
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")


class ConflictResolver:
    """冲突解决器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_conflicts = {}
    
    async def resolve_conflict(self, 
                             session_id: str,
                             conflict_id: str,
                             resolution: dict[str, Any]) -> bool:
        """解决冲突"""
        try:
            if conflict_id in self.active_conflicts:
                # 应用解决方案
                conflict = self.active_conflicts[conflict_id]
                conflict["resolution"] = resolution
                conflict["resolved_at"] = datetime.now().isoformat()
                conflict["status"] = "resolved"
                
                # 从活跃冲突中移除
                del self.active_conflicts[conflict_id]
                
                self.logger.info(f"解决冲突: {conflict_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"解决冲突失败: {e}")
            return False


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    sskg_manager = EnhancedSSKGManager()
    memory_agent = MemAgent()
    allocator = SmartReviewerAllocator(None, sskg_manager, memory_agent)
    
    # 创建协作环境
    environment = CollaborativeReviewEnvironment(sskg_manager, memory_agent, allocator)
    
    # 创建评审会话
    session = await environment.create_review_session(
        review_request_id="review_001",
        participants=["reviewer_001", "reviewer_002", "reviewer_003"],
        content="这是待评审的文档内容..."
    )
    
    print(f"创建评审会话: {session.id}")
    
    # 添加评论
    comment = await environment.add_comment(
        session_id=session.id,
        reviewer_id="reviewer_001",
        content="这里需要更多的技术细节",
        position={"line_start": 10, "line_end": 15, "char_start": 0, "char_end": 50}
    )
    
    print(f"添加评论: {comment.id}")
    
    # 添加标注
    annotation = await environment.add_annotation(
        session_id=session.id,
        reviewer_id="reviewer_002",
        annotation_type=AnnotationType.HIGHLIGHT,
        content="重要部分",
        position={"line_start": 20, "line_end": 25, "char_start": 0, "char_end": 30},
        color="#FFD700"
    )
    
    print(f"添加标注: {annotation.id}")
    
    # 开始讨论
    discussion = await environment.start_discussion(
        session_id=session.id,
        initiator_id="reviewer_003",
        title="关于实现方案的讨论",
        description="我们需要讨论这个实现方案是否合适",
        related_sections=["section_1", "section_2"]
    )
    
    print(f"开始讨论: {discussion.id}")
    
    # 获取会话状态
    state = await environment.get_session_state(session.id)
    print(f"会话状态: {state['participants_count']} 位参与者")
    
    # 获取统计信息
    stats = await environment.get_environment_statistics()
    print(f"环境统计: {stats['active_sessions']} 个活跃会话")


if __name__ == "__main__":
    asyncio.run(example_usage())