"""
增强的意图识别器 - 支持置信度循环和工作流切换
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """意图类型枚举"""
    QUESTION = "question"      # 问题类对话
    CHAT = "chat"            # 普通聊天
    WORKFLOW = "workflow"      # 工作流（辩论、论文下载、Wiki等）


@dataclass
class Intent:
    """意图数据类"""
    name: str
    confidence: float
    parameters: Dict[str, Any]
    tool_name: Optional[str] = None
    description: str = ""
    intent_type: IntentType = IntentType.CHAT
    requires_confidence_check: bool = False


class EnhancedIntentRecognizer:
    """增强的自然语言意图识别器"""
    
    def __init__(self):
        """初始化增强意图识别器"""
        self.intent_patterns = {
            # 问题类意图 - 需要置信度检查
            "question": {
                "patterns": [
                    r".+\?",                          # 以问号结尾
                    r"什么是",
                    r"如何",
                    r"为什么",
                    r"怎么",
                    r"怎样",
                    r".*吗\?",
                    r".*呢\?",
                    r"能否",
                    r"可否",
                    r"是否"
                ],
                "tool": None,
                "extract_params": self._extract_question_params,
                "description": "问题类对话",
                "intent_type": IntentType.QUESTION,
                "requires_confidence_check": True
            },
            
            # 普通聊天意图 - 直接回答
            "chat": {
                "patterns": [
                    r"你好",
                    r"hi",
                    r"hello",
                    r"谢谢",
                    r"再见",
                    r"早上好",
                    r"晚上好",
                    r"你好吗",
                    r"怎么样",
                    r"最近.*"
                ],
                "tool": None,
                "extract_params": self._extract_chat_params,
                "description": "普通聊天",
                "intent_type": IntentType.CHAT,
                "requires_confidence_check": False
            },
            
            # 论文检索工作流 - 进入专门流程
            "search_papers": {
                "patterns": [
                    r"搜索.*论文",
                    r"查找.*论文", 
                    r"找.*论文",
                    r"search.*paper",
                    r"find.*paper",
                    r"论文.*搜索",
                    r"学术.*搜索",
                    r"arxiv.*搜索",
                    r"下载.*论文",
                    r"download.*paper"
                ],
                "tool": "search_academic_papers",
                "extract_params": self._extract_search_params,
                "description": "学术论文检索工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 论文下载工作流
            "download_paper": {
                "patterns": [
                    r"下载.*论文.*(\d+\.\d+)",
                    r"下载.*arxiv.*(\d+\.\d+)",
                    r"download.*arxiv.*(\d+\.\d+)",
                    r"获取.*论文.*(\d+\.\d+)"
                ],
                "tool": "download_paper",
                "extract_params": self._extract_download_params,
                "description": "论文下载工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 辩论工作流
            "start_debate": {
                "patterns": [
                    r"开始.*辩论",
                    r"发起.*辩论",
                    r"辩论.*话题",
                    r"debate.*topic",
                    r"讨论.*话题",
                    r"我们来辩论.*",
                    r"我想辩论.*"
                ],
                "tool": "debate",
                "extract_params": self._extract_debate_params,
                "description": "辩论工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # Wiki工作流
            "create_wiki": {
                "patterns": [
                    r"创建.*wiki",
                    r"新建.*wiki",
                    r"写.*wiki",
                    r"编辑.*wiki",
                    r"wiki.*页面",
                    r"create.*wiki",
                    r"edit.*wiki"
                ],
                "tool": "wiki",
                "extract_params": self._extract_wiki_params,
                "description": "Wiki创建工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 压缩上下文
            "compress_context": {
                "patterns": [
                    r"压缩.*上下文",
                    r"清理.*历史",
                    r"压缩.*对话",
                    r"compress.*context",
                    r"清理.*内存",
                    r"内存.*管理"
                ],
                "tool": "compress",
                "extract_params": self._extract_compress_params,
                "description": "上下文压缩",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 项目初始化工作流
            "initialize_project": {
                "patterns": [
                    r"初始化.*项目",
                    r"创建.*项目",
                    r"新建.*项目",
                    r"初始化.*环境",
                    r"setup.*project",
                    r"init.*project"
                ],
                "tool": "scaffold",
                "extract_params": self._extract_scaffold_params,
                "description": "项目初始化工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 查看辩论历史
            "view_debate_history": {
                "patterns": [
                    r"显示.*辩论.*历史",
                    r"查看.*辩论.*历史",
                    r"辩论.*历史",
                    r"show.*debate.*history",
                    r"list.*debates?",
                    r"view.*debates?",
                    r"what.*debates?.*there",
                    r"show.*past.*debates?",
                    r"list.*debate.*sessions?",
                    r"view.*debate.*sessions?",
                    r"辩论.*列表",
                    r"历史.*辩论",
                    r"过去.*辩论.*哪些",
                    r"之前的.*辩论.*情况",
                    r"最近.*辩论.*结果",
                    r"上次.*辩论.*情况",
                    r"近期.*辩论.*记录",
                    r"历史.*记录.*辩论"
                ],
                "tool": "debate_history",
                "extract_params": self._extract_debate_history_params,
                "description": "查看辩论历史",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 查看特定辩论历史
            "view_specific_debate": {
                "patterns": [
                    r"显示.*辩论.*(\w+)",
                    r"查看.*辩论.*(\w+)",
                    r"查看.*辩论.*session.*(\w+)",
                    r"查看.*session.*(\w+).*辩论",
                    r"显示.*debate.*(\w+)",
                    r"view.*debate.*(\w+)",
                    r"show.*debate.*(\w+)",
                    r"view.*session.*(\w+)",
                    r"show.*session.*(\w+)"
                ],
                "tool": "debate_history",
                "extract_params": self._extract_specific_debate_params,
                "description": "查看特定辩论历史",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            }
        }
    
    def recognize_intent(self, text: str) -> Optional[Intent]:
        """
        识别用户输入的意图
        
        Args:
            text: 用户输入文本
            
        Returns:
            识别到的意图，如果没有匹配则返回None
        """
        text = text.strip().lower()
        
        best_intent = None
        best_confidence = 0.0
        
        for intent_name, intent_config in self.intent_patterns.items():
            for pattern in intent_config["patterns"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # 计算匹配置信度
                    confidence = len(match.group(0)) / len(text)
                    
                    if confidence > best_confidence:
                        # 提取参数
                        params = intent_config["extract_params"](text, match)
                        
                        best_intent = Intent(
                            name=intent_name,
                            confidence=confidence,
                            parameters=params,
                            tool_name=intent_config["tool"],
                            description=intent_config["description"],
                            intent_type=intent_config["intent_type"],
                            requires_confidence_check=intent_config["requires_confidence_check"]
                        )
                        best_confidence = confidence
        
        # 设置置信度阈值
        if best_intent and best_confidence > 0.3:
            return best_intent
        
        return None
    
    def _extract_question_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取问题参数"""
        return {
            "question": text,
            "requires_confidence_check": True
        }
    
    def _extract_chat_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取聊天参数"""
        return {
            "chat_content": text,
            "requires_confidence_check": False
        }
    
    def _extract_search_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取论文搜索参数"""
        # 尝试提取搜索关键词
        keywords = []
        
        # 常见学术关键词模式
        academic_patterns = [
            r"关于(.+?)的论文",
            r"搜索(.+?)论文",
            r"查找(.+?)相关",
            r"search.*for(.+)",
            r"find.*papers.*about(.+)"
        ]
        
        for pattern in academic_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                keywords.append(m.group(1).strip())
        
        # 如果没有找到特定关键词，使用整个文本作为查询
        if not keywords:
            # 移除命令词，保留核心搜索词
            cleaned_text = re.sub(r"(搜索|查找|找|search|find|论文|paper)", "", text, flags=re.IGNORECASE)
            keywords = [cleaned_text.strip()]
        
        return {
            "query": " ".join(keywords) if keywords else text,
            "max_results": 10,
            "source": "arxiv"
        }
    
    def _extract_download_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取论文下载参数"""
        paper_id = match.group(1) if match.groups() else None
        
        return {
            "paper_id": paper_id,
            "save_path": None,
            "format": "pdf"
        }
    
    def _extract_debate_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取辩论参数"""
        # 尝试提取辩论主题
        topic_patterns = [
            r"辩论.*[:：](.+)",
            r"话题[:：](.+)",
            r"关于(.+?)的辩论",
            r"debate.*about(.+)"
        ]
        
        topic = None
        for pattern in topic_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                topic = m.group(1).strip()
                break
        
        # 如果没有找到特定主题，使用整个文本
        if not topic:
            topic = text
        
        return {
            "topic": topic,
            "roles": None,  # 使用默认角色
            "rounds": 3     # 默认3轮
        }
    
    def _extract_wiki_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取Wiki参数"""
        # 尝试提取页面标题
        title_patterns = [
            r"创建.*wiki.*[:：](.+)",
            r"wiki.*页面[:：](.+)",
            r"编辑.*wiki.*[:：](.+)",
            r"create.*wiki.*[:](.+)",
            r"edit.*wiki.*[:](.+)"
        ]
        
        title = None
        for pattern in title_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                title = m.group(1).strip()
                break
        
        # 如果没有找到特定标题，使用整个文本
        if not title:
            title = text
        
        return {
            "title": title,
            "content": "",  # 将由用户后续提供
            "tags": []
        }
    
    def _extract_compress_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取压缩参数"""
        return {
            "method": "auto",  # 自动压缩
            "keep_recent": 5   # 保留最近5条对话
        }
    
    def _extract_scaffold_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取项目初始化参数"""
        # 尝试提取项目类型或描述
        type_patterns = [
            r"创建.*(.+?)项目",
            r"初始化.*(.+?)项目",
            r"新建.*(.+?)项目",
            r"create.*(.+?)project",
            r"init.*(.+?)project"
        ]
        
        project_type = None
        for pattern in type_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                project_type = m.group(1).strip()
                break
        
        return {
            "project_type": project_type or "general",
            "description": text
        }
    
    def _extract_debate_history_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取辩论历史查询参数"""
        return {
            "query": text,
            "session_id": None  # Will be extracted if specific session is mentioned
        }
    
    def _extract_specific_debate_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取特定辩论查询参数"""
        # Extract session ID or debate ID if present in the match
        session_id = None
        if match.groups():
            session_id = match.group(1)  # First capture group usually contains the ID
        
        # Look for more specific session ID patterns if not already found
        if not session_id:
            session_patterns = [
                r"session[:\s]*([a-zA-Z0-9_-]+)",
                r"debate[:\s]*([a-zA-Z0-9_-]+)",
                r"([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})",  # UUID pattern
            ]
            
            for pattern in session_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    session_id = m.group(1)
                    break
        
        return {
            "query": text,
            "session_id": session_id
        }
    
    def get_available_intents(self) -> List[str]:
        """获取所有可用的意图列表"""
        return list(self.intent_patterns.keys())
    
    def get_intent_description(self, intent_name: str) -> str:
        """获取意图描述"""
        if intent_name in self.intent_patterns:
            return self.intent_patterns[intent_name]["description"]
        return "未知意图"