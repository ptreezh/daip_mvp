# 整体项目计划：DAIP-LIVE MVP 实施方案

本计划旨在将 DAIP-LIVE MVP 从概念和骨架阶段，推进到功能完备、可测试的系统。

---

### **阶段 1: 文档与骨架搭建 (已完成)**

此阶段的目标是为项目奠定坚实的理论和结构基础。

*   **1.1. 核心架构定义 (已完成)**: 在 `docs/CORE_MISSION_AND_ARCHITECTURE.md` 中明确了系统的核心使命和分层架构。
*   **1.2. 项目入口说明 (已完成)**: 在 `README.md` 中更新了项目概览，明确了 MVP 范围和“CLI优先，后端先行”的开发哲学。
*   **1.3. 用户场景定义 (已完成)**: 在 `docs/cases/multi_role_debate_mvp_scenarios.md` 中详细描述了用户画像、故事和交互流程。
*   **1.4. 测试策略制定 (已完成)**: 在 `docs/testing/mvp_debate_test_plan.md` 中为 MVP 阶段的测试提供了详细指导。
*   **1.5. API 接口骨架 (已完成)**: 在 `src/main.py` 中搭建了所有 FastAPI 端点，并返回 mock 数据。
*   **1.6. 核心服务骨架 (已完成)**: 在 `src/core_services/` 目录下创建了所有服务类的接口定义。
*   **1.7. 协同协议骨架 (已完成)**: 在 `src/protocols/` 目录下创建了 `WorkflowManager` 的状态机骨架。
*   **1.8. 基础内核骨架 (已完成)**: 在 `src/kernel/` 目录下创建了 `ContextSegmenter` 的接口定义。

---

### **阶段 2: 核心服务实现**

此阶段的目标是将骨架代码填充为具备文件持久化和核心业务逻辑的功能模块。

*   **子阶段 2.1: TaskManager 功能增强 (已完成)**
    *   **原子计划 2.1.1**: 在 `task_manager.py` 中，实现 `update_task_status` 方法，使其能够读写任务文件的 `status` 字段。(已完成)
    *   **原子计划 2.1.2**: 在 `task_manager.py` 中，实现 `get_ready_tasks` 方法，使其能够根据依赖关系返回可执行的任务列表。(已完成)
    *   **原子计划 2.1.3**: 在 `task_manager.py` 中，实现 `get_task_context` 方法，使其能够递归聚合所有依赖项的交付物内容。(已完成)
*   **子阶段 2.2: WikiService 功能增强 (已完成)**
    *   **原子计划 2.2.1**: 在 `wiki_service.py` 中，重构 `create_entry` 方法，实现基于文件系统的版本化存储。(已完成)
    *   **原子计划 2.2.2**: 在 `wiki_service.py` 中，重构 `propose_edit` 方法，以创建 JSON 格式的编辑提案文件。(已完成)
    *   **原子计划 2.2.3**: 在 `wiki_service.py` 中，重构 `get_entry` 方法，使其从文件系统读取条目内容。(已完成)
    *   **原子计划 2.2.4**: 在 `wiki_service.py` 中，添加 `_apply_proposal` 私有方法，用于应用提案并创建新版本。(已完成)
*   **子阶段 2.3: MemoryService 创建与实现 (已完成)**
    *   **原子计划 2.3.1**: 创建新文件 `daip_mvp_project/src/core_services/memory_service.py`。(已完成)
    *   **原子计划 2.3.2**: 在 `memory_service.py` 中，实现 `save_message` 方法，以 JSONL 格式追加对话历史。(已完成)
    *   **原子计划 2.3.3**: 在 `memory_service.py` 中，实现 `get_history` 方法，以从日志文件中读取完整的对话历史。(已完成)
*   **原子计划 2.3.4**: 在 `MemoryService` 中实现事实暂存区 (`pending_facts` 表)，用于存储待审核的事实，为人工审核（Human-in-the-Loop）提供支持。(已完成)

*   **子阶段 2.4: RoleManager 功能增强 (已完成)**
    *   **原子计划 2.4.1**: 在 `role_manager.py` 中，实现从配置文件（如 YAML 或 JSON）加载角色定义。(已完成)
    *   **原子计划 2.4.2**: 在 `role_manager.py` 中，实现 `get_role_by_id` 方法，以获取特定角色的完整信息（Prompt、能力等）。(已完成)
    *   **原子计划 2.4.3**: 在 `role_manager.py` 中，实现 `list_roles` 方法，以返回所有可用角色的列表。(已完成)

*   **子阶段 2.5: Synthesis Engine 实现 (已完成)**
    *   **原子计划 2.5.1**: 创建新文件 `src/core_services/synthesis_engine.py`。(已完成)
    *   **原子计划 2.5.2**: 在 `synthesis_engine.py` 中，实现 `synthesize_opinions` 方法，该方法接收多个观点文本。(已完成)
    *   **原子计划 2.5.3**: 实现调用 `LLM Interface` 生成综合性总结的逻辑 (依赖于阶段 3 的 `LLM Interface`)。(已完成)
*   **子阶段 2.6: Fact Extraction & Validation Service 实现 (新增, 已完成)**
    *   **原则**: 建立一个从非结构化对话中自动捕获、筛选和验证结构化知识的管道。
    *   **原子计划 2.6.1**: 创建 `FactExtractionService`，使用 LLM 从对话中提取 (主体, 谓词, 对象, 置信度) 事实四元组。(已完成)
    *   **原子计划 2.6.2**: 实现基于置信度阈值的自动过滤机制，低置信度事实被自动标记为 `rejected`，高置信度事实进入 `pending` 队列。(已完成)
    *   **原子计划 2.6.3**: 创建 `FactValidationService`，提供审核、批准、拒绝暂存事实的业务逻辑。(已完成)
    *   **原子计划 2.6.4**: 在 `MemoryService` 中实现 `approve_fact` 方法，在事实被批准后，将其从暂存区正式移入 SSKG 知识图谱中。(已完成)


