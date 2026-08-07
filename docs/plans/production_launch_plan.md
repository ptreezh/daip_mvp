# DAIP-LIVE 真实状态测评与生产上线计划

**日期**: 2026-08-06
**评估对象**: D:\DAIP\refactdoc（分支 `gnhf/-055e31` @ `6f31c13`，62 commits，远端仅 origin/main）
**评估方式**: 5 路并行探索 + 关键证据直接核验 + Oracle 生产就绪评审（nemotron-3-ultra-free）+ grill-down 决策（Q1-Q3 用户确认）
**评估结论**: **35/100，NOT READY（未达生产标准）**——架构骨架完整，但存在 5 项运行时阻断级问题、测试可信度崩塌、零可观测性。

---

## 1. 项目真实状态（事实层）

### 1.1 总体判断

DAIP-LIVE 是一个**骨架完整、血肉未愈**的个人生产级 AI 助手工作站。P1-P8 模块化结构、事件驱动 agent 循环、SQLite 本地持久化、Textual TUI + FastAPI Web GUI 的架构方向是正确的，且 62 次提交、2224 个测试的规模说明项目经历过大量开发。但**测试规模与真实可靠性严重倒挂**：测试越多，越不可信。

### 1.2 架构事实（已核验）

| 层级 | 现状 | 证据 |
|------|------|------|
| P1 持久化 | SQLite + SQLAlchemy 2.0，但使用 Pydantic v1 弃用 API | `persistence/database.py:39` |
| P2 知识管理 | FAISS 索引，embedding 维度硬编码 384 | `knowledge/manager.py:34`（含 `TODO: Make this configurable`） |
| P3 模型提供 | LiteLLM 统一接口，配置默认 ollama/llama3:latest + nomic-embed-text | `config.yaml:8-9` |
| P4 角色/工具 | 角色 YAML 驱动；`basic_tools` 层 13 个工具**无外部调用** | `basic_tools/__init__.py` + `core.py`（仅 2 个被废弃 TUI 直接 import） |
| P5 Agent 引擎 | 动态循环 + session/state 管理（已清理 3 个废弃文件，保留被依赖的 2 个） | git `6f31c13` |
| P6 CLI/TUI | CLI 重构中（`cli.py`/`cli_main.py` 已删 → `cli/main.py` 包，**未提交**）；简化版 TUI 2962 行，基线 7 测试通过 | git status；`tui/simplified_main.py` |
| P7 Web GUI | `p7_gui/`（FastAPI）为现行；`p7_gui_v1/` 为遗留，含语法错误测试文件 | `p7_gui_v1/test/uat/runner.py:33` |
| P8 辩论 | 优化架构默认开启，但模型错误被吞并伪造"成功" | `enhanced_debate_manager.py:582-586` |

### 1.3 测试现实（已核验）

- **2224 个测试**（收集 7.59s，实测），100+ 测试文件，**5250 处 mock 引用分布在 146 个文件**（直接 rg 实测）
- `tests/test_dependency_hang.py`：6 个测试仅 `assert True`（导入即通过，零行为覆盖）
- `tests/unit/test_real_model_integration_red.py`：**故意 `pytest.fail()` 的 TDD 红灯测试残留在套件中**
- **零 CI**：无 `.github/` 目录，无任何合并门槛
- `p7_gui_v1/test/uat/runner.py:33`：语法错误导致 mypy 无法解析
- 亮点：TUI 集成 + e2e 基线 7 个测试真实通过（45.3s，含真实辩论优化路径）

### 1.4 运维现实（已核验）

- **日志零配置**：20+ 模块 `logging.getLogger(__name__)`，但全局无 `basicConfig`；仅 `intent_recognition/error_handling.py` 有一处局部 `FileHandler`
- 配置：`config.yaml` 7 区段（database/debate/knowledge_base/llm_provider/mcp/paper/role_manager/wiki），MCP 服务 markdownify(8081) + scihub(8082) 默认启用，`allowed_domains` 仅 arxiv.org + doi.org，默认策略 `ask`
- `pyproject.toml:11` `requires-python` 表达式为 ruff 无法解析的写法；入口 `daip = daip_live.cli.main:app`（指向重构后的包，工作树未提交状态下可运行）

