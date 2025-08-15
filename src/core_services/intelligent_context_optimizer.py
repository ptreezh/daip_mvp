#!/usr/bin/env python3
"""智能上下文优化器

基于用户历史对话记录和当前任务，使用多面嵌入技术优化LLM调用的上下文
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


@dataclass
class ContextEmbedding:
    """多面嵌入上下文模型"""
    problem_pattern: np.ndarray  # 问题模式嵌入
    goal_embedding: np.ndarray   # 目标嵌入  
    solution_steps: np.ndarray   # 解决方案步骤嵌入
    context_embedding: np.ndarray # 上下文嵌入（可选）
    metadata: dict[str, Any]     # 元数据
    
    def similarity(self, other: 'ContextEmbedding') -> float:
        """计算多维相似度"""
        try:
            pattern_sim = self._cosine_similarity(self.problem_pattern, other.problem_pattern)
            goal_sim = self._cosine_similarity(self.goal_embedding, other.goal_embedding)
            solution_sim = self._cosine_similarity(self.solution_steps, other.solution_steps)
            context_sim = self._cosine_similarity(self.context_embedding, other.context_embedding)
            
            # 加权计算综合相似度
            return (pattern_sim * 0.3 + goal_sim * 0.3 + 
                    solution_sim * 0.25 + context_sim * 0.15)
        except Exception as e:
            logger.warning(f"计算相似度失败: {e}")
            return 0.0
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        if vec1 is None or vec2 is None:
            return 0.0
        
        # 确保向量是一维的
        vec1 = vec1.flatten()
        vec2 = vec2.flatten()
        
        # 处理零向量
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)


@dataclass
class Conversation:
    """对话记录"""
    conversation_id: str
    user_id: str
    messages: list[dict[str, Any]]
    timestamp: str
    topic: Optional[str] = None
    task_type: Optional[str] = None
    outcome: Optional[str] = None


@dataclass
class Task:
    """当前任务"""
    task_id: str
    task_type: str
    description: str
    required_roles: list[str]
    complexity_level: str
    expected_output: str
    context_requirements: list[str]


@dataclass
class OptimizedContext:
    """优化后的上下文"""
    context_id: str
    original_context: dict[str, Any]
    optimized_context: dict[str, Any]
    optimization_reasoning: str
    relevance_scores: dict[str, float]
    embedding_analysis: dict[str, Any]
    performance_metrics: dict[str, float]


class IntelligentContextOptimizer:
    """智能上下文优化器"""
    
    def __init__(self):
        """初始化智能上下文优化器"""
        self.conversation_analyzer = ConversationHistoryAnalyzer()
        self.task_analyzer = TaskFeatureAnalyzer()
        self.embedding_processor = MultifacetedEmbeddingProcessor()
        self.context_synthesizer = ContextSynthesizer()
        
        # 缓存已计算的嵌入
        self.embedding_cache = {}
        
        logger.info("智能上下文优化器初始化完成")
    
    def optimize_context(self, 
                        user_history: list[Conversation],
                        current_task: Task,
                        available_context: dict[str, Any]) -> OptimizedContext:
        """优化上下文"""
        try:
            context_id = f"ctx_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 1. 分析历史对话模式
            logger.info("分析用户历史对话模式...")
            history_patterns = self.conversation_analyzer.analyze_conversation_history(user_history)
            
            # 2. 提取当前任务特征
            logger.info("提取当前任务特征...")
            task_features = self.task_analyzer.extract_task_features(current_task)
            
            # 3. 生成多面嵌入
            logger.info("生成多面嵌入...")
            embeddings = self.embedding_processor.generate_multifaceted_embeddings(
                history_patterns, task_features, available_context
            )
            
            # 4. 计算上下文相关性
            logger.info("计算上下文相关性...")
            relevance_scores = self._calculate_context_relevance(embeddings, available_context)
            
            # 5. 合成优化上下文
            logger.info("合成优化上下文...")
            optimized_context_data = self.context_synthesizer.synthesize_context(
                relevance_scores, available_context, task_features
            )
            
            # 6. 生成优化理由
            optimization_reasoning = self._generate_optimization_reasoning(
                history_patterns, task_features, relevance_scores
            )
            
            # 7. 计算性能指标
            performance_metrics = self._calculate_performance_metrics(
                available_context, optimized_context_data, relevance_scores
            )
            
            optimized_context = OptimizedContext(
                context_id=context_id,
                original_context=available_context,
                optimized_context=optimized_context_data,
                optimization_reasoning=optimization_reasoning,
                relevance_scores=relevance_scores,
                embedding_analysis={
                    "history_patterns": history_patterns,
                    "task_features": task_features,
                    "embedding_dimensions": len(embeddings.problem_pattern) if embeddings.problem_pattern is not None else 0
                },
                performance_metrics=performance_metrics
            )
            
            logger.info(f"上下文优化完成: {context_id}")
            return optimized_context
            
        except Exception as e:
            logger.error(f"上下文优化失败: {e}")
            # 返回原始上下文作为fallback
            return OptimizedContext(
                context_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                original_context=available_context,
                optimized_context=available_context,
                optimization_reasoning=f"优化失败，使用原始上下文: {str(e)}",
                relevance_scores={},
                embedding_analysis={},
                performance_metrics={}
            )
    
    def _calculate_context_relevance(self, 
                                   embeddings: ContextEmbedding,
                                   available_context: dict[str, Any]) -> dict[str, float]:
        """计算上下文相关性"""
        relevance_scores = {}
        
        try:
            for context_key, context_value in available_context.items():
                if isinstance(context_value, str):
                    # 为每个上下文片段生成嵌入
                    context_embedding = self.embedding_processor.generate_text_embedding(context_value)
                    
                    # 计算与当前任务的相关性
                    if context_embedding is not None and embeddings.context_embedding is not None:
                        similarity = self.embedding_processor._cosine_similarity(
                            context_embedding, embeddings.context_embedding
                        )
                        relevance_scores[context_key] = similarity
                    else:
                        # 使用简单的关键词匹配作为fallback
                        relevance_scores[context_key] = self._keyword_relevance(
                            context_value, embeddings.metadata.get("keywords", [])
                        )
                else:
                    # 对于非文本内容，给予默认相关性分数
                    relevance_scores[context_key] = 0.5
            
        except Exception as e:
            logger.warning(f"计算上下文相关性失败: {e}")
        
        return relevance_scores
    
    def _keyword_relevance(self, text: str, keywords: list[str]) -> float:
        """基于关键词计算相关性"""
        if not keywords:
            return 0.5
        
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        return min(matches / len(keywords), 1.0)
    
    def _generate_optimization_reasoning(self,
                                       history_patterns: dict[str, Any],
                                       task_features: dict[str, Any],
                                       relevance_scores: dict[str, float]) -> str:
        """生成优化理由"""
        reasoning_parts = []
        
        # 基于历史模式的优化
        if history_patterns.get("dominant_topics"):
            dominant_topics = history_patterns["dominant_topics"][:3]
            reasoning_parts.append(f"基于用户历史对话中的主要话题({', '.join(dominant_topics)})进行上下文优化")
        
        # 基于任务特征的优化
        task_type = task_features.get("task_type", "unknown")
        complexity = task_features.get("complexity_level", "medium")
        reasoning_parts.append(f"针对{task_type}类型任务(复杂度: {complexity})调整上下文结构")
        
        # 基于相关性分数的优化
        high_relevance_items = [k for k, v in relevance_scores.items() if v > 0.7]
        if high_relevance_items:
            reasoning_parts.append(f"重点保留高相关性内容: {', '.join(high_relevance_items[:3])}")
        
        low_relevance_items = [k for k, v in relevance_scores.items() if v < 0.3]
        if low_relevance_items:
            reasoning_parts.append(f"过滤低相关性内容: {len(low_relevance_items)}项")
        
        if not reasoning_parts:
            reasoning_parts.append("基于多面嵌入分析进行标准上下文优化")
        
        return "；".join(reasoning_parts) + "。"
    
    def _calculate_performance_metrics(self,
                                     original_context: dict[str, Any],
                                     optimized_context: dict[str, Any],
                                     relevance_scores: dict[str, float]) -> dict[str, float]:
        """计算性能指标"""
        try:
            # 计算上下文压缩率
            original_size = len(str(original_context))
            optimized_size = len(str(optimized_context))
            compression_ratio = 1 - (optimized_size / original_size) if original_size > 0 else 0
            
            # 计算平均相关性
            avg_relevance = sum(relevance_scores.values()) / len(relevance_scores) if relevance_scores else 0.5
            
            # 计算信息密度
            high_relevance_count = sum(1 for score in relevance_scores.values() if score > 0.6)
            total_items = len(relevance_scores)
            information_density = high_relevance_count / total_items if total_items > 0 else 0
            
            # 计算优化效果分数
            optimization_score = (avg_relevance * 0.5 + information_density * 0.3 + 
                                min(compression_ratio, 0.5) * 0.2)
            
            return {
                "compression_ratio": compression_ratio,
                "average_relevance": avg_relevance,
                "information_density": information_density,
                "optimization_score": optimization_score,
                "original_size": original_size,
                "optimized_size": optimized_size
            }
            
        except Exception as e:
            logger.warning(f"计算性能指标失败: {e}")
            return {
                "compression_ratio": 0.0,
                "average_relevance": 0.5,
                "information_density": 0.5,
                "optimization_score": 0.5,
                "original_size": 0,
                "optimized_size": 0
            }


class ConversationHistoryAnalyzer:
    """对话历史分析器"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def analyze_conversation_history(self, conversations: list[Conversation]) -> dict[str, Any]:
        """分析对话历史"""
        try:
            if not conversations:
                return {"dominant_topics": [], "user_patterns": {}, "interaction_frequency": {}}
            
            # 提取所有对话文本
            all_texts = []
            topics = []
            interaction_types = defaultdict(int)
            
            for conv in conversations:
                for message in conv.messages:
                    content = message.get("content", "")
                    if content:
                        all_texts.append(content)
                        
                        # 分析交互类型
                        msg_type = message.get("type", "unknown")
                        interaction_types[msg_type] += 1
                
                if conv.topic:
                    topics.append(conv.topic)
            
            # 主题聚类分析
            dominant_topics = self._extract_dominant_topics(all_texts)
            
            # 用户模式分析
            user_patterns = self._analyze_user_patterns(conversations)
            
            # 交互频率分析
            interaction_frequency = dict(interaction_types)
            
            return {
                "dominant_topics": dominant_topics,
                "user_patterns": user_patterns,
                "interaction_frequency": interaction_frequency,
                "total_conversations": len(conversations),
                "total_messages": len(all_texts),
                "unique_topics": list(set(topics))
            }
            
        except Exception as e:
            logger.error(f"分析对话历史失败: {e}")
            return {"dominant_topics": [], "user_patterns": {}, "interaction_frequency": {}}
    
    def _extract_dominant_topics(self, texts: list[str]) -> list[str]:
        """提取主导话题"""
        if not texts:
            return []
        
        try:
            # 使用TF-IDF提取关键词
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # 计算每个词的平均TF-IDF分数
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # 获取分数最高的词作为主导话题
            top_indices = np.argsort(mean_scores)[-10:][::-1]
            dominant_topics = [feature_names[i] for i in top_indices if mean_scores[i] > 0.1]
            
            return dominant_topics[:5]  # 返回前5个主导话题
            
        except Exception as e:
            logger.warning(f"提取主导话题失败: {e}")
            return []
    
    def _analyze_user_patterns(self, conversations: list[Conversation]) -> dict[str, Any]:
        """分析用户模式"""
        patterns = {
            "avg_message_length": 0,
            "preferred_time": "unknown",
            "question_ratio": 0,
            "topic_diversity": 0
        }
        
        try:
            total_length = 0
            total_messages = 0
            question_count = 0
            time_hours = defaultdict(int)
            topics = set()
            
            for conv in conversations:
                if conv.topic:
                    topics.add(conv.topic)
                
                # 分析时间模式
                try:
                    dt = datetime.fromisoformat(conv.timestamp.replace('Z', '+00:00'))
                    time_hours[dt.hour] += 1
                except:
                    pass
                
                for message in conv.messages:
                    content = message.get("content", "")
                    if content:
                        total_length += len(content)
                        total_messages += 1
                        
                        # 检测问题
                        if "?" in content or content.strip().endswith("？"):
                            question_count += 1
            
            if total_messages > 0:
                patterns["avg_message_length"] = total_length / total_messages
                patterns["question_ratio"] = question_count / total_messages
            
            if time_hours:
                most_active_hour = max(time_hours.items(), key=lambda x: x[1])[0]
                patterns["preferred_time"] = f"{most_active_hour:02d}:00"
            
            patterns["topic_diversity"] = len(topics)
            
        except Exception as e:
            logger.warning(f"分析用户模式失败: {e}")
        
        return patterns


