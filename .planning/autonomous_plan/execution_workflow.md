# DAIP-LIVE 自主执行工作流

**目标**: 长时自动运行，无须人工干预
**机制**: GOSkill + Worktree + TDD + Grill-Down
**文档先行**: SPEC 先落地，再执行

---

## 🎯 启动方式

### 方式 1: 使用 GOSkill (推荐)

```bash
# 启动自主循环，持续运行直到目标达成
/goskill autonomous-daip-run
```

### 方式 2: 使用 Loop

```bash
# 每 30 分钟检查一次进度
/loop 30m /autonomous-daip-status

# 或使用 cron
CronCreate cron="*/30 * * * *" prompt="/autonomous-daip-status" recurring=true
```

---

## 📋 执行清单

### 启动前检查

- [ ] 主分支干净 (无未提交变更)
- [ ] pytest 基线测试通过 (2224 收集)
- [ ] TUI 基线测试通过 (7/7)
- [ ] 磁盘空间充足 (~500MB for worktrees)
- [ ] 所有 SPEC.md 文件已创建
- [ ] Grill-Down 验证已通过

### 执行流程

```
┌─────────────────────────────────────────────────────────────┐
│                    自主执行流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 读取当前 Phase (STATE.md)                                │
│     ↓                                                       │
│  2. 读取 Phase SPEC.md                                       │
│     ↓                                                       │
│  3. Grill-Down 验证 (如果未验证)                             │
│     ↓                                                       │
│  4. 创建 worktree                                            │
│     ↓                                                       │
│  5. TDD 执行 (红灯 → 绿灯)                                   │
│     ↓                                                       │
│  6. 验证 (pytest + mypy + ruff)                             │
│     ↓                                                       │
│  7. 提交到 worktree                                          │
│     ↓                                                       │
│  8. 合并到主分支                                             │
│     ↓                                                       │
│  9. 更新进度 (PROGRESS.md)                                   │
│     ↓                                                       │
│  10. 回到步骤 1 (进入下一个 Phase)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
.planning/autonomous_plan/
├── MASTER_PLAN.md           # 主计划
├── STATE.md                # 全局状态
├── grill_down_template.md  # Grill-Down 模板
├── autonomous_loop.sh      # 循环脚本
├── phase_0/
│   ├── SPEC.md             # Phase 0 规范
│   ├── TASKS.md            # 任务清单
│   └── PROGRESS.md         # 进度跟踪
├── phase_1/
│   ├── SPEC.md
│   ├── TASKS.md
│   └── PROGRESS.md
├── phase_2/
│   ├── SPEC.md
│   ├── TASKS.md
│   └── PROGRESS.md
├── phase_3/
│   ├── SPEC.md
│   ├── TASKS.md
│   └── PROGRESS.md
├── phase_4/
│   ├── SPEC.md
│   ├── TASKS.md
│   └── PROGRESS.md
└── phase_5/
    ├── SPEC.md
    ├── TASKS.md
    └── PROGRESS.md
```

---

## 🔧 Phase 执行顺序

```
Phase 0 (地基稳定) ──> Phase 1 (辩论真实) ──> Phase 2 (死代码清除)
     ──> Phase 3 (测试康复) ──> Phase 4 (混合委派) ──> Phase 5 (可观测性)
```

---

## 📊 验收标准

### Phase 0 完成标准

- [ ] `poetry run pytest tests/unit/persistence/ -v` 全通过
- [ ] `poetry run mypy src/daip_live/persistence` 无错误
- [ ] `poetry run ruff check src/` 无警告
- [ ] `daip run` 产生日志文件
- [ ] 生产就绪评分 ≥ 45/100

### 最终完成标准

- [ ] 所有 Phase 完成
- [ ] 生产就绪评分 ≥ 90/100
- [ ] 所有测试通过
- [ ] CI/CD 运行正常
- [ ] 日志完整可追踪

---

## 🚨 中断与恢复

### 中断条件

- pytest 失败超过 3 次
- mypy 错误无法自动修复
- worktree 合并冲突
- 磁盘空间不足 < 100MB
- 网络连接超时

### 恢复流程

1. 检查 `.planning/autonomous_plan/STATE.md`
2. 读取失败 Phase 的 `PROGRESS.md`
3. 定位失败任务
4. 清理 worktree (如需要)
5. 重新执行失败任务

---

## 📝 日志

所有执行日志写入 `data/logs/autonomous_loop.log`，包括：

- 时间戳
- 执行的 Phase
- 任务状态
- 验证结果
- 错误信息

---

*自主执行工作流定义完成。*
