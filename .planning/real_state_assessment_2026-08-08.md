# DAIP-LIVE 真实状态测评与生产上线计划（2026-08-08 实测版）

**定位**: 个人生产级本地工具（非对外发布产品）+ 本地/云端混合模型调用（本地优先审核安全隐私）
**方法**: 本报告所有数字均为本次会话直接实测（命令执行取证），不转述历史文档；转述处明确标注来源。
**对照基线**: `docs/plans/true_state_assessment.md`（2026-08-07）+ `.planning/ROADMAP.md`

---

## 1. 实测数字总览（对照 08-07 基线）

| 维度 | 08-07 基线 | 08-08 实测 | 变化 | 取证命令 |
|------|-----------|-----------|------|---------|
| unit 测试 | 21F / 185P / 32E | **10F / 252P / 0E** | ✅ 32E 全消，21F→10F | `py -m pytest tests/unit/ -q --tb=no` |
| integration | 19F / 24P / 9E | **26F / 26P / 0E** | ⚠️ 9E 全消但 19F→26F（TUI 族由 ERROR 转 FAILED） | `py -m pytest tests/integration/ -q --tb=no` |
| security | 4F / 15P | **4F / 15P / 6w** | ➡️ 持平 | `py -m pytest tests/security/ -q --tb=line` |
| e2e | 1 语法错 | **18F / 21P / 11E（11.26s 实跑全量）** | ✅ 语法错已修且全量可执行 | `py -m pytest tests/e2e/ -q --tb=line` |
| ruff | 11191 | **11183** | ⚠️ 仅 -8 | `py -m ruff check src/ --statistics` |
| mypy | 8E / 7F | **8E / 7F** | ➡️ 持平 | `py -m mypy src/daip_live/` |
| 调试绕过 | 存在 | **已移除**（enhanced_debate_manager.py:98） | ✅ | 源码核对 |
| config embedding_dimension | 缺失 | **已补**（config.yaml:7, 768） | ✅ | 读文件 |
| CLI 命令 | — | **7 个注册；model/session/role 未挂载** | ⚠️ 幽灵功能 | `py -m daip_live.cli.main --help` |
| 数据库 | — | **root/daip_live.db 1.64MB，6 表有数据** | 新发现 | sqlite3 查询 |
| 本地模型 | Ollama 在跑 | **6 模型可用**（qwen3.5:4b/gemma4:e2b/deepseek-r1:8b/ministral-3:3b/phi3:mini/llama3） | ✅ | `curl /api/tags` |

**一句话现状**: 相比 08-07，测试骨架明显好转（unit 32E 清零、e2e 可收集），但 integration 仍有 26F、静态检查持平、且暴露了此前未发现的架构真相（CLI 假功能、hybrid 零接线、数据库知识摄取为空）。

---

## 2. 真实状态详解

### 2.1 正面事实（个人工具确实可用的部分）

1. **CLI 可启动**：`py -m daip_live.cli.main --help` 正常输出 7 命令（run/ask/debate/doc/role-intel/knowledge/wiki）。（有 runpy 双模块名警告，见 2.3）
2. **真实模型路径通**：`provider.py` 中 `ollama/*` 不落入 mock 分支（`is_local_model` 仅命中 `LOCAL_MODEL_CONFIGS` 的 test-model/mock-llm/local-gpt，见 local_models.py:23-39）；`ollama/llama3:latest` 走 `litellm.completion` 真实调用；embedding 有 `ollama list` 子进程真实探测 + fallback（provider.py:94-98, 202-228）。Ollama 实测运行中。
3. **数据有真实沉淀**：`daip_live.db` 1.64MB，sessions 406 行、dialogue_turns 611 行、debate_sessions 43 行、debate_turns 33 行——系统真实运行过、有落盘。
4. **模块化骨架完整**：26 个业务目录、304 个 py 文件；P1-P8 模块边界清晰；container DI 存在；unit 252 通过覆盖核心逻辑。
5. **hybrid 三件套代码存在**：security_gate.py（112 行，LOW/MEDIUM/HIGH 三档分类）、sanitization.py（88 行，API key/密码/路径脱敏）、cloud_pool.py（108 行，多 provider 池状态管理），各有 unit 测试（test_hybrid_cloud_pool.py / test_hybrid_sanitization.py，在 252P 内）。
6. **e2e 层 21 个测试真实通过**：全量 50 个 e2e 在 11.26s 内可执行，21 绿（api 端点、wiki 部分、knowledge 搜索等）——测试栈端到端可跑，不依赖慢速外部服务。

