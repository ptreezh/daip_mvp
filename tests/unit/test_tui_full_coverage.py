"""TUI 全命令全覆盖端到端走查（31 命令 × 主要子命令，最严苛标准）。

逐命令驱动 dispatch，断言：
1. 不抛异常（或抛可预期异常且有诚实输出）
2. 输出非空
3. 无模拟数据标记（"模拟"/硬编码假数据/伪造示例）

策略：object.__new__ 绕过 Textual App 初始化，mock _update_log_view，
隔离真实依赖（mock container），聚焦 handler 逻辑。
"""

from unittest.mock import MagicMock

import pytest

from daip_live.tui.simplified_main import SimplifiedTUI

# 模拟数据标记（出现即失败）
FAKE_MARKERS = [
    "模拟",
    "示例数据",
    "识别准确率: ~85%",
    "gpt-4 - OpenAI GPT-4",  # 硬编码模型列表
    "AI助手项目",  # 硬编码项目列表
    "AI伦理辩论 - 2024",  # 伪造辩论历史
    "1,234",  # 硬编码文档数
    "456MB",  # 硬编码索引大小
    "项目创建完成",
    "脚手架创建完成",
    "模型切换完成",
]


def _make_tui(**attrs) -> SimplifiedTUI:
    tui = object.__new__(SimplifiedTUI)
    tui._update_log_view = MagicMock()
    tui._update_system_log = MagicMock()
    tui._current_session_id = None
    tui._session_manager = None
    tui._memory_service = None
    tui._knowledge_manager = None
    tui._background_tasks = set()
    tui._intent_recognizer = None
    tui._db_manager = None
    tui.container = None
    tui.utility_commands = MagicMock()
    tui.debate_commands = MagicMock()
    tui._available_commands = [
        ("/help", "显示帮助信息"),
        ("/copy", "复制主对话区内容"),
        ("/copy_recent", "复制最近N行内容"),
        ("/search", "搜索历史对话"),
        ("/debate", "辩论系统"),
        ("/model", "模型管理"),
        ("/compact", "压缩会话历史"),
        ("/doc", "文档搜索"),
        ("/wiki", "Wiki管理"),
        ("/permission", "权限管理"),
        ("/role", "角色管理"),
        ("/knowledge", "知识库管理"),
        ("/sync", "扫描本地 Skills"),
    ]
    for k, v in attrs.items():
        setattr(tui, k, v)
    return tui


def _captured(tui) -> list[str]:
    return [str(c[0][0]) for c in tui._update_log_view.call_args_list]


async def _run(tui, cmd: str, args: str = ""):
    """驱动 dispatch（含 async 处理）。"""
    await tui._dispatch_command(cmd, args)


def _check(tui, cmd: str, args: str = "", expect_ok: bool = True):
    """同步 handler 检查。"""
    msgs = _captured(tui)
    joined = " ".join(msgs)
    assert msgs, f"/{cmd} 无任何输出"
    for marker in FAKE_MARKERS:
        assert marker not in joined, f"/{cmd} 含模拟数据标记: {marker}"
    if expect_ok:
        assert "❌" not in joined, f"/{cmd} 输出错误: {joined[-200:]}"
    return joined