### 1.5 进行中的工作（未提交）

工作树存在未提交变更：CLI 包化重构（删除 `cli.py`/`cli_main.py`，新建 `cli/main.py` 包 + 11 个相关文件修改），`docs/plans/` 未跟踪。**评估期间不得改动这些文件。**

---

## 2. 生产就绪度测评（评分 35/100，NOT READY）

### 2.1 评分依据（5 条）

1. **运行时必崩**：SQLAlchemy 2.0 已移除 `session.dict()`，所有会话保存/加载在 ≥2.0 运行时失败；embedding 维度硬编码 384，换任何非 nomic 模型即建索引失败（静默）。
2. **数据造假**：辩论管理器吞掉 `ModelError`，以错误文本冒充成功回复——用户无法区分真实输出与伪造输出。
3. **零可观测性**：无日志配置，生产故障不可定位，无审计轨迹。
4. **测试即剧场**：2224 测试中大量 mock-to-nothing；故意失败的红灯测试留在套件；零 CI 无法设门槛。
5. **死代码冒充功能**：`basic_tools` 13 工具无真实挂载；遗留 GUI v1 含语法错误测试。

### 2.2 Top 5 阻断问题（按生产风险排序）

| # | 问题 | 证据 | 为什么阻断 | 最小修复 |
|---|------|------|-----------|---------|
| 1 | SQLAlchemy 2.0 `session.dict()` 已移除 | `persistence/database.py:39` | 所有会话保存/加载在运行时失败 | 改为 `session.model_dump()`（Pydantic v2） |
| 2 | embedding_dim=384 硬编码 | `knowledge/manager.py:34` | 换嵌入模型即索引维度错配（静默失败） | 从 provider/config 读维度，加载索引时校验 |
| 3 | 辩论静默造假 | `enhanced_debate_manager.py:582-586` | 用户拿到"成功"的伪造辩论结果 | 移除吞异常，`ModelError` 向上传播，UI 显示错误边界 |
| 4 | 零日志基础设施 | 全局无 handler | 故障不可定位，无审计 | container 引导时配 `RotatingFileHandler`，由 config.yaml 驱动 |
| 5 | 无 CI + 测试不可信 | E5 全套证据 | 无法设合并门槛，回归无法拦截 | 最小 GitHub Actions（ruff+mypy+pytest）；删红灯测试；修 runner.py 语法 |

---

## 3. 优化计划

### 3.1 KEEP / DELETE 评估

| 代码层 | 裁决 | 理由 | 动作 |
|--------|------|------|------|
| `basic_tools/`（13 工具） | **DELETE** | 仅 2 个函数被废弃 TUI 直接 import；`register_basic_tools` 无外部调用点；依赖 arxiv/scholarly/python-docx 为它服务 | 删除整个目录；清理 pyproject 依赖 |
| `tests/test_real_model_integration_red.py` | **DELETE** | 故意 `pytest.fail()` 的 TDD 残留 | 删除 |
| `tests/test_dependency_hang.py` | **DELETE** | 6 个测试仅 assert True | 删除 |
| `p7_gui_v1/`（遗留 GUI） | **DELETE/ARCHIVE** | 被 `p7_gui/` 取代；测试有语法错误 | 归档后删除 |
| `p7_gui_v1/test/uat/runner.py` | **REPAIR** | 语法错误阻断 mypy；UAT runner 概念有价值 | 修 L33 语法 |
| P1-P8 核心 + `tui/` + `cli/` + `p7_gui/` + `memory/` + `permission/` + `security/` + `container.py` | **KEEP** | 现行架构主体 | 修复 E1-E3 后继续演进 |

### 3.2 测试套件康复策略

