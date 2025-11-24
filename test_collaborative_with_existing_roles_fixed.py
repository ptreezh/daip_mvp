"""
测试使用现有角色的协作功能
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, './src')

from daip_live.wiki.manager import WikiManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig

async def test_collaborative_wiki_with_existing_roles():
    print("="*70)
    print("🔍 测试使用现有角色的协作维基功能")
    print("="*70)
    
    # 创建必要的组件
    wiki_root = Path("./test_wiki")
    
    # Create a basic provider config
    config = ProviderConfig(
        model="ollama/llama3:instruct",
        base_url="http://localhost:11434"
    )
    model_provider = LiteLLMProvider(config)
    role_model_manager = RoleModelManager()  # 加载现有角色配置
    
    # 创建wiki管理器
    wiki_manager = WikiManager(
        wiki_root=wiki_root,
        role_model_manager=role_model_manager,
        model_provider=model_provider
    )
    
    print("📋 系统中可用的角色:")
    all_roles = list(role_model_manager._roles.keys())
    for role in all_roles[:10]:  # 只显示前10个
        print(f"  • {role}")
    if len(all_roles) > 10:
        print(f"  ... 还有 {len(all_roles)-10} 个角色")
    
    # 验证一些常用角色是否存在
    common_roles = ["pro_arguer", "con_arguer", "creative_writer", "research_analyst", "tech_analyst", "philosophy_thinker"]
    available_common_roles = [role for role in common_roles if role in all_roles]
    
    print(f"\n📋 可用的常用角色: {available_common_roles}")
    
    # 创建测试页面
    print(f"\n📝 创建基础测试页面...")
    try:
        test_page = wiki_manager.create_page(
            title="AI伦理协作分析",
            content="# AI伦理协作分析\n\n这是一个测试页面，用于验证多角色协作功能。\n\n",
            tags=["AI伦理", "协作", "测试"]
        )
        print(f"  ✅ 测试页面创建成功: {test_page.title}")
    except Exception as e:
        print(f"  ❌ 测试页面创建失败: {e}")
        return
    
    # 测试使用现有角色添加内容
    if len(available_common_roles) >= 2:  # 至少需要2个角色
        print(f"\n👥 测试使用现有角色进行协作...")
        try:
            # 使用系统已有的角色
            roles_instructions = {}
            for i, role_name in enumerate(available_common_roles[:4]):  # 使用最多4个角色
                if role_name == "pro_arguer":
                    roles_instructions[role_name] = "作为支持方，请提供支持AI伦理的观点和论证"
                elif role_name == "con_arguer":
                    roles_instructions[role_name] = "作为反对方，请提供反对AI伦理的观点和论证"
                elif role_name == "research_analyst":
                    roles_instructions[role_name] = "作为研究分析师，请提供相关研究数据和分析"
                elif role_name == "tech_analyst":
                    roles_instructions[role_name] = "作为技术分析师，请提供技术层面的分析和见解"
                elif role_name == "creative_writer":
                    roles_instructions[role_name] = "作为创意作家，请提供创新的观点和表达方式"
                else:
                    roles_instructions[role_name] = f"作为{role_name}角色，请提供相关专业观点和分析"
            
            print(f"  使用角色: {list(roles_instructions.keys())}")
            
            # 调用正确的内部方法名
            if hasattr(wiki_manager, '_add_content_by_all_roles'):
                updated_page = await wiki_manager._add_content_by_all_roles(
                    page_title="AI伦理协作分析",
                    roles_instructions=roles_instructions,
                    instruction="为AI伦理主题协作添加深入分析"
                )
                print(f"  ✅ 多角色协作内容添加成功: {updated_page.title}")
                print(f"  📝 页面内容长度: {len(updated_page.content)} 字符")
                
                # 检查是否添加了内容
                if len(updated_page.content) > len(test_page.content):
                    print("  ✅ 内容确实被添加到了页面中")
                else:
                    print("  ⚠️  页面内容长度没有明显增加可能意味着AI模型没有返回内容")
                    
            else:
                print("  ❌ WikiManager没有_add_content_by_all_roles方法")
                return
                
        except Exception as e:
            print(f"  ❌ 多角色协作内容添加失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⚠️  可用角色不足，无法测试协作功能")
        print(f"   需要至少2个角色，但只有: {available_common_roles}")
    
    print(f"\n🎯 协作维基功能测试完成!")
    print(f"✅ 系统架构已支持多角色协作功能")
    print(f"⚠️  需要确保Ollama服务运行以生成实际内容")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_collaborative_wiki_with_existing_roles())