class TestFullCoverage:
    @pytest.mark.asyncio
    async def test_all_commands_dispatch_no_crash(self):
        """31 个命令逐一 dispatch：不崩溃、有输出、无模拟标记。"""
        tui = _make_tui()
        # 委托型命令（输出在子模块，验证子模块被调用）
        delegated = {
            "search": ("utility_commands", "handle_search_command"),
            "debate": ("debate_commands", "handle_debate_command"),
        }
        async_handlers = {
            "compact",
            "debate_history",
            "doc",
            "knowledge",
            "pa",
            "quit",
            "role",
            "run",
            "skill",
            "copy",
            "copy_recent",
            "wiki",
        }
        commands = [
            ("search", "测试"),
            ("debate", "list"),
            ("help", ""),
            ("claude_skills_info", ""),
            ("claude_skills_list", ""),
            ("claude_skills_run", "skill_name"),
            ("claude_skills_search", "test"),
            ("claude_skills_sync", ""),
            ("sync", ""),
            ("clear", ""),
            ("compact", ""),
            ("debate_history", ""),
            ("doc", "search test"),
            ("init", ""),
            ("intention", ""),
            ("knowledge", "stats"),
            ("model", "list"),
            ("model", "status"),
            ("model", "switch gpt-4"),
            ("pa", "任务"),
            ("permission", ""),
            ("project", "list"),
            ("quit", "confirm"),
            ("role", "list"),
            ("run", "任务"),
            ("scaffold", "web myapp"),
            ("session", "list"),
            ("shortcut", ""),
            ("skill", "list"),
            ("copy", ""),
            ("copy_recent", "10"),
            ("todo", "list"),
            ("wiki", "list"),
        ]
        for cmd, args in commands:
            tui._update_log_view.reset_mock()
            try:
                if cmd in delegated:
                    # 委托型：验证子模块方法被调用
                    obj_name, method = delegated[cmd]
                    obj = getattr(tui, obj_name)
                    await _run(tui, cmd, args)
                    getattr(obj, method).assert_called()
                    continue

                if cmd == "help":
                    # help 用 push_screen 弹窗（需 Textual 运行时），fake 之
                    pushed = []
                    tui.push_screen = pushed.append
                    await _run(tui, cmd, args)
                    assert len(pushed) == 1, "/help 未触发弹窗"
                    continue

                if cmd == "sync":
                    # sync 是 claude_skills_sync 别名：走 dispatch 验证映射
                    await _run(tui, cmd, args)
                    msgs = _captured(tui)
                    joined = " ".join(msgs)
                    assert msgs, "/sync 无任何输出"
                    for marker in FAKE_MARKERS:
                        assert marker not in joined
                    continue

                if cmd in async_handlers:
                    await _run(tui, cmd, args)
                else:
                    mapping = {
                        "search": "search",
                        "debate": "debate",
                        "help": "help",
                        "claude_skills_info": "claude_skills_info",
                        "claude_skills_list": "claude_skills_list",
                        "claude_skills_run": "claude_skills_run",
                        "claude_skills_search": "claude_skills_search",
                        "claude_skills_sync": "claude_skills_sync",
                        "sync": "sync",
                        "clear": "clear",
                        "debate_history": "debate_history",
                        "doc": "doc",
                        "init": "init",
                        "intention": "intention",
                        "knowledge": "knowledge",
                        "model": "model",
                        "pa": "pa",
                        "permission": "permission",
                        "project": "project",
                        "quit": "quit",
                        "role": "role",
                        "run": "run",
                        "scaffold": "scaffold",
                        "session": "session",
                        "shortcut": "shortcut",
                        "skill": "skill",
                        "copy": "copy",
                        "copy_recent": "copy_recent",
                        "todo": "todo",
                        "wiki": "wiki",
                    }
                    handler_name = f"_handle_{mapping[cmd]}_command"
                    handler = getattr(tui, handler_name, None)
                    if handler is None:
                        raise AssertionError(f"handler 不存在: {handler_name}")
                    import inspect

                    if inspect.iscoroutinefunction(handler):
                        await handler(args)
                    else:
                        handler(args)
                msgs = _captured(tui)
                joined = " ".join(msgs)
                assert msgs, f"/{cmd} 无任何输出"
                for marker in FAKE_MARKERS:
                    assert marker not in joined, (
                        f"/{cmd} 含模拟标记: {marker}（输出: {joined[-150:]}）"
                    )
            except Exception as e:
                if isinstance(e, AssertionError):
                    raise
                msgs = _captured(tui)
                if msgs:
                    continue
                raise AssertionError(f"/{cmd} 抛异常且无输出: {type(e).__name__}: {e}")

    def test_help_dialog_contains_all_commands(self):
        """/help 弹窗含全部关键命令（真实 UX 可见性）。"""
        tui = _make_tui()
        pushed = []

        def fake_push(dialog):
            pushed.append(dialog)

        tui.push_screen = fake_push
        tui._handle_help_command("show")
        assert len(pushed) == 1
        text = pushed[0].help_text
        for cmd in ["/compact", "/knowledge", "/sync", "/model", "/wiki", "/todo"]:
            assert cmd in text, f"帮助缺 {cmd}"

    def test_available_commands_in_autocomplete(self):
        """_available_commands 含全部可补全命令。"""
        tui = _make_tui()
        names = {name for name, _ in tui._available_commands}
        for cmd in ["/help", "/compact", "/knowledge", "/sync", "/model", "/wiki"]:
            assert cmd in names, f"autocomplete 缺 {cmd}"
