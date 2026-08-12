# TUI 模拟命令真实化方案（/sync /compact + 会话系统修复）

> 状态: 已批准待执行 | 创建: 2026-08-11 | 对齐目标: 生产交付、零假功能
> 范围: TUI（`src/daip_live/tui/simplified_main.py`）+ memory 压缩 + 知识库同步

## 1. 背景与问题（全部实测证据）

grill-down 压力测试轮次后，用户要求消灭 TUI 模拟命令。实测确认 4 处假实现：

| 位置 | 现状 | 证据 |
|------|------|------|
| `_handle_compact_command` (L2518-2529) | 纯模拟：打印"压缩完成"，无真实压缩；且 `_current_session_id` 恒 None 使 `if self._current_session_id` 恒 False，永远走"无活动会话" | simplified_main.py |
| `_handle_claude_skills_sync_command` (L2499-2505) | 纯模拟：打印"同步完成" | simplified_main.py |
| `_handle_knowledge_command` sync 分支 (L2697-2699) | 纯模拟：打印"知识库同步完成" | simplified_main.py |
| `_handle_knowledge_command` stats 分支 (L2700-2703) | **硬编码假数据**：1,234 文档/456MB | simplified_main.py |

附带缺陷（真实会话系统断连）：
- `_current_session_id` 仅在 L252 初始化为 None，**从未赋值** → 对话用 "default" 兜底（L1422），compact 永远无会话可压
- `memory/service.py:50 compress_history` 用 `summary, _ = await self.model_provider.generate(prompt)` 解包 async generator → **必然 TypeError，实际不可用**

## 2. 可对接的真实能力（已验证存在）

| 能力 | 入口 | 状态 |
|------|------|------|
| 会话压缩 | `MemoryService.compress_history(session)` (memory/service.py:50) | 存在但 generate bug 需修 |
| 会话读取 | `SessionManager.get_session(session_id)` (session_manager.py:78) | 可用 |
| 会话创建/保存 | `SessionManager.create_session/save_session` | 可用 |
| 知识库同步 | `KnowledgeManager.sync_knowledge_base()` (knowledge/manager.py:104) | 可用（CLI 已验证） |
| 知识库状态 | `KnowledgeManager.db_manager.get_all_knowledge_sources()` + `faiss_index.ntotal` | 可用（CLI status 已验证） |

## 3. 方案设计

### 3.1 会话系统真实化（前置，compact 依赖）
**问题**：TUI 对话不创建 session，`_current_session_id` 恒 None。
**方案**：
- TUI 首次对话（`_handle_chat_input`）时创建真实 session：`self._session_manager.create_session(...)` → 存 `_current_session_id`，后续对话 `add_dialogue_turn` 写入
- 从 container 获取 `session_manager` + `memory_service`（container 已有注册，TUI `_initialize_backend_session_manager` 已取 session_manager）
- 已有 session（重启 TUI）通过 `list_sessions()` 恢复最近一个

### 3.2 `/compact` 真实化
**方案**：
- 修 `compress_history` 的 generate→agenerate bug
- `_handle_compact_command`：取 `_current_session_id` → `get_session` → 有 history 则 `memory_service.compress_history(session)` + `save_session`，输出真实摘要长度/历史条数；无会话则诚实提示
- 量化输出：压缩前后 history 条数、摘要字数

### 3.3 `/knowledge sync` 真实化
**方案**：
- 调 `KnowledgeManager.sync_knowledge_base()`（复用 CLI 的 `_build_knowledge_manager` 构造逻辑，含 `DAIP_DB_PATH`/`DAIP_KNOWLEDGE_DIR` 隔离）
- 输出真实统计：added/updated/removed/unchanged
- 异步执行（`asyncio.create_task`），进度提示

### 3.4 `/knowledge stats` 真实化
**方案**：
- 读 `get_all_knowledge_sources()`（真实计数）+ `faiss_index.ntotal`（真实索引数）+ 磁盘占用（sum file sizes）
- 删除硬编码 1,234/456MB

### 3.5 `/claude_skills_sync` 决策
**问题**：Claude Skills 是用户级目录（`~/.claude/skills`），不属于本项目数据。
**方案**（诚实化）：
- 扫描真实 skills 目录（`~/.claude/skills` 或 `DAIP_SKILLS_DIR` env 覆盖），列出数量与最近修改
- 若目录不存在/不可访问 → 诚实提示"未找到 Skills 目录"，不假装同步成功
- 不做网络下载（无官方 sync API；保持本地扫描语义）

## 4. 执行步骤（TDD，每步可验证）

| # | 任务 | 文件 | 验证 |
|---|------|------|------|
| 1 | 修 `compress_history` generate→agenerate | memory/service.py | 单测：mock agenerate 返回摘要，断言 session.compressed_history 更新 |
| 2 | TUI 会话创建/复用（_handle_chat_input 时 create_session） | simplified_main.py | 单测：对话后 _current_session_id 非 None，session 落库 |
| 3 | `/compact` 接真实压缩 | simplified_main.py | 单测：有 session+history → 调 compress_history，输出摘要信息 |
| 4 | `/knowledge sync` 接真实 sync | simplified_main.py | 单测：mock sync_knowledge_base 返回 dict，断言输出真实数字 |
| 5 | `/knowledge stats` 读真实数据 | simplified_main.py | 单测：mock sources/faiss，断言无硬编码 |
| 6 | `/claude_skills_sync` 真实扫描 + 诚实提示 | simplified_main.py | 单测：mock 目录存在/缺失两分支 |
| 7 | 全量回归 + CI | 全仓库 | 1791+ 通过，CI 绿 |

## 5. 风险与缓解

| 风险 | 缓解 |
|------|------|
| TUI 无历史测试覆盖（Textual 组件难测） | handler 抽成纯方法（可独立测），TUI 薄壳只做渲染；用 `run_test` 冒烟 |
| compress_history 调真实 LLM 慢 | 仅 history > 5 条才压缩；mock 测试隔离 |
| container 依赖在 TUI 环境可能缺失 | 保留降级：无 session_manager 时诚实提示，不假装成功 |
| `/claude_skills_sync` 语义模糊 | 明确为"本地扫描"语义（非网络同步），文档化 |

## 6. 成功标准（全部可测）

1. `pytest tests/` 全绿（>=1791），新增 >=6 个针对性测试
2. `/compact` 在有会话时真实压缩（history 条数变化 + compressed_history 更新），无会话时诚实提示
3. `/knowledge sync` 真实调用 sync_knowledge_base，输出真实统计
4. `/knowledge stats` 无任何硬编码数字
5. `/claude_skills_sync` 扫描真实目录或诚实提示不可用
6. TUI `daip run` 冒烟通过（Textual run_test）
