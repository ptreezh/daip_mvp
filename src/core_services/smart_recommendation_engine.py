"""@Time: 2025-08-03
@Author: DAIP-LIVE
@File: smart_recommendation_engine.py
@Description: V0.3.4 智能推荐引擎 - 基于用户兴趣和讨论上下文的知识推荐算法
"""

import asyncio
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.knowledge_retrieval_service import KnowledgeRetrievalService
from ..core_services.memory_agent import MemAgent


class RecommendationType(Enum):
    """推荐类型枚举"""
    CONTENT_BASED = "content_based"  # 基于内容的推荐
    COLLABORATIVE = "collaborative"  # 协同过滤推荐
    KNOWLEDGE_GRAPH = "knowledge_graph"  # 知识图谱推荐
    HYBRID = "hybrid"  # 混合推荐


@dataclass
class UserInterest:
    """用户兴趣模型"""
    user_id: str
    interests: dict[str, float]  # 兴趣领域及权重
    interaction_history: list[dict]  # 交互历史
    knowledge_preferences: dict[str, float]  # 知识类型偏好
    last_updated: datetime
    expertise_level: dict[str, float]  # 不同领域的专业程度


@dataclass
class ContextFeatures:
    """上下文特征"""
    current_topic: str
    session_type: str
    time_of_day: str
    discussion_depth: int
    participant_roles: list[str]
    recent_keywords: list[str]
    knowledge_domain: str


@dataclass
class KnowledgeItem:
    """知识项"""
    id: str
    title: str
    content: str
    type: str
    domain: str
    confidence: float
    created_time: datetime
    tags: list[str]
    metadata: dict[str, Any]


@dataclass
class RecommendationResult:
    """推荐结果"""
    knowledge_items: list[KnowledgeItem]
    recommendation_scores: list[float]
    recommendation_types: list[RecommendationType]
    explanation: str
    confidence: float
    metadata: dict[str, Any]


class UserInterestModel:
    """用户兴趣模型管理器"""
    
    def __init__(self, memory_agent: MemAgent):
        self.memory_agent = memory_agent
        self.interest_decay_rate = 0.95  # 兴趣衰减率
        self.min_interest_threshold = 0.1  # 最小兴趣阈值
        
    async def get_user_interests(self, user_id: str) -> UserInterest:
        """获取用户兴趣模型"""
        try:
            # 从记忆中获取用户兴趣数据
            memory_key = f"user_interests_{user_id}"
            interest_data = await self.memory_agent.retrieve_memory(memory_key)
            
            if interest_data:
                user_interest = UserInterest(**interest_data)
                # 更新兴趣权重（衰减）
                user_interest.interests = self._decay_interests(user_interest.interests)
                return user_interest
            else:
                # 创建新的用户兴趣模型
                return await self._create_default_interest_model(user_id)
                
        except Exception as e:
            logging.error(f"获取用户兴趣模型失败: {e}")
            return await self._create_default_interest_model(user_id)
    
    async def update_user_interests(self, user_id: str, interaction_data: dict):
        """更新用户兴趣模型"""
        try:
            user_interest = await self.get_user_interests(user_id)
            
            # 基于交互数据更新兴趣
            topic = interaction_data.get('topic', '')
            interaction_type = interaction_data.get('type', '')
            engagement_score = interaction_data.get('engagement_score', 0.5)
            
            if topic:
                # 更新兴趣权重
                current_weight = user_interest.interests.get(topic, 0.0)
                user_interest.interests[topic] = min(1.0, current_weight + engagement_score * 0.1)
                
                # 更新交互历史
                user_interest.interaction_history.append({
                    'topic': topic,
                    'type': interaction_type,
                    'timestamp': datetime.now().isoformat(),
                    'engagement_score': engagement_score
                })
                
                # 限制历史记录长度
                if len(user_interest.interaction_history) > 100:
                    user_interest.interaction_history = user_interest.interaction_history[-100:]
                
                user_interest.last_updated = datetime.now()
                
                # 保存更新后的兴趣模型
                await self.memory_agent.store_memory(
                    f"user_interests_{user_id}",
                    user_interest.__dict__
                )
                
        except Exception as e:
            logging.error(f"更新用户兴趣模型失败: {e}")
    
    def _decay_interests(self, interests: dict[str, float]) -> dict[str, float]:
        """兴趣衰减处理"""
        decayed_interests = {}
        for topic, weight in interests.items():
            decayed_weight = weight * self.interest_decay_rate
            if decayed_weight > self.min_interest_threshold:
                decayed_interests[topic] = decayed_weight
        return decayed_interests
    
    async def _create_default_interest_model(self, user_id: str) -> UserInterest:
        """创建默认用户兴趣模型"""
        return UserInterest(
            user_id=user_id,
            interests={},
            interaction_history=[],
            knowledge_preferences={
                'FACT': 0.7,
                'CONCEPT': 0.8,
                'MEMORY': 0.6,
                'WIKI': 0.9
            },
            last_updated=datetime.now(),
            expertise_level={}
        )


