# 阶段3：协同协议逻辑实现 - 详细技术方案

本文档基于 `OVERALL_IMPLEMENTATION_PLAN.md`，为阶段3的实施提供详细的技术方案和任务分解。

## 1. 总体技术方案

协同协议是驱动核心服务（`core_services`）来完成复杂业务流程的“大脑”。

*   **实现方式**：每个协议（如辩论、敏捷项目）将被实现为一个独立的、有状态的Python类。
*   **文件位置**：所有协议类都将存放在 `src/protocols/` 目录下。
*   **生命周期**：协议实例由 `WorkflowManager` 根据用户指令（如 `!debate`）创建和管理，并与一个特定的 `session_id` 绑定。
*   **交互模型**：协议类将通过依赖注入的方式接收 `core_services` 的实例，并调用它们的方法来读写持久化数据（如任务、知识、记忆）。
*   **异步优先**：所有涉及I/O（特别是LLM调用）的操作都必须是异步的 (`async/await`)，以确保系统的高性能和响应能力。

---

## 2. 任务分解与技术细节

### 子阶段 3.1: 辩论与共识协议 (`DebateProtocol`)

此协议旨在模拟一个多角色辩论过程，并最终达成共识。

*   **新文件**: `daip_mvp_project/src/protocols/debate_protocol.py`
*   **核心类**: `DebateProtocol`
    ```python
    class DebateProtocol:
        def __init__(self, session_id: str, role_manager: RoleManager, memory_service: MemoryService, synthesis_engine: SynthesisEngine, wiki_service: WikiService):
            # ... 初始化 ...

        async def start_debate(self, topic: str, role_ids: list[str]):
            # ... 启动辩论 ...

        async def handle_message(self, message: str) -> str:
            # ... 处理用户或角色的下一轮发言 ...

        async def _detect_disagreement(self) -> bool:
            # ... 检测分歧 ...

        async def _run_consensus_vote(self) -> dict:
            # ... 运行共识投票 ...
    ```

#### **原子计划 3.1.1: 实现分歧检测逻辑**
*   **技术方案**:
    1.  在每次角色发言后，从 `MemoryService` 中获取最近的两次不同角色的发言。
    2.  调用LLM，使用一个专门的Prompt来判断这两次发言是否存在逻辑冲突或观点分歧。
    3.  Prompt应要求LLM以JSON格式返回结果，例如：`{"conflict": true, "reason": "Statement A focuses on economic benefits, while Statement B highlights ethical risks, presenting a direct conflict in priorities."}`。
    4.  根据返回结果，协议可以改变内部状态，例如进入“反驳”或“澄清”阶段。
*   **依赖**: `MemoryService`, LLM接口。

#### **原子计划 3.1.2: 实现辩论轮次控制和角色调度**
*   **技术方案**:
    1.  在 `DebateProtocol` 内部维护一个状态机，记录当前辩论阶段（如 `opening`, `argument`, `rebuttal`）、当前轮次和下一个发言的角色。
    2.  角色调度可以从简单的轮询（Round-robin）开始。
    3.  `handle_message` 方法将驱动状态机前进：确定当前发言角色 -> 构建Prompt -> 调用LLM -> 使用 `MemoryService` 保存发言 -> 更新状态以准备下一轮。
*   **依赖**: `RoleManager`, `MemoryService`。

#### **原子计划 3.1.3: 实现共识投票机制**
*   **技术方案**:
    1.  当辩论达到预设的结束条件（如最大轮次）时，触发共识投票。
    2.  调用 `SynthesisEngine` 生成对辩论正反方关键论点的总结。
    3.  将总结呈现给所有参与辩论的AI角色，并要求它们对一个明确的议题进行投票（例如：“你是否同意采纳方案A？”）。
    4.  每个角色的投票结果（同意/反对/中立）及其理由，可以作为一个提案（Proposal）写入 `WikiService`，以实现持久化和可追溯。
    5.  统计投票结果，得出最终共识。
*   **依赖**: `SynthesisEngine`, `WikiService`, `MemoryService`。

---

### 子阶段 3.2: 敏捷项目协议 (`AgileProtocol`)

此协议旨在自动化敏捷项目中的任务分解流程。

