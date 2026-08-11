# DAIP-LIVE 生产上线检查清单（Go-Live Checklist）

**编制日期**: 2026-08-09
**定位**: 个人生产级本地工具（单用户、本地优先）+ 本地/云端混合（云端为已确认硬需求、暂缓实施）
**依据**: `.planning/real_state_assessment_2026-08-09.md`（全部数字实测）

---

## 1. 门禁终态（全部实测）

| # | 门禁 | 状态 | 证据 |
|---|------|------|------|
| G1 | 全量测试 0F/0E | ✅ | `py -m pytest -q` → 1774P/433S/0F/0E（本地与 CI 一致；+6：hybrid pipeline v3） |
| G2 | ruff = 0（src + tests） | ✅ | `py -m ruff check src/ tests/` → **0（首次真实全量覆盖）**；此前 .gitignore `test_*.py` 无锚定规则使 ruff 跳过全部测试文件，G2 曾为假绿；已修复 + 200+ 文件治理 |
| G3 | mypy = 0 | ⚠️ Backlog | 917 项（1247→917 分级收敛），全为类型注解完善类（抽样确认无运行时 bug）；CI 软门禁，**不作为上线阻塞** |
| G4 | Python 3.9 语法全过 | ✅ | `py -m python scripts/check_py39_syntax.py` → 0（曾 6 处 invalid-syntax） |
| G5 | CI 全绿 | ✅ | **2026-08-09 首次真实跑绿**（run 31326913217，16 步全 success）：ruff format+check（src+tests）、py39、mypy 软门禁、Ollama 安装+模型拉取、全量测试 1757P/433S/0F/0E。**2026-08-10 再次全绿**（run 31345770906，1766P/433S/0F/0E，含 role/doc/model/wiki/multimodel 修复） |
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
| CLI 冷启动（已优化） | 根因 = litellm import ~9-14s | 2026-08-10 完成：provider/delegation_pipeline 函数级懒加载 → import 9.45s→0.39s / 6.73s→0.31s；`knowledge status` 21s→1.94s；1774P 无回归 |
| `daip knowledge <query>` 裸参数（已收敛） | Typer 架构限制（未知命令优先报错，callback 的 ctx.args 从不触发） | 2026-08-10 删除死 callback：无参数默认 sync；搜索用显式 `knowledge search/auto <query>`；docstring 记录限制 |
| wiki CLI `:memory:` DB（已清理） | 8 处 `DatabaseManager(":memory:")` 为死代码（构造后丢弃；WikiManager 实际文件系统持久化 .md + .wiki_index.json） | 2026-08-10 删除 8 处死代码；端到端验证页面真实落盘 |
| Stage 5 混合路由 | ✅ 最小闭环已实施（2026-08-10） | **核心原则（用户）**：全局上下文永不发云端；任务本地模型（Ollama）分解为 >=3 自包含子任务；子任务级分发不同云端模型；无 key/失败/高风险回退本地。feature flag `DAIP_HYBRID_ENABLED`（默认关）。**未做**：人工确认流、规则外置 config、云端 provider 真实接入（需 API key） |
| 云端 API key | config.yaml 无云端段 | 混合路由实施时补 |
| 模型检查器 bug（已修复） | 曾对嵌入模型 nomic-embed-text 调 generate() 致辩论无法启动 | 2026-08-09 修复：嵌入模型走 embed() 检查 + "does not support" 独立分类；防回归测试 4 个 |
| PermissionInteraction 枚举 bug（已修复） | `use_enum_values=True` 使赋值后 state 变字符串，`to_result().granted`/状态比较恒 False（安全相关） | 2026-08-09 修复：移除 use_enum_values；合并被覆盖吞掉的重复测试类（恢复 8 个测试） |
| .gitignore 无锚定临时脚本规则（已修复） | `test_*.py` 等模式忽略所有层级，13 个 tests/ 正式测试从未入库 + ruff 全跳过（G2 假绿、CI 测试集≠本地） | 2026-08-09 修复：加 `/` 锚定根目录 + 20 个历史文件入库 + 全量 lint 治理 |
| role create/delete（已修复） | stub 打印成功但不写/删文件（假功能） | 2026-08-10 修复：RoleManager 真实 yaml 持久化 + get_role_by_name 不再造默认角色 |
| doc search/download（已修复） | CLI 用依赖已删 arxiv 库的版本，恒不可用 | 2026-08-10 修复：切到完整版 + arxiv API(https) + 修重复方法遮蔽/atom:id/版本号 |
| model list/status/info（已修复） | ModelManager 全空 stub | 2026-08-10 修复：连 Ollama /api/tags 真实解析 |
| wiki 全命令目录错位（已修复） | 读错 config key（directory vs pages_directory）→ 页面写到 root wiki/ | 2026-08-10 修复：_get_wiki_dir 兼容两 key + 迁移 12 个用户页面 |
| debate multimodel（已修复） | 缺 session_id 致 pydantic 报错 | 2026-08-10 修复：补 timestamp session_id |
| TUI 论文搜索/下载（已修复） | 用 basic_tools.core 依赖已删 arxiv 库 → 恒降级"模拟" | 2026-08-10 修复：改用 doc.paper_downloader 真实 API |

## 3b. 仍未实现清单（诚实盘点，2026-08-10）

| 项 | 性质 | 说明 |
|----|------|------|
| **Stage 5 混合路由（云端）** | ✅ 最小闭环已实施（2026-08-10，见上表） | 本地分解+子任务分发+全局上下文隔离已完成；真实云端接入需 API key |
| **pubmed/web 论文来源** | doc 命令明确提示"暂不支持" | 仅 arxiv 可用；pubmed/web 需另接 API（当前诚实降级提示，非假成功） |
| **mypy 917 项类型注解** | Backlog | CI 软门禁，非运行时 bug |
| **CLI 冷启动（已优化）** | ✅ 2026-08-10 完成 | provider/delegation_pipeline 懒加载；knowledge status 21s→1.94s |
| **turn_in_round 硬编码 1** | ✅ 已修复 | history_tracker 轮内序号递增（见 35dad6b） |
| **wiki CLI `:memory:` DB（已清理）** | ✅ 2026-08-10 完成 | 8 处死代码删除；文件系统持久化端到端验证 |
| **TUI `/sync`（Claude Skills）与 `/compact`** | TUI 内部命令为模拟 | 仅提示"同步/压缩完成"不做实际工作；非 CLI 核心 |
| **433 skip 测试** | 绝大多数是旧 spec | TDD 红阶段/旧 TUI API spec（测已删除代码），skip 正确；无真实功能缺口 |
| **multi_agent_collab 模拟搜索** | 死代码 | 模块未被 CLI 引用（仅旧 TUI import 痕迹），内部 _simulate 不影响交付 |
| **`daip knowledge <query>` 裸参数（已收敛）** | ✅ 2026-08-10 | 死 callback 删除；用 `knowledge search/auto <query>` |
| **H2 完整 TUI 人工体验** | 待用户 | 自动化冒烟已过 |

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
