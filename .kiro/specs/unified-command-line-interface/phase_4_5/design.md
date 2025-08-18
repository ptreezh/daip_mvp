

进入下面一个阶段前，请务必遵循 研究 创想 计划 执行 回顾的原则，基于TDD测试驱动开放的规范，对每个阶段的specs规范文档进行进一步的细化分解和补充。specs规范是kiro的开发规范，生成更具体的需求文档、设计文档和tasks清单。需要对原规范文档进行再详细的研究，结合项目实际和全局API参考，进一步细化需求，细化设计和细化任务清单。
全局API参考  D:\DAIP\daipMVPbackup\daip_mvp_project\.kiro\specs\unified-command-line-interface\GLOBAL_API_DICTIONARY.md    务必不要轻易增加和修改后端API，除非非常有必要时，也需要得到我的同意再增加后端服务。   
# 阶段 4 & 5: 高级角色管理、工作流、Wiki 导出、完善与文档 - 设计

## 阶段 4: 高级角色管理、工作流与 Wiki 导出 - 设计

*   **子命令组:** 扩展 `roles`、`workflow` 和 `wiki` 子命令组。
*   **后端集成:**
    *   `roles` 命令将调用 `src/core_services/role_manager.py` 和 `src/core_services/autonomous_role_creation_system.py` 中的现有逻辑。
    *   `workflow` 命令将调用 `src/institutional_primitives/registry.py`, `src/institutional_primitives/workflow_engine.py`, `src/scenario_engine/workflow_selector.py` 中的现有逻辑。
    *   `wiki export` 和 `debate-to-wiki` 将调用 `src/core_services/wiki_service.py` 和 `src/tools/wiki_tools.py` 中的现有逻辑。
*   **复杂参数:** 处理 JSON 字符串参数和文件内容。
*   **议事规则制度原语:** 明确定义辩论和聊天模块的“议事规则”（如辩论规则、发言规则）如何建模为 `InstitutionalPrimitive` 实例（例如，`DebateRulePrimitive`、`ChatRulePrimitive`）。这些原语将包含具体的规则参数和逻辑。

## 阶段 5: 完善、错误处理与文档 - 设计

*   **帮助系统:** 利用 Typer 的内置帮助文档生成能力，为每个命令和参数提供详细描述。
*   **全局错误处理:** 实现一个中央错误处理机制，捕获并统一处理来自后端服务和 CLI 内部的异常。
*   **输入验证:** 在 CLI 层面进行初步的参数验证，提供即时反馈。
*   **文档:** 更新 `README.md`、`GEMINI.md` 和其他相关文档，包含所有 CLI 命令的最新用法和示例。
*   **代码质量:** 确保 `ruff.toml` 配置正确，并在开发流程中强制执行代码风格和质量检查。
