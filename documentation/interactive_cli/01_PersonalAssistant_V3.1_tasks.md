# 01 - 个人智能秘书 (V3.1) - 任务列表

## 概述
此任务列表以TDD方式涵盖了实现V3.1版个人智能秘书的所有步骤。`TaskManager` 和 `Executor` 的任务与V2版本相似，可复用。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 意图分类 (`IntentClassifier`)

-   [ ] **RED**: **T-PA-V3.1-01**: 创建测试 `test_intent_classifier.py`。编写失败测试 `test_classify_as_casual_chat`。Mock `IntegratedLLMManager`，让其在收到包含“分类器”Prompt的调用时返回 "闲聊"。断言 `classifier.classify(...)` 返回 "闲聊"。
-   [ ] **GREEN**: **T-PA-V3.1-02**: 创建 `intent_classifier.py`。实现 `classify` 方法，使其构建正确的Prompt，调用LLM并解析结果。让测试通过。
-   [ ] **RED**: **T-PA-V3.1-03**: 编写类似的失败测试 `test_classify_as_complex_task`。
-   [ ] **GREEN**: **T-PA-V3.1-04**: 确保 `classify` 方法能正确处理 "复杂任务" 的返回，让测试通过。

### Epic 2: 闲聊模式 (`CasualChat`)

-   [ ] **RED**: **T-PA-V3.1-05**: 创建测试 `test_casual_chat.py`。编写失败测试 `test_casual_chat_prompt`。Mock `IntegratedLLMManager`。调用 `casual_chat.handle("你好")`，断言传递给LLM的Prompt包含了“Paul Graham风格”的角色设定。
-   [ ] **GREEN**: **T-PA-V3.1-06**: 创建 `casual_chat.py`。实现 `handle` 方法，使其构建正确的Prompt并调用LLM。让测试通过。
-   [ ] **RED**: **T-PA-V3.1-07**: 编写失败测试 `test_casual_chat_maintains_history`。连续调用两次 `casual_chat.handle`，断言第二次调用LLM时的Prompt包含了第一次的用户输入和AI响应。
-   [ ] **GREEN**: **T-PA-V3.1-08**: 在 `CasualChat` 类中添加对话历史管理，让测试通过。

### Epic 3: 复杂任务处理 (`ComplexTaskHandler`, `Secretary`, `Planner`)

-   [ ] **RED**: **T-PA-V3.1-09**: 创建测试 `test_secretary.py`。编写失败测试，断言 `secretary.refine` 方法调用LLM时，构建了包含用户历史和“秘书”角色的Prompt。
-   [ ] **GREEN**: **T-PA-V3.1-10**: 创建 `secretary.py` 并实现 `refine` 方法，让测试通过。
-   [ ] **RED**: **T-PA-V3.1-11**: 创建测试 `test_planner.py`。编写失败测试，断言 `planner.plan` 方法调用LLM时，构建了包含可用API列表和“规划师”角色的Prompt。
-   [ ] **GREEN**: **T-PA-V3.1-12**: 创建 `planner.py` 并实现 `plan` 方法，让测试通过。
-   [ ] **RED**: **T-PA-V3.1-13**: 创建测试 `test_complex_task_handler.py`。Mock `Secretary`, `Planner`, `TaskManager`, `Executor`。断言 `handler.handle` 方法按顺序调用了 `secretary.refine`, `planner.plan`, `task_manager.create_task`, `executor.execute_plan_async`。
-   [ ] **GREEN**: **T-PA-V3.1-14**: 创建 `complex_task_handler.py` 并实现 `handle` 方法的编排逻辑，让测试通过。

### Epic 4: 主循环集成

-   [ ] **RED**: **T-PA-V3.1-15**: 在 `test_cli_framework.py` 或独立的 `test_personal_assistant_main.py` 中，编写失败测试 `test_main_loop_dispatches_to_casual_chat`。Mock `IntentClassifier` 使其返回 "闲聊"，Mock `CasualChat`。断言 `casual_chat.handle` 被调用。
-   [ ] **GREEN**: **T-PA-V3.1-16**: 在 `interactive_cli.py` 的 `start_personal_assistant` 中实现主分发逻辑，让测试通过。
-   [ ] **RED**: **T-PA-V3.1-17**: 编写失败测试 `test_main_loop_dispatches_to_complex_task`。Mock `IntentClassifier` 使其返回 "复杂任务"，Mock `ComplexTaskHandler`。断言 `complex_task_handler.handle` 被调用。
-   [ ] **GREEN**: **T-PA-V3.1-18**: 完善 `start_personal_assistant` 的主分发逻辑，让测试通过。
-   [ ] **REFACTOR**: **T-PA-V3.1-19**: 全面重构个人智能秘书的所有新建组件，确保代码清晰、职责单一，并确保所有测试依然通过。
