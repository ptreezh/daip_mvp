# 阶段 1: CLI 基础框架与核心辩论命令 (MVP) - 任务清单

*   **1.1 CLI 基础设置与版本/帮助命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证执行 `python daip-cli.py --version` 和 `python daip-cli.py --help` 时，CLI 能正确显示版本号和帮助信息。
        *   **GREEN:** 在 `daip-cli.py` 和 `src/cli/main.py` 中初始化 Typer 应用，添加版本信息和默认帮助功能。
        *   **REFACTOR:** 优化 CLI 启动逻辑和模块导入，确保 Typer 应用的正确初始化。
*   **1.2 实现 `daip-cli roles` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `src/core_services/role_manager.py` 返回一个预定义的角色列表，并断言 `daip-cli roles` 的输出包含这些角色名称。
        *   **GREEN:** 在 `src/cli/main.py` 中添加 `roles` 命令，调用 `role_manager` 的 `list_roles` 方法，并格式化输出。
        *   **REFACTOR:** 优化角色列表的显示格式，考虑添加角色描述等信息。
*   **1.3 实现 `daip-cli status` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `src/core_services/system_monitor.py` 返回不同组件（LLM, Vector Store）的健康状态（OK/ERROR），并断言 `daip-cli status` 的输出能准确反映这些状态。
        *   **GREEN:** 在 `src/cli/main.py` 中添加 `status` 命令，调用 `system_monitor` 的相关方法，并打印系统健康报告。
        *   **REFACTOR:** 改进状态报告的详细程度和可读性，例如使用颜色区分状态。
*   **1.4 实现 `daip-cli start` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `src/application/debate_service.py` 成功启动辩论，并断言 `daip-cli start "topic" --role "R1" --rounds 3` 等命令能正确执行并输出辩论开始的确认信息。测试不同参数组合和默认值。
        *   **GREEN:** 在 `src/cli/main.py` 中添加 `start` 命令，定义 `topic`, `roles`, `rounds`, `consensus` 和 `output` 参数，并调用 `debate_service` 的 `start_debate` 方法。
        *   **REFACTOR:** 优化参数验证逻辑，确保与后端服务的数据契约一致。