class ContextAnalyzer:
    """上下文分析器"""
    
    def __init__(self):
        self.topic_extractor = TopicExtractor()
        self.keyword_extractor = KeywordExtractor()
        
    async def extract_features(self, context: dict) -> ContextFeatures:
        """提取上下文特征"""
        try:
            # 分析当前话题
            current_topic = context.get('topic', '')
            session_type = context.get('session_type', 'general')
            
            # 提取关键词
            recent_keywords = self.keyword_extractor.extract(context.get('recent_content', ''))
            
            # 分析讨论深度
            discussion_depth = self._analyze_discussion_depth(context)
            
            # 识别知识领域
            knowledge_domain = await self.topic_extractor.classify_domain(current_topic)
            
            # 获取时间信息
            time_of_day = self._get_time_of_day()
            
            return ContextFeatures(
                current_topic=current_topic,
                session_type=session_type,
                time_of_day=time_of_day,
                discussion_depth=discussion_depth,
                participant_roles=context.get('participant_roles', []),
                recent_keywords=recent_keywords,
                knowledge_domain=knowledge_domain
            )
            
        except Exception as e:
            logging.error(f"上下文特征提取失败: {e}")
            return ContextFeatures(
                current_topic="",
                session_type="general",
                time_of_day="morning",
                discussion_depth=0,
                participant_roles=[],
                recent_keywords=[],
                knowledge_domain="general"
            )
    
    def _analyze_discussion_depth(self, context: dict) -> int:
        """分析讨论深度"""
        content_length = len(context.get('recent_content', ''))
        interaction_count = len(context.get('recent_interactions', []))
        
        # 简单的深度计算公式
        depth_score = min(10, (content_length // 100) + (interaction_count // 3))
        return depth_score
    
    def _get_time_of_day(self) -> str:
        """获取时间段"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 24:
            return "evening"
        else:
            return "night"


class TopicExtractor:
    """话题提取器"""
    
    def __init__(self):
        self.domain_keywords = {
            'technology': ['AI', 'machine learning', 'software', 'programming', 'data'],
            'science': ['research', 'experiment', 'theory', 'analysis', 'study'],
            'business': ['market', 'strategy', 'management', 'finance', 'investment'],
            'education': ['learning', 'teaching', 'curriculum', 'student', 'pedagogy'],
            'health': ['medical', 'healthcare', 'treatment', 'diagnosis', 'therapy']
        }
    
    async def classify_domain(self, topic: str) -> str:
        """分类知识领域"""
        if not topic:
            return "general"
            
        topic_lower = topic.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in topic_lower)
            domain_scores[domain] = score
        
        # 返回得分最高的领域
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain
        
        return "general"


class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with'
        }
    
    def extract(self, text: str) -> list[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 简单的关键词提取
        words = text.lower().split()
        keywords = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # 返回频率最高的前10个关键词
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(10)]


class HybridRecommendationStrategy:
    """混合推荐策略"""
    
    def __init__(self, knowledge_retrieval: KnowledgeRetrievalService, 
                 sskg_manager: EnhancedSSKGManager):
        self.knowledge_retrieval = knowledge_retrieval
        self.sskg_manager = sskg_manager
        self.content_weight = 0.4  # 内容推荐权重
        self.collaborative_weight = 0.3  # 协同过滤权重
        self.knowledge_graph_weight = 0.3  # 知识图谱权重
        
    async def hybrid_recommend(self, user_interests: UserInterest, 
                             context_features: ContextFeatures) -> list[KnowledgeItem]:
        """混合推荐算法"""
        try:
            # 并行执行不同推荐策略
            content_recommendations = await self._content_based_recommend(
                user_interests, context_features
            )
            collaborative_recommendations = await self._collaborative_recommend(
                user_interests, context_features
            )
            knowledge_graph_recommendations = await self._knowledge_graph_recommend(
                user_interests, context_features
            )
            
            # 合并和排序推荐结果
            final_recommendations = self._merge_and_rank_recommendations(
                content_recommendations,
                collaborative_recommendations,
                knowledge_graph_recommendations
            )
            
            return final_recommendations[:20]  # 返回前20个推荐
            
        except Exception as e:
            logging.error(f"混合推荐失败: {e}")
            return []
    
    async def _content_based_recommend(self, user_interests: UserInterest,
                                     context_features: ContextFeatures) -> list[KnowledgeItem]:
        """基于内容的推荐"""
        try:
            # 基于用户兴趣领域检索相关知识
            query_topics = list(user_interests.interests.keys())
            if not query_topics:
                query_topics = [context_features.current_topic]
            
            # 执行语义搜索
            search_results = await self.knowledge_retrieval.semantic_search(
                query=" OR ".join(query_topics),
                limit=50
            )
            
            # 根据用户兴趣权重排序
            ranked_results = []
            for result in search_results:
                relevance_score = self._calculate_content_relevance(
                    result, user_interests, context_features
                )
                ranked_results.append((result, relevance_score))
            
            ranked_results.sort(key=lambda x: x[1], reverse=True)
            return [result for result, score in ranked_results[:30]]
            
        except Exception as e:
            logging.error(f"基于内容推荐失败: {e}")
            return []
    
    async def _collaborative_recommend(self, user_interests: UserInterest,
                                     context_features: ContextFeatures) -> list[KnowledgeItem]:
        """协同过滤推荐"""
        try:
            # 基于用户历史行为和相似用户推荐
            # 这里简化实现，实际应该基于用户行为数据
            
            # 查找相似用户的知识
            similar_users = await self._find_similar_users(user_interests)
            
            if not similar_users:
                return []
            
            # 获取相似用户感兴趣的知识
            recommended_knowledge = []
            for similar_user in similar_users[:5]:  # 取前5个相似用户
                user_knowledge = await self._get_user_knowledge(similar_user)
                recommended_knowledge.extend(user_knowledge)
            
            # 去重和排序
            unique_knowledge = self._deduplicate_knowledge(recommended_knowledge)
            return unique_knowledge[:20]
            
        except Exception as e:
            logging.error(f"协同过滤推荐失败: {e}")
            return []
    
    async def _knowledge_graph_recommend(self, user_interests: UserInterest,
                                       context_features: ContextFeatures) -> list[KnowledgeItem]:
        """知识图谱推荐"""
        try:
            # 基于知识图谱的关联推荐
            current_topic = context_features.current_topic
            
            if not current_topic:
                return []
            
            # 在知识图谱中查找相关节点
            related_nodes = await self.sskg_manager.find_related_nodes(
                current_topic, 
                relation_types=['SUPPORTS', 'ELABORATES', 'IMPLIES'],
                max_depth=2
            )
            
            # 转换为知识项
            knowledge_items = []
            for node in related_nodes:
                if hasattr(node, 'properties'):
                    knowledge_item = KnowledgeItem(
                        id=node.id,
                        title=node.properties.get('title', node.id),
                        content=node.properties.get('content', ''),
                        type=node.properties.get('type', 'CONCEPT'),
                        domain=node.properties.get('domain', 'general'),
                        confidence=node.properties.get('confidence', 0.8),
                        created_time=datetime.fromisoformat(node.properties.get('created_time', datetime.now().isoformat())),
                        tags=node.properties.get('tags', []),
                        metadata=node.properties
                    )
                    knowledge_items.append(knowledge_item)
            
            return knowledge_items[:30]
            
        except Exception as e:
            logging.error(f"知识图谱推荐失败: {e}")
            return []
    
    def _calculate_content_relevance(self, knowledge_item: Any,
                                   user_interests: UserInterest,
                                   context_features: ContextFeatures) -> float:
        """计算内容相关性分数"""
        try:
            score = 0.0
            
            # 基于用户兴趣的相关性
            for interest, weight in user_interests.interests.items():
                if interest.lower() in knowledge_item.get('content', '').lower():
                    score += weight * 0.5
            
            # 基于上下文的相关性
            if context_features.knowledge_domain == knowledge_item.get('domain', ''):
                score += 0.3
            
            # 基于置信度的相关性
            confidence = knowledge_item.get('confidence', 0.5)
            score += confidence * 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            logging.error(f"计算内容相关性失败: {e}")
            return 0.0
    
    def _merge_and_rank_recommendations(self, content_results: list[KnowledgeItem],
                                     collaborative_results: list[KnowledgeItem],
                                     knowledge_graph_results: list[KnowledgeItem]) -> list[KnowledgeItem]:
        """合并和排序推荐结果"""
        try:
            # 合并所有结果
            all_results = []
            
            # 添加基于内容的推荐
            for item in content_results:
                all_results.append((item, self.content_weight, RecommendationType.CONTENT_BASED))
            
            # 添加协同过滤推荐
            for item in collaborative_results:
                all_results.append((item, self.collaborative_weight, RecommendationType.COLLABORATIVE))
            
            # 添加知识图谱推荐
            for item in knowledge_graph_results:
                all_results.append((item, self.knowledge_graph_weight, RecommendationType.KNOWLEDGE_GRAPH))
            
            # 去重
            unique_results = self._deduplicate_weighted_results(all_results)
            
            # 按权重排序
            unique_results.sort(key=lambda x: x[1], reverse=True)
            
            return [item for item, weight, rec_type in unique_results]
            
        except Exception as e:
            logging.error(f"合并推荐结果失败: {e}")
            return []
    
    def _deduplicate_knowledge(self, knowledge_items: list[KnowledgeItem]) -> list[KnowledgeItem]:
        """去重知识项"""
        seen_ids = set()
        unique_items = []
        
        for item in knowledge_items:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_items.append(item)
        
        return unique_items
    
    def _deduplicate_weighted_results(self, weighted_results: list[tuple[KnowledgeItem, float, RecommendationType]]) -> list[tuple[KnowledgeItem, float, RecommendationType]]:
        """去重加权结果"""
        item_scores = defaultdict(lambda: {'total_score': 0.0, 'types': []})
        
        for item, weight, rec_type in weighted_results:
            if item.id not in item_scores:
                item_scores[item.id] = {'total_score': 0.0, 'types': [], 'item': item}
            
            item_scores[item.id]['total_score'] += weight
            item_scores[item.id]['types'].append(rec_type)
            item_scores[item.id]['item'] = item
        
        # 转换为排序列表
        deduplicated_results = []
        for item_id, data in item_scores.items():
            deduplicated_results.append((
                data['item'], 
                data['total_score'], 
                data['types'][0]  # 取第一个推荐类型
            ))
        
        return deduplicated_results
    
    async def _find_similar_users(self, user_interests: UserInterest) -> list[str]:
        """查找相似用户"""
        # 简化实现，实际应该基于用户行为相似度计算
        return []
    
    async def _get_user_knowledge(self, user_id: str) -> list[KnowledgeItem]:
        """获取用户知识"""
        # 简化实现
        return []


class SmartRecommendationEngine:
    """智能推荐引擎主类"""
    
    def __init__(self, memory_agent: MemAgent, 
                 knowledge_retrieval: KnowledgeRetrievalService,
                 sskg_manager: EnhancedSSKGManager):
        self.user_interest_model = UserInterestModel(memory_agent)
        self.context_analyzer = ContextAnalyzer()
        self.recommendation_strategy = HybridRecommendationStrategy(
            knowledge_retrieval, sskg_manager
        )
        self.logger = logging.getLogger(__name__)
    
    async def recommend_knowledge(self, user_id: str, context: dict) -> RecommendationResult:
        """基于用户画像和上下文的智能推荐"""
        try:
            # 获取用户兴趣模型
            user_interests = await self.user_interest_model.get_user_interests(user_id)
            
            # 提取上下文特征
            context_features = await self.context_analyzer.extract_features(context)
            
            # 执行混合推荐
            recommended_items = await self.recommendation_strategy.hybrid_recommend(
                user_interests, context_features
            )
            
            # 计算推荐分数
            recommendation_scores = self._calculate_recommendation_scores(
                recommended_items, user_interests, context_features
            )
            
            # 生成推荐解释
            explanation = self._generate_explanation(
                recommended_items, user_interests, context_features
            )
            
            # 计算整体置信度
            confidence = self._calculate_confidence(
                recommended_items, recommendation_scores
            )
            
            return RecommendationResult(
                knowledge_items=recommended_items,
                recommendation_scores=recommendation_scores,
                recommendation_types=[RecommendationType.HYBRID] * len(recommended_items),
                explanation=explanation,
                confidence=confidence,
                metadata={
                    'user_interests': user_interests.interests,
                    'context_features': context_features.__dict__,
                    'recommendation_time': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"智能推荐失败: {e}")
            return RecommendationResult(
                knowledge_items=[],
                recommendation_scores=[],
                recommendation_types=[],
                explanation="推荐系统暂时不可用",
                confidence=0.0,
                metadata={'error': str(e)}
            )
    
    async def update_user_interaction(self, user_id: str, interaction_data: dict):
        """更新用户交互数据"""
        try:
            await self.user_interest_model.update_user_interests(user_id, interaction_data)
        except Exception as e:
            self.logger.error(f"更新用户交互数据失败: {e}")
    
    def _calculate_recommendation_scores(self, items: list[KnowledgeItem],
                                       user_interests: UserInterest,
                                       context_features: ContextFeatures) -> list[float]:
        """计算推荐分数"""
        scores = []
        for item in items:
            score = 0.0
            
            # 基于用户兴趣的分数
            for interest, weight in user_interests.interests.items():
                if interest.lower() in item.content.lower():
                    score += weight * 0.4
            
            # 基于上下文的分数
            if context_features.knowledge_domain == item.domain:
                score += 0.3
            
            # 基于知识质量的分数
            score += item.confidence * 0.2
            
            # 基于时间新鲜度的分数
            days_old = (datetime.now() - item.created_time).days
            freshness_score = max(0.0, 1.0 - days_old / 365.0)
            score += freshness_score * 0.1
            
            scores.append(min(1.0, score))
        
        return scores
    
    def _generate_explanation(self, items: list[KnowledgeItem],
                            user_interests: UserInterest,
                            context_features: ContextFeatures) -> str:
        """生成推荐解释"""
        if not items:
            return "暂无推荐内容"
        
        # 分析推荐的主要因素
        top_interests = sorted(user_interests.interests.items(), 
                              key=lambda x: x[1], reverse=True)[:3]
        
        explanation_parts = []
        
        if top_interests:
            explanation_parts.append(f"基于您的兴趣领域：{', '.join([i[0] for i in top_interests])}")
        
        if context_features.current_topic:
            explanation_parts.append(f"当前讨论话题：{context_features.current_topic}")
        
        if context_features.knowledge_domain != "general":
            explanation_parts.append(f"相关领域：{context_features.knowledge_domain}")
        
        return "；".join(explanation_parts)
    
    def _calculate_confidence(self, items: list[KnowledgeItem], scores: list[float]) -> float:
        """计算推荐置信度"""
        if not items:
            return 0.0
        
        # 基于分数分布计算置信度
        avg_score = np.mean(scores)
        score_std = np.std(scores)
        
        # 分数越高、分布越集中，置信度越高
        confidence = avg_score * (1.0 - score_std)
        
        return max(0.0, min(1.0, confidence))


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    memory_agent = MemAgent()
    knowledge_retrieval = KnowledgeRetrievalService()
    sskg_manager = EnhancedSSKGManager()
    
    # 创建推荐引擎
    recommendation_engine = SmartRecommendationEngine(
        memory_agent, knowledge_retrieval, sskg_manager
    )
    
    # 模拟用户上下文
    user_context = {
        'topic': '机器学习在教育中的应用',
        'session_type': 'academic_research',
        'recent_content': '我们正在讨论AI技术在教育领域的应用，包括个性化学习、智能评估等方面。',
        'participant_roles': ['researcher', 'educator'],
        'recent_interactions': [
            {'type': 'search', 'query': 'AI education'},
            {'type': 'view', 'item_id': 'ml_education_001'}
        ]
    }
    
    # 获取推荐
    user_id = "user_001"
    recommendation_result = await recommendation_engine.recommend_knowledge(
        user_id, user_context
    )
    
    print(f"推荐结果数量: {len(recommendation_result.knowledge_items)}")
    print(f"推荐置信度: {recommendation_result.confidence:.2f}")
    print(f"推荐解释: {recommendation_result.explanation}")
    
    # 更新用户交互
    interaction_data = {
        'topic': '机器学习在教育中的应用',
        'type': 'view',
        'engagement_score': 0.8,
        'item_ids': [item.id for item in recommendation_result.knowledge_items[:3]]
    }
    
    await recommendation_engine.update_user_interaction(user_id, interaction_data)


if __name__ == "__main__":
    asyncio.run(example_usage())