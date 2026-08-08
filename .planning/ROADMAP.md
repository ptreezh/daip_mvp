# Roadmap: DAIP-LIVE 生产上线（质量修复里程碑）

## Overview

将 main@09768c3 从"文档宣称 85/100、代码实际破损"的状态，通过五个阶段（对应 `true_state_assessment.md` 的 Wave 0-4）修复到可交付上线：先止血立骨架（Phase 1），再恢复测试全绿（Phase 2），然后兼容性与类型清零（Phase 3），静态检查清零（Phase 4），最后 CI 与文档落地（Phase 5）。全程 TDD 驱动，门禁以实测为准。

## Phases

- [x] **Phase 1: 止血（Wave 0）** - e2e 语法修复、调试绕过移除、config 补齐
- [ ] **Phase 2: 测试恢复（Wave 1）** - TUI mock、Session 构造、wiki 对齐、安全测试
- [ ] **Phase 3: 兼容与类型（Wave 2）** - 3.12 f-string、mypy stubs、工具链统一
- [ ] **Phase 4: 静态清零（Wave 3）** - ruff 11191 清零
- [ ] **Phase 5: CI 与文档（Wave 4）** - CI 硬化、文档纠正、配置统一

## Phase Details

### Phase 1: 止血（Wave 0）
**Goal**: 先让"红"变"绿"的骨架立起来——e2e 可收集、生产代码诚实、配置显式化
**Depends on**: Nothing (first phase)
**Requirements**: TEST-01, HON-01, HON-02, HON-03
**Success Criteria** (what must be TRUE):
  1. `py -m py_compile tests/e2e/*.py` 全量 0 失败（`test_tui_interaction_e2e.py:316` 逗号→冒号修复生效）
  2. `enhanced_debate_manager.py` 无调试绕过（`is_model_ok = True` 硬编码消失），角色缺失时抛 `ValueError`
  3. `config.yaml` 含 `embedding_dimension` 键；新增/更新单测验证上述行为（TDD 红→绿）
**Plans**: 3 plans

Plans:
- [x] 01-01: e2e 语法修复 + py_compile 全量扫描
- [x] 01-02: 调试绕过移除 + 角色缺失 raise ValueError + 单元测试
- [x] 01-03: config.yaml 补 embedding_dimension + 测试验证

### Phase 2: 测试恢复（Wave 1）
**Goal**: 单元/集成/安全测试全部恢复绿——TUI mock 有效、模型构造同步、wiki 对齐、安全断言修正
**Depends on**: Phase 1
**Requirements**: TEST-02, TEST-03, TEST-04, TEST-05
**Success Criteria** (what must be TRUE):
  1. `py -m pytest tests/unit/` 0 error 0 failed（32 ERROR + 21 FAILED 消除）
  2. `py -m pytest tests/integration/` 0 error 0 failed（9 ERROR + 19 FAILED 消除）
  3. `py -m pytest tests/security/` 0 failed，无 PytestReturnNotNoneWarning
**Plans**: 4 plans

Plans:
- [x] 02-01: TUI Container mock 目标修复（方案 A：恢复 `__init__.py` 导出，失败则方案 B）
- [x] 02-02: Session/DialogueTurn 测试构造同步（3 处 + role→participant_id）
- [ ] 02-03: wiki GREEN/RED 测试与生产校验对齐
- [ ] 02-04: 安全测试 4F 修复 + PytestReturnNotNoneWarning

### Phase 3: 兼容与类型（Wave 2）
**Goal**: 3.9-3.12 语法兼容 + mypy 清零 + 工具链统一
**Depends on**: Phase 2
**Requirements**: TYP-01, TYP-02, TYP-03, TYP-04
**Success Criteria** (what must be TRUE):
  1. 全部 `src/daip_live/` 文件在 3.9 语法语义下 `ast.parse` 0 失败（6 处 f-string 修复生效）
  2. `py -m mypy src/daip_live/` 0 错误（含 types-* stubs 安装后）
  3. CI/本地工具链版本统一（ruff/mypy 版本一致，无复现性漂移）
**Plans**: 4 plans

Plans:
- [ ] 03-01: 3.12 专属 f-string 修复 + ast.parse 静态检查步骤
- [ ] 03-02: mypy types-* stubs 补齐
- [ ] 03-03: context_manager 模块名重复解决
- [ ] 03-04: 工具链版本统一

### Phase 4: 静态清零（Wave 3）
**Goal**: ruff 11191 错误归零，静态检查成为硬门禁
**Depends on**: Phase 3
**Requirements**: STT-01, STT-02
**Success Criteria** (what must be TRUE):
  1. `py -m ruff check src/` 输出 0 errors
  2. `py -m mypy src/daip_live/` 输出 0 errors
  3. 人工处理 F821（未定义名称 25）、E722（bare except 44）等真 bug 候选
**Plans**: 3 plans

Plans:
- [ ] 04-01: ruff --fix 自动修复 4143 项
- [ ] 04-02: 格式化类分批（W293/W291/I001/E501 等）
- [ ] 04-03: 真 bug 候选人工处理（F821/E722/F405/F403/T201）+ 终验

### Phase 5: CI 与文档（Wave 4）
**Goal**: CI 全步骤绿、文档分数真实、pytest 配置统一、生产冒烟
**Depends on**: Phase 4
**Requirements**: REL-01, REL-02, REL-03, REL-04
**Success Criteria** (what must be TRUE):
  1. CI 全步骤绿：含 e2e、security，无 `continue-on-error` 掩盖
  2. `PRODUCTION_READINESS_*.md` 分数与实测一致；README badge 真实
  3. pytest 配置单一来源（markers/testpaths/--strict-markers 生效）
  4. `poetry run daip run` 冒烟走通一次会话（或明确记录阻塞原因）
**Plans**: 4 plans

Plans:
- [ ] 05-01: CI 硬化（e2e + security + 去 continue-on-error）
- [ ] 05-02: 文档分数纠正（PRODUCTION_READINESS_*.md + README）
- [ ] 05-03: pytest 配置统一
- [ ] 05-04: 生产启动冒烟 + 终验门禁（Stage A/B/C）

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. 止血（Wave 0） | 3/3 | Completed | 2026-08-07 |
| 2. 测试恢复（Wave 1） | 2/4 | In progress | - |
| 3. 兼容与类型（Wave 2） | 0/4 | Not started | - |
| 4. 静态清零（Wave 3） | 0/3 | Not started | - |
| 5. CI 与文档（Wave 4） | 0/4 | Not started | - |
