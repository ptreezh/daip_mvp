# DAIP-LIVE 真实状态测评（main @ 09768c3）

测评日期：2026-08-07（本机时钟）
测评对象：`D:\DAIP\refactdoc`，分支 main，HEAD `09768c3 phase-12: Test quality fixes`，工作树干净
测评方法：全部数字为**直接实测**（运行命令所得），非文档转述；与本仓库 `PRODUCTION_READINESS_FINAL.md`、`PRODUCTION_READINESS_PHASE_8_11.md` 中的声称逐项对照。

---

## 1. 结论摘要

**文档声称 "Overall Production Readiness: 85/100"、"READY FOR MERGE"，实测结论：不成立。** 当前 main 处于"文档已宣称完成、代码实际破损"的状态：

| 维度 | 文档声称 | 实测 |
|---|---|---|
| 单元测试 | — | 238 收集，**21 失败 / 185 通过 / 32 错误** |
| 集成测试 | — | **19 失败 / 24 通过 / 9 错误**（12.48s） |
| E2E 测试 | — | **无法收集**：`tests/e2e/test_tui_interaction_e2e.py:316` 语法错误 |
| Ruff | — | **11191 个错误**（其中 6 个 invalid-syntax） |
| Mypy | — | **8 个错误 / 7 个文件** |
| 安全测试 | 11/11 通过（phase-12 提交信息） | **4 失败 / 15 通过**（该提交本身已过期） |
| CI/CD | 20 → 85 | CI 的 ruff 与 mypy 步骤现在就会失败；**e2e 从未在 CI 中运行**；集成测试 `continue-on-error: true` |
| API 标准 | 20 → 85 | `openapi.json` 存在，但整体就绪性被上述失败否决 |

历史上有真实改进（Phase 0-2 的旧阻塞项已修复，见第 4 节），但 Phase 8-11 的分数是被高估的：测试与代码漂移（stale mock、stale 构造函数、3.12 专属语法）使"85/100"不成立。

---

## 2. 实测证据（命令 + 结果）

### 2.1 单元测试 `tests/unit/`（31 个文件）
```
py -m pytest tests/unit/ -q --tb=short   # 后台运行，日志已留存
→ collected 238 items
→ 21 failed, 185 passed, 32 errors
```
- **32 个 ERROR 全部同一根因**：`unittest.mock.patch("src.daip_live.tui.Container", ...)` 抛
  `AttributeError: <module 'src.daip_live.tui' ...> does not have the attribute 'Container'`
  （触发点 `E:\Python312\Lib\unittest\mock.py:1428`）。
  受影响：`test_tui_background_tasks.py` ×7、`test_tui_copy_paste.py` ×5、`test_tui_debate_output_display.py`、
  `test_tui_input_handling.py`、`test_tui_model_switching.py`、`test_model_response.py` ×1、`test_multi_model_debate_integration.py` ×2。
  复现确认：`py -m pytest tests/unit/test_tui_model_switching.py -x --tb=long -q` → "1 error in 12.33s"。
- **21 个 FAILED 的完整构成**（日志 FAILED 行已逐条抓取核验）：
  - `test_persistence_sqlalchemy_compat.py` ×3：仍用旧 `Session(session_id=..., user_id=..., agent_type=..., status=..., history=[])` 构造，
    而 `src/daip_live/core/models.py:128-132` 的 Session 已新增必填字段 `session_type` / `goal` / `participant_ids`；
    `test_session_with_history` 另用旧字段名 `role` 构造 `DialogueTurn`（模型字段为 `participant_id`）。
  - wiki 多模型 GREEN/RED 系列 ×11：`test_multi_model_wiki_collaboration_green.py` ×5、
    `test_multi_model_wiki_collaboration_red.py` ×3、`test_wiki_collaboration_core_green.py` ×3。
  - 真实模型系列 ×7：`test_real_content_generation_green.py` ×2、`test_real_model_integration_green.py` ×1、
    `test_real_model_integration_red.py` ×1、`test_real_wiki_collaboration_red.py` ×3。
- 日志显示 GREEN 系列测试执行到了 `_run_debate_optimized`，且命中了下面的调试绕过分支（见 4.5）。

