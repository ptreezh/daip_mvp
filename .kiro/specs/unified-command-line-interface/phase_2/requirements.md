# 阶段 2: 智能体助手 - 需求

## 核心功能与用户故事 (来自 01_PersonalAssistant_V3.1_requirements.md)

*   **FR-PA-V3.1-01: 意图分类**
    *   **必须** 在处理用户输入前，首先判断其意图是“闲聊”还是“具体的工作指令或专业研究或专业咨询需求”，如果不是闲聊，需要判断这个任务是否可以自己完成，还是需要分解的“复杂任务”，是否有明确的组织讨论的指示，如果有组织讨论的指示，则帮助用户提交一个组织专家协同辩论的工作流，最后返回辩论和共识的结果，如果是复杂的任务则调用规划师的角色，发起一个任务分解最后系统综合返回的工作流。
    *   **必须** 通过调用 `IntegratedLLMManager.call_llm_for_role` 并使用一个“分类器”角色的Prompt来实现此功能。
*   **FR-PA-V3.1-02: 闲聊模式**
    *   如果意图为“闲聊”，**必须** 进入一个专门的对话循环。
    *   在此循环中，对 `IntegratedLLMManager.call_llm_for_role` 的每次调用都**必须**使用一个特定的、符合Paul Graham/Arthur Brooks风格的Prompt。
    *   对话**必须**能持续多轮，直到用户输入退出命令或一个被识别为“复杂任务”的指令。
*   **FR-PA-V3.1-03: 复杂任务处理模式**
    *   如果意图为“复杂任务”，**必须** 启动一个两阶段的规划流程：
        1.  **意图精炼**: 调用LLM（“秘书”角色）对用户的原始指令进行分析、上下文补充和重构，输出结构化的指令。
        2.  **任务分解**: 调用LLM（“规划师”角色）将结构化的指令分解为一个由**已验证API调用**组成的JSON执行计划（即工作流定义）。
    *   **必须** 调用 `TaskManager` 来创建和持久化任务。
    *   **必须** 异步执行该计划（通过工作流引擎）。
*   **FR-PA-V3.1-04: 任务管理与记忆**
    *   **必须** 为每个复杂任务分配唯一ID，并允许用户查询状态。
    *   **必须** 将用户的原始指令和每次交互都记录到持久化日志中 (`secretary_log.jsonl`)。
    *   **必须** 将每个被创建的复杂任务及其状态记录到持久化存储中 (`task_memory.json`)。

## 扩展需求 (来自 IMPLEMENTATION_PLAN.md)

*   用户能够通过 `daip-cli debate view-disagreements <debate_id>` 查看指定辩论中的分歧点。
*   用户能够通过 `daip-cli debate select-consensus-algorithm <debate_id> <algorithm_name>` 动态选择辩论的共识算法。
*   用户能够通过 `daip-cli assistant chat <query>` 与个人助手进行交互。
*   用户能够通过 `daip-cli assistant status <task_id>` 查询复杂任务的状态。
*   用户能够通过 `daip-cli assistant logs` 查看 `secretary_log.jsonl` 中的最新条目。