### 2.2 破损清单（全量，逐项可复现）

**测试（实测）**
- unit 10F：real_content_generation_green ×2、real_model_integration_green ×1、real_model_integration_red ×1、real_wiki_collaboration_red ×3、wiki_collaboration_core_green ×3（real 系列为真实模型/真实组件测试，个人工具本机 Ollama 可用，应能修绿而非豁免）。
- integration 26F，7 族：
  - test_tui_integration 4F + test_tui_copy_paste_integration 3F + test_tui_intent_recognition 2F = **TUI 族 9F**
  - test_wiki_multi_model_integration **8F**
  - test_enhanced_debate_features 2F + test_enhanced_debate_integration 5F = **debate 族 7F**
  - test_cli_intent_recognition **2F**
- security 4F（根因已实锤）：test_enhanced_debate_security.py 的 special_characters（7==1）/ concurrent_access（35==5）/ authorization（94==5）/ resource_limit（94==20）——**不是产品安全逻辑漏洞，是持久化污染**：`history_tracker.py:27-37` 构造参数写 `":memory:"` 却被静默替换成共享临时文件 `%TEMP%\daip_debate_history.db`；测试用固定 session_id（security_input_test_000 等）+ 无清理 fixture，前次失败运行留下的 session 累积 → 7/35/94 全为历史存量。`test_session_id_validation` 等通过是因为断言对累积不敏感。
- e2e 全量实跑：**18F / 21P / 11E（11.26s）**，证明 e2e 不依赖外部服务（fixture 本地实现）。失败分 4 族：
  - **api datetime 序列化真 bug**：`test_get_nonexistent_session_e2e` → `json.encoder.py:180 TypeError: Object of type datetime is not JSON serializable`（FastAPI 响应返回 datetime 对象）。
  - **knowledge 族 11 个 ERROR 的 fixture 契约错**：`tests/e2e/test_knowledge_collaboration_e2e.py:63` fixture 把 **dict** 传给 `KnowledgeManager`，实现 `manager.py:29` 要 `config.directory` 属性 → `AttributeError: 'dict' object has no attribute 'directory'`（9 ERROR）；test_tui_interaction_e2e.py 的 TestTUIDisplayE2E 另有 2 ERROR（同族 setup 失败）。
  - **debate 族 6F**（test_enhanced_debate_e2e.py）：与 integration debate 族同源。
  - **wiki 族 5F + 1F**：与 integration wiki 族同源（含完整用户场景）。
  - **21 个通过**：api 大部分、wiki 部分、knowledge 搜索等真实绿。

**静态检查（实测）**
- ruff 11183：E501 3102、W293 2765、UP006 1999、T201 998、F401 557、UP035 469、I001 337、W292 251、W291 239、其余约 1066（含 F821 25、E722 44 真 bug 候选）。**含 6 处 invalid-syntax**：agile_task_system_core.py:525 + tui_compatible_integrator.py:335 的 f-string 表达式内反斜杠（`{"\\n\\n".join(...)}`）——Python 3.9-3.11 直接语法错误，而 pyproject 声明 `requires-python >=3.9,<3.13`。
- mypy 8E/7F：全部为 import-untyped（yaml/aiofiles/markdown/requests）+ "Source file found twice under different module names: daip_live.intent_recognition.context_manager / src.daip_live.intent_recognition.context_manager"。

**配置冲突（实测）**
- pytest.ini（4 行：pythonpath/norecursedirs/asyncio_mode/asyncio_default_fixture_loop_scope）存在时，`pyproject.toml` 的 `[tool.pytest.ini_options]`（testpaths/markers/strict-markers）**被完全忽略**——所有 `@pytest.mark.integration/unit/e2e/slow` 产生 PytestUnknownMarkWarning。
- `pytest-asyncio` 同时出现在运行时依赖（pyproject:15）与 dev 依赖（pyproject:46）——测试框架进了生产依赖。

### 2.3 架构真相（源码逐行核实）

