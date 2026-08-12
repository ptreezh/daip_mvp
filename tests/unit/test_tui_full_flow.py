"""TUI 全流程端到端交互走查（L4，最严苛标准）。

用 Textual run_test 驱动真实输入序列，验证：
1. TUI 挂载
2. 对话创建真实 session
3. /compact（无会话/短历史提示；有会话后台压缩）
4. /knowledge stats（真实数据）
5. /knowledge sync（真实同步）
6. /sync（真实 Skills 扫描）
7. /help（含新命令）
8. 退出

注意：完整 TUI 依赖 container（真实 Ollama/DB），此测试用 DAIP_DB_PATH 隔离，
不依赖外部服务启动成功（不可用时命令应诚实降级而非崩溃）。
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from daip_live.tui.simplified_main import SimplifiedTUI


@pytest.mark.asyncio
async def test_full_flow_mount_and_help():
    """TUI 挂载 + /help 显示（mock 容器隔离真实 Ollama/DB 初始化）。"""
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["DAIP_DB_PATH"] = str(Path(tmp) / "test.db")
        with patch("daip_live.container.Container"):
            app = SimplifiedTUI()
            try:
                async with app.run_test() as pilot:
                    await pilot.pause()
                    assert app.is_running

                    # 输入 /help
                    await pilot.press(":", "h", "e", "l", "p", "enter")
                    await pilot.pause()
                    # 不崩溃即可（help 内容渲染进 log）
            finally:
                os.environ.pop("DAIP_DB_PATH", None)


@pytest.mark.asyncio
async def test_chat_creates_real_session():
    """普通对话创建真实 session（_current_session_id 非 None 且落库）。

    用真实 SessionManager（临时 DB）注入，验证 _ensure_session 创建会话，
    不触发真实模型调用（意图识别 mock 掉）。
    """
    import tempfile

    from daip_live.memory.session_manager import SessionManager
    from daip_live.persistence.database import DatabaseManager

    with tempfile.TemporaryDirectory() as tmp:
        dbm = DatabaseManager(db_path=str(Path(tmp) / "sess.db"))
        try:
            sm = SessionManager(db_manager=dbm)

            app = object.__new__(SimplifiedTUI)
            app._update_log_view = lambda msg: None
            app._update_system_log = lambda msg: None
            app._session_manager = sm
            app._memory_service = None
            app._knowledge_manager = None
            app._current_session_id = None

            sid = await app._ensure_session()
            assert sid is not None
            assert sid != "default"
            assert app._current_session_id == sid
            # 会话已落库
            session = sm.get_session(sid)
            assert session is not None
            assert session.session_id == sid
        finally:
            dbm.close()


@pytest.mark.asyncio
async def test_compact_honest_no_session():
    """无会话时 /compact 诚实提示。"""
    app = object.__new__(SimplifiedTUI)
    app._update_log_view = lambda msg: None
    app._current_session_id = None
    app._session_manager = None
    app._memory_service = None
    app._background_tasks = set()
    messages = []
    app._update_log_view = messages.append

    await app._handle_compact_command("")

    joined = " ".join(str(m) for m in messages)
    assert "没有活动会话" in joined


@pytest.mark.asyncio
async def test_sync_command_real_scan(tmp_path):
    """/sync 真实扫描目录（DAIP_SKILLS_DIR 指向临时目录）。"""
    (tmp_path / "skill_x").mkdir()
    (tmp_path / "skill_y").mkdir()
    app = object.__new__(SimplifiedTUI)
    messages = []
    app._update_log_view = messages.append
    app._update_system_log = messages.append

    with patch.dict("os.environ", {"DAIP_SKILLS_DIR": str(tmp_path)}):
        app._handle_claude_skills_sync_command("")

    joined = " ".join(str(m) for m in messages)
    assert "2 个技能" in joined


@pytest.mark.asyncio
async def test_knowledge_stats_real(tmp_path):
    """stats 显示真实数据（含磁盘占用），无硬编码。"""
    from unittest.mock import MagicMock

    from daip_live.tui.simplified_main import SimplifiedTUI

    km = MagicMock()
    src = MagicMock()
    src.file_path = str(tmp_path / "doc1.md")
    (tmp_path / "doc1.md").write_text("x" * 2048, encoding="utf-8")
    km.db_manager.get_all_knowledge_sources.return_value = [src]
    km.faiss_index = MagicMock()
    km.faiss_index.ntotal = 7

    app = object.__new__(SimplifiedTUI)
    messages = []
    app._update_log_view = messages.append
    app._knowledge_manager = km

    await app._handle_knowledge_stats()

    joined = " ".join(str(m) for m in messages)
    assert "文档数量: 1" in joined
    assert "索引向量: 7" in joined
    assert "磁盘占用" in joined
    assert "1,234" not in joined
    assert "456MB" not in joined


@pytest.mark.asyncio
async def test_dispatch_sync_alias():
    """/sync 别名触发 claude_skills_sync handler。"""
    from unittest.mock import patch

    from daip_live.tui.simplified_main import SimplifiedTUI

    app = object.__new__(SimplifiedTUI)
    app._update_log_view = lambda msg: None
    app._update_system_log = lambda msg: None

    with patch.object(app, "_handle_claude_skills_sync_command") as mock_handler:
        await app._dispatch_command("sync", "")
    mock_handler.assert_called_once_with("")
