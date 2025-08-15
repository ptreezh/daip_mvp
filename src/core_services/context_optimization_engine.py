#!/usr/bin/env python3
"""上下文优化引擎

基于多面嵌入技术的自动上下文优化系统
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ContextElement:
    """上下文元素"""
    element_id: str
    content: str
    element_type: str  # "history", "task", "environment", "role", "knowledge"
    relevance_score: float
    confidence_score: float
    source: str
    timestamp: datetime
    embedding: Optional[np.ndarray] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ContextOptimizationRequest:
    """上下文优化请求"""
    user_id: str
    current_query: str
    conversation_history: list[dict[str, Any]]
    current_task: Optional[str] = None
    available_context: dict[str, Any] = None
    optimization_strategy: str = "adaptive"

    def __post_init__(self):
        if self.available_context is None:
            self.available_context = {}


@dataclass
class OptimizedContext:
    """优化后的上下文"""
    optimized_prompt: str
    context_elements: list[ContextElement]
    relevance_scores: dict[str, float]
    optimization_reasoning: str
    confidence_score: float
    original_context_size: int
    optimized_context_size: int
    optimization_metrics: dict[str, Any] = None

    def __post_init__(self):
        if self.optimization_metrics is None:
            self.optimization_metrics = {}


class MultiAspectEmbeddingModel:
    """多面嵌入模型"""
    
    def __init__(self):
        """初始化多面嵌入模型"""
        self.embedding_dim = 384  # 简化的嵌入维度
        self.pattern_keywords = {
            "question": ["什么", "如何", "为什么", "怎样", "请问", "?", "？"],
            "analysis": ["分析", "评估", "研究", "探讨", "考虑"],
            "decision": ["决定", "选择", "判断", "建议", "推荐"],
            "explanation": ["解释", "说明", "阐述", "描述", "介绍"],
            "comparison": ["比较", "对比", "区别", "差异", "优缺点"]
        }
        
        self.goal_keywords = {
            "understanding": ["理解", "了解", "掌握", "学习", "知道"],
            "problem_solving": ["解决", "处理", "应对", "克服", "改善"],
            "decision_making": ["决策", "选择", "判断", "确定", "决定"],
            "creation": ["创建", "制作", "设计", "开发", "构建"],
            "evaluation": ["评价", "评估", "审查", "检查", "验证"]
        }
        
        logger.info("多面嵌入模型初始化完成")
    
    def encode_pattern(self, text: str) -> np.ndarray:
        """编码问题模式"""
        pattern_vector = np.zeros(self.embedding_dim)
        
        # 基于关键词匹配计算模式向量
        for i, (pattern_type, keywords) in enumerate(self.pattern_keywords.items()):
            score = sum(1 for keyword in keywords if keyword in text.lower())
            if score > 0:
                # 在向量的不同位置编码不同模式
                start_idx = i * (self.embedding_dim // len(self.pattern_keywords))
                end_idx = start_idx + (self.embedding_dim // len(self.pattern_keywords))
                pattern_vector[start_idx:end_idx] = score / len(keywords)
        
        # 归一化
        norm = np.linalg.norm(pattern_vector)
        if norm > 0:
            pattern_vector = pattern_vector / norm
        
        return pattern_vector
    
    def encode_goal(self, text: str) -> np.ndarray:
        """编码目标"""
        goal_vector = np.zeros(self.embedding_dim)
        
        # 基于关键词匹配计算目标向量
        for i, (goal_type, keywords) in enumerate(self.goal_keywords.items()):
            score = sum(1 for keyword in keywords if keyword in text.lower())
            if score > 0:
                # 在向量的不同位置编码不同目标
                start_idx = i * (self.embedding_dim // len(self.goal_keywords))
                end_idx = start_idx + (self.embedding_dim // len(self.goal_keywords))
                goal_vector[start_idx:end_idx] = score / len(keywords)
        
        # 归一化
        norm = np.linalg.norm(goal_vector)
        if norm > 0:
            goal_vector = goal_vector / norm
        
        return goal_vector
    
    def encode_solution(self, text: str) -> np.ndarray:
        """编码解决方案步骤"""
        # 简化实现：基于文本长度和结构特征
        solution_vector = np.random.normal(0, 0.1, self.embedding_dim)
        
        # 基于文本特征调整向量
        text_length = len(text)
        sentence_count = len(re.split(r'[。！？.!?]', text))
        
        # 长度特征
        solution_vector[:50] *= (text_length / 1000)
        
        # 结构特征
        solution_vector[50:100] *= (sentence_count / 10)
        
        # 归一化
        norm = np.linalg.norm(solution_vector)
        if norm > 0:
            solution_vector = solution_vector / norm
        
        return solution_vector
    
    def encode_context(self, context_info: dict[str, Any]) -> np.ndarray:
        """编码上下文"""
        context_vector = np.zeros(self.embedding_dim)
        
        # 基于上下文信息的不同维度编码
        if "user_profile" in context_info:
            context_vector[:100] = np.random.normal(0, 0.1, 100)
        
        if "task_type" in context_info:
            context_vector[100:200] = np.random.normal(0, 0.1, 100)
        
        if "environment" in context_info:
            context_vector[200:300] = np.random.normal(0, 0.1, 100)
        
        # 归一化
        norm = np.linalg.norm(context_vector)
        if norm > 0:
            context_vector = context_vector / norm
        
        return context_vector
    
    def encode_multi_aspect(
        self, 
        text: str, 
        context_info: dict[str, Any] = None
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """多面嵌入编码"""
        if context_info is None:
            context_info = {}
        
        pattern_embedding = self.encode_pattern(text)
        goal_embedding = self.encode_goal(text)
        solution_embedding = self.encode_solution(text)
        context_embedding = self.encode_context(context_info)
        
        return pattern_embedding, goal_embedding, solution_embedding, context_embedding

class ConversationHistoryAnalyzer:
    """对话历史分析器"""
    
    def __init__(self):
        """初始化对话历史分析器"""
        self.embedding_model = MultiAspectEmbeddingModel()
        logger.info("对话历史分析器初始化完成")
    
    async def analyze(self, conversation_history: list[dict[str, Any]]) -> dict[str, Any]:
        """分析对话历史"""
        try:
            if not conversation_history:
                return {"patterns": {}, "preferences": {}, "success_indicators": {}}
            
            # 分析对话模式
            patterns = self._analyze_conversation_patterns(conversation_history)
            
            # 分析用户偏好
            preferences = self._analyze_user_preferences(conversation_history)
            
            # 分析成功指标
            success_indicators = self._analyze_success_indicators(conversation_history)
            
            # 提取关键主题
            key_topics = self._extract_key_topics(conversation_history)
            
            # 分析时间模式
            time_patterns = self._analyze_time_patterns(conversation_history)
            
            analysis_result = {
                "patterns": patterns,
                "preferences": preferences,
                "success_indicators": success_indicators,
                "key_topics": key_topics,
                "time_patterns": time_patterns,
                "total_conversations": len(conversation_history),
                "analysis_confidence": self._calculate_analysis_confidence(conversation_history)
            }
            
            logger.info(f"对话历史分析完成: {len(conversation_history)}条记录")
            return analysis_result
            
        except Exception as e:
            logger.error(f"对话历史分析失败: {e}")
            return {"error": str(e)}
    
    def _analyze_conversation_patterns(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        """分析对话模式"""
        patterns = {
            "question_types": defaultdict(int),
            "response_lengths": [],
            "interaction_frequency": defaultdict(int),
            "topic_transitions": []
        }
        
        for i, turn in enumerate(history):
            content = turn.get("content", "")
            turn_type = turn.get("type", "unknown")
            
            # 分析问题类型
            if "?" in content or "？" in content:
                patterns["question_types"]["question"] += 1
            elif any(word in content for word in ["分析", "评估", "研究"]):
                patterns["question_types"]["analysis"] += 1
            elif any(word in content for word in ["建议", "推荐", "选择"]):
                patterns["question_types"]["recommendation"] += 1
            
            # 记录回应长度
            patterns["response_lengths"].append(len(content))
            
            # 记录交互频率
            patterns["interaction_frequency"][turn_type] += 1
            
            # 分析主题转换
            if i > 0:
                prev_content = history[i-1].get("content", "")
                similarity = self._calculate_content_similarity(prev_content, content)
                patterns["topic_transitions"].append(similarity)
        
        return dict(patterns)
    
    def _analyze_user_preferences(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        """分析用户偏好"""
        preferences = {
            "preferred_response_style": "balanced",
            "detail_level": "medium",
            "interaction_style": "collaborative",
            "topic_interests": defaultdict(float)
        }
        
        # 分析回应风格偏好
        formal_indicators = 0
        casual_indicators = 0
        
        for turn in history:
            content = turn.get("content", "")
            
            # 正式性指标
            if any(word in content for word in ["请", "您", "敬请", "恳请"]):
                formal_indicators += 1
            
            # 随意性指标
            if any(word in content for word in ["嗯", "哦", "好的", "OK"]):
                casual_indicators += 1
            
            # 主题兴趣分析
            for topic in ["技术", "商业", "伦理", "创新", "分析"]:
                if topic in content:
                    preferences["topic_interests"][topic] += 1
        
        # 确定偏好风格
        if formal_indicators > casual_indicators * 1.5:
            preferences["preferred_response_style"] = "formal"
        elif casual_indicators > formal_indicators * 1.5:
            preferences["preferred_response_style"] = "casual"
        
        return dict(preferences)
    
    def _analyze_success_indicators(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        """分析成功指标"""
        success_indicators = {
            "satisfaction_signals": 0,
            "follow_up_questions": 0,
            "positive_feedback": 0,
            "task_completion_rate": 0.0
        }
        
        positive_words = ["好", "谢谢", "有用", "清楚", "明白", "满意"]
        question_indicators = ["?", "？", "如何", "为什么", "怎样"]
        
        for turn in history:
            content = turn.get("content", "")
            
            # 满意度信号
            if any(word in content for word in positive_words):
                success_indicators["satisfaction_signals"] += 1
            
            # 后续问题
            if any(indicator in content for indicator in question_indicators):
                success_indicators["follow_up_questions"] += 1
            
            # 正面反馈
            if any(word in content for word in ["好", "谢谢", "有帮助"]):
                success_indicators["positive_feedback"] += 1
        
        # 计算任务完成率（简化）
        if len(history) > 0:
            success_indicators["task_completion_rate"] = (
                success_indicators["satisfaction_signals"] / len(history)
            )
        
        return success_indicators
    
    def _extract_key_topics(self, history: list[dict[str, Any]]) -> list[str]:
        """提取关键主题"""
        topic_counts = defaultdict(int)
        
        # 预定义主题关键词
        topic_keywords = {
            "AI伦理": ["伦理", "道德", "责任", "公平", "透明"],
            "技术实现": ["算法", "模型", "实现", "技术", "开发"],
            "商业策略": ["商业", "策略", "市场", "竞争", "盈利"],
            "用户体验": ["用户", "体验", "界面", "交互", "设计"],
            "数据分析": ["数据", "分析", "统计", "指标", "报告"]
        }
        
        for turn in history:
            content = turn.get("content", "").lower()
            
            for topic, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content)
                if score > 0:
                    topic_counts[topic] += score
        
        # 返回按频率排序的主题
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:5]]
    
    def _analyze_time_patterns(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        """分析时间模式"""
        time_patterns = {
            "session_duration": 0.0,
            "response_intervals": [],
            "active_hours": defaultdict(int),
            "conversation_frequency": "unknown"
        }
        
        timestamps = []
        for turn in history:
            timestamp_str = turn.get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(timestamp)
                    
                    # 记录活跃时间
                    time_patterns["active_hours"][timestamp.hour] += 1
                except:
                    continue
        
        if len(timestamps) >= 2:
            # 计算会话持续时间
            time_patterns["session_duration"] = (
                timestamps[-1] - timestamps[0]
            ).total_seconds() / 60  # 分钟
            
            # 计算回应间隔
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                time_patterns["response_intervals"].append(interval)
        
        return dict(time_patterns)
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度"""
        # 简化的相似度计算
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_analysis_confidence(self, history: list[dict[str, Any]]) -> float:
        """计算分析置信度"""
        if not history:
            return 0.0
        
        # 基于对话数量和质量计算置信度
        conversation_count = len(history)
        
        # 数量因子
        count_factor = min(conversation_count / 20, 1.0)  # 20条对话为满分
        
        # 质量因子（基于内容长度）
        avg_length = sum(len(turn.get("content", "")) for turn in history) / len(history)
        quality_factor = min(avg_length / 100, 1.0)  # 100字符为满分
        
        return (count_factor + quality_factor) / 2


