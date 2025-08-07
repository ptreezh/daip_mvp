# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : database.py
@Description:
    Database manager for PostgreSQL integration.
    Handles database connections, sessions, and ORM operations.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic
from datetime import datetime
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Boolean, Integer, Float, JSON, ForeignKey, select, update, delete
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..domain.entities import User, Session, Task, Message
from ..domain.value_objects import (
    EntranceType, IntentType, TaskStatus, SessionStatus, 
    MessageIntent, ConsensusLevel, UserPreference, 
    TaskPriority, TimeInterval
)

# 类型变量
T = TypeVar('T')

# 基础模型类
class BaseModel(DeclarativeBase):
    """SQLAlchemy 基础模型类"""
    __abstract__ = True
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 数据库模型
class UserModel(BaseModel):
    """用户表"""
    __tablename__ = 'users'
    
    user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    preferred_entrance: Mapped[str] = mapped_column(String(50), nullable=False)
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class SessionModel(BaseModel):
    """会话表"""
    __tablename__ = 'sessions'
    
    session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entrance_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    session_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

class TaskModel(BaseModel):
    """任务表"""
    __tablename__ = 'tasks'
    
    task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    session_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

class MessageModel(BaseModel):
    """消息表"""
    __tablename__ = 'messages'
    
    message_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    agent_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)
    session_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

class DebateModel(BaseModel):
    """辩论表"""
    __tablename__ = 'debates'
    
    debate_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    participants: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    consensus_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

class SystemEventModel(BaseModel):
    """系统事件表"""
    __tablename__ = 'system_events'
    
    event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

# 全局数据库管理器实例
_database_manager: Optional['DatabaseManager'] = None


class DatabaseManager:
    """数据库管理器 - 管理PostgreSQL连接和操作"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.is_initialized = False
        
    async def initialize(self):
        """初始化数据库连接"""
        if self.is_initialized:
            return
            
        try:
            # 创建异步引擎
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # 设置为True可以查看SQL语句
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # 创建会话工厂
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 创建表
            async with self.engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.create_all)
            
            self.is_initialized = True
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
            self.is_initialized = False
            logging.info("Database connection closed")
    
    @asynccontextmanager
    async def get_session(self):
        """获取数据库会话"""
        if not self.is_initialized:
            raise RuntimeError("Database not initialized")
        
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            return [dict(row._mapping) for row in result.fetchall()]
    
    async def execute_update(self, query: str, params: Dict[str, Any] = None) -> int:
        """执行更新"""
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            await session.commit()
            return result.rowcount
    
    async def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            async with self.get_session() as session:
                # 执行简单查询
                result = await session.execute(select(func.count()).select_from(UserModel))
                count = result.scalar()
                
                return {
                    "status": "healthy",
                    "connected": True,
                    "user_count": count,
                    "last_check": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }


class BaseRepository(Generic[T]):
    """基础仓储类"""
    
    def __init__(self, session: AsyncSession, model_class: Type[BaseModel]):
        self.session = session
        self.model_class = model_class
    
    async def create(self, **kwargs) -> T:
        """创建记录"""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """根据ID获取记录"""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """获取所有记录"""
        result = await self.session.execute(
            select(self.model_class)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """更新记录"""
        await self.session.execute(
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)
    
    async def delete(self, id: str) -> bool:
        """删除记录"""
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def count(self) -> int:
        """记录数量"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model_class)
        )
        return result.scalar()


