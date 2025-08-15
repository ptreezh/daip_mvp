#!/usr/bin/env python3
"""验证知识冲突解决
"""

import asyncio
import sys

sys.path.append('src')

def test_knowledge_conflict_resolver():
    """测试知识冲突解决器"""
    try:
        from src.core_services.knowledge_conflict_resolver import KnowledgeConflictResolver
        
        # 创建知识冲突解决器
        resolver = KnowledgeConflictResolver()
        
        # 验证基本属性
        assert hasattr(resolver, 'conflict_detection_rules'), "缺少conflict_detection_rules属性"
        assert hasattr(resolver, 'resolution_strategies'), "缺少resolution_strategies属性"
        assert hasattr(resolver, 'conflict_history'), "缺少conflict_history属性"
        
        # 验证基本方法
        assert hasattr(resolver, 'detect_conflicts'), "缺少detect_conflicts方法"
        assert hasattr(resolver, 'resolve_conflict'), "缺少resolve_conflict方法"
        assert hasattr(resolver, 'validate_resolution'), "缺少validate_resolution方法"
        
        print("✅ KnowledgeConflictResolver验证通过")
        return True
        
    except Exception as e:
        print(f"❌ KnowledgeConflictResolver验证失败: {e}")
        return False

def test_conflict_detection():
    """测试冲突检测"""
    try:
        from src.core_services.knowledge_conflict_resolver import KnowledgeConflictResolver
        
        # 创建冲突解决器
        resolver = KnowledgeConflictResolver()
        
        # 模拟冲突知识（增强矛盾性）
        knowledge_items = [
            {
                "id": "ai_safety_1",
                "title": "AI安全性评估",
                "content": "AI系统在医疗诊断中是安全可靠的，准确率达到95%",
                "source": "技术报告A",
                "confidence": 0.8,
                "timestamp": "2025-01-01T10:00:00"
            },
            {
                "id": "ai_safety_2", 
                "title": "AI医疗风险分析",
                "content": "AI系统在医疗诊断中是危险不可靠的，存在重大风险",
                "source": "研究论文B",
                "confidence": 0.7,
                "timestamp": "2025-01-02T14:00:00"
            },
            {
                "id": "ai_safety_3",
                "title": "AI诊断准确性对比",
                "content": "AI医疗诊断准确率仅为75%，远低于预期",
                "source": "临床研究C",
                "confidence": 0.9,
                "timestamp": "2025-01-03T09:00:00"
            }
        ]
        
        # 检测冲突
        conflicts = resolver.detect_conflicts(knowledge_items)
        
        assert isinstance(conflicts, list), "冲突检测结果应为列表"
        assert len(conflicts) > 0, "应该检测到冲突"
        
        # 验证冲突结构
        for conflict in conflicts:
            assert "conflict_id" in conflict, "冲突缺少conflict_id"
            assert "conflict_type" in conflict, "冲突缺少conflict_type"
            assert "conflicting_items" in conflict, "冲突缺少conflicting_items"
            assert "severity" in conflict, "冲突缺少severity"
        
        print(f"   检测到冲突数量: {len(conflicts)}")
        print(f"   冲突类型: {[c['conflict_type'] for c in conflicts]}")
        print(f"   冲突严重程度: {[c['severity'] for c in conflicts]}")
        
        print("✅ 冲突检测验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 冲突检测验证失败: {e}")
        return False

