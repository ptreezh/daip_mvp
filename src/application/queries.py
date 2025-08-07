# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : queries.py
@Description:
    Query handlers for the Personal Intelligence Hub.
    These handlers implement the Query part of CQRS pattern.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

from ..domain.entities import User, Session, Task, Message, Debate
from ..domain.value_objects import (
    EntranceType, IntentType, TaskStatus, SessionStatus, 
    MessageIntent, ConsensusLevel, UserPreference, 
    TaskPriority, TimeInterval
)


@dataclass
class BaseQuery:
    """基础查询类"""
    query_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GetUserQuery(BaseQuery):
    """获取用户查询"""
    user_id: str = ""


@dataclass
class GetSessionQuery(BaseQuery):
    """获取会话查询"""
    session_id: str = ""


@dataclass
class GetTaskQuery(BaseQuery):
    """获取任务查询"""
    task_id: str = ""


@dataclass
class GetSessionTasksQuery(BaseQuery):
    """获取会话任务查询"""
    session_id: str = ""
    limit: int = 50
    offset: int = 0


@dataclass
class GetSessionMessagesQuery(BaseQuery):
    """获取会话消息查询"""
    session_id: str = ""
    limit: int = 50
    offset: int = 0


@dataclass
class GetUserSessionsQuery(BaseQuery):
    """获取用户会话查询"""
    user_id: str = ""
    limit: int = 50
    offset: int = 0


@dataclass
class GetActiveSessionsQuery(BaseQuery):
    """获取活跃会话查询"""
    limit: int = 100
    offset: int = 0


@dataclass
class GetDebateQuery(BaseQuery):
    """获取辩论查询"""
    debate_id: str = ""


@dataclass
class GetSessionDebateQuery(BaseQuery):
    """获取会话辩论查询"""
    session_id: str = ""


@dataclass
class GetSystemStatusQuery(BaseQuery):
    """获取系统状态查询"""


@dataclass
class GetUserStatisticsQuery(BaseQuery):
    """获取用户统计查询"""
    user_id: str = ""


@dataclass
class SearchSessionsQuery(BaseQuery):
    """搜索会话查询"""
    search_term: str = ""
    limit: int = 50
    offset: int = 0


class QueryResult:
    """查询结果"""
    
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class QueryHandler(ABC):
    """查询处理器接口"""
    
    @abstractmethod
    async def handle(self, query: BaseQuery) -> QueryResult:
        """处理查询"""
        pass


class GetUserQueryHandler(QueryHandler):
    """获取用户查询处理器"""
    
    def __init__(self, db_manager, redis_client):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, query: GetUserQuery) -> QueryResult:
        """处理获取用户查询"""
        try:
            # 尝试从缓存获取
            cached_user = await self.redis_client.get(f"user:{query.user_id}")
            if cached_user:
                return QueryResult(True, cached_user)
            
            # 从数据库获取
            async with self.db_manager.get_session() as session:
                from ..infrastructure.database import UserRepository
                user_repo = UserRepository(session)
                
                user_data = await user_repo.get_by_user_id(query.user_id)
                if not user_data:
                    return QueryResult(False, error=f"User {query.user_id} not found")
                
                user_info = {
                    "user_id": user_data.user_id,
                    "username": user_data.username,
                    "email": user_data.email,
                    "preferred_entrance": user_data.preferred_entrance,
                    "is_active": user_data.is_active,
                    "preferences": user_data.preferences,
                    "created_at": user_data.created_at.isoformat(),
                    "updated_at": user_data.updated_at.isoformat()
                }
                
                # 缓存用户信息
                await self.redis_client.set(f"user:{query.user_id}", user_info, ttl=3600)
                
                return QueryResult(True, user_info)
                
        except Exception as e:
            self.logger.error(f"Error handling GetUserQuery: {e}")
            return QueryResult(False, error=str(e))


class GetSessionQueryHandler(QueryHandler):
    """获取会话查询处理器"""
    
    def __init__(self, db_manager, redis_client):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, query: GetSessionQuery) -> QueryResult:
        """处理获取会话查询"""
        try:
            # 尝试从缓存获取
            cached_session = await self.redis_client.get(f"session:{query.session_id}")
            if cached_session:
                return QueryResult(True, cached_session)
            
            # 从数据库获取
            async with self.db_manager.get_session() as session:
                from ..infrastructure.database import SessionRepository
                session_repo = SessionRepository(session)
                
                session_data = await session_repo.get_by_session_id(query.session_id)
                if not session_data:
                    return QueryResult(False, error=f"Session {query.session_id} not found")
                
                session_info = {
                    "session_id": session_data.session_id,
                    "user_id": session_data.user_id,
                    "entrance_type": session_data.entrance_type,
                    "status": session_data.status,
                    "created_at": session_data.created_at.isoformat(),
                    "updated_at": session_data.updated_at.isoformat(),
                    "metadata": session_data.metadata
                }
                
                # 缓存会话信息
                await self.redis_client.set(f"session:{query.session_id}", session_info, ttl=300)
                
                return QueryResult(True, session_info)
                
        except Exception as e:
            self.logger.error(f"Error handling GetSessionQuery: {e}")
            return QueryResult(False, error=str(e))


