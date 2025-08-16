#!/usr/bin/env python3
"""验证个人知识图谱集成
"""

import asyncio
import sys

sys.path.append('src')

def test_personal_knowledge_graph():
    """测试个人知识图谱"""
    try:
        from src.core_services.personal_knowledge_graph import PersonalKnowledgeGraph

        # 创建个人知识图谱
        pkg = PersonalKnowledgeGraph()

        # 验证基本属性
        assert hasattr(pkg, 'knowledge_nodes'), "缺少knowledge_nodes属性"
        assert hasattr(pkg, 'relationships'), "缺少relationships属性"
        assert hasattr(pkg, 'user_profile'), "缺少user_profile属性"

        # 验证基本方法
        assert hasattr(pkg, 'add_knowledge_node'), "缺少add_knowledge_node方法"
        assert hasattr(pkg, 'create_relationship'), "缺少create_relationship方法"
        assert hasattr(pkg, 'query_knowledge'), "缺少query_knowledge方法"

        print("✅ PersonalKnowledgeGraph验证通过")
        return True

    except Exception as e:
        print(f"❌ PersonalKnowledgeGraph验证失败: {e}")
        return False

def test_knowledge_graph_builder():
    """测试知识图谱构建器"""
    try:
        from src.core_services.knowledge_graph_builder import KnowledgeGraphBuilder

        # 创建知识图谱构建器
        builder = KnowledgeGraphBuilder()

        # 验证基本属性
        assert hasattr(builder, 'entity_extractor'), "缺少entity_extractor属性"
        assert hasattr(builder, 'relation_detector'), "缺少relation_detector属性"

        # 验证基本方法
        assert hasattr(builder, 'extract_entities'), "缺少extract_entities方法"
        assert hasattr(builder, 'detect_relations'), "缺少detect_relations方法"
        assert hasattr(builder, 'build_graph_from_text'), "缺少build_graph_from_text方法"

        # 测试从文本构建图谱
        test_text = "AI伦理是人工智能发展的重要指导原则。透明度和公平性是AI伦理的核心要素。"

        graph_result = builder.build_graph_from_text(test_text)

        assert "entities" in graph_result, "图谱构建结果缺少entities"
        assert "relations" in graph_result, "图谱构建结果缺少relations"
        assert "graph_structure" in graph_result, "图谱构建结果缺少graph_structure"

        print(f"   提取实体数量: {len(graph_result['entities'])}")
        print(f"   检测关系数量: {len(graph_result['relations'])}")
        print(f"   图谱节点数: {len(graph_result['graph_structure']['nodes'])}")

        print("✅ KnowledgeGraphBuilder验证通过")
        return True

    except Exception as e:
        print(f"❌ KnowledgeGraphBuilder验证失败: {e}")
        return False

def test_user_interest_profiler():
    """测试用户兴趣画像器"""
    try:
        from src.core_services.user_interest_profiler import UserInterestProfiler

        # 创建用户兴趣画像器
        profiler = UserInterestProfiler()

        # 验证基本属性
        assert hasattr(profiler, 'interest_categories'), "缺少interest_categories属性"
        assert hasattr(profiler, 'user_interactions'), "缺少user_interactions属性"

        # 验证基本方法
        assert hasattr(profiler, 'analyze_user_behavior'), "缺少analyze_user_behavior方法"
        assert hasattr(profiler, 'update_interest_profile'), "缺少update_interest_profile方法"
        assert hasattr(profiler, 'get_personalized_recommendations'), "缺少get_personalized_recommendations方法"

        # 测试用户行为分析
        user_behavior = {
            "user_id": "test_user",
            "interactions": [
                {"type": "query", "content": "AI伦理相关问题", "timestamp": "2025-01-01T10:00:00"},
                {"type": "debate_participation", "content": "AI安全性", "timestamp": "2025-01-01T11:00:00"},
                {"type": "knowledge_creation", "content": "机器学习算法分析", "timestamp": "2025-01-01T12:00:00"}
            ]
        }

        behavior_analysis = profiler.analyze_user_behavior(user_behavior)

        assert "interest_scores" in behavior_analysis, "行为分析缺少interest_scores"
        assert "dominant_interests" in behavior_analysis, "行为分析缺少dominant_interests"
        assert "interaction_patterns" in behavior_analysis, "行为分析缺少interaction_patterns"

        print(f"   主要兴趣: {behavior_analysis['dominant_interests']}")
        print(f"   兴趣分数数量: {len(behavior_analysis['interest_scores'])}")
        print(f"   交互模式: {behavior_analysis['interaction_patterns']}")

        print("✅ UserInterestProfiler验证通过")
        return True

    except Exception as e:
        print(f"❌ UserInterestProfiler验证失败: {e}")
        return False

