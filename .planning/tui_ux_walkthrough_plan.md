# TUI 分层交互体验测试计划（全流程走查，最严苛标准）

> 状态: 已批准待执行 | 创建: 2026-08-12 | 目标: TUI 完全可用、可信、可交付
> 范围: `src/daip_live/tui/simplified_main.py`（`daip run` 真实入口）

## 0. 分层原则

交互体验按 4 层递进验证，每层通过后才进入下一层：

```
L1 命令可达性    → 命令能被用户输入触发（dispatch 映射/别名/补全/帮助）
L2 功能真实性    → handler 调真实后端，无 mock/硬编码/假完成
L3 交互流畅性    → 不阻塞 UI、有进度反馈、错误可恢复
L4 端到端走查    → Textual run_test 模拟真实用户输入序列，全链路通过
```

## 1. L1 命令可达性检查清单

| # | 命令 | dispatch 映射 | 别名 | autocomplete | /help 条目 |
|---|------|--------------|------|--------------|-----------|
| 1 | /compact | ✅ L1322 | - | ✅ | ✅ L2318 |
| 2 | /knowledge | ✅ L1327 | - | ✅ sync/search | ✅ L2313+ |
| 3 | /knowledge sync | 子命令 | - | ✅ | ✅ 2026-08-12 |
| 4 | /knowledge stats | 子命令 | - | 待加 stats | ✅ 2026-08-12 |
| 5 | /claude_skills_sync | ✅ L1320 | /sync ✅ | 待加 | ✅ L2330 |
| 6 | /help | ✅ | - | ✅ | - |

**待补**: autocomplete `_get_knowledge_suggestions` 加 stats；`_available_commands` 已加 /sync。

## 2. L2 功能真实性验证（每项：源码引用 + 单测 + 手工证据）

| 命令 | 真实后端 | 无假数据证据 |
|------|---------|-------------|
| /compact | memory_service.compress_history（修 agenerate bug 后） | 输出真实 history 条数→摘要字数 |
| /knowledge sync | knowledge_manager.sync_knowledge_base() | 输出真实 added/updated/removed/unchanged |
| /knowledge stats | get_all_knowledge_sources + faiss ntotal + 磁盘 | 无硬编码数字 |
| /sync | 真实目录扫描（DAIP_SKILLS_DIR/~/.claude/skills） | 缺失时诚实提示 |

## 3. L3 交互流畅性

| 检查 | 标准 | 验证 |
|------|------|------|
| /compact 不阻塞 | 后台任务（asyncio.create_task + _background_tasks） | 单测断言立即返回 + 后台完成 |
| 进度反馈 | 命令启动即输出"进行中" | 单测断言 |
| 错误可恢复 | 失败显示红色错误不崩溃 | 单测断言 except 路径 |
| 会话缺失 | 诚实提示"无会话" | 单测 |

## 4. L4 端到端走查（Textual run_test 真实交互序列）

模拟用户真实输入，逐步走查：

```
1. daip run 启动 → TUI 挂载（无异常）
2. 输入普通文本对话 → 创建真实 session（_current_session_id 非 None）
3. /compact → 启动后台压缩（短历史提示无需压缩）
4. /knowledge stats → 真实文档/索引/磁盘
5. /sync → 扫描 Skills 目录（或诚实提示）
6. /knowledge sync → 真实同步统计
7. /help → 显示含所有新命令
8. Ctrl+E 退出 → 正常关闭
```

## 5. 量化验收标准

1. `pytest tests/unit/test_tui_real_commands.py` 13 项全过
2. `pytest tests/` 全量 >=1803 通过，0 失败
3. Textual run_test 端到端序列无异常（L4）
4. 无任何 mock/硬编码/假完成残留（rg 扫描 4 处旧 handler 消息确认清零）
5. lint/format 全过

## 6. 执行顺序

1. ✅ 完成后台任务化（/compact）— 已提交
2. ✅ /sync 别名 + autocomplete + help — 已提交
3. 补 autocomplete stats + /sync 子命令补全
4. 执行 L4 端到端 run_test 走查（写 tests/unit/test_tui_full_flow.py）
5. 全量回归 + CI