class TaskFeatureAnalyzer:
    """任务特征分析器"""
    
    def extract_task_features(self, task: Task) -> dict[str, Any]:
        """提取任务特征"""
        try:
            features = {
                "task_type": task.task_type,
                "complexity_level": task.complexity_level,
                "required_roles": task.required_roles,
                "expected_output": task.expected_output,
                "context_requirements": task.context_requirements,
                "description_length": len(task.description),
                "role_count": len(task.required_roles),
                "keywords": self._extract_keywords(task.description)
            }
            
            # 分析任务复杂度
            complexity_score = self._calculate_complexity_score(task)
            features["complexity_score"] = complexity_score
            
            # 分析所需资源
            resource_requirements = self._analyze_resource_requirements(task)
            features["resource_requirements"] = resource_requirements
            
            return features
            
        except Exception as e:
            logger.error(f"提取任务特征失败: {e}")
            return {
                "task_type": "unknown",
                "complexity_level": "medium",
                "required_roles": [],
                "keywords": []
            }
    
    def _extract_keywords(self, text: str) -> list[str]:
        """提取关键词"""
        # 简单的关键词提取
        keywords = []
        
        # 预定义的重要关键词
        important_terms = [
            "AI伦理", "人工智能", "机器学习", "算法", "透明度", "公平性",
            "隐私", "安全", "监管", "政策", "决策", "分析", "评估", "优化"
        ]
        
        text_lower = text.lower()
        for term in important_terms:
            if term.lower() in text_lower:
                keywords.append(term)
        
        # 使用正则表达式提取其他关键词
        word_pattern = r'\b[a-zA-Z\u4e00-\u9fff]{3,}\b'
        words = re.findall(word_pattern, text)
        
        # 过滤常见词汇
        stop_words = {"的", "是", "在", "有", "和", "与", "或", "但", "如果", "因为", "所以"}
        filtered_words = [word for word in words if word not in stop_words]
        
        keywords.extend(filtered_words[:10])  # 添加前10个词
        
        return list(set(keywords))  # 去重
    
    def _calculate_complexity_score(self, task: Task) -> float:
        """计算任务复杂度分数"""
        score = 0.0
        
        # 基于描述长度
        if len(task.description) > 200:
            score += 0.3
        elif len(task.description) > 100:
            score += 0.2
        else:
            score += 0.1
        
        # 基于所需角色数量
        role_count = len(task.required_roles)
        if role_count > 5:
            score += 0.4
        elif role_count > 3:
            score += 0.3
        else:
            score += 0.2
        
        # 基于复杂度级别
        complexity_map = {
            "simple": 0.1,
            "medium": 0.3,
            "complex": 0.5,
            "expert": 0.7
        }
        score += complexity_map.get(task.complexity_level, 0.3)
        
        return min(score, 1.0)
    
    def _analyze_resource_requirements(self, task: Task) -> dict[str, Any]:
        """分析资源需求"""
        return {
            "computational_intensity": "medium",  # 基于任务类型推断
            "memory_requirements": "standard",
            "time_estimate": "5-15 minutes",  # 基于复杂度推断
            "specialized_knowledge": len(task.required_roles) > 3
        }


