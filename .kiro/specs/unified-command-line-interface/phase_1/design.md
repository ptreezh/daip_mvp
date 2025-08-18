# 阶段 1: CLI 基础框架与核心辩论命令 (MVP) - 设计

*   **框架:** 使用 `typer` 库作为 CLI 框架，主应用入口点为 `daip-cli.py`，核心逻辑在 `src/cli/main.py` 中组织。
*   **模块化:** 将不同功能的 CLI 命令组织到 Typer 的子命令组中（例如 `debate` 组）。
*   **后端集成:**
    *   `roles` 命令将调用 `src/core_services/role_manager.py` 中的 `list_roles` 方法。
    *   `status` 命令将调用 `src/core_services/system_monitor.py` (或类似服务) 中的健康检查逻辑。
    *   `start` 命令将调用 `src/application/debate_service.py` 中的 `start_debate` 方法。
*   **错误处理:** 捕获后端服务异常，并以用户友好的方式通过 CLI 输出错误信息。