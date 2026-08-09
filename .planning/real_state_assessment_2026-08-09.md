# DAIP-LIVE 真实状态测评与生产上线计划（2026-08-09 实测版）

**定位**: 个人生产级本地工具（非对外发布产品）+ 本地/云端混合模型调用（本地优先审核安全隐私）
**方法**: 本报告所有数字均为本会话直接实测（命令执行取证），不转述历史文档；转述处明确标注来源。
**对照基线**: `.planning/real_state_assessment_2026-08-08.md` + `.planning/ROADMAP.md` + `.planning/STATE.md`
**取证环境**: Windows 本机 / Python 3.12.0rc3 / Ollama 在线（6 模型）/ git main @ afc883f

---

## 1. 实测数字总览（08-09 vs 08-08 基线）

| 维度 | 08-08 实测 | **08-09 实测** | 变化 | 取证命令 |
|------|-----------|----------------|------|---------|
| 全量测试 tests/ | 未定义 | **1738P / 433S / 0F / 0E（369s）** | ✅ 质变：0F/0E | `py -m pytest tests/ -q --tb=line -rs` |
| 默认 pytest（无参） | 未定义 | **仅收集 364** | ⚠️ testpaths 缺陷 | `py -m pytest --collect-only -q` |
| 收集总数 | — | **2171** | — | `py -m pytest tests/ --collect-only -q` |
| ruff | 11183 | **11116**（**6 invalid-syntax 未修**） | ⚠️ 仅 -67，语法错原样 | `py -m ruff check src/ --statistics` |
| mypy | 8E / 7F | **8E / 7F** | ➡️ 持平 | `py -m mypy src/daip_live/` |
| CLI 命令 | 7 注册 | **10 命令全挂载**（model/session/role 补齐） | ✅ Stage 1-2 完成 | `--help` |
| debate start | 假演示壳 | **真实 Ollama 辩论实测跑通**（真论据+共识摘要） | ✅ Stage 1-3 完成 | 实跑一轮 |
| ask | Would 占位 | **4 个 handler 全部复用真实命令/执行器** | ✅ Stage 1-4 完成 | 源码核实 |
| hybrid 接线 | 零 | **零**（仅 `__init__.py` 自引用） | ❌ 未启动 | `rg "from daip_live.hybrid" src` |
| 备份 | 规划中 | **存在且完整**：`backups/daip-20260808-0821xx.zip` ×2（19 项，含 daip_live.db + config.yaml + 全部知识文件）；git tag `pre-production-2026-08-08` | ✅ Stage 0 完成 | zip 枚举 |
| knowledge_sources | 0 | **0**（根因查明：CLI sync 用 `:memory:` DB + MockModelProvider） | ❌ 真 bug，非未用 | `sync` 实跑 + sqlite 复核 |
| DB 会话数据 | 406 会话 / 611 轮 | **64 会话且全部为 "Test session"（08-08 23:47 写入）/ dialogue_turns 0** | ❌ 测试污染致真实数据不存 | sqlite 分组统计 |
| CLI 冷启动 | 未测 | **7.8s**（`--help`） | ⚠️ 慢 | `Measure-Command` |
| Ollama | 6 模型 | **6 模型** | ✅ | `/api/tags` |
| 6 处 invalid-syntax | 存在 | **原封未动**（`agile_task_system_core.py:525`、`tui_compatible_integrator.py:335`） | ❌ Stage 1 声称修复未做 | ruff concise 定位 |

**一句话现状**: 相比 08-08，"假功能清理 + 测试恢复"两个大项真实完成（1738 绿、CLI 全真实、备份到位）；但**静态检查纹丝未动**（11116/8E/6 语法错）、**knowledge 管线查出更深的壳**（sync 空转、搜索空壳、默认入口不可达）、**测试战役污染了真实数据库**（dialogue_turns 归零）、**hybrid 仍未启动**。

---

## 2. 项目全面理解（架构地图）

