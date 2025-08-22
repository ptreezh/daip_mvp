"""
Enhanced Intent Recognition System for DAIP-LIVE

This module provides advanced intent recognition capabilities with a comprehensive taxonomy
of 50+ intent categories across multiple domains, supporting multi-intent detection,
context awareness, and personalization.
"""

import logging
import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IntentCategory(str, Enum):
    """Enhanced intent categories covering all DAIP-LIVE functionality"""
    
    # Basic Communication Intents
    GREETING = "greeting"
    FAREWELL = "farewell"
    AFFIRMATION = "affirmation"
    NEGATION = "negation"
    APOLOGY = "apology"
    THANKS = "thanks"
    
    # Information Seeking Intents
    QUESTION = "question"
    CLARIFICATION = "clarification"
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    COMPARISON = "comparison"
    STATUS_INQUIRY = "status_inquiry"
    HELP_REQUEST = "help_request"
    
    # Task-Oriented Intents
    REQUEST = "request"
    COMMAND = "command"
    CREATION = "creation"
    MODIFICATION = "modification"
    DELETION = "deletion"
    CONFIGURATION = "configuration"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    OPTIMIZATION = "optimization"
    
    # Wiki-Specific Intents
    WIKI_CREATE = "wiki_create"
    WIKI_VIEW = "wiki_view"
    WIKI_EDIT = "wiki_edit"
    WIKI_DELETE = "wiki_delete"
    WIKI_SEARCH = "wiki_search"
    WIKI_LIST = "wiki_list"
    WIKI_EXPORT = "wiki_export"
    WIKI_COLLABORATE = "wiki_collaborate"
    WIKI_PROPOSAL_APPROVE = "wiki_proposal_approve"
    WIKI_PROPOSAL_REJECT = "wiki_proposal_reject"
    WIKI_PROPOSAL_LIST = "wiki_proposal_list"
    
    # Chat-Specific Intents
    CHAT_START = "chat_start"
    CHAT_MESSAGE = "chat_message"
    CHAT_HISTORY = "chat_history"
    CHAT_CLEAR = "chat_clear"
    CHAT_CLOSE = "chat_close"
    CHAT_DELETE = "chat_delete"
    CHAT_LIST = "chat_list"
    CHAT_INVITE = "chat_invite"
    
    # Role Management Intents
    ROLE_MATCH = "role_match"
    ROLE_LIST = "role_list"
    ROLE_STATS = "role_stats"
    ROLE_INVITE = "role_invite"
    
    # Debate & Collaboration Intents
    DEBATE_START = "debate_start"
    DEBATE_JOIN = "debate_join"
    DEBATE_MODERATE = "debate_moderate"
    CONTENT_GENERATE = "content_generate"
    COLLABORATE = "collaborate"
    FEEDBACK_PROVIDE = "feedback_provide"
    CONSENSUS_SEEK = "consensus_seek"
    
    # System-Specific Intents
    SYSTEM_STATUS = "system_status"
    ERROR_REPORT = "error_report"
    CONFIGURE = "configure"
    RESET = "reset"
    BACKUP = "backup"
    RESTORE = "restore"
    
    # Advanced Intents
    INTENT_CORRECTION = "intent_correction"
    TASK_DELEGATION = "task_delegation"
    WORKFLOW_AUTOMATION = "workflow_automation"
    PERSONALIZATION_REQUEST = "personalization_request"


class ConfidenceLevel(str, Enum):
    """Confidence levels for intent recognition"""
    VERY_LOW = "very_low"      # 0.0 - 0.3
    LOW = "low"               # 0.3 - 0.5
    MEDIUM = "medium"         # 0.5 - 0.7
    HIGH = "high"             # 0.7 - 0.9
    VERY_HIGH = "very_high"    # 0.9 - 1.0


class IntentSource(str, Enum):
    """Sources of intent detection"""
    KEYWORD_MATCH = "keyword_match"
    ML_CLASSIFICATION = "ml_classification"
    CONTEXT_ANALYSIS = "context_analysis"
    PERSONALIZATION = "personalization"
    ENSEMBLE = "ensemble"