*   **新文件**: `daip_mvp_project/src/protocols/agile_protocol.py`
*   **核心类**: `AgileProtocol`
    ```python
    class AgileProtocol:
        def __init__(self, session_id: str, task_manager: TaskManager, role_manager: RoleManager):
            # ... 初始化 ...

        async def start_decomposition(self, high_level_task: str):
            # ... 开始任务分解 ...

        async def confirm_decomposition(self, user_confirmation: bool):
            # ... 处理用户确认 ...
    ```

#### **原子计划 3.2.1: 实现 `!decompose` 命令的引导式任务分解流程**
*   **技术方案**:
    1.  当 `WorkflowManager` 收到 `!decompose "一个复杂的任务"` 命令时，实例化并调用 `AgileProtocol.start_decomposition`。
    2.  协议首先通过 `RoleManager` 加载一个“任务分解大师”角色。
    3.  调用LLM，使用“任务分解大师”的Prompt，将高级任务分解为一个结构化的子任务列表。每个子任务应包含`title`, `description`, 和 `dependencies`。
    4.  将生成的任务列表暂存（例如，在 `memory_bank/sessions/{session_id}/` 下创建一个临时的 `decomposition_proposal.json` 文件），并将协议状态设置为 `PENDING_CONFIRMATION`。
*   **依赖**: `RoleManager`, `TaskManager`, LLM接口。

#### **原子计划 3.2.2: 实现任务分解后的人类确认（Human-in-the-Loop）环节**
*   **技术方案**:
    1.  在协议状态为 `PENDING_CONFIRMATION` 时，系统等待用户发出 `!confirm_decomposition` 或 `!reject_decomposition` 命令。
    2.  `AgileProtocol.confirm_decomposition` 方法处理该命令。
    3.  如果确认，协议将读取暂存的 `decomposition_proposal.json` 文件，并循环调用 `TaskManager.create_task` 将所有任务持久化。
    4.  如果拒绝，协议将删除临时文件并重置状态。
*   **依赖**: `TaskManager`。

---

### 子阶段 3.3: 工作流管理器集成

此阶段的目标是让 `WorkflowManager` 能够真正地驱动和管理上述协议。

*   **修改文件**: `daip_mvp_project/src/protocols/workflow_manager.py`

#### **原子计划 3.3.1: 在 `WorkflowManager` 中实现完整的状态转换逻辑**
*   **技术方案**:
    1.  增强 `handle_event` 方法，使其能解析收到的命令（如 `!debate`, `!decompose`）。
    2.  根据命令，调用 `_transition_to` 方法，更新会话的宏观状态（`SystemState`）。例如，收到 `!debate` 后，状态从 `IDLE` 变为 `DEBATE_IN_PROGRESS`。
*   **依赖**: `SystemState` 枚举。

#### **原子计划 3.3.2: 在 `WorkflowManager` 中实例化并调用相应的协议模块**
*   **技术方案**:
    1.  `WorkflowManager` 在 `__init__` 时，需要被注入所有核心服务的实例。
    2.  在 `_transition_to` 方法中，当进入一个新状态时，`WorkflowManager` 会实例化对应的协议类，并将所需的服务实例传递给它。
        ```python
        # 在 WorkflowManager 中
        if new_state == SystemState.DEBATE_IN_PROGRESS:
            self.active_protocol = DebateProtocol(self.session_id, self.role_manager, ...)
            await self.active_protocol.start_debate(...)
        ```
    3.  后续的用户消息或命令将被委托给 `self.active_protocol` 进行处理。
*   **依赖**: `DebateProtocol`, `AgileProtocol`, 所有 `core_services`。

---

## 3. API 端点集成

*   **修改文件**: `daip_mvp_project/src/main.py`
*   **技术方案**:
    1.  FastAPI应用启动时，需要创建一个全局的会话管理器，用于存储所有活跃的 `WorkflowManager` 实例（例如，一个字典 `dict[str, WorkflowManager]`）。
    2.  `/sessions/{session_id}/command` 和 `/sessions/{session_id}/chat` 端点将是主要入口。
    3.  这些端点会根据 `session_id` 查找或创建对应的 `WorkflowManager` 实例，并调用其 `handle_event` 方法，将用户命令或消息传递进去。

---

## 4. 测试策略

1.  **单元测试**: 为 `DebateProtocol` 和 `AgileProtocol` 编写独立的单元测试，使用Mock对象模拟核心服务，验证其内部状态转换和逻辑的正确性。
2.  **集成测试**: 编写集成测试，覆盖从API端点 -> `WorkflowManager` -> 具体协议 -> 核心服务的完整调用链，验证端到端功能的正确性。