### 2.2 集成测试 `tests/integration/`（9 个文件）
```
py -m pytest tests/integration/ -q --tb=line
→ 19 failed, 24 passed, 3 warnings, 9 errors in 12.48s
```
- ERROR ×9 与单元测试同根因（TUI Container mock 失效）：`test_tui_integration.py` ×6、`test_tui_copy_paste_integration.py` ×3。
- 集成 FAILED ×19 分布于 5 个文件（重跑实测确认）：`test_wiki_multi_model_integration.py` ×8、
  `test_enhanced_debate_integration.py` ×5、`test_cli_intent_recognition.py` ×2、
  `test_enhanced_debate_features.py` ×2、`test_tui_intent_recognition.py` ×2。

### 2.3 E2E 测试 `tests/e2e/`（5 个文件）
```
pytest tests/integration/ tests/e2e/（后台组合运行）
→ 收集阶段即被杀死：
  tests/e2e/test_tui_interaction_e2e.py:316
  E   SyntaxError: ':' expected after dictionary key
```
- 直接读取确认 `tests/e2e/test_tui_interaction_e2e.py:312-320` 的字典字面量第 316 行为
  `"Participants", ", ".join(loaded.participant_ids),` —— 逗号应为冒号。
- 其余 4 个 e2e 文件 `py -m py_compile` 全通过（`test_api_endpoints_e2e.py`、`test_enhanced_debate_e2e.py`、
  `test_knowledge_collaboration_e2e.py`、`test_wiki_collaboration_e2e.py`），语法错误仅此 1 处。
- 结论：**e2e 套件一条测试都未运行过**（无论本地还是 CI），因为整个进程在收集阶段崩溃（1 处语法错误杀死全部）。

### 2.4 Ruff（`py -m ruff check src/`，ruff 0.12.10）
```
Found 11191 errors.   [*] 4143 fixable with --fix
                        3319 hidden fixes with --unsafe-fixes
```
规则分布（--statistics，按数量降序）：
E501 line-too-long 3106、W293 空白行尾随空格 2765、UP006 非 PEP585 注解 1999、T201 print 998、
F401 未用 import 559、UP035 过期 import 469、I001 import 未排序 340、W292 文件尾缺换行 251、
W291 行尾空格 239、F541 空 f-string 124、F841 未用变量 92、UP015 冗余 open 模式 58、
E722 bare except 44、E402 import 不在顶部 31、F811 重复定义 25、**F821 未定义名称 25**、
F405 import-star 后未定义 24、C401 7、**invalid-syntax 6**、F601 4、UP037 4、C414 3、
F403 3、F823 3、C405 2、C420 2、F402 2、UP008 2、UP024 2、C408 1、C416 1。

其中 **6 个 invalid-syntax 是真语法兼容性问题**：
- `src/daip_live/task_decomposition/agile_task_system_core.py:525`（4 处）
- `src/daip_live/task_decomposition/tui_compatible_integrator.py:335`（2 处）
- 内容为 f-string 表达式内使用反斜杠 `{"\\n\\n".join(task_summaries)}`——**Python 3.12 才合法**。
- 影响：项目声明 `requires-python >=3.9,<3.13`，CI 跑 Python 3.11；这两个文件在 3.9-3.11 下
  **import 即 SyntaxError**。本机（3.12）`ast.parse` 全量 0 失败，恰好掩盖了这一点。
- 工具注意：ruff 0.12.10 已移除规则码 E999（`--select E999` 报 "Rule `E999` was removed"），须用
  `--output-format concise | rg invalid-syntax`。

### 2.5 Mypy（`py -m mypy src/daip_live/`）
```
Found 8 errors in 7 files (errors prevented further checking)
```
- 缺类型 stub：`yaml`（`cli/commands/knowledge.py:119`、`cli/commands/wiki.py:51`）、
  `aiofiles`（`doc/converter/docx_to_md.py:7`、`doc/converter/md_to_docx.py:7`）、
  `markdown`（`doc/converter/md_to_docx.py:12`）、`requests`（`doc/tools/paper_downloader.py:12`、`doc/paper_downloader.py:10`）。
- 模块名重复：`daip_live.intent_recognition.context_manager` vs `src.daip_live.intent_recognition.context_manager`
  （`src/daip_live/intent_recognition/context_manager.py`），导致 "errors prevented further checking"。

