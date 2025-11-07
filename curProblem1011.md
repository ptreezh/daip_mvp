# 问题诊断与测试计划 - 2025-10-11

## 1. 当前问题 (Problem)

核心问题是在 `tests/agent_engine/test_workflow.py` 中的 `test_token_usage_is_accumulated` 测试持续失败。

- **预期行为**: Agent 在一个执行步骤中，完成“思考 -> 使用工具 -> 再次思考 -> 最终响应”的完整序列，这个过程应该调用两次大模型（`generate` 函数）。
- **实际行为**: 测试结果始终是 `AssertionError: assert 100 == 200`，这确凿地证明了 `generate` 函数只被调用了一次。

## 2. 上下文背景 (Context)

- 我们正在对 `agent_engine` 模块进行大规模的回归测试修复。
- 此前的重构将 `AgentExecutor` 的核心功能拆分到了 `StateManager` (状态管理器) 和 `StepExecutor` (步骤执行器) 中。
- 当前的 `test_token_usage_is_accumulated` 测试旨在验证重构后的 `StepExecutor` 依然能够处理一个包含工具调用的、多轮思考的复杂任务步骤。

## 3. 已尝试的分析与失败的假设 (Analysis & Failed Hypotheses)

为了解决 `100 == 200` 的问题，我提出并验证了多个假设，但全部失败，这表明问题的根源非常隐蔽。

1.  **假设1：`StateManager` 未正确连接**
    - **操作**: 通过依赖注入将 `StateManager` 传入 `StepExecutor`。
    - **结果**: 失败。Token 计数开始更新（从0变为100），但第二次调用仍未发生。

2.  **假设2：`usage` 对象类型错误**
    - **操作**: 发现 `StepExecutor` 期望 `generate` 返回一个 `dict` 而不是 `MagicMock`。修改了测试用例。
    - **结果**: 失败。错误依旧是 `100 == 200`。

3.  **假设3：`tool_manager.execute_tool` 的同步/异步调用不匹配**
    - **操作**: 将 `StepExecutor` 中的调用改为 `await`，并将测试中的 mock 改为 `AsyncMock`。
    - **结果**: 失败。错误依旧是 `100 == 200`。

4.  **假设4：`AsyncMock` 的 `side_effect` 行为不符合预期**
    - **操作**: 怀疑 `is_todo_list_complete` 的 `side_effect=[False, True]` 导致主循环未执行。将其改为一个明确的、有状态的 `async def` 闭包函数。
    - **结果**: 失败。错误依旧是 `100 == 200`。这证明了主循环确实执行了，问题在 `StepExecutor` 内部。

5.  **假设5：`_parse_tool_call` 解析逻辑有缺陷**
    - **操作**: 多次尝试加固解析工具调用的正则表达式，甚至用一个硬编码的“哑”实现替换它。
    - **结果**: 失败。错误依旧是 `100 == 200`。

## 4. 核心障碍 (Obstacles)

- **根本矛盾**: `StepExecutor` 的状态机代码逻辑清晰地表明，在工具执行后，状态会切换回 `THINKING`，这**应该**触发第二次 `generate` 调用。但所有测试结果都表明这没有发生。
- **调试失效**: 常规的逻辑推理和代码检查已完全失效。即使通过 `print` 语句进行最原始的调试，也只观察到了 `THINKING -> EVALUATING -> RESPONDING` 的错误状态流，而无法解释**为什么**状态没有按预期进入 `EXECUTING_TOOL`。

## 5. 下一步测试计划 (TDD-Driven Test Plan)

我将严格遵循TDD，从最小的单元开始，分块隔离测试，重新建立信任链。

### 阶段一：原子单元测试 - `_parse_tool_call`

- **目标**: 彻底、绝对地确认 `_parse_tool_call` 函数的行为。
- **RED**:
    1. 创建一个全新的测试文件 `tests/agent_engine/test_parser.py`。
    2. 在其中编写一个**同步的、不依赖任何 fixture** 的测试函数 `test_vanilla_parse_tool_call`。
    3. 在此函数中，直接用字符串 `"Use Tool: search_web(query='test')"` 调用 `StepExecutor._parse_tool_call`。
    4. 断言其返回值**不是** `None`，并且等于 `('search_web', {'query': 'test'})`。
- **GREEN**:
    1. 运行此测试。如果失败，则集中全部精力修复 `_parse_tool_call` 方法，直到这个最简单的测试通过为止。

### 阶段二：隔离集成测试 - `StepExecutor` 状态机

- **目标**: 在完全隔离的环境中，验证 `StepExecutor` 的内部循环。
- **RED**:
    1. 在 `test_workflow.py` 中创建一个新的测试 `test_isolated_step_executor_loop`。
    2. **不使用** `AgentExecutor`。直接实例化 `StepExecutor`。
    3. 为其所有依赖（`state_manager`, `memory_service`, `model_provider`, `tool_manager`）提供干净的 `AsyncMock`。
    4. 精确地设置 `model_provider.generate` 的 `side_effect`，使其按顺序返回“工具调用”和“最终答案”。
    5. 调用 `async for event in step_executor.execute_step(...)` 并收集所有事件。
    6. 断言 `model_provider.generate.call_count` **等于 2**。
- **GREEN**:
    1. 运行此测试。它很可能会失败。
    2. 因为环境已被完全隔离，所有变量都在掌控之中。通过调试这个失败的测试，我们必然能找到状态机循环提前退出的根本原因，并修复它。

### 阶段三：回归测试

- **目标**: 验证端到端行为已修复。
- **执行**:
    1. 在前两个阶段的测试全部通过后，重新运行最初失败的 `test_token_usage_is_accumulated` 测试。
    2. 此时，它应该会通过。

这个计划将使我们能够从最基础的单元功能开始，逐层向上验证，最终定位并解决这个顽固的bug。