class TaskAnalyzer:
    """任务分析器"""
    
    def __init__(self):
        """初始化任务分析器"""
        self.task_types = {
            "analysis": ["分析", "研究", "探讨", "调查", "评估"],
            "decision": ["决定", "选择", "判断", "决策", "确定"],
            "creation": ["创建", "制作", "设计", "开发", "构建"],
            "explanation": ["解释", "说明", "阐述", "介绍", "描述"],
            "comparison": ["比较", "对比", "区别", "差异", "优劣"]
        }
        
        logger.info("任务分析器初始化完成")
    
    async def analyze(self, current_query: str, current_task: Optional[str] = None) -> dict[str, Any]:
        """分析当前任务"""
        try:
            # 识别任务类型
            task_type = self._identify_task_type(current_query)
            
            # 分析任务复杂度
            complexity = self._analyze_task_complexity(current_query)
            
            # 提取任务关键词
            keywords = self._extract_task_keywords(current_query)
            
            # 分析所需资源
            required_resources = self._analyze_required_resources(current_query, task_type)
            
            # 估算处理时间
            estimated_time = self._estimate_processing_time(complexity, task_type)
            
            analysis_result = {
                "task_type": task_type,
                "complexity": complexity,
                "keywords": keywords,
                "required_resources": required_resources,
                "estimated_time": estimated_time,
                "current_task": current_task,
                "analysis_confidence": self._calculate_task_confidence(current_query)
            }
            
            logger.info(f"任务分析完成: 类型={task_type}, 复杂度={complexity}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"任务分析失败: {e}")
            return {"error": str(e)}
    
    def _identify_task_type(self, query: str) -> str:
        """识别任务类型"""
        query_lower = query.lower()
        
        type_scores = {}
        for task_type, keywords in self.task_types.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                type_scores[task_type] = score
        
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        else:
            return "general"
    
    def _analyze_task_complexity(self, query: str) -> str:
        """分析任务复杂度"""
        # 基于查询长度和关键词复杂度
        query_length = len(query)
        
        complex_indicators = [
            "多角度", "综合", "深入", "全面", "系统", "详细",
            "比较", "对比", "分析", "评估", "研究"
        ]
        
        complexity_score = sum(1 for indicator in complex_indicators if indicator in query)
        
        if query_length > 200 or complexity_score >= 3:
            return "high"
        elif query_length > 100 or complexity_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _extract_task_keywords(self, query: str) -> list[str]:
        """提取任务关键词"""
        # 简化的关键词提取
        important_words = []
        
        # 预定义重要词汇
        important_patterns = [
            r"AI\w*", r"人工智能", r"机器学习", r"深度学习",
            r"算法", r"模型", r"数据", r"分析", r"系统",
            r"伦理", r"安全", r"隐私", r"透明", r"公平"
        ]
        
        for pattern in important_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            important_words.extend(matches)
        
        return list(set(important_words))[:10]  # 返回前10个关键词
    
    def _analyze_required_resources(self, query: str, task_type: str) -> dict[str, Any]:
        """分析所需资源"""
        resources = {
            "roles": [],
            "knowledge_domains": [],
            "tools": [],
            "time_estimate": "medium"
        }
        
        # 基于任务类型确定所需角色
        role_mapping = {
            "analysis": ["分析师", "研究员"],
            "decision": ["决策专家", "顾问"],
            "creation": ["设计师", "开发者"],
            "explanation": ["教育专家", "沟通专家"],
            "comparison": ["评估专家", "比较分析师"]
        }
        
        resources["roles"] = role_mapping.get(task_type, ["通用专家"])
        
        # 基于关键词确定知识领域
        if any(word in query for word in ["AI", "人工智能", "算法"]):
            resources["knowledge_domains"].append("人工智能")
        if any(word in query for word in ["伦理", "道德", "责任"]):
            resources["knowledge_domains"].append("伦理学")
        if any(word in query for word in ["商业", "市场", "策略"]):
            resources["knowledge_domains"].append("商业策略")
        
        return resources
    
    def _estimate_processing_time(self, complexity: str, task_type: str) -> int:
        """估算处理时间（秒）"""
        base_times = {
            "analysis": 30,
            "decision": 25,
            "creation": 45,
            "explanation": 20,
            "comparison": 35,
            "general": 15
        }
        
        complexity_multipliers = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.5
        }
        
        base_time = base_times.get(task_type, 20)
        multiplier = complexity_multipliers.get(complexity, 1.0)
        
        return int(base_time * multiplier)
    
    def _calculate_task_confidence(self, query: str) -> float:
        """计算任务分析置信度"""
        # 基于查询清晰度和完整性
        clarity_indicators = ["具体", "明确", "详细", "清楚"]
        completeness_indicators = ["目标", "要求", "期望", "结果"]
        
        clarity_score = sum(1 for indicator in clarity_indicators if indicator in query)
        completeness_score = sum(1 for indicator in completeness_indicators if indicator in query)
        
        # 基于长度的置信度
        length_confidence = min(len(query) / 50, 1.0)
        
        # 综合置信度
        total_confidence = (
            clarity_score * 0.3 +
            completeness_score * 0.3 +
            length_confidence * 0.4
        )
        
        return min(total_confidence, 1.0)


