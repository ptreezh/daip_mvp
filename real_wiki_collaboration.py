#!/usr/bin/env python3
"""
真实的Wiki协同编辑功能
使用真实模型提供者，不使用任何模拟
按照配置文件设置的路径保存文件
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def create_real_wiki_collaboration():
    """创建真实的Wiki协同编辑"""
    print("🚀 真实Wiki协同编辑功能")
    print("=" * 50)
    print("⚠️  此功能使用真实AI模型，确保Ollama服务正在运行")
    print("=" * 50)

    try:
        # 导入真实组件
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.core.models import ProviderConfig
        from daip_live.config import config_manager

        # 检查Ollama服务
        import subprocess
        try:
            result = subprocess.run(['ollama', 'list'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ Ollama服务未运行，请先启动Ollama服务")
                print("   启动命令: ollama serve")
                return False
            print("✅ Ollama服务正在运行")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Ollama未安装或未运行，请先安装并启动Ollama")
            return False

        # 使用配置文件设置
        config = config_manager.get_config()
        model_config = config.model_dump().get('llm_provider', {})
        wiki_pages_dir = config.model_dump()['wiki']['pages_directory']
        roles_dir = config.model_dump()['role_manager']['roles_dir']

        print(f"📋 使用模型: {model_config.get('default_model', 'ollama/llama3')}")
        print(f"📁 Wiki保存路径: {wiki_pages_dir}")
        print(f"👥 角色配置路径: {roles_dir}")

        # 创建真实的模型提供者
        provider_config = ProviderConfig(
            model=model_config.get('default_model', 'ollama/llama3'),
            temperature=0.7,
            max_tokens=1500
        )
        real_provider = LiteLLMProvider(provider_config)

        # 创建真实的角色管理器
        real_role_manager = RoleModelManager(roles_dir)

        # 确保Wiki目录存在
        wiki_root = Path(wiki_pages_dir)
        wiki_root.mkdir(parents=True, exist_ok=True)

        # 创建EnhancedWikiManager
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=wiki_root,
            role_model_manager=real_role_manager,
            model_provider=real_provider
        )

        print("✅ 真实协作系统初始化完成")

        # 定义协作主题
        title = "量子计算基础原理"
        topic = "量子计算的基本概念、核心算法和实际应用前景"

        print(f"\n📝 开始创建协作Wiki:")
        print(f"  标题: {title}")
        print(f"  主题: {topic}")

        # 执行真实的协作创建
        wiki_page = await enhanced_wiki.create_collaborative_wiki(
            title=title,
            topic=topic,
            roles=["domain_expert", "researcher", "editor"],
            rounds=1,
            show_progress=True
        )

        # 显示结果
        print(f"\n🎉 真实协作Wiki创建成功！")
        print(f"📄 标题: {wiki_page.title}")
        print(f"📏 内容长度: {len(wiki_page.content)} 字符")
        print(f"📁 保存位置: {wiki_page.file_path}")
        print(f"⏱️  创建时间: {wiki_page.created_at}")

        # 验证文件已保存
        if wiki_page.file_path.exists():
            print(f"✅ 文件已成功保存到配置路径")
            print(f"📂 可在文件管理器中查看: {wiki_page.file_path.absolute()}")
        else:
            print(f"❌ 文件保存失败")
            return False

        # 显示内容预览
        print(f"\n📖 内容预览:")
        print("-" * 50)
        preview_length = min(800, len(wiki_page.content))
        preview = wiki_page.content[:preview_length]
        if len(wiki_page.content) > preview_length:
            preview += "..."
        print(preview)
        print("-" * 50)

        return True

    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 协作创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = asyncio.run(create_real_wiki_collaboration())

    if success:
        print(f"\n✨ 真实Wiki协同编辑完成！")
        print(f"💡 使用说明:")
        print(f"   - 生成的Wiki文件保存在config.yaml配置的路径中")
        print(f"   - 内容使用真实AI模型生成，非模拟内容")
        print(f"   - 支持多角色协作，每个角色使用其专业视角")
        print(f"   - 进度条显示已优化，无错误百分比")
        print(f"   - 可以用任何Markdown编辑器查看生成的文件")
    else:
        print(f"\n❌ 真实Wiki协同编辑失败")
        print(f"💡 故障排除:")
        print(f"   - 确保Ollama服务正在运行: ollama serve")
        print(f"   - 检查config.yaml配置是否正确")
        print(f"   - 确保已下载AI模型: ollama pull llama3")

if __name__ == "__main__":
    main()