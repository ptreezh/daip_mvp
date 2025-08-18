# 阶段 2: 智能体助手 - 任务清单

## 核心任务 (TDD 驱动)

*   **2.1 实现 `PersonalAssistantRouter` 的意图分类与模式分派**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `PersonalAssistantRouter` 能正确识别“闲聊”和“复杂任务”意图，并能根据意图分派到不同的处理流程。测试 LLM 意图分析失败时的优雅降级（回退到关键词或默认）。
        *   **GREEN:** 实现 `PersonalAssistantRouter` 的核心逻辑，集成增强型 `IntentAnalysisService`。
        *   **REFACTOR:** 优化意图分类的 Prompt，确保其准确性和鲁棒性。
*   **2.2 增强 `IntentAnalysisService`**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `IntentAnalysisService` 能够调用 `IntegratedLLMManager.call_llm_for_role` 并使用“分类器”角色，返回结构化意图。测试 LLM 响应解析的健壮性。
        *   **GREEN:** 修改 `IntentAnalysisService`，使其使用 LLM 进行意图分类，并处理 LLM 响应。
        *   **REFACTOR:** 优化 LLM 调用参数和错误处理。
*   **2.3 实现闲聊模式**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证在闲聊模式下，助手能进行多轮对话，并使用 Paul Graham/Arthur Brooks 风格的 Prompt。测试用户输入复杂任务指令时能正确退出闲聊模式。
        *   **GREEN:** 在 `PersonalAssistantRouter` 中实现闲聊模式的对话循环，调用 `IntegratedLLMManager.call_llm_for_role`。
        *   **REFACTOR:** 优化对话上下文管理和 Prompt。
# 阶段 2: 智能体助手 - 任务清单

## 核心任务 (TDD 驱动)

*   **2.1 实现 `PersonalAssistantRouter` 的意图分类与模式分派**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `PersonalAssistantRouter` 能正确识别“闲聊”和“复杂任务”意图，并能根据意图分派到不同的处理流程。测试 LLM 意图分析失败时的优雅降级（回退到关键词或默认）。
        *   **GREEN:** 实现 `PersonalAssistantRouter` 的核心逻辑，集成增强型 `IntentAnalysisService`。
        *   **REFACTOR:** 优化意图分类的 Prompt，确保其准确性和鲁棒性。
*   **2.2 增强 `IntentAnalysisService`**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `IntentAnalysisService` 能够调用 `IntegratedLLMManager.call_llm_for_role` 并使用“分类器”角色，返回结构化意图。测试 LLM 响应解析的健壮性。
        *   **GREEN:** 修改 `IntentAnalysisService`，使其使用 LLM 进行意图分类，并处理 LLM 响应。
        *   **REFACTOR:** 优化 LLM 调用参数和错误处理。
*   **2.3 实现闲聊模式**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证在闲聊模式下，助手能进行多轮对话，并使用 Paul Graham/Arthur Brooks 风格的 Prompt。测试用户输入复杂任务指令时能正确退出闲聊模式。
        *   **GREEN:** 在 `PersonalAssistantRouter` 中实现闲聊模式的对话循环，调用 `IntegratedLLMManager.call_llm_for_role`。
        *   **REFACTOR:** 优化对话上下文管理和 Prompt。
*   **2.4 实现复杂任务的意图精炼与规划 (规划师 LLM)**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证“秘书”LLM 能精炼用户指令，并验证“规划师”LLM 能根据精炼后的指令和提供的 API Schema 生成有效的 JSON 工作流定义，**包括辩论和聊天模块的“议事规则”制度原语**。测试生成无效 API 调用时的错误处理。
        *   **GREEN:** 实现调用“秘书”和“规划师”LLM 的逻辑，并解析其输出为工作流定义。
        *   **REFACTOR:** 优化 LLM Prompt，确保生成的 API 调用符合 `GLOBAL_API_DICTIONARY.md` **并能正确包含和配置议事规则**。
*   **2.5 实现角色匹配与创建逻辑**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证“规划师”LLM 或辅助服务能根据辩论/聊天议题，智能匹配现有角色或生成创建新角色的指令。
        *   **GREEN:** 实现 Planner LLM 与 `RoleManager` 交互的逻辑，包括 `list_roles`, `get_role_by_id`, `save_role`。
        *   **REFACTOR:** 优化角色匹配算法和新角色创建的 Prompt。
*   **2.6 集成 `TaskManager`**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证复杂任务创建后能被 `TaskManager` 正确持久化，并能通过 ID 查询其状态。
        *   **GREEN:** 在 `PersonalAssistantRouter` 中集成 `TaskManager`，用于创建和更新任务状态。
        *   **REFACTOR:** 优化任务状态流转和错误处理。
*   **2.7 启动工作流执行**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `PersonalAssistantRouter` 能将生成的复杂任务工作流定义传递给 `WorkflowEngine` 并成功启动执行。
        *   **GREEN:** 实现将工作流定义传递给 `WorkflowEngine` 的逻辑。
        *   **REFACTOR:** 确保工作流启动的参数正确。
