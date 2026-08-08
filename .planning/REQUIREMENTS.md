# Requirements: DAIP-LIVE 生产上线（质量修复里程碑）

**Defined:** 2026-08-07
**Core Value:** truth in execution——系统宣称的状态必须与真实状态一致，测试全绿才算绿，分数以实测为准

## v1 Requirements

需求来源：`docs/plans/true_state_assessment.md` §5（Wave 0-4）与 §6（Stage A/B/C 门禁），每条需求映射到 GSD Phase 1-5。

### 测试完整性（TEST）

- [ ] **TEST-01**: 全部测试套件（unit/integration/e2e/security）收集并运行，0 语法错误、0 收集错误
- [ ] **TEST-02**: TUI 测试的 Container mock 目标有效（单元 32 ERROR + 集成 9 ERROR 消除）
- [ ] **TEST-03**: `test_persistence_sqlalchemy_compat.py` 按新 Session 必填字段构造（3 处），`test_session_with_history` 用 `participant_id=`（非 `role=`）
- [ ] **TEST-04**: wiki 多模型 GREEN/RED 测试与生产校验对齐（单元 11F + 集成 8F 消除）
- [ ] **TEST-05**: 安全测试 4 个 FAILED 修复，`test_security_audit.py` 的 `return` 改 `assert`（PytestReturnNotNoneWarning 消除）

### 生产代码诚实性（HON）

- [ ] **HON-01**: `enhanced_debate_manager.py` 调试绕过（`is_model_ok = True` 硬编码）移除，恢复真实模型可用性检查
- [ ] **HON-02**: 缺失角色映射时 `raise ValueError`（非"创建默认映射"），并有单元测试覆盖检查逻辑
- [ ] **HON-03**: `config.yaml` 显式声明 `embedding_dimension`，与 `knowledge/manager.py:34` 读取对齐

### 兼容性与类型（TYP）

- [ ] **TYP-01**: 6 处 3.12 专属 f-string 改为 3.9 兼容写法（2 个文件）
- [ ] **TYP-02**: 增加 3.9 语法兼容静态检查（`ast.parse` 或 CI 3.9 矩阵），防版本回归
- [ ] **TYP-03**: mypy 0 错误（补 types-PyYAML/types-requests/types-aiofiles/types-markdown，解决 context_manager 模块名重复）
- [ ] **TYP-04**: 工具链统一（CI 用 `poetry run ruff/mypy`；`poetry lock --no-update` 或升级 lock，消除复现性漂移）

### 静态质量（STT）

- [ ] **STT-01**: ruff 0 错误（11191 → 0），先 `--fix` 自动项再分批人工处理 E722/F821/F405/F403/T201/E501
- [ ] **STT-02**: 收尾门槛：`py -m ruff check src/` 0 错误 + `py -m mypy src/daip_live/` 0 错误

### CI 与文档（REL）

- [ ] **REL-01**: CI 增加 `pytest tests/e2e/` 与 `pytest tests/security/`；集成测试去掉 `continue-on-error`
- [ ] **REL-02**: `PRODUCTION_READINESS_*.md` 分数改为实测值；README badge 与真实状态一致
- [ ] **REL-03**: pytest 配置统一（删 pytest.ini 归入 pyproject，markers/testpaths/--strict-markers 生效）
- [ ] **REL-04**: 生产启动冒烟 `poetry run daip run` 走通一次会话（本机 Ollama 条件具备）

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

- **V2-01**: 全量 ruff `--unsafe-fixes` 人工复核（3319 hidden fixes）
- **V2-02**: 真实模型集成测试接入 CI（需外部 Ollama 服务）
- **V2-03**: Python 3.9-3.12 全版本矩阵 CI

## Out of Scope

| Feature | Reason |
|---------|--------|
| 新功能开发 | 本里程碑只做质量修复与上线就绪 |
| TUI 前端重构 | Textual 已满足需求，与止血目标无关 |
| 云端部署 | 本地优先定位不变 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TEST-01 | Phase 1 | Pending |
| HON-01 | Phase 1 | Pending |
| HON-02 | Phase 1 | Pending |
| HON-03 | Phase 1 | Pending |
| TEST-02 | Phase 2 | Pending |
| TEST-03 | Phase 2 | Pending |
| TEST-04 | Phase 2 | Pending |
| TEST-05 | Phase 2 | Pending |
| TYP-01 | Phase 3 | Pending |
| TYP-02 | Phase 3 | Pending |
| TYP-03 | Phase 3 | Pending |
| TYP-04 | Phase 3 | Pending |
| STT-01 | Phase 4 | Pending |
| STT-02 | Phase 4 | Pending |
| REL-01 | Phase 5 | Pending |
| REL-02 | Phase 5 | Pending |
| REL-03 | Phase 5 | Pending |
| REL-04 | Stage C 验收 | Pending |

**Coverage:**
- v1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-07*
*Last updated: 2026-08-07 after GSD project initialization*
