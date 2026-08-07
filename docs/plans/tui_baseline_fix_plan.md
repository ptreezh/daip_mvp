# 简化版 TUI 基线修复方案

## 目标
修复简化版 TUI 基线，使以下两个测试文件经 `py -m pytest` 全绿（含必要测试侧修正）：

- `tests/integration/test_tui_integration.py`（137 行，4 个测试）
- `tests/test_e2e_tui_debate_model_switching.py`（88 行，1 个端到端测试）

实施方式：本方案归档 → grill-down 自审 → 红灯确认 → 按 gsd 分步 TDD，每步收敛至全绿。

## 已核验事实（2026-08-05 契约核验）

### e2e 测试契约（test_e2e_tui_debate_model_switching.py，全文 88 行已读）
- 被测对象为 `DAIP_TUI`，构造参数九选一注入：`config_manager`、`enhanced_debate_manager`、`ollama_instance_manager`、`model_provider`（其余容器对象走 container DI）。
- fixture 三处 `override_with`：`container.model_provider` / `container.enhanced_debate_manager` / `container.ollama_instance_manager`。
- L22/L30 崩点：`container.config_manager` 是 DEPS 对象，fixture 误当方法直接取 `get_config()` → 需改 `container.config_manager().get_config()`。
- 测试体断言（L82-88）：
  - `app._current_debate['role_models'].get('tech_analyst') == 'qwen3:8b'`
  - `app._current_debate['role_models'].get('pro_arguer') == 'llama3:instruct'`
  - `await app.wait_participant('tech_analyst')` → 再 `('pro_arguer')` → `await app.wait_debate_completed()`
- 结论：`role_models` 须为 `{角色名: 模型名字符串}` dict；模型名来自 `get_debate_model_mappings` 的 `role_model_config.model_name`（tech_analyst.yaml `debate_model_config.model_name = qwen3:8b`、pro_arguer.yaml 为 `llama3:instruct`，均为纯名无前缀，与断言完全一致）。

### 辩论执行路径（enhanced_debate_manager.py，全文 856 行已读完关键段）
- `EnhancedDebateManager.__init__(..., use_optimized_architecture=True)`：优化架构默认开启；`ollama_manager = OllamaInstanceManager(shared_provider=model_provider)`。
- `run_debate` → `_run_debate_optimized`（L79-264）：
  - 跳过模型可用性检查（L98-102，不阻塞离线运行）。
  - 每轮 `_run_optimized_round`（L460-551）：`ollama_manager._switch_model`（纯内存）→ `DebateTurnStartEvent` → `_generate_optimized_response` → `DialogueTurn` → `DebateTurnCompleteEvent` → `TokenUsageEvent`。
  - 总结：`_generate_optimized_summary`（L599+）。
  - 结束：`DebateCompleteEvent`（L260-263）→ 优化路径**必然产出完成事件**。
- `_generate_optimized_response`（L560-597）：调 `ollama_manager.generate_with_model(model_name, prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)`，`except ModelError` 时返回兜底错误文本 + usage=None，**不向生成器抛异常**。
- `OllamaInstanceManager.generate_with_model`（ollama_instance_manager.py L47-104）：任意 provider 异常 → 包装为 `ModelError`（含 ConnectionError/Connection refused → 友好中文消息）。
- **关键结论：离线环境（无 Ollama）下，辩论仍能完整跑完（每轮输出兜底错误文本），`DebateCompleteEvent` 正常产出 → e2e 无需模型桩即可通过，前提是 provider 为真实 LiteLLMProvider 且其 generate 异常被 OllamaInstanceManager 包装为 ModelError。**
- `_get_model_provider_for_config`（L742-761）：按 `{provider}_{model_name}` 缓存**新建**真实 LiteLLMProvider，不使用 `self.model_provider` → 仅影响 legacy 架构路径；优化架构不走此函数。

### 集成测试契约（test_tui_integration.py，L44-73 已读）
- `test_model_switching_integration`（L46-68）：`patch.object(tui_app, '_model_manager')`（**要求 `_model_manager` 属性已存在**，否则 AttributeError）、`patch.object(tui_app, '_model_provider')`；断言 `mock_manager.switch_model.assert_called_once_with(model_name, 'ollama')`（**双参调用**）与 `tui_app._update_current_model.assert_called_once_with(model_name)`；`_handle_model_switch(model_name)` 为同步方法。
- `test_autocomplete_integration`（L70+）：`partial_input = "/he"`，待读完整断言。

### simplified_main.py（2962 行，关键段已读）
- `_apply_smart_defaults`（L1243-1288）：`('help','')` → `('help','show')`；`('help', args)` → `('help', 'show args')`；`default_mappings` 含 help→show、debate→start、model→list 等。
- `_handle_model_switch` 位于 L2462 区域；`_background_tasks` 属性已存在（L286）。
- `_start_debate`（L293-361）：L306 调 `self._debate_manager.run_debate(topic=..., roles_names=..., num_rounds=int(rounds))`。
- `_initialize_debate_manager`（L363-486）：L398 存在 `role_model_manager` NameError。
- `__init__` 未见 `_model_manager` 初始化（待最后确认，若缺则新增）。

