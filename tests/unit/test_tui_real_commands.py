"""TUI 真实命令测试：/compact、/knowledge sync、/knowledge stats、/claude_skills_sync。

策略：object.__new__ 绕过 Textual App 初始化，只测 handler 逻辑（纯方法），
mock _update_log_view 捕获输出，不启动 UI。
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from daip_live.tui.simplified_main import SimplifiedTUI


def _make_tui(**attrs) -> SimplifiedTUI:
    tui = object.__new__(SimplifiedTUI)
    # 默认属性
    tui._update_log_view = MagicMock()
    tui._update_system_log = MagicMock()
    tui._current_session_id = None
    tui._session_manager = None
    tui._memory_service = None
    tui._knowledge_manager = None
    for k, v in attrs.items():
        setattr(tui, k, v)
    return tui


def _captured(tui) -> list[str]:
    return [str(c[0][0]) for c in tui._update_log_view.call_args_list]


class TestEnsureSession:
    async def test_creates_session_when_none(self):
        """无会话时创建真实 session 并赋值 _current_session_id。"""
        sm = MagicMock()
        sm.list_sessions.return_value = []
        session = MagicMock()
        session.session_id = "sess_new_001"
        sm.create_session.return_value = session
        tui = _make_tui(_session_manager=sm)

        sid = await tui._ensure_session()

        assert sid == "sess_new_001"
        assert tui._current_session_id == "sess_new_001"
        sm.create_session.assert_called_once()

    async def test_reuses_existing_session(self):
        """已有未结束会话时复用（重启连续性）。"""
        sm = MagicMock()
        existing = MagicMock()
        existing.session_id = "sess_old_001"
        sm.list_sessions.return_value = [existing]
        tui = _make_tui(_session_manager=sm)

        sid = await tui._ensure_session()

        assert sid == "sess_old_001"
        sm.create_session.assert_not_called()

    async def test_falls_back_to_default_without_manager(self):
        """无 session_manager 时降级 default，不假装持久化。"""
        tui = _make_tui(_session_manager=None)
        sid = await tui._ensure_session()
        assert sid == "default"
        assert tui._current_session_id == "default"


class TestCompactCommand:
    async def test_compacts_real_session_background(self):
        """有会话+历史>5 时启动后台压缩任务，完成时输出量化信息。"""
        session = MagicMock()
        session.history = [MagicMock() for _ in range(10)]
        session.compressed_history = None
        sm = MagicMock()
        sm.get_session.return_value = session
        memory = AsyncMock()
        memory.compress_history = AsyncMock()

        async def fake_compress(s):
            s.compressed_history = "这是压缩后的结构化摘要。"

        memory.compress_history.side_effect = fake_compress
        tui = _make_tui(
            _current_session_id="sess_001",
            _session_manager=sm,
            _memory_service=memory,
        )
        tui._background_tasks = set()

        await tui._handle_compact_command("")

        # 立即返回（后台任务启动），UI 不阻塞
        memory.compress_history.assert_not_awaited()
        assert len(tui._background_tasks) == 1
        joined = " ".join(_captured(tui))
        assert "后台执行" in joined

        # 等后台任务完成并验证结果
        await asyncio.gather(*list(tui._background_tasks))
        memory.compress_history.assert_awaited_once_with(session)
        sm.save_session.assert_called_once_with(session)
        joined2 = " ".join(_captured(tui))
        assert "10 条历史" in joined2
        assert "压缩完成" in joined2

    async def test_no_session_honest_message(self):
        """无会话时诚实提示，不假装压缩。"""
        tui = _make_tui(_current_session_id=None, _session_manager=None)
        tui._background_tasks = set()
        await tui._handle_compact_command("")
        joined = " ".join(_captured(tui))
        assert "没有活动会话" in joined

    async def test_short_history_no_compress(self):
        """历史 <=5 条时提示无需压缩。"""
        session = MagicMock()
        session.history = [MagicMock() for _ in range(3)]
        sm = MagicMock()
        sm.get_session.return_value = session
        memory = AsyncMock()
        tui = _make_tui(
            _current_session_id="sess_001",
            _session_manager=sm,
            _memory_service=memory,
        )
        tui._background_tasks = set()
        await tui._handle_compact_command("")
        memory.compress_history.assert_not_called()
        joined = " ".join(_captured(tui))
        assert "无需压缩" in joined


class TestKnowledgeSyncCommand:
    async def test_sync_real_stats(self):
        """sync 真实调用 sync_knowledge_base 并输出真实数字。"""
        km = MagicMock()
        km.sync_knowledge_base = AsyncMock(
            return_value={"added": 5, "updated": 2, "removed": 1, "unchanged": 42}
        )
        tui = _make_tui(_knowledge_manager=km)
        await tui._handle_knowledge_sync()
        km.sync_knowledge_base.assert_awaited_once()
        joined = " ".join(_captured(tui))
        assert "新增 5" in joined
        assert "更新 2" in joined
        assert "删除 1" in joined
        assert "未变 42" in joined

    async def test_sync_no_manager_honest(self):
        """无 manager 时诚实提示。"""
        tui = _make_tui(_knowledge_manager=None)
        await tui._handle_knowledge_sync()
        joined = " ".join(_captured(tui))
        assert "未初始化" in joined


class TestKnowledgeStatsCommand:
    async def test_stats_real_data_no_hardcode(self):
        """stats 读真实 sources/faiss/磁盘占用，无硬编码数字。"""
        km = MagicMock()
        src = MagicMock()
        src.file_path = str(Path("tests") / "test_wiki_module.py")
        km.db_manager.get_all_knowledge_sources.return_value = [src]
        km.faiss_index = MagicMock()
        km.faiss_index.ntotal = 13
        tui = _make_tui(_knowledge_manager=km)

        await tui._handle_knowledge_stats()

        joined = " ".join(_captured(tui))
        assert "文档数量: 1" in joined
        assert "索引向量: 13" in joined
        # 确认无硬编码假数据
        assert "1,234" not in joined
        assert "456MB" not in joined

    async def test_stats_no_manager_honest(self):
        tui = _make_tui(_knowledge_manager=None)
        await tui._handle_knowledge_stats()
        joined = " ".join(_captured(tui))
        assert "未初始化" in joined


class TestClaudeSkillsSyncCommand:
    def test_scans_real_dir(self, tmp_path):
        """真实扫描 skills 目录并报告数量。"""
        (tmp_path / "skill_a").mkdir()
        (tmp_path / "skill_b").mkdir()
        (tmp_path / "skill_b" / "SKILL.md").write_text("x", encoding="utf-8")
        with patch.dict("os.environ", {"DAIP_SKILLS_DIR": str(tmp_path)}):
            tui = _make_tui()
            tui._handle_claude_skills_sync_command("")
        joined = " ".join(_captured(tui))
        assert "2 个技能" in joined

    def test_sync_alias_dispatches(self):
        """/sync 别名映射到 claude_skills_sync handler。"""
        tui = _make_tui()
        with patch.object(tui, "_handle_claude_skills_sync_command") as mock_handler:
            asyncio.run(tui._dispatch_command("sync", ""))
        mock_handler.assert_called_once_with("")

    def test_missing_dir_honest(self):
        """目录缺失时诚实提示，不假装同步成功。"""
        with patch.dict("os.environ", {"DAIP_SKILLS_DIR": "/nonexistent_dir_xyz"}):
            tui = _make_tui()
            tui._handle_claude_skills_sync_command("")
        joined = " ".join(_captured(tui))
        assert "未找到 Skills 目录" in joined
        assert "不假装同步成功" in joined
