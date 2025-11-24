"""
扩展的上下文管理器，支持历史分析功能
"""

from typing import Dict, Any, Optional
from .context_manager import ContextManager
from .conversation_history_analyzer import ConversationHistoryAnalyzer


class HistoryAwareContextManager(ContextManager):
    """支持历史分析的上下文管理器"""
    
    def __init__(self):
        super().__init__()
        self.history_analyzer = ConversationHistoryAnalyzer()
    
    def get_relevant_content_for_task(self, session_id: str, task_type: str) -> Dict[str, Any]:
        """
        为任务获取相关的历史内容
        
        Args:
            session_id: 会话ID
            task_type: 任务类型
            
        Returns:
            包含相关历史内容的字典
        """
        session_state = self.get_session_state(session_id)
        if not session_state or not session_state.history:
            return {}
        
        # 分析历史记录以提取相关内容
        if task_type == 'create_wiki':
            return self.history_analyzer.extract_debate_content_from_history(session_state.history)
        
        # 未来可扩展其他任务类型
        return {}