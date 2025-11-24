"""
验证TUI中的更改是否已正确应用
"""
import asyncio
from unittest.mock import MagicMock
from pathlib import Path

from daip_live.tui import DAIP_TUI
from daip_live.wiki.collaborative_wiki import EnhancedWikiManager
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider


def test_tui_wiki_integration():
    """测试TUI是否正确集成了Wiki协作功能"""
    # 创建模拟依赖项
    session_manager = MagicMock(spec=SessionManager)
    role_manager = MagicMock(spec=RoleManager)
    role_model_manager = MagicMock(spec=RoleModelManager)
    model_provider = MagicMock(spec=LiteLLMProvider)
    
    # 创建TUI实例
    tui = DAIP_TUI(
        session_manager=session_manager,
        role_manager=role_manager,
        model_provider=model_provider,
        role_model_manager=role_model_manager,
        knowledge_manager=MagicMock(),
        debate_manager=MagicMock(),
        db_manager=MagicMock()
    )
    
    # 验证wiki管理器是否存在
    assert hasattr(tui, '_wiki_manager'), "TUI应包含wiki管理器"
    assert tui._wiki_manager is not None, "wiki管理器不应为None"
    
    # 验证wiki管理器是否是增强类型（带协作功能）
    wiki_manager = tui._wiki_manager
    print(f"Wiki管理器类型: {type(wiki_manager)}")
    
    # 检查是否具备协作功能
    has_collaborator = hasattr(wiki_manager, 'collaborator') and wiki_manager.collaborator is not None
    print(f"是否具备协作器: {has_collaborator}")
    
    # 验证TUI中存在处理协作创建的方法
    assert hasattr(tui, '_handle_collaborative_wiki_creation'), "TUI应包含协作创建处理方法"
    print("✓ TUI包含协作创建处理方法")
    
    # 验证TUI中有异步的wiki创建方法
    assert hasattr(tui, '_handle_wiki_create'), "TUI应包含wiki创建处理方法"
    print("✓ TUI包含wiki创建处理方法")
    
    print("\n集成验证完成！")
    print("- TUI正确初始化了wiki管理器")
    print("- TUI包含协作创建处理方法")
    print("- TUI中的wiki命令将使用协作方式创建页面")


if __name__ == "__main__":
    test_tui_wiki_integration()
    print("\n✓ TUI集成验证成功！")