"""
@Time: 2025-08-03
@Author: DAIP-LIVE
@File: knowledge_retrieval_optimizer.py
@Description: V0.3.4 知识检索优化器 - 多级缓存、查询优化和性能提升
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
import functools
from collections import defaultdict, OrderedDict, deque
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

from ..core_services.knowledge_retrieval_service import KnowledgeRetrievalService
from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.memory_agent import MemAgent
from ..virtual_role_chat.sskg.models import KnowledgeFact, KnowledgeQuery, SearchResult


class CacheLevel(Enum):
    """缓存级别"""
    L1_MEMORY = "l1_memory"  # 内存缓存
    L2_REDIS = "l2_redis"    # Redis缓存
    L3_DISK = "l3_disk"      # 磁盘缓存


class OptimizationStrategy(Enum):
    """优化策略"""
    QUERY_CACHING = "query_caching"          # 查询缓存
    SEMANTIC_INDEXING = "semantic_indexing"   # 语义索引
    PARALLEL_SEARCH = "parallel_search"       # 并行搜索
    RESULT_RANKING = "result_ranking"         # 结果排序优化
    CONTEXT_AWARE = "context_aware"           # 上下文感知
    ADAPTIVE_FILTERING = "adaptive_filtering"  # 自适应过滤


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    timestamp: datetime
    ttl: int
    access_count: int
    size_bytes: int
    metadata: Dict[str, Any] = None


@dataclass
class QueryMetrics:
    """查询指标"""
    query_id: str
    query_text: str
    execution_time: float
    cache_hit: bool
    result_count: int
    optimization_applied: List[str]
    timestamp: datetime


@dataclass
class PerformanceMetrics:
    """性能指标"""
    total_queries: int
    cache_hit_rate: float
    average_response_time: float
    throughput_qps: float
    memory_usage_mb: float
    error_rate: float
    top_queries: List[Dict[str, Any]]
    optimization_stats: Dict[str, Dict[str, float]]


class KnowledgeRetrievalOptimizer:
    """知识检索优化器"""
    
    def __init__(self, knowledge_retrieval: KnowledgeRetrievalService,
                 sskg_manager: EnhancedSSKGManager,
                 memory_agent: MemAgent):
        self.knowledge_retrieval = knowledge_retrieval
        self.sskg_manager = sskg_manager
        self.memory_agent = memory_agent
        self.logger = logging.getLogger(__name__)
        
        # 多级缓存
        self.l1_cache = OrderedDict()  # LRU缓存
        self.l2_cache = {}             # 内存缓存
        self.l3_cache_path = "data/cache/knowledge_cache.pkl"
        
        # 缓存配置
        self.l1_cache_size = 1000     # L1缓存条目数
        self.l2_cache_size = 5000      # L2缓存条目数
        self.cache_ttl = 3600          # 缓存过期时间（秒）
        
        # 性能监控
        self.query_metrics = deque(maxlen=10000)
        self.performance_stats = defaultdict(lambda: {
            'count': 0, 'total_time': 0.0, 'cache_hits': 0
        })
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 语义索引
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.semantic_index = None
        self.index_built = False
        
        # 查询优化器
        self.query_optimizer = QueryOptimizer()
        self.result_ranker = ResultRanker()
        
        # 启动后台任务
        self._start_background_tasks()
    
    async def optimized_search(self, 
                             query: str,
                             filters: Dict[str, Any] = None,
                             limit: int = 10,
                             optimization_strategies: List[OptimizationStrategy] = None) -> List[SearchResult]:
        """优化搜索"""
        if optimization_strategies is None:
            optimization_strategies = [
                OptimizationStrategy.QUERY_CACHING,
                OptimizationStrategy.SEMANTIC_INDEXING,
                OptimizationStrategy.RESULT_RANKING
            ]
        
        query_id = self._generate_query_id(query)
        start_time = time.time()
        cache_hit = False
        applied_optimizations = []
        
        try:
            # 1. 查询缓存优化
            if OptimizationStrategy.QUERY_CACHING in optimization_strategies:
                cached_result = await self._get_cached_result(query, filters, limit)
                if cached_result:
                    cache_hit = True
                    applied_optimizations.append("query_caching")
                    self._record_query_metrics(
                        query_id, query, time.time() - start_time, 
                        cache_hit, len(cached_result), applied_optimizations
                    )
                    return cached_result
            
            # 2. 查询优化
            optimized_query = self.query_optimizer.optimize(query, filters)
            applied_optimizations.append("query_optimization")
            
            # 3. 并行搜索
            if OptimizationStrategy.PARALLEL_SEARCH in optimization_strategies:
                search_tasks = []
                
                # 语义搜索
                search_tasks.append(
                    self.knowledge_retrieval.semantic_search(
                        optimized_query.query_text, 
                        limit=limit * 2
                    )
                )
                
                # 关键词搜索
                search_tasks.append(
                    self.knowledge_retrieval.keyword_search(
                        optimized_query.query_text,
                        limit=limit * 2
                    )
                )
                
                # 图谱搜索
                search_tasks.append(
                    self.sskg_manager.find_related_nodes(
                        optimized_query.query_text,
                        max_depth=2
                    )
                )
                
                # 并行执行
                results = await asyncio.gather(*search_tasks, return_exceptions=True)
                applied_optimizations.append("parallel_search")
                
                # 合并结果
                merged_results = self._merge_search_results(results)
                
            else:
                # 串行搜索
                merged_results = await self.knowledge_retrieval.semantic_search(
                    optimized_query.query_text, limit=limit * 2
                )
            
            # 4. 结果排序优化
            if OptimizationStrategy.RESULT_RANKING in optimization_strategies:
                ranked_results = self.result_ranker.rank_results(
                    merged_results, query, optimized_query
                )
                applied_optimizations.append("result_ranking")
            else:
                ranked_results = merged_results
            
            # 5. 应用过滤
            if filters:
                filtered_results = self._apply_filters(ranked_results, filters)
                applied_optimizations.append("filtering")
            else:
                filtered_results = ranked_results
            
            # 6. 限制结果数量
            final_results = filtered_results[:limit]
            
            # 7. 缓存结果
            if OptimizationStrategy.QUERY_CACHING in optimization_strategies:
                await self._cache_result(query, filters, limit, final_results)
            
            # 记录指标
            execution_time = time.time() - start_time
            self._record_query_metrics(
                query_id, query, execution_time, cache_hit, 
                len(final_results), applied_optimizations
            )
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"优化搜索失败: {e}")
            # 降级到基础搜索
            fallback_results = await self.knowledge_retrieval.semantic_search(
                query, limit=limit
            )
            
            execution_time = time.time() - start_time
            self._record_query_metrics(
                query_id, query, execution_time, False, 
                len(fallback_results), ["fallback"]
            )
            
            return fallback_results
    
    async def build_semantic_index(self, knowledge_facts: List[KnowledgeFact] = None):
        """构建语义索引"""
        try:
            if knowledge_facts is None:
                knowledge_facts = await self.knowledge_retrieval.get_recent_knowledge(10000)
            
            if not knowledge_facts:
                self.logger.warning("没有知识事实用于构建索引")
                return
            
            # 准备文档
            documents = [fact.content for fact in knowledge_facts]
            
            # 构建TF-IDF索引
            self.semantic_index = self.tfidf_vectorizer.fit_transform(documents)
            self.index_built = True
            
            # 保存索引到缓存
            await self._cache_semantic_index()
            
            self.logger.info(f"语义索引构建完成，包含 {len(knowledge_facts)} 个文档")
            
        except Exception as e:
            self.logger.error(f"构建语义索引失败: {e}")
    
    async def semantic_similarity_search(self, 
                                       query: str,
                                       threshold: float = 0.3,
                                       limit: int = 10) -> List[SearchResult]:
        """语义相似性搜索"""
        try:
            if not self.index_built:
                await self.build_semantic_index()
            
            if not self.index_built:
                return []
            
            # 向量化查询
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # 计算相似度
            similarities = cosine_similarity(query_vector, self.semantic_index)[0]
            
            # 筛选结果
            similar_indices = np.where(similarities >= threshold)[0]
            sorted_indices = similar_indices[np.argsort(similarities[similar_indices])[::-1]]
            
            # 获取结果
            results = []
            for idx in sorted_indices[:limit]:
                similarity_score = similarities[idx]
                
                # 这里需要根据索引获取实际的知识事实
                # 简化实现
                result = SearchResult(
                    item=KnowledgeFact(
                        content=f"Semantic result {idx}",
                        source="semantic_index",
                        confidence=similarity_score
                    ),
                    relevance_score=similarity_score,
                    match_type="semantic"
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"语义相似性搜索失败: {e}")
            return []
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        try:
            # 计算基础指标
            total_queries = len(self.query_metrics)
            
            if total_queries == 0:
                return PerformanceMetrics(
                    total_queries=0,
                    cache_hit_rate=0.0,
                    average_response_time=0.0,
                    throughput_qps=0.0,
                    memory_usage_mb=0.0,
                    error_rate=0.0,
                    top_queries=[],
                    optimization_stats={}
                )
            
            cache_hits = sum(1 for m in self.query_metrics if m.cache_hit)
            cache_hit_rate = cache_hits / total_queries
            
            avg_response_time = sum(m.execution_time for m in self.query_metrics) / total_queries
            
            # 计算吞吐量（最近1小时）
            recent_queries = [m for m in self.query_metrics 
                            if m.timestamp > datetime.now() - timedelta(hours=1)]
            throughput_qps = len(recent_queries) / 3600.0 if recent_queries else 0.0
            
            # 计算内存使用
            memory_usage = self._calculate_memory_usage()
            
            # 计算错误率
            error_count = sum(1 for m in self.query_metrics if m.execution_time > 10.0)
            error_rate = error_count / total_queries
            
            # 热门查询
            query_counts = defaultdict(int)
            for m in self.query_metrics:
                query_counts[m.query_text] += 1
            
            top_queries = [
                {"query": query, "count": count}
                for query, count in sorted(query_counts.items(), 
                                         key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # 优化统计
            optimization_stats = {}
            for m in self.query_metrics:
                for opt in m.optimization_applied:
                    if opt not in optimization_stats:
                        optimization_stats[opt] = {"count": 0, "avg_time": 0.0}
                    optimization_stats[opt]["count"] += 1
                    optimization_stats[opt]["avg_time"] += m.execution_time
            
            # 计算平均时间
            for opt_stats in optimization_stats.values():
                if opt_stats["count"] > 0:
                    opt_stats["avg_time"] /= opt_stats["count"]
            
            return PerformanceMetrics(
                total_queries=total_queries,
                cache_hit_rate=cache_hit_rate,
                average_response_time=avg_response_time,
                throughput_qps=throughput_qps,
                memory_usage_mb=memory_usage,
                error_rate=error_rate,
                top_queries=top_queries,
                optimization_stats=optimization_stats
            )
            
        except Exception as e:
            self.logger.error(f"获取性能指标失败: {e}")
            return PerformanceMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, [], {})
    
    async def optimize_cache(self):
        """优化缓存"""
        try:
            # 清理过期缓存
            current_time = datetime.now()
            
            # 清理L1缓存
            expired_keys = []
            for key, entry in self.l1_cache.items():
                if (current_time - entry.timestamp).total_seconds() > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.l1_cache[key]
            
            # 清理L2缓存
            expired_keys = []
            for key, entry in self.l2_cache.items():
                if (current_time - entry.timestamp).total_seconds() > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.l2_cache[key]
            
            # 保存L3缓存
            await self._save_l3_cache()
            
            self.logger.info(f"缓存优化完成，清理了 {len(expired_keys)} 个过期条目")
            
        except Exception as e:
            self.logger.error(f"缓存优化失败: {e}")
    
    async def _get_cached_result(self, query: str, filters: Dict[str, Any], limit: int) -> Optional[List[SearchResult]]:
        """获取缓存结果"""
        try:
            cache_key = self._generate_cache_key(query, filters, limit)
            
            # L1缓存
            if cache_key in self.l1_cache:
                entry = self.l1_cache[cache_key]
                if (datetime.now() - entry.timestamp).total_seconds() < entry.ttl:
                    entry.access_count += 1
                    # 更新LRU
                    self.l1_cache.move_to_end(cache_key)
                    return entry.value
                else:
                    del self.l1_cache[cache_key]
            
            # L2缓存
            if cache_key in self.l2_cache:
                entry = self.l2_cache[cache_key]
                if (datetime.now() - entry.timestamp).total_seconds() < entry.ttl:
                    entry.access_count += 1
                    # 提升到L1缓存
                    self._add_to_l1_cache(cache_key, entry)
                    return entry.value
                else:
                    del self.l2_cache[cache_key]
            
            # L3缓存
            return await self._get_l3_cache(cache_key)
            
        except Exception as e:
            self.logger.error(f"获取缓存结果失败: {e}")
            return None
    
    async def _cache_result(self, query: str, filters: Dict[str, Any], limit: int, results: List[SearchResult]):
        """缓存结果"""
        try:
            cache_key = self._generate_cache_key(query, filters, limit)
            
            # 序列化结果
            serialized_results = self._serialize_results(results)
            
            # 创建缓存条目
            entry = CacheEntry(
                key=cache_key,
                value=serialized_results,
                timestamp=datetime.now(),
                ttl=self.cache_ttl,
                access_count=1,
                size_bytes=len(pickle.dumps(serialized_results))
            )
            
            # 添加到L1缓存
            self._add_to_l1_cache(cache_key, entry)
            
            # 添加到L2缓存
            self._add_to_l2_cache(cache_key, entry)
            
        except Exception as e:
            self.logger.error(f"缓存结果失败: {e}")
    
    def _add_to_l1_cache(self, key: str, entry: CacheEntry):
        """添加到L1缓存"""
        self.l1_cache[key] = entry
        
        # 如果超过大小限制，移除最旧的
        if len(self.l1_cache) > self.l1_cache_size:
            self.l1_cache.popitem(last=False)
    
    def _add_to_l2_cache(self, key: str, entry: CacheEntry):
        """添加到L2缓存"""
        self.l2_cache[key] = entry
        
        # 如果超过大小限制，移除访问次数最少的
        if len(self.l2_cache) > self.l2_cache_size:
            min_access_key = min(self.l2_cache.keys(), 
                               key=lambda k: self.l2_cache[k].access_count)
            del self.l2_cache[min_access_key]
    
    async def _get_l3_cache(self, key: str) -> Optional[List[SearchResult]]:
        """获取L3缓存"""
        try:
            if not hasattr(self, '_l3_cache'):
                await self._load_l3_cache()
            
            if key in self._l3_cache:
                entry = self._l3_cache[key]
                if (datetime.now() - entry.timestamp).total_seconds() < entry.ttl:
                    entry.access_count += 1
                    return entry.value
                else:
                    del self._l3_cache[key]
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取L3缓存失败: {e}")
            return None
    
    async def _load_l3_cache(self):
        """加载L3缓存"""
        try:
            import os
            if os.path.exists(self.l3_cache_path):
                with open(self.l3_cache_path, 'rb') as f:
                    self._l3_cache = pickle.load(f)
            else:
                self._l3_cache = {}
        except Exception as e:
            self.logger.error(f"加载L3缓存失败: {e}")
            self._l3_cache = {}
    
    async def _save_l3_cache(self):
        """保存L3缓存"""
        try:
            import os
            os.makedirs(os.path.dirname(self.l3_cache_path), exist_ok=True)
            
            if hasattr(self, '_l3_cache'):
                with open(self.l3_cache_path, 'wb') as f:
                    pickle.dump(self._l3_cache, f)
        except Exception as e:
            self.logger.error(f"保存L3缓存失败: {e}")
    
    def _generate_cache_key(self, query: str, filters: Dict[str, Any], limit: int) -> str:
        """生成缓存键"""
        cache_data = {
            'query': query,
            'filters': filters or {},
            'limit': limit
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def _generate_query_id(self, query: str) -> str:
        """生成查询ID"""
        return hashlib.md5(f"{query}_{time.time()}".encode()).hexdigest()
    
    def _record_query_metrics(self, query_id: str, query: str, execution_time: float,
                            cache_hit: bool, result_count: int, optimizations: List[str]):
        """记录查询指标"""
        metrics = QueryMetrics(
            query_id=query_id,
            query_text=query,
            execution_time=execution_time,
            cache_hit=cache_hit,
            result_count=result_count,
            optimization_applied=optimizations,
            timestamp=datetime.now()
        )
        
        self.query_metrics.append(metrics)
        
        # 更新统计信息
        for opt in optimizations:
            self.performance_stats[opt]['count'] += 1
            self.performance_stats[opt]['total_time'] += execution_time
            if cache_hit:
                self.performance_stats[opt]['cache_hits'] += 1
    
    def _merge_search_results(self, results: List) -> List[SearchResult]:
        """合并搜索结果"""
        try:
            merged = []
            seen_ids = set()
            
            for result in results:
                if isinstance(result, Exception):
                    continue
                
                # 处理不同类型的搜索结果
                if hasattr(result, '__iter__'):
                    for item in result:
                        if hasattr(item, 'id'):
                            if item.id not in seen_ids:
                                merged.append(item)
                                seen_ids.add(item.id)
                        else:
                            merged.append(item)
                else:
                    merged.append(result)
            
            return merged
            
        except Exception as e:
            self.logger.error(f"合并搜索结果失败: {e}")
            return []
    
    def _apply_filters(self, results: List[SearchResult], filters: Dict[str, Any]) -> List[SearchResult]:
        """应用过滤器"""
        try:
            filtered = results
            
            # 按置信度过滤
            if 'min_confidence' in filters:
                min_confidence = filters['min_confidence']
                filtered = [r for r in filtered if r.item.confidence >= min_confidence]
            
            # 按领域过滤
            if 'domain' in filters:
                domain = filters['domain']
                filtered = [r for r in filtered if r.item.domain == domain]
            
            # 按时间范围过滤
            if 'start_time' in filters or 'end_time' in filters:
                start_time = filters.get('start_time')
                end_time = filters.get('end_time')
                
                filtered = [r for r in filtered if self._time_in_range(
                    r.item.timestamp, start_time, end_time
                )]
            
            return filtered
            
        except Exception as e:
            self.logger.error(f"应用过滤器失败: {e}")
            return results
    
    def _time_in_range(self, timestamp: datetime, start_time: datetime, end_time: datetime) -> bool:
        """检查时间是否在范围内"""
        if start_time and timestamp < start_time:
            return False
        if end_time and timestamp > end_time:
            return False
        return True
    
    def _serialize_results(self, results: List[SearchResult]) -> Any:
        """序列化结果"""
        try:
            return [self._serialize_result(r) for r in results]
        except Exception:
            return results
    
    def _serialize_result(self, result: SearchResult) -> Dict[str, Any]:
        """序列化单个结果"""
        try:
            return {
                'item': {
                    'id': result.item.id,
                    'content': result.item.content,
                    'source': result.item.source,
                    'confidence': result.item.confidence,
                    'timestamp': result.item.timestamp.isoformat()
                },
                'relevance_score': result.relevance_score,
                'match_type': result.match_type
            }
        except Exception:
            return str(result)
    
    def _calculate_memory_usage(self) -> float:
        """计算内存使用量"""
        try:
            import sys
            total_size = 0
            
            # L1缓存大小
            total_size += sys.getsizeof(self.l1_cache)
            
            # L2缓存大小
            total_size += sys.getsizeof(self.l2_cache)
            
            # 语义索引大小
            if self.semantic_index is not None:
                total_size += self.semantic_index.data.nbytes
            
            return total_size / (1024 * 1024)  # 转换为MB
            
        except Exception:
            return 0.0
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 缓存清理任务
        def cache_cleanup_task():
            while True:
                time.sleep(300)  # 5分钟清理一次
                try:
                    asyncio.run(self.optimize_cache())
                except Exception as e:
                    self.logger.error(f"后台缓存清理失败: {e}")
        
        # 启动后台线程
        cleanup_thread = threading.Thread(target=cache_cleanup_task, daemon=True)
        cleanup_thread.start()
    
    async def _cache_semantic_index(self):
        """缓存语义索引"""
        try:
            if self.semantic_index is not None:
                cache_data = {
                    'index': self.semantic_index,
                    'vectorizer': self.tfidf_vectorizer,
                    'timestamp': datetime.now().isoformat()
                }
                
                cache_key = "semantic_index"
                entry = CacheEntry(
                    key=cache_key,
                    value=cache_data,
                    timestamp=datetime.now(),
                    ttl=86400,  # 24小时
                    access_count=1,
                    size_bytes=len(pickle.dumps(cache_data))
                )
                
                self._add_to_l2_cache(cache_key, entry)
                
        except Exception as e:
            self.logger.error(f"缓存语义索引失败: {e}")


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize(self, query: str, filters: Dict[str, Any] = None) -> Any:
        """优化查询"""
        try:
            # 创建优化后的查询对象
            optimized_query = OptimizedQuery(
                original_query=query,
                query_text=self._optimize_query_text(query),
                filters=self._optimize_filters(filters),
                expansion_terms=self._expand_query_terms(query),
                weight_factors=self._calculate_weight_factors(query)
            )
            
            return optimized_query
            
        except Exception as e:
            self.logger.error(f"查询优化失败: {e}")
            return OptimizedQuery(query, query, filters or {}, [], {})
    
    def _optimize_query_text(self, query: str) -> str:
        """优化查询文本"""
        # 移除停用词
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with'}
        words = [word for word in query.split() if word.lower() not in stop_words]
        
        # 提取关键词
        keywords = [word for word in words if len(word) > 2]
        
        return ' '.join(keywords)
    
    def _optimize_filters(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """优化过滤器"""
        if filters is None:
            return {}
        
        optimized = filters.copy()
        
        # 移除无效的过滤器
        for key in list(optimized.keys()):
            if optimized[key] is None or optimized[key] == '':
                del optimized[key]
        
        return optimized
    
    def _expand_query_terms(self, query: str) -> List[str]:
        """扩展查询词"""
        # 简化的同义词扩展
        expansion_map = {
            'ai': ['artificial intelligence', 'machine learning'],
            'ml': ['machine learning'],
            'dl': ['deep learning'],
            'nlp': ['natural language processing']
        }
        
        expanded = []
        words = query.lower().split()
        
        for word in words:
            if word in expansion_map:
                expanded.extend(expansion_map[word])
        
        return expanded
    
    def _calculate_weight_factors(self, query: str) -> Dict[str, float]:
        """计算权重因子"""
        words = query.split()
        
        factors = {
            'title_weight': 0.3,
            'content_weight': 0.5,
            'tag_weight': 0.2
        }
        
        # 根据查询长度调整权重
        if len(words) > 5:
            factors['content_weight'] = 0.6
            factors['title_weight'] = 0.3
            factors['tag_weight'] = 0.1
        elif len(words) < 3:
            factors['content_weight'] = 0.4
            factors['title_weight'] = 0.4
            factors['tag_weight'] = 0.2
        
        return factors


class ResultRanker:
    """结果排序器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def rank_results(self, results: List[SearchResult], query: str, 
                    optimized_query: Any) -> List[SearchResult]:
        """排序结果"""
        try:
            if not results:
                return results
            
            # 计算综合分数
            scored_results = []
            for result in results:
                score = self._calculate_combined_score(result, query, optimized_query)
                scored_results.append((result, score))
            
            # 按分数排序
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            return [result for result, score in scored_results]
            
        except Exception as e:
            self.logger.error(f"结果排序失败: {e}")
            return results
    
    def _calculate_combined_score(self, result: SearchResult, query: str, 
                                optimized_query: Any) -> float:
        """计算综合分数"""
        score = 0.0
        
        # 基础相关性分数
        score += result.relevance_score * 0.4
        
        # 置信度分数
        score += result.item.confidence * 0.3
        
        # 时间新鲜度分数
        age_days = (datetime.now() - result.item.timestamp).days
        freshness_score = max(0.0, 1.0 - age_days / 365.0)
        score += freshness_score * 0.2
        
        # 访问频率分数
        access_score = min(1.0, result.item.access_count / 10.0)
        score += access_score * 0.1
        
        return score


