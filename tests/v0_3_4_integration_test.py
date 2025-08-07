"""
@Time: 2025-08-03
@Author: DAIP-LIVE
@File: v0_3_4_integration_test.py
@Description: V0.3.4 知识检索和可视化系统集成测试
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any
from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch

# 导入V0.3.4组件
from src.core_services.smart_recommendation_engine import SmartRecommendationEngine
from src.core_services.knowledge_association_engine import KnowledgeAssociationEngine
from src.core_services.knowledge_visualization_engine import KnowledgeVisualizationEngine
from src.core_services.knowledge_retrieval_optimizer import KnowledgeRetrievalOptimizer
from src.core_services.knowledge_history_tracker import KnowledgeHistoryTracker
from src.core_services.knowledge_retrieval_service import KnowledgeRetrievalService
from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.memory_agent import MemAgent


class V0_3_4_IntegrationTest(unittest.TestCase):
    """V0.3.4集成测试"""
    
    def setUp(self):
        """测试初始化"""
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # 创建模拟组件
        self.mock_knowledge_retrieval = Mock(spec=KnowledgeRetrievalService)
        self.mock_sskg_manager = Mock(spec=EnhancedSSKGManager)
        self.mock_memory_agent = Mock(spec=MemAgent)
        
        # 创建V0.3.4组件实例
        self.recommendation_engine = SmartRecommendationEngine(
            self.mock_memory_agent,
            self.mock_knowledge_retrieval,
            self.mock_sskg_manager
        )
        
        self.association_engine = KnowledgeAssociationEngine(
            self.mock_knowledge_retrieval,
            self.mock_sskg_manager
        )
        
        self.visualization_engine = KnowledgeVisualizationEngine(
            self.mock_sskg_manager,
            self.mock_knowledge_retrieval
        )
        
        self.retrieval_optimizer = KnowledgeRetrievalOptimizer(
            self.mock_knowledge_retrieval,
            self.mock_sskg_manager,
            self.mock_memory_agent
        )
        
        self.history_tracker = KnowledgeHistoryTracker(
            self.mock_knowledge_retrieval,
            self.mock_sskg_manager,
            self.mock_memory_agent
        )
        
        # 测试数据
        self.test_knowledge_data = self._create_test_knowledge_data()
        self.test_user_context = self._create_test_user_context()
        
    def _create_test_knowledge_data(self) -> List[Dict]:
        """创建测试知识数据"""
        return [
            {
                "id": "knowledge_001",
                "title": "机器学习基础",
                "content": "机器学习是人工智能的一个分支，专注于开发能够从数据中学习的算法",
                "domain": "technology",
                "confidence": 0.9,
                "created_time": datetime.now() - timedelta(days=30),
                "tags": ["AI", "ML", "技术"],
                "metadata": {"type": "concept", "source": "academic"}
            },
            {
                "id": "knowledge_002",
                "title": "深度学习应用",
                "content": "深度学习在计算机视觉、自然语言处理等领域有广泛应用",
                "domain": "technology",
                "confidence": 0.85,
                "created_time": datetime.now() - timedelta(days=15),
                "tags": ["DL", "AI", "应用"],
                "metadata": {"type": "application", "source": "industry"}
            },
            {
                "id": "knowledge_003",
                "title": "教育技术创新",
                "content": "AI技术正在改变教育方式，包括个性化学习和智能评估",
                "domain": "education",
                "confidence": 0.8,
                "created_time": datetime.now() - timedelta(days=5),
                "tags": ["教育", "AI", "创新"],
                "metadata": {"type": "innovation", "source": "research"}
            }
        ]
    
    def _create_test_user_context(self) -> Dict:
        """创建测试用户上下文"""
        return {
            "user_id": "test_user_001",
            "topic": "机器学习在教育中的应用",
            "session_type": "academic_research",
            "recent_content": "我们正在研究AI技术在教育领域的应用前景",
            "participant_roles": ["researcher", "educator"],
            "recent_interactions": [
                {"type": "search", "query": "AI education"},
                {"type": "view", "item_id": "knowledge_001"}
            ]
        }
    
    async def test_01_smart_recommendation_engine(self):
        """测试智能推荐引擎"""
        print("\n=== 测试智能推荐引擎 ===")
        
        try:
            # 模拟依赖服务
            self.mock_memory_agent.retrieve_memory.return_value = None
            self.mock_knowledge_retrieval.semantic_search.return_value = self.test_knowledge_data
            self.mock_sskg_manager.find_related_nodes.return_value = []
            
            # 测试推荐功能
            start_time = time.time()
            recommendation_result = await self.recommendation_engine.recommend_knowledge(
                user_id="test_user_001",
                context=self.test_user_context
            )
            
            execution_time = time.time() - start_time
            
            # 验证结果
            self.assertIsNotNone(recommendation_result)
            self.assertGreater(len(recommendation_result.knowledge_items), 0)
            self.assertGreater(recommendation_result.confidence, 0.0)
            self.assertIsNotNone(recommendation_result.explanation)
            
            # 性能要求：响应时间 < 2秒
            self.assertLess(execution_time, 2.0)
            
            print(f"✓ 智能推荐测试通过")
            print(f"  - 推荐项目数: {len(recommendation_result.knowledge_items)}")
            print(f"  - 推荐置信度: {recommendation_result.confidence:.2f}")
            print(f"  - 执行时间: {execution_time:.3f}秒")
            
        except Exception as e:
            print(f"✗ 智能推荐测试失败: {e}")
            raise
    
    async def test_02_knowledge_association_engine(self):
        """测试知识关联引擎"""
        print("\n=== 测试知识关联引擎 ===")
        
        try:
            # 模拟依赖服务
            self.mock_knowledge_retrieval.semantic_search.return_value = self.test_knowledge_data
            self.mock_sskg_manager.find_related_nodes.return_value = []
            
            # 测试关联发现
            start_time = time.time()
            associations = await self.association_engine.discover_associations(
                knowledge_id="knowledge_001"
            )
            
            execution_time = time.time() - start_time
            
            # 验证结果
            self.assertIsNotNone(associations)
            self.assertIsInstance(associations, list)
            
            # 性能要求：响应时间 < 3秒
            self.assertLess(execution_time, 3.0)
            
            print(f"✓ 知识关联测试通过")
            print(f"  - 发现关联数: {len(associations)}")
            print(f"  - 执行时间: {execution_time:.3f}秒")
            
        except Exception as e:
            print(f"✗ 知识关联测试失败: {e}")
            raise
    
    async def test_03_knowledge_visualization_engine(self):
        """测试知识可视化引擎"""
        print("\n=== 测试知识可视化引擎 ===")
        
        try:
            # 模拟依赖服务
            self.mock_sskg_manager.find_related_nodes.return_value = []
            
            # 测试知识图谱生成
            start_time = time.time()
            graph_result = await self.visualization_engine.generate_knowledge_graph(
                query="机器学习",
                max_nodes=10
            )
            
            execution_time = time.time() - start_time
            
            # 验证结果
            self.assertIsNotNone(graph_result)
            self.assertIn("visualization_type", graph_result)
            self.assertIn("figure", graph_result)
            self.assertIn("stats", graph_result)
            
            # 性能要求：响应时间 < 5秒
            self.assertLess(execution_time, 5.0)
            
            print(f"✓ 知识可视化测试通过")
            print(f"  - 节点数: {graph_result['stats']['total_nodes']}")
            print(f"  - 边数: {graph_result['stats']['total_edges']}")
            print(f"  - 执行时间: {execution_time:.3f}秒")
            
        except Exception as e:
            print(f"✗ 知识可视化测试失败: {e}")
            raise
    
    async def test_04_knowledge_retrieval_optimizer(self):
        """测试知识检索优化器"""
        print("\n=== 测试知识检索优化器 ===")
        
        try:
            # 模拟依赖服务
            self.mock_knowledge_retrieval.semantic_search.return_value = self.test_knowledge_data
            self.mock_knowledge_retrieval.keyword_search.return_value = self.test_knowledge_data
            
            # 测试优化搜索
            start_time = time.time()
            results = await self.retrieval_optimizer.optimized_search(
                query="机器学习",
                filters={"domain": "technology"},
                limit=5
            )
            
            execution_time = time.time() - start_time
            
            # 验证结果
            self.assertIsNotNone(results)
            self.assertIsInstance(results, list)
            
            # 性能要求：响应时间 < 2秒
            self.assertLess(execution_time, 2.0)
            
            # 获取性能指标
            metrics = await self.retrieval_optimizer.get_performance_metrics()
            self.assertIsNotNone(metrics)
            
            print(f"✓ 检索优化测试通过")
            print(f"  - 搜索结果数: {len(results)}")
            print(f"  - 执行时间: {execution_time:.3f}秒")
            print(f"  - 缓存命中率: {metrics.cache_hit_rate:.2f}")
            
        except Exception as e:
            print(f"✗ 检索优化测试失败: {e}")
            raise
    
    async def test_05_knowledge_history_tracker(self):
        """测试知识历史追溯"""
        print("\n=== 测试知识历史追溯 ===")
        
        try:
            # 测试变更追踪
            start_time = time.time()
            version_id = await self.history_tracker.track_knowledge_change(
                knowledge_id="test_knowledge_001",
                old_content="原始内容",
                new_content="更新后的内容",
                author="test_user",
                change_type=self.history_tracker.ChangeType.MODIFICATION,
                change_summary="测试更新"
            )
            
            execution_time = time.time() - start_time
            
            # 验证结果
            self.assertIsNotNone(version_id)
            self.assertIsInstance(version_id, str)
            
            # 测试版本历史获取
            history = await self.history_tracker.get_version_history("test_knowledge_001")
            self.assertIsNotNone(history)
            
            # 测试演化追溯
            trace_result = await self.history_tracker.trace_knowledge_evolution(
                knowledge_id="test_knowledge_001"
            )
            self.assertIsNotNone(trace_result)
            
            # 性能要求：响应时间 < 1秒
            self.assertLess(execution_time, 1.0)
            
            print(f"✓ 历史追溯测试通过")
            print(f"  - 版本ID: {version_id}")
            print(f"  - 版本历史数: {len(history)}")
            print(f"  - 执行时间: {execution_time:.3f}秒")
            
        except Exception as e:
            print(f"✗ 历史追溯测试失败: {e}")
            raise
    
    async def test_06_component_integration(self):
        """测试组件集成"""
        print("\n=== 测试组件集成 ===")
        
        try:
            # 模拟完整的知识检索和可视化流程
            start_time = time.time()
            
            # 1. 用户查询
            user_query = "机器学习在教育中的应用"
            
            # 2. 优化检索
            self.mock_knowledge_retrieval.semantic_search.return_value = self.test_knowledge_data
            search_results = await self.retrieval_optimizer.optimized_search(
                query=user_query,
                limit=10
            )
            
            # 3. 智能推荐
            recommendation_result = await self.recommendation_engine.recommend_knowledge(
                user_id="test_user_001",
                context=self.test_user_context
            )
            
            # 4. 关联发现
            if search_results:
                associations = await self.association_engine.discover_associations(
                    knowledge_id=search_results[0].id if hasattr(search_results[0], 'id') else "knowledge_001"
                )
            
            # 5. 可视化生成
            graph_result = await self.visualization_engine.generate_knowledge_graph(
                query=user_query,
                max_nodes=20
            )
            
            # 6. 历史追踪
            version_id = await self.history_tracker.track_knowledge_change(
                knowledge_id="integrated_test_001",
                old_content="",
                new_content=f"集成测试: {user_query}",
                author="integration_test",
                change_type=self.history_tracker.ChangeType.CREATION
            )
            
            total_time = time.time() - start_time
            
            # 验证集成结果
            self.assertGreater(len(search_results), 0)
            self.assertGreater(len(recommendation_result.knowledge_items), 0)
            self.assertIsNotNone(graph_result)
            self.assertIsNotNone(version_id)
            
            # 性能要求：整体流程 < 10秒
            self.assertLess(total_time, 10.0)
            
            print(f"✓ 组件集成测试通过")
            print(f"  - 搜索结果: {len(search_results)}")
            print(f"  - 推荐结果: {len(recommendation_result.knowledge_items)}")
            print(f"  - 图谱节点: {graph_result['stats']['total_nodes']}")
            print(f"  - 总执行时间: {total_time:.3f}秒")
            
        except Exception as e:
            print(f"✗ 组件集成测试失败: {e}")
            raise
    
    async def test_07_performance_benchmarks(self):
        """测试性能基准"""
        print("\n=== 测试性能基准 ===")
        
        try:
            # 测试并发处理能力
            concurrent_tasks = []
            for i in range(5):
                task = self.retrieval_optimizer.optimized_search(
                    query=f"测试查询 {i}",
                    limit=10
                )
                concurrent_tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*concurrent_tasks)
            total_time = time.time() - start_time
            
            # 验证并发性能
            self.assertEqual(len(results), 5)
            self.assertLess(total_time, 8.0)  # 平均每个查询 < 1.6秒
            
            # 测试内存使用
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"✓ 性能基准测试通过")
            print(f"  - 并发查询数: 5")
            print(f"  - 总执行时间: {total_time:.3f}秒")
            print(f"  - 平均响应时间: {total_time/5:.3f}秒")
            print(f"  - 内存使用: {memory_usage:.1f}MB")
            
            # 性能要求：内存使用 < 500MB
            self.assertLess(memory_usage, 500)
            
        except Exception as e:
            print(f"✗ 性能基准测试失败: {e}")
            raise
    
    async def test_08_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        try:
            # 测试空查询处理
            empty_result = await self.retrieval_optimizer.optimized_search(
                query="",
                limit=10
            )
            self.assertIsNotNone(empty_result)
            
            # 测试无效知识ID处理
            invalid_history = await self.history_tracker.get_version_history("invalid_id")
            self.assertIsNotNone(invalid_history)
            
            # 测试服务降级
            self.mock_knowledge_retrieval.semantic_search.side_effect = Exception("Service unavailable")
            
            fallback_result = await self.retrieval_optimizer.optimized_search(
                query="测试降级",
                limit=5
            )
            self.assertIsNotNone(fallback_result)
            
            print(f"✓ 错误处理测试通过")
            print(f"  - 空查询处理: 正常")
            print(f"  - 无效ID处理: 正常")
            print(f"  - 服务降级: 正常")
            
        except Exception as e:
            print(f"✗ 错误处理测试失败: {e}")
            raise
    
    async def test_09_data_consistency(self):
        """测试数据一致性"""
        print("\n=== 测试数据一致性 ===")
        
        try:
            # 创建测试知识变更链
            knowledge_id = "consistency_test_001"
            
            # 创建版本1
            version1 = await self.history_tracker.track_knowledge_change(
                knowledge_id=knowledge_id,
                old_content="",
                new_content="版本1内容",
                author="test_user",
                change_type=self.history_tracker.ChangeType.CREATION
            )
            
            # 创建版本2
            version2 = await self.history_tracker.track_knowledge_change(
                knowledge_id=knowledge_id,
                old_content="版本1内容",
                new_content="版本2内容",
                author="test_user",
                change_type=self.history_tracker.ChangeType.MODIFICATION
            )
            
            # 验证版本历史一致性
            history = await self.history_tracker.get_version_history(knowledge_id)
            self.assertEqual(len(history), 2)
            
            # 验证版本对比
            comparison = await self.history_tracker.compare_versions(version1, version2)
            self.assertIn("differences", comparison)
            
            # 验证演化追溯
            trace_result = await self.history_tracker.trace_knowledge_evolution(knowledge_id)
            self.assertEqual(len(trace_result.timeline), 2)
            
            print(f"✓ 数据一致性测试通过")
            print(f"  - 版本数量: {len(history)}")
            print(f"  - 版本差异: {comparison['differences']['change_percentage']:.2f}%")
            print(f"  - 演化事件: {len(trace_result.evolution_events)}")
            
        except Exception as e:
            print(f"✗ 数据一致性测试失败: {e}")
            raise
    
    async def test_10_system_scalability(self):
        """测试系统可扩展性"""
        print("\n=== 测试系统可扩展性 ===")
        
        try:
            # 创建大量测试数据
            large_dataset = []
            for i in range(100):
                knowledge_item = {
                    "id": f"knowledge_{i:03d}",
                    "title": f"测试知识 {i}",
                    "content": f"这是第{i}个测试知识项的内容",
                    "domain": "test",
                    "confidence": 0.8,
                    "created_time": datetime.now() - timedelta(days=i),
                    "tags": ["test"],
                    "metadata": {"type": "test"}
                }
                large_dataset.append(knowledge_item)
            
            # 测试大规模数据处理
            self.mock_knowledge_retrieval.semantic_search.return_value = large_dataset
            
            start_time = time.time()
            results = await self.retrieval_optimizer.optimized_search(
                query="大规模测试",
                limit=50
            )
            processing_time = time.time() - start_time
            
            # 验证扩展性
            self.assertGreaterEqual(len(results), 50)
            self.assertLess(processing_time, 3.0)  # 大规模数据 < 3秒
            
            print(f"✓ 系统可扩展性测试通过")
            print(f"  - 数据集大小: {len(large_dataset)}")
            print(f"  - 处理结果数: {len(results)}")
            print(f"  - 处理时间: {processing_time:.3f}秒")
            
        except Exception as e:
            print(f"✗ 系统可扩展性测试失败: {e}")
            raise
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("V0.3.4 知识检索和可视化系统集成测试")
        print("=" * 60)
        
        tests = [
            self.test_01_smart_recommendation_engine,
            self.test_02_knowledge_association_engine,
            self.test_03_knowledge_visualization_engine,
            self.test_04_knowledge_retrieval_optimizer,
            self.test_05_knowledge_history_tracker,
            self.test_06_component_integration,
            self.test_07_performance_benchmarks,
            self.test_08_error_handling,
            self.test_09_data_consistency,
            self.test_10_system_scalability
        ]
        
        passed_tests = 0
        failed_tests = 0
        total_start_time = time.time()
        
        for test in tests:
            try:
                await test()
                passed_tests += 1
            except Exception as e:
                print(f"✗ 测试失败: {e}")
                failed_tests += 1
        
        total_time = time.time() - total_start_time
        
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"通过测试: {passed_tests}/{len(tests)}")
        print(f"失败测试: {failed_tests}/{len(tests)}")
        print(f"成功率: {passed_tests/len(tests)*100:.1f}%")
        print(f"总执行时间: {total_time:.3f}秒")
        
        if failed_tests == 0:
            print("✓ 所有测试通过！V0.3.4系统集成成功！")
        else:
            print("✗ 部分测试失败，需要修复。")


async def main():
    """主测试函数"""
    test_suite = V0_3_4_IntegrationTest()
    test_suite.setUp()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())