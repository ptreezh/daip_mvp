"""
信息提取和参数预填充系统
用于解决用户输入中已包含明确信息但未被提取的问题
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import re
from datetime import datetime


@dataclass
class ExtractedParameters:
    """提取的参数数据模型"""
    title: Optional[str] = None
    topic: Optional[str] = None
    arxiv_id: Optional[str] = None
    content: Optional[str] = None
    keywords: List[str] = None
    extracted_at: datetime = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.extracted_at is None:
            self.extracted_at = datetime.now()


class ParameterExtractor:
    """参数提取器 - 从用户输入中提取已有的参数"""
    
    def __init__(self):
        # 论文相关提取模式
        self.paper_patterns = [
            # 匹配arXiv ID
            (r'(\d{4}\.\d{4,5}(v\d+)?)', 'arxiv_id'),
            # 匹配论文主题关键词
            (r'(?:关于|有关|的)\s*([^，。；！？\s]+(?:\s+[^，。；！？\s]+)*)\s*论文', 'topic'),
            (r'论文\s+([^，。；！？\s]+(?:\s+[^，。；！？\s]+)*)', 'topic'),
            (r'下载\s+([^，。；！？\s]+(?:\s+[^，。；！？\s]+)*)\s*论文', 'topic'),
        ]
        
        # Wiki相关提取模式
        self.wiki_patterns = [
            (r'(?:编写|创建|新建|生成|写)\s*[^，。；！？\s]*\s*(.+?)(?:的\s*词条|词条|页面|百科)', 'title'),
            (r'(?:关于|有关)\s*(.+?)(?:的\s*词条|词条|页面|百科)', 'title'),
            (r'(?:词条|页面|百科)\s*(.+)', 'title'),
        ]
        
        # 通用参数提取模式
        self.general_patterns = [
            (r'(?:主题|话题|议题|题目|标题)\s*[:：]\s*([^，。；！？\s]+(?:\s+[^，。；！？\s]+)*)', 'topic'),
            (r'(?:关键词|关键字|关键词)\s*[:：]\s*([^，。；！？\s]+(?:\s+[^，。；！？\s]+)*)', 'keywords'),
        ]
    
    def extract_from_input(self, user_input: str, task_type: str = None) -> ExtractedParameters:
        """从用户输入中提取参数"""
        params = ExtractedParameters()
        
        # 根据任务类型选择合适的提取模式
        patterns = []
        if task_type == 'paper':
            patterns = self.paper_patterns + self.general_patterns
        elif task_type == 'wiki':
            patterns = self.wiki_patterns + self.general_patterns
        else:
            patterns = self.paper_patterns + self.wiki_patterns + self.general_patterns
        
        for pattern, param_type in patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                # 如果match是元组（有多个捕获组），取第一个捕获组
                if isinstance(matches[0], tuple):
                    value = matches[0][0].strip() if matches[0][0] else ""
                else:
                    value = matches[0].strip()

                if param_type == 'keywords':
                    if isinstance(matches[0], tuple):
                        params.keywords.extend([val.strip() for val in matches[0] if val.strip()])
                    else:
                        params.keywords.append(value)
                elif param_type == 'topic' and not params.topic:
                    params.topic = value
                elif param_type == 'title' and not params.title:
                    params.title = value
                elif param_type == 'arxiv_id' and not params.arxiv_id:
                    params.arxiv_id = value
        
        # 尝试提取一般性的内容
        if not params.topic and not params.title:
            # 智能提取输入中的关键内容
            cleaned_input = re.sub(r'^(?:下载|创建|帮我|请|我想|需要)\s*', '', user_input, flags=re.IGNORECASE)
            cleaned_input = re.sub(r'[，。；！？:\s]+$', '', cleaned_input)
            cleaned_input = cleaned_input.strip()
            
            # 如果清理后的输入有意义，且没有其他参数，可以作为主题
            if cleaned_input and len(cleaned_input) > 2:
                if task_type == 'wiki' and not params.title:
                    params.title = cleaned_input
                elif task_type in ['paper', None] and not params.topic:
                    params.topic = cleaned_input
        
        return params


class EnhancedContextManager:
    """增强版上下文管理器 - 集成参数提取功能"""
    
    def __init__(self):
        self.sessions: Dict[str, Any] = {}
        self.parameter_extractor = ParameterExtractor()
    
    def set_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """设置特定会话的上下文"""
        if session_id not in self.sessions:
            from src.intent_recognition.session_state import SessionState
            self.sessions[session_id] = SessionState(session_id=session_id)
        
        session_state = self.sessions[session_id]
        
        # 创建新的任务上下文
        from src.intent_recognition.task_context import TaskContext
        task_type = context.get('task_type', '')
        required_params = context.get('required_params', [])
        task_context = TaskContext(
            task_type=task_type,
            required_params=required_params
        )
        
        session_state.current_task = task_context
        session_state.update_last_accessed()
    
    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取特定会话的上下文"""
        if session_id not in self.sessions:
            return None
        
        session_state = self.sessions[session_id]
        if session_state.current_task is None:
            return None
        
        return {
            'task_type': session_state.current_task.task_type,
            'parameters': session_state.current_task.parameters,
            'required_params': session_state.current_task.required_params,
            'filled_params': session_state.current_task.filled_params,
            'status': session_state.current_task.status
        }
    
    def clear_context(self, session_id: str) -> None:
        """清除特定会话的上下文"""
        if session_id in self.sessions:
            self.sessions[session_id].current_task = None
            self.sessions[session_id].update_last_accessed()
    
    def is_in_task(self, session_id: str) -> bool:
        """检查会话是否正在进行任务"""
        if session_id not in self.sessions:
            return False
        
        return self.sessions[session_id].has_active_task()
    
    def add_task_parameter(self, session_id: str, param_name: str, param_value: Any) -> bool:
        """为指定会话的任务添加参数"""
        if session_id not in self.sessions or self.sessions[session_id].current_task is None:
            return False
        
        self.sessions[session_id].current_task.add_parameter(param_name, param_value)
        self.sessions[session_id].update_last_accessed()
        return True
    
    def process_user_input_with_extraction(self, session_id: str, user_input: str) -> tuple:
        """处理用户输入并尝试提取参数"""
        # 检查是否在任务中
        if not self.is_in_task(session_id):
            # 不在任务中，直接返回
            return False, user_input
        
        # 获取当前任务的类型
        context = self.get_context(session_id)
        task_type = context['task_type'] if context else None
        
        # 尝试从用户输入中提取参数
        extracted_params = self.parameter_extractor.extract_from_input(user_input, task_type)
        
        # 检查提取的结果，看是否可以直接填充任务参数
        session_task = self.sessions[session_id].current_task
        missing_params = session_task.get_missing_params()
        
        filled_params = []
        
        # 根据需要的参数类型尝试填充
        if 'title' in missing_params and extracted_params.title:
            self.add_task_parameter(session_id, 'title', extracted_params.title)
            filled_params.append(('title', extracted_params.title))
        
        if 'topic' in missing_params and extracted_params.topic:
            self.add_task_parameter(session_id, 'topic', extracted_params.topic)
            filled_params.append(('topic', extracted_params.topic))
        
        if 'content' in missing_params and extracted_params.content:
            self.add_task_parameter(session_id, 'content', extracted_params.content)
            filled_params.append(('content', extracted_params.content))
            
        if 'arxiv_id' in missing_params and extracted_params.arxiv_id:
            self.add_task_parameter(session_id, 'arxiv_id', extracted_params.arxiv_id)
            filled_params.append(('arxiv_id', extracted_params.arxiv_id))
        
        # 如果还有未填充的关键参数，但仍有一些信息提取到，可考虑填充
        if extracted_params.topic and 'keywords' in missing_params:
            self.add_task_parameter(session_id, 'keywords', extracted_params.topic)  # 临时用topic作为keywords
            filled_params.append(('keywords', extracted_params.topic))
        
        return len(filled_params) > 0, user_input, extracted_params, filled_params