### 2.1 规模与构成（实测）
- **源码**: `src/daip_live/` 306 个 py 文件 / **77,384 行**
- **测试**: `tests/` 212 个 py 文件 / **48,523 行**（2171 收集）
- **37 个子模块**：agent_engine / basic_tools / cli(+commands) / config / container(DI) / core / debate_module / doc / hybrid / intent_recognition / knowledge / memory / model_manager / model_provider / multi_agent_collab / observability / p4_role_manager_tools / p7_gui / p8_debate_system / permission / persistence / scaffolding / skills / task_decomposition / todo / tui(+tui_v1) / utils / wiki / workflow
- **技术栈**: Python 3.9-3.12（声明）、Typer + Textual + Streamlit、SQLAlchemy 2、FAISS、langchain、litellm、FastAPI/uvicorn、dependency-injector、rich
- **数据**: SQLite（`daip_live.db` 1.7MB）+ `knowledge/`（faiss 索引 + wiki 页 + 论文 PDF）+ `roles/`（13 角色 yaml）+ `config.yaml`
- **git 历史**: 5 月 gnhf 清理战役（18 commits）→ 8/7 生产就绪 Phase 0-12（35→65/100 声称）→ 8/7 真实测评打假 → 8/8 Stage 0-1（备份/命令挂载/真实化）→ 8/8-9 S2 测试对齐战役（13 commits，1738 绿收官）

### 2.2 分层架构实况