def test_conflict_resolution():
    """测试冲突解决"""
    try:
        from src.core_services.knowledge_conflict_resolver import KnowledgeConflictResolver
        
        # 创建冲突解决器
        resolver = KnowledgeConflictResolver()
        
        # 模拟冲突
        conflict = {
            "conflict_id": "conflict_001",
            "conflict_type": "contradictory_claims",
            "conflicting_items": [
                {
                    "id": "item_1",
                    "content": "AI诊断准确率为95%",
                    "confidence": 0.8,
                    "source": "研究A"
                },
                {
                    "id": "item_2", 
                    "content": "AI诊断存在重大风险",
                    "confidence": 0.7,
                    "source": "研究B"
                }
            ],
            "severity": "high",
            "context": "AI医疗诊断安全性"
        }
        
        # 解决冲突
        resolution = resolver.resolve_conflict(conflict)
        
        assert "resolution_id" in resolution, "解决方案缺少resolution_id"
        assert "strategy" in resolution, "解决方案缺少strategy"
        assert "resolved_content" in resolution, "解决方案缺少resolved_content"
        assert "confidence_score" in resolution, "解决方案缺少confidence_score"
        assert "evidence" in resolution, "解决方案缺少evidence"
        
        print(f"   解决方案ID: {resolution['resolution_id']}")
        print(f"   解决策略: {resolution['strategy']}")
        print(f"   置信度: {resolution['confidence_score']:.2f}")
        print(f"   证据数量: {len(resolution['evidence'])}")
        
        # 验证解决方案
        validation = resolver.validate_resolution(resolution)
        
        assert "is_valid" in validation, "验证结果缺少is_valid"
        assert "validation_score" in validation, "验证结果缺少validation_score"
        
        print(f"   解决方案有效性: {validation['is_valid']}")
        print(f"   验证分数: {validation['validation_score']:.2f}")
        
        print("✅ 冲突解决验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 冲突解决验证失败: {e}")
        return False

def test_transparent_conflict_resolution():
    """测试透明冲突解决展示"""
    try:
        from src.real_demo_system.transparent_conflict_resolution import TransparentConflictResolution
        
        # 创建透明冲突解决展示
        transparent_resolver = TransparentConflictResolution()
        
        # 验证基本属性
        assert hasattr(transparent_resolver, 'resolution_steps'), "缺少resolution_steps属性"
        assert hasattr(transparent_resolver, 'transparency_level'), "缺少transparency_level属性"
        
        # 验证基本方法
        assert hasattr(transparent_resolver, 'show_conflict_analysis'), "缺少show_conflict_analysis方法"
        assert hasattr(transparent_resolver, 'display_resolution_process'), "缺少display_resolution_process方法"
        assert hasattr(transparent_resolver, 'generate_resolution_report'), "缺少generate_resolution_report方法"
        
        # 测试冲突分析展示
        conflict_data = {
            "conflict_id": "demo_conflict",
            "conflicting_statements": [
                "AI系统完全可靠",
                "AI系统存在风险"
            ],
            "sources": ["研究A", "研究B"],
            "context": "AI安全性讨论"
        }
        
        analysis_display = transparent_resolver.show_conflict_analysis(conflict_data)
        
        assert "analysis_id" in analysis_display, "分析展示缺少analysis_id"
        assert "conflict_visualization" in analysis_display, "分析展示缺少conflict_visualization"
        assert "stakeholder_positions" in analysis_display, "分析展示缺少stakeholder_positions"
        
        print(f"   分析ID: {analysis_display['analysis_id']}")
        print(f"   可视化类型: {analysis_display['conflict_visualization']['type']}")
        print(f"   利益相关者: {len(analysis_display['stakeholder_positions'])}")
        
        print("✅ 透明冲突解决展示验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 透明冲突解决展示验证失败: {e}")
        return False

async def test_real_time_conflict_monitoring():
    """测试实时冲突监控"""
    try:
        from src.real_demo_system.real_time_conflict_monitor import RealTimeConflictMonitor
        
        # 创建实时冲突监控器
        monitor = RealTimeConflictMonitor()
        
        # 验证基本属性
        assert hasattr(monitor, 'active_monitors'), "缺少active_monitors属性"
        assert hasattr(monitor, 'conflict_alerts'), "缺少conflict_alerts属性"
        
        # 验证基本方法
        assert hasattr(monitor, 'start_monitoring'), "缺少start_monitoring方法"
        assert hasattr(monitor, 'detect_emerging_conflicts'), "缺少detect_emerging_conflicts方法"
        assert hasattr(monitor, 'send_conflict_alert'), "缺少send_conflict_alert方法"
        
        # 启动监控
        monitor_id = monitor.start_monitoring(
            knowledge_domain="AI医疗诊断",
            sensitivity_level="high"
        )
        
        assert monitor_id is not None, "监控启动失败"
        assert len(monitor.active_monitors) > 0, "活跃监控列表为空"
        
        # 模拟新知识输入
        new_knowledge = {
            "content": "最新研究显示AI诊断准确率仅为80%",
            "source": "新研究D",
            "confidence": 0.85,
            "domain": "AI医疗诊断"
        }
        
        # 检测新兴冲突
        emerging_conflicts = monitor.detect_emerging_conflicts(new_knowledge)
        
        assert isinstance(emerging_conflicts, list), "新兴冲突检测结果应为列表"
        
        print(f"   监控ID: {monitor_id}")
        print(f"   活跃监控数量: {len(monitor.active_monitors)}")
        print(f"   检测到新兴冲突: {len(emerging_conflicts)}")
        
        # 如果检测到冲突，发送警报
        if emerging_conflicts:
            for conflict in emerging_conflicts:
                alert_result = monitor.send_conflict_alert(conflict)
                assert alert_result["success"] == True, "冲突警报发送失败"
                print(f"   冲突警报: {alert_result['alert_id']}")
        
        print("✅ 实时冲突监控验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 实时冲突监控验证失败: {e}")
        return False

