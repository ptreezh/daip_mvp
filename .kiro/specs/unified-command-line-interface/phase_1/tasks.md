# 阶段 1: CLI 基础框架与核心辩论命令 (MVP) - 任务清单

*   **1.1 CLI 基础设置与版本/帮助命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证执行 `python daip-cli.py --version` 和 `python daip-cli.py --help` 时，CLI 能正确显示版本号和帮助信息。
        *   **GREEN:** 在 `daip-cli.py` 和 `src/cli/main.py` 中初始化 Typer 应用，添加版本信息和默认帮助功能。
        *   **REFACTOR:** 优化 CLI 启动逻辑和模块导入，确保 Typer 应用的正确初始化。
# 阶段 1: CLI 基础框架与核心辩论命令 (MVP) - 任务清单

*   **1.1 CLI 基础设置与版本/帮助命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证执行 `python daip-cli.py --version` 和 `python daip-cli.py --help` 时，CLI 能正确显示版本号和帮助信息。
        *   **GREEN:** 在 `daip-cli.py` 和 `src/cli/main.py` 中初始化 Typer 应用，添加版本信息和默认帮助功能。
        *   **REFACTOR:** 优化 CLI 启动逻辑和模块导入，确保 Typer 应用的正确初始化。
*   **1.2 实现 `daip-cli roles` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 `daip-cli roles` 命令在无角色和有角色情况下的输出。
        *   **GREEN:** 在 `src/cli/commands.py` 中实现 `list_available_roles` 函数，并在 `src/cli/main.py` 中定义 `roles` 命令，调用该函数并展示结果。
        *   **REFACTOR:** 确保 `RoleManager` 正确初始化，改进输出格式和错误处理。

## 任务 1.3: 实现 `daip-cli status` 命令

*   **TDD Cycle (整体):**
    *   **RED:** 编写测试用例 `test_cli_status_command_healthy` 和 `test_cli_status_command_unhealthy`，模拟不同系统健康状态，并断言 CLI 输出符合预期。
    *   **GREEN:** 实现 `status` 命令的核心功能，使测试通过。
    *   **REFACTOR:** 优化健康检查的健壮性、输出清晰度和错误处理。

*   **细分任务 (GREEN 阶段):**
    *   **1.3.1 在 `src/cli/commands.py` 中实现 `check_system_health` (基本结构)**
        *   **RED:** `test_cli_status_command_healthy` 和 `test_cli_status_command_unhealthy` 失败（已完成）。
        *   **GREEN:** 在 `src/cli/commands.py` 中添加 `check_system_health` 函数，返回一个包含基本状态（例如，"配置：已加载"）的字典。
        *   **REFACTOR:** 确保函数签名正确，并能被 `status` 命令调用。
    *   **1.3.2 在 `src/cli/main.py` 中实现 `status()` 命令 (显示基本健康状况)**
        *   **RED:** `test_cli_status_command_healthy` 和 `test_cli_status_command_unhealthy` 失败。
        *   **GREEN:** 在 `src/cli/main.py` 中定义 `status()` 命令，调用 `check_system_health` 并使用 `rich.table` 展示其返回的基本信息。
        *   **REFACTOR:** 优化表格布局和整体健康状态的显示。
    *   **1.3.3 增强 `check_system_health` (详细检查)**
        *   **RED:** `test_cli_status_command_healthy` 和 `test_cli_status_command_unhealthy` 失败。
        *   **GREEN:** 在 `check_system_health` 中添加对 LLM 配置、向量存储、依赖项、服务初始化和 API 连接的详细检查。
        *   **REFACTOR:** 优化错误分类和故障排除提示。

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