class ContextAggregator:
    """上下文聚合器"""
    
    def __init__(self):
        """初始化上下文聚合器"""
        logger.info("上下文聚合器初始化完成")
    
    async def aggregate(
        self,
        available_context: dict[str, Any],
        history_insights: dict[str, Any],
        task_insights: dict[str, Any]
    ) -> list[ContextElement]:
        """聚合上下文信息"""
        try:
            context_elements = []
            
            # 处理历史上下文
            history_elements = self._process_history_context(history_insights)
            context_elements.extend(history_elements)
            
            # 处理任务上下文
            task_elements = self._process_task_context(task_insights)
            context_elements.extend(task_elements)
            
            # 处理环境上下文
            env_elements = self._process_environment_context(available_context)
            context_elements.extend(env_elements)
            
            # 处理知识上下文
            knowledge_elements = self._process_knowledge_context(available_context)
            context_elements.extend(knowledge_elements)
            
            # 排序和过滤
            filtered_elements = self._filter_and_rank_elements(context_elements)
            
            logger.info(f"上下文聚合完成: {len(filtered_elements)}个元素")
            return filtered_elements
            
        except Exception as e:
            logger.error(f"上下文聚合失败: {e}")
            return []
    
    def _process_history_context(self, history_insights: dict[str, Any]) -> list[ContextElement]:
        """处理历史上下文"""
        elements = []
        
        # 处理关键主题
        key_topics = history_insights.get("key_topics", [])
        for i, topic in enumerate(key_topics[:3]):  # 取前3个主题
            element = ContextElement(
                element_id=f"history_topic_{i}",
                content=f"用户历史关注主题: {topic}",
                element_type="history",
                relevance_score=0.8 - i * 0.1,  # 递减相关性
                confidence_score=0.9,
                source="conversation_history",
                timestamp=datetime.now(),
                metadata={"topic": topic, "rank": i}
            )
            elements.append(element)
        
        # 处理用户偏好
        preferences = history_insights.get("preferences", {})
        if preferences:
            preferred_style = preferences.get("preferred_response_style", "balanced")
            element = ContextElement(
                element_id="history_preference_style",
                content=f"用户偏好回应风格: {preferred_style}",
                element_type="history",
                relevance_score=0.7,
                confidence_score=0.8,
                source="conversation_history",
                timestamp=datetime.now(),
                metadata={"preference_type": "response_style", "value": preferred_style}
            )
            elements.append(element)
        
        return elements
    
    def _process_task_context(self, task_insights: dict[str, Any]) -> list[ContextElement]:
        """处理任务上下文"""
        elements = []
        
        # 任务类型
        task_type = task_insights.get("task_type", "general")
        element = ContextElement(
            element_id="task_type",
            content=f"当前任务类型: {task_type}",
            element_type="task",
            relevance_score=0.9,
            confidence_score=task_insights.get("analysis_confidence", 0.8),
            source="task_analysis",
            timestamp=datetime.now(),
            metadata={"task_type": task_type}
        )
        elements.append(element)
        
        # 任务复杂度
        complexity = task_insights.get("complexity", "medium")
        element = ContextElement(
            element_id="task_complexity",
            content=f"任务复杂度: {complexity}",
            element_type="task",
            relevance_score=0.8,
            confidence_score=0.9,
            source="task_analysis",
            timestamp=datetime.now(),
            metadata={"complexity": complexity}
        )
        elements.append(element)
        
        return elements
    
    def _process_environment_context(self, available_context: dict[str, Any]) -> list[ContextElement]:
        """处理环境上下文"""
        elements = []
        
        # 时间上下文
        current_time = datetime.now()
        element = ContextElement(
            element_id="env_time_context",
            content=f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
            element_type="environment",
            relevance_score=0.4,
            confidence_score=1.0,
            source="system_time",
            timestamp=current_time,
            metadata={"timestamp": current_time.isoformat()}
        )
        elements.append(element)
        
        return elements
    
    def _process_knowledge_context(self, available_context: dict[str, Any]) -> list[ContextElement]:
        """处理知识上下文"""
        elements = []
        
        # 相关知识
        relevant_knowledge = available_context.get("relevant_knowledge", [])
        for i, knowledge in enumerate(relevant_knowledge[:3]):  # 取前3个知识点
            element = ContextElement(
                element_id=f"knowledge_{i}",
                content=f"相关知识: {knowledge}",
                element_type="knowledge",
                relevance_score=0.7 - i * 0.1,
                confidence_score=0.8,
                source="knowledge_base",
                timestamp=datetime.now(),
                metadata={"knowledge_item": knowledge, "rank": i}
            )
            elements.append(element)
        
        return elements
    
    def _filter_and_rank_elements(self, elements: list[ContextElement]) -> list[ContextElement]:
        """过滤和排序上下文元素"""
        # 按相关性分数排序
        sorted_elements = sorted(elements, key=lambda x: x.relevance_score, reverse=True)
        
        # 过滤低相关性元素
        filtered_elements = [elem for elem in sorted_elements if elem.relevance_score >= 0.3]
        
        # 限制数量（避免上下文过长）
        return filtered_elements[:20]


