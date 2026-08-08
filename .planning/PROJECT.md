# DAIP-LIVE

## What This Is

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE System) 是一个本地优先的 AI 智能体工作站，支持多 AI 角色协作、结构化辩论、本地知识管理与 Wiki 协作。单用户环境，核心数据（知识库、配置、会话历史）本地存储于 SQLite 与文件系统，强调隐私、透明与用户可控。

## Core Value

**truth in execution**：系统宣称的状态必须与真实状态一致——测试全绿才算绿，分数以实测为准，不允许文档虚高、调试绕过或静默失败掩盖真实质量。

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ 多模型协作与角色辩论（P8 辩论系统）— phase 0-2
- ✓ 本地知识管理 + 向量检索（P2 知识管理）— phase 3+
- ✓ 现代化 TUI 界面（Textual）— phase 6
- ✓ SPEC 驱动开发流程示范 — 项目定位

### Active

<!-- Current scope. Building toward these. -->

- [ ] **TEST-01**: 全部测试套件（unit/integration/e2e/security）通过，无语法错误、无 stale mock、无旧模型构造
- [ ] **TEST-02**: 生产代码移除调试绕过（`enhanced_debate_manager.py` 的 `is_model_ok = True` 硬编码）
- [ ] **CONF-01**: `config.yaml` 显式声明 `embedding_dimension`，消除隐性依赖
- [ ] **COMP-01**: 代码在 Python 3.9-3.12 全部可解析（修复 6 处 3.12 专属 f-string）
- [ ] **TYPE-01**: mypy 0 错误（补 types-* stubs，解决模块名重复）
- [ ] **LINT-01**: ruff 0 错误（11191 项清零）
- [ ] **CI-01**: CI 全步骤绿：含 e2e、security，无 `continue-on-error` 掩盖
- [ ] **DOC-01**: 生产就绪文档分数与实测一致（拒绝 85/100 虚高）
- [ ] **CFG-01**: pytest 配置统一（pytest.ini 与 pyproject 二选一，markers/testpaths 生效）

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- 重构 TUI 为全新前端框架 — 与上线止血目标无关，Textual 已满足需求
- 新功能开发 — 当前里程碑只做质量修复与上线就绪，不扩功能面
- 云端部署 — 本地优先定位不变

## Context

- main @ `09768c3`（phase-12: Test quality fixes），真实状态测评见 `docs/plans/true_state_assessment.md`（2026-08-07 实测）。
- 实测基线：单元 21F/185P/32E，集成 19F/24P/9E，e2e 1 处语法错误导致整套零运行，安全 4F/15P，ruff 11191 错误，mypy 8 错误/7 文件。
- 历史真实改进存在：Phase 0-2 旧阻塞项已修复（Pydantic v2 迁移、embedding 配置驱动、死代码清理、openapi.json 存在）。
- 本机环境：Python 3.12.0rc3、pytest 8.3.4、pydantic 2.13、ruff 0.12.10（PATH 无 ruff，须 `py -m ruff`）；Ollama localhost:11434 可达。
- CI 环境：ubuntu-latest / Python 3.11 / poetry；poetry.lock 锁定 ruff 0.4.10 / mypy 1.17.1（与本地不一致）。

## Constraints

- **Compatibility**: `requires-python >=3.9,<3.13` — 代码必须在 3.9 下可解析；CI 跑 3.11
- **Tech stack**: Python 3.9+、Poetry、pytest、ruff、mypy、SQLAlchemy、Textual、LiteLLM
- **Testing**: TDD 驱动 — 每个修复先写/改测试（红）→ 实现（绿）→ 验证
- **Quality gate**: 门禁以实测为准（pytest 输出、ruff/mypy 退出码），拒绝"应该能过"的声称
- **Environment**: Windows 本机 + 全局规则（rg 用 `-g "*.py"`、禁止 `task()` 子代理、只用 free models）

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 按真实状态测评（非文档声称）作为实施基线 | 文档 85/100 与实测矛盾，必须以实测为准 | ✓ Good |
| Wave 0-4 分波实施，对应 GSD Phase 1-5 | 先止血（红→绿）再质量（静态清零）再落地（CI/文档） | ✓ Good |
| TUI mock 修复采用方案 A（恢复 `__init__.py` 导出 Container）优先，失败则方案 B | 改动最小、最快恢复 41 个错误 | — Pending |
| pytest 配置统一建议删 pytest.ini 归入 pyproject | 单一配置源，markers/testpaths/strict-markers 生效 | — Pending |

---
*Last updated: 2026-08-07 after GSD project initialization*