class MultifacetedEmbeddingProcessor:
    """多面嵌入处理器"""
    
    def __init__(self):
        self.embedding_dim = 384  # 使用标准的嵌入维度
        
    def generate_multifaceted_embeddings(self,
                                       history_patterns: dict[str, Any],
                                       task_features: dict[str, Any],
                                       available_context: dict[str, Any]) -> ContextEmbedding:
        """生成多面嵌入"""
        try:
            # 生成问题模式嵌入
            problem_pattern = self._generate_problem_pattern_embedding(
                history_patterns, task_features
            )
            
            # 生成目标嵌入
            goal_embedding = self._generate_goal_embedding(task_features)
            
            # 生成解决方案步骤嵌入
            solution_steps = self._generate_solution_steps_embedding(
                task_features, available_context
            )
            
            # 生成上下文嵌入
            context_embedding = self._generate_context_embedding(available_context)
            
            # 生成元数据
            metadata = {
                "keywords": task_features.get("keywords", []),
                "task_type": task_features.get("task_type", "unknown"),
                "complexity": task_features.get("complexity_level", "medium"),
                "generation_time": datetime.now().isoformat()
            }
            
            return ContextEmbedding(
                problem_pattern=problem_pattern,
                goal_embedding=goal_embedding,
                solution_steps=solution_steps,
                context_embedding=context_embedding,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"生成多面嵌入失败: {e}")
            # 返回零向量作为fallback
            zero_embedding = np.zeros(self.embedding_dim)
            return ContextEmbedding(
                problem_pattern=zero_embedding,
                goal_embedding=zero_embedding,
                solution_steps=zero_embedding,
                context_embedding=zero_embedding,
                metadata={"error": str(e)}
            )
    
    def _generate_problem_pattern_embedding(self,
                                          history_patterns: dict[str, Any],
                                          task_features: dict[str, Any]) -> np.ndarray:
        """生成问题模式嵌入"""
        # 简化实现：基于历史话题和当前任务类型
        features = []
        
        # 历史话题特征
        dominant_topics = history_patterns.get("dominant_topics", [])
        topic_vector = np.zeros(100)  # 话题向量
        for i, topic in enumerate(dominant_topics[:100]):
            topic_vector[i] = 1.0
        features.extend(topic_vector)
        
        # 任务类型特征
        task_type = task_features.get("task_type", "unknown")
        task_type_vector = self._encode_task_type(task_type)
        features.extend(task_type_vector)
        
        # 复杂度特征
        complexity = task_features.get("complexity_score", 0.5)
        complexity_vector = np.full(50, complexity)
        features.extend(complexity_vector)
        
        # 用户模式特征
        user_patterns = history_patterns.get("user_patterns", {})
        pattern_vector = self._encode_user_patterns(user_patterns)
        features.extend(pattern_vector)
        
        # 确保向量长度正确
        embedding = np.array(features[:self.embedding_dim])
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding))
            embedding = np.concatenate([embedding, padding])
        
        return embedding
    
    def _generate_goal_embedding(self, task_features: dict[str, Any]) -> np.ndarray:
        """生成目标嵌入"""
        features = []
        
        # 预期输出特征
        expected_output = task_features.get("expected_output", "")
        output_vector = self._encode_text_features(expected_output, 100)
        features.extend(output_vector)
        
        # 所需角色特征
        required_roles = task_features.get("required_roles", [])
        role_vector = self._encode_roles(required_roles)
        features.extend(role_vector)
        
        # 上下文需求特征
        context_requirements = task_features.get("context_requirements", [])
        context_req_vector = self._encode_context_requirements(context_requirements)
        features.extend(context_req_vector)
        
        # 填充到目标维度
        embedding = np.array(features[:self.embedding_dim])
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding))
            embedding = np.concatenate([embedding, padding])
        
        return embedding
    
    def _generate_solution_steps_embedding(self,
                                         task_features: dict[str, Any],
                                         available_context: dict[str, Any]) -> np.ndarray:
        """生成解决方案步骤嵌入"""
        features = []
        
        # 任务描述特征
        description = task_features.get("description", "")
        desc_vector = self._encode_text_features(description, 150)
        features.extend(desc_vector)
        
        # 可用上下文特征
        context_vector = self._encode_available_context(available_context)
        features.extend(context_vector)
        
        # 资源需求特征
        resource_req = task_features.get("resource_requirements", {})
        resource_vector = self._encode_resource_requirements(resource_req)
        features.extend(resource_vector)
        
        # 填充到目标维度
        embedding = np.array(features[:self.embedding_dim])
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding))
            embedding = np.concatenate([embedding, padding])
        
        return embedding
    
    def _generate_context_embedding(self, available_context: dict[str, Any]) -> np.ndarray:
        """生成上下文嵌入"""
        features = []
        
        # 遍历所有可用上下文
        for key, value in available_context.items():
            if isinstance(value, str):
                # 文本内容特征
                text_features = self._encode_text_features(value, 50)
                features.extend(text_features)
            elif isinstance(value, (list, dict)):
                # 结构化数据特征
                struct_features = self._encode_structured_data(value)
                features.extend(struct_features)
        
        # 填充到目标维度
        embedding = np.array(features[:self.embedding_dim])
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding))
            embedding = np.concatenate([embedding, padding])
        
        return embedding
    
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """生成文本嵌入"""
        return self._encode_text_features(text, self.embedding_dim)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        if vec1 is None or vec2 is None:
            return 0.0
        
        vec1 = vec1.flatten()
        vec2 = vec2.flatten()
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def _encode_task_type(self, task_type: str) -> list[float]:
        """编码任务类型"""
        type_map = {
            "analysis": [1.0, 0.0, 0.0, 0.0],
            "decision": [0.0, 1.0, 0.0, 0.0],
            "evaluation": [0.0, 0.0, 1.0, 0.0],
            "creation": [0.0, 0.0, 0.0, 1.0]
        }
        
        base_vector = type_map.get(task_type, [0.25, 0.25, 0.25, 0.25])
        return base_vector + [0.0] * 96  # 填充到100维
    
    def _encode_user_patterns(self, patterns: dict[str, Any]) -> list[float]:
        """编码用户模式"""
        features = []
        
        # 平均消息长度（归一化）
        avg_length = patterns.get("avg_message_length", 100)
        features.append(min(avg_length / 500, 1.0))
        
        # 问题比例
        question_ratio = patterns.get("question_ratio", 0.3)
        features.append(question_ratio)
        
        # 话题多样性（归一化）
        topic_diversity = patterns.get("topic_diversity", 5)
        features.append(min(topic_diversity / 20, 1.0))
        
        # 填充到目标长度
        while len(features) < 134:  # 384 - 100 - 100 - 50 = 134
            features.append(0.0)
        
        return features[:134]
    
    def _encode_text_features(self, text: str, target_dim: int) -> list[float]:
        """编码文本特征"""
        if not text:
            return [0.0] * target_dim
        
        features = []
        
        # 文本长度特征
        features.append(min(len(text) / 1000, 1.0))
        
        # 字符频率特征
        char_counts = defaultdict(int)
        for char in text.lower():
            if char.isalnum():
                char_counts[char] += 1
        
        # 取最常见的字符
        common_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        for char, count in common_chars:
            features.append(min(count / len(text), 1.0))
        
        # 填充到目标维度
        while len(features) < target_dim:
            features.append(0.0)
        
        return features[:target_dim]
    
    def _encode_roles(self, roles: list[str]) -> list[float]:
        """编码角色特征"""
        # 预定义角色类型
        role_types = [
            "analyst", "creative", "strategic", "ethical", "technical",
            "legal", "medical", "financial", "educational", "social"
        ]
        
        features = []
        for role_type in role_types:
            # 检查是否有匹配的角色
            match_count = sum(1 for role in roles if role_type in role.lower())
            features.append(min(match_count / len(roles) if roles else 0, 1.0))
        
        # 填充到目标长度
        while len(features) < 100:
            features.append(0.0)
        
        return features[:100]
    
    def _encode_context_requirements(self, requirements: list[str]) -> list[float]:
        """编码上下文需求特征"""
        features = []
        
        # 需求数量
        features.append(min(len(requirements) / 10, 1.0))
        
        # 需求类型分析
        requirement_types = ["data", "analysis", "history", "expert", "reference"]
        for req_type in requirement_types:
            match_count = sum(1 for req in requirements if req_type in req.lower())
            features.append(min(match_count / len(requirements) if requirements else 0, 1.0))
        
        # 填充到目标长度
        while len(features) < 84:  # 384 - 100 - 100 - 100 = 84
            features.append(0.0)
        
        return features[:84]
    
    def _encode_available_context(self, context: dict[str, Any]) -> list[float]:
        """编码可用上下文特征"""
        features = []
        
        # 上下文项目数量
        features.append(min(len(context) / 20, 1.0))
        
        # 上下文类型分析
        text_count = sum(1 for v in context.values() if isinstance(v, str))
        list_count = sum(1 for v in context.values() if isinstance(v, list))
        dict_count = sum(1 for v in context.values() if isinstance(v, dict))
        
        total_items = len(context)
        if total_items > 0:
            features.extend([
                text_count / total_items,
                list_count / total_items,
                dict_count / total_items
            ])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        # 填充到目标长度
        while len(features) < 80:
            features.append(0.0)
        
        return features[:80]
    
    def _encode_resource_requirements(self, requirements: dict[str, Any]) -> list[float]:
        """编码资源需求特征"""
        features = []
        
        # 计算强度
        intensity_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "extreme": 1.0}
        intensity = requirements.get("computational_intensity", "medium")
        features.append(intensity_map.get(intensity, 0.5))
        
        # 内存需求
        memory_map = {"minimal": 0.2, "standard": 0.5, "high": 0.8, "extreme": 1.0}
        memory = requirements.get("memory_requirements", "standard")
        features.append(memory_map.get(memory, 0.5))
        
        # 专业知识需求
        specialized = requirements.get("specialized_knowledge", False)
        features.append(1.0 if specialized else 0.0)
        
        # 填充到目标长度
        while len(features) < 54:  # 384 - 150 - 100 - 80 = 54
            features.append(0.0)
        
        return features[:54]
    
    def _encode_structured_data(self, data: Any) -> list[float]:
        """编码结构化数据特征"""
        features = []
        
        if isinstance(data, list):
            features.append(min(len(data) / 50, 1.0))  # 列表长度
            features.append(1.0)  # 是列表
            features.append(0.0)  # 不是字典
        elif isinstance(data, dict):
            features.append(min(len(data) / 20, 1.0))  # 字典大小
            features.append(0.0)  # 不是列表
            features.append(1.0)  # 是字典
        else:
            features.extend([0.0, 0.0, 0.0])
        
        # 填充到固定长度
        while len(features) < 10:
            features.append(0.0)
        
        return features[:10]