def test_conflict_resolution_strategies():
    """测试冲突解决策略"""
    try:
        from src.core_services.conflict_resolution_strategies import ConflictResolutionStrategies
        
        # 创建冲突解决策略
        strategies = ConflictResolutionStrategies()
        
        # 验证基本属性
        assert hasattr(strategies, 'available_strategies'), "缺少available_strategies属性"
        assert hasattr(strategies, 'strategy_effectiveness'), "缺少strategy_effectiveness属性"
        
        # 验证基本方法
        assert hasattr(strategies, 'select_strategy'), "缺少select_strategy方法"
        assert hasattr(strategies, 'apply_synthesis_strategy'), "缺少apply_synthesis_strategy方法"
        assert hasattr(strategies, 'apply_evidence_weighting'), "缺少apply_evidence_weighting方法"
        
        # 测试策略选择
        conflict_context = {
            "conflict_type": "contradictory_claims",
            "domain": "medical_ai",
            "severity": "high",
            "evidence_quality": "mixed"
        }
        
        selected_strategy = strategies.select_strategy(conflict_context)
        
        assert "strategy_name" in selected_strategy, "策略选择结果缺少strategy_name"
        assert "confidence" in selected_strategy, "策略选择结果缺少confidence"
        assert "rationale" in selected_strategy, "策略选择结果缺少rationale"
        
        print(f"   选择策略: {selected_strategy['strategy_name']}")
        print(f"   策略置信度: {selected_strategy['confidence']:.2f}")
        print(f"   选择理由: {selected_strategy['rationale']}")
        
        # 测试综合策略
        conflicting_claims = [
            {"claim": "AI诊断准确率95%", "evidence_strength": 0.8, "source_credibility": 0.7},
            {"claim": "AI诊断存在风险", "evidence_strength": 0.7, "source_credibility": 0.8},
            {"claim": "AI需要医生监督", "evidence_strength": 0.9, "source_credibility": 0.9}
        ]
        
        synthesis_result = strategies.apply_synthesis_strategy(conflicting_claims)
        
        assert "synthesized_position" in synthesis_result, "综合结果缺少synthesized_position"
        assert "confidence_level" in synthesis_result, "综合结果缺少confidence_level"
        assert "supporting_evidence" in synthesis_result, "综合结果缺少supporting_evidence"
        
        print(f"   综合立场: {synthesis_result['synthesized_position'][:100]}...")
        print(f"   综合置信度: {synthesis_result['confidence_level']:.2f}")
        print(f"   支持证据数量: {len(synthesis_result['supporting_evidence'])}")
        
        print("✅ 冲突解决策略验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 冲突解决策略验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证知识冲突解决")
    
    tests = [
        ("知识冲突解决器", test_knowledge_conflict_resolver),
        ("冲突检测", test_conflict_detection),
        ("冲突解决", test_conflict_resolution),
        ("透明冲突解决展示", test_transparent_conflict_resolution),
        ("实时冲突监控", test_real_time_conflict_monitoring),
        ("冲突解决策略", test_conflict_resolution_strategies)
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