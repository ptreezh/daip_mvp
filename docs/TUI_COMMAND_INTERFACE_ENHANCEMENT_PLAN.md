# TUI 命令系统增强计划

## 1. 概述

本文档旨在将当前的TUI命令系统，从一个基本的命令执行器，升级为一个智能、易用、上下文感知的交互界面，其设计参考了 Gemini CLI 的高级命令模式。

核心目标是填补后台服务能力与前端用户体验之间的巨大鸿沟，将已实现的后台功能完整、友好地呈现给用户。

## 2. 目标用户体验 (Target UX)

1.  **命令自动补全**: 用户输入 `/` 时，自动弹出所有可用主命令的列表。
2.  **上下文帮助**: 列表中每个命令都附有简短的用途说明。
3.  **参数自动补全**: 当用户输入一个需要参数的命令时（如 `/role view `），系统会自动弹出第二个列表，其中包含所有可用的参数选项（如所有角色的名字）。用户可以从中选择，而无需手动输入。
4.  **清晰的结果呈现**: 命令执行后，结果（无论是列表、对象详情还是状态信息）都将以格式化、易于阅读的方式呈现在主日志区域。

## 3. 功能审计与命令规格总表

| TUI 命令 | 参数 | 后台方法 | 后台状态 | TUI 实现状态 | 参数自动补全 | 实施优先级 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/role list` | (无) | `RoleManager.list_roles()` | **缺失** | **已实现** | 不适用 | 1 |
| `/role view` | `<name>` | `RoleManager.get_role_by_name(name)` | **可用** | **已实现** | **是** (角色列表) | 2 |
| `/session list` | (无) | `SessionManager.list_sessions()` | **可用** | **已实现** | 不适用 | 3 |
| `/session view` | `<id>` | `SessionManager.get_session(id)` | **可用** | **已实现** | **是** (会话列表) | 4 |
| `/knowledge sync` | (无) | `KnowledgeManager.sync_knowledge_base()` | **可用** | **已实现** | 不适用 | 5 |
| `/knowledge search`| `<query>` | `KnowledgeManager.search(query)` | **可用** | **已实现** | 否 | 6 |
| `/pa` | `<goal>` | `AgentExecutor` | **可用** | **已实现** | 否 | - |
| `/help` | (无) | (TUI内置) | **可用** | **已实现** | 不适用 | - |
| `/quit` | (无) | `app.exit()` | **可用** | **已实现** | 不适用 | - |

## 4. 实施计划 (TDD 驱动)

我们将遵循TDD原则，以命令为单位，逐一进行迭代开发。

### 迭代 1: 实现 `/role` 命令

*   **任务 1.1 (后台增强)**: 
    *   **目标**: 为 `RoleManager` 添加 `list_roles()` 方法。
    *   **TDD**: 先为 `list_roles()` 编写测试，然后实现该方法。

*   **任务 1.2 (TUI 实现 `/role list`)**:
    *   **RED**: 编写测试，断言执行 `/role list` 后，TUI日志中会打印出格式化的角色列表。
    *   **GREEN**: 修改 `_handle_role_command`，使其能解析 `list` 子命令，并调用 `role_manager.list_roles()` 接口获取数据、格式化输出。
    *   **REFACTOR**: 重构代码。

*   **任务 1.3 (TUI 实现 `/role view` 参数补全)**:
    *   **RED**: 编写测试，模拟用户输入 `/role view `，断言自动补全窗口会弹出，并包含所有可用的角色名称。
    *   **GREEN**: 增强 `on_input_changed` 逻辑，当识别到 `/role view ` 时，调用 `role_manager.list_roles()` 获取角色列表并更新自动补全窗口。
    *   **REFACTOR**: 重构代码。

*   **任务 1.4 (TUI 实现 `/role view` 执行)**:
    *   **RED**: 编写测试，模拟用户选择一个角色并执行命令，断言TUI日志中会显示该角色的详细信息。
    *   **GREEN**: 实现命令的最终执行逻辑。
    *   **REFACTOR**: 重构代码。

### 迭代 2: 实现 `/session` 命令 (及后续迭代)

后续的 `/session` 和 `/knowledge` 命令将遵循与 `/role` 类似的TDD开发流程，直至所有命令都实现完毕。