### 2.6 安全测试 `tests/security/`（2 个文件）
```
py -m pytest tests/security/ -q --tb=short
→ 4 failed, 15 passed, 6 warnings in 3.66s
```
- FAILED ×4，全部在 `test_enhanced_debate_security.py::TestEnhancedDebateSecurity`：
  `test_input_validation_for_special_characters`、`test_concurrent_access_security`、
  `test_history_retrieval_authorization`、`test_resource_limit_enforcement`（重跑逐条确认）。
- **phase-12 提交信息声称 "Security tests: 11/11 passed (was 5/11)"，实测当前已是 4F/15P——该声称在提交后即过期**；
  且 phase-12 只改了 2 个测试文件（test_security_audit.py、test_api_docs.py），却仍出现 2 个新失败，
  说明"Test quality fixes"修复不完整或引入了回归。
- 另有 `PytestReturnNotNoneWarning`（`test_security_audit.py` 的测试函数 `return` 字典而非断言，pytest 未来版本会变 error）。

### 2.7 CI 配置 `.github/workflows/ci.yml`
- ubuntu-latest / Python 3.11 / poetry。
- 步骤：`ruff check src/`、`mypy src/daip_live/`、`pytest tests/unit/ -v --tb=short`、
  `pytest tests/integration/`（注入 `OLLAMA_HOST`，**`continue-on-error: true`**）。
- 三个盲点：**e2e 从不运行**；集成测试失败不阻塞（continue-on-error）；ruff/mypy 步骤当前就会红，
  说明"CI 全绿"的声称与实际不符（除非从未真正跑过 CI）。

### 2.8 配置优先级问题
- `pytest.ini` 存在（pythonpath=.、norecursedirs=litellm、asyncio_mode=auto、
  asyncio_default_fixture_loop_scope=function），**优先于** `pyproject.toml` 的 `[tool.pytest.ini_options]`。
- 后果：pyproject 中注册的 markers（integration/e2e/unit/slow）与 `--strict-markers`、testpaths 全部失效，
  运行处处报 `PytestUnknownMarkWarning`；**`--strict-markers` 在 pytest.ini 优先下根本不生效**，
  未注册 marker 只警告不报错，掩盖了标记拼写错误。
- poetry.lock 锁定 ruff **0.4.10** / mypy **1.17.1**；pyproject 约束 `ruff ^0.4.4`、`mypy ^1.10.0`；
  本机实际为 ruff **0.12.10** / pytest 8.3.4 / pydantic 2.13 / Python 3.12.0rc3。锁与本地不一致。

### 2.9 文档声称（对照项）
- `PRODUCTION_READINESS_FINAL.md`：`35/100 → 65+/100`、`Status: READY FOR MERGE`、CI/CD 20→85。
- `PRODUCTION_READINESS_PHASE_8_11.md`：`Overall Production Readiness: 85/100`、CI/CD 20→85、Security 40→85、API Standards 20→85。
- 与 2.1-2.8 实测全部矛盾。

---

## 3. 根因分组（按影响面排序）

1. **TUI 重构后 mock 目标失效（约 41 个错误：单元 32 + 集成 9）**——最高频、最易修。
   `src/daip_live/tui/__init__.py` 不再导出 `Container`，但大量测试仍 `patch("src.daip_live.tui.Container")`。
2. **Session/DialogueTurn 模型必填字段变更未同步测试（3 个单元失败）**——`models.py:128-132` 新增
   `session_type/goal/participant_ids`，`test_persistence_sqlalchemy_compat.py` 还在用旧构造
   （`Session(session_id=..., user_id=..., agent_type=..., ...)`）；
   `DialogueTurn` 已有 `participant_id` 字段，但 `test_session_with_history` 仍用旧字段名 `role` 构造
   （实测 `ValidationError: participant_id Field required`），需改为 `participant_id=`。
3. **wiki 多模型 GREEN/RED 测试与生产校验漂移（11 个单元失败 + 8 个集成失败）**——
   GREEN 系列仍在喂 Mock 模型，而生产侧（phase 3+）已有真实模型校验；日志证实执行进入了 `_run_debate_optimized`
   且命中了调试绕过（4.5），掩盖了真实校验逻辑。集成侧同系列 8 个失败（`test_wiki_multi_model_integration.py`）。
4. **e2e 语法错误使整个 e2e 套件零运行（1 处语法错误杀死全部 5 个文件）**——
   `test_tui_interaction_e2e.py:316` 一处逗号/冒号；其余 4 个文件 py_compile 通过。