---

### **阶段 3: 基础内核层实现 (已完成)**

此阶段的目标是实现与大语言模型交互和管理长上下文的核心能力。

*   **子阶段 3.1: LLM Interface 实现 (已完成)**
    *   **原子计划 3.1.1**: 在 `src/kernel/llm_interface.py` 中，实现一个可插拔的 LLM 接口，支持至少一种本地模型（如 Ollama）和一种云端模型（如 OpenAI API）。(已完成)
    *   **原子计划 3.1.2**: 定义统一的输入（Prompt、配置）和输出（文本、结构化数据）格式。(已完成)
*   **子阶段 3.2: Interaction Manager 实现 (已完成)**
    *   **原则**: 此模块将遵循“技术遗产全覆盖原则”，完整地、健壮地重构 `src/vendor/old/lim.py` 中包含的核心上下文管理功能。(已完成)
    *   **原子计划 3.2.1**: 创建新文件 `src/kernel/interaction_manager.py`。(已完成)
    *   **原子计划 3.2.2**: 在 `InteractionManager` 中实现核心处理流程，该流程将编排 `LLMInterface`, `MemoryService`, `WikiService`, 和 `SynthesisEngine`。(已完成)
    *   **原子计划 3.2.3**: 实现 RAG 逻辑，通过调用 `WikiService` 检索相关知识。(已完成)
    *   **原子计划 3.2.4**: 实现长上下文自动压缩逻辑，当上下文超过阈值时，调用 `SynthesisEngine` 对历史对话进行总结。(已完成)
    *   **原子计划 3.2.5**: 实现最终 Prompt 的构建逻辑，将角色指令、RAG 结果、对话历史和用户输入整合在一起。(已完成)
*   **子阶段 3.3: Unified Tool Executor 实现 (已完成)**
    *   **原子计划 3.3.1**: 在 `src/kernel/tool_executor.py` 中，实现一个工具注册表，允许动态加载和验证工具。(已完成)
    *   **原子计划 3.3.2**: 实现一个安全的执行器，能够根据 LLM 的请求调用已注册的工具并返回结果。(已完成)
*   **子阶段 3.4: LLM Scheduler 实现 (已完成)**
    *   **原子计划 3.4.1**: 在 `src/kernel/llm_scheduler.py` 中，设计一个任务队列来管理并发的 LLM 请求。(已完成)
    *   **原子计划 3.4.2**: 实现一个基础的调度策略（如 FIFO 或基于优先级的调度）。(已完成)

---

### **阶段 4: 协同协议逻辑实现 (当前计划)**

此阶段的目标是实现驱动核心服务的业务流程。

*   **子阶段 4.1: 辩论与共识协议 (部分完成)**
    *   **原子计划 4.1.1**: 在 `ProtocolService` 中实现 `run_debate` 方法，通过 `DebateProtocol` 编排辩论流程。(已完成)
    *   **原子计划 4.1.2**: 实现可插拔的共识策略（如 `SimpleMajorityVoteStrategy`），并通过 `UnifiedToolManager` 注册为可执行工具。(已完成)
    *   **原子计划 4.1.3**: 实现辩论轮次控制和角色调度。(进行中)
*   **子阶段 4.2: 敏捷项目与协同协议 (部分完成)**
    *   **原子计划 4.2.1**: 在 `CollaborationService` 中实现任务的创建、查询和更新逻辑。(已完成)
    *   **原子计划 4.2.2**: 在 `CollaborationService` 中实现 Wiki 的版本化读写逻辑。(已完成)
    *   **原子计划 4.2.3**: 实现引导式任务分解流程。(未来计划)
*   **子阶段 4.3: 虚拟团队引擎 (新增, 已完成)**
    *   **原子计划 4.3.1**: 实现 `VirtualTeamService`，用于管理虚拟项目、任务分配和角色上下文。(已完成)
    *   **原子计划 4.3.2**: 将项目记忆存储在独立的 `MemoryBank` 中，实现项目知识的隔离。(已完成)
*   **子阶段 4.4: 工作流管理器集成 (未来计划)**
    *   **原子计划 4.4.1**: 在 `WorkflowManager` 中实现完整的状态转换逻辑。
    *   **原子计划 4.4.2**: 在 `WorkflowManager` 中实例化并调用相应的协议模块。



---

### **阶段 5: CLI 与集成测试 (未来计划)**

此阶段的目标是提供一个可用的用户界面并确保端到端功能的正确性。

*   **子阶段 5.1: CLI 客户端开发**
    *   **原子计划 5.1.1**: 开发用于发起和管理辩论的 CLI 命令。
    *   **原子计划 5.1.2**: 实现对 SSE 实时事件流的处理和显示。
    *   **原子计划 5.1.3**: 开发用于任务管理的 CLI 命令。
*   **子阶段 5.2: 端到端集成测试**
    *   **原子计划 5.2.1**: 编写并执行覆盖完整辩论场景的集成测试。
    *   **原子计划 5.2.2**: 编写并执行覆盖任务分解场景的集成测试。
    *   **原子计划 5.2.3**: 编写并执行幻觉抑制专项测试用例。
