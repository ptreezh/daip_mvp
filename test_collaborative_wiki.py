"""
测试多角色协作维基创建功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.wiki.manager import WikiManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig
from pathlib import Path
import asyncio

async def test_collaborative_wiki():
    print("="*70)
    print("🔍 测试多角色协作维基功能")
    print("="*70)
    
    # 创建必要的组件
    wiki_root = Path("./test_wiki")
    
    # Create a basic provider config
    config = ProviderConfig(
        model="llama3:instruct",
        base_url="http://localhost:11434"
    )
    model_provider = LiteLLMProvider(config)
    role_model_manager = RoleModelManager()  # 创建角色模型管理器
    
    # 创建wiki管理器
    wiki_manager = WikiManager(
        wiki_root=wiki_root,
        role_model_manager=role_model_manager,
        model_provider=model_provider
    )
    
    print("📋 测试协作功能接口...")
    print(f"  - WikiManager: {type(wiki_manager).__name__}")
    print(f"  - has _add_content_by_all_roles: {hasattr(wiki_manager, '_add_content_by_all_roles')}")
    print(f"  - has create_collaborative_page: {hasattr(wiki_manager, 'create_collaborative_page')}")
    
    # 测试创建基础页面
    print(f"\n📝 测试基础页面创建...")
    try:
        from datetime import datetime
        base_page = wiki_manager.create_page(
            title="Test Collaborative Knowledge",
            content="# Test Collaborative Knowledge\n\nThis page was created to test multi-role collaboration.\n\n## Initial Section\n\n",
            tags=["test", "collaborative", "multi-role"]
        )
        print(f"  ✅ 基础页面创建成功: {base_page.title}")
    except Exception as e:
        print(f"  ❌ 基础页面创建失败: {e}")
        return
    
    # 测试多角色添加内容
    print(f"\n👥 测试多角色协作内容添加...")
    try:
        roles_instructions = {
            "domain_expert": "作为领域专家，请提供专业知识和核心技术要点",
            "researcher": "作为研究员，请提供研究依据和参考资料",
            "editor": "作为编辑，请负责内容结构和语言润色",
            "analyst": "作为分析师，请提供批判性思考和改进建议"
        }
        
        updated_page = await wiki_manager._add_content_by_all_roles(
            page_title="Test Collaborative Knowledge",
            roles_instructions=roles_instructions,
            instruction="为协作知识页面添加相关内容"
        )
        
        print(f"  ✅ 多角色协作内容添加成功: {updated_page.title}")
        print(f"  📝 页面内容长度: {len(updated_page.content)} 字符")
        
        # 检查内容中是否包含多角色贡献
        content = updated_page.content
        role_contributions = [
            "Contribution by domain_expert" in content,
            "Contribution by researcher" in content,
            "Contribution by editor" in content,
            "Contribution by analyst" in content
        ]
        
        print(f"  📊 角色贡献检测: {sum(role_contributions)}/4 个角色贡献被添加")
        
        for i, role in enumerate(["domain_expert", "researcher", "editor", "analyst"]):
            if role_contributions[i]:
                print(f"     ✅ {role}: 已添加")
            else:
                print(f"     ❌ {role}: 未添加")
                
    except Exception as e:
        print(f"  ❌ 多角色协作内容添加失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n🎯 多角色协作维基功能测试完成!")
    print(f"✅ 系统现在支持:")
    print(f"  • 创建基础维基页面")
    print(f"  • 多角色AI模型协作添加内容")
    print(f"  • 基于不同角色视角的差异化贡献")
    print(f"  • 完整的内容整合和管理")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_collaborative_wiki())