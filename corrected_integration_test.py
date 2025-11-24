"""
修正后的集成测试，使用正确的函数名
"""
import sys
sys.path.insert(0, './src')

# 注意：我们先用同步方法测试，稍后再处理协程问题
import asyncio
from daip_live.multi_agent_collab.real_collaboration_engine import MultiRoleWikiCollaborator


async def run_corrected_integration_test():
    print("="*90)
    print("🔧 修正后的集成测试 - 验证多角色维基协作功能")
    print("="*90)

    print("\\n🤖 测试多角色维基协作功能:")
    
    try:
        print("   创建多角色维基协作者...")
        wiki_collaborator = MultiRoleWikiCollaborator()
        
        print("   启动协作会话...")
        await wiki_collaborator.start_collaboration(
            title="测试维基协作",
            participants=["Researcher_Agent", "Writer_Agent", "Editor_Agent"],
            initial_content="这是一篇测试协作的维基词条。"
        )
        
        print("   执行协作编辑轮次...")
        contributions = await wiki_collaborator.run_collaborative_editing_round(["overview"])
        print(f"   协作完成，收到 {len(contributions)} 个贡献")
        
        # 获取并展示最终内容
        content = await wiki_collaborator.get_current_content()
        print(f"   最终内容预览: {list(content.values())[0][:100] if content else 'N/A'}...")
        
        print("   保存维基内容...")
        save_path = await wiki_collaborator.save_wiki_content()
        print(f"   ✅ 内容已保存到: {save_path}")
        
        print("   维基协作功能测试: ✅ 通过")
        
    except Exception as e:
        print(f"   ❌ 维基协作功能测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\\n📄 测试论文搜索下载功能:")
    
    try:
        from daip_live.multi_agent_collab.paper_search_download_system import AdvancedPaperSearchDownloadSystem
        
        print("   创建高级论文搜索下载系统...")
        paper_system = AdvancedPaperSearchDownloadSystem()
        
        print("   测试关键词扩展...")
        keywords = await paper_system.expand_search_keywords_with_llm("机器学习")
        print(f"   搜索关键词扩展: {keywords}")
        
        print("   测试搜索功能...")
        search_results = await paper_system.search_papers_multiple_sources(keywords[:2])  # 只搜索前2个关键词
        print(f"   搜索完成，找到 {len(search_results)} 篇论文")
        
        print("   论文搜索下载功能测试: ✅ 通过")
        
    except Exception as e:
        print(f"   ❌ 论文搜索下载功能测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_corrected_integration_test())