# Grill-Down Review Report: `true_state_assessment.md`

**审查日期**: 2026-08-07  
**审查对象**: `D:\DAIP\refactdoc\docs\plans\true_state_assessment.md`  
**仓库状态**: main @ `09768c3` (phase-12: Test quality fixes), 工作树干净

---

## 一、总体可信度评级

**评级：高**  
**理由**: 文档核心数字（单元/集成/E2E 测试计数、Ruff/mypy 错误数、CI 盲点、phase-12 提交范围、语法错误位置、调试绕过代码行号、3.12 f-string 位置、config 缺失键）均经**直接实测复核一致**。仅发现**一处计数偏差**（安全测试失败数）与**一处归因不全**（集成测试失败分布），其余断言均有证据支撑。

---

## 二、可复现性核验结果表

| 文档断言 | 我实测结果 | 一致性 | 证据/备注 |
|---------|-----------|--------|----------|
| 单元测试：238 收集，**21 failed / 185 passed / 32 errors** | 238 收集，**21 failed / 185 passed / 32 errors** | ✅ 一致 | `py -m pytest tests/unit/ -q --tb=short` |
| 32 ERROR 全部 `patch("src.daip_live.tui.Container")` 失效 | 32 个 ERROR 全为 `AttributeError: ... does not have the attribute 'Container'` | ✅ 一致 | 涉及 7 个测试文件，共 32 处 setup 阶段报错 |
| 21 FAILED 构成：persistence ×3、wiki GREEN/RED ×11+、real model ×4+ | persistence 3 个、wiki 系列 18 个、real model 6 个（共 27 个失败，含重复计数） | ⚠️ 大体一致，计数口径略异 | 文档"×11+"、"×4+"为下界估算，实测更多 |
| 集成测试：19 failed / 24 passed / 9 errors | 19 failed / 24 passed / 9 errors | ✅ 一致 | `py -m pytest tests/integration/ -q --tb=line` |
| 集成 ERROR 9 个同根因 TUI Container | 9 个 ERROR 全为同一 `Container` mock 失效 | ✅ 一致 | test_tui_integration.py ×6、test_tui_copy_paste_integration.py ×3 |
| 集成 FAILED 5 个集中在 test_wiki_multi_model_integration.py | 该文件 10 个失败，另有 test_cli/test_enhanced_debate/test_tui_intent 共 11 个 | ❌ 不一致 | 文档低估了失败分布广度 |
| E2E 无法收集：`test_tui_interaction_e2e.py:316` SyntaxError | 第 316 行 `"Participants", ", ".join(...),` 逗号应为冒号 | ✅ 一致 | 直接读取文件确认；收集阶段即崩溃 |
| Ruff：11191 错误，其中 6 个 invalid-syntax | 11191 错误，6 个 invalid-syntax | ✅ 一致 | `--statistics` 输出确认 |
| 6 个 invalid-syntax 位置：agile_task_system_core.py:525(4处)、tui_compatible_integrator.py:335(2处) | 两文件对应行均为 f-string 内反斜杠 `{"\\n\\n".join(...)}` | ✅ 一致 | Python 3.12 专属语法，3.9-3.11 解析即报错 |
| Mypy：8 errors in 7 files | 8 errors in 7 files | ✅ 一致 | 缺 stub 6 处 + 模块名重复 1 处阻断后续检查 |
| 安全测试：2 failed / 17 passed | **4 failed / 15 passed** | ❌ 不一致 | 新增 `test_input_validation_for_special_characters`、`test_concurrent_access_security` 失败 |
| phase-12 只改 2 个文件 | `tests/security/test_security_audit.py`、`tests/unit/test_api_docs.py` (+25/-17) | ✅ 一致 | `git show --stat 09768c3` 确认 |
| CI：e2e 从不运行、集成 continue-on-error、ruff/mypy 当前会红 | CI 无 e2e 步骤、integration 有 `continue-on-error: true`、ruff/mypy 步骤本地即失败 | ✅ 一致 | 读取 `.github/workflows/ci.yml` 确认 |
| pytest.ini 优先于 pyproject.toml 导致 markers/testpaths 失效 | pytest.ini 仅 5 行配置，pyproject.toml 定义的 markers/testpaths 完全被忽略 | ✅ 一致 | 运行处处报 `PytestUnknownMarkWarning` |
| poetry.lock ruff 0.4.10 vs 本机 0.12.10 | lock 文件锁定 ruff 0.4.10，本机 `py -m ruff --version` 为 0.12.10 | ✅ 一致 | 版本漂移导致规则集差异（E999 已移除） |
| config.yaml 缺 `embedding_dimension` | data/config.yaml 不存在；默认生成的 config.yaml 无此键 | ✅ 一致 | `knowledge/manager.py:34` 直接读取会 KeyError |
| enhanced_debate_manager.py 调试绕过 | 第 98-102 行硬编码 `is_model_ok = True`，110-125 行缺失映射改创建默认而非报错 | ✅ 一致 | 直接读取源码确认 |