| 类别 | 动作 | 目标 |
|------|------|------|
| 纯 import/assert-True 测试 | DELETE | -500 级 |
| TDD 红灯残留 | DELETE | 清零 |
| mock-to-nothing 测试 | 移入 `tests/quarantine/` | -800 级 |
| 真实 DB/FAISS/Ollama 集成测试 | KEEP + 扩展 | +20 级 |
| TUI e2e（7 个真实通过） | KEEP | 7 |

新增高价值测试优先级：安全门契约测试 → 脱敏管线往返测试 → 辩论故障注入测试 → SQLAlchemy 2.0 持久化测试 → embedding 维度兼容测试。

---

## 4. 生产上线计划（6 阶段，4 周）

### Phase 0: 地基稳定（第 1 周）— 退出标准：干净构建 + 有日志
- 修 `session.dict()` → `model_dump()`（E1）
- embedding 维度动态化（E2）
- container 引导加 `RotatingFileHandler`（E9）
- 修 pyproject `requires-python`（E6）
- 验证：`py -m pytest tests/unit/persistence -v` 通过；`daip run` 产出 `data/logs/daip_live.log`

### Phase 1: 辩论系统说真话（第 1-2 周）— 退出标准：无静默造假
- 移除 `enhanced_debate_manager.py:582-586` 的吞异常
- TUI 辩论视图加错误边界：用户看到 "模型不可用: {error}" 而非伪造内容

### Phase 2: 死代码清除（第 2 周）— 退出标准：精简代码库
- 删 `basic_tools/`、`test_dependency_hang.py`、`test_real_model_integration_red.py`
- 归档/删除 `p7_gui_v1/`
- 验证：pytest 收集 ≤2200，无 import 错误

### Phase 3: 测试康复 + CI 门槛（第 2-3 周）— 退出标准：可信 CI 门
- 建 `.github/workflows/ci.yml`（ruff + mypy + pytest，unit/integration 分跑）
- 5 个高价值集成测试从 mock 转真实组件（DB/FAISS/Ollama）
- mock 引用减少 ≥50%，真实路径覆盖率 ≥60%

### Phase 4: 混合委派 MVP（第 3-4 周）— 退出标准：LOW 风险任务可上云
- 安全门（风险分类 HIGH/MEDIUM/LOW，规则文件 `config/security_rules.yaml`）
- 脱敏管线（PII/密钥剥离 + 本地 ID 令牌化，presidio-analyzer）
- 云提供方池（LiteLLM 多 provider，成本感知路由）
- 验证：`daip run` 委派总结任务上云成功、结果合并、审计日志入库

### Phase 5: 可观测与加固（第 4 周）— 退出标准：可运维
- JSON 结构化日志 + 轮转
- FastAPI `/healthz` 健康检查
- 优雅关闭（SIGTERM → 干净关库/刷索引/刷日志）

---

## 5. 混合架构设计（本地安全门 + 脱敏管线 + 多云委派）

### 5.1 架构原则（用户 Q2/Q3 决策固化）

- **本地优先安全**：安全门、脱敏管线、审核规则全部本地执行
- **多云委派**：零风险任务外包给多个云端；**每个云端任何时候只能看到脱敏后的局部上下文**
- **混合审核**：自动预审放行低风险任务，高风险自动转人工确认（阻塞式 UI 提示）

### 5.2 数据流

1. 任务进入 → 安全门分类（规则引擎，本地 YAML/JSON）
2. HIGH → 人工确认（阻塞）
3. MEDIUM → 自动脱敏 → 本地执行 + 审计日志
4. LOW → 自动脱敏 → 云池委派（轮询/成本感知）
5. 云端响应 → 脱敏校验（无意外数据外泄）→ 合并入本地上下文
6. 全路径 → 本地 agent 循环继续，SQLite 全量审计

### 5.3 脱敏边界（具体规则）