5. **3.12 专属 f-string（2 文件 6 处）**——违反 >=3.9 支持声明，3.11 CI 下 import 即挂。
6. **生产代码里留了调试绕过（`enhanced_debate_manager.py:98-102`）**：
   ```python
   # 临时绕过模型可用性检查（调试用）
   log.info("Skipping model availability check for debugging...")
   is_model_ok = True
   check_message = "Model check skipped for debugging"
   ```
   以及 110-125 行对缺失角色映射不报错、改为"创建默认映射"——与 phase-1 "truth in debate" 方向相悖。
7. **CI 形同虚设的三重盲点**（无 e2e、集成 continue-on-error、ruff/mypy 现在就会红）。
8. **依赖锁与本地工具链不一致**（ruff 0.4.10 锁 vs 0.12.10 本机），数字复现性差。
9. **文档分数虚高**（85/100 vs 实测），phase-12 的"11/11"在提交后即过期。

---

## 4. 已被证实存在的历史改进（避免误判"全是垃圾"）

- Phase 0-2 的旧阻塞项确实修复了：
  - `persistence/database.py` 已无 `session.dict()`/`.dict()`（Pydantic v2 迁移完成）。
  - `knowledge/manager.py:34` 改为 `embedding_dim = config.embedding_dimension`（配置驱动）。
    ⚠️ 但 `config.yaml`（仓库根目录，实测存在）目前**没有** `embedding_dimension` 键；
    `KnowledgeBaseConfig.embedding_dimension` 有默认值 768（实测 `KnowledgeBaseConfig(directory='x').embedding_dimension == 768`），
    故不会 KeyError，只是未显式配置——建议在配置中显式声明以消除隐性依赖。
  - `core/exceptions.py` 存在；`observability/`、`hybrid/` 存在；`p7_gui_v1` 死代码已删；`openapi.json` 存在。
- main 提交历史与声称一致：phase-0 `1efda31`、phase-1 `d02101f`、phase-2 `4611800`、phase-3 `86dccac`、
  gnhf #14-22、merge `c6f6f40`（35→65/100）、phase-8 `5b2c76f`、phase-9-11 `d27e720`、phase-12 `09768c3`（HEAD）。
- `git show --stat 09768c3`：phase-12 只改了 2 个文件（`tests/security/test_security_audit.py`、
  `tests/unit/test_api_docs.py`，+25/-17），**没有触碰任何当前失败/错误的测试**——"Test quality fixes"名不副实。
- 185 个单元测试 + 24 个集成测试确实在通过（含 `test_api_docs.py`、`test_knowledge_embedding_dimension.py`、
  `test_observability_*`、`test_hybrid_*`、`test_core_errors.py`、`test_logging_infrastructure.py`、`test_skill_manager.py`）。
- Ollama 本机 `localhost:11434` 可达（Test-NetConnection 通过），真实模型集成具备本地复现条件。

---

## 5. 优化计划（按优先级分波）

### Wave 0 —— 止血（当天可完成，先把"红"变"绿"的骨架立起来）
1. 修 `tests/e2e/test_tui_interaction_e2e.py:316`：逗号改冒号 → e2e 可收集；
   并跑 `py -m py_compile tests/e2e/*.py` 全量扫描，确认其余 4 个文件无同类问题（本轮已实测通过）。
2. 删/改 `enhanced_debate_manager.py:98-102` 调试绕过，恢复真实模型可用性检查（或加显式开关参数，默认开）；
   110-125 行改回 `raise ValueError` 而非"创建默认映射"，并补单元测试验证检查逻辑。
3. `config.yaml` 补 `embedding_dimension`（仓库根文件，与 `knowledge/manager.py:34` 读取对齐；模型默认值 768 已兜底，补键为显式化）。

### Wave 1 —— 测试恢复（1-2 天）
4. TUI mock 失效：二选一（推荐 A，改动最小）：
   - A. 在 `src/daip_live/tui/__init__.py` 恢复导出 `Container`（若组件仍存在）；
   - B. 把 30+ 处 `patch("src.daip_live.tui.Container")` 改指真实位置（`tui/...` 子模块）。
5. `test_persistence_sqlalchemy_compat.py`：按新 Session 必填字段更新构造（3 处）；
   `test_session_with_history` 中 `DialogueTurn(role=..., ...)` 改为 `participant_id=`（模型已有该字段，实测缺的是测试旧字段名）。
