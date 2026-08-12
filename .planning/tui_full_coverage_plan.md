# TUI 全命令全覆盖端到端走查计划（最严苛标准）

> 状态: 已批准待执行 | 创建: 2026-08-12 | 目标: 31 命令 × 全子命令 × 全交互 零遗漏
> 覆盖: dispatch → handler → 真实后端 → UI 反馈，逐命令五层验证

## 1. 命令全景清单（31 个 handler，来自 command_handlers 映射）

| # | 命令 | handler | 真实性 | 子命令 |
|---|------|---------|--------|--------|
| 1 | search | _handle_search_command | 待查 | - |
| 2 | debate | _handle_debate_command | 真实(CLI 复用) | start/history/search |
| 3 | help | _handle_help_command | 真实(push_screen) | show |
| 4 | claude_skills_info | ...info_command | 待查 | - |
| 5 | claude_skills_list | ...list_command | 真实(adapter) | - |
| 6 | claude_skills_run | ...run_command | 真实(adapter) | - |
| 7 | claude_skills_search | ...search_command | 待查 | - |
| 8 | claude_skills_sync | ...sync_command | ✅ 真实(已修) | - |
| 9 | sync (别名) | → sync | ✅ 真实 | - |
| 10 | clear | _handle_clear_command | 真实 | - |
| 11 | compact | _handle_compact_command | ✅ 真实(后台) | - |
| 12 | debate_history | ...history_command | ⚠️ 无 tracker 用模拟数据 | list/session-id |
| 13 | doc | _handle_doc_command | 真实(CLI 复用) | search/download |
| 14 | init | _handle_init_command | ❌ 纯打印 | - |
| 15 | intention | _handle_intention_command | 待查 | - |
| 16 | knowledge | _handle_knowledge_command | ✅ 真实(已修) | search/sync/stats |
| 17 | model | _handle_model_command | ⚠️ switch 模拟 | list/switch/status |
| 18 | pa | _handle_pa_command | 真实(executor) | - |
| 19 | permission | _handle_permission_command | ⚠️ 仅列表无控制 | <perm> <on/off> |
| 20 | project | _handle_project_command | ❌ 无实现 | create/list/status |
| 21 | quit | _handle_quit_command | 真实 | confirm |
| 22 | role | _handle_role_command | 真实(CLI 复用) | list/show/create/delete |
| 23 | run | _handle_run_command | 待查 | - |
| 24 | scaffold | _handle_scaffold_command | ❌ 纯打印 | - |
| 25 | session | _handle_session_command | 待查 | clear/list |
| 26 | shortcut | _handle_shortcut_command | 待查 | - |
| 27 | skill | _handle_skill_command | 待查 | - |
| 28 | copy | _handle_copy_command | 真实 | - |
| 29 | copy_recent | _handle_copy_recent_command | 真实 | N |
| 30 | todo | _handle_todo_command | 真实(memory_service) | list/add/complete |
| 31 | wiki | _handle_wiki_command | 真实(CLI 复用) | create/search/show/delete |

## 2. 分层验证标准（每命令 × 每子命令）

```
L1 可达   : dispatch 映射存在 + /help 可见 + autocomplete 可补全
L2 真实   : handler 调真实后端（无纯打印/模拟数据/硬编码）
L3 流畅   : 不阻塞 UI（长任务后台）、有进度反馈、错误可恢复
L4 端到端 : run_test 真实输入触发，输出非空且真实
L5 回归   : 全量 pytest 0 失败 + CI 绿
```

## 3. 待修复模拟命令（grill-down 发现）

| 命令 | 现状 | 修复方案 |
|------|------|---------|
| init | 纯打印"初始化完成" | 调真实 config/db 检查（container db_manager + config 存在性），输出真实状态 |
| scaffold | 纯打印"创建完成" | CLI 无 scaffold 命令 → 诚实提示"CLI 不支持 + 建议路径"，不做假创建 |
| project | 无实现 | CLI 无 project 命令 → 诚实提示 |
| model switch | 模拟切换 | 检查真实能力：能否持久化 config.yaml 的 default_model？能则实现，不能则诚实提示 |
| permission | 仅列表 | 检查 permission 系统真实接口，能则接，不能则诚实提示只读 |
| debate_history | 无 tracker 用模拟数据 | 移除模拟数据分支，无 tracker 时诚实提示 |

## 4. 端到端全覆盖测试（tests/unit/test_tui_full_coverage.py）

对 31 命令 × 主要子命令逐一驱动 dispatch，断言：
- 不抛异常（或抛可预期异常并有诚实输出）
- 输出非空
- 无模拟数据标记（"模拟"/"demo"/硬编码数字）

## 5. 成功标准

1. 31 命令全部可达 + 全部有测试覆盖
2. 模拟命令清零（修复或诚实降级）
3. 全量 pytest >=1810 通过，0 失败
4. CI 绿