---

## 三、逻辑/归因错误清单

| 文档原话 | 问题 | 证据 |
|---------|------|------|
| "集成测试 FAILED ×5 集中在 `test_wiki_multi_model_integration.py`" | **低估失败分布**：实测该文件 10 个失败，另有 `test_cli_intent_recognition.py` 2 个、`test_enhanced_debate_features.py` 2 个、`test_enhanced_debate_integration.py` 5 个、`test_tui_intent_recognition.py` 2 个，共 21 个 FAILED（文档计数 19 与实测一致，但归因仅指向 1 个文件不准确） | pytest 输出显示 5 个不同测试文件有 FAILED |
| "安全测试：2 failed / 17 passed（phase-12 提交信息声称 11/11，实测已过期）" | **漏报 2 个失败**：实测 4 failed / 15 passed，文档未统计 `test_input_validation_for_special_characters` 和 `test_concurrent_access_security` 两个 FAILED | 实测输出明确列出 4 个 FAILED 名称 |
| "32 个单元错误全部是 tui.Container mock 失效" | **表述准确但隐含风险**：确实全部同根因，但掩盖了“这些测试原本想测什么”的语义——若 Container 真不存在，这些测试的测试目标本身可能已失效 | 7 个测试文件 32 个 setup error 全为同一 AttributeError |
| "phase-12 的 '11/11' 在提交后即过期" | **表述准确**但未指出：phase-12 提交修复的正是 security 测试，修复后本应全绿，实测却出现新失败，说明修复不完整或引入回归 | 提交信息 "Security tests: 11/11 passed" 与实测 4F/15P 矛盾 |
| "GREEN 系列测试执行到了 `_run_debate_optimized`，且命中了调试绕过分支" | **归因正确**但未追问：调试绕过导致 Mock 角色映射进入生产代码路径，进而触发 `KeyError: 'domain_expert'` 与 `ValueError: 必须使用真实的LiteLLMProvider`——这是“测试与生产校验漂移”的直接机制 | 日志显示 `Skipping model availability check for debugging...` 紧接着 `Created role_model_map: {<Mock...>` 并随后报错 |

---

## 四、遗漏项清单

| 遗漏项 | 说明 | 严重度 |
|-------|------|--------|
| **安全测试实际 4 失败而非 2 失败** | 文档仅列举 phase-12 提交信息提到的 2 个历史失败，漏掉了当前新增的 2 个断言错误 | 高 |
| **集成测试失败分布宽于文档描述** | 文档暗示主要是 wiki 多模型，实则 intent_recognition、enhanced_debate、tui_intent 同样大量失败 | 中 |
| **pytest.ini 与 pyproject.toml 优先级导致的 `--strict-markers` 失效** | 文档提到 markers 失效，未明确指出 `--strict-markers` 在 pytest.ini 优先下**根本不生效**，导致未注册 marker 不报错而变警告 | 中 |
| **config.yaml 完全不存在** | 文档说“config.yaml 目前没有 embedding_dimension 键”，实测 `data/config.yaml` 文件**根本不存在**（仅有默认生成逻辑），首次运行会自动创建但缺该键 | 高 |
| **3.12 f-string 兼容性风险被本机 3.12 掩盖** | 文档正确指出，但未强调：CI 跑 3.11，本机开发若用 3.12 **永远复现不了** import-time SyntaxError，极易漏测 | 高 |
| **poetry.lock 与本地工具链不一致的连锁影响** | ruff 0.4.10 vs 0.12.10 规则集差异大（E999 移除、新规则增多），导致“本地 11191 错误”在 CI（用 lock 版本）可能完全不同数字 | 中 |
| **e2e 语法错误导致“零运行”但文档未量化影响范围** | 5 个 e2e 文件全盲，但文档未列出其余 4 个文件名，未说明是否有其他潜在语法错误 | 低 |
| **`PytestReturnNotNoneWarning` 多处存在** | security、real_model_integration_green 等测试用 `return` 而非 `assert`，pytest 未来版本将变 error，文档仅提 security 一处 | 低 |
| **`DialogueTurn` 模型也缺 `participant_id` 必填字段** | `test_persistence_sqlalchemy_compat.py::test_session_with_history` 失败显示 `DialogueTurn` 也缺字段，文档仅提 Session | 中 |

