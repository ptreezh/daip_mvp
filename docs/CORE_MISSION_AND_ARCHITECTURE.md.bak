# DAIP-MVP 核心使命与系统架构

## 1. 核心使命

本项目的核心使命是：**构建一个具备动态协同辩论与自动化敏捷项目执行能力的 DAIP-LIVE 系统，并重点验证基于本地小模型的社会化工程幻觉抑制效果。**

我们致力于通过以下方式实现这一使命：

*   **多角色协同**: 模拟一个由多个具有不同专长和视角的AI角色组成的团队，通过对话、辩论和协作来解决复杂问题。
*   **幻觉抑制**: 利用社会化工程（多角色审查、对抗性辩论、共识机制）来识别、挑战和抑制单一模型可能产生的幻觉。
*   **工程可用性**: 确保所有核心功能都通过稳定、可测试的后端服务和API提供，遵循CLI优先的开发哲学。
*   **可扩展性**: 设计一个模块化、分层的架构，便于未来功能的扩展和新技术的集成。

## 2. 系统架构

系统采用分层架构，确保高内聚、低耦合。

```mermaid
graph TD
    subgraph Layer_A [应用层 (Application Layer)]
        CLI_Interface[CLI Interface]
        Web_API[Web API (FastAPI)]
    end

    subgraph Layer_B [协同协议层 (Protocol Layer)]
        WorkflowManager[Workflow Manager (State Machine)]
        AgileProtocol[Agile Project Protocol]
        DebateProtocol[Debate & Consensus Protocol (Enhanced for Hallucination)]
    end

    subgraph Layer_C [核心服务层 (Core Services Layer)]
        RoleManager[Role Manager]
        TaskManager[Task Manager (DAG-aware)]
        WikiService[Wiki Service (Versioned)]
        MemoryService[Memory Service (Integrated with SSKG)]
        SynthesisEngine[Synthesis Engine (System Synthesizer)]
    end

    subgraph Layer_D [基础内核层 (Kernel Layer)]
        Scheduler[LLM Scheduler (Time-sharing)]
        ToolExecutor[Unified Tool Executor]
        LLM_Interface[LLM Interface (Local/Cloud)]
        ContextSegmenter[Context Segmenter & Summarizer]
    end

    CLI_Interface --> Web_API
    Web_API --> WorkflowManager

    WorkflowManager -- "triggers" --> AgileProtocol
    WorkflowManager -- "triggers" --> DebateProtocol

    AgileProtocol -- "uses" --> TaskManager
    DebateProtocol -- "uses" --> RoleManager
    DebateProtocol -- "uses" --> WikiService
    DebateProtocol -- "uses" --> SynthesisEngine

    RoleManager --> MemoryService
    TaskManager --> MemoryService
    WikiService --> MemoryService
    SynthesisEngine --> MemoryService

    MemoryService -- "interacts with" --> Scheduler
    Scheduler -- "calls" --> ToolExecutor
    Scheduler -- "calls" --> LLM_Interface
    LLM_Interface -- "uses" --> ContextSegmenter
    ContextSegmenter -- "provides context" --> LLM_Interface

    style Layer_A fill:#D6EAF8,stroke:#333
    style Layer_B fill:#D1F2EB,stroke:#333
    style Layer_C fill:#FEF9E7,stroke:#333
    style Layer_D fill:#FDEDEC,stroke:#333
```

### 组件职责

*   **应用层 (Application Layer)**:
    *   **CLI Interface**: 提供命令行界面，用于与系统进行交互，是MVP阶段的主要入口。
    *   **Web API (FastAPI)**: 提供所有功能的HTTP接口，是CLI和未来Web UI的统一入口。

*   **协同协议层 (Protocol Layer)**:
    *   **Workflow Manager**: 系统主状态机，管理系统在`IDLE`, `PROJECT_EXECUTION`, `DEBATE_IN_PROGRESS`等宏观状态之间切换。它负责接收来自协议层（如 `DebateProtocol`）的执行结果，并根据当前工作流决定下一步行动（例如，将辩论共识转化为一个新任务）。
    *   **Agile Project Protocol**: 实现敏捷项目管理的逻辑，如引导式任务分解。
    *   **Debate & Consensus Protocol**: 实现一个**可配置的**、基于参数化模板的辩论流程（如轮次、发言顺序）。它负责编排整个辩论的生命周期，包括角色调度、意见收集和最终的综合。**它不直接实现共识算法，而是通过调用 `ToolExecutor` 来执行一个可选择的共识策略（如简单投票）**，从而实现业务逻辑与共识机制的解耦。

*   **核心服务层 (Core Services Layer)**:
    *   **Role Manager**: 负责加载、管理和分配AI角色及其对应的Prompt和能力。
    *   **Task Manager (DAG-aware)**: 负责创建、管理和追踪具有依赖关系的任务。
    *   **Wiki Service (Versioned)**: 提供版本化的知识库服务，用于记录和管理项目知识。
    *   **Memory Service (Integrated with SSKG)**: 提供统一的记忆服务，管理角色的短期记忆、长期记忆，并集成语义结构化知识图谱（SSKG）以进行事实核查。
    *   **Synthesis Engine (System Synthesizer)**: 负责在辩论结束后，综合各方观点，生成结构化的、高质量的总结意见。
Fact Extraction Service: （新增） 使用LLM从对话中自动提取结构化事实，并根据置信度进行初步筛选，然后存入MemoryService的暂存区。
Fact Validation Service: （新增） 提供业务逻辑，允许人工或自动化流程审核暂存区中的事实，并将批准的事实正式提交到SSKG中。
*   **基础内核层 (Kernel Layer)**:
    *   **LLM Scheduler**: 负责LLM资源的分时复用和任务调度。
    *   **Unified Tool Executor**: 提供统一的工具调用执行能力。它不仅能调用外部工具（如文件操作），**还能将内部核心能力（如 `ConsensusStrategy`、`TaskManager` 的操作）封装为可供协议调用的工具**，实现了系统各层级间的松耦合调用。
    *   **LLM Interface**: 封装与本地或云端大语言模型的交互接口。
    *   **Context Segmenter & Summarizer**: 负责处理长上下文，通过分段和摘要来解决LLM的上下文窗口限制。
