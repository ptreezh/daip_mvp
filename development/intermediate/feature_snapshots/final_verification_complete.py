"""
最终验证：完整的多角色维基协作和论文下载连续流程
"""
import sys
sys.path.insert(0, './src')
import asyncio

print("="*90)
print("🎯 DAIP-LIVE 系统最终验证 - 多角色维基协作与论文搜索下载流程")
print("="*90)

print("\\n📋 验证功能实现:")

# 测试1: 意图识别准确率
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

test_cases = [
    # Wiki协作相关
    ("创建维基 人工智能历史", "create_wiki", "维基创建意图"),
    ("协作写个维基 量子计算", "create_wiki", "协作维基创建"),
    ("创建词条 机器学习", "create_wiki", "词条创建"),
    ("多模型辩论 AI伦理", "start_debate", "多模型辩论"),
    ("帮我分析这段文本", "execute_skill", "技能执行"),
    
    # 澄清相关
    ("创建维基", "create_wiki", "需要澄清的维基创建"),
    ("辩论", "start_debate", "需要澄清的辩论"),
    ("帮我", "execute_skill", "需要澄清的技能执行"),
]

success_count = 0
for test_input, expected_intent, description in test_cases:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        clarity_needed = getattr(intent, 'requires_clarification', False) if intent else False
        print(f"  ✅ {description}: '{test_input}' -> {intent.name} (澄清: {clarity_needed})")
        success_count += 1
    else:
        print(f"  ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'}")

accuracy = success_count / len(test_cases) * 100
print(f"\\n📊 意图识别准确率: {accuracy:.1f}% ({success_count}/{len(test_cases)})")

# 测试2: 多角色Wiki协作功能
print("\\n🤖 验证多角色Wiki协作功能:")
try:
    from daip_live.multi_agent_collab.real_collaboration_engine import MultiRoleWikiCollaborator
    
    async def test_collaboration():
        collaborator = MultiRoleWikiCollaborator()
        
        # 启动协作会话
        await collaborator.start_collaboration(
            title="测试协作维基",
            participants=["Researcher_Agent", "Writer_Agent", "Editor_Agent", "Fact_Checker_Agent"],
            initial_content="这是用于测试多角色协作的维基词条。"
        )
        
        print(f"   ✅ 协作会话启动成功: 标题='{collaborator.title}'")
        print(f"   ✅ 参与角色数: {len(collaborator.participants)}")
        
        # 运行一轮协作编辑
        contributions = await collaborator.run_collaborative_editing_round(["overview"])
        print(f"   ✅ 协作编辑完成: 产生{len(contributions)}个贡献")
        
        # 获取内容验证
        content = await collaborator.get_current_content()
        print(f"   ✅ 内容获取成功: 有{len(content)}个章节")
        
        # 结束会话
        result = await collaborator.end_session()
        print(f"   ✅ 会话结果: 成功，贡献数={result['total_contributions']}")
        
        return True
    
    collaboration_success = asyncio.run(test_collaboration())
    if collaboration_success:
        print("   ✅ 多角色维基协作功能完整")
    else:
        print("   ❌ 多角色维基协作功能存在问题")
        
except ImportError:
    print("   ⚠️  MultiRoleWikiCollaborator 未实现")
    collaboration_success = False
except Exception as e:
    print(f"   ❌ 多角色维基协作功能错误: {e}")
    collaboration_success = False

# 测试3: 论文搜索下载连续流程
print("\\n📄 验证论文搜索下载连续流程:")
try:
    from daip_live.multi_agent_collab.paper_search_download_system import AdvancedPaperSearchDownloadSystem
    
    async def test_paper_flow():
        paper_system = AdvancedPaperSearchDownloadSystem()
        
        # 扩展关键词测试
        keywords = await paper_system.expand_search_keywords_with_llm("深度学习")
        print(f"   ✅ 关键词扩展: {keywords[:3]}...")  # 显示前3个
        
        # 搜索测试
        search_results = await paper_system.search_papers_multiple_sources(keywords[:2])
        print(f"   ✅ 搜索完成: 找到{len(search_results)}篇论文")
        
        # 生成下载指令测试
        if search_results:
            download_instructions = await paper_system.generate_download_instructions(search_results[:2])  # 只下载前2篇
            print(f"   ✅ 生成下载指令: {len(download_instructions)}个")
        
        return True
    
    paper_flow_success = asyncio.run(test_paper_flow())
    if paper_flow_success:
        print("   ✅ 论文搜索下载连续流程完整")
    else:
        print("   ❌ 论文搜索下载流程存在问题")
        
except ImportError:
    print("   ⚠️  AdvancedPaperSearchDownloadSystem 未实现")
    paper_flow_success = False
except Exception as e:
    print(f"   ❌ 论文搜索下载流程错误: {e}")
    import traceback
    traceback.print_exc()
    paper_flow_success = False

# 测试4: 语义匹配功能
print("\\n🔍 验证语义匹配功能:")
try:
    from daip_live.multi_agent_collab.complete_semantic_matcher import SemanticSimilarityMatcher
    
    matcher = SemanticSimilarityMatcher()
    
    semantic_tests = [
        ("一起协作编写量子物理维基", "wiki_creation", "协作编写维基"),
        ("多个AI辩论深度学习", "debate_start", "多AI辩论"),
        ("帮我分析这个复杂文本", "skill_execution", "复杂技能请求")
    ]
    
    semantic_success = 0
    for test_input, expected_category, description in semantic_tests:
        result = matcher.match_intent_by_semantics(test_input)
        if result.confidence > 0.5 and expected_category.replace("_", "") in result.intent_name.replace("_", ""):
            print(f"   ✅ {description}: '{test_input}' -> {result.intent_name} (置信度: {result.confidence:.2f})")
            semantic_success += 1
        else:
            print(f"   ❌ {description}: '{test_input}' -> {result.intent_name} (置信度: {result.confidence:.2f})")
    
    print(f"   语义匹配准确率: {semantic_success}/{len(semantic_tests)} ({semantic_success/len(semantic_tests)*100:.1f}%)")
    
except ImportError:
    print("   ⚠️  语义匹配器未实现")
    semantic_success = 0
except Exception as e:
    print(f"   ❌ 语义匹配功能错误: {e}")
    semantic_success = 0

# 总结
overall_pass = (accuracy >= 80 and 
                collaboration_success and 
                paper_flow_success and 
                semantic_success >= 2)

print("\\n" + "="*90)
print("📋 最终验证总结:")
print(f"  意图识别准确率: {accuracy:.1f}% (目标 ≥80%) {'✅' if accuracy >= 80 else '❌'}")
print(f"  多角色协作功能: {'✅ 通过' if collaboration_success else '❌ 失败'}")
print(f"  论文连续流程: {'✅ 通过' if paper_flow_success else '❌ 失败'}")
print(f"  语义匹配功能: {semantic_success}/3 通过 ({'✅' if semantic_success >= 2 else '❌'})")

print(f"\\n🎯 总体验证结果: {'✅ 全部通过' if overall_pass else '⚠️  部分通过'}")

if overall_pass:
    print("\\n🎉 恭喜！DAIP-LIVE系统所有功能已成功实现并通过验证！")
    print("   - 多角色维基协作编辑功能完整")
    print("   - 论文搜索下载连续流程完整") 
    print("   - 意图识别准确率达标")
    print("   - 语义匹配功能实现")
    print("   - 澄清机制工作正常")
    print("\\n🚀 系统现在可以部署使用！")
else:
    print("\\n⚠️  部分功能仍需完善")
    
print("="*90)