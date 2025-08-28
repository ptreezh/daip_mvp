#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辩论状态管理系统

管理辩论会话的状态、持久化、恢复和同步。
支持分布式环境下的状态一致性和实时更新。
"""

import asyncio
import pickle
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import uuid
import threading

from .debate_flow_definition import (
    DebateSession, DebateContribution, 
    DebateStatus, DebatePhase, DebateParticipant
)


class StateChangeType(Enum):
    """状态变更类型"""
    SESSION_CREATED = "session_created"
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    PARTICIPANT_JOINED = "participant_joined"
    PARTICIPANT_LEFT = "participant_left"
    ROUND_STARTED = "round_started"
    ROUND_COMPLETED = "round_completed"
    PHASE_CHANGED = "phase_changed"
    CONTRIBUTION_ADDED = "contribution_added"
    CUSTOM = "custom"


@dataclass
class StateChange:
    """状态变更记录"""
    change_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    change_type: StateChangeType = StateChangeType.CUSTOM
    timestamp: datetime = field(default_factory=datetime.now)
    actor_id: Optional[str] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1


@dataclass
class StateSnapshot:
    """状态快照"""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    session_state: Dict[str, Any] = field(default_factory=dict)
    participant_states: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateStorage(ABC):
    """状态存储抽象接口"""
    
    @abstractmethod
    async def save_session(self, session: DebateSession) -> bool:
        """保存会话状态"""
        pass
    
    @abstractmethod
    async def load_session(self, session_id: str) -> Optional[DebateSession]:
        """加载会话状态"""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """删除会话状态"""
        pass
    
    @abstractmethod
    async def save_snapshot(self, snapshot: StateSnapshot) -> bool:
        """保存状态快照"""
        pass
    
    @abstractmethod
    async def load_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """加载状态快照"""
        pass
    
    @abstractmethod
    async def list_sessions(self, 
                           status: Optional[DebateStatus] = None,
                           limit: int = 100) -> List[str]:
        """列出会话ID"""
        pass


class MemoryStateStorage(StateStorage):
    """内存状态存储实现"""
    
    def __init__(self):
        self.sessions: Dict[str, DebateSession] = {}
        self.snapshots: Dict[str, StateSnapshot] = {}
        self._lock = threading.RLock()
    
    async def save_session(self, session: DebateSession) -> bool:
        """保存会话状态"""
        try:
            with self._lock:
                # 深拷贝以避免引用问题
                session_copy = pickle.loads(pickle.dumps(session))
                self.sessions[session.session_id] = session_copy
            return True
        except Exception:
            return False
    
    async def load_session(self, session_id: str) -> Optional[DebateSession]:
        """加载会话状态"""
        try:
            with self._lock:
                if session_id in self.sessions:
                    # 返回深拷贝
                    return pickle.loads(pickle.dumps(self.sessions[session_id]))
            return None
        except Exception:
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话状态"""
        try:
            with self._lock:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    return True
            return False
        except Exception:
            return False
    
    async def save_snapshot(self, snapshot: StateSnapshot) -> bool:
        """保存状态快照"""
        try:
            with self._lock:
                snapshot_copy = pickle.loads(pickle.dumps(snapshot))
                self.snapshots[snapshot.snapshot_id] = snapshot_copy
            return True
        except Exception:
            return False
    
    async def load_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """加载状态快照"""
        try:
            with self._lock:
                if snapshot_id in self.snapshots:
                    return pickle.loads(pickle.dumps(self.snapshots[snapshot_id]))
            return None
        except Exception:
            return None
    
    async def list_sessions(self, 
                           status: Optional[DebateStatus] = None,
                           limit: int = 100) -> List[str]:
        """列出会话ID"""
        with self._lock:
            session_ids = []
            for session_id, session in self.sessions.items():
                if status is None or session.status == status:
                    session_ids.append(session_id)
                if len(session_ids) >= limit:
                    break
            return session_ids


