"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : session_manager.py
@Description:
    Session Manager - Manages user sessions across different entrance types.
    Handles session creation, lifecycle management, and state persistence.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from ..domain.aggregates import SessionAggregate, TaskAggregate
from ..domain.entities import Message, User
from ..domain.value_objects import (
    EntranceType,
    SessionStatus,
)


class SessionState(Enum):
    """会话状态枚举"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ERROR = "error"


class SessionEventType(Enum):
    """会话事件类型枚举"""
    CREATED = "session_created"
    STARTED = "session_started"
    PAUSED = "session_paused"
    RESUMED = "session_resumed"
    COMPLETED = "session_completed"
    EXPIRED = "session_expired"
    ERROR = "session_error"
    TASK_ADDED = "task_added"
    TASK_COMPLETED = "task_completed"
    MESSAGE_ADDED = "message_added"
    ENTRANCE_SWITCHED = "entrance_switched"


@dataclass
class SessionEvent:
    """会话事件"""
    event_id: str
    event_type: SessionEventType
    session_id: str
    user_id: str
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


@dataclass
class SessionConfig:
    """会话配置"""
    max_duration_hours: int = 24
    max_tasks_per_session: int = 50
    max_messages_per_session: int = 1000
    enable_persistence: bool = True
    auto_cleanup_enabled: bool = True
    cleanup_interval_minutes: int = 60
    enable_event_logging: bool = True
    max_event_history: int = 1000


class SessionManager:
    """会话管理器 - 管理不同入口类型的用户会话"""
    
    def __init__(self, config: SessionConfig = None):
        self.config = config or SessionConfig()
        
        # 会话存储
        self.sessions: dict[str, SessionAggregate] = {}
        self.user_sessions: dict[str, set[str]] = {}  # user_id -> session_ids
        
        # 事件历史
        self.event_history: list[SessionEvent] = []
        
        # 统计信息
        self.stats = {
            "total_sessions_created": 0,
            "active_sessions": 0,
            "completed_sessions": 0,
            "expired_sessions": 0,
            "total_tasks_created": 0,
            "total_messages_sent": 0,
            "start_time": datetime.now()
        }
        
        # 会话状态监听器
        self.session_listeners: dict[str, list[callable]] = {}
        
        # 后台任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._persistence_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start(self):
        """启动会话管理器"""
        if self._is_running:
            return
        
        self._is_running = True
        
        # 启动后台任务
        if self.config.auto_cleanup_enabled:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        
        if self.config.enable_persistence:
            self._persistence_task = asyncio.create_task(self._persist_session_data())
        
        logging.info("Session Manager started")
    
    async def stop(self):
        """停止会话管理器"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # 取消后台任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        if self._persistence_task:
            self._persistence_task.cancel()
        
        # 完成所有活跃会话
        for session_aggregate in self.sessions.values():
            try:
                session_aggregate.complete()
                await self._record_event(SessionEventType.COMPLETED, session_aggregate.session_id, 
                                       session_aggregate.user_id, {"reason": "manager_shutdown"})
            except Exception as e:
                logging.error(f"Error completing session {session_aggregate.session_id}: {e}")
        
        logging.info("Session Manager stopped")
    
    async def create_session(self, user: User, entrance_type: EntranceType, 
                           session_config: dict[str, Any] = None) -> SessionAggregate:
        """创建新会话"""
        # 检查用户会话数量限制
        user_session_count = len(self.user_sessions.get(user.user_id, set()))
        if user_session_count >= 10:  # 每个用户最多10个会话
            raise ValueError(f"User {user.user_id} has reached maximum session limit")
        
        # 创建会话聚合
        session_aggregate = SessionAggregate(
            user_id=user.user_id,
            entrance_type=entrance_type
        )
        
        # 应用配置
        if session_config:
            for key, value in session_config.items():
                session_aggregate.update_metadata(key, value)
        
        # 保存会话
        self.sessions[session_aggregate.session_id] = session_aggregate
        
        # 更新用户会话映射
        if user.user_id not in self.user_sessions:
            self.user_sessions[user.user_id] = set()
        self.user_sessions[user.user_id].add(session_aggregate.session_id)
        
        # 更新统计
        self.stats["total_sessions_created"] += 1
        self.stats["active_sessions"] += 1
        
        # 记录事件
        await self._record_event(SessionEventType.CREATED, session_aggregate.session_id, 
                               user.user_id, {
                                   "entrance_type": entrance_type.value,
                                   "config": session_config
                               })
        
        # 通知监听器
        await self._notify_listeners(session_aggregate.session_id, SessionEventType.CREATED, session_aggregate)
        
        logging.info(f"Created session {session_aggregate.session_id} for user {user.user_id}")
        
        return session_aggregate
    
    async def get_session(self, session_id: str) -> Optional[SessionAggregate]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    async def get_user_sessions(self, user_id: str) -> list[SessionAggregate]:
        """获取用户的所有会话"""
        session_ids = self.user_sessions.get(user_id, set())
        return [self.sessions[session_id] for session_id in session_ids if session_id in self.sessions]
    
    async def get_active_sessions(self) -> list[SessionAggregate]:
        """获取所有活跃会话"""
        return [session for session in self.sessions.values() if session.session.is_active()]
    
    async def pause_session(self, session_id: str) -> bool:
        """暂停会话"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        if not session_aggregate.session.is_active():
            return False
        
        session_aggregate.pause()
        
        await self._record_event(SessionEventType.PAUSED, session_id, session_aggregate.user_id)
        await self._notify_listeners(session_id, SessionEventType.PAUSED, session_aggregate)
        
        logging.info(f"Paused session {session_id}")
        return True
    
    async def resume_session(self, session_id: str) -> bool:
        """恢复会话"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        if session_aggregate.session.status != SessionStatus.PAUSED:
            return False
        
        session_aggregate.resume()
        
        await self._record_event(SessionEventType.RESUMED, session_id, session_aggregate.user_id)
        await self._notify_listeners(session_id, SessionEventType.RESUMED, session_aggregate)
        
        logging.info(f"Resumed session {session_id}")
        return True
    
    async def complete_session(self, session_id: str, reason: str = "user_request") -> bool:
        """完成会话"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        if session_aggregate.session.status == SessionStatus.COMPLETED:
            return True
        
        session_aggregate.complete()
        
        await self._record_event(SessionEventType.COMPLETED, session_id, session_aggregate.user_id, {"reason": reason})
        await self._notify_listeners(session_id, SessionEventType.COMPLETED, session_aggregate)
        
        # 更新统计
        self.stats["active_sessions"] -= 1
        self.stats["completed_sessions"] += 1
        
        logging.info(f"Completed session {session_id} (reason: {reason})")
        return True
    
    async def add_task_to_session(self, session_id: str, task_aggregate: TaskAggregate) -> bool:
        """向会话添加任务"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        # 检查任务数量限制
        if len(session_aggregate.tasks) >= self.config.max_tasks_per_session:
            raise ValueError(f"Session {session_id} has reached maximum task limit")
        
        # 设置任务会话ID
        task_aggregate.set_session(session_id)
        
        # 添加任务到会话
        success = session_aggregate.add_task(task_aggregate.task)
        if success:
            await self._record_event(SessionEventType.TASK_ADDED, session_id, session_aggregate.user_id, {
                "task_id": task_aggregate.task_id,
                "task_content": task_aggregate.task.content[:100] + "..." if len(task_aggregate.task.content) > 100 else task_aggregate.task.content,
                "intent_type": task_aggregate.task.intent_type.value
            })
            
            # 更新统计
            self.stats["total_tasks_created"] += 1
            
            # 通知监听器
            await self._notify_listeners(session_id, SessionEventType.TASK_ADDED, session_aggregate)
        
        return success
    
    async def add_message_to_session(self, session_id: str, message: Message) -> bool:
        """向会话添加消息"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        # 检查消息数量限制
        if len(session_aggregate.messages) >= self.config.max_messages_per_session:
            raise ValueError(f"Session {session_id} has reached maximum message limit")
        
        # 添加消息到会话
        success = session_aggregate.add_message(message)
        if success:
            await self._record_event(SessionEventType.MESSAGE_ADDED, session_id, session_aggregate.user_id, {
                "message_id": message.message_id,
                "sender": message.sender,
                "content": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                "message_type": type(message).__name__
            })
            
            # 更新统计
            self.stats["total_messages_sent"] += 1
            
            # 通知监听器
            await self._notify_listeners(session_id, SessionEventType.MESSAGE_ADDED, session_aggregate)
        
        return success
    
    async def get_session_tasks(self, session_id: str) -> list[TaskAggregate]:
        """获取会话的任务"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return []
        
        # 这里简化处理，实际应该从任务管理器获取
        return []
    
    async def get_session_messages(self, session_id: str, limit: int = 50) -> list[Message]:
        """获取会话的消息"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return []
        
        # 获取最近的消息
        recent_messages = session_aggregate.get_recent_messages(limit)
        return recent_messages
    
    async def get_session_status(self, session_id: str) -> dict[str, Any]:
        """获取会话状态"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return {"error": "Session not found"}
        
        session = session_aggregate.session
        
        # 检查是否过期
        is_expired = session.is_expired(self.config.max_duration_hours)
        
        # 计算会话统计
        task_count = session_aggregate.get_task_count()
        completed_tasks = len(session_aggregate.get_completed_tasks())
        message_count = len(session_aggregate.messages)
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "entrance_type": session.entrance_type.value,
            "status": session.status.value,
            "is_expired": is_expired,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "duration_seconds": session_aggregate.get_duration(),
            "task_count": task_count,
            "completed_tasks": completed_tasks,
            "message_count": message_count,
            "completion_rate": completed_tasks / task_count if task_count > 0 else 0,
            "metadata": session.metadata
        }
    
    async def switch_session_entrance(self, session_id: str, new_entrance: EntranceType) -> bool:
        """切换会话入口类型"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        old_entrance = session_aggregate.entrance_type
        
        # 这里应该有更复杂的逻辑来处理入口切换
        # 简化处理，只更新元数据
        session_aggregate.update_metadata("entrance_switch_history", {
            "from_entrance": old_entrance.value,
            "to_entrance": new_entrance.value,
            "switched_at": datetime.now().isoformat()
        })
        
        await self._record_event(SessionEventType.ENTRANCE_SWITCHED, session_id, 
                               session_aggregate.user_id, {
                                   "from_entrance": old_entrance.value,
                                   "to_entrance": new_entrance.value
                               })
        
        await self._notify_listeners(session_id, SessionEventType.ENTRANCE_SWITCHED, session_aggregate)
        
        logging.info(f"Switched session {session_id} from {old_entrance.value} to {new_entrance.value}")
        return True
    
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session_aggregate in self.sessions.items():
            if session_aggregate.session.is_expired(self.config.max_duration_hours):
                expired_sessions.append(session_id)
        
        cleaned_count = 0
        for session_id in expired_sessions:
            if await self.expire_session(session_id):
                cleaned_count += 1
        
        return cleaned_count
    
    async def expire_session(self, session_id: str) -> bool:
        """使会话过期"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        # 更新会话状态
        session_aggregate.session.status = SessionStatus.EXPIRED
        session_aggregate.session.updated_at = datetime.now()
        
        # 从用户会话映射中移除
        user_id = session_aggregate.user_id
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
        
        # 记录事件
        await self._record_event(SessionEventType.EXPIRED, session_id, user_id)
        await self._notify_listeners(session_id, SessionEventType.EXPIRED, session_aggregate)
        
        # 更新统计
        self.stats["active_sessions"] -= 1
        self.stats["expired_sessions"] += 1
        
        # 从活跃会话中移除
        del self.sessions[session_id]
        
        logging.info(f"Expired session {session_id}")
        return True
    
    def add_session_listener(self, session_id: str, listener: callable):
        """添加会话监听器"""
        if session_id not in self.session_listeners:
            self.session_listeners[session_id] = []
        self.session_listeners[session_id].append(listener)
    
    def remove_session_listener(self, session_id: str, listener: callable):
        """移除会话监听器"""
        if session_id in self.session_listeners:
            try:
                self.session_listeners[session_id].remove(listener)
            except ValueError:
                pass
    
    async def _notify_listeners(self, session_id: str, event_type: SessionEventType, session_aggregate: SessionAggregate):
        """通知监听器"""
        if session_id in self.session_listeners:
            for listener in self.session_listeners[session_id]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(event_type, session_aggregate)
                    else:
                        listener(event_type, session_aggregate)
                except Exception as e:
                    logging.error(f"Error in session listener for {session_id}: {e}")
    
    async def _record_event(self, event_type: SessionEventType, session_id: str, user_id: str, data: dict[str, Any] = None):
        """记录事件"""
        if not self.config.enable_event_logging:
            return
        
        event = SessionEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            session_id=session_id,
            user_id=user_id,
            timestamp=datetime.now(),
            data=data or {}
        )
        
        self.event_history.append(event)
        
        # 限制事件历史大小
        if len(self.event_history) > self.config.max_event_history:
            self.event_history = self.event_history[-self.config.max_event_history:]
    
    async def _cleanup_expired_sessions(self):
        """定期清理过期会话"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.cleanup_interval_minutes * 60)
                
                cleaned_count = await self.cleanup_expired_sessions()
                if cleaned_count > 0:
                    logging.info(f"Cleaned up {cleaned_count} expired sessions")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cleanup task: {e}")
    
    async def _persist_session_data(self):
        """定期持久化会话数据"""
        while self._is_running:
            try:
                await asyncio.sleep(300)  # 每5分钟持久化一次
                
                # 简化的持久化逻辑
                # 在实际应用中，这里应该将会话数据保存到数据库
                await self._save_sessions_to_storage()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in persistence task: {e}")
    
    async def _save_sessions_to_storage(self):
        """保存会话数据到存储"""
        # 简化的存储逻辑
        # 在实际应用中，这里应该实现数据库持久化
        pass
    
    async def get_session_events(self, session_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """获取会话事件历史"""
        session_events = [
            event for event in self.event_history 
            if event.session_id == session_id
        ]
        
        # 按时间排序并限制数量
        session_events.sort(key=lambda x: x.timestamp, reverse=True)
        recent_events = session_events[:limit]
        
        return [event.to_dict() for event in recent_events]
    
    async def get_user_session_summary(self, user_id: str) -> dict[str, Any]:
        """获取用户会话摘要"""
        user_session_ids = self.user_sessions.get(user_id, set())
        user_sessions = [self.sessions[sid] for sid in user_session_ids if sid in self.sessions]
        
        total_sessions = len(user_sessions)
        active_sessions = len([s for s in user_sessions if s.session.is_active()])
        completed_sessions = len([s for s in user_sessions if s.session.status == SessionStatus.COMPLETED])
        
        # 计算总任务数和消息数
        total_tasks = sum(len(s.tasks) for s in user_sessions)
        total_messages = sum(len(s.messages) for s in user_sessions)
        
        # 计算平均会话持续时间
        if user_sessions:
            avg_duration = sum(s.get_duration() for s in user_sessions) / total_sessions
        else:
            avg_duration = 0
        
        # 入口类型分布
        entrance_distribution = {}
        for session in user_sessions:
            entrance = session.entrance_type.value
            entrance_distribution[entrance] = entrance_distribution.get(entrance, 0) + 1
        
        return {
            "user_id": user_id,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "total_tasks": total_tasks,
            "total_messages": total_messages,
            "average_session_duration": avg_duration,
            "entrance_distribution": entrance_distribution,
            "last_activity": max([s.session.updated_at for s in user_sessions]) if user_sessions else None
        }
    
    async def get_system_statistics(self) -> dict[str, Any]:
        """获取系统统计信息"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        # 计算每个入口类型的会话数
        entrance_stats = {}
        for session in self.sessions.values():
            entrance = session.entrance_type.value
            entrance_stats[entrance] = entrance_stats.get(entrance, 0) + 1
        
        # 计算事件统计
        event_stats = {}
        for event in self.event_history:
            event_type = event.event_type.value
            event_stats[event_type] = event_stats.get(event_type, 0) + 1
        
        return {
            "total_sessions_created": self.stats["total_sessions_created"],
            "active_sessions": self.stats["active_sessions"],
            "completed_sessions": self.stats["completed_sessions"],
            "expired_sessions": self.stats["expired_sessions"],
            "total_tasks_created": self.stats["total_tasks_created"],
            "total_messages_sent": self.stats["total_messages_sent"],
            "uptime_seconds": uptime,
            "entrance_distribution": entrance_stats,
            "event_statistics": event_stats,
            "total_events": len(self.event_history),
            "is_running": self._is_running
        }
    
    async def validate_session(self, session_id: str) -> bool:
        """验证会话有效性"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return False
        
        # 检查会话是否过期
        if session_aggregate.session.is_expired(self.config.max_duration_hours):
            await self.expire_session(session_id)
            return False
        
        # 检查会话状态
        return session_aggregate.session.status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]
    
    async def get_session_transcript(self, session_id: str) -> dict[str, Any]:
        """获取会话转录"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return {"error": "Session not found"}
        
        # 获取所有消息
        messages = session_aggregate.messages
        
        # 按时间排序
        messages.sort(key=lambda x: x.timestamp)
        
        # 构建转录
        transcript = {
            "session_id": session_id,
            "user_id": session_aggregate.user_id,
            "entrance_type": session_aggregate.entrance_type.value,
            "started_at": session_aggregate.session.created_at.isoformat(),
            "ended_at": session_aggregate.session.updated_at.isoformat(),
            "duration": session_aggregate.get_duration(),
            "messages": [
                {
                    "message_id": msg.message_id,
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "type": type(msg).__name__
                }
                for msg in messages
            ],
            "task_count": session_aggregate.get_task_count(),
            "completed_tasks": len(session_aggregate.get_completed_tasks())
        }
        
        return transcript
    
    async def export_session_data(self, session_id: str, format_type: str = "json") -> dict[str, Any]:
        """导出会话数据"""
        session_aggregate = await self.get_session(session_id)
        if not session_aggregate:
            return {"error": "Session not found"}
        
        # 获取会话状态
        status = await self.get_session_status(session_id)
        
        # 获取会话事件
        events = await self.get_session_events(session_id)
        
        # 获取会话转录
        transcript = await self.get_session_transcript(session_id)
        
        export_data = {
            "session_info": status,
            "events": events,
            "transcript": transcript,
            "exported_at": datetime.now().isoformat(),
            "format": format_type
        }
        
        if format_type == "json":
            return export_data
        else:
            # 其他格式可以在这里实现
            return {"error": f"Unsupported format: {format_type}"}
    
    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        active_sessions = len(await self.get_active_sessions())
        total_sessions = len(self.sessions)
        
        # 检查是否有过多的过期会话
        expired_count = 0
        for session_aggregate in self.sessions.values():
            if session_aggregate.session.is_expired(self.config.max_duration_hours):
                expired_count += 1
        
        return {
            "status": "healthy" if expired_count < total_sessions * 0.1 else "warning",
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "expired_sessions": expired_count,
            "expired_ratio": expired_count / total_sessions if total_sessions > 0 else 0,
            "is_running": self._is_running,
            "last_health_check": datetime.now().isoformat()
        }