@dataclass
class OptimizedQuery:
    """优化后的查询"""
    original_query: str
    query_text: str
    filters: Dict[str, Any]
    expansion_terms: List[str]
    weight_factors: Dict[str, float]


# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化组件
    knowledge_retrieval = KnowledgeRetrievalService()
    sskg_manager = EnhancedSSKGManager()
    memory_agent = MemAgent()
    
    # 创建检索优化器
    optimizer = KnowledgeRetrievalOptimizer(
        knowledge_retrieval, sskg_manager, memory_agent
    )
    
    # 构建语义索引
    await optimizer.build_semantic_index()
    
    # 优化搜索
    results = await optimizer.optimized_search(
        query="机器学习在教育中的应用",
        filters={"domain": "education", "min_confidence": 0.7},
        limit=10,
        optimization_strategies=[
            OptimizationStrategy.QUERY_CACHING,
            OptimizationStrategy.PARALLEL_SEARCH,
            OptimizationStrategy.RESULT_RANKING
        ]
    )
    
    print(f"搜索结果数量: {len(results)}")
    
    # 获取性能指标
    metrics = await optimizer.get_performance_metrics()
    print(f"缓存命中率: {metrics.cache_hit_rate:.2f}")
    print(f"平均响应时间: {metrics.average_response_time:.3f}秒")
    
    # 语义相似性搜索
    similar_results = await optimizer.semantic_similarity_search(
        query="深度学习算法",
        threshold=0.3,
        limit=5
    )
    
    print(f"语义相似结果: {len(similar_results)}")


if __name__ == "__main__":
    asyncio.run(example_usage())