class ContextSynthesizer:
    """上下文合成器"""
    
    def synthesize_context(self,
                          relevance_scores: dict[str, float],
                          available_context: dict[str, Any],
                          task_features: dict[str, Any]) -> dict[str, Any]:
        """合成优化上下文"""
        try:
            optimized_context = {}
            
            # 1. 按相关性分数排序
            sorted_items = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
            
            # 2. 选择高相关性项目
            high_relevance_threshold = 0.6
            selected_items = [item for item, score in sorted_items if score >= high_relevance_threshold]
            
            # 3. 如果高相关性项目太少，降低阈值
            if len(selected_items) < 3:
                medium_relevance_threshold = 0.4
                selected_items = [item for item, score in sorted_items if score >= medium_relevance_threshold]
            
            # 4. 确保至少有一些基本上下文
            if len(selected_items) < 2:
                selected_items = [item for item, score in sorted_items[:5]]
            
            # 5. 构建优化后的上下文
            for item in selected_items:
                if item in available_context:
                    optimized_context[item] = available_context[item]
            
            # 6. 添加任务特定的上下文增强
            task_enhancements = self._generate_task_enhancements(task_features)
            optimized_context.update(task_enhancements)
            
            # 7. 添加元信息
            optimized_context["_optimization_metadata"] = {
                "optimization_time": datetime.now().isoformat(),
                "selected_items": selected_items,
                "relevance_threshold": high_relevance_threshold,
                "total_original_items": len(available_context),
                "optimization_ratio": len(selected_items) / len(available_context) if available_context else 0
            }
            
            return optimized_context
            
        except Exception as e:
            logger.error(f"合成上下文失败: {e}")
            return available_context  # 返回原始上下文作为fallback
    
    def _generate_task_enhancements(self, task_features: dict[str, Any]) -> dict[str, Any]:
        """生成任务特定的上下文增强"""
        enhancements = {}
        
        # 基于任务类型添加特定指导
        task_type = task_features.get("task_type", "unknown")
        
        if task_type == "analysis":
            enhancements["analysis_guidelines"] = {
                "approach": "systematic_analysis",
                "focus_areas": ["data_examination", "pattern_identification", "conclusion_drawing"],
                "output_structure": "structured_report"
            }
        elif task_type == "decision":
            enhancements["decision_framework"] = {
                "methodology": "multi_criteria_evaluation",
                "considerations": ["feasibility", "risks", "benefits", "alternatives"],
                "output_format": "recommendation_with_rationale"
            }
        elif task_type == "evaluation":
            enhancements["evaluation_criteria"] = {
                "assessment_dimensions": ["effectiveness", "efficiency", "quality", "impact"],
                "scoring_method": "weighted_criteria",
                "validation_approach": "evidence_based"
            }
        
        # 基于复杂度添加处理指导
        complexity = task_features.get("complexity_level", "medium")
        if complexity in ["complex", "expert"]:
            enhancements["complexity_handling"] = {
                "decomposition_strategy": "hierarchical_breakdown",
                "collaboration_mode": "multi_expert_consultation",
                "validation_level": "rigorous_review"
            }
        
        # 基于所需角色添加协作指导
        required_roles = task_features.get("required_roles", [])
        if len(required_roles) > 3:
            enhancements["collaboration_guidance"] = {
                "coordination_approach": "structured_discussion",
                "consensus_method": "weighted_voting",
                "conflict_resolution": "evidence_based_arbitration"
            }
        
        return enhancements