# DAIP-LIVE 自主执行系统 - 使用指南

**创建日期**: 2026-08-07
**状态**: 就绪，等待启动

---

## 🎯 系统概述

这是一个**长时自动运行、无须人工干预**的自动化开发系统，基于以下原则：

- ✅ **Spec 先行**: 所有任务先有规范文档，再执行
- ✅ **TDD 驱动**: 测试先行，红灯 → 绿灯 → 重构
- ✅ **Worktree 隔离**: 每个 Phase 在独立 worktree 中执行
- ✅ **Grill-Down 验证**: 每个任务执行前经过方案验证
- ✅ **原子提交**: 每个修复一个提交，便于回滚
- ✅ **YAGNI/KISS/SOLID**: 不过度设计，保持简单

---

## 📁 已创建的文档

```
.planning/autonomous_plan/
├── README.md                # 本文件 - 使用指南
├── MASTER_PLAN.md           # 主计划 - 阶段划分
├── STATE.md                 # 全局状态跟踪
├── execution_workflow.md    # 执行工作流
├── grill_down_template.md  # Grill-Down 验证模板
├── autonomous_loop.sh      # 自动循环脚本
└── phase_0/
    ├── SPEC.md             # Phase 0 详细规范 ✅
    ├── TASKS.md            # 任务清单 ✅
    └── PROGRESS.md         # 进度跟踪 ✅
```

---

## 🚀 启动方式

### 方式 1: 使用 CronCreate (推荐用于长时运行)

```bash
# 创建每 30 分钟检查一次的循环任务
CronCreate cron="*/30 * * * *" prompt="Execute next task in autonomous plan" recurring=true durable=true

# 或使用 ScheduleWakeup (如果使用 /loop)
ScheduleWakeup delaySeconds=1800 reason="Check autonomous execution progress" prompt="Execute next autonomous task"
```

### 方式 2: 手动执行 Phase 0

```bash
# 1. 创建 worktree
git worktree add ../daip-live-phase-0 -b phase-0

# 2. 进入 worktree
cd ../daip-live-phase-0

# 3. 安装依赖
poetry install

# 4. 执行 P0-1 (SQLAlchemy 兼容性)
# 按照 phase_0/SPEC.md 中的 TDD 步骤执行

# 5. 验证
poetry run pytest tests/unit/persistence/ -v

# 6. 提交
git commit -m "phase-0: SQLAlchemy 2.0 compatibility fix"

# 7. 合并回主分支
cd ../refactdoc
git merge phase-0 --no-ff
```

### 方式 3: 使用 AI Agent 自动执行

向 AI 发送以下指令：

```
请按照 .planning/autonomous_plan/phase_0/SPEC.md 执行 Phase 0。
使用 worktree 隔离，遵循 TDD 流程，每个任务验证后再执行下一个。
```

---

## 📋 执行流程详解

### 1. 准备阶段 (P0-0)

```bash
# 检查环境
git status  # 应该干净
poetry run pytest --collect-only  # 应该收集 2224 测试

# 创建 worktree
git worktree add ../daip-live-phase-0 -b phase-0
cd ../daip-live-phase-0
```

### 2. P0-1: SQLAlchemy 2.0 兼容性

```bash
# 步骤 1: 写测试 (红灯)
# 创建 tests/unit/test_persistence_sqlalchemy_compat.py
# 运行: poetry run pytest tests/unit/test_persistence_sqlalchemy_compat.py -v
# 应该失败

# 步骤 2: 修复代码 (绿灯)
# 修改 src/daip_live/persistence/database.py
# 将 session.dict() 改为 session.model_dump()

# 步骤 3: 验证
poetry run pytest tests/unit/persistence/ -v
```

### 3. P0-2: 动态 embedding 维度

```bash
# 步骤 1: 写测试
# 创建 tests/unit/test_knowledge_embedding_dimension.py

# 步骤 2: 修复代码
# 修改 src/daip_live/knowledge/manager.py
# 添加从配置读取维度的逻辑

# 步骤 3: 更新配置
# 修改 config.yaml 添加 embedding_dimension

# 步骤 4: 验证
poetry run pytest tests/unit/knowledge/ -v
```

### 4. P0-3: 日志基础设施

```bash
# 步骤 1: 写测试
# 创建 tests/unit/test_logging_infrastructure.py

# 步骤 2: 修复代码
# 修改 src/daip_live/container.py
# 添加 setup_logging 函数

# 步骤 3: 更新配置
# 修改 config.yaml 添加 logging 配置

# 步骤 4: 验证
poetry run pytest tests/unit/test_logging_infrastructure.py -v
daip run
cat data/logs/daip_live.log
```

### 5. P0-4: pyproject 配置修复

```bash
# 步骤 1: 修复 pyproject.toml
# 将 requires-python = ">=3.9.7,<3.13"
# 改为 requires-python = ">=3.9"

# 步骤 2: 验证
poetry run ruff check src/
```

### 6. 集成验证与合并

```bash
# 全量验证
poetry run pytest tests/unit/ -v
poetry run mypy src/daip_live/
poetry run ruff check src/

# 提交
git add .
git commit -m "phase-0: foundation stabilization

- SQLAlchemy 2.0 compatibility (model_dump)
- Dynamic embedding dimension
- Logging infrastructure
- pyproject.toml fixes"

# 合并到主分支
cd ../refactdoc
git merge phase-0 --no-ff

# 清理 worktree
git worktree remove ../daip-live-phase-0
```

---

## 📊 进度跟踪

### 当前状态

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    🎯 准备启动 Phase 0                      │
│                                                             │
│              Phase 0: 地基稳定 (Foundation)                  │
│                                                             │
│              ░░░░░░░░░░░░░░░░░░░░░ 0%                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 验收标准

| 指标 | 当前 | 目标 |
|------|------|------|
| 生产就绪评分 | 35/100 | 45/100 |
| persistence 测试 | 有问题 | 全通过 |
| knowledge 测试 | 有问题 | 全通过 |
| 日志系统 | 无 | 有日志文件 |
| mypy 错误 | 有 | 无错误 |

---

## 🔧 故障排除

### 问题 1: Worktree 创建失败

```bash
# 检查是否有未提交的变更
git status

# 清理旧的 worktree
git worktree list
git worktree remove <name>
```

### 问题 2: 测试失败

```bash
# 查看详细错误
poetry run pytest <test_file> -v -s

# 检查依赖
poetry show

# 重新安装
poetry install
```

### 问题 3: 日志文件未创建

```bash
# 检查目录权限
ls -la data/

# 手动创建
mkdir -p data/logs
```

---

## 📞 支持

如遇问题，查看以下文档：

- `.planning/autonomous_plan/MASTER_PLAN.md` - 主计划
- `.planning/autonomous_plan/phase_0/SPEC.md` - Phase 0 规范
- `.planning/autonomous_plan/phase_0/TASKS.md` - 任务清单
- `.planning/autonomous_plan/phase_0/PROGRESS.md` - 进度跟踪

---

*自主执行系统就绪。等待启动命令。*