6. wiki GREEN/RED 测试：与生产校验对齐——GREEN 系列改喂"通过校验的 fake"或真实可用模型，RED 系列保持负例。
7. 安全测试 4 个 FAILED：`test_history_retrieval_authorization`、`test_resource_limit_enforcement`、
   `test_input_validation_for_special_characters`、`test_concurrent_access_security` 按当前实现修断言；
   顺手修 `test_security_audit.py` 的 `return` 而非 `assert`（PytestReturnNotNoneWarning）。

### Wave 2 —— 兼容性与类型（1 天）
8. 修 6 处 3.12 专属 f-string（`agile_task_system_core.py:525`、`tui_compatible_integrator.py:335`）→ 3.9 兼容写法；
   CI 增加 Python 3.9 矩阵或至少 `ast.parse` 静态检查步骤，防止版本回归（本机 3.12 永远复现不了 3.11 import 错误）。
9. mypy：dev 依赖补 `types-PyYAML`、`types-requests`、`types-aiofiles`、`types-markdown`；解决
   `intent_recognition/context_manager` 模块名重复（移动/改名使 import 一致）。
10. 统一工具链：CI 用 `poetry run ruff/mypy`；`poetry lock --no-update` 固定 lock 版本，
    或显式 `poetry add ruff@0.12.10 mypy@1.15.0` 升级 lock 后再统一，消除"本地 11191 错误 vs CI lock 版本"的复现性漂移。

### Wave 3 —— 静态检查清零（2-3 天，可并行分包）
11. Ruff 11191 按批次清：先 `--fix` 4143 个自动修复项，再分批处理 W293/W291/I001 等格式化类，
    再人工处理 E722/F821/F405/F403（真 bug 候选，需逐条看）、T201（print 是否该留）、E501（配 docstring 例外或折行）。
12. 收尾门槛：`py -m ruff check src/` 0 错误、`py -m mypy src/daip_live/` 0 错误。

### Wave 4 —— CI 与文档落地（0.5-1 天）
13. CI 增加 `pytest tests/e2e/`；集成测试去掉 `continue-on-error`（或改为显式 artifact 上报，不再静默绿）；
    增加 `pytest tests/security/`。
14. 文档纠正：更新 `PRODUCTION_READINESS_*.md` 分数为实测值；README badge 与真实状态一致。
15. 可选：`pytest.ini` 与 pyproject 二选一（建议删 pytest.ini，统一到 pyproject，让 markers/testpaths 生效）。

---

## 6. 生产上线计划（分阶段门禁）

### Stage A：基线绿（对应 Wave 0-1）
- 门禁：`pytest tests/unit/`、`tests/integration/`、`tests/e2e/`、`tests/security/` 全部通过；
  调试绕过移除；config 默认值补齐。
- 产出：可重复的本地全绿基线 + CI 全绿。

### Stage B：质量闸门（对应 Wave 2-3）
- 门禁：ruff 0 错误、mypy 0 错误、3.9-3.12 语法兼容（CI 加 3.9 与 3.12 双版本矩阵或至少 3.11 解析检查）。
- 产出：静态检查进 CI 成为硬门禁。

### Stage C：上线就绪（对应 Wave 4 + 验收）
- 门禁：
  - CI 全步骤绿（含 e2e、security，无 continue-on-error 掩盖）；
  - 文档分数与实测一致（重新评估并给出真实分数，拒绝沿用 85/100）；
  - 生产启动冒烟：`poetry run daip run` 走通一次会话（本机 Ollama 已具备条件）；
  - 安全测试恢复全绿。
- 产出：可交付的 `PRODUCTION_READINESS_*` 终版（以实测为准），然后才谈 merge/release。

---

## 7. 测评过程留下的工具性备注

- 本机 `ruff` 不在 PATH：一律 `py -m ruff`。
- ruff JSON 导出被控制台编码破坏（`JSONDecodeError` @ char 75463）：用 `--output-format concise` + rg。
- `rg --type py` 在 Windows 失效：用 `-g "*.py"`。
- 单位测日志留存：`C:\Users\Zhang\AppData\Local\Temp\opencode\pytest_unit.log`（FAILED 名单在行 820-844）。
- 集成/E2E 组合日志：`C:\Users\Zhang\AppData\Local\Temp\opencode\pytest_integration_e2e.log`。
- 本测评未改动任何源码，工作树仍为 clean。