@dataclass
class Entity:
    """Represents a named entity extracted from user input"""
    text: str
    label: str
    start_pos: int
    end_pos: int
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentSegment:
    """Represents a segment of user input with detected intent"""
    text: str
    start_pos: int
    end_pos: int
    intent: IntentCategory
    confidence: float
    entities: List[Entity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedIntentAnalysis(BaseModel):
    """Enhanced intent analysis result with comprehensive information"""
    
    # Core intent information
    user_input: str
    primary_intent: IntentCategory
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    
    # Multi-intent support
    secondary_intents: List[Tuple[IntentCategory, float]] = Field(default_factory=list)
    intent_segments: List[IntentSegment] = Field(default_factory=list)
    
    # Entity information
    entities: List[Entity] = Field(default_factory=list)
    
    # Context information
    context_requirements: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    
    # Detection metadata
    detection_sources: List[IntentSource] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    
    # Personalization
    user_id: Optional[str] = None
    personalization_score: float = 0.0
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntentRecognizerInterface(ABC):
    """Interface for advanced intent recognition systems"""
    
    @abstractmethod
    async def recognize_intent(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> EnhancedIntentAnalysis:
        """Recognize intent from user input with context awareness"""
        pass
    
    @abstractmethod
    async def recognize_multiple_intents(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> List[EnhancedIntentAnalysis]:
        """Recognize multiple intents in a single utterance"""
        pass
    
    @abstractmethod
    def get_intent_taxonomy(self) -> Dict[str, List[str]]:
        """Get the complete intent taxonomy with hierarchies"""
        pass
    
    @abstractmethod
    def get_intent_confidence(
        self, 
        intent: IntentCategory, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> float:
        """Get confidence score for specific intent"""
        pass


class KeywordIntentMatcher:
    """Advanced keyword-based intent matching with patterns and scoring"""
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.entity_patterns = self._build_entity_patterns()
    
    def _build_intent_patterns(self) -> Dict[IntentCategory, List[Dict[str, Any]]]:
        """Build comprehensive intent patterns for keyword matching"""
        
        patterns = {
            # Basic Communication
            IntentCategory.GREETING: [
                {"keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"], "weight": 1.0},
                {"keywords": ["早上好", "下午好", "晚上好", "你好", "您好"], "weight": 1.0},
            ],
            IntentCategory.FAREWELL: [
                {"keywords": ["bye", "goodbye", "see you", "talk later", "farewell"], "weight": 1.0},
                {"keywords": ["再见", "拜拜", "回头见", "下次聊"], "weight": 1.0},
            ],
            IntentCategory.AFFIRMATION: [
                {"keywords": ["yes", "yeah", "sure", "okay", "ok", "correct", "right"], "weight": 1.0},
                {"keywords": ["是的", "对的", "正确", "好的", "没问题"], "weight": 1.0},
            ],
            IntentCategory.NEGATION: [
                {"keywords": ["no", "nope", "not", "don't", "doesn't", "isn't", "wrong"], "weight": 1.0},
                {"keywords": ["不", "不是", "不对", "没有", "不行"], "weight": 1.0},
            ],
            
            # Information Seeking
            IntentCategory.QUESTION: [
                {"keywords": ["what", "how", "why", "when", "where", "who", "which"], "weight": 0.8},
                {"keywords": ["什么", "怎么", "为什么", "何时", "哪里", "谁", "哪个"], "weight": 0.8},
                {"keywords": ["?", "？"], "weight": 0.5},
            ],
            IntentCategory.CLARIFICATION: [
                {"keywords": ["what do you mean", "clarify", "explain more", "don't understand"], "weight": 0.9},
                {"keywords": ["什么意思", "解释一下", "不明白", "不清楚"], "weight": 0.9},
            ],
            IntentCategory.HELP_REQUEST: [
                {"keywords": ["help", "assist", "support", "guide", "how to"], "weight": 0.9},
                {"keywords": ["帮助", "协助", "支持", "指导", "怎么"], "weight": 0.9},
            ],
            
            # Wiki-specific
            IntentCategory.WIKI_CREATE: [
                {"keywords": ["create wiki", "new wiki", "add wiki", "make wiki"], "weight": 0.9},
                {"keywords": ["创建wiki", "新建wiki", "添加wiki", "制作wiki"], "weight": 0.9},
                {"keywords": ["create entry", "new entry", "add entry"], "weight": 0.8},
                {"keywords": ["创建词条", "新建词条", "添加词条"], "weight": 0.8},
            ],
            IntentCategory.WIKI_VIEW: [
                {"keywords": ["view wiki", "show wiki", "display wiki", "read wiki"], "weight": 0.9},
                {"keywords": ["查看wiki", "显示wiki", "阅读wiki"], "weight": 0.9},
                {"keywords": ["view entry", "show entry", "open entry"], "weight": 0.8},
                {"keywords": ["查看词条", "显示词条", "打开词条"], "weight": 0.8},
            ],
            IntentCategory.WIKI_EDIT: [
                {"keywords": ["edit wiki", "modify wiki", "update wiki", "change wiki"], "weight": 0.9},
                {"keywords": ["编辑wiki", "修改wiki", "更新wiki", "更改wiki"], "weight": 0.9},
                {"keywords": ["edit entry", "modify entry"], "weight": 0.8},
                {"keywords": ["编辑词条", "修改词条"], "weight": 0.8},
            ],
            IntentCategory.WIKI_DELETE: [
                {"keywords": ["delete wiki", "remove wiki", "delete entry"], "weight": 0.9},
                {"keywords": ["删除wiki", "移除wiki", "删除词条"], "weight": 0.9},
            ],
            IntentCategory.WIKI_SEARCH: [
                {"keywords": ["search wiki", "find wiki", "lookup wiki"], "weight": 0.9},
                {"keywords": ["搜索wiki", "查找wiki", "搜索词条"], "weight": 0.9},
            ],
            IntentCategory.WIKI_COLLABORATE: [
                {"keywords": ["collaborate on wiki", "wiki collaboration", "cooperative wiki"], "weight": 0.9},
                {"keywords": ["wiki协作", "协作wiki", "共同编辑"], "weight": 0.9},
            ],
            
            # Chat-specific
            IntentCategory.CHAT_START: [
                {"keywords": ["start chat", "new chat", "begin chat", "create chat"], "weight": 0.9},
                {"keywords": ["开始聊天", "新建聊天", "创建聊天室"], "weight": 0.9},
            ],
            IntentCategory.CHAT_MESSAGE: [
                {"keywords": ["send message", "post message", "chat message"], "weight": 0.9},
                {"keywords": ["发送消息", "发送信息", "聊天消息"], "weight": 0.9},
            ],
            IntentCategory.CHAT_HISTORY: [
                {"keywords": ["chat history", "message history", "conversation history"], "weight": 0.9},
                {"keywords": ["聊天历史", "消息历史", "对话记录"], "weight": 0.9},
            ],
            IntentCategory.CHAT_CLEAR: [
                {"keywords": ["clear chat", "clear history", "clear messages"], "weight": 0.9},
                {"keywords": ["清除聊天", "清空历史", "清除消息"], "weight": 0.9},
            ],
            IntentCategory.CHAT_CLOSE: [
                {"keywords": ["close chat", "end chat", "finish chat"], "weight": 0.9},
                {"keywords": ["关闭聊天", "结束聊天", "完成聊天"], "weight": 0.9},
            ],
            IntentCategory.CHAT_DELETE: [
                {"keywords": ["delete chat", "remove chat", "delete room"], "weight": 0.9},
                {"keywords": ["删除聊天", "移除聊天", "删除聊天室"], "weight": 0.9},
            ],
            
            # Role management
            IntentCategory.ROLE_MATCH: [
                {"keywords": ["match roles", "find roles", "role matching"], "weight": 0.9},
                {"keywords": ["匹配角色", "查找角色", "角色匹配"], "weight": 0.9},
            ],
            IntentCategory.ROLE_LIST: [
                {"keywords": ["list roles", "show roles", "display roles"], "weight": 0.9},
                {"keywords": ["列出角色", "显示角色", "展示角色"], "weight": 0.9},
            ],
            IntentCategory.ROLE_STATS: [
                {"keywords": ["role stats", "role statistics", "role analysis"], "weight": 0.9},
                {"keywords": ["角色统计", "角色分析", "角色数据"], "weight": 0.9},
            ],
            
            # Content generation
            IntentCategory.CONTENT_GENERATE: [
                {"keywords": ["generate content", "create content", "content generation"], "weight": 0.9},
                {"keywords": ["生成内容", "创建内容", "内容生成"], "weight": 0.9},
            ],
            IntentCategory.DEBATE_START: [
                {"keywords": ["start debate", "begin debate", "create debate"], "weight": 0.9},
                {"keywords": ["开始辩论", "发起辩论", "创建辩论"], "weight": 0.9},
            ],
            
            # System commands
            IntentCategory.SYSTEM_STATUS: [
                {"keywords": ["system status", "status check", "system info"], "weight": 0.9},
                {"keywords": ["系统状态", "状态检查", "系统信息"], "weight": 0.9},
            ],
            IntentCategory.CONFIGURE: [
                {"keywords": ["configure", "configuration", "settings", "setup"], "weight": 0.9},
                {"keywords": ["配置", "设置", "设定", "安装"], "weight": 0.9},
            ],
        }
        
        return patterns
    
    def _build_entity_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build entity extraction patterns"""
        
        patterns = {
            "wiki_entry": [
                {"patterns": [r'\b[A-Z][a-zA-Z\s]+\b', r'\b[\u4e00-\u9fff]+\b'], "label": "wiki_entry"},
            ],
            "chat_room": [
                {"patterns": [r'room\s+[A-Za-z0-9_]+', r'聊天室\s*[\u4e00-\u9fff]+'], "label": "chat_room"},
            ],
            "role_name": [
                {"patterns": [r'role\s+[A-Za-z0-9_]+', r'角色\s*[\u4e00-\u9fff]+'], "label": "role_name"},
            ],
            "file_path": [
                {"patterns": [r'[A-Za-z]:\\[^\\]+\\*[^\\]*', r'/[^/\s]+/\*[^/\s]*'], "label": "file_path"},
            ],
            "url": [
                {"patterns": [r'https?://[^\s]+', r'www\.[^\s]+'], "label": "url"},
            ],
            "number": [
                {"patterns": [r'\b\d+\b'], "label": "number"},
            ],
        }
        
        return patterns
    
    def match_intent(self, user_input: str) -> Dict[IntentCategory, float]:
        """Match intents using keyword patterns with confidence scoring"""
        
        input_lower = user_input.lower()
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            total_score = 0.0
            total_weight = 0.0
            
            for pattern in patterns:
                keywords = pattern["keywords"]
                weight = pattern["weight"]
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in input_lower)
                if matches > 0:
                    # Calculate score based on matches and weight
                    pattern_score = min(matches / len(keywords), 1.0) * weight
                    total_score += pattern_score
                    total_weight += weight
            
            # Normalize score
            if total_weight > 0:
                normalized_score = total_score / total_weight
                scores[intent] = normalized_score
        
        return scores
    
    def extract_entities(self, user_input: str) -> List[Entity]:
        """Extract entities from user input using patterns"""
        
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern_config in patterns:
                for pattern in pattern_config["patterns"]:
                    try:
                        matches = re.finditer(pattern, user_input)
                        for match in matches:
                            entity = Entity(
                                text=match.group(),
                                label=entity_type,
                                start_pos=match.start(),
                                end_pos=match.end(),
                                confidence=0.8,  # Default confidence for regex matches
                                metadata={"pattern": pattern}
                            )
                            entities.append(entity)
                    except re.error:
                        continue
        
        return entities


class EnhancedIntentRecognizer(IntentRecognizerInterface):
    """Enhanced intent recognizer with comprehensive taxonomy and multi-modal detection"""
    
    def __init__(self):
        self.keyword_matcher = KeywordIntentMatcher()
        self.intent_taxonomy = self._build_intent_taxonomy()
        
    def _build_intent_taxonomy(self) -> Dict[str, List[IntentCategory]]:
        """Build hierarchical intent taxonomy"""
        
        taxonomy = {
            "basic_communication": [
                IntentCategory.GREETING,
                IntentCategory.FAREWELL,
                IntentCategory.AFFIRMATION,
                IntentCategory.NEGATION,
                IntentCategory.APOLOGY,
                IntentCategory.THANKS,
            ],
            "information_seeking": [
                IntentCategory.QUESTION,
                IntentCategory.CLARIFICATION,
                IntentCategory.DEFINITION,
                IntentCategory.EXPLANATION,
                IntentCategory.EXAMPLE,
                IntentCategory.COMPARISON,
                IntentCategory.STATUS_INQUIRY,
                IntentCategory.HELP_REQUEST,
            ],
            "task_oriented": [
                IntentCategory.REQUEST,
                IntentCategory.COMMAND,
                IntentCategory.CREATION,
                IntentCategory.MODIFICATION,
                IntentCategory.DELETION,
                IntentCategory.CONFIGURATION,
                IntentCategory.ANALYSIS,
                IntentCategory.GENERATION,
                IntentCategory.OPTIMIZATION,
            ],
            "wiki_management": [
                IntentCategory.WIKI_CREATE,
                IntentCategory.WIKI_VIEW,
                IntentCategory.WIKI_EDIT,
                IntentCategory.WIKI_DELETE,
                IntentCategory.WIKI_SEARCH,
                IntentCategory.WIKI_LIST,
                IntentCategory.WIKI_EXPORT,
                IntentCategory.WIKI_COLLABORATE,
                IntentCategory.WIKI_PROPOSAL_APPROVE,
                IntentCategory.WIKI_PROPOSAL_REJECT,
                IntentCategory.WIKI_PROPOSAL_LIST,
            ],
            "chat_management": [
                IntentCategory.CHAT_START,
                IntentCategory.CHAT_MESSAGE,
                IntentCategory.CHAT_HISTORY,
                IntentCategory.CHAT_CLEAR,
                IntentCategory.CHAT_CLOSE,
                IntentCategory.CHAT_DELETE,
                IntentCategory.CHAT_LIST,
                IntentCategory.CHAT_INVITE,
            ],
            "role_management": [
                IntentCategory.ROLE_MATCH,
                IntentCategory.ROLE_LIST,
                IntentCategory.ROLE_STATS,
                IntentCategory.ROLE_INVITE,
            ],
            "collaboration": [
                IntentCategory.DEBATE_START,
                IntentCategory.DEBATE_JOIN,
                IntentCategory.DEBATE_MODERATE,
                IntentCategory.CONTENT_GENERATE,
                IntentCategory.COLLABORATE,
                IntentCategory.FEEDBACK_PROVIDE,
                IntentCategory.CONSENSUS_SEEK,
            ],
            "system_management": [
                IntentCategory.SYSTEM_STATUS,
                IntentCategory.ERROR_REPORT,
                IntentCategory.CONFIGURE,
                IntentCategory.RESET,
                IntentCategory.BACKUP,
                IntentCategory.RESTORE,
            ],
            "advanced": [
                IntentCategory.INTENT_CORRECTION,
                IntentCategory.TASK_DELEGATION,
                IntentCategory.WORKFLOW_AUTOMATION,
                IntentCategory.PERSONALIZATION_REQUEST,
            ],
        }
        
        return taxonomy
    
    async def recognize_intent(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> EnhancedIntentAnalysis:
        """Recognize primary intent from user input"""
        
        import time
        start_time = time.time()
        
        # Get keyword-based scores
        keyword_scores = self.keyword_matcher.match_intent(user_input)
        
        # Extract entities
        entities = self.keyword_matcher.extract_entities(user_input)
        
        # Determine primary intent
        if keyword_scores:
            primary_intent = max(keyword_scores.items(), key=lambda x: x[1])
            intent_category, confidence = primary_intent
        else:
            intent_category = IntentCategory.QUESTION  # Default fallback
            confidence = 0.3
        
        # Get secondary intents
        secondary_intents = [
            (intent, score) for intent, score in keyword_scores.items()
            if intent != intent_category and score > 0.3
        ]
        secondary_intents.sort(key=lambda x: x[1], reverse=True)
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(confidence)
        
        # Generate context requirements and suggested actions
        context_requirements = self._get_context_requirements(intent_category, entities)
        suggested_actions = self._get_suggested_actions(intent_category, entities)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create analysis result
        analysis = EnhancedIntentAnalysis(
            user_input=user_input,
            primary_intent=intent_category,
            confidence=confidence,
            confidence_level=confidence_level,
            secondary_intents=secondary_intents[:3],  # Top 3 secondary intents
            entities=entities,
            context_requirements=context_requirements,
            suggested_actions=suggested_actions,
            detection_sources=[IntentSource.KEYWORD_MATCH],
            processing_time_ms=processing_time,
            user_id=context.get("user_id"),
            metadata={
                "keyword_scores": keyword_scores,
                "input_length": len(user_input),
                "entity_count": len(entities)
            }
        )
        
        logger.info(f"Intent recognized: {intent_category.value} with confidence {confidence:.2f}")
        return analysis
    
    async def recognize_multiple_intents(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> List[EnhancedIntentAnalysis]:
        """Recognize multiple intents in a single utterance"""
        
        # For now, return single intent analysis
        # TODO: Implement proper multi-intent segmentation
        analysis = await self.recognize_intent(user_input, context)
        return [analysis]
    
    def get_intent_taxonomy(self) -> Dict[str, List[str]]:
        """Get the complete intent taxonomy"""
        return {
            category: [intent.value for intent in intents]
            for category, intents in self.intent_taxonomy.items()
        }
    
    def get_intent_confidence(
        self, 
        intent: IntentCategory, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> float:
        """Get confidence score for specific intent"""
        
        scores = self.keyword_matcher.match_intent(user_input)
        return scores.get(intent, 0.0)
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to confidence level"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _get_context_requirements(
        self, 
        intent: IntentCategory, 
        entities: List[Entity]
    ) -> List[str]:
        """Get context requirements for intent"""
        
        requirements = {
            IntentCategory.WIKI_CREATE: ["wiki_entry_name", "content_type"],
            IntentCategory.WIKI_EDIT: ["wiki_entry_name", "edit_content"],
            IntentCategory.CHAT_START: ["chat_room_name", "topic"],
            IntentCategory.ROLE_MATCH: ["task_description", "task_type"],
            IntentCategory.CONTENT_GENERATE: ["topic", "content_type", "audience"],
        }
        
        return requirements.get(intent, [])
    
    def _get_suggested_actions(
        self, 
        intent: IntentCategory, 
        entities: List[Entity]
    ) -> List[str]:
        """Get suggested actions for intent"""
        
        actions = {
            IntentCategory.WIKI_CREATE: ["Create new wiki entry", "Request content suggestions"],
            IntentCategory.WIKI_VIEW: ["Display wiki content", "Show entry metadata"],
            IntentCategory.WIKI_EDIT: ["Open edit interface", "Show edit history"],
            IntentCategory.CHAT_START: ["Create chat room", "Suggest participants"],
            IntentCategory.ROLE_MATCH: ["Find matching roles", "Show role statistics"],
            IntentCategory.CONTENT_GENERATE: ["Generate content", "Optimize for audience"],
        }
        
        return actions.get(intent, [])


# Factory function for creating intent recognizer
def create_enhanced_intent_recognizer() -> EnhancedIntentRecognizer:
    """Create an enhanced intent recognizer instance"""
    return EnhancedIntentRecognizer()