async def test_personalized_knowledge_recommendation():
    """测试个性化知识推荐"""
    try:
        from src.core_services.personal_knowledge_graph import PersonalKnowledgeGraph
        from src.core_services.user_interest_profiler import UserInterestProfiler
        from src.real_demo_system.personalized_recommendation_engine import PersonalizedRecommendationEngine

        # 创建组件
        pkg = PersonalKnowledgeGraph()
        profiler = UserInterestProfiler()
        recommender = PersonalizedRecommendationEngine()

        # 构建个人知识图谱
        user_knowledge = [
            {"concept": "AI伦理", "type": "domain", "importance": 0.9},
            {"concept": "机器学习", "type": "technology", "importance": 0.8},
            {"concept": "数据隐私", "type": "concern", "importance": 0.7},
            {"concept": "算法公平性", "type": "principle", "importance": 0.8}
        ]

        for knowledge in user_knowledge:
            node_id = pkg.add_knowledge_node(
                concept=knowledge["concept"],
                node_type=knowledge["type"],
                importance=knowledge["importance"]
            )
            assert node_id is not None, f"知识节点创建失败: {knowledge['concept']}"

        # 创建关系
        pkg.create_relationship(
            source_concept="AI伦理",
            target_concept="算法公平性",
            relation_type="includes",
            strength=0.9
        )

        pkg.create_relationship(
            source_concept="机器学习",
            target_concept="数据隐私",
            relation_type="affects",
            strength=0.7
        )

        # 模拟用户兴趣
        user_profile = {
            "user_id": "test_user",
            "interests": {
                "AI伦理": 0.9,
                "技术实现": 0.6,
                "政策法规": 0.7
            },
            "expertise_level": "intermediate",
            "preferred_content_types": ["analysis", "case_study"]
        }

        # 生成个性化推荐
        recommendations = recommender.generate_recommendations(
            user_profile=user_profile,
            knowledge_graph=pkg,
            recommendation_count=5
        )

        assert "recommended_topics" in recommendations, "推荐结果缺少recommended_topics"
        assert "reasoning" in recommendations, "推荐结果缺少reasoning"
        assert "confidence_scores" in recommendations, "推荐结果缺少confidence_scores"

        print(f"   个人知识节点数: {len(pkg.knowledge_nodes)}")
        print(f"   知识关系数: {len(pkg.relationships)}")
        print(f"   推荐主题数: {len(recommendations['recommended_topics'])}")
        print(f"   推荐置信度: {recommendations['confidence_scores']}")

        print("✅ 个性化知识推荐验证通过")
        return True

    except Exception as e:
        print(f"❌ 个性化知识推荐验证失败: {e}")
        return False

