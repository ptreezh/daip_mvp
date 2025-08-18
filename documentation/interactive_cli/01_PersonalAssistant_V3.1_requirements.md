# 01 - 个人智能秘书 (V3.1) - 需求文档

## 1. 简介
本模块旨在实现一个具备高级交互能力的个人智能秘书。它能区分用户意图，在“闲聊”和“复杂任务处理”两种模式间智能切换，并能对复杂任务进行规划和执行。

## 2. 核心功能与用户故事
- **As a user**, I want the assistant to engage in insightful, casual conversation when I'm not giving it a specific task.
- **As a user**, I want the assistant to recognize when I'm giving it a complex, multi-step task.
- **As a user**, I want the assistant to analyze my complex tasks, refine them, and create an execution plan.
- **As a user**, I want the assistant to execute that plan using the system's capabilities (debates, wikis, etc.).
- **As a user**, I want the assistant to maintain a long-term memory of my requests.

## 3. 功能性需求

### FR-PA-V3.1-01: 意图分类
- **必须** 在处理用户输入前，首先判断其意图是“闲聊”还是“具体的工作指令或专业研究或专业咨询需求”，如果不是闲聊，需要判断这个任务是否可以自己完成，还是需要分解的“复杂任务”，是否有明确的组织讨论的指示，如果有组织讨论的指示，则帮助用户提交一个组织专家协同辩论的工作流，最后返回辩论和共识的结果，如果是复杂的任务则调用规划师的角色，发起一个任务分解最后系统综合返回的工作流。
- **必须** 通过调用 `IntegratedLLMManager.call_llm_for_role` 并使用一个“分类器”角色的Prompt来实现此功能。

### FR-PA-V3.1-02: 闲聊模式
- 如果意图为“闲聊”，**必须** 进入一个专门的对话循环。
- 在此循环中，对 `IntegratedLLMManager.call_llm_for_role` 的每次调用都**必须**使用一个特定的、符合Paul Graham/Arthur Brooks风格的Prompt。
- 对话**必须**能持续多轮，直到用户输入退出命令或一个被识别为“复杂任务”的指令。

### FR-PA-V3.1-03: 复杂任务处理模式
- 如果意图为“复杂任务”，**必须** 启动一个两阶段的规划流程：
    1.  **意图精炼**: 调用LLM（“秘书”角色）对用户的原始指令进行分析、上下文补充和重构，输出结构化的指令。
    2.  **任务分解**: 调用LLM（“规划师”角色）将结构化的指令分解为一个由**已验证API调用**组成的JSON执行计划。
- **必须** 调用 `TaskManager` 来创建和持久化任务。
- **必须** 异步执行该计划。

### FR-PA-V3.1-04: 任务管理与记忆
- **必须** 为每个复杂任务分配唯一ID，并允许用户查询状态。
- **必须** 将用户的原始指令和每次交互都记录到持久化日志中 (`secretary_log.jsonl`)。
- **必须** 将每个被创建的复杂任务及其状态记录到持久化存储中 (`task_memory.json`)。

## 4. 验收测试用例
- **ATC-PA-V3.1-01: 成功识别并进入闲聊模式**
    - **Given**: 用户在助手界面。
    - **When**: 用户输入 "你对未来有什么看法？"。
    - **Then**: 意图分类器LLM调用**必须**被触发，并返回“闲聊”。
    - **And**: 第二次LLM调用**必须**使用“Paul Graham风格”的Prompt。
    - **And**: 终端**必须**显示一个启发性的、非任务导向的回答。
- **ATC-PA-V3.1-02: 成功识别并执行复杂任务**
    - **Given**: 用户在助手界面。
    - **When**: 用户输入 "用一个批判家和一个支持者的角色辩论一下通用基本收入，然后把结论存起来"。
    - **Then**: 意图分类器LLM调用**必须**被触发，并返回“复杂任务”。
    - **And**: “秘书”角色的LLM调用**必须**被触发以精炼指令。
    - **And**: “规划师”角色的LLM调用**必须**被触发以生成API计划。
    - **And**: `TaskManager.create_task` **必须**被调用。
    - **And**: `MultiRoleDialogueEngine.start_dialogue` **必须**被异步执行。
- **ATC-PA-V3.1-03: 从闲聊切换到复杂任务**
    - **Given**: 用户正处于闲聊模式。
    - **When**: 用户输入 "好了，现在帮我办正事：分析一下最近的AI论文..."。
    - **Then**: 意图分类器LLM调用**必须**被触发，并返回“复杂任务”。
    - **And**: 系统**必须**退出闲聊循环，并启动复杂任务处理流程。
