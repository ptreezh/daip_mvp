#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Wiki实时更新机制
"""

import sys
import os
import asyncio
sys.path.append('src')

def test_wiki_service():
    """测试Wiki服务"""
    try:
        from src.core_services.wiki_service import WikiService
        
        # 创建Wiki服务
        wiki_service = WikiService()
        
        # 验证基本属性
        assert hasattr(wiki_service, '_wiki_directory'), "缺少_wiki_directory属性"
        assert hasattr(wiki_service, 'vector_client'), "缺少vector_client属性"
        assert hasattr(wiki_service, 'chroma_collection'), "缺少chroma_collection属性"
        
        # 验证基本方法
        assert hasattr(wiki_service, 'create_entry'), "缺少create_entry方法"
        assert hasattr(wiki_service, 'search'), "缺少search方法"
        assert hasattr(wiki_service, 'get_entry'), "缺少get_entry方法"
        
        print(f"   Wiki目录: {wiki_service._wiki_directory}")
        print(f"   向量数据库: 已初始化")
        print(f"   集合名称: {wiki_service.chroma_collection.name}")
        
        print("✅ WikiService验证通过")
        return True
        
    except Exception as e:
        print(f"❌ WikiService验证失败: {e}")
        return False

def test_real_time_wiki_updater():
    """测试实时Wiki更新器"""
    try:
        from src.real_demo_system.real_time_wiki_updater import RealTimeWikiUpdater
        
        # 创建实时Wiki更新器
        updater = RealTimeWikiUpdater()
        
        # 验证基本属性
        assert hasattr(updater, 'wiki_service'), "缺少wiki_service属性"
        assert hasattr(updater, 'update_queue'), "缺少update_queue属性"
        assert hasattr(updater, 'update_history'), "缺少update_history属性"
        
        # 验证基本方法
        assert hasattr(updater, 'process_debate_result'), "缺少process_debate_result方法"
        assert hasattr(updater, 'auto_update_knowledge'), "缺少auto_update_knowledge方法"
        assert hasattr(updater, 'track_changes'), "缺少track_changes方法"
        
        print("✅ RealTimeWikiUpdater验证通过")
        return True
        
    except Exception as e:
        print(f"❌ RealTimeWikiUpdater验证失败: {e}")
        return False

def test_knowledge_version_control():
    """测试知识版本控制"""
    try:
        from src.core_services.knowledge_version_control import KnowledgeVersionControl
        
        # 创建知识版本控制
        version_control = KnowledgeVersionControl()
        
        # 验证基本属性
        assert hasattr(version_control, 'versions'), "缺少versions属性"
        assert hasattr(version_control, 'change_log'), "缺少change_log属性"
        
        # 验证基本方法
        assert hasattr(version_control, 'create_version'), "缺少create_version方法"
        assert hasattr(version_control, 'compare_versions'), "缺少compare_versions方法"
        assert hasattr(version_control, 'rollback_version'), "缺少rollback_version方法"
        
        # 测试版本创建
        test_content = {
            "title": "AI伦理原则",
            "content": "AI系统应该遵循透明、公平、可解释的原则",
            "author": "AI Ethics Expert",
            "tags": ["AI", "伦理", "原则"]
        }
        
        version_id = version_control.create_version(
            content=test_content,
            change_description="初始版本创建"
        )
        
        assert version_id is not None, "版本创建失败"
        assert len(version_control.versions) > 0, "版本列表为空"
        
        print(f"   版本ID: {version_id}")
        print(f"   版本数量: {len(version_control.versions)}")
        
        print("✅ KnowledgeVersionControl验证通过")
        return True
        
    except Exception as e:
        print(f"❌ KnowledgeVersionControl验证失败: {e}")
        return False

def test_knowledge_quality_scorer():
    """测试知识质量评分器"""
    try:
        from src.core_services.knowledge_quality_scorer import KnowledgeQualityScorer
        
        # 创建知识质量评分器
        scorer = KnowledgeQualityScorer()
        
        # 验证基本属性
        assert hasattr(scorer, 'quality_metrics'), "缺少quality_metrics属性"
        assert hasattr(scorer, 'scoring_history'), "缺少scoring_history属性"
        
        # 验证基本方法
        assert hasattr(scorer, 'score_knowledge'), "缺少score_knowledge方法"
        assert hasattr(scorer, 'evaluate_accuracy'), "缺少evaluate_accuracy方法"
        assert hasattr(scorer, 'assess_completeness'), "缺少assess_completeness方法"
        
        # 测试知识评分
        test_knowledge = {
            "title": "机器学习基础",
            "content": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习模式。主要包括监督学习、无监督学习和强化学习三种类型。",
            "sources": ["学术论文", "教科书"],
            "evidence": ["实验数据", "理论证明"],
            "author_expertise": 0.8
        }
        
        quality_score = scorer.score_knowledge(test_knowledge)
        
        assert "overall_score" in quality_score, "质量评分缺少overall_score"
        assert "scores" in quality_score, "质量评分缺少scores"
        
        scores = quality_score["scores"]
        assert "accuracy_score" in scores, "质量评分缺少accuracy_score"
        assert "completeness_score" in scores, "质量评分缺少completeness_score"
        assert "reliability_score" in scores, "质量评分缺少reliability_score"
        
        print(f"   总体评分: {quality_score['overall_score']:.2f}")
        print(f"   准确性评分: {scores['accuracy_score']:.2f}")
        print(f"   完整性评分: {scores['completeness_score']:.2f}")
        print(f"   可靠性评分: {scores['reliability_score']:.2f}")
        print(f"   质量等级: {quality_score['quality_grade']}")
        
        print("✅ KnowledgeQualityScorer验证通过")
        return True
        
    except Exception as e:
        print(f"❌ KnowledgeQualityScorer验证失败: {e}")
        return False

async def test_wiki_real_time_update_demo():
    """测试Wiki实时更新演示"""
    try:
        from src.core_services.wiki_service import WikiService
        from src.real_demo_system.real_time_wiki_updater import RealTimeWikiUpdater
        
        # 创建组件
        wiki_service = WikiService()
        updater = RealTimeWikiUpdater()
        
        # 模拟辩论结果
        debate_result = {
            "topic": "AI在医疗诊断中的应用",
            "participants": ["AI Ethics", "Medical Professional", "Data Governance Expert"],
            "consensus": {
                "agreement_level": 0.85,
                "key_points": [
                    "AI可以提高诊断准确性",
                    "需要医生监督和验证",
                    "必须保护患者隐私",
                    "需要建立责任机制"
                ]
            },
            "new_insights": [
                "AI辅助诊断的最佳实践",
                "医疗AI的伦理边界",
                "患者数据保护策略"
            ],
            "evidence": [
                "临床试验数据显示AI诊断准确率达95%",
                "欧盟GDPR对医疗数据的严格要求",
                "美国FDA对医疗AI的监管框架"
            ]
        }
        
        # 处理辩论结果并更新Wiki
        update_result = updater.process_debate_result(debate_result)
        
        assert "updated_entries" in update_result, "更新结果缺少updated_entries"
        assert "new_entries" in update_result, "更新结果缺少new_entries"
        assert "quality_scores" in update_result, "更新结果缺少quality_scores"
        
        print(f"   处理主题: {debate_result['topic']}")
        print(f"   参与者数量: {len(debate_result['participants'])}")
        print(f"   共识水平: {debate_result['consensus']['agreement_level']}")
        print(f"   更新条目数: {len(update_result['updated_entries'])}")
        print(f"   新增条目数: {len(update_result['new_entries'])}")
        
        # 测试自动知识更新
        auto_update_result = updater.auto_update_knowledge(
            topic="AI医疗诊断",
            new_information=debate_result["new_insights"]
        )
        
        assert "success" in auto_update_result, "自动更新结果缺少success字段"
        assert auto_update_result["success"] == True, "自动更新失败"
        
        print(f"   自动更新: {'成功' if auto_update_result['success'] else '失败'}")
        print(f"   更新条目: {len(auto_update_result.get('updated_entries', []))}")
        
        print("✅ Wiki实时更新演示验证通过")
        return True
        
    except Exception as e:
        print(f"❌ Wiki实时更新演示验证失败: {e}")
        return False

def test_change_tracking():
    """测试变更追踪"""
    try:
        from src.core_services.wiki_change_tracker import WikiChangeTracker
        
        # 创建变更追踪器
        tracker = WikiChangeTracker()
        
        # 验证基本属性
        assert hasattr(tracker, 'change_history'), "缺少change_history属性"
        assert hasattr(tracker, 'tracked_entities'), "缺少tracked_entities属性"
        
        # 验证基本方法
        assert hasattr(tracker, 'track_change'), "缺少track_change方法"
        assert hasattr(tracker, 'get_change_history'), "缺少get_change_history方法"
        assert hasattr(tracker, 'analyze_change_patterns'), "缺少analyze_change_patterns方法"
        
        # 测试变更追踪
        change_data = {
            "entity_id": "ai_medical_diagnosis",
            "change_type": "content_update",
            "old_content": "AI在医疗诊断中的应用还在探索阶段",
            "new_content": "AI在医疗诊断中已显示出显著的准确性提升，但需要医生监督",
            "change_reason": "基于最新辩论共识更新",
            "contributor": "AI Ethics Expert",
            "evidence": ["临床试验数据", "专家共识"]
        }
        
        change_id = tracker.track_change(change_data)
        
        assert change_id is not None, "变更追踪失败"
        assert len(tracker.change_history) > 0, "变更历史为空"
        
        # 获取变更历史
        history = tracker.get_change_history("ai_medical_diagnosis")
        
        assert len(history) > 0, "实体变更历史为空"
        assert history[0]["change_id"] == change_id, "变更历史不匹配"
        
        print(f"   变更ID: {change_id}")
        print(f"   变更类型: {change_data['change_type']}")
        print(f"   变更历史数量: {len(history)}")
        
        # 分析变更模式
        patterns = tracker.analyze_change_patterns()
        
        assert "frequent_contributors" in patterns, "变更模式分析缺少frequent_contributors"
        assert "change_types" in patterns, "变更模式分析缺少change_types"
        
        print(f"   变更模式分析: 完成")
        print(f"   活跃贡献者: {len(patterns['frequent_contributors'])}")
        print(f"   变更类型: {len(patterns['change_types'])}")
        
        print("✅ 变更追踪验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 变更追踪验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证Wiki实时更新机制")
    
    tests = [
        ("Wiki服务", test_wiki_service),
        ("实时Wiki更新器", test_real_time_wiki_updater),
        ("知识版本控制", test_knowledge_version_control),
        ("知识质量评分器", test_knowledge_quality_scorer),
        ("Wiki实时更新演示", test_wiki_real_time_update_demo),
        ("变更追踪", test_change_tracking)
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