# 阶段 2: 智能体助手 - 设计

## 最佳实践方案：工作流驱动的编排 (健壮性、优雅降级、去耦合)

我们将把“编排”的职责从一个定制的“个人助手编排器”转移到一个通用且可配置的 **`src.institutional_primitives.workflow_engine.WorkflowEngine`** 上。

### 1. 核心架构与组件

*   **`PersonalAssistantRouter` (或简化版 `Orchestrator`)**
    *   **职责:** 作为 CLI 的入口点，负责**初始的用户意图分类**。
    *   **模式分派:**
        *   如果意图是“闲聊”，则进入一个简单的“闲聊模式”循环，直接与 LLM 交互。
        *   如果意图是“复杂任务”，则将用户请求传递给“规划师”LLM，并**启动一个工作流**。
    *   **去耦合:** 轻量级，只负责路由和启动工作流，不直接管理复杂任务的执行细节。

*   **`IntentAnalysisService` (增强型)**
    *   **职责:** 执行意图分类。将调用 `IntegratedLLMManager.call_llm_for_role`，使用专门的“分类器”角色和 Prompt，引导 LLM 输出结构化意图（例如，使用 `IntentType` 和 `MessageIntent` 枚举）。
    *   **去耦合:** `PersonalAssistantRouter` 依赖于 `IntentAnalysisService` 接口。
    *   **优雅降级:** 如果 LLM 意图分析失败，可回退到基于关键词的 `BasicIntentAnalysisService` 或默认意图。

*   **“规划师”LLM (Agent/Role)**
    *   **职责:** 接收用户请求（或精炼后的指令），并基于 `GLOBAL_API_DICTIONARY.md` 中定义的可用 API，生成一个**可由 `WorkflowEngine` 直接执行的 JSON 格式的“工作流定义”**。
    *   **核心:** 扮演“智能协调者”角色，将高层意图转化为可执行的步骤序列。Prompt 中需包含可用 API 的详细 schema。
    # 阶段 2: 智能体助手 - 设计

## 最佳实践方案：工作流驱动的编排 (健壮性、优雅降级、去耦合)

我们将把“编排”的职责从一个定制的“个人助手编排器”转移到一个通用且可配置的 **`src.institutional_primitives.workflow_engine.WorkflowEngine`** 上。

### 1. 核心架构与组件

*   **`PersonalAssistantRouter` (或简化版 `Orchestrator`)**
    *   **职责:** 作为 CLI 的入口点，负责**初始的用户意图分类**。
    *   **模式分派:**
        *   如果意图是“闲聊”，则进入一个简单的“闲聊模式”循环，直接与 LLM 交互。
        *   如果意图是“复杂任务”，则将用户请求传递给“规划师”LLM，并**启动一个工作流**。
    *   **去耦合:** 轻量级，只负责路由和启动工作流，不直接管理复杂任务的执行细节。

*   **`IntentAnalysisService` (增强型)**
    *   **职责:** 执行意图分类。将调用 `IntegratedLLMManager.call_llm_for_role`，使用专门的“分类器”角色和 Prompt，引导 LLM 输出结构化意图（例如，使用 `IntentType` 和 `MessageIntent` 枚举）。
    *   **去耦合:** `PersonalAssistantRouter` 依赖于 `IntentAnalysisService` 接口。
    *   **优雅降级:** 如果 LLM 意图分析失败，可回退到基于关键词的 `BasicIntentAnalysisService` 或默认意图。

*   **“规划师”LLM (Agent/Role)**
    *   **职责:** 接收用户请求（或精炼后的指令），并基于 `GLOBAL_API_DICTIONARY.md` 中定义的可用 API，生成一个**可由 `WorkflowEngine` 直接执行的 JSON 格式的“工作流定义”**。
    *   **核心:** 扮演“智能协调者”角色，将高层意图转化为可执行的步骤序列。Prompt 中需包含可用 API 的详细 schema。
    *   **扩展职责:** 能够生成包含**辩论和聊天模块的“议事规则”制度原语**（如 `DebateRulePrimitive`, `ChatRulePrimitive`）的工作流定义。同时，根据议题智能匹配或创建辩论/聊天角色，并将其纳入工作流。

*   **`WorkflowEngine` (核心编排器)**
    *   **职责:** 接收“规划师”LLM 生成的“工作流定义”，并负责**异步执行**其中的每一个步骤（即 API 调用或制度原语）。
    *   **健壮性:** 自身具备状态管理、错误处理、重试和日志记录能力。
    *   **去耦合:** 不关心具体是哪个 LLM 角色生成了工作流，也不关心工作流内部的每个步骤具体由哪个服务实现。

