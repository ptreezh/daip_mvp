"""
意图识别上下文管理接口定义
遵循接口隔离原则 - 最小化接口方法
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class IContextManager(ABC):
    """
    上下文管理器接口
    遵循接口隔离原则 - 定义最小化的接口方法
    """
    
    @abstractmethod
    def set_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """
        设置特定会话的上下文
        
        Args:
            session_id: 会话标识符
            context: 上下文数据
        """
        pass

    @abstractmethod
    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定会话的上下文
        
        Args:
            session_id: 会话标识符
            
        Returns:
            会话上下文数据，如果不存在则返回None
        """
        pass

    @abstractmethod
    def clear_context(self, session_id: str) -> None:
        """
        清除特定会话的上下文
        
        Args:
            session_id: 会话标识符
        """
        pass

    @abstractmethod
    def is_in_task(self, session_id: str) -> bool:
        """
        检查会话是否正在进行任务
        
        Args:
            session_id: 会话标识符
            
        Returns:
            如果会话正在进行任务则返回True，否则返回False
        """
        pass


class IIntentRecognizer(ABC):
    """
    意图识别器接口
    遵循接口隔离原则 - 定义最小化的接口方法
    """
    
    @abstractmethod
    def recognize_intent(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        识别用户输入的意图
        
        Args:
            session_id: 会话标识符
            user_input: 用户输入
            
        Returns:
            包含意图识别结果的字典
        """
        pass