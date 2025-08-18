# 阶段 1: CLI 基础框架与核心辩论命令 (MVP) - 设计

*   **框架:** 使用 `typer` 库作为 CLI 框架，主应用入口点为 `daip-cli.py`，核心逻辑在 `src/cli/main.py` 中组织。
*   **模块化:** 将不同功能的 CLI 命令组织到 Typer 的子命令组中（例如 `debate` 组）。
*   **后端集成:**
    *   `roles` 命令将调用 `src/core_services/role_manager.py` 中的 `list_roles` 方法。
    *   `status` 命令将调用 `src/core_services/system_monitor.py` (或类似服务) 中的健康检查逻辑。
    *   `start` 命令将调用 `src/application/debate_service.py` 中的 `start_debate` 方法。
*   **错误处理:** 捕获后端服务异常，并以用户友好的方式通过 CLI 输出错误信息。

## 任务 1.3: `daip-cli status` 命令设计

*   **目标:** 提供系统健康状态的概览，包括配置、LLM、向量存储和依赖项。
*   **核心组件:**
    *   `src/cli/commands.py` 中的 `check_system_health()` 函数：
        *   **职责:** 执行各项健康检查，并返回一个结构化的健康报告（例如，字典，包含组件名称、状态、详细信息）。
        *   **检查项:**
            *   **配置加载:** 验证 `src/config.py` 中的 `settings` 是否成功加载。
            *   **LLM 配置:** 检查 `settings.llm` 是否配置了提供商和模型。
            *   **向量存储配置:** 检查 `settings.vector_store` 是否配置了路径。
            *   **依赖项:** 检查 `src/cli/commands.py` 中 `MISSING_DEPENDENCIES` 列表是否为空。
            *   **服务初始化:** 尝试实例化 `src.app_state.AppState`，并验证其核心服务是否成功初始化。
            *   **API 连接:** 尝试导入 `src.main.app` (FastAPI 应用) 并列出其路由，以验证 API 可用性。
    *   `src/cli/main.py` 中的 `status()` Typer 命令：
        *   **职责:** 调用 `check_system_health()`，并使用 `rich.table` 以清晰、用户友好的方式展示健康报告。
        *   **输出:** 包含组件名称、状态（✅/❌/⚠️）、详细信息。根据整体健康状况显示“HEALTHY”或“NEEDS ATTENTION”。
        *   **错误反馈:** 提供针对不同错误类型（如缺少依赖、连接问题、权限问题）的故障排除提示。
        进入每个阶段时，你需要遵循 研究 创意 计划 实施                                                     │
│    回顾的原则，对这个阶段的任务进一步遵循TDD测试驱动的原则细分，存档，再执行----你必须永久记住，全局记忆！