**A. CLI 假功能**
- `debate start`（cli/main.py:94,109）：对 async generator 用**同步 `for` 迭代** → 抛 TypeError 被 except 吞掉 → L122-134 打印"简化辩论管理器导入成功 / 支持者第1轮发言: 简化的观点..."**假成功演示**。真辩论从未执行。
- `ask`（cli/main.py:509-582）：`_handle_debate_intent` 等 4 个 handler 全部打印 `Would start debate...` 占位，**不执行任何动作**。
- `doc download/search` 为真实调用（PaperDownloader）——已实测核实：**主实现 `doc/paper_downloader.py` 用 arxiv HTTP API 直连（`export.arxiv.org/api/query`），不依赖 arxiv 库**；`doc/tools/paper_downloader.py:15-21` 有 `try: import arxiv / except ImportError: arxiv=None` 防御，不会 ImportError 崩溃，但 arxiv=None 时该实现运行期 AttributeError（双实现并存）。doc 命令真实执行列入 Stage 1 冒烟矩阵。

**B. 幽灵功能（文件存在、零接线）**
- `cli/commands/model.py`、`session.py`、`role.py` 存在，但 main.py 仅注册 knowledge/wiki/role-intel——`daip model status` 实测报 **No such command**（README 声称可用）。
- **hybrid 三件套业务零引用**：`rg "from daip_live.hybrid" src/daip_live -g "*.py"` 仅命中 `hybrid/__init__.py` 自身；`container.py` 无任何 hybrid 注册（rg 无匹配）——安全门/脱敏/云端池从未进入任何业务路径。

**C. 半成品**
- CloudPool 只有数据结构（provider 状态、并发计数、API key 环境变量检查），**没有发起 LLM 调用的方法**——DelegationRequest/DelegationResult 定义了但无执行者。
- SecurityGate 的 MEDIUM 处置语义矛盾：类注释写 "Auto-sanitize, local execution"（自相矛盾，脱敏后本地执行则脱敏给谁看？）；无人工确认流程实现。
- Sanitization 正则误报高：`password\s+([^\s,;.]+)` 会把 "password protection" 的 "protection" 当密码红action；`token` 关键词误伤正常语境；**不覆盖人名/邮箱/电话等 PII**。

**D. 双模块名**：cli/main.py:26 `sys.path.insert(0, .../src)` 导致 `daip_live` 与 `src.daip_live` 双身份（mypy 8E 之一 + runpy RuntimeWarning 同源）。

**E. 静默落盘的 `:memory:` 缺陷（本轮新发现）**：`history_tracker.py:27-37` 构造默认 `db_path=":memory:"`，但实现把 `":memory:"` 替换为 `tempfile.gettempdir()/daip_debate_history.db`（共享磁盘文件）。调用方（含全部测试）以为在用内存库，实际所有实例共享系统临时目录同一个文件 → 测试跨运行污染（security 4F 根因）+ 潜在并发写冲突。此为产品级缺陷（隔离不可能 + 行为与参数签名不符）。

**F. 配置对象契约不一致**：`KnowledgeManager.__init__`（knowledge/manager.py:29）以属性方式访问 `self.config.directory`，而 e2e fixture 传 dict → `AttributeError: 'dict' object has no attribute 'directory'`（knowledge 族 11 ERROR 根因）。API 期望"对象"但无类型约束，调用方按 dict 构造即崩。

**G. 文档错位**：AGENTS.md 声称 `data/daip_live.db`，实测库在**项目根目录**；`data/` 下仅 logs。README 的 3.9+ / code_quality A badge / model/session/role 命令均与实际不符（实测打脸）。

### 2.4 数据资产实况

| 表 | 行数 | 含义 |
|----|------|------|
| sessions | 406 | 会话记录（真实） |
| dialogue_turns | 611 | 对话轮次（真实） |
| debate_sessions | 43 | 辩论场次（真实） |
| debate_turns | 33 | 辩论轮次（真实） |
| knowledge_sources | **0** | **知识摄取从未成功**（index.faiss 存在但空） |

---

## 3. 全面测评（8 维度，个人工具加权）

评分标准：1-10，10 = 个人日常可无脑依赖。证据全为 2.1-2.4 实测。

