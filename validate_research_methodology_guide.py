#!/usr/bin/env python3
"""验证研究方法论指导系统
"""

import asyncio
import sys
import traceback
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def validate_research_methodology_guide():
    """验证研究方法论指导系统"""
    print("🔍 验证研究方法论指导系统")
    print("=" * 60)
    
    validation_results = {
        "imports": False,
        "initialization": False,
        "methodology_recommendation": False,
        "research_design": False,
        "report_generation": False
    }
    
    try:
        # 1. 验证导入
        print("\n1️⃣ 验证组件导入...")
        
        try:
            from src.scenarios.enhanced_academic_research_scenario import ResearchMethodology, ResearchQuestion
            from src.scenarios.research_methodology_guide import (
                MethodologyRecommendation,
                ResearchComplexity,
                ResearchDesign,
                ResearchDomain,
                ResearchMethodologyGuideSystem,
            )
            print("   ✅ 组件导入成功")
            validation_results["imports"] = True
        except ImportError as e:
            print(f"   ❌ 组件导入失败: {e}")
            traceback.print_exc()
            return validation_results
        
        # 2. 验证初始化
        print("\n2️⃣ 验证系统初始化...")
        
        try:
            guide_system = ResearchMethodologyGuideSystem()
            print("   ✅ 系统初始化成功")
            print(f"   ✅ 方法论数据库: {len(guide_system.methodology_database)} 种方法")
            print(f"   ✅ 领域指导: {len(guide_system.domain_specific_guides)} 个领域")
            
            validation_results["initialization"] = True
        except Exception as e:
            print(f"   ❌ 系统初始化失败: {e}")
            traceback.print_exc()
            return validation_results
        
        # 3. 验证方法论推荐
        print("\n3️⃣ 验证方法论推荐功能...")
        
        try:
            # 创建测试研究问题
            research_question = ResearchQuestion(
                question="How does technology affect student learning outcomes?",
                research_type="empirical",
                methodology_suggestions=[ResearchMethodology.MIXED_METHODS],
                background="Educational technology research",
                significance="Understanding technology impact on education",
                feasibility_score=0.8,
                novelty_score=0.7
            )
            
            # 获取方法论推荐
            recommendations = await guide_system.recommend_methodology(
                research_question,
                ResearchDomain.EDUCATION,
                ResearchComplexity.INTERMEDIATE
            )
            
            assert len(recommendations) > 0
            assert all(isinstance(rec, MethodologyRecommendation) for rec in recommendations)
            
            print(f"   ✅ 方法论推荐成功: {len(recommendations)} 个推荐")
            for i, rec in enumerate(recommendations[:3]):
                print(f"      {i+1}. {rec.methodology.value} (适用性: {rec.suitability_score:.2f})")
            
            validation_results["methodology_recommendation"] = True
        except Exception as e:
            print(f"   ❌ 方法论推荐失败: {e}")
            traceback.print_exc()
            return validation_results
        
        # 4. 验证研究设计创建
        print("\n4️⃣ 验证研究设计创建...")
        
        try:
            # 使用第一个推荐的方法论创建研究设计
            selected_methodology = recommendations[0].methodology
            
            research_design = await guide_system.create_research_design(
                research_question,
                selected_methodology,
                ResearchDomain.EDUCATION
            )
            
            assert isinstance(research_design, ResearchDesign)
            assert research_design.methodology == selected_methodology
            assert len(research_design.data_collection_methods) > 0
            assert len(research_design.timeline) > 0
            
            print("   ✅ 研究设计创建成功")
            print(f"      方法论: {research_design.methodology.value}")
            print(f"      研究设计: {research_design.study_design}")
            print(f"      数据收集方法: {len(research_design.data_collection_methods)} 种")
            print(f"      时间线阶段: {len(research_design.timeline)} 个")
            print(f"      伦理考虑: {len(research_design.ethical_considerations)} 项")
            
            validation_results["research_design"] = True
        except Exception as e:
            print(f"   ❌ 研究设计创建失败: {e}")
            traceback.print_exc()
            return validation_results
        
        # 5. 验证报告生成
        print("\n5️⃣ 验证方法论报告生成...")
        
        try:
            methodology_report = await guide_system.generate_methodology_report(research_design)
            
            assert isinstance(methodology_report, str)
            assert len(methodology_report) > 500
            assert "Research Methodology" in methodology_report
            assert "Study Design" in methodology_report
            
            print("   ✅ 方法论报告生成成功")
            print(f"      报告长度: {len(methodology_report)} 字符")
            print(f"      包含章节: {'✅' if 'Study Design' in methodology_report else '❌'}")
            print(f"      包含数据收集: {'✅' if 'Data Collection' in methodology_report else '❌'}")
            print(f"      包含分析计划: {'✅' if 'Data Analysis' in methodology_report else '❌'}")
            
            validation_results["report_generation"] = True
        except Exception as e:
            print(f"   ❌ 方法论报告生成失败: {e}")
            traceback.print_exc()
            return validation_results
        
        # 6. 验证方法论数据库完整性
        print("\n6️⃣ 验证方法论数据库...")
        
        try:
            methodologies = list(guide_system.methodology_database.keys())
            print(f"   ✅ 支持的方法论 ({len(methodologies)} 种):")
            for methodology in methodologies:
                guide = guide_system.methodology_database[methodology]
                print(f"      - {methodology.value}: {len(guide.steps)} 步骤, {len(guide.advantages)} 优点")
            
        except Exception as e:
            print(f"   ❌ 方法论数据库验证失败: {e}")
            traceback.print_exc()
        
        return validation_results
        
    except Exception as e:
        print(f"\n💥 验证过程中发生错误: {e}")
        traceback.print_exc()
        return validation_results


async def main():
    """主函数"""
    print("🚀 开始验证研究方法论指导系统")
    
    # 运行验证
    results = await validate_research_methodology_guide()
    
    # 显示结果
    passed_count = sum(results.values())
    total_count = len(results)
    
    print("\n" + "=" * 60)
    print("📊 验证结果:")
    for key, value in results.items():
        status = "✅ 通过" if value else "❌ 失败"
        item_name = {
            "imports": "组件导入",
            "initialization": "系统初始化", 
            "methodology_recommendation": "方法论推荐",
            "research_design": "研究设计创建",
            "report_generation": "报告生成"
        }.get(key, key)
        print(f"   {item_name}: {status}")
    
    print(f"\n总体结果: {passed_count}/{total_count} 项通过")
    
    if passed_count == total_count:
        print("🎉 研究方法论指导系统验证成功！")
        return True
    else:
        print("⚠️ 研究方法论指导系统验证部分失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)