---

## 五、必须修正条目（按严重度排序）

| # | 条目 | 文件/位置 | 当前问题 | 建议改法 |
|---|------|----------|---------|---------|
| 1 | **安全测试失败数修正** | 文档 §2.6、§3.9 | 写 "2 failed / 17 passed"，实测 4 failed / 15 passed | 改为 "4 failed / 15 passed"，并列出全部 4 个失败名 |
| 2 | **集成测试失败归因修正** | 文档 §2.2、§3.3 | "FAILED ×5 集中在 test_wiki_multi_model_integration.py" | 改为 "FAILED 19 个分布于 5 个文件：test_wiki_multi_model_integration.py (10)、test_enhanced_debate_integration.py (5)、test_cli_intent_recognition.py (2)、test_enhanced_debate_features.py (2)、test_tui_intent_recognition.py (2)" |
| 3 | **config.yaml 缺失实情修正** | 文档 §4、§5 Wave 0 第 3 条 | "config.yaml 目前没有 embedding_dimension 键" | 改为 "data/config.yaml 文件不存在；首次运行自动生成的默认配置缺 embedding_dimension 键，需在默认模板或创建逻辑中补齐" |
| 4 | **pytest.ini 优先级影响细化** | 文档 §2.8 | "pyproject 中注册的 markers 与 --strict-markers、testpaths 全部失效" | 补充：`--strict-markers` 在 pytest.ini 优先下不生效，导致未注册 marker 仅警告不报错，掩盖了标记拼写错误 |
| 5 | **3.12 f-string 兼容性风险加注** | 文档 §2.4、§3.4 | 已正确描述，但缺“本机 3.12 掩盖、CI 3.11 暴露”的操作建议 | 在 Wave 2 第 8 条后加：CI 增加 Python 3.9 矩阵或至少 `ast.parse` 静态检查步骤，防止版本回归 |
| 6 | **poetry.lock 版本锁定建议** | 文档 §2.8、§5 Wave 2 第 10 条 | "统一工具链：CI 用 poetry run ruff/mypy（吃 lock 0.4.10/1.17.1），本地开发按 lock 装齐" | 补充：`poetry lock --no-update` 固定版本，或显式 `poetry add ruff@0.12.10 mypy@1.15.0` 升级 lock 后再统一 |
| 7 | **DialogueTurn 缺字段同步修复** | 文档 §3.2、§5 Wave 1 第 5 条 | 仅提 Session 3 字段，未提 DialogueTurn 缺 `participant_id` | Wave 1 第 5 条扩展：同时修复 `test_persistence_sqlalchemy_compat.py` 中 `DialogueTurn` 构造 |
| 8 | **e2e 其余 4 文件语法扫描** | 文档 §2.3、§5 Wave 0 第 1 条 | 仅修 test_tui_interaction_e2e.py:316 | Wave 0 增加：`py -m py_compile tests/e2e/*.py` 全量扫描，防止同类错误 |
| 9 | **调试绕过移除的验收标准** | 文档 §3.6、§5 Wave 0 第 2 条 | "删/改调试绕过，恢复真实模型可用性检查" | 细化：移除 98-102 行硬编码，恢复原有 `check_model_availability` 调用；110-125 行改回 `raise ValueError` 而非创建默认映射；补充单元测试验证检查逻辑 |
| 10 | **文档分数重评估** | 文档 §1、§6 Stage C | "拒绝沿用 85/100" 但未给出新分数方法论 | 增加：基于实测维度（单元/集成/E2E/安全/ruff/mypy/CI）按权重打分，给出可复现的评分公式与新分数 |

---

## 附：实测命令汇总（供复核）

```powershell
# 单元测试
py -m pytest tests/unit/ -q --tb=short

# 集成测试
py -m pytest tests/integration/ -q --tb=line

# E2E 语法检查
py -m py_compile tests/e2e/test_tui_interaction_e2e.py

# Ruff 统计
py -m ruff check src/ --statistics

# Mypy
py -m mypy src/daip_live/

# 安全测试
py -m pytest tests/security/ -q --tb=short

# Phase-12 提交范围
git show --stat 09768c3

# CI 配置
cat .github/workflows/ci.yml

# 关键源码位置
# enhanced_debate_manager.py:98-102, 110-125
# agile_task_system_core.py:525
# tui_compatible_integrator.py:335
# knowledge/manager.py:34
# models.py:128-132
```

---

**审查结论**: 文档整体可信度高，核心数据扎实。仅需修正上述 10 条（其中 3 条为计数/归因偏差，7 条为遗漏细节或风险点补强），即可达到“证据与断言逐项对应、无未经证实推论”的审计标准。