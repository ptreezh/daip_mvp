"""
多角色AI协作编辑维基词条 - 完整演示
基于真实模型、真实角色的协同，过程可视化，增量编辑
"""

import asyncio
import tempfile
from pathlib import Path

from src.daip_live.model_provider.provider import LiteLLMProvider
from src.daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from src.daip_live.wiki.manager import WikiManager
from src.daip_live.wiki.visual_collaboration_display import (
    create_visual_collaboration_system,
)


async def setup_wiki_collaboration_environment():
    """设置维基协作环境"""

    # 使用临时目录进行演示
    temp_dir = Path(tempfile.mkdtemp(prefix="wiki_demo_"))

    # 创建模型提供者
    try:
        from src.daip_live.model_provider.provider_config import ProviderConfig

        config = ProviderConfig(
            model="ollama/llama3:instruct", temperature=0.7, max_tokens=1000
        )
        model_provider = LiteLLMProvider(config=config)
    except Exception:
        model_provider = None  # 后续使用模拟实现

    # 创建角色模型管理器
    try:
        role_model_manager = RoleModelManager()
    except Exception:
        role_model_manager = None

    # 创建其他依赖 - 使用None值来避免依赖问题
    session_manager = None  # SessionManager需要数据库管理器
    role_manager = None  # 我们可能用不到

    # 创建维基管理器
    wiki_manager = WikiManager(
        wiki_root=temp_dir,
        role_model_manager=role_model_manager,
        model_provider=model_provider,
    )

    return (
        wiki_manager,
        model_provider,
        role_model_manager,
        session_manager,
        role_manager,
        temp_dir,
    )


async def demonstrate_basic_wiki_creation(wiki_manager: WikiManager):
    """演示基本维基词条创建"""

    title = "量子计算基础概念"
    content = """# 量子计算基础概念

量子计算是一种基于量子力学原理的计算方式，使用量子比特（qubit）作为信息的基本单位。

## 概述
本词条介绍量子计算的基本概念和原理。
"""
    tags = ["量子计算", "计算机科学", "物理学"]

    page = wiki_manager.create_page(title, content, tags)

    return page


async def demonstrate_incremental_editing(wiki_manager: WikiManager):
    """演示增量编辑功能"""

    title = "量子计算基础概念"  # 使用上面创建的同名页面

    # 添加新技术发展章节
    new_section_content = (
        """量子计算在近年来取得了显著进展，特别是在量子纠错和量子优势方面。"""
    )
    updated_page = wiki_manager.update_page_incremental(
        title=title,
        section_title="技术发展",
        new_content=new_section_content,
        action="replace",
    )

    # 追加另一个章节
    applications_content = (
        """量子计算在密码学、优化问题和人工智能等领域具有巨大潜力。"""
    )
    updated_page = wiki_manager.update_page_incremental(
        title=title,
        section_title="应用领域",
        new_content=applications_content,
        action="append",
    )

    return updated_page


