"""
会话状态存储实现
遵循开闭原则 - 对扩展开放，对修改关闭
"""

from typing import Dict, Any, Optional
from .session_state import SessionState


class SessionStateStore:
    """
    会话状态存储实现
    遵循开闭原则 - 对扩展开放，对修改关闭
    """
    
    def __init__(self):
        # 可以扩展为其他存储方式（如Redis、数据库等）
        self._storage: Dict[str, SessionState] = {}
    
    def store(self, session_id: str, state: SessionState) -> None:
        """
        存储会话状态
        
        Args:
            session_id: 会话标识符
            state: 会话状态对象
        """
        self._storage[session_id] = state
    
    def retrieve(self, session_id: str) -> Optional[SessionState]:
        """
        获取会话状态
        
        Args:
            session_id: 会话标识符
            
        Returns:
            会话状态对象，如果不存在则返回None
        """
        return self._storage.get(session_id)
    
    def delete(self, session_id: str) -> bool:
        """
        删除会话状态
        
        Args:
            session_id: 会话标识符
            
        Returns:
            如果成功删除则返回True，否则返回False
        """
        if session_id in self._storage:
            del self._storage[session_id]
            return True
        return False
    
    def update(self, session_id: str, state: SessionState) -> bool:
        """
        更新已存在的会话状态
        
        Args:
            session_id: 会话标识符
            state: 新的会话状态对象
            
        Returns:
            如果成功更新则返回True，否则返回False
        """
        if session_id in self._storage:
            self._storage[session_id] = state
            return True
        return False