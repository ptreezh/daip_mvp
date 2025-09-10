# DAIP-LIVE 项目实施计划

基于对 `GEMINI.md` 和 `docs` 目录结构的分析，项目将采用与工作包（Work Packages）完全对应的分阶段实施计划。

## 核心开发原则

*   **测试驱动开发 (TDD)**：为每个功能模块先编写测试用例，再进行功能实现。
*   **代码质量**：遵循 `pyproject.toml` 中定义的 `ruff` 和 `mypy` 规范，确保代码风格和类型安全。
*   **模块化**：严格按照 P0-P8 的模块划分进行开发，确保高内聚、低耦合。

## 实施阶段详情

| 阶段 | 工作包 (WP) | 核心任务 | 主要产出 | 关联文档 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **P0 & P1** | **核心接口与数据持久化**<br>- 定义所有核心数据模型 (Pydantic Models)<br>- 实现基于 SQLAlchemy 的数据库会话管理<br>- 实现数据模型的CRUD操作 | `src/core/`, `src/persistence/` 模块及单元测试 | `docs/p0_.../`, `docs/p1_.../` |
| 2 | **P2** | **知识库管理器**<br>- 实现文档加载与文本分割<br>- 集成 `faiss-cpu` 和 `langchain` 构建向量存储<br>- 实现知识库的创建、同步和查询接口 | `src/knowledge/` 模块及单元测试 | `docs/p2_.../` |
| 2 | **P-AUX-MEMORY** | **实现内存服务**<br>- 实现三层记忆架构（短期、中期、长期）<br>- 上下文构建与管理策略 | `src/memory/` 模块及单元测试 | `docs/p_aux_memory/README.md` |
| 3 | **P3** | **模型供应器**<br>- 构建与不同 LLM API (本地/云端)交互的工厂类<br>- 统一输入/输出接口<br>- 处理 API 认证和异常 | `src/models/` 模块及单元测试 | `docs/p3_.../` |
| 3 | **P3** | **增强模型供应器：集成LiteLLM Router**<br>- 实现多LLM透明管理（负载均衡、故障转移）<br>- 动态模型选择 | `src/model_provider/` 模块更新，支持多LLM管理 | `docs/p3_model_provider/README.md` |
| 4 | **P4** | **角色与工具管理器**<br>- 定义角色(Persona)的数据结构<br>- 实现工具的动态加载与安全执行管道<br>- 管理工具的输入/输出验证 | `src/roles/`, `src/tools/` 模块及单元测试 | `docs/p4_.../` |
| 5 | **P5** | **Agent 引擎**<br>- 实现核心的“信度驱动状态机”<br>- 编排规划、执行、反思的 Agent 循环<br>- 集成 P1-P4 的所有服务 | `src/agent/` 模块及集成测试 | `docs/p5_.../` |
| 6 | **P6** | **CLI / TUI 接口**<br>- 使用 `Typer` 构建命令行接口<br>- 使用 `Textual` 开发交互式 TUI<br>- 将 CLI/TUI 命令连接到 Agent 引擎 | `src/cli/` 模块及端到端测试 | `docs/p6_.../` |
| 7 | **P7 & P8** | **GUI 与人类助手**<br>- (可选) 使用 `Streamlit` 构建基础的 Web GUI<br>- (可选) 实现人机协作与干预功能 | `src/gui/`, `src/assistant/` 模块 | `docs/p7_.../`, `docs/p8_.../` |