*   **`TaskManager`**
    *   **职责:** 管理复杂任务的生命周期和持久化，包括创建、更新状态、查询。

*   **`TaskExecutor` (由 `WorkflowEngine` 内部或作为其调用的原语)**
    *   **职责:** 负责执行工作流中具体的 API 调用步骤。
    *   **健壮性:** 捕获服务调用异常，并根据工作流定义进行错误处理（例如，记录、重试、标记失败）。

### 2. 状态管理与记忆

*   **对话状态:** `PersonalAssistantRouter` 在闲聊模式下维护短期对话历史。
*   **任务状态:** `TaskManager` 负责复杂任务的持久化状态（PENDING, RUNNING, COMPLETED, FAILED）。
*   **长期记忆:** `secretary_log.jsonl` 和 `task_memory.json` 用于记录所有交互和任务状态。

### 3. 错误处理与优雅降级

*   **LLM 调用失败:** 指数退避、重试、回退到简单机制、记录错误。
*   **API 执行失败:** `TaskExecutor` 捕获异常，记录错误，更新任务状态，并根据工作流定义进行后续处理。
*   **输入验证:** 严格验证用户输入和 LLM 生成的计划。

### 4. 去耦合策略

*   **服务接口:** 所有核心服务（意图分析、任务管理、LLM 管理等）都应暴露清晰的接口（ABC），`PersonalAssistantRouter` 和 `WorkflowEngine` 依赖这些接口。
*   **依赖注入:** 通过 `AppState` 或构造函数注入服务实例。
*   **工作流驱动:** 各个服务通过工作流定义进行松散耦合，而非直接相互调用。

### 5. CLI 命令结构

*   `daip-cli assistant chat <query>`: 主要入口点，委托给 `PersonalAssistantRouter`。
*   `daip-cli assistant status <task_id>`: 查询复杂任务状态。
*   `daip-cli assistant logs`: 查看 `secretary_log.jsonl`。
*   `daip-cli debate view-disagreements <debate_id>`: 查看辩论分歧点。
*   `daip-cli debate select-consensus-algorithm <debate_id> <algorithm_name>`: 动态选择共识算法。


*   **`WorkflowEngine` (核心编排器)**
    *   **职责:** 接收“规划师”LLM 生成的“工作流定义”，并负责**异步执行**其中的每一个步骤（即 API 调用或制度原语）。
    *   **健壮性:** 自身具备状态管理、错误处理、重试和日志记录能力。
    *   **去耦合:** 不关心具体是哪个 LLM 角色生成了工作流，也不关心工作流内部的每个步骤具体由哪个服务实现。

*   **`TaskManager`**
    *   **职责:** 管理复杂任务的生命周期和持久化，包括创建、更新状态、查询。

*   **`TaskExecutor` (由 `WorkflowEngine` 内部或作为其调用的原语)**
    *   **职责:** 负责执行工作流中具体的 API 调用步骤。
    *   **健壮性:** 捕获服务调用异常，并根据工作流定义进行错误处理（例如，记录、重试、标记失败）。

### 2. 状态管理与记忆

*   **对话状态:** `PersonalAssistantRouter` 在闲聊模式下维护短期对话历史。
*   **任务状态:** `TaskManager` 负责复杂任务的持久化状态（PENDING, RUNNING, COMPLETED, FAILED）。
*   **长期记忆:** `secretary_log.jsonl` 和 `task_memory.json` 用于记录所有交互和任务状态。

### 3. 错误处理与优雅降级

*   **LLM 调用失败:** 指数退避、重试、回退到简单机制、记录错误。
*   **API 执行失败:** `TaskExecutor` 捕获异常，记录错误，更新任务状态，并根据工作流定义进行后续处理。
*   **输入验证:** 严格验证用户输入和 LLM 生成的计划。

### 4. 去耦合策略

*   **服务接口:** 所有核心服务（意图分析、任务管理、LLM 管理等）都应暴露清晰的接口（ABC），`PersonalAssistantRouter` 和 `WorkflowEngine` 依赖这些接口。
*   **依赖注入:** 通过 `AppState` 或构造函数注入服务实例。
*   **工作流驱动:** 各个服务通过工作流定义进行松散耦合，而非直接相互调用。

### 5. CLI 命令结构

*   `daip-cli assistant chat <query>`: 主要入口点，委托给 `PersonalAssistantRouter`。
*   `daip-cli assistant status <task_id>`: 查询复杂任务状态。
*   `daip-cli assistant logs`: 查看 `secretary_log.jsonl`。
*   `daip-cli debate view-disagreements <debate_id>`: 查看辩论分歧点。
*   `daip-cli debate select-consensus-algorithm <debate_id> <algorithm_name>`: 动态选择共识算法。
