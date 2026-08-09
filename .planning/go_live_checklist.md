# DAIP-LIVE 生产上线检查清单（Go-Live Checklist）

**编制日期**: 2026-08-09
**定位**: 个人生产级本地工具（单用户、本地优先）+ 本地/云端混合（云端为已确认硬需求、暂缓实施）
**依据**: `.planning/real_state_assessment_2026-08-09.md`（全部数字实测）

---

## 1. 门禁终态（全部实测）

| # | 门禁 | 状态 | 证据 |
|---|------|------|------|
| G1 | 全量测试 0F/0E | ✅ | `py -m pytest -q` → 1754P/433S/0F/0E（+12：合并重复类恢复 8 个被吞测试 + 模型检查器 4 个） |
| G2 | ruff = 0（src + tests） | ✅ | `py -m ruff check src/ tests/` → **0（首次真实全量覆盖）**；此前 .gitignore `test_*.py` 无锚定规则使 ruff 跳过全部测试文件，G2 曾为假绿；已修复 + 200+ 文件治理 |
| G3 | mypy = 0 | ⚠️ Backlog | 917 项（1247→917 分级收敛），全为类型注解完善类（抽样确认无运行时 bug）；CI 软门禁，**不作为上线阻塞** |
| G4 | Python 3.9 语法全过 | ✅ | `py -m python scripts/check_py39_syntax.py` → 0（曾 6 处 invalid-syntax） |
| G5 | CI 全绿 | ⚠️ | 已硬化并入库（ci.yml 此前从未跟踪）；仅 mypy 软门禁（记录在案的 Backlog） |
| G6 | knowledge 端到端真实 | ✅ | `knowledge_sources` 13 落盘；`knowledge search "量子计算"` 返回真实结果 |
| G7 | 数据隔离 | ✅ | DB/faiss 移出 git；保护断言曾抓到 p7_gui 违规者并已修复；测试后 git 干净 |
| G8 | 备份可恢复 | ✅ | 演练完成（备份含 406 会话/611 轮）；每日计划任务已注册 |
| G9 | 文档诚实化 | ✅ | 6 份虚高文档加横幅；README badge 删除；AGENTS.md 路径修正 |
| G10 | TUI 冒烟 | ✅ | 启动冒烟 + Textual run_test 交互冒烟（tests/unit/test_tui_smoke.py） |

**上线判定**: G1/G2/G4/G6/G7/G8/G9/G10 全绿 + G3/G5 为记录在案的软门禁 → **达到"可日常依赖"标准**。

---

## 2. 上线前人工确认项（需用户执行）

| # | 项 | 说明 | 操作 |
|---|----|------|------|
| H1 | **DB 数据恢复决策** | ✅ 2026-08-09 已决策：**不恢复，保持当前库**（knowledge_sources 13 条活的；406 会话备份在 zip 可随时手动查阅） | 如需回溯旧会话：`pwsh .planning/scripts/restore.ps1 -Zip backups/daip-20260808-082131.zip`（自动备份当前态 + 校验 + 覆盖） |
| H2 | TUI 完整交互体验 | run_test 冒烟已过，完整人工体验一次 | `py -m daip_live.cli.main run`（Ctrl+Q 退出） |
| H3 | 真实辩论冒烟 | ✅ 2026-08-09 复测通过（修复嵌入模型检查 bug 后重跑：正反论点/Consensus/DebateCompleteEvent 齐全） | `py -m daip_live.cli.main debate start "上线验收" --roles pro_arguer,con_arguer --rounds 1` |
| H4 | 备份任务确认 | ✅ 已注册启用，下次 2026/8/10 02:00；⚠️ Logon Mode = Interactive only（仅登录时运行，注销不备份——单用户本机可接受，注意勿长期注销运行） | `schtasks /query /tn "DAIP-Live Backup" /fo LIST /v` |

---

## 3. 已知限制（诚实声明，不影响上线判定）

| 项 | 状态 | 后续 |
|----|------|------|
| mypy 917 项类型注解 | Backlog（CI 软门禁） | 类型化长期工程，不阻塞上线 |
| CLI 冷启动 ~7.8s | 根因 = litellm import ~9.2s | 方案（入口懒加载）已记录，Backlog |
| `daip knowledge <query>` 裸参数 | Typer 架构限制（未知命令优先报错） | 主入口 `daip knowledge search <query>` |
| wiki CLI 7 处 `:memory:` DB | wiki_index.json 文件系统兜底 | 观察项 |
| Stage 5 混合路由 | 用户确认硬需求、暂缓实施 | Backlog（H1-H6 蓝图在 08-08 报告 §4） |
| 云端 API key | config.yaml 无云端段 | 混合路由实施时补 |
| 模型检查器 bug（已修复） | 曾对嵌入模型 nomic-embed-text 调 generate() 致辩论无法启动 | 2026-08-09 修复：嵌入模型走 embed() 检查 + "does not support" 独立分类；防回归测试 4 个 |
| PermissionInteraction 枚举 bug（已修复） | `use_enum_values=True` 使赋值后 state 变字符串，`to_result().granted`/状态比较恒 False（安全相关） | 2026-08-09 修复：移除 use_enum_values；合并被覆盖吞掉的重复测试类（恢复 8 个测试） |
| .gitignore 无锚定临时脚本规则（已修复） | `test_*.py` 等模式忽略所有层级，13 个 tests/ 正式测试从未入库 + ruff 全跳过（G2 假绿、CI 测试集≠本地） | 2026-08-09 修复：加 `/` 锚定根目录 + 20 个历史文件入库 + 全量 lint 治理 |

---

## 4. 上线后日常运营

1. **每日备份**: 计划任务自动（db + knowledge + config → `backups/daip-<日期>.zip`）；保留策略：定期清理旧 zip（建议 >30 天）。
2. **知识库**: 新增文档到 `knowledge/wiki/` 后运行 `py -m daip_live.cli.main knowledge sync`（增量检测，二次 sync "up to date"）。
3. **数据安全**: `daip_live.db` 不跟踪 git；禁止测试写 root DB（保护断言在 `tests/conftest.py` 会拦截）。
4. **版本管理**: 上线的 `main` 分支 + 备份 zip 双保险；重大变更前 `pwsh .planning/scripts/backup.ps1` 手动备份一次。

---

## 5. 上线验收命令（一键自检）

```powershell
py -m pytest -q --tb=no                        # G1: 1754P/0F/0E
py -m ruff check src/ tests/                   # G2: 0
py -m python scripts/check_py39_syntax.py      # G4: 0 failures
py -m daip_live.cli.main knowledge status      # G6: Indexed 13
py -m daip_live.cli.main knowledge search "量子计算"  # G6: 真实结果
git status --short                             # G7: 干净
pwsh .planning/scripts/backup.ps1 -Restore backups/daip-20260808-082131.zip  # G8: 演练
```