async def demonstrate_multi_role_collaboration(
    wiki_manager: WikiManager,
    model_provider,
    role_model_manager,
    session_manager,
    role_manager,
):
    """演示多角色协作编辑"""

    if model_provider is None:
        # 使用模拟模式创建协作
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager
        from src.daip_live.wiki.visual_collaboration_display import (
            VisualCollaborationDisplay,
        )

        # 创建一个可视化显示器
        visual_display = VisualCollaborationDisplay()

        title = "人工智能伦理问题"

        # 使用增强版维基管理器的协作功能
        EnhancedWikiManager(
            wiki_root=wiki_manager.wiki_root,
            role_model_manager=role_model_manager,
            model_provider=model_provider,
            session_manager=session_manager,
            role_manager=role_manager,
        )

        # 记录开始事件
        visual_display.log_event(
            "progress", None, "system", f"开始创建协作维基词条: {title}"
        )

        # 模拟多角色的贡献过程
        roles = ["domain_expert", "researcher", "editor", "critic"]
        topic = title

        for i, role in enumerate(roles):
            visual_display.log_event(
                "role_contribution",
                role,
                "main_content",
                f"角色 {role} 正在为 '{topic}' 贡献内容...",
                {"round": 1, "step": i + 1},
            )

            # 模拟角色贡献
            contribution = f"【{role}贡献】\n基于{role}的专业视角，{topic}需要考虑多个方面：技术实现、伦理影响、社会后果等。"  # noqa: E501

            # 记录贡献
            visual_display.log_event(
                "content_merge",
                role,
                "main_content",
                f"已合并{role}的贡献",
                {"contribution_length": len(contribution)},
            )

        # 创建一个维基页面来展示协作结果
        content = (
            f"# {title}\n\n本词条由多个AI角色协作创建，融合了不同领域的专业见解。\n\n"
        )
        for role in roles:
            content += f"## {role}的观点\n\n【{role}贡献】\n基于{role}的专业视角，{topic}需要考虑多个方面：技术实现、伦理影响、社会后果等。\n\n"  # noqa: E501

        tags = ["AI伦理", "技术哲学", "协作编辑"]
        page = wiki_manager.create_page(title, content, tags)

        visual_display.log_event(
            "progress", None, "system", f"协作完成! 共4个角色参与，创建词条: {title}"
        )

        # 显示协作摘要
        visual_display.get_collaboration_summary()

        # 显示详细日志
        visual_display.get_detailed_log()

        return page.file_path
    else:
        # 如果模型提供者可用，则使用真实的协作系统
        # 创建可视化协作系统
        collaborator, visual_display = create_visual_collaboration_system(
            model_provider
        )

        title = "人工智能伦理问题"
        participants = [
            "Researcher_Agent",
            "Writer_Agent",
            "Fact_Checker_Agent",
            "Editor_Agent",
        ]

        # 开始协作
        await collaborator.start_collaboration(
            title=title,
            participants=participants,
            initial_content=f"# {title}\n\n这是关于{title}的协作维基词条。",
        )

        # 运行多轮协作
        await visual_display.display_real_time_collaboration(
            collaborator=collaborator,
            title=title,
            participants=participants,
            total_rounds=2,
        )

        # 保存结果
        save_result = await collaborator.save_wiki_content()

        # 显示协作摘要
        collaborator.get_collaboration_summary()

        # 显示详细日志
        collaborator.get_detailed_log()

        return save_result


async def demonstrate_existing_page_collaboration(wiki_manager: WikiManager):
    """演示对已有页面的协作编辑"""

    title = "量子计算基础概念"  # 使用之前创建的页面

    # 获取已有页面内容
    existing_page = wiki_manager.get_page_by_title(title)
    if existing_page:
        # 使用协同编辑功能添加新内容
        updated_page = wiki_manager.collaborative_edit_page(
            title=title,
            editor_role="Researcher_Agent",
            edit_instruction="补充量子纠缠相关的最新研究成果",
            section_title="量子纠缠",
        )

    else:
        return None

    return updated_page


async def main():
    """主演示函数"""

    # 设置协作环境
    (
        wiki_manager,
        model_provider,
        role_model_manager,
        session_manager,
        role_manager,
        temp_dir,
    ) = await setup_wiki_collaboration_environment()

    try:
        # 演示1: 基本维基词条创建
        await demonstrate_basic_wiki_creation(wiki_manager)

        # 演示2: 增量编辑功能
        await demonstrate_incremental_editing(wiki_manager)

        # 演示3: 多角色协作编辑 (如果模型提供者可用)
        if model_provider:
            await demonstrate_multi_role_collaboration(
                wiki_manager,
                model_provider,
                role_model_manager,
                session_manager,
                role_manager,
            )
        else:
            # 使用模拟模式的协作演示
            title = "人工智能伦理问题"

            # 创建一个简单的页面
            content = f"# {title}\n\n这是关于{title}的维基词条。"
            wiki_manager.create_page(title, content, ["AI伦理", "技术哲学"])

            # 模拟多个角色的贡献
            roles_contributions = [
                ("Researcher", "人工智能伦理研究是当前AI发展的重要议题..."),
                ("Ethicist", "从伦理学角度看，AI的决策透明性至关重要..."),
                ("Technologist", "技术实现层面需要考虑算法偏见问题..."),
                ("PolicyExpert", "政策制定者需要建立相应的监管框架..."),
            ]

            for role, contribution in roles_contributions:
                # 追加到页面
                wiki_manager.update_page_incremental(
                    title, f"{role}观点", contribution, action="append"
                )

        # 演示4: 对已有页面的协作编辑
        await demonstrate_existing_page_collaboration(wiki_manager)

        # 总结

    except Exception:
        import traceback

        traceback.print_exc()

    finally:
        # 清理临时目录（可选）
        try:
            import shutil

            shutil.rmtree(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