class GetTaskQueryHandler(QueryHandler):
    """获取任务查询处理器"""
    
    def __init__(self, db_manager, redis_client):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, query: GetTaskQuery) -> QueryResult:
        """处理获取任务查询"""
        try:
            # 尝试从缓存获取
            cached_task = await self.redis_client.get(f"task:{query.task_id}")
            if cached_task:
                return QueryResult(True, cached_task)
            
            # 从数据库获取
            async with self.db_manager.get_session() as session:
                from ..infrastructure.database import TaskRepository
                task_repo = TaskRepository(session)
                
                task_data = await task_repo.get_by_task_id(query.task_id)
                if not task_data:
                    return QueryResult(False, error=f"Task {query.task_id} not found")
                
                task_info = {
                    "task_id": task_data.task_id,
                    "session_id": task_data.session_id,
                    "content": task_data.content,
                    "intent_type": task_data.intent_type,
                    "status": task_data.status,
                    "priority": task_data.priority,
                    "result": task_data.result,
                    "created_at": task_data.created_at.isoformat(),
                    "updated_at": task_data.updated_at.isoformat(),
                    "completed_at": task_data.completed_at.isoformat() if task_data.completed_at else None,
                    "metadata": task_data.metadata
                }
                
                # 缓存任务信息
                await self.redis_client.set(f"task:{query.task_id}", task_info, ttl=300)
                
                return QueryResult(True, task_info)
                
        except Exception as e:
            self.logger.error(f"Error handling GetTaskQuery: {e}")
            return QueryResult(False, error=str(e))


