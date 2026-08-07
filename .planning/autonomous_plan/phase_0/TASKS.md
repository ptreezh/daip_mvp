# Phase 0 任务清单

**最后更新**: 2026-08-07
**状态**: 待执行

---

## 📋 任务列表

### P0-0: 准备阶段

| ID | 任务 | 命令 | 状态 |
|----|------|------|------|
| P0-0.1 | 创建 phase-0 worktree | `git worktree add ../daip-live-phase-0 -b phase-0` | ⏳ |
| P0-0.2 | 切换到 worktree | `cd ../daip-live-phase-0` | ⏳ |
| P0-0.3 | 安装依赖 | `poetry install` | ⏳ |
| P0-0.4 | 验证基线 | `poetry run pytest --collect-only` | ⏳ |

### P0-1: SQLAlchemy 2.0 兼容性

| ID | 任务 | 文件 | 状态 | 退出标准 |
|----|------|------|------|----------|
| P0-1.1 | 写兼容性测试 | `tests/unit/test_persistence_sqlalchemy_compat.py` | ⏳ | 红灯 (测试失败) |
| P0-1.2 | 修复 database.py | `src/daip_live/persistence/database.py` | ⏳ | 绿灯 (测试通过) |
| P0-1.3 | 重构改善 | `src/daip_live/persistence/database.py` | ⏳ | 代码整洁 |
| P0-1.4 | 验证 | `poetry run pytest tests/unit/persistence/ -v` | ⏳ | 全通过 |

### P0-2: 动态 embedding 维度

| ID | 任务 | 文件 | 状态 | 退出标准 |
|----|------|------|------|----------|
| P0-2.1 | 写维度测试 | `tests/unit/test_knowledge_embedding_dimension.py` | ⏳ | 红灯 |
| P0-2.2 | 修复 manager.py | `src/daip_live/knowledge/manager.py` | ⏳ | 绿灯 |
| P0-2.3 | 更新 config.yaml | `config.yaml` | ⏳ | 配置正确 |
| P0-2.4 | 验证 | `poetry run pytest tests/unit/knowledge/ -v` | ⏳ | 全通过 |

### P0-3: 日志基础设施

| ID | 任务 | 文件 | 状态 | 退出标准 |
|----|------|------|------|----------|
| P0-3.1 | 写日志测试 | `tests/unit/test_logging_infrastructure.py` | ⏳ | 红灯 |
| P0-3.2 | 修复 container.py | `src/daip_live/container.py` | ⏳ | 绿灯 |
| P0-3.3 | 更新 config.yaml | `config.yaml` | ⏳ | 配置正确 |
| P0-3.4 | 验证 | `daip run && cat data/logs/daip_live.log` | ⏳ | 有日志 |

### P0-4: pyproject 配置修复

| ID | 任务 | 文件 | 状态 | 退出标准 |
|----|------|------|------|----------|
| P0-4.1 | 修复 requires-python | `pyproject.toml` | ⏳ | ruff 可解析 |
| P0-4.2 | 验证 | `poetry run ruff check src/` | ⏳ | 无解析错误 |

### P0-5: 集成验证与合并

| ID | 任务 | 命令 | 状态 | 退出标准 |
|----|------|------|------|----------|
| P0-5.1 | 全量单元测试 | `poetry run pytest tests/unit/ -v` | ⏳ | 全通过 |
| P0-5.2 | 类型检查 | `poetry run mypy src/daip_live/` | ⏳ | 无错误 |
| P0-5.3 | Lint 检查 | `poetry run ruff check src/` | ⏳ | 无警告 |
| P0-5.4 | 提交变更 | `git commit -m "phase-0: ..."` | ⏳ | 提交成功 |
| P0-5.5 | 合并到主分支 | `git merge phase-0 --no-ff` | ⏳ | 合并成功 |

---

## 🔧 执行顺序 (依赖图)

```
P0-0.1 ──┐
P0-0.2 ──┤
P0-0.3 ──┤──> P0-1.1 ─> P0-1.2 ─> P0-1.3 ─> P0-1.4 ─┐
P0-0.4 ──┘                                              │
                                                         ├──> P0-5.1 ─> ...
P0-2.1 ─> P0-2.2 ─> P0-2.3 ─> P0-2.4 ───────────────────┤
                                                         │
P0-3.1 ─> P0-3.2 ─> P0-3.3 ─> P0-3.4 ───────────────────┤
                                                         │
P0-4.1 ─> P0-4.2 ────────────────────────────────────────┘
```

---

## 📊 进度统计

```
总任务数: 26
已完成: 0
进行中: 0
待执行: 26
完成率: 0%
```

---

## 🚨 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| SQLAlchemy 版本不兼容 | P0-1 失败 | 使用 model_dump() 适配 |
| embedding 模型未知 | P0-2 失败 | 提供默认维度映射 |
| 日志目录权限问题 | P0-3 失败 | mkdir -p 自动创建 |
| ruff 解析失败 | P0-4 失败 | 使用标准版本语法 |

---

*任务清单完成。等待执行启动。*
