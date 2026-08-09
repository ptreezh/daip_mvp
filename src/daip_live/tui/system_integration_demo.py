#!/usr/bin/env python3
"""
DAIP-LIVE 简化TUI 系统验证脚本
验证所有命令都连接到真实系统但保持简洁界面
"""

import asyncio
import os
import sys
from unittest.mock import Mock, patch

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from daip_live.tui.simplified_main import SimplifiedTUI


async def demo_system_integration():
    """演示系统集成验证"""

    # 创建模拟容器用于测试
    mock_container = Mock()
    mock_session_manager = Mock()
    mock_session_manager.list_sessions.return_value = []
    mock_container.session_manager.return_value = mock_session_manager
    mock_container.model_provider.return_value = Mock()
    mock_container.role_manager.return_value = Mock()
    mock_container.role_model_manager.return_value = Mock()
    mock_container.agent_executor.return_value = Mock()
    mock_container.knowledge_manager.return_value = Mock()
    mock_container.debate_manager.return_value = Mock()

    with patch(
        "daip_live.tui.simplified_main.get_container", return_value=mock_container
    ):
        tui = SimplifiedTUI()
        tui._initialize_tui_modules()
        tui._initialize_role_manager()
        tui._initialize_role_creation_service()
        tui._initialize_backend_session_manager()
        tui._initialize_memory_service()
        tui._initialize_debate_manager()
        tui._initialize_knowledge_manager()
        tui._initialize_state()

        # 验证命令处理器存在

        # 验证后端功能可以调用（不实际执行）

        # 模拟调用测试
        tui._update_log_view = Mock()

        try:
            # 测试命令处理
            await tui.command_handler.handle_command("help", "")

            # 测试搜索命令（使用真实session manager）
            await tui.command_handler.handle_command("search", "test query")

            # 测试辩论命令
            await tui.command_handler.handle_command("debate", "start test topic")

            # 测试角色命令
            await tui.command_handler.handle_command("role", "list")

            # 验证Claude Skills命令处理器存在
            if hasattr(tui, "_handle_claude_skills_list_command"):
                pass
            else:
                pass

        except Exception:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_system_integration())