| 维度 | 权重 | 分 | 核心证据 | 一句话结论 |
|------|------|-----|---------|-----------|
| 核心功能可用性 | 25% | **4** | CLI 能跑但 debate 演示壳、ask 占位、wiki 集成 8F、knowledge_sources=0 | 骨架在，核心流程没跑通 |
| 模型接入 | 15% | **7** | ollama/* 走真实 litellm、embedding fallback 真、6 模型在线；但 get_available_models 硬编码、无混合路由 | 本地真调用通，云端/路由未建 |
| 数据安全与隐私 | 20% | **3** | hybrid 零接线、无备份机制、db 路径错位、脱敏不覆盖 PII、知识库为空 | 用户核心需求 = 现状 0 分起点 |
| 测试守护 | 15% | **4** | unit 252P 真实、integration 26F、e2e 18F/21P/11E（11s 可全跑）、security 4F=测试污染、配置冲突 | 一半红一半绿，不可作门禁；但测试栈可执行性已恢复 |
| 代码质量 | 10% | **3** | ruff 11183、mypy 8E、6 语法错、双模块名 | 静态检查全红 |
| 文档与定位一致性 | 10% | **2** | README 三处虚假（badge/版本/命令）、开源示范叙事 | 与"个人生产级工具"定位严重不符 |
| 可维护性 | 5% | **4** | 模块化好、DI 在；幽灵功能多、半成品多 | 架构底子好，卫生差 |
| 性能与体验 | 0%（未测） | — | 未做启动/响应实测 | 列入 Stage 4 |

**加权总分 ≈ 4.1/10。** 结论：底子是真模块化架构 + 真模型路径 + 真数据；现状是"半成品演示级"而非"个人生产级"。

---

## 4. 混合本地/云端架构：需求 → 现状 → 落地设计

### 4.1 需求映射矩阵（用户需求逐条 vs 现状）

| 用户需求 | 现状 | 差距 |
|---------|------|------|
| 本地和云端混合，本地优先 | 仅本地（ollama），无云端配置（config.yaml 无 provider/api_key 段） | 需补 CloudPool 接线 + config 扩展 + 路由层 |
| 本地优先审核安全隐私 | security_gate.py 存在但零接线 | 需接入业务调用链（agent_engine/container） |
| 确保无安全隐患的任务交付多个云端 | CloudPool 有 provider 池但**无 LLM 调用方法**、无健康检查、无轮询 | 需补 execute() + 探活 + 降级 |
| 每个云端只能看到无隐患的局部上下文 | **无上下文切片机制**，只有整 prompt 脱敏 | 需设计任务分片/最小化披露 |
| 自动预审放行低风险，高风险转人工确认 | RiskLevel.HIGH 枚举存在，**人工确认流程不存在** | 需接 permission/user_response_collector + TUI/CLI 确认入口 |
| 审核规则与脱敏管线全在本地 | 规则硬编码在源码，脱敏正则误报高 | 规则外置 config.yaml + 规则增强 |

### 4.2 目标管线（落地蓝图）

```
用户任务
   │
   ▼
[1] 本地预审 SecurityGate v2        ← 规则来自 config.yaml（本地）
   ├─ LOW    → [2] 直接委托 CloudPool（云端只见该任务）
   ├─ MEDIUM → [3] 本地脱敏（sanitize_prompt v2 + PII 人名/邮箱/电话）
   │            └─ 脱敏后仍含业务上下文 → 尝试切片外包；无法切片 → 本地执行
   └─ HIGH   → [4] 人工确认（阻塞等待，TUI 弹窗/CLI 提示，接 user_response_collector）
                 ├─ 批准 → 本地脱敏后委托 / 本地执行
                 └─ 拒绝 → 本地执行或终止
[5] 云端执行 CloudPool.execute()     ← 每个云端仅收一个脱敏/切片子任务
   ├─ 健康检查（provider 状态 + API key + 限流）
   ├─ 并发上限（max_concurrent 已存在）
   └─ 失败降级（下一 provider / 回落本地）
[6] 结果回填（脱敏还原映射表 → 原始上下文）
```

设计原则：**默认本地**（config 未配云端 API key 时全链路本地，行为不变）；**最小化披露**（每云端只见单任务分片）；**人工确认必须真实阻塞**（HIGH 不静默降级）。

### 4.3 分步实施（TDD，每步含测试与回滚，Grill-Down 5 步自审随行）

- **H1: 规则外置** — config.yaml 增 `security_rules:` 段（模式/风险级/处置）；SecurityGate 从配置加载。测试：规则表驱动（新增规则立即生效）。回滚：config 回退默认内置规则。
- **H2: SecurityGate v2** — context 感知（工具调用/文件访问标记）、中文 PII 模式、切片点标记（返回哪些子句可外包）。测试：注入样本集（含中文、路径、凭证）。回滚：保留 v1 类名兼容。
- **H3: CloudPool 补 execute()** — litellm 真实调用 + 超时 + 重试 + 状态流转（AVAILABLE/UNAVAILABLE/RATE_LIMITED）。测试：mock litellm 验证池语义；真实 litellm 冒烟走 Ollama（无 key 时降级本地）。回滚：新方法不破坏现有池 API。
- **H4: DelegationPipeline** — preflight→sanitize→slice→delegate→verify 编排 + container 注册。测试：全 mock 管线集成；安全注入样本（凭证/路径/中文 PII 不得出本地边界）。回滚：管线未启用开关（feature flag）。
- **H5: 人工确认流** — 接 user_response_collector，HIGH 任务异步等待确认（TUI 通知 + CLI 命令）；确认记录入库。测试：确认/拒绝/超时三分支。回滚：确认器 mock。
- **H6: 业务接线** — agent_engine/intent_recognition 的模型调用点接入管线；config 增云端 provider 示例（api_key_env 引用，不存明文）。测试：端到端 LOW 任务真实外包（本机 mock 云端端点）+ MEDIUM 脱敏断言 + HIGH 人工确认。

---

## 5. 优化与生产上线计划（衔接 ROADMAP Phase 2-5）

ROADMAP 继续有效；本节按"个人生产级本地工具"定位重排优先级并补充数据安全与混合路由。

### Stage 0: 数据安全基线（今天，1 小时内）
- [ ] S0-1 备份脚本：`daip_live.db` + `knowledge/` + `config.yaml` → `backups/daip-<日期>.zip`；写恢复演练步骤（个人数据 1.6MB，必须可恢复）
- [ ] S0-2 记录基线：git tag `pre-production-2026-08-08`（当前 19 改动文件先提交或 stash 决策）
- **门禁**: 备份文件可解压、sqlite 打开行数一致。**回滚**: 无（纯增量脚本）。

### Stage 1: 真实可用性（≈1-2 天）— 修"假功能"
- [ ] S1-1 pytest 配置统一：合并 pytest.ini 进 pyproject `[tool.pytest.ini_options]`，删除 pytest.ini；markers 警告消除、strict-markers 生效（ROADMAP 05-03 前置）
- [ ] S1-2 挂载 model/session/role 命令（3 文件已存在，main.py 补 import + add_typer）；`daip model status` 冒烟绿
- [ ] S1-3 修 debate start：async 迭代（`async for`）、删除 L122-134 假演示代码；真模型 1 轮辩论端到端成功
- [ ] S1-4 ask 处置：真实现或明确标注未实现（删除 Would 占位欺骗）
- [ ] S1-5 6 处 invalid-syntax 修复（f-string 反斜杠提变量）——同时解决 3.9-3.11 兼容（ROADMAP 03-01）
- **门禁**: 冒烟矩阵表（README 全部命令逐条执行，真成功或文档删改）；`ast.parse` 全量 0 失败。**回滚**: 每项单提交，`git revert` 单项。

### Stage 2: 测试恢复（3-5 天）— integration 26F 三族（ROADMAP Phase 2 续）
- [ ] S2-1 TUI 族 9F：根因已定位——测试把 async 方法当 sync 调用（`on_input_submitted` 协程从未 await，test_tui_integration.py:39）；逐测试修复 await + 修正 mock 目标
- [ ] S2-2 wiki 族 8F：AsyncMock 未 await（collaborative_wiki.py:110）+ 中文主题语义映射缺 'critic' + Mock 依赖链简化
- [ ] S2-3 debate 族 7F + security 4F 一并修：**history_tracker 隔离改造**（`history_tracker.py:27-37` 的 `:memory:` 静默落盘改为真内存库或可注入 db_path，配合测试用 tempfile fixture 每次清库）——这是 security 4F 全部 + debate 族部分共根因
- [ ] S2-4 CLI intent 2F + unit 10F（real 系列走本机 Ollama 真跑，wiki_collaboration_core_green 对齐生产）
- [ ] S2-5 e2e 修复（已实跑摸底完成）：api datetime 序列化（响应模型转 str/ISO）→ knowledge 族 fixture 契约（dict→配置对象，或实现放宽为 Mapping）→ debate/wiki 族随 S2-2/S2-3 同步绿 → tui display 2 ERROR
- **门禁**: unit 0F、integration 0F（或 mock-only 类显式豁免清单）、security 0F、e2e 0F/0E（全部 50 个绿，或以环境前置显式豁免清单）。**回滚**: 按测试族分批提交。

### Stage 3: 静态与安全门禁（2-3 天，可并行 Stage 2）
- [ ] S3-1 ruff 分区清零：invalid-syntax → F821/E722 真 bug 人工 → 格式类 `ruff --fix` 批量（ROADMAP Phase 4）
- [ ] S3-2 mypy 清零：双模块名修复（删 cli/main.py:26 的 sys.path.insert，靠正确安装）+ types-* stubs（ROADMAP 03-02/03-03）
- [ ] S3-3 pytest-asyncio 从运行时依赖移出（pyproject:15）
- **门禁**: `ruff check src/` 0、`mypy src/daip_live/` 0。**回滚**: 分区提交，逐区 revert。

### Stage 4: 混合路由落地（4-6 天）— 第 4 节 H1-H6 全量
- **门禁**: H1-H6 各步测试绿 + 安全注入样本全拦截 + 人工确认三分支真跑。**回滚**: feature flag 关断即回纯本地。

### Stage 5: 日常运营化（1-2 天）
- [ ] S5-1 README 重写为个人工具定位：删虚假 badge（code_quality A / python 3.9+）、命令表与实测一致、写备份/恢复说明（ROADMAP 05-02）
- [ ] S5-2 CI 硬化：去 `continue-on-error`、纳入 e2e/security、markers 生效（ROADMAP 05-01）
- [ ] S5-3 数据目录统一：db 路径改为 `data/daip_live.db`（或更新文档）+ 启动冒烟 + 冷启动计时
- **门禁**: CI 全步骤绿、README 无虚假声明、`daip run` 冒烟一次会话。

---

## 6. Grill-Down 自审（对上述计划的批判验证）

按 `.planning/autonomous_plan/grill_down_template.md` 5 步框架逐条自审：

### 6.1 每个关键声明的证据行

| 声明 | 证据 | 可信度 |
|------|------|--------|
| unit 10F/252P | 本会话实测输出（2026-08-08 实测） | ✅ 直接取证 |
| integration 26F 7 族 | 本会话实测 + 26 行 FAILED 清单 | ✅ 直接取证 |
| e2e 18F/21P/11E | 本会话全量实跑（11.26s，-q --tb=line） | ✅ 直接取证 |
| api datetime 序列化 bug | e2e 输出 `json.encoder.py:180 TypeError: Object of type datetime is not JSON serializable` | ✅ 直接取证 |
| knowledge 11 ERROR 契约错 | e2e setup 输出 `manager.py:29 AttributeError: 'dict' object has no attribute 'directory'` + 测试 fixture 源码:63 | ✅ 直接取证 |
| security 4F = 持久化污染 | `history_tracker.py:27-37` `:memory:` 静默替换 temp 文件 + 测试固定 session_id + 断言输出 7==1/35==5/94==5/94==20 | ✅ 源码+输出双取证 |
| doc/arxiv 非 ImportError | `doc/paper_downloader.py` HTTP 直连无库依赖 + `doc/tools/paper_downloader.py:15-21` try/except fallback | ✅ 源码核实 |
| debate start 假演示 | cli/main.py:94/109 同步 for + L122-134 假打印 | ✅ 源码核实 |
| hybrid 零接线 | `rg "from daip_live.hybrid" src/daip_live -g "*.py"` 仅命中 __init__；container.py 无匹配 | ✅ 工具核实 |
| ollama/* 走真实路径 | local_models.py:45-47 + provider.py:276-310 源码链 | ✅ 源码核实 |
| knowledge_sources=0 | sqlite3 实测行数 | ✅ 直接取证 |
| 6 invalid-syntax | ruff --statistics + 两文件 518-540 行源码定位 | ✅ 直接取证 |
| pytest 配置冲突 | pytest.ini 4 行实测 + pyproject:71-96 读文件 + PytestUnknownMarkWarning 实测输出 | ✅ 直接取证 |

### 6.2 诚实声明的不确定性（未达 100% 确证项）

1. ~~e2e 未实跑~~ **已实跑**：18F/21P/11E 全量取证；剩余不确定 = 11 个 ERROR 中 TUI display 2 个的精确 fixture 断言、18F 中 debate/wiki 族与 integration 是否同一断言实例——待 Stage 2 逐条修绿时确认。
2. **integration 26F 的逐断言细节**：仅深挖了 TUI input_handling（async 未 await）与 wiki role_intelligence_selector（中文缺 critic + Mock 链）两个样例；TUI model_switching/autocomplete/background_task、debate 族 7F 的具体断言原因待 Stage 2 逐条打开——**不预先声称根因**。
3. **doc download/search 实际执行行为**：依赖结构已核实（主实现 HTTP 直连、tools 实现有 fallback），但未实际执行一次下载（需联网 + 真实 arxiv 请求）——Stage 1 冒烟矩阵覆盖。
4. **`daip run`（TUI）** 未实跑（交互式 TUI 不适合自动化冒烟），Stage 5 冒烟门禁。
5. **unit real 系列 7F 是否本机 Ollama 能修绿**：逻辑上 ollama/* 真实路径通，但需实测修绿——不预先断言。
6. ~~security 4F 根因未开~~ **已开**：持久化污染 + `:memory:` 静默落盘（双证据）；待修 = tracker 隔离 + 测试 fixture 清库后能否全绿（可能与 debate 族共享该根因）。

### 6.3 方案最小性自审（YAGNI/KISS/SOLID）

- S1-3 debate 修复 = 改迭代方式 + 删假打印（约 10 行），不重写辩论系统——最小。
- H1-H6 混合路由 = 复用已有三件套补 execute + 接线，不新建模块——最小（CloudPool 数据结构已够用）。
- 无方案引入新依赖（除 types-* stubs，属 mypy 官方配套）。
- 每阶段可回滚：单提交/feature flag/配置回退，无不可逆步骤。

### 6.4 回滚验证（每阶段的失败退出路径）

- Stage 0：备份脚本独立文件，失败=不产生副作用。
- Stage 1：每项单 commit，`git revert <hash>` 单项回滚；配置合并若破坏测试收集，恢复 pytest.ini。
- Stage 2：按测试族分 commit，族级 revert。
- Stage 3：ruff 分区提交；mypy 修复若引入新错，revert 双模块名修复单独提交。
- Stage 4：DelegationPipeline 以 feature flag 启用，关断即回纯本地，业务零影响。
- Stage 5：文档/CI 修改无运行风险。

### 6.5 执行验证协议（每步 TDD 红→绿）

1. 先写/改测试（红灯，命令输出留档）→ 2. 最小实现（绿灯）→ 3. 相邻测试回归（无新红）→ 4. 提交。禁止为通过而删/弱化测试（ULTRAWORK 条款）。

---

## 7. 结论

- **真实状态**：模块化底子 + 真实模型路径 + 真实数据（406 会话/611 轮对话/43 辩论）+ 21 个真实通过的 e2e 为可用资产；CLI 假功能（debate 演示壳、ask 占位）、幽灵功能（model/session/role 命令、hybrid 三件套）、integration 26F、e2e 18F/11E（含 api datetime 序列化真 bug）、ruff 11183、知识库零摄取为真实破损。
- **个人工具判定**：当前 = 半成品演示级（4.1/10），不可作为生产工具依赖；但距离"可用"无结构性障碍——测试骨架已恢复大半，真实模型链路已通，最大短板是"假功能清理 + 测试修绿 + 混合路由接线 + 数据备份"。
- **执行顺序**：Stage 0（备份，今天）→ Stage 1（假功能清理 + 配置统一）→ Stage 2（测试恢复，含 e2e 18F/11E 修复与 history_tracker 隔离）→ Stage 3（静态清零）→ Stage 4（混合路由）→ Stage 5（运营化）。
- **混合路由落地前提**：SecurityGate/Sanitization/CloudPool 已写好一半，补 execute() + 切片 + 人工确认 + 接线即可，不需要推倒重来。
