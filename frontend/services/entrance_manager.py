#!/usr/bin/env python3
"""双入口管理器

负责管理Secretariat和Forum两种入口模式
提供统一的入口切换和上下文保存机制
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional

from .dual_entrance_websocket_manager import EntranceType, MessageType, dual_entrance_websocket_manager

# 配置日志
logger = logging.getLogger(__name__)


class UserContext:
    """用户上下文"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferred_entrance = EntranceType.SECRETARIAT
        self.theme = "light"
        self.language = "zh-CN"
        self.notification_settings = {
            "task_completion": True,
            "forum_updates": False,
            "system_alerts": True
        }
        self.usage_stats = {
            "total_sessions": 0,
            "total_tasks": 0,
            "avg_session_duration": 0.0,
            "favorite_topics": []
        }
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "user_id": self.user_id,
            "preferred_entrance": self.preferred_entrance.value,
            "theme": self.theme,
            "language": self.language,
            "notification_settings": self.notification_settings,
            "usage_stats": self.usage_stats,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'UserContext':
        """从字典创建用户上下文"""
        context = cls(data["user_id"])
        context.preferred_entrance = EntranceType(data["preferred_entrance"])
        context.theme = data["theme"]
        context.language = data["language"]
        context.notification_settings = data["notification_settings"]
        context.usage_stats = data["usage_stats"]
        context.created_at = datetime.fromisoformat(data["created_at"])
        context.updated_at = datetime.fromisoformat(data["updated_at"])
        return context


class SessionContext:
    """会话上下文"""
    
    def __init__(self, session_id: str, entrance_type: EntranceType, user_id: str):
        self.session_id = session_id
        self.entrance_type = entrance_type
        self.user_id = user_id
        self.status = "active"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_activity = datetime.now()
        
        # 入口特定上下文
        self.entrance_context = {}
        
        # 共享上下文
        self.shared_context = {
            "current_topic": "",
            "active_agents": [],
            "knowledge_base": [],
            "conversation_history": [],
            "consensus_data": {}
        }
        
        # 工作流状态
        self.workflow_state = {
            "current_workflow": None,
            "workflow_steps": [],
            "current_step": 0,
            "workflow_results": {}
        }
        
        # 临时数据
        self.temp_data = {}
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.now()
        self.updated_at = datetime.now()
    
    def add_conversation_message(self, message: dict[str, Any]):
        """添加对话消息"""
        self.shared_context["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            **message
        })
        
        # 限制历史记录长度
        if len(self.shared_context["conversation_history"]) > 100:
            self.shared_context["conversation_history"] = self.shared_context["conversation_history"][-100:]
    
    def set_current_topic(self, topic: str):
        """设置当前主题"""
        self.shared_context["current_topic"] = topic
        self.update_activity()
    
    def add_active_agent(self, agent_id: str, agent_role: str):
        """添加活跃代理"""
        agent_info = {"agent_id": agent_id, "agent_role": agent_role, "joined_at": datetime.now().isoformat()}
        
        # 检查是否已存在
        for agent in self.shared_context["active_agents"]:
            if agent["agent_id"] == agent_id:
                return
        
        self.shared_context["active_agents"].append(agent_info)
        self.update_activity()
    
    def remove_active_agent(self, agent_id: str):
        """移除活跃代理"""
        self.shared_context["active_agents"] = [
            agent for agent in self.shared_context["active_agents"]
            if agent["agent_id"] != agent_id
        ]
        self.update_activity()
    
    def update_consensus_data(self, consensus_data: dict[str, Any]):
        """更新共识数据"""
        self.shared_context["consensus_data"].update(consensus_data)
        self.update_activity()
    
    def set_workflow_state(self, workflow_id: str, step: int, results: dict[str, Any]):
        """设置工作流状态"""
        self.workflow_state["current_workflow"] = workflow_id
        self.workflow_state["current_step"] = step
        self.workflow_state["workflow_results"].update(results)
        self.update_activity()
    
    def get_entrance_context(self) -> dict[str, Any]:
        """获取入口特定上下文"""
        return self.entrance_context
    
    def set_entrance_context(self, context: dict[str, Any]):
        """设置入口特定上下文"""
        self.entrance_context.update(context)
        self.update_activity()
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "entrance_type": self.entrance_type.value,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "entrance_context": self.entrance_context,
            "shared_context": self.shared_context,
            "workflow_state": self.workflow_state,
            "temp_data": self.temp_data
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SessionContext':
        """从字典创建会话上下文"""
        context = cls(
            data["session_id"],
            EntranceType(data["entrance_type"]),
            data["user_id"]
        )
        context.status = data["status"]
        context.created_at = datetime.fromisoformat(data["created_at"])
        context.updated_at = datetime.fromisoformat(data["updated_at"])
        context.last_activity = datetime.fromisoformat(data["last_activity"])
        context.entrance_context = data["entrance_context"]
        context.shared_context = data["shared_context"]
        context.workflow_state = data["workflow_state"]
        context.temp_data = data["temp_data"]
        return context