### 基础设施
- pytest.ini：`testpaths = tests`，rootdir 仓库根，`py -m pytest` 可用（Windows 无 `python` 命令，用 `py`）。
- `tui/__init__.py`（64 行）：缺 `import asyncio`、缺 `Container` 导出；集成测试 `patch('src.daip_live.tui.asyncio.get_running_loop')` 依赖模块级 `asyncio` 属性存在。
- container.py：`providers` 已含 model_provider / ollama_instance_manager / enhanced_debate_manager / config_manager / debate_manager 等。
- 角色 YAML：tech_analyst.yaml 全文核毕（debate_model_config=qwen3:8b）；pro_arguer.yaml 为 llama3:instruct。

## 必改清单

### 代码侧（simplified_main.py + tui/__init__.py）
1. `tui/__init__.py`：补 `import asyncio`；`from daip_live.container import Container` 并导出。
2. `__init__`：新增 `self._model_manager`（若不存在）——双参 `switch_model(model_name, provider)` 兼容封装（真实 `ModelManager.switch_model` 为单参，需要薄适配层或直接调真实对象时剥离 provider 参数）；同时保证 `patch.object(tui_app, '_model_manager')` 可打补丁。
3. `_handle_model_switch`（L2462）：改为调 `self._model_manager.switch_model(model_name, 'ollama')`（满足集成测试双参断言）+ 保留 `self._update_current_model(model_name)` 调用。
4. `_initialize_debate_manager`：kwargs `_enhanced_debate_manager` 优先 → `container.enhanced_debate_manager()` → 手动构造兜底；修 L398 NameError（`self._role_model_manager` / container / None 三级兜底）；确保结果不被基础 `debate_manager()` 覆盖。
5. `_start_debate`：启动时填充 `_current_debate`（含 `role_models = {role_name: mapping.role_model_config.model_name}`）；新增 async `wait_debate_started` / `wait_participant` / `wait_debate_completed`（内部事件 + 30s 超时，`participants_seen` 集合避免瞬态竞争）。

### 测试侧（fixture / 集成测试）
6. e2e fixture L22/L30：`container.config_manager()` 调用修正为 `container.config_manager().get_config()`。
7. 集成测试 `test_input_handling_integration`（L21-44，待读完整）：按真实分发链适配（async/await + patch `_handle_help_command` + 参数断言）。

## 验证步骤（TDD）
1. 红灯：`py -m pytest tests/integration/test_tui_integration.py tests/test_e2e_tui_debate_model_switching.py -x` 记录失败清单。
2. 代码侧 1-4 → `py -m pytest tests/integration/test_tui_integration.py -x`。
3. 代码侧 5 → e2e 单测。
4. 测试侧 6-7 → 全量 `py -m pytest` 收敛。
5. 质量：`ruff check src/daip_live/tui/`、`mypy src/daip_live/tui/`（如已有配置）。

## 风险
- `_handle_help_command` / `_dispatch_command` 链若与集成测试期望不一致 → 以真实分发链为准修测试断言（测试侧修正已获授权）。
- 优化架构默认开启（`use_optimized_architecture=True`）→ e2e 走 `_run_debate_optimized`；若 fixture 传入 False 需复核（fixture 未传 → 默认 True，安全）。
- `_model_manager` 双参适配：真实对象为单参 `switch_model(model_name)` → 需薄封装，避免生产路径 TypeError。

## 待办收尾核验（保存后继续）
- [x] 集成测试 L1-44（`test_input_handling_integration` 完整体）与 L74-137（autocomplete 断言、command/background 两测试确认）— 已重写并全绿
- [x] `_generate_optimized_summary`（L599-740）确认 ModelError 兜底 — e2e 通过（fake_key 下 summary 正常产出）
- [x] role_model_manager.py 中 `RoleModelMapping.from_role` 的 debate 配置选择（L98-160 区域）— L118-120 确认 `use_debate_config=True` 时取 `debate_model_config`
- [x] simplified_main.py `__init__` 中 `_model_manager` 是否已初始化（rg 确认）— 已存在，集成测试验证通过
- [x] `_handle_model_switch` 当前实现（L2427-2496 区域）— 双参调用，集成测试验证通过

## 实施结果（2026-08-06）
- 全量复跑：`py -m pytest tests/integration/test_tui_integration.py tests/test_e2e_tui_debate_model_switching.py --tb=short -q` → **7 passed**（integration 6/6 + e2e 1/1），45.30s。
- 代码侧第 5 项完成：`_start_debate` 启动即填 `_current_debate`（is_active/topic/total_rounds/role_models），turn-complete 分支更新 current_round/current_participant 并登记 `_debate_participants_spoken`，complete/异常路径复位 is_active；新增 `_resolve_role_models` + `wait_debate_started` / `wait_participant` / `wait_debate_completed`（30s 超时轮询）。
- 原 "Task was destroyed but it is pending"（`_start_debate` L325 挂起）泄漏已消除。
- 残留警告（非阻断，未改动）：`database.py:39` Pydantic `session.dict()` 弃用；provider 层 Pydantic 序列化警告（Expected 10 fields but got 6，litellm 响应结构差异）。
- 计划全部必改项（代码侧 1-5 + 测试侧 6-7）已交付并验证。