| 输入类型 | 脱敏规则 | 云端可见 |
|---------|---------|---------|
| 用户提示词 | 剥离文件路径/API 密钥/密钥（正则 + LLM 分类器） | 仅脱敏文本 |
| RAG 上下文 | 本地 ID → 不透明令牌；PII 经 presidio 剥离 | 令牌化分块 |
| 工具调用 | **绝不**上云，仅本地执行 | 阻断 |
| 模型配置 | 仅模型名 + 参数（无密钥、无本地端点） | 白名单字段 |
| 会话历史 | 最近 N 轮，PII 剥离，无工具结果 | 脱敏文本 |

### 5.4 运行位置分工

| 组件 | 位置 | 理由 |
|------|------|------|
| 安全门 / 风险分类 | 本地 | 零信任；规则用户可控 |
| 脱敏管线 | 本地 | 密钥永不离开机器 |
| Agent 循环 / 工具执行 | 本地 | 需 FS/DB 访问 |
| Embedding / RAG | 本地 | 知识库私有 |
| LLM 推理（可委派任务） | 云端（多 provider） | 零风险任务的成本/延迟优化 |
| LLM 推理（敏感任务） | 本地（Ollama） | 隐私保证 |

---

## 6. 混合模式 Top 3 失败风险与缓解

| 风险 | 描述 | 缓解 |
|------|------|------|
| 1. 脱敏绕过/数据外泄 | 脱敏器 bug 泄漏 PII/密钥/本地路径/API 密钥给云端 | 纵深防御：正则 + LLM 分类器 + presidio 三重检查；云端载荷 Pydantic 白名单校验（拒收意外字段）；每次云请求/响应本地哈希审计 + 周检；金丝雀测试（套件注入合成密钥，CI 若在云端 mock 中出现即失败） |
| 2. 云不可用/供应商锁定 | 单云故障 → 可委派任务停滞；成本飙升；API 变更破坏委派 | ≥3 provider 轮询池；所有可委派任务有本地 Ollama 等价实现，云错自动故障转移；按 provider 日预算熔断（超支自动切本地）；`CloudProvider` 协议适配层 |
| 3. 委派结果语义漂移 | 云模型输出与本地模型微妙不同 → 下游决策分叉 | 可委派任务 temperature=0 + 提示词模板版本化；影子模式（本地+云并行跑 100 任务，语义散度 >5%（余弦 <0.95）告警）；前 N 次委派人工确认后才自动接受；黄金输出回归套件，CI 比对 |

---

## 7. 证据索引

| 编号 | 证据 | 位置 |
|------|------|------|
| E1 | `session.dict()` 弃用 API | `src/daip_live/persistence/database.py:39` |
| E2 | embedding_dim=384 硬编码 | `src/daip_live/knowledge/manager.py:34` |
| E3 | ModelError 吞掉伪造成功 | `src/daip_live/p8_debate_system/enhanced_debate_manager.py:582-586` |
| E4 | basic_tools 无外部调用 | `src/daip_live/basic_tools/__init__.py` + `core.py:931` |
| E5 | 2224 测试 / 5250 mock 引用(146 文件) / 零 CI / 红灯测试 | `tests/` 全量 + 无 `.github/` |
| E6 | requires-python 破坏 ruff | `pyproject.toml:11`（L36-37 daip 入口） |
| E7 | 默认 ollama 模型 + MCP 配置 | `config.yaml:8-9,10-29` |
| E8 | CLI 重构未提交 | git status（cli.py/cli_main.py 删除，cli/main.py 包） |
| E9 | 日志零 handler | 全局搜索无 basicConfig/FileHandler（仅 error_handling.py 局部一处） |
| E10 | P1-P8 架构 + TUI 基线 7 测试通过 | `src/daip_live/` 结构；`py -m pytest tests/integration/test_tui_integration.py tests/test_e2e_tui_debate_model_switching.py` → 7 passed |

---

*本计划全部声明基于上述证据与直接代码检视；评分与阶段划分与 Oracle 生产就绪评审（PRODUCTION_READINESS_ASSESSMENT.md）一致。*