class EntranceManager:
    """入口管理器"""
    
    def __init__(self):
        self.user_contexts: dict[str, UserContext] = {}
        self.session_contexts: dict[str, SessionContext] = {}
        self.entrance_callbacks: dict[str, list[Callable]] = {}
        
        # 注册WebSocket消息处理器
        self._setup_websocket_handlers()
        
        logger.info("入口管理器初始化完成")
    
    def _setup_websocket_handlers(self):
        """设置WebSocket消息处理器"""
        # 注册通用消息处理器
        dual_entrance_websocket_manager.register_handler(
            MessageType.SYSTEM_STATUS, self._handle_system_status
        )
        
        # 注册Secretariat消息处理器
        dual_entrance_websocket_manager.register_handler(
            MessageType.SECRETARIAT_TASK, self._handle_secretariat_task, EntranceType.SECRETARIAT
        )
        
        dual_entrance_websocket_manager.register_handler(
            MessageType.TASK_STATUS, self._handle_task_status, EntranceType.SECRETARIAT
        )
        
        # 注册Forum消息处理器
        dual_entrance_websocket_manager.register_handler(
            MessageType.CREATE_FORUM_SESSION, self._handle_forum_session, EntranceType.FORUM
        )
        
        dual_entrance_websocket_manager.register_handler(
            MessageType.CONSENSUS_UPDATE, self._handle_consensus_update, EntranceType.FORUM
        )
    
    async def create_user_context(self, user_id: str, preferences: dict[str, Any] = None) -> UserContext:
        """创建用户上下文"""
        if user_id in self.user_contexts:
            logger.warning(f"用户上下文已存在: {user_id}")
            return self.user_contexts[user_id]
        
        user_context = UserContext(user_id)
        
        if preferences:
            if "preferred_entrance" in preferences:
                user_context.preferred_entrance = EntranceType(preferences["preferred_entrance"])
            if "theme" in preferences:
                user_context.theme = preferences["theme"]
            if "language" in preferences:
                user_context.language = preferences["language"]
            if "notification_settings" in preferences:
                user_context.notification_settings.update(preferences["notification_settings"])
        
        self.user_contexts[user_id] = user_context
        
        logger.info(f"创建用户上下文: {user_id}")
        
        return user_context
    
    async def create_session_context(self, user_id: str, entrance_type: EntranceType, 
                                    initial_context: dict[str, Any] = None) -> str:
        """创建会话上下文"""
        session_id = await dual_entrance_websocket_manager.create_session(
            entrance_type, user_id, initial_context
        )
        
        session_context = SessionContext(session_id, entrance_type, user_id)
        
        if initial_context:
            session_context.set_entrance_context(initial_context)
        
        self.session_contexts[session_id] = session_context
        
        # 更新用户统计
        if user_id in self.user_contexts:
            self.user_contexts[user_id].usage_stats["total_sessions"] += 1
        
        logger.info(f"创建会话上下文: {session_id} ({entrance_type.value})")
        
        # 触发回调
        await self._trigger_callbacks("session_created", {
            "session_id": session_id,
            "entrance_type": entrance_type.value,
            "user_id": user_id
        })
        
        return session_id
    
    async def switch_entrance(self, session_id: str, new_entrance_type: EntranceType) -> str:
        """切换入口类型"""
        if session_id not in self.session_contexts:
            logger.error(f"会话不存在: {session_id}")
            return None
        
        old_context = self.session_contexts[session_id]
        
        # 创建新会话
        new_session_id = await self.create_session_context(
            old_context.user_id,
            new_entrance_type,
            old_context.shared_context.copy()
        )
        
        # 关闭旧会话
        await self.close_session(session_id)
        
        logger.info(f"切换入口: {session_id} -> {new_session_id} ({new_entrance_type.value})")
        
        return new_session_id
    
    async def close_session(self, session_id: str):
        """关闭会话"""
        if session_id not in self.session_contexts:
            logger.warning(f"会话不存在: {session_id}")
            return
        
        session_context = self.session_contexts[session_id]
        session_context.status = "closed"
        
        # 更新用户统计
        if session_context.user_id in self.user_contexts:
            user_context = self.user_contexts[session_context.user_id]
            session_duration = (datetime.now() - session_context.created_at).total_seconds()
            
            # 更新平均会话时长
            if user_context.usage_stats["avg_session_duration"] == 0:
                user_context.usage_stats["avg_session_duration"] = session_duration
            else:
                total_sessions = user_context.usage_stats["total_sessions"]
                user_context.usage_stats["avg_session_duration"] = (
                    (user_context.usage_stats["avg_session_duration"] * (total_sessions - 1) + session_duration) / total_sessions
                )
        
        # 从WebSocket管理器中移除
        if session_id in dual_entrance_websocket_manager.active_sessions:
            del dual_entrance_websocket_manager.active_sessions[session_id]
        
        if session_id in dual_entrance_websocket_manager.session_types:
            del dual_entrance_websocket_manager.session_types[session_id]
        
        logger.info(f"关闭会话: {session_id}")
        
        # 触发回调
        await self._trigger_callbacks("session_closed", {
            "session_id": session_id,
            "entrance_type": session_context.entrance_type.value,
            "user_id": session_context.user_id
        })
    
    def get_user_context(self, user_id: str) -> Optional[UserContext]:
        """获取用户上下文"""
        return self.user_contexts.get(user_id)
    
    def get_session_context(self, session_id: str) -> Optional[SessionContext]:
        """获取会话上下文"""
        return self.session_contexts.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> list[str]:
        """获取用户的所有会话"""
        return [
            session_id for session_id, context in self.session_contexts.items()
            if context.user_id == user_id and context.status == "active"
        ]
    
    def register_callback(self, event_type: str, callback: Callable):
        """注册事件回调"""
        if event_type not in self.entrance_callbacks:
            self.entrance_callbacks[event_type] = []
        self.entrance_callbacks[event_type].append(callback)
    
    async def _trigger_callbacks(self, event_type: str, data: dict[str, Any]):
        """触发事件回调"""
        if event_type in self.entrance_callbacks:
            for callback in self.entrance_callbacks[event_type]:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"回调执行失败 {event_type}: {e}")
    
    async def _handle_system_status(self, message):
        """处理系统状态消息"""
        logger.info(f"收到系统状态消息: {message.payload}")
    
    async def _handle_secretariat_task(self, message):
        """处理Secretariat任务消息"""
        logger.info(f"收到Secretariat任务消息: {message.payload}")
        
        if message.session_id in self.session_contexts:
            session_context = self.session_contexts[message.session_id]
            session_context.update_activity()
    
    async def _handle_task_status(self, message):
        """处理任务状态消息"""
        logger.info(f"收到任务状态消息: {message.payload}")
        
        if message.session_id in self.session_contexts:
            session_context = self.session_contexts[message.session_id]
            session_context.update_activity()
    
    async def _handle_forum_session(self, message):
        """处理Forum会话消息"""
        logger.info(f"收到Forum会话消息: {message.payload}")
        
        if message.session_id in self.session_contexts:
            session_context = self.session_contexts[message.session_id]
            session_context.update_activity()
    
    async def _handle_consensus_update(self, message):
        """处理共识更新消息"""
        logger.info(f"收到共识更新消息: {message.payload}")
        
        if message.session_id in self.session_contexts:
            session_context = self.session_contexts[message.session_id]
            session_context.update_consensus_data(message.payload)
    
    def get_manager_status(self) -> dict[str, Any]:
        """获取管理器状态"""
        return {
            "total_users": len(self.user_contexts),
            "active_sessions": len([s for s in self.session_contexts.values() if s.status == "active"]),
            "total_sessions": len(self.session_contexts),
            "websocket_status": dual_entrance_websocket_manager.get_connection_status()
        }
    
    def cleanup_inactive_sessions(self, max_inactive_time: int = 3600):
        """清理不活跃的会话"""
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, context in self.session_contexts.items():
            inactive_time = (current_time - context.last_activity).total_seconds()
            if inactive_time > max_inactive_time:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            asyncio.create_task(self.close_session(session_id))
        
        logger.info(f"清理了 {len(inactive_sessions)} 个不活跃的会话")


# 全局入口管理器实例
entrance_manager = EntranceManager()