class DebateStateManager:
    """
    辩论状态管理器
    
    负责辩论会话的状态管理、持久化、同步和通知。
    支持分布式环境下的状态一致性和实时更新。
    """
    
    def __init__(self, storage: Optional[StateStorage] = None):
        self.storage = storage or MemoryStateStorage()
        
        # 内存缓存
        self.session_cache: Dict[str, DebateSession] = {}
        self.cache_lock = threading.RLock()
        
        # 状态变更历史
        self.change_history: List[StateChange] = []
        self.history_lock = threading.RLock()
        
        # 快照管理
        self.snapshots: Dict[str, List[str]] = {}  # session_id -> snapshot_ids
        
        # 配置
        self.auto_save_interval = 60  # 自动保存间隔（秒）
        self.max_history_size = 1000  # 最大历史记录数
        self.max_snapshots_per_session = 10  # 每个会话最大快照数
    
    async def create_session(self, session: DebateSession) -> bool:
        """创建新的辩论会话"""
        try:
            # 保存到存储
            success = await self.storage.save_session(session)
            if not success:
                return False
            
            # 更新缓存
            with self.cache_lock:
                self.session_cache[session.session_id] = session
            
            # 记录状态变更
            change = StateChange(
                session_id=session.session_id,
                change_type=StateChangeType.SESSION_CREATED,
                new_state={"status": session.status.value},
                metadata={"title": session.title, "topic": session.topic}
            )
            await self._record_state_change(change)
            
            return True
        
        except Exception as e:
            print(f"Error creating session {session.session_id}: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[DebateSession]:
        """获取辩论会话"""
        try:
            # 先检查缓存
            with self.cache_lock:
                if session_id in self.session_cache:
                    return self.session_cache[session_id]
            
            # 从存储加载
            session = await self.storage.load_session(session_id)
            if session:
                # 更新缓存
                with self.cache_lock:
                    self.session_cache[session_id] = session
            
            return session
        
        except Exception as e:
            print(f"Error getting session {session_id}: {e}")
            return None
    
    async def update_session(self, 
                           session: DebateSession,
                           actor_id: Optional[str] = None,
                           change_type: StateChangeType = StateChangeType.CUSTOM) -> bool:
        """更新辩论会话"""
        try:
            # 获取旧状态
            old_session = await self.get_session(session.session_id)
            previous_state = None
            if old_session:
                previous_state = {
                    "status": old_session.status.value,
                    "current_round": old_session.current_round,
                    "participants_count": len(old_session.participants)
                }
            
            # 保存到存储
            success = await self.storage.save_session(session)
            if not success:
                return False
            
            # 更新缓存
            with self.cache_lock:
                self.session_cache[session.session_id] = session
            
            # 记录状态变更
            new_state = {
                "status": session.status.value,
                "current_round": session.current_round,
                "participants_count": len(session.participants)
            }
            
            change = StateChange(
                session_id=session.session_id,
                change_type=change_type,
                actor_id=actor_id,
                previous_state=previous_state,
                new_state=new_state
            )
            await self._record_state_change(change)
            
            return True
        
        except Exception as e:
            print(f"Error updating session {session.session_id}: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """删除辩论会话"""
        try:
            # 从存储删除
            success = await self.storage.delete_session(session_id)
            if not success:
                return False
            
            # 从缓存删除
            with self.cache_lock:
                if session_id in self.session_cache:
                    del self.session_cache[session_id]
            
            # 清理快照
            if session_id in self.snapshots:
                del self.snapshots[session_id]
            
            # 记录状态变更
            change = StateChange(
                session_id=session_id,
                change_type=StateChangeType.SESSION_COMPLETED
            )
            await self._record_state_change(change)
            
            return True
        
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    async def add_participant(self,
                            session_id: str,
                            participant: DebateParticipant,
                            actor_id: Optional[str] = None) -> bool:
        """添加参与者"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # 检查参与者是否已存在
        existing_ids = [p.participant_id for p in session.participants]
        if participant.participant_id in existing_ids:
            return False
        
        session.participants.append(participant)
        
        success = await self.update_session(
            session, actor_id, StateChangeType.PARTICIPANT_JOINED
        )
        
        return success
    
    async def remove_participant(self,
                               session_id: str,
                               participant_id: str,
                               actor_id: Optional[str] = None) -> bool:
        """移除参与者"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # 查找并移除参与者
        original_count = len(session.participants)
        session.participants = [
            p for p in session.participants 
            if p.participant_id != participant_id
        ]
        
        if len(session.participants) == original_count:
            return False  # 参与者不存在
        
        success = await self.update_session(
            session, actor_id, StateChangeType.PARTICIPANT_LEFT
        )
        
        return success
    
    async def add_contribution(self,
                             session_id: str,
                             contribution: DebateContribution,
                             actor_id: Optional[str] = None) -> bool:
        """添加辩论贡献"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        if not session.rounds:
            return False
        
        current_round = session.rounds[session.current_round - 1]
        current_round.contributions.append(contribution)
        
        success = await self.update_session(
            session, actor_id, StateChangeType.CONTRIBUTION_ADDED
        )
        
        return success
    
    async def advance_phase(self,
                          session_id: str,
                          new_phase: DebatePhase,
                          actor_id: Optional[str] = None) -> bool:
        """推进辩论阶段"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        if not session.rounds:
            return False
        
        current_round = session.rounds[session.current_round - 1]
        old_phase = current_round.current_phase
        current_round.current_phase = new_phase
        
        success = await self.update_session(
            session, actor_id, StateChangeType.PHASE_CHANGED
        )
        
        if success:
            # 记录阶段变更详情
            change = StateChange(
                session_id=session_id,
                change_type=StateChangeType.PHASE_CHANGED,
                actor_id=actor_id,
                previous_state={"phase": old_phase.value},
                new_state={"phase": new_phase.value},
                metadata={"round": session.current_round}
            )
            await self._record_state_change(change)
        
        return success
    
    async def create_snapshot(self,
                            session_id: str,
                            metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """创建状态快照"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return None
            
            # 创建快照
            snapshot = StateSnapshot(
                session_id=session_id,
                session_state=asdict(session),
                metadata=metadata or {}
            )
            
            # 保存快照
            success = await self.storage.save_snapshot(snapshot)
            if not success:
                return None
            
            # 管理快照数量
            if session_id not in self.snapshots:
                self.snapshots[session_id] = []
            
            self.snapshots[session_id].append(snapshot.snapshot_id)
            
            # 限制快照数量
            if len(self.snapshots[session_id]) > self.max_snapshots_per_session:
                # 删除最旧的快照
                oldest_snapshot_id = self.snapshots[session_id].pop(0)
                # 这里可以添加删除存储中快照的逻辑
            
            return snapshot.snapshot_id
        
        except Exception as e:
            print(f"Error creating snapshot for session {session_id}: {e}")
            return None
    
    async def get_session_history(self,
                                session_id: str,
                                limit: int = 100) -> List[StateChange]:
        """获取会话历史"""
        with self.history_lock:
            history = [
                change for change in self.change_history
                if change.session_id == session_id
            ]
            
            # 按时间倒序排列
            history.sort(key=lambda x: x.timestamp, reverse=True)
            
            return history[:limit]
    
    async def get_active_sessions(self) -> List[str]:
        """获取活跃会话列表"""
        return await self.storage.list_sessions(DebateStatus.ACTIVE)
    
    async def get_session_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话指标"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # 计算基本指标
        total_contributions = sum(len(round.contributions) for round in session.rounds)
        total_participants = len(session.participants)
        
        # 计算持续时间
        duration_minutes = 0
        if session.started_at:
            end_time = session.completed_at or datetime.now()
            duration = end_time - session.started_at
            duration_minutes = duration.total_seconds() / 60
        
        # 获取历史记录数
        history = await self.get_session_history(session_id)
        
        return {
            "session_id": session_id,
            "status": session.status.value,
            "total_rounds": len(session.rounds),
            "current_round": session.current_round,
            "total_participants": total_participants,
            "total_contributions": total_contributions,
            "duration_minutes": duration_minutes,
            "state_changes": len(history),
            "created_at": session.created_at.isoformat(),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
    
    async def _record_state_change(self, change: StateChange) -> None:
        """记录状态变更"""
        with self.history_lock:
            self.change_history.append(change)
            
            # 限制历史记录大小
            if len(self.change_history) > self.max_history_size:
                self.change_history = self.change_history[-self.max_history_size:]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            # 统计会话数量
            all_sessions = await self.storage.list_sessions()
            active_sessions = await self.storage.list_sessions(DebateStatus.ACTIVE)
            
            # 缓存统计
            with self.cache_lock:
                cached_sessions = len(self.session_cache)
            
            # 历史记录统计
            with self.history_lock:
                total_changes = len(self.change_history)
            
            return {
                "total_sessions": len(all_sessions),
                "active_sessions": len(active_sessions),
                "cached_sessions": cached_sessions,
                "total_state_changes": total_changes,
                "system_uptime": datetime.now().isoformat(),
                "storage_type": type(self.storage).__name__
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# 使用示例和测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_debate_state_manager():
        """测试辩论状态管理器"""
        print("🧪 测试辩论状态管理器...")
        
        # 创建状态管理器
        state_manager = DebateStateManager()
        
        # 创建测试会话
        from debate_flow_definition import DebateSession, DebateParticipant, ParticipantRole
        
        session = DebateSession(
            title="测试辩论",
            topic="人工智能的未来发展",
            description="讨论AI技术的发展趋势和影响"
        )
        
        # 测试创建会话
        success = await state_manager.create_session(session)
        print(f"✅ 创建会话: {'成功' if success else '失败'}")
        
        # 测试获取会话
        retrieved_session = await state_manager.get_session(session.session_id)
        print(f"✅ 获取会话: {'成功' if retrieved_session else '失败'}")
        
        # 测试添加参与者
        participant = DebateParticipant(
            participant_id="user_001",
            name="测试用户",
            role=ParticipantRole.PROPONENT
        )
        
        success = await state_manager.add_participant(
            session.session_id, participant, "system"
        )
        print(f"✅ 添加参与者: {'成功' if success else '失败'}")
        
        # 测试创建快照
        snapshot_id = await state_manager.create_snapshot(
            session.session_id, {"reason": "测试快照"}
        )
        print(f"✅ 创建快照: {'成功' if snapshot_id else '失败'}")
        
        # 测试获取会话指标
        metrics = await state_manager.get_session_metrics(session.session_id)
        print(f"✅ 获取指标: {'成功' if metrics else '失败'}")
        if metrics:
            print(f"   - 参与者数量: {metrics['total_participants']}")
            print(f"   - 状态变更: {metrics['state_changes']}")
        
        # 测试获取系统状态
        system_status = await state_manager.get_system_status()
        print(f"✅ 系统状态: {system_status}")
        
        print("🎉 辩论状态管理器测试完成！")
    
    # 运行测试
    asyncio.run(test_debate_state_manager())