def test_knowledge_graph_visualization():
    """测试知识图谱可视化"""
    try:
        from src.real_demo_system.knowledge_graph_visualizer import KnowledgeGraphVisualizer

        # 创建知识图谱可视化器
        visualizer = KnowledgeGraphVisualizer()

        # 验证基本属性
        assert hasattr(visualizer, 'layout_algorithms'), "缺少layout_algorithms属性"
        assert hasattr(visualizer, 'visualization_styles'), "缺少visualization_styles属性"

        # 验证基本方法
        assert hasattr(visualizer, 'create_graph_visualization'), "缺少create_graph_visualization方法"
        assert hasattr(visualizer, 'generate_interactive_view'), "缺少generate_interactive_view方法"
        assert hasattr(visualizer, 'export_graph_data'), "缺少export_graph_data方法"

        # 测试图谱可视化
        graph_data = {
            "nodes": [
                {"id": "ai_ethics", "label": "AI伦理", "type": "domain", "importance": 0.9},
                {"id": "fairness", "label": "公平性", "type": "principle", "importance": 0.8},
                {"id": "transparency", "label": "透明度", "type": "principle", "importance": 0.8}
            ],
            "edges": [
                {"source": "ai_ethics", "target": "fairness", "type": "includes", "weight": 0.9},
                {"source": "ai_ethics", "target": "transparency", "type": "includes", "weight": 0.8}
            ]
        }

        visualization = visualizer.create_graph_visualization(graph_data)

        assert "visualization_id" in visualization, "可视化结果缺少visualization_id"
        assert "layout_config" in visualization, "可视化结果缺少layout_config"
        assert "interactive_features" in visualization, "可视化结果缺少interactive_features"

        print(f"   可视化ID: {visualization['visualization_id']}")
        print(f"   节点数量: {len(graph_data['nodes'])}")
        print(f"   边数量: {len(graph_data['edges'])}")
        print(f"   布局算法: {visualization['layout_config']['algorithm']}")

        print("✅ 知识图谱可视化验证通过")
        return True

    except Exception as e:
        print(f"❌ 知识图谱可视化验证失败: {e}")
        return False

def test_adaptive_learning_system():
    """测试自适应学习系统"""
    try:
        from src.core_services.adaptive_learning_system import AdaptiveLearningSystem

        # 创建自适应学习系统
        learning_system = AdaptiveLearningSystem()

        # 验证基本属性
        assert hasattr(learning_system, 'learning_models'), "缺少learning_models属性"
        assert hasattr(learning_system, 'adaptation_strategies'), "缺少adaptation_strategies属性"

        # 验证基本方法
        assert hasattr(learning_system, 'learn_from_interaction'), "缺少learn_from_interaction方法"
        assert hasattr(learning_system, 'adapt_recommendations'), "缺少adapt_recommendations方法"
        assert hasattr(learning_system, 'evaluate_learning_effectiveness'), "缺少evaluate_learning_effectiveness方法"

        # 测试从交互中学习
        interaction_data = {
            "user_id": "test_user",
            "interaction_type": "knowledge_query",
            "query": "AI伦理的最新发展",
            "user_feedback": {
                "relevance": 0.8,
                "usefulness": 0.9,
                "satisfaction": 0.7
            },
            "context": {
                "previous_queries": ["机器学习算法", "数据隐私保护"],
                "user_expertise": "intermediate"
            }
        }

        learning_result = learning_system.learn_from_interaction(interaction_data)

        assert "learning_updates" in learning_result, "学习结果缺少learning_updates"
        assert "model_adjustments" in learning_result, "学习结果缺少model_adjustments"
        assert "confidence_change" in learning_result, "学习结果缺少confidence_change"

        print(f"   学习更新数量: {len(learning_result['learning_updates'])}")
        print(f"   模型调整: {learning_result['model_adjustments']}")
        print(f"   置信度变化: {learning_result['confidence_change']:.3f}")

        print("✅ 自适应学习系统验证通过")
        return True

    except Exception as e:
        print(f"❌ 自适应学习系统验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证个人知识图谱集成")

    tests = [
        ("个人知识图谱", test_personal_knowledge_graph),
        ("知识图谱构建器", test_knowledge_graph_builder),
        ("用户兴趣画像器", test_user_interest_profiler),
        ("个性化知识推荐", test_personalized_knowledge_recommendation),
        ("知识图谱可视化", test_knowledge_graph_visualization),
        ("自适应学习系统", test_adaptive_learning_system)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()

        if result:
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break

    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