class GetSessionTasksQueryHandler(QueryHandler):
    """获取会话任务查询处理器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, query: GetSessionTasksQuery) -> QueryResult:
        """处理获取会话任务查询"""
        try:
            async with self.db_manager.get_session() as session:
                from ..infrastructure.database import TaskRepository
                task_repo = TaskRepository(session)
                
                tasks = await task_repo.get_session_tasks(query.session_id)
                
                # 应用分页
                offset = query.offset
                limit = query.limit
                paginated_tasks = tasks[offset:offset + limit]
                
                tasks_info = []
                for task in paginated_tasks:
                    tasks_info.append({
                        "task_id": task.task_id,
                        "session_id": task.session_id,
                        "content": task.content[:100] + "..." if len(task.content) > 100 else task.content,
                        "intent_type": task.intent_type,
                        "status": task.status,
                        "priority": task.priority,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat(),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    })
                
                return QueryResult(True, {
                    "tasks": tasks_info,
                    "total": len(tasks),
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < len(tasks)
                })
                
        except Exception as e:
            self.logger.error(f"Error handling GetSessionTasksQuery: {e}")
            return QueryResult(False, error=str(e))


class GetSessionMessagesQueryHandler(QueryHandler):
    """获取会话消息查询处理器"""
    
    def __init__(self, db_manager, redis_client):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, query: GetSessionMessagesQuery) -> QueryResult:
        """处理获取会话消息查询"""
        try:
            # 尝试从缓存获取最近消息
            cached_messages = await self.redis_client.get(f"session_messages:{query.session_id}")
            if cached_messages and len(cached_messages) >= query.limit:
                # 应用分页
                offset = query.offset
                limit = query.limit
                paginated_messages = cached_messages[offset:offset + limit]
                
                return QueryResult(True, {
                    "messages": paginated_messages,
                    "total": len(cached_messages),
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < len(cached_messages),
                    "source": "cache"
                })
            
            # 从数据库获取
            async with self.db_manager.get_session() as session:
                from ..infrastructure.database import MessageRepository
                message_repo = MessageRepository(session)
                
                messages = await message_repo.get_session_messages(query.session_id, limit=query.limit + query.offset)
                
                # 应用分页
                offset = query.offset
                limit = query.limit
                paginated_messages = messages[offset:offset + limit]
                
                messages_info = []
                for message in paginated_messages:
                    messages_info.append({
                        "message_id": message.message_id,
                        "session_id": message.session_id,
                        "content": message.content[:200] + "..." if len(message.content) > 200 else message.content,
                        "sender": message.sender,
                        "intent": message.intent,
                        "confidence": message.confidence,
                        "agent_role": message.agent_role,
                        "message_type": message.message_type,
                        "created_at": message.created_at.isoformat()
                    })
                
                return QueryResult(True, {
                    "messages": messages_info,
                    "total": len(messages),
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < len(messages),
                    "source": "database"
                })
                
        except Exception as e:
            self.logger.error(f"Error handling GetSessionMessagesQuery: {e}")
            return QueryResult(False, error=str(e))


class GetUserSessionsQueryHandler(QueryHandler):
    """获取用户会话查询处理器"""
    
    def __init__(self, db_manager, redis_client):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, query: GetUserSessionsQuery) -> QueryResult:
        """处理获取用户会话查询"""
        try:
            # 尝试从缓存获取
            cached_sessions = await self.redis_client.get(f"user_sessions:{query.user_id}")
            if cached_sessions:
                # 获取会话详情
                sessions_info = []
                for session_id in cached_sessions[query.offset:query.offset + query.limit]:
                    session_data = await self.redis_client.get(f"session:{session_id}")
                    if session_data:
                        sessions_info.append(session_data)
                
                return QueryResult(True, {
                    "sessions": sessions_info,
                    "total": len(cached_sessions),
                    "offset": query.offset,
                    "limit": query.limit,
                    "has_more": query.offset + query.limit < len(cached_sessions),
                    "source": "cache"
                })
            
            # 从数据库获取
            async with self.db_manager.get_session() as session:
                from ..infrastructure.database import SessionRepository
                session_repo = SessionRepository(session)
                
                sessions = await session_repo.get_user_sessions(query.user_id)
                
                # 应用分页
                offset = query.offset
                limit = query.limit
                paginated_sessions = sessions[offset:offset + limit]
                
                sessions_info = []
                for session_data in paginated_sessions:
                    sessions_info.append({
                        "session_id": session_data.session_id,
                        "user_id": session_data.user_id,
                        "entrance_type": session_data.entrance_type,
                        "status": session_data.status,
                        "created_at": session_data.created_at.isoformat(),
                        "updated_at": session_data.updated_at.isoformat(),
                        "metadata": session_data.metadata
                    })
                
                return QueryResult(True, {
                    "sessions": sessions_info,
                    "total": len(sessions),
                    "offset": offset,
                    "limit": limit,
                    "has_more": offset + limit < len(sessions),
                    "source": "database"
                })
                
        except Exception as e:
            self.logger.error(f"Error handling GetUserSessionsQuery: {e}")
            return QueryResult(False, error=str(e))


class GetSystemStatusQueryHandler(QueryHandler):
    """获取系统状态查询处理器"""
    
    def __init__(self, db_manager, redis_client):
        self.db_manager = db_manager
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, query: GetSystemStatusQuery) -> QueryResult:
        """处理获取系统状态查询"""
        try:
            status_info = {
                "timestamp": datetime.now().isoformat(),
                "services": {},
                "statistics": {}
            }
            
            # 检查数据库状态
            try:
                db_health = await self.db_manager.health_check()
                status_info["services"]["database"] = db_health
            except Exception as e:
                status_info["services"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # 检查Redis状态
            try:
                redis_pong = await self.redis_client.ping()
                status_info["services"]["redis"] = {
                    "status": "healthy" if redis_pong else "unhealthy",
                    "connected": redis_pong
                }
            except Exception as e:
                status_info["services"]["redis"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # 获取系统统计信息
            try:
                async with self.db_manager.get_session() as session:
                    from ..infrastructure.database import UserRepository, SessionRepository, TaskRepository
                    
                    user_repo = UserRepository(session)
                    session_repo = SessionRepository(session)
                    task_repo = TaskRepository(session)
                    
                    user_count = await user_repo.count()
                    session_count = await session_repo.count()
                    task_count = await task_repo.count()
                    
                    status_info["statistics"] = {
                        "total_users": user_count,
                        "total_sessions": session_count,
                        "total_tasks": task_count,
                        "active_users": len(await user_repo.get_active_users()),
                        "active_sessions": len(await session_repo.get_active_sessions()),
                        "pending_tasks": len(await task_repo.get_tasks_by_status("pending")),
                        "running_tasks": len(await task_repo.get_tasks_by_status("running")),
                        "completed_tasks": len(await task_repo.get_tasks_by_status("completed"))
                    }
            except Exception as e:
                status_info["statistics"] = {
                    "error": f"Failed to get statistics: {str(e)}"
                }
            
            # 确定整体状态
            service_statuses = [service["status"] for service in status_info["services"].values()]
            if "unhealthy" in service_statuses:
                overall_status = "unhealthy"
            elif all(status == "healthy" for status in service_statuses):
                overall_status = "healthy"
            else:
                overall_status = "degraded"
            
            status_info["overall_status"] = overall_status
            
            return QueryResult(True, status_info)
            
        except Exception as e:
            self.logger.error(f"Error handling GetSystemStatusQuery: {e}")
            return QueryResult(False, error=str(e))


class QueryBus:
    """查询总线"""
    
    def __init__(self):
        self.handlers: Dict[type, QueryHandler] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register_handler(self, query_type: type, handler: QueryHandler):
        """注册查询处理器"""
        self.handlers[query_type] = handler
        self.logger.info(f"Registered handler for {query_type.__name__}")
    
    async def dispatch(self, query: BaseQuery) -> QueryResult:
        """分发查询"""
        query_type = type(query)
        
        if query_type not in self.handlers:
            error_msg = f"No handler registered for {query_type.__name__}"
            self.logger.error(error_msg)
            return QueryResult(False, error=error_msg)
        
        handler = self.handlers[query_type]
        
        try:
            self.logger.info(f"Dispatching {query_type.__name__} with ID {query.query_id}")
            result = await handler.handle(query)
            self.logger.info(f"Query {query.query_id} executed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Error executing query {query.query_id}: {str(e)}"
            self.logger.error(error_msg)
            return QueryResult(False, error=error_msg)
    
    def get_registered_queries(self) -> list[str]:
        """获取已注册的查询类型"""
        return [handler_type.__name__ for handler_type in self.handlers.keys()]


class QueryDispatcher:
    """查询分发器"""
    
    def __init__(self, query_bus: QueryBus, db_manager, redis_client):
        self.query_bus = query_bus
        self.db_manager = db_manager
        self.redis_client = redis_client
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置查询处理器"""
        # 注册所有查询处理器
        self.query_bus.register_handler(
            GetUserQuery,
            GetUserQueryHandler(self.db_manager, self.redis_client)
        )
        
        self.query_bus.register_handler(
            GetSessionQuery,
            GetSessionQueryHandler(self.db_manager, self.redis_client)
        )
        
        self.query_bus.register_handler(
            GetTaskQuery,
            GetTaskQueryHandler(self.db_manager, self.redis_client)
        )
        
        self.query_bus.register_handler(
            GetSessionTasksQuery,
            GetSessionTasksQueryHandler(self.db_manager)
        )
        
        self.query_bus.register_handler(
            GetSessionMessagesQuery,
            GetSessionMessagesQueryHandler(self.db_manager, self.redis_client)
        )
        
        self.query_bus.register_handler(
            GetUserSessionsQuery,
            GetUserSessionsQueryHandler(self.db_manager, self.redis_client)
        )
        
        self.query_bus.register_handler(
            GetSystemStatusQuery,
            GetSystemStatusQueryHandler(self.db_manager, self.redis_client)
        )
    
    async def dispatch_query(self, query: BaseQuery) -> QueryResult:
        """分发查询"""
        return await self.query_bus.dispatch(query)
    
    async def get_user(self, user_id: str = "") -> QueryResult:
        """获取用户"""
        query = GetUserQuery(
            query_id=f"get_user_{user_id}",
            user_id=user_id
        )
        
        return await self.dispatch_query(query)
    
    async def get_session(self, session_id: str = "") -> QueryResult:
        """获取会话"""
        query = GetSessionQuery(
            query_id=f"get_session_{session_id}",
            session_id=session_id
        )
        
        return await self.dispatch_query(query)
    
    async def get_task(self, task_id: str = "") -> QueryResult:
        """获取任务"""
        query = GetTaskQuery(
            query_id=f"get_task_{task_id}",
            task_id=task_id
        )
        
        return await self.dispatch_query(query)
    
    async def get_session_tasks(self, session_id: str = "", limit: int = 50, offset: int = 0) -> QueryResult:
        """获取会话任务"""
        query = GetSessionTasksQuery(
            query_id=f"get_session_tasks_{session_id}",
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        return await self.dispatch_query(query)
    
    async def get_session_messages(self, session_id: str = "", limit: int = 50, offset: int = 0) -> QueryResult:
        """获取会话消息"""
        query = GetSessionMessagesQuery(
            query_id=f"get_session_messages_{session_id}",
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        return await self.dispatch_query(query)
    
    async def get_user_sessions(self, user_id: str = "", limit: int = 50, offset: int = 0) -> QueryResult:
        """获取用户会话"""
        query = GetUserSessionsQuery(
            query_id=f"get_user_sessions_{user_id}",
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return await self.dispatch_query(query)
    
    async def get_system_status(self) -> QueryResult:
        """获取系统状态"""
        query = GetSystemStatusQuery(
            query_id="get_system_status"
        )
        
        return await self.dispatch_query(query)