class UserRepository(BaseRepository[UserModel]):
    """用户仓储"""
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserModel]:
        """根据用户ID获取用户"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """根据邮箱获取用户"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self) -> List[UserModel]:
        """获取活跃用户"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.is_active == True)
        )
        return result.scalars().all()
    
    async def create_user(self, user_id: str, username: str, email: str, 
                        preferred_entrance: str, preferences: Dict[str, Any]) -> UserModel:
        """创建用户"""
        return await self.create(
            user_id=user_id,
            username=username,
            email=email,
            preferred_entrance=preferred_entrance,
            preferences=preferences
        )


class SessionRepository(BaseRepository[SessionModel]):
    """会话仓储"""
    
    async def get_by_session_id(self, session_id: str) -> Optional[SessionModel]:
        """根据会话ID获取会话"""
        result = await self.session.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_sessions(self, user_id: str) -> List[SessionModel]:
        """获取用户的所有会话"""
        result = await self.session.execute(
            select(SessionModel).where(SessionModel.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_active_sessions(self) -> List[SessionModel]:
        """获取活跃会话"""
        result = await self.session.execute(
            select(SessionModel).where(SessionModel.status == SessionStatus.ACTIVE.value)
        )
        return result.scalars().all()
    
    async def create_session(self, session_id: str, user_id: str, entrance_type: str, 
                           status: str, metadata: Dict[str, Any] = None) -> SessionModel:
        """创建会话"""
        return await self.create(
            session_id=session_id,
            user_id=user_id,
            entrance_type=entrance_type,
            status=status,
            metadata=metadata or {}
        )


class TaskRepository(BaseRepository[TaskModel]):
    """任务仓储"""
    
    async def get_by_task_id(self, task_id: str) -> Optional[TaskModel]:
        """根据任务ID获取任务"""
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.task_id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_session_tasks(self, session_id: str) -> List[TaskModel]:
        """获取会话的所有任务"""
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.session_id == session_id)
        )
        return result.scalars().all()
    
    async def get_tasks_by_status(self, status: str) -> List[TaskModel]:
        """根据状态获取任务"""
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.status == status)
        )
        return result.scalars().all()
    
    async def create_task(self, task_id: str, session_id: str, content: str, 
                         intent_type: str, status: str, priority: str = "normal",
                         metadata: Dict[str, Any] = None) -> TaskModel:
        """创建任务"""
        return await self.create(
            task_id=task_id,
            session_id=session_id,
            content=content,
            intent_type=intent_type,
            status=status,
            priority=priority,
            metadata=metadata or {}
        )
    
    async def update_task_status(self, task_id: str, status: str, result: str = None) -> Optional[TaskModel]:
        """更新任务状态"""
        update_data = {"status": status}
        if result:
            update_data["result"] = result
        if status == TaskStatus.COMPLETED.value:
            update_data["completed_at"] = datetime.now()
        
        return await self.update(task_id, **update_data)


class MessageRepository(BaseRepository[MessageModel]):
    """消息仓储"""
    
    async def get_by_message_id(self, message_id: str) -> Optional[MessageModel]:
        """根据消息ID获取消息"""
        result = await self.session.execute(
            select(MessageModel).where(MessageModel.message_id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def get_session_messages(self, session_id: str, limit: int = 50) -> List[MessageModel]:
        """获取会话消息"""
        result = await self.session.execute(
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_messages_by_sender(self, session_id: str, sender: str) -> List[MessageModel]:
        """获取发送者的消息"""
        result = await self.session.execute(
            select(MessageModel)
            .where(
                (MessageModel.session_id == session_id) &
                (MessageModel.sender == sender)
            )
        )
        return result.scalars().all()
    
    async def create_message(self, message_id: str, session_id: str, content: str, 
                           sender: str, message_type: str, intent: str = None,
                           confidence: float = None, agent_role: str = None,
                           metadata: Dict[str, Any] = None) -> MessageModel:
        """创建消息"""
        return await self.create(
            message_id=message_id,
            session_id=session_id,
            content=content,
            sender=sender,
            intent=intent,
            confidence=confidence,
            agent_role=agent_role,
            message_type=message_type,
            metadata=metadata or {}
        )


class DebateRepository(BaseRepository[DebateModel]):
    """辩论仓储"""
    
    async def get_by_debate_id(self, debate_id: str) -> Optional[DebateModel]:
        """根据辩论ID获取辩论"""
        result = await self.session.execute(
            select(DebateModel).where(DebateModel.debate_id == debate_id)
        )
        return result.scalar_one_or_none()
    
    async def get_session_debate(self, session_id: str) -> Optional[DebateModel]:
        """获取会话的辩论"""
        result = await self.session.execute(
            select(DebateModel).where(DebateModel.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_debates(self) -> List[DebateModel]:
        """获取活跃辩论"""
        result = await self.session.execute(
            select(DebateModel).where(DebateModel.status == "active")
        )
        return result.scalars().all()
    
    async def create_debate(self, debate_id: str, session_id: str, topic: str, 
                          participants: List[str], status: str = "active") -> DebateModel:
        """创建辩论"""
        return await self.create(
            debate_id=debate_id,
            session_id=session_id,
            topic=topic,
            participants=participants,
            status=status
        )
    
    async def update_consensus_level(self, debate_id: str, consensus_level: float) -> Optional[DebateModel]:
        """更新共识水平"""
        return await self.update(debate_id, consensus_level=consensus_level)


async def get_database_manager(database_url: str = None) -> DatabaseManager:
    """获取数据库管理器实例"""
    global _database_manager
    
    if _database_manager is None:
        if database_url is None:
            raise ValueError("Database URL is required for first initialization")
        
        _database_manager = DatabaseManager(database_url)
        await _database_manager.initialize()
    
    return _database_manager


async def close_database_connection():
    """关闭数据库连接"""
    global _database_manager
    
    if _database_manager:
        await _database_manager.close()
        _database_manager = None