| 层 | 模块 | 状态（实测） |
|----|------|-------------|
| P1 持久化 | persistence/ | 真实；`DatabaseManager` 支持 `:memory:`/文件；但 CLI 层误用 `:memory:`（knowledge.py:135/244） |
| P2 知识 | knowledge/ + wiki/ | **半壳**：索引文件会写（20KB faiss），元数据永不落盘；搜索路径空转（见 3.2） |
| P3 模型 | model_provider/ | 真实 litellm 路径通（ollama/* 实测辩论成功）；embedding 有 fallback；无云端路由 |
| P4 角色/工具 | p4_role_manager_tools/ | 真实；13 角色 yaml；role-intel 挂载 |
| P5 引擎 | agent_engine/ | 真实；EnhancedChatExecutor/EnhancedIntentRecognizer 被 ask 复用 |
| P6 CLI/TUI | cli/ + tui/ | CLI 10 命令真实；TUI 未自动化冒烟（交互式）；双模块名警告未消 |
| P7 GUI | p7_gui/ | 存在，未在本轮深测（有 e2e 覆盖） |
| P8 辩论 | p8_debate_system/ | **核心修复**：history_tracker `:memory:` 隔离修复为真；辩论实测跑通；`turn_in_round` 硬编码 1 待办 |
| 横切 | hybrid/ | 三件套存在（security_gate/sanitization/cloud_pool）但**业务零引用** |
| 横切 | observability/ | 存在（JSON 日志/健康检查/优雅停机） |
| DI | container.py | 真实装配；e2e container override 传播已修（S2-3） |

### 2.3 测试体系结构
- 目录: unit / integration / e2e / security / performance / stability / stress / functional / regression / interactive / 以及约 60 个根级测试文件 + tui/ + wiki/ + cli/ 等
- **关键配置事实**: pyproject `testpaths = ["tests/unit","tests/integration","tests/e2e"]` → **默认 `poetry run pytest` 只收 364 个**（约 1/6）；全量必须显式 `pytest tests/`（2171）
- markers: unit/integration/e2e/slow/performance/load/security 已注册（strict-markers 生效，因为 pytest.ini 已删除）
- conftest.py 有模块级裸 `print("sys.path in conftest.py:", ...)`（L9）

---

## 3. 真实状态详解

### 3.1 正面事实（全部本会话实测验证）

1. **全量测试 1738 绿 / 0F / 0E**（369.36s，13 warnings）：`py -m pytest tests/ -q --tb=line -rs` → `1738 passed, 433 skipped`。S2 战役的真实成果，无失败无错误。
2. **debate start 真实可用**：实跑 `debate start "人工智能的伦理挑战" --roles pro_arguer,con_arguer --rounds 1`，正反双方真实生成论点（英文长论据），产出 Consensus/Controversial/Key Points 摘要，`DebateCompleteEvent` 正常 yield。容器装配 EnhancedDebateManager + 真实 Ollama。
3. **ask 命令真实化**：`cli/main.py:422-493` 四个 intent handler 全部复用真实命令（debate_start / doc_search / doc_download / EnhancedChatExecutor），占位文本已清（rg 无 "Would start"）。
4. **CLI 10 命令全挂载**：run/ask/debate/doc/role-intel/knowledge/wiki/model/session/role；`model status` 实测输出 "No model is currently set"（真行为）；`session list` 实测连真库输出表格。
5. **history_tracker `:memory:` 隔离修复为真**：`history_tracker.py:36-39` 改为每实例唯一临时文件 `daip_debate_history_<uuid>.db`，注释如实记录修复动机。security 4F 根因消除（该簇测试现绿）。
6. **备份完整**：`backups/daip-20260808-082131.zip`（1,526,828 字节，19 项）含 `daip_live.db`、`config.yaml`、13 个 wiki 页、2 篇论文、index.faiss；git tag `pre-production-2026-08-08` 存在。
7. **知识资产在磁盘上真实存在**：13 个中文 wiki 页（含 2025-12-13 协作记录、量子计算、人工通用智能等真实内容）、2 篇 arXiv 量子计算论文 PDF、`knowledge/index.faiss` 20KB。
8. **Ollama 6 模型在线**：qwen3.5:4b / gemma4:e2b / deepseek-r1:8b / ministral-3:3b / llama3:latest / phi3:mini。
9. **配置显式化**：`config.yaml` 含 `embedding_dimension: 768`（08-08 补的键保留）；`pytest.ini` 已删除并入 pyproject（Stage 1-1 完成）。
10. **辩论真实数据留存**：debate_sessions 50 行，其中 43 条为 2025-11-06~2025-12-11 真实辩论记录 + 7 条 08-08 测试记录——真实历史数据未被测试战役清除。

### 3.2 破损与风险清单（逐项可复现）

**A. 静态检查（实测）**
1. **6 处 invalid-syntax 原封未动**：`task_decomposition/agile_task_system_core.py:525`（`{"\\n\\n".join(...)}` f-string 内反斜杠）+ `task_decomposition/tui_compatible_integrator.py:335`。**Python 3.9-3.11 import 即 SyntaxError**，与 pyproject `requires-python >=3.9,<3.13` 直接冲突；本机 3.12 掩盖此问题（08-07 grill-down 已预警此风险，仍未修）。
2. **ruff 11116 项**：E501 3102 / W293 2746 / UP006 2004 / T201 961 / F401 551 / UP035 470 / I001 339 / W292 251 / W291 233 / F541 118 / F841 89 / **E722 bare-except 44** / E402 34 / F811 25 / **F821 undefined-name 25** / F405 24 / 其余约 1000。4103 项可 `--fix` 自动修。
3. **mypy 8E/7F 不变**：import-untyped（yaml/aiofiles/markdown/requests 缺 stub）×7 + 模块名重复（`daip_live.intent_recognition.context_manager` vs `src.daip_live...`）——双模块名与 CLI runpy RuntimeWarning 同源。
4. **pytest-asyncio 重复依赖**：同时出现在运行时依赖（pyproject:27）与 dev 依赖（pyproject:47）。

**B. knowledge 管线（本轮新挖，比 08-08 认知更深）**
5. **CLI sync 是空转**：`knowledge.py:244/135` `DatabaseManager(":memory:")` + `MockModelProvider`（"Use mock provider to avoid embedding issues"）。实测：`daip knowledge sync` 报告 **"Added: 13"**，随后 sqlite 查 `knowledge_sources` **仍为 0**——元数据写进内存库即蒸发，每次 sync 都当全新摄入（无增量检测能力），faiss 索引每次被 mock 向量重写。
6. **搜索路径空壳**：`_search_knowledge_default`（L192-196）`search_results = []` 硬编码空结果。实测 `knowledge auto --search "量子计算"` → "No results found"，而知识库中恰有《量子计算基础原理.md》。显式 `search` 命令查 root DB 的 `knowledge_sources`（0 行）同样必空。
7. **默认查询入口不可达**：`daip knowledge "量子计算"` 实测报 **"No such command"**——设计的"位置参数即查询"默认行为未挂成 group 默认命令，用户必须知道 `auto --search` 这种内部命令名。
8. **根因归纳**：知识管线 = 真实文件资产（wiki/paper 在盘上）+ 真实索引文件（faiss 会写）+ **全 mock/内存的执行层**。三件套互不接通。

**C. 数据安全（本轮新发现，优先级最高）**
9. **DB 被测试战役污染**：sessions 64 行**全部**为 "Test session"（`goal LIKE '%Test%'` = 64/64），时间 08-08 23:47 之后；`dialogue_turns` 表**归零**。08-08 评估的 406 会话/611 轮已不存在（备份 zip 中或许仍存）。根因：S2 的 session 测试直接读写 root `daip_live.db`（`session list` 实测输出即含 23:47 写入的测试会话），无隔离。
10. **DB/索引被 git 跟踪**：`daip_live.db`、`knowledge/index.faiss`、`docs/index.faiss` 均 tracked → 每次测试/运行污染都进 `git status`（当前脏状态 ` M daip_live.db`、` M knowledge/index.faiss`），且有二进制冲突与数据泄露风险。
11. **无恢复演练**：备份存在但从未解压验证过（本报告已验 zip 完整性，未验恢复后行数）。
12. **hybrid 三件套仍零接线**：`rg "from daip_live.hybrid" src` 仅命中 `__init__.py` 自身；08-08 计划 Stage 4 未启动。用户核心需求（本地预审/脱敏/云端委托）现状 = 0 分起点。

**D. CI 与配置**
13. **CI 必然红色**：`.github/workflows/ci.yml` 的 ruff 步骤（11116 错）与 mypy 步骤（8E）在任何提交上都会失败；integration 步骤带 `continue-on-error: true`；**无 e2e、无 security、无全量测试**步骤。与 PRODUCTION_READINESS_FINAL.md 声称的 "CI/CD 85/100" 直接矛盾。
14. **默认 pytest 只收 364**（testpaths 仅 3 目录）：`poetry run pytest` 与 AGENTS.md 的 "Run all tests" 承诺不符，约 2/3 测试（含 security/performance/stability 与全部根级文件）不在默认门禁内。
15. **433 个 skip（20%）**：全部为"旧 spec / TDD 红阶段 / 刻意 RED"白名单，理由文档化（如 TUI 旧 API、`_get_autocomplete_suggestions` 等已移除方法）。其中 `test_real_model_integration_red.py:129` 明确"真实AI内容生成功能尚未实现（白名单豁免）"——**真实模型能力缺口被白名单遮盖**；`test_real_wiki_collaboration_red.py` 系列 08-08 建议"本机 Ollama 应能修绿而非豁免"，S2 选择了跳过。
16. **CLI 冷启动 7.8s**（`--help`），每次附带 runpy RuntimeWarning（双模块名）。
17. **13 个 pytest 警告**：Pydantic 序列化警告（litellm `Message`/`Choices` 字段契约不匹配 `PydanticSerializationUnexpectedValue`）。

**E. 代码卫生**
18. **`turn_in_round` 硬编码 1**：`history_tracker.py:156`（`# We'll update this properly later`——生产代码残留 TODO 语义）。
19. **conftest.py:9 裸 print** 污染测试输出。
20. **半成品仍在**：CloudPool 无 execute()；SecurityGate MEDIUM 语义矛盾（脱敏后本地执行给谁看）；Sanitization 正则误报高、不覆盖 PII（均 08-08 已核，本轮未再逐行复核，仍适用）。

### 3.3 数据资产实况（sqlite 实测）

| 表 | 行数 | 含义 | 判定 |
|----|------|------|------|
| sessions | 64 | **全部为测试会话**（08-08 23:47+） | ❌ 真实会话数据已失 |
| dialogue_turns | **0** | 对话轮次**归零** | ❌ 数据丢失（备份中或存） |
| debate_sessions | 50 | 43 条真实（2025-11/12）+ 7 条测试 | ✅ 历史保留 |
| debate_turns | 41 | 辩论轮次 | ✅ 保留 |
| knowledge_sources | **0** | 知识元数据**永远为空**（CLI 用内存库） | ❌ 结构性 bug |

---

## 4. 综合测评（8 维度，个人工具加权）

评分标准：1-10，10 = 个人日常可无脑依赖。证据全为 §1-§3 实测。

| 维度 | 权重 | 08-08 | **08-09** | 核心证据 | 一句话结论 |
|------|------|-------|-----------|---------|-----------|
| 核心功能可用性 | 25% | 4 | **6** | debate/ask/CLI 全真实并实测通过；但 knowledge 三壳、wiki 真实模型集成被 skip、TUI 未冒烟 | 主命令活了，知识侧还是壳 |
| 模型接入 | 15% | 7 | **7** | 真实 litellm + 辩论实测 + 6 模型；无云端/路由 | 本地真调用，云端未建 |
| 数据安全与隐私 | 20% | 3 | **4** | 备份完整 + .env gitignore；但 DB 进 git + 测试污染致 dialogue_turns 归零 + 无恢复演练 + hybrid 零接线 | 有备份了，但污染教训惨重 |
| 测试守护 | 15% | 4 | **7** | 1738P/0F/0E（369s 全量实跑）为质变；433 skip 白名单 + testpaths 缺陷 + CI 不全量 | 测试栈真绿，门禁还不完整 |
| 代码质量 | 10% | 3 | **3** | ruff 11116（含 6 语法错）、mypy 8E、双模块名、conftest print | 静态全红，纹丝未动 |
| 文档与定位一致性 | 10% | 2 | **3** | CLI 相关文档部分纠正；PRODUCTION_READINESS_FINAL "READY FOR MERGE/65+/CI85" 与实测（CI 红）矛盾；README badge 仍虚 | 一半诚实一半虚高 |
| 可维护性 | 5% | 4 | **5** | 幽灵命令全清除、模块化底子好；knowledge/hybrid/turn_in_round 半成品在 | 卫生好转，仍有欠账 |
| 性能与体验 | 0%（参考） | — | **3** | CLI 冷启动 7.8s；TUI 未自动化实测 | 偏慢，未测体验 |

**加权总分 = 0.25×6 + 0.15×7 + 0.20×4 + 0.15×7 + 0.10×3 + 0.10×3 + 0.05×5 = 5.25 ≈ 5.3/10**（08-08: 4.1）。

**判定**：从"半成品演示级"进到"测试绿、命令真、有备份"的**可修复工程态**；距"个人生产级"（≥7）的主要缺口 = 静态清零 + CI 硬化 + 数据隔离/恢复 + knowledge 管线接通 + 混合路由落地。

---

## 5. 优化计划（分阶段，每步含门禁与回滚）

> 原则：TDD（先红后绿）；每阶段单提交可 revert；不动用户真实数据；不扩功能面（混合路由已确认为硬需求但暂缓实施，见 Stage 5 决策记录）。

**用户决策（2026-08-09 确认）**: ① 混合路由 = **硬需求，当前暂不实现**（降级 Backlog，需求保留）；② S3-1（DB/faiss 移出 git）= **批准执行**。

### Stage 1: 兼容性与静态清零（1-2 天）——CI 变绿的前提
- [ ] S1-1 **修 6 处 invalid-syntax**：`agile_task_system_core.py:525`、`tui_compatible_integrator.py:335` f-string 反斜杠提为变量。**门禁**: 全量 `ast.parse` 0 失败（写进 CI 步骤防回归）。**回滚**: 单提交 revert。
- [ ] S1-2 **ruff 批量清零**：`ruff --fix` 自动修 4103 项（分 2-3 批提交，每批后跑全量测试兜底）→ 人工处理真 bug 候选（**F821×25 必须逐个核实是否真 undefined**、E722×44 bare-except 最小化收紧、F541×118 f-string 无占位、T201×961 print 批量改 logging 或白名单）。**门禁**: `ruff check src/` = 0。**回滚**: 分批 revert。
- [ ] S1-3 **mypy 清零**：装 types-PyYAML/types-aiofiles/types-Markdown/types-requests；解决双模块名（确认 `daip_live` 以安装布局导入，评估删 `cli/main.py:26` sys.path.insert 与 conftest.py 的 src 注入，二者需同步处理）。**门禁**: `mypy src/daip_live/` = 0 + CLI 冒烟不回退。**回滚**: 双模块名修复单独提交。
- [ ] S1-4 **pytest-asyncio 移出运行时依赖**（pyproject:27 删除，dev 保留）。
- **并行建议**: S1-1/S1-2 可与 S2 并行（不同文件域）。

### Stage 2: 测试配置与 CI 硬化（0.5-1 天）
- [ ] S2-1 **testpaths 修正**：默认 `poetry run pytest` 应收集全量（改 testpaths 为 `tests/`），或显式文档化"全量 = `pytest tests/`"并让 CI 用全量。**门禁**: 无参 pytest 收集 ≥ 2000。
- [ ] S2-2 **CI 硬化**：ruff/mypy 恢复硬 gate（Stage 1 后自然变绿）；integration 去 `continue-on-error`；**新增 e2e + security 步骤**；用全量测试。**门禁**: 本地模拟 CI 命令序列全绿。
- [ ] S2-3 **删 conftest.py:9 裸 print**。
- [ ] S2-4 **skip 白名单审计**（433 项）：分类为 ①真废弃（API 已移除）→ 删除测试或改写；②可修绿（如 wiki real 系列：用 fixture 提供 config + 真 Ollama）→ 修；③真未实现（真实 AI 内容生成）→ 保留白名单但进 README 功能清单"未实现"区。**门禁**: 白名单缩减 ≥ 50% 或有明确理由留档。

### Stage 3: 数据安全与隔离（1 天，个人工具命脉，**建议最先做**）
- [x] S3-1 **DB/faiss 移出 git**：`git rm --cached daip_live.db knowledge/index.faiss docs/index.faiss` + .gitignore + 单提交。**用户已批准（2026-08-09）并已执行**（含 `*.faiss`/`test_output/`/`AGENTS.md.backup-*` 忽略规则）。⚠️ 注：gitignore 不覆盖已跟踪文件，须 `git rm --cached` 解除跟踪（已完成）。**回滚**: `git revert` 后需重新 `git rm --cached`。
- [ ] S3-2 **测试 DB 隔离**：session/dialogue 相关测试改为 tmp_path 或环境变量指向独立 DB；**加保护性验证**——测试套件运行前后 `daip_live.db` 文件 hash 必须一致（可做成 pytest session fixture 断言）。**门禁**: 全量测试后 `git status` 干净（无 db/faiss 变更）。
- [ ] S3-3 **备份恢复演练**：从 `daip-20260808-082131.zip` 恢复 db 到临时目录，验证行数/可查询；写恢复 SOP 文档。**门禁**: 恢复后的 DB 行数与 zip 内记录一致。
- [ ] S3-4 **备份自动化**：把 Stage 0 的备份脚本挂到每日任务或 pre-commit 挂钩（至少 weekly），备份目标目录 `.gitignore`。

### Stage 4: knowledge 管线接通（1-2 天）
- [ ] S4-1 **CLI sync 改持久 DB + 真实 embedding**：`DatabaseManager(":memory:")` → 文件 DB（root 或 `data/`）；MockModelProvider → 真实 embedding（`ollama/nomic-embed-text` 需 `ollama pull`，或配置 fallback 策略并显式声明）。**门禁**: sync 后 `knowledge_sources > 0` 且文件哈希去重生效（二次 sync "Added: 0"）。
- [ ] S4-2 **默认查询入口修复**：`knowledge <query>` 位置参数可达（Typer group 默认命令处理）；删 `search_results = []` 空壳，接真实检索。
- [ ] S4-3 **端到端验证**：`daip knowledge "量子计算"` 返回《量子计算基础原理.md》相关片段。**门禁**: 实测返回非空真实结果。
- **注意**: 与 e2e knowledge 族（21 个已绿测试测的是底层 KnowledgeManager）不冲突，补 CLI 层测试即可。

### Stage 5: 混合路由落地（4-6 天，08-08 计划 H1-H6 续）——【Backlog：硬需求，暂缓实施】

**决策记录（2026-08-09 用户确认）**: 混合路由是**硬需求**（对应需求映射矩阵全部条目：本地预审/脱敏/云端委托/最小披露/人工确认），但**当前暂不实现**。实施降级为 Backlog，不进入当前上线时间线，不影响发布门禁 G1-G10。恢复实施时沿用 08-08 蓝图：

- H1 规则外置 → H2 SecurityGate v2（中文 PII/切片点）→ H3 CloudPool.execute() → H4 DelegationPipeline（feature flag）→ H5 人工确认流 → H6 业务接线。
- **门禁**: 各步测试绿 + 安全注入样本全拦截 + 人工确认三分支真跑。**回滚**: flag 关断即回纯本地。

### Stage 6: 体验与运营化（1 天）
- [ ] S6-1 **CLI 冷启动优化**：评估 lazy import（litellm/textual/streamlit 仅在对应命令时导入）；目标 ≤ 2s 或文档化接受。
- [ ] S6-2 **文档诚实化**：修正 `PRODUCTION_READINESS_FINAL.md`（65+/CI85/READY FOR MERGE 全部与实测不符）、README（badge、命令表、db 路径 `data/` vs 实际 root）。
- [ ] S6-3 **数据目录统一**：db 路径迁移到 `data/daip_live.db`（或改文档），与 AGENTS.md 对齐。
- [ ] S6-4 **turn_in_round 实现**（history_tracker.py:156 去 TODO）。

---

## 6. 生产上线计划

### 6.1 发布门禁（全部必须为真，缺一不发布）
| # | 门禁 | 验证命令 | 当前状态 |
|---|------|---------|---------|
| G1 | 全量测试 0F/0E（skip 有治理清单） | `poetry run pytest tests/ -q --tb=line` | ✅ 1738P/0F/0E（skip 治理未做） |
| G2 | ruff = 0 | `poetry run ruff check src/` | ❌ 11116 |
| G3 | mypy = 0 | `poetry run mypy src/daip_live/` | ❌ 8E |
| G4 | ast.parse 3.9 语义全过 | 新增检查脚本 | ❌ 6 语法错 |
| G5 | CI 全绿（含 e2e/security，无 continue-on-error） | GitHub Actions | ❌ 必红 |
| G6 | knowledge 端到端真实 | `daip knowledge "查询"` 返回真实结果；sync 后 `knowledge_sources > 0` | ❌ 壳 |
| G7 | 数据隔离：测试后 git status 无 db/faiss 变更 | `git status --short` | ⚠️ S3-1 已移出跟踪；测试隔离（S3-2）未做 |
| G8 | 备份可恢复（演练过） | 恢复演练记录 | ⚠️ 有备份未演练 |
| G9 | 文档与实测一致（抽查 3 处：README 命令表 / PRODUCTION_READINESS_FINAL / AGENTS.md 数据路径） | 人工对照 | ❌ |
| G10 | `daip run` TUI 冒烟一次会话 | 人工 | ⚠️ 未测 |

### 6.2 执行顺序与时间线（乐观，参照历史节奏打折）
| 窗口 | 内容 | 依赖 | 门禁 |
|------|------|------|------|
| 第 1-2 天 | Stage 3（数据隔离+恢复演练，先保命） | 无 | G7/G8 |
| 第 2-4 天 | Stage 1（静态清零）\| Stage 2（CI 硬化）并行 | S3 后 | G2/G3/G4/G5 |
| 第 4-5 天 | Stage 4（knowledge 接通） | S1 后（同域） | G6 |
| — Backlog | Stage 5（混合路由）— 硬需求已确认，暂缓实施 | 用户决策 2026-08-09 | 恢复时各步门禁 |
| 第 5-6 天 | Stage 6 + 终验 | 全部 | G1-G10 全绿 |

**注意**: 08-08 计划曾估 Stage 1 "1-2 天"实际耗了整日 + S2 整日 + 隔夜——本时间线按历史节奏已打折，**以实测为准，逐日复盘**。

### 6.3 发布判定（个人工具语义）
发布 = "日常可无脑依赖"：核心 3 命令（debate/ask/knowledge）+ TUI 冒烟通过 + 数据不丢（备份自动化+恢复演练）+ 门禁 G1-G10 全绿。不满足则继续，不强行"上线"。

---

## 7. Grill-Down 自审（对上述计划的批判验证）

### 7.1 关键声明证据表
| 声明 | 证据 | 可信度 |
|------|------|--------|
| 1738P/433S/0F/0E | 本会话 `pytest tests/ -q --tb=line -rs` 实测输出 | ✅ 直接取证 |
| 默认 pytest 只收 364 | `--collect-only -q` 输出 | ✅ 直接取证 |
| 6 invalid-syntax 未修 | ruff concise 定位两文件两行 + 读源码 L525 | ✅ 直接取证 |
| knowledge sync 空转 | 实跑 "Added: 13" + 随后 sqlite `knowledge_sources=0` | ✅ 直接取证 |
| 搜索空壳 | `auto --search "量子计算"` → No results + 源码 L192-196 + 同名 wiki 页在盘 | ✅ 双重取证 |
| 默认查询不可达 | `knowledge "量子计算"` → No such command | ✅ 直接取证 |
| DB 测试污染 | sqlite 分组：64/64 sessions 全 Test goal、dialogue_turns=0 | ✅ 直接取证 |
| debate 真实 | 实跑一轮，真实论点+摘要+DebateCompleteEvent 日志 | ✅ 直接取证 |
| 备份完整 | zip 19 项枚举含 db/config | ✅ 直接取证 |
| CI 必红 | ci.yml 读取 + ruff/mypy 本地实测 | ✅ 双重取证 |

### 7.2 诚实声明的不确定性（未达 100% 确证项）
1. **406 会话/611 轮历史数据是否真实用户数据、备份中是否可恢复**：08-08 评估标注"真实"，但当日测量值可能本身包含早期测试数据；备份 zip 内 db 未解压做行数核对（zip 完整性已验证）。S3-3 演练时一并确认。
2. **explicit `search` 命令**（knowledge.py:486）未实跑：逻辑上查 root DB 的 knowledge_sources（0 行）必空，但未逐行读完该命令体——不预先断言，S4 一并修。
3. **TUI（`daip run`）未自动化冒烟**：交互式 Textual 应用不适合非 TTY 自动化；门禁 G10 保留人工步骤。
4. **433 个 skip 中可修绿比例**：仅抽样了 wiki real 系列与真实内容生成两个族，其余（TUI 旧 spec 等）需 S2-4 审计时逐一确认。
5. **S1-2 ruff --fix 4103 项的行为风险**：自动修复多为格式类（I001/W292/W293/W291/UP015），但 UP006/UP035 改注解可能引入运行时差异——需分批复跑全量测试兜底，不预先承诺零风险。
6. **p7_gui（Web GUI）与 observability 的深度状态**：本轮未深测，仅靠 e2e 绿推断；上线前补一次冒烟。

### 7.3 方案最小性自审（YAGNI/KISS/SOLID）
- S1-1 修复 = 2 文件约 4 行改动（反斜杠提变量），最小。
- S3-2 隔离 = fixture 注入 DB 路径 + 保护断言，不新建框架。
- S4 修复 = 换 DB 构造 + 删空壳 + 接真实检索，不重写 KnowledgeManager（底层 21 个 e2e 已绿，证明底层可用）。
- 无方案引入新重依赖（types-* 属 mypy 官方配套；nomic-embed-text 属 Ollama 模型）。
- 唯一"扩功能面"是 Stage 5 混合路由——但那是用户明确需求（08-08 需求映射矩阵逐条对应），非我加戏。

### 7.4 回滚验证（每阶段失败退出路径）
- Stage 1：S1-1 单提交 revert；S1-2 分批提交、批级 revert；S1-3 双模块名修复单独提交。
- Stage 2：CI/testpaths 变更纯配置，revert 无运行风险。
- Stage 3：S3-1 是**唯一不可简单 revert** 的操作（git rm --cached 后重加回需手动）；故必须先备份、后操作、且需用户批准。S3-2 保护断言失败 = 说明隔离未生效，回退 fixture。
- Stage 4：knowledge 改动若破坏 e2e，revert 单提交（e2e 21 绿做回归哨兵）。
- Stage 5：feature flag 关断即回纯本地，业务零影响。

### 7.5 对计划自身的反例攻击（最严厉的一问）
1. **"1738 绿"会不会是白名单堆出来的？** 部分成立：433 skip 中有 2 个"刻意 RED"（真实 AI 内容生成未实现）+ wiki real 系列（08-08 建议修绿被跳过）。但 1738 个真跑绿不是虚的——门禁 G1 必须加"skip 治理清单"（S2-4），否则 1738 这个数字会继续掩盖缺口。
2. **Stage 3 放最前面会不会拖慢 CI 变绿？** 不会：S3 只动 git 跟踪与测试 fixture，与 S1 静态检查零冲突；且数据不丢优先级高于门禁变绿。先保命再装修。
3. **S1-2 的 ruff --fix 与 F821 人工处理会不会引入回归？** 会，除非分批+全量测试兜底——已在计划内（批级门禁）。F821 25 处需逐个看是"真 undefined（bug）"还是"动态注入（假阳性）"，后者白名单处理。
4. **S3-1 git rm DB 是否破坏 08-08 的"数据资产"叙事？** 不：文件仍在磁盘，只是离开 git 跟踪；数据安全反而提升（二进制噪音消除）。前提：备份已就位（已确认）。
5. **Stage 5 混合路由对单用户个人工具是否 YAGNI？** 已与用户确认（2026-08-09）：**硬需求，当前暂不实现，降级 Backlog**。理由：单用户本地场景下云端委托是增强项而非上线阻塞项；需求保留避免功能面缩水，实施延后避免为当前里程碑增负。恢复条件（建议写进 Backlog）：用户开始需要跨机/多 provider 工作流时触发。
6. **时间线可信吗？** 历史节奏打脸过（Stage 1 估 1-2 天实耗 1 天 + S2 连续 2 天战役）。本计划已按节奏打折并设每日复盘，但**诚实结论：11-12 天是乐观下限，真实可能 2-3 周**。
7. **测试污染教训会不会重演？** 会，除非 S3-2 的保护断言真的进 CI——"测试运行后 DB hash 不变"作为 pytest session fixture 是防回归的硬机制，已纳入门禁 G7。

---

## 8. 结论

- **真实状态（08-09 实测）**：测试 1738P/0F/0E（质变，S2 战役成果）+ CLI 10 命令全真实（debate 实跑通过、ask 真实现）+ 备份完整（Stage 0 兑现）+ history_tracker 修复为真 = **可修复工程态，约 5.3/10**（08-08 为 4.1/10）。
- **核心破损**：① 静态检查全红（11116 / 8E / **6 语法错未修**，CI 必红）；② **knowledge 管线三壳**（sync 空转 / 搜索空壳 / 默认入口不可达，`knowledge_sources` 结构性为 0）；③ **测试污染真实 DB**（dialogue_turns 归零，教训：无隔离 + DB 进 git）；④ 433 skip 白名单治理缺失；⑤ hybrid 混合路由零进展。
- **执行优先级**：Stage 3（数据隔离+恢复，S3-1 已批准执行）→ Stage 1（静态清零）∥ Stage 2（CI 硬化）→ Stage 4（knowledge 接通）→ Stage 6（体验+文档）。Stage 5（混合路由）已确认硬需求但**暂缓为 Backlog**，不阻塞上线。
- **上线判定**：门禁 G1-G10 全绿 + 核心 3 命令 + TUI 冒烟 + 数据不丢，缺一不发布。当前距离上线 = 静态清零 + CI 硬化 + 测试隔离 + knowledge 接通四项，估 1-2 周（乐观 5-6 天，不含 Backlog 的 Stage 5）。
