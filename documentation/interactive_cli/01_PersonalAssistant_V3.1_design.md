# 01 - 个人智能秘书 (V3.1) - 设计文档

## 1. 技术方法
个人智能秘书将实现为一个三层决策模型，在 `start_personal_assistant()` 函数中进行编排。

- **`IntentClassifier`**: 一个独立的组件（类或函数），负责执行第一层决策。它封装了调用LLM以区分“闲聊”和“复杂任务”的逻辑。
- **`CasualChat`**: 一个独立的组件，负责处理闲聊模式。它管理对话历史，并使用特定的“Paul Graham风格”Prompt调用LLM。
- **`ComplexTaskHandler`**: 一个独立的组件，负责处理复杂任务。它内部包含了V3方案的两个核心组件：
    - **`Secretary`**: 执行意图精炼。
    - **`Planner`**: 执行任务分解。
- **`TaskManager`**: 与V2设计相同，负责任务的持久化和状态管理。
- **`Executor`**: 与V2设计相同，负责执行由`Planner`生成的API计划。

这种组件化的设计使得代码结构清晰，易于独立测试。

## 2. 组件交互
- **`start_personal_assistant()`**:
    - 初始化 `IntentClassifier`, `CasualChat`, `ComplexTaskHandler`, `TaskManager`。
    - 进入主循环，接收用户输入。
    - **For each input**:
        1.  调用 `intent_classifier.classify(user_input)`。
        2.  **If "闲聊"**: 调用 `casual_chat.handle(user_input)`，打印其返回的对话内容。
        3.  **If "复杂任务"**: 调用 `complex_task_handler.handle(user_input)`，它会返回一个任务ID。打印任务创建成功的信息。

- **`ComplexTaskHandler.handle(user_input)`**:
    1.  调用 `secretary.refine(user_input)` 获得结构化的指令。
    2.  调用 `planner.plan(structured_command)` 获得API执行计划。
    3.  调用 `task_manager.create_task(...)` 创建任务。
    4.  调用 `executor.execute_plan_async(plan, task_id)` 异步执行。
    5.  返回 `task_id`。

## 3. 关键Prompt设计
- **意图分类器Prompt**: 极简、零样本（zero-shot），强制要求输出特定关键词。
- **闲聊模式Prompt**: 详细的角色设定（few-shot），包含Paul Graham/Brooks的核心理念，并附带最近的对话历史作为上下文。
- **秘书角色Prompt**: 详细的角色设定，解释其目标（分析、重构、补充上下文），提供用户历史作为参考，并强制要求输出JSON格式的结构化指令。
- **规划师角色Prompt**: 包含精炼后的指令，以及一份**可用API的列表和描述**，并强制要求输出JSON格式的API执行计划。

## 4. 测试策略
- **单元测试**:
    - **`IntentClassifier`**: Mock `IntegratedLLMManager`。提供不同的用户输入，断言LLM被以正确的“分类器”Prompt调用，并测试分类器能否正确解析LLM返回的 "闲聊" / "复杂任务" 字符串。
    - **`CasualChat`**: Mock `IntegratedLLMManager`。模拟多轮对话，断言每次传递给LLM的Prompt都正确地包含了“Paul Graham风格”的角色设定和不断增长的对话历史。
    - **`Secretary` & `Planner`**: Mock `IntegratedLLMManager`。分别测试它们是否能构建正确的Prompt，并正确解析LLM返回的JSON。
    - **`start_personal_assistant` (Orchestrator)**: Mock `IntentClassifier`, `CasualChat`, `ComplexTaskHandler`。测试主循环是否能根据 `IntentClassifier` 的返回值，正确地调用 `CasualChat` 或 `ComplexTaskHandler`。
