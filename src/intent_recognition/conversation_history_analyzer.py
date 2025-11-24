"""
对话历史分析和信息提取服务
用于从之前的会话记录中提取相关信息
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re


class ConversationHistoryAnalyzer:
    """对话历史分析器 - 从历史记录中提取相关信息"""
    
    def __init__(self):
        # 定义用于识别辩论内容的关键模式
        self.debate_patterns = [
            # 辩论结论、结果相关
            (r'(?:辩论|讨论)结果[:：]?\s*([^。！？\n]+)', re.IGNORECASE),
            (r'(?:结论|总结)[:：]?\s*([^。！？\n]+)', re.IGNORECASE),
            (r'(?:最终|最后)观点[:：]?\s*([^。！？\n]+)', re.IGNORECASE),
            (r'(?:达成|形成)共识[:：]?\s*([^。！？\n]+)', re.IGNORECASE),
            (r'双方同意[:：]?\s*([^。！？\n]+)', re.IGNORECASE),
            (r'关键点[:：]?\s*([^。！？\n]+)', re.IGNORECASE),
            (r'核心议题[:：]?\s*([^。！？\n]+)', re.IGNORECASE),
            # 匹配多行的辩论总结
            (r'(?:辩论|讨论)总结[\n\s]*([^\n]+(?:\n[^\n]+)*)', re.IGNORECASE),
            (r'(?:结论|最终)是[:：]?\s*([^\n]+(?:\n[^\n]+)*)', re.IGNORECASE),
        ]
        
        # 定义用于识别对话主题的模式
        self.topic_patterns = [
            (r'关于(?:.*?的)?\s*(\w+)', re.IGNORECASE),
            (r'讨论(?:.*?的)?\s*(\w+)', re.IGNORECASE),
            (r'辩论(?:.*?的)?\s*(\w+)', re.IGNORECASE),
            (r'话题[:：]?\s*([^\n，。！？\s]+)', re.IGNORECASE),
        ]
    
    def extract_debate_content_from_history(self, history: List[Dict[str, Any]], 
                                          max_messages: int = 10) -> Dict[str, Any]:
        """
        从对话历史中提取辩论内容
        
        Args:
            history: 会话历史记录
            max_messages: 分析的最大消息数（从最新开始）
            
        Returns:
            包含提取内容的字典
        """
        if not history:
            return {"topic": None, "content": None, "summary": None, "confidence": 0.0}
        
        # 取最近的消息进行分析
        recent_messages = history[-max_messages:] if len(history) > max_messages else history
        
        # 将消息内容连接起来
        all_content = ""
        debate_segments = []
        
        for msg in recent_messages:
            content = msg.get('content', '') or msg.get('message', '') or msg.get('text', '')
            role = msg.get('role', '') or msg.get('sender', '')
            timestamp = msg.get('timestamp', '')
            
            message_text = f"[{role}] {content}"
            all_content += message_text + "\n"
            
            # 如果消息来自系统或助手，可能包含辩论结果
            if role.lower() in ['system', 'assistant', 'ai', '']:
                debate_segments.append(message_text)
        
        # 从完整内容中提取信息
        topic = self._extract_topic(all_content)
        content = self._extract_debate_content(all_content)
        summary = self._extract_summary(all_content)
        
        # 计算置信度
        confidence = self._calculate_extraction_confidence(topic, content, summary)
        
        return {
            "topic": topic,
            "content": content,
            "summary": summary,
            "confidence": confidence,
            "debug_content": all_content  # 用于调试
        }
    
    def _extract_topic(self, text: str) -> Optional[str]:
        """从文本中提取主题"""
        for pattern, flags in self.topic_patterns:
            match = re.search(pattern, text, flags)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_debate_content(self, text: str) -> Optional[str]:
        """从文本中提取辩论内容"""
        for pattern, flags in self.debate_patterns:
            match = re.search(pattern, text, flags)
            if match:
                content = match.group(1).strip()
                # 过滤掉一些太短或不太可能的内容
                if len(content) > 5:  # 至少5个字符
                    return content
        return None
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """提取可能的总结信息"""
        # 查找明确标记为总结的内容
        summary_patterns = [
            (r'总结[:：]\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|$)', re.IGNORECASE),
            (r'结论[:：]\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|$)', re.IGNORECASE),
        ]
        
        for pattern, flags in summary_patterns:
            matches = re.finditer(pattern, text, flags)
            for match in matches:
                summary = match.group(1).strip()
                if len(summary) > 10:  # 至少10个字符
                    return summary
        return None
    
    def _calculate_extraction_confidence(self, topic: str, content: str, summary: str) -> float:
        """计算提取结果的置信度"""
        score = 0.0
        
        # 检查是否有提取到任何内容
        if topic:
            score += 0.3
        if content:
            score += 0.4
        if summary:
            score += 0.3
        
        return min(score, 1.0)  # 最大为1.0


class ConversationHistoryAnalyzerMixin:
    """对话历史分析混入类，用于扩展ContextManager的功能"""

    def __init__(self):
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
        session_state = self.get_session_state(session_id)  # 需要上下文管理器提供此方法
        if not session_state or not session_state.history:
            return {}

        # 分析历史记录以提取相关内容
        if task_type == 'create_wiki':
            return self.history_analyzer.extract_debate_content_from_history(session_state.history)

        # 未来可扩展其他任务类型
        return {}