class ContextOptimizationEngine:
    """上下文优化引擎"""
    
    def __init__(self):
        """初始化上下文优化引擎"""
        self.history_analyzer = ConversationHistoryAnalyzer()
        self.task_analyzer = TaskAnalyzer()
        self.context_aggregator = ContextAggregator()
        self.embedding_model = MultiAspectEmbeddingModel()
        
        # 优化策略
        self.optimization_strategies = {
            "adaptive": self._adaptive_optimization_strategy,
            "focused": self._focused_optimization_strategy,
            "comprehensive": self._comprehensive_optimization_strategy
        }
        
        logger.info("上下文优化引擎初始化完成")
    
    async def optimize_context(
        self, 
        request: ContextOptimizationRequest
    ) -> OptimizedContext:
        """优化上下文"""
        try:
            # 分析历史对话
            history_insights = await self.history_analyzer.analyze(
                request.conversation_history
            )
            
            # 分析当前任务
            task_insights = await self.task_analyzer.analyze(
                request.current_query, 
                request.current_task
            )
            
            # 聚合可用上下文
            aggregated_context = await self.context_aggregator.aggregate(
                request.available_context,
                history_insights,
                task_insights
            )
            
            # 执行优化策略
            strategy_func = self.optimization_strategies.get(
                request.optimization_strategy, 
                self._adaptive_optimization_strategy
            )
            
            optimized_context = await strategy_func(
                request,
                aggregated_context,
                history_insights,
                task_insights
            )
            
            logger.info(f"上下文优化完成: {request.user_id}, 策略: {request.optimization_strategy}")
            return optimized_context
            
        except Exception as e:
            logger.error(f"上下文优化失败: {e}")
            return OptimizedContext(
                optimized_prompt="",
                context_elements=[],
                relevance_scores={},
                optimization_reasoning=f"优化失败: {str(e)}",
                confidence_score=0.0,
                original_context_size=0,
                optimized_context_size=0
            )
    
    async def _adaptive_optimization_strategy(
        self,
        request: ContextOptimizationRequest,
        context_elements: list[ContextElement],
        history_insights: dict[str, Any],
        task_insights: dict[str, Any]
    ) -> OptimizedContext:
        """自适应优化策略"""
        # 根据用户历史和任务特征动态调整优化参数
        
        # 计算用户经验水平
        user_experience = self._calculate_user_experience(history_insights)
        
        # 根据经验水平调整上下文详细程度
        if user_experience > 0.7:
            # 经验丰富的用户，提供更精简的上下文
            max_elements = 10
            detail_level = "concise"
        elif user_experience > 0.4:
            # 中等经验用户，平衡详细程度
            max_elements = 15
            detail_level = "balanced"
        else:
            # 新用户，提供更详细的上下文
            max_elements = 20
            detail_level = "detailed"
        
        # 选择最相关的上下文元素
        selected_elements = self._select_relevant_elements(
            context_elements, 
            request.current_query,
            max_elements
        )
        
        # 生成优化后的提示
        optimized_prompt = self._generate_optimized_prompt(
            request.current_query,
            selected_elements,
            detail_level,
            history_insights,
            task_insights
        )
        
        # 计算相关性分数
        relevance_scores = {
            elem.element_id: elem.relevance_score 
            for elem in selected_elements
        }
        
        # 生成优化理由
        optimization_reasoning = self._generate_optimization_reasoning(
            "adaptive", user_experience, detail_level, len(selected_elements)
        )
        
        # 计算置信度
        confidence_score = self._calculate_optimization_confidence(
            selected_elements, history_insights, task_insights
        )
        
        return OptimizedContext(
            optimized_prompt=optimized_prompt,
            context_elements=selected_elements,
            relevance_scores=relevance_scores,
            optimization_reasoning=optimization_reasoning,
            confidence_score=confidence_score,
            original_context_size=len(context_elements),
            optimized_context_size=len(selected_elements),
            optimization_metrics={
                "user_experience": user_experience,
                "detail_level": detail_level,
                "strategy": "adaptive"
            }
        )
    
    async def _focused_optimization_strategy(
        self,
        request: ContextOptimizationRequest,
        context_elements: list[ContextElement],
        history_insights: dict[str, Any],
        task_insights: dict[str, Any]
    ) -> OptimizedContext:
        """聚焦优化策略"""
        # 专注于当前任务最相关的上下文
        
        # 只选择与当前任务高度相关的元素
        task_focused_elements = [
            elem for elem in context_elements 
            if elem.element_type in ["task", "knowledge"] and elem.relevance_score >= 0.6
        ]
        
        # 限制数量，保持聚焦
        selected_elements = task_focused_elements[:8]
        
        # 生成聚焦的提示
        optimized_prompt = self._generate_focused_prompt(
            request.current_query,
            selected_elements,
            task_insights
        )
        
        relevance_scores = {
            elem.element_id: elem.relevance_score 
            for elem in selected_elements
        }
        
        optimization_reasoning = (
            f"采用聚焦策略，专注于当前任务最相关的{len(selected_elements)}个上下文元素，"
            f"任务类型: {task_insights.get('task_type', 'unknown')}，"
            f"复杂度: {task_insights.get('complexity', 'unknown')}"
        )
        
        confidence_score = self._calculate_optimization_confidence(
            selected_elements, history_insights, task_insights
        )
        
        return OptimizedContext(
            optimized_prompt=optimized_prompt,
            context_elements=selected_elements,
            relevance_scores=relevance_scores,
            optimization_reasoning=optimization_reasoning,
            confidence_score=confidence_score,
            original_context_size=len(context_elements),
            optimized_context_size=len(selected_elements),
            optimization_metrics={
                "focus_threshold": 0.6,
                "strategy": "focused"
            }
        )
    
    async def _comprehensive_optimization_strategy(
        self,
        request: ContextOptimizationRequest,
        context_elements: list[ContextElement],
        history_insights: dict[str, Any],
        task_insights: dict[str, Any]
    ) -> OptimizedContext:
        """综合优化策略"""
        # 保留更多背景信息，支持复杂分析
        
        # 选择更多元素，包含各种类型的上下文
        type_quotas = {
            "history": 5,
            "task": 8,
            "environment": 3,
            "knowledge": 6
        }
        
        selected_elements = []
        for elem_type, quota in type_quotas.items():
            type_elements = [
                elem for elem in context_elements 
                if elem.element_type == elem_type
            ]
            # 按相关性排序并选择
            type_elements.sort(key=lambda x: x.relevance_score, reverse=True)
            selected_elements.extend(type_elements[:quota])
        
        # 按相关性重新排序
        selected_elements.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 生成综合的提示
        optimized_prompt = self._generate_comprehensive_prompt(
            request.current_query,
            selected_elements,
            history_insights,
            task_insights
        )
        
        relevance_scores = {
            elem.element_id: elem.relevance_score 
            for elem in selected_elements
        }
        
        optimization_reasoning = (
            f"采用综合策略，保留丰富的背景信息支持复杂分析，"
            f"包含{len(selected_elements)}个上下文元素，"
            f"覆盖历史、任务、环境、知识等多个维度"
        )
        
        confidence_score = self._calculate_optimization_confidence(
            selected_elements, history_insights, task_insights
        )
        
        return OptimizedContext(
            optimized_prompt=optimized_prompt,
            context_elements=selected_elements,
            relevance_scores=relevance_scores,
            optimization_reasoning=optimization_reasoning,
            confidence_score=confidence_score,
            original_context_size=len(context_elements),
            optimized_context_size=len(selected_elements),
            optimization_metrics={
                "type_quotas": type_quotas,
                "strategy": "comprehensive"
            }
        )
    
    def _calculate_user_experience(self, history_insights: dict[str, Any]) -> float:
        """计算用户经验水平"""
        total_conversations = history_insights.get("total_conversations", 0)
        success_rate = history_insights.get("success_indicators", {}).get("task_completion_rate", 0.0)
        topic_diversity = len(history_insights.get("key_topics", []))
        
        # 综合计算经验水平
        conversation_factor = min(total_conversations / 50, 1.0)  # 50次对话为满分
        success_factor = success_rate
        diversity_factor = min(topic_diversity / 10, 1.0)  # 10个主题为满分
        
        experience_level = (
            conversation_factor * 0.4 +
            success_factor * 0.4 +
            diversity_factor * 0.2
        )
        
        return experience_level
    
    def _select_relevant_elements(
        self, 
        elements: list[ContextElement], 
        query: str, 
        max_elements: int
    ) -> list[ContextElement]:
        """选择相关的上下文元素"""
        # 计算查询嵌入
        query_pattern, query_goal, _, _ = self.embedding_model.encode_multi_aspect(query)
        
        # 为每个元素计算与查询的相似度
        for element in elements:
            if element.embedding is None:
                # 为元素生成嵌入
                elem_pattern, elem_goal, _, _ = self.embedding_model.encode_multi_aspect(
                    element.content
                )
                element.embedding = elem_pattern  # 简化，只使用模式嵌入
            
            # 计算相似度
            if element.embedding is not None:
                similarity = self._cosine_similarity(query_pattern, element.embedding)
                # 调整相关性分数
                element.relevance_score = (element.relevance_score + similarity) / 2
        
        # 按调整后的相关性排序并选择
        elements.sort(key=lambda x: x.relevance_score, reverse=True)
        return elements[:max_elements]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except:
            return 0.0
    
    def _generate_optimized_prompt(
        self,
        query: str,
        elements: list[ContextElement],
        detail_level: str,
        history_insights: dict[str, Any],
        task_insights: dict[str, Any]
    ) -> str:
        """生成优化后的提示"""
        prompt_parts = []
        
        # 添加系统角色说明
        prompt_parts.append("你是一个智能助手，能够基于用户的历史对话和当前任务提供个性化的帮助。")
        
        # 添加用户背景信息
        key_topics = history_insights.get("key_topics", [])
        if key_topics:
            prompt_parts.append(f"用户历史关注的主要话题包括: {', '.join(key_topics[:3])}")
        
        preferences = history_insights.get("preferences", {})
        preferred_style = preferences.get("preferred_response_style", "balanced")
        if preferred_style != "balanced":
            prompt_parts.append(f"用户偏好{preferred_style}的回应风格")
        
        # 添加任务信息
        task_type = task_insights.get("task_type", "general")
        complexity = task_insights.get("complexity", "medium")
        prompt_parts.append(f"当前任务类型: {task_type}, 复杂度: {complexity}")
        
        # 添加相关上下文
        if elements:
            prompt_parts.append("相关上下文信息:")
            for elem in elements[:10]:  # 限制显示数量
                if detail_level == "concise":
                    prompt_parts.append(f"- {elem.content[:50]}...")
                elif detail_level == "detailed":
                    prompt_parts.append(f"- {elem.content} (相关性: {elem.relevance_score:.2f})")
                else:
                    prompt_parts.append(f"- {elem.content}")
        
        # 添加用户查询
        prompt_parts.append(f"用户问题: {query}")
        
        # 添加回应指导
        if detail_level == "concise":
            prompt_parts.append("请提供简洁而精准的回应。")
        elif detail_level == "detailed":
            prompt_parts.append("请提供详细和全面的回应，包含必要的解释和背景信息。")
        else:
            prompt_parts.append("请提供平衡的回应，既要准确又要易于理解。")
        
        return "\n\n".join(prompt_parts)
    
    def _generate_focused_prompt(
        self,
        query: str,
        elements: list[ContextElement],
        task_insights: dict[str, Any]
    ) -> str:
        """生成聚焦的提示"""
        prompt_parts = []
        
        prompt_parts.append("你是一个专业的任务处理助手，专注于解决当前的具体问题。")
        
        task_type = task_insights.get("task_type", "general")
        prompt_parts.append(f"当前任务类型: {task_type}")
        
        # 只包含最相关的上下文
        if elements:
            prompt_parts.append("核心相关信息:")
            for elem in elements[:5]:  # 只显示前5个最相关的
                prompt_parts.append(f"- {elem.content}")
        
        prompt_parts.append(f"用户问题: {query}")
        prompt_parts.append("请直接针对问题提供精准的解答。")
        
        return "\n\n".join(prompt_parts)
    
    def _generate_comprehensive_prompt(
        self,
        query: str,
        elements: list[ContextElement],
        history_insights: dict[str, Any],
        task_insights: dict[str, Any]
    ) -> str:
        """生成综合的提示"""
        prompt_parts = []
        
        prompt_parts.append("你是一个全面的智能分析助手，能够综合考虑多方面信息提供深入的分析和建议。")
        
        # 详细的用户背景
        total_conversations = history_insights.get("total_conversations", 0)
        if total_conversations > 0:
            prompt_parts.append(f"用户已进行{total_conversations}次对话，显示出持续的学习和探索意愿。")
        
        key_topics = history_insights.get("key_topics", [])
        if key_topics:
            prompt_parts.append(f"用户的兴趣领域包括: {', '.join(key_topics)}")
        
        # 任务详细信息
        task_type = task_insights.get("task_type", "general")
        complexity = task_insights.get("complexity", "medium")
        keywords = task_insights.get("keywords", [])
        
        prompt_parts.append(f"当前任务: 类型={task_type}, 复杂度={complexity}")
        if keywords:
            prompt_parts.append(f"关键概念: {', '.join(keywords[:5])}")
        
        # 分类显示上下文
        context_by_type = defaultdict(list)
        for elem in elements:
            context_by_type[elem.element_type].append(elem)
        
        for elem_type, type_elements in context_by_type.items():
            if type_elements:
                type_name = {
                    "history": "历史背景",
                    "task": "任务相关",
                    "environment": "环境信息",
                    "knowledge": "相关知识"
                }.get(elem_type, elem_type)
                
                prompt_parts.append(f"{type_name}:")
                for elem in type_elements[:5]:  # 每类最多5个
                    prompt_parts.append(f"  - {elem.content}")
        
        prompt_parts.append(f"用户问题: {query}")
        prompt_parts.append("请基于以上全面的背景信息，提供深入、多角度的分析和建议。")
        
        return "\n\n".join(prompt_parts)
    
    def _generate_optimization_reasoning(
        self, 
        strategy: str, 
        user_experience: float, 
        detail_level: str, 
        element_count: int
    ) -> str:
        """生成优化理由"""
        reasoning_parts = []
        
        strategy_descriptions = {
            "adaptive": "自适应策略",
            "focused": "聚焦策略", 
            "comprehensive": "综合策略"
        }
        
        reasoning_parts.append(f"采用{strategy_descriptions.get(strategy, strategy)}")
        
        if strategy == "adaptive":
            experience_level = "高" if user_experience > 0.7 else "中" if user_experience > 0.4 else "低"
            reasoning_parts.append(f"根据用户经验水平({experience_level})调整为{detail_level}详细程度")
        
        reasoning_parts.append(f"选择了{element_count}个最相关的上下文元素")
        reasoning_parts.append("基于多面嵌入技术计算相关性并优化上下文结构")
        
        return "，".join(reasoning_parts) + "。"
    
    def _calculate_optimization_confidence(
        self,
        selected_elements: list[ContextElement],
        history_insights: dict[str, Any],
        task_insights: dict[str, Any]
    ) -> float:
        """计算优化置信度"""
        if not selected_elements:
            return 0.0
        
        # 基于元素质量的置信度
        avg_relevance = sum(elem.relevance_score for elem in selected_elements) / len(selected_elements)
        avg_confidence = sum(elem.confidence_score for elem in selected_elements) / len(selected_elements)
        
        # 基于分析质量的置信度
        history_confidence = history_insights.get("analysis_confidence", 0.5)
        task_confidence = task_insights.get("analysis_confidence", 0.5)
        
        # 综合置信度
        overall_confidence = (
            avg_relevance * 0.3 +
            avg_confidence * 0.3 +
            history_confidence * 0.2 +
            task_confidence * 0.2
        )
        
        return min(overall_confidence, 1.0)