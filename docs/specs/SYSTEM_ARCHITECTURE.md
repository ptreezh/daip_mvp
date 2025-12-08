# 系统架构规格

---

## 1. 核心结论 (Answer First)

本系统采用**模块化的单体应用架构**，专为本地单用户环境设计，以实现最高性能和最强隐私保护。其核心是一个**动态的、事件驱动的Agent执行引擎**，而非静态的工作流系统。所有服务通过直接的Python调用进行通信，以避免网络延迟。

*   **架构选择**: 模块化单体 (Modular Monolith)
*   **核心模型**: 动态Agent执行循环 (Dynamic Agent Loop)
*   **通信方式**: 本地函数调用 (Local Function Calls)

> 本架构设计旨在直接服务于[主控文档](./../MAIN_CONTROL_DOCUMENT.md)中定义的“本地优先、过程透明、可被驾驭”的核心目标。

---

## 2. 架构设计原则

*   **简单性 (KISS)**: 避免引入微服务、容器化、分布式消息队列等对于单机应用而言过于复杂的组件，以降低维护成本和潜在的故障点。
*   **响应性 (Responsiveness)**: 所有组件必须设计为异步兼容，确保UI/TUI能够实时响应用户输入和Agent状态变化，不被后台任务阻塞。
*   **可扩展性 (Extensibility)**: 通过清晰的接口定义（见P0）和依赖注入，允许系统轻松替换或添加新的服务（如模型提供者、工具）。

---

## 3. 系统分层与数据流

系统在逻辑上分为三层，数据和控制流自上而下传递。

```mermaid
graph TD
    subgraph 用户界面层 (P6, P7)
        A[CLI / TUI / GUI]
    end

    subgraph 核心逻辑层 (P5, P8, P4)
        B(Agent / Workflow Engine)
        C(Role & Tool Manager)
    end

    subgraph 基础服务层 (P1, P2, P3)
        D(Data Persistence)
        E(Knowledge Manager)
        F(Model Provider)
    end

    A -- User Goal / Command --> B
    B -- Uses --> C
    B -- Uses --> D
    B -- Uses --> E
    B -- Uses --> F
```

1.  **用户界面层 (UI Layer)**: 负责接收用户指令，并渲染由核心逻辑层产生的事件流。这是系统的“五官”。
2.  **核心逻辑层 (Logic Layer)**: 系统的“大脑”。`AgentEngine` (P5) 在此层运行其状态机，通过`RoleManager`和`ToolManager` (P4) 决定使用何种身份和能力，并可由`WorkflowOrchestrator` (P8) 进行更高层次的编排。
3.  **基础服务层 (Service Layer)**: 提供具体的、独立的“基础能力”，如数据库访问 (P1)、知识检索 (P2) 和模型调用 (P3)。它们被动地响应逻辑层的调用。

---

## 4. 关键组件规格

### 4.1 Agent执行引擎 (P5)
- **职责**: 实现一个异步的、事件驱动的状态机，管理单个Agent的完整生命周期。
- **输入**: 一个高阶目标 (goal)。
- **输出**: 一个异步事件流 (`AsyncGenerator[AgentEvent, None]`)。

### 4.2 异步消息队列
- **职责**: 解耦UI层和逻辑层，实现用户对正在运行的Agent的实时“驾驭”。
- **实现**: UI层将用户输入放入一个标准的`asyncio.Queue`。该队列在`AgentEngine`启动时被注入。`AgentEngine`在其状态机的每个循环开始时，都会非阻塞地检查此队列，以决定是否需要改变计划。

### 4.3 依赖注入
- **职责**: 在应用启动时，集中实例化所有服务和管理器，并将其注入到需要它们的组件中。
- **实现**: 可通过一个简单的`ServiceContainer`类或使用`dependency-injector`等库来实现。