*   **2.8 实现 `daip-cli assistant chat` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `daip-cli assistant chat <query>` 能正确调用 `PersonalAssistantRouter` 并显示其返回的响应。
        *   **GREEN:** 在 `src/cli/main.py` 中添加 `assistant` 子命令组，并实现 `chat` 命令，调用 `PersonalAssistantRouter`。
        *   **REFACTOR:** 优化 CLI 输出的用户体验。
*   **2.9 实现 `daip-cli assistant status <task_id>` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `daip-cli assistant status <task_id>` 能正确查询 `TaskManager` 并显示任务状态。
        *   **GREEN:** 在 `assistant` 子命令组中添加 `status` 命令，调用 `TaskManager`。
        *   **REFACTOR:** 优化任务状态的显示格式。
*   **2.10 实现 `daip-cli assistant logs` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `daip-cli assistant logs` 能正确读取 `secretary_log.jsonl` 并显示最新日志。
        *   **GREEN:** 在 `assistant` 子命令组中添加 `logs` 命令，读取日志文件。
        *   **REFACTOR:** 优化日志显示格式和分页。

## 扩展任务 (来自 IMPLEMENTATION_PLAN.md)

*   **2.11 实现 `daip-cli debate view-disagreements` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟后端服务返回特定辩论的分歧点数据，并断言 CLI 输出能清晰展示这些分歧点。
        *   **GREEN:** 在 `src/cli/main.py` 中创建 `debate` Typer 子命令组，并添加 `view-disagreements` 命令，调用相关后端服务。
        *   **REFACTOR:** 优化分歧点的展示格式，使其易于理解和分析。
*   **2.12 实现 `daip-cli debate select-consensus-algorithm` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟后端服务成功更新辩论的共识算法，并断言 CLI 输出确认信息。测试无效算法名称的错误处理。
        *   **GREEN:** 在 `debate` 子命令组中添加 `select-consensus-algorithm` 命令，调用 `consensus_algorithm_selector`。
        *   **REFACTOR:** 增加对可用共识算法的提示或验证。

*   **2.5 实现角色匹配与创建逻辑**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证“规划师”LLM 或辅助服务能根据辩论/聊天议题，智能匹配现有角色或生成创建新角色的指令。
        *   **GREEN:** 实现 Planner LLM 与 `RoleManager` 交互的逻辑，包括 `list_roles`, `get_role_by_id`, `save_role`。
        *   **REFACTOR:** 优化角色匹配算法和新角色创建的 Prompt。
*   **2.6 集成 `TaskManager`**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证复杂任务创建后能被 `TaskManager` 正确持久化，并能通过 ID 查询其状态。
        *   **GREEN:** 在 `PersonalAssistantRouter` 中集成 `TaskManager`，用于创建和更新任务状态。
        *   **REFACTOR:** 优化任务状态流转和错误处理。
*   **2.7 启动工作流执行**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `PersonalAssistantRouter` 能将生成的复杂任务工作流定义传递给 `WorkflowEngine` 并成功启动执行。
        *   **GREEN:** 实现将工作流定义传递给 `WorkflowEngine` 的逻辑。
        *   **REFACTOR:** 确保工作流启动的参数正确。
*   **2.8 实现 `daip-cli assistant chat` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `daip-cli assistant chat <query>` 能正确调用 `PersonalAssistantRouter` 并显示其返回的响应。
        *   **GREEN:** 在 `src/cli/main.py` 中添加 `assistant` 子命令组，并实现 `chat` 命令，调用 `PersonalAssistantRouter`。
        *   **REFACTOR:** 优化 CLI 输出的用户体验。
*   **2.9 实现 `daip-cli assistant status <task_id>` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `daip-cli assistant status <task_id>` 能正确查询 `TaskManager` 并显示任务状态。
        *   **GREEN:** 在 `assistant` 子命令组中添加 `status` 命令，调用 `TaskManager`。
        *   **REFACTOR:** 优化任务状态的显示格式。
*   **2.10 实现 `daip-cli assistant logs` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `daip-cli assistant logs` 能正确读取 `secretary_log.jsonl` 并显示最新日志。
        *   **GREEN:** 在 `assistant` 子命令组中添加 `logs` 命令，读取日志文件。
        *   **REFACTOR:** 优化日志显示格式和分页。

## 扩展任务 (来自 IMPLEMENTATION_PLAN.md)

*   **2.11 实现 `daip-cli debate view-disagreements` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟后端服务返回特定辩论的分歧点数据，并断言 CLI 输出能清晰展示这些分歧点。
        *   **GREEN:** 在 `src/cli/main.py` 中创建 `debate` Typer 子命令组，并添加 `view-disagreements` 命令，调用相关后端服务。
        *   **REFACTOR:** 优化分歧点的展示格式，使其易于理解和分析。
*   **2.12 实现 `daip-cli debate select-consensus-algorithm` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟后端服务成功更新辩论的共识算法，并断言 CLI 输出确认信息。测试无效算法名称的错误处理。
        *   **GREEN:** 在 `debate` 子命令组中添加 `select-consensus-algorithm` 命令，调用 `consensus_algorithm_selector`。
        *   **REFACTOR:** 增加对可用共识算法的提示或验证。
