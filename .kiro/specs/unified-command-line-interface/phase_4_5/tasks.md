# 阶段 4 & 5: 高级角色管理、工作流、Wiki 导出、完善与文档 - 任务清单

## 阶段 4: 高级角色管理、工作流与 Wiki 导出 - 任务清单

*   **4.1 实现 `daip-cli roles create` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `role_manager` 成功创建角色，并断言 CLI 输出确认信息。测试包含描述和标签的创建。
        *   **GREEN:** 在 `roles` 子命令组中添加 `create` 命令，接收 `name`, `description`, `tags`，调用 `role_manager`。
        *   **REFACTOR:** 优化标签参数的解析和验证。
*   **4.2 实现 `daip-cli roles invite` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `role_manager` 成功邀请角色，并断言 CLI 输出确认信息。
        *   **GREEN:** 在 `roles` 子命令组中添加 `invite` 命令，接收 `role_id` 和 `debate_id`，调用 `role_manager`。
        *   **REFACTOR:** 验证 ID 的有效性。
*   **4.3 实现 `daip-cli roles manage` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `role_manager` 成功更新角色属性，并断言 CLI 输出确认信息。
        *   **GREEN:** 在 `roles` 子命令组中添加 `manage` 命令，接收 `role_id` 和更新参数，调用 `role_manager`。
        *   **REFACTOR:** 确保更新操作的原子性和错误处理。
*   **4.4 定义和注册“议事规则”制度原语**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证能够定义新的 `InstitutionalPrimitive` 类来表示辩论规则（如 `DebateRulePrimitive`）和聊天室规则（如 `ChatRulePrimitive`），并成功注册到 `PrimitiveRegistry`。
        *   **GREEN:** 实现这些新的 `InstitutionalPrimitive` 类，并编写注册逻辑。
        *   **REFACTOR:** 优化原语的定义结构和参数。
*   **4.5 实现 `daip-cli workflow list` 命令** (原 4.4)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟工作流注册表返回工作流列表，并断言 CLI 输出能正确显示这些工作流。
        *   **GREEN:** 在 `src/cli/main.py` 中创建 `workflow` Typer 子命令组，并添加 `list` 命令，调用 `institutional_primitives.registry`。
        *   **REFACTOR:** 优化工作流列表的显示格式。
*   **4.6 实现 `daip-cli workflow create` 命令 (支持规则原语)** (原 4.5)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证 CLI 能够创建包含“议事规则”制度原语的工作流定义，并成功注册。
        *   **GREEN:** 扩展 `daip-cli workflow create` 命令，使其能够接收和处理新的规则原语定义。
        *   **REFACTOR:** 优化命令参数和验证。
*   **4.7 实现 `daip-cli workflow select` 命令** (原 4.6)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟工作流选择服务成功选择工作流，并断言 CLI 输出确认信息。
        *   **GREEN:** 在 `workflow` 子命令组中添加 `select` 命令，接收 `workflow_id` 和 `scenario_type`，调用 `scenario_engine.workflow_selector`。
        *   **REFACTOR:** 验证场景类型的有效性。
*   **4.8 实现 `daip-cli workflow execute` 命令** (原 4.7)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟工作流引擎成功执行工作流，并断言 CLI 输出执行结果。测试 JSON 字符串参数的传递。
        *   **GREEN:** 在 `workflow` 子命令组中添加 `execute` 命令，接收 `workflow_id` 和 `params_json_string`，调用 `institutional_primitives.workflow_engine`。
        *   **REFACTOR:** 优化 JSON 参数的解析和错误处理。
*   **4.9 实现 `daip-cli wiki export` 命令** (原 4.8)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `wiki_service` 成功导出 Wiki 页面，并断言 CLI 输出导出路径或内容。
        *   **GREEN:** 在 `wiki` 子命令组中添加 `export` 命令，接收 `title_or_id` 和 `format`，调用 `wiki_service`。
        *   **REFACTOR:** 验证导出格式的有效性。
*   **4.10 实现 `daip-cli debate export-to-wiki` 命令** (原 4.9)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `wiki_tools` 成功将辩论结果导出到 Wiki，并断言 CLI 输出确认信息。
        *   **GREEN:** 在 `debate` 子命令组中添加 `export-to-wiki` 命令，接收 `debate_id` 和 `wiki_title`，调用 `wiki_tools`。
        *   **REFACTOR:** 确保辩论 ID 和 Wiki 标题的有效性。

## 阶段 5: 完善、错误处理与文档 - 任务清单

*   **5.1 全局错误处理与用户友好消息**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟后端服务抛出各种已知异常（例如，`NotFoundError`, `ServiceUnavailableError`），并断言 CLI 能够捕获这些异常并显示预定义的用户友好错误消息，而不是原始堆栈跟踪。
        *   **GREEN:** 实现一个全局异常处理器（例如，使用 Typer 的 `callback` 或自定义装饰器），将后端异常映射到清晰的 CLI 错误输出。
        *   **REFACTOR:** 细化错误消息的粒度，为不同类型的错误提供更具体的指导。
*   **5.2 命令行参数验证与提示**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证当用户提供无效参数（例如，非法的 ID 格式、超出预期范围的数字、不匹配的枚举值）时，CLI 能够给出明确的错误提示，而不是直接崩溃。
        *   **GREEN:** 为所有 Typer 命令的参数添加更严格的类型提示、默认值、验证器（例如，使用 `typer.Argument` 或 `typer.Option` 的 `help` 和 `callback`）。
        *   **REFACTOR:** 优化验证逻辑，确保错误提示的即时性和准确性。
*   **5.3 命令行帮助与示例**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证每个已实现命令的 `--help` 输出是否包含所有参数、清晰的描述和至少一个实际的使用示例。
        *   **GREEN:** 为所有 Typer 命令和子命令添加详细的 `help` 字符串和 `example` 文本。
        *   **REFACTOR:** 统一帮助信息的风格和格式，确保一致性。
*   **5.4 性能优化与用户体验改进**
    *   **TDD Cycle:**
        *   **RED:** 编写性能测试，测量关键命令（例如 `start` 辩论、`chat` 交互）的端到端响应时间，并识别潜在的性能瓶颈。
        *   **GREEN:** 审查并优化 CLI 与后端服务的交互，考虑数据传输效率、并发请求（如果后端支持且不新增接口）。
        *   **REFACTOR:** 改进 CLI 的加载速度和命令执行效率，考虑为长时间运行的命令添加进度指示器。
*   **5.5 文档更新与维护**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证项目文档（例如 `README.md`, `GEMINI.md`）是否包含所有 CLI 命令的最新用法、参数说明和示例，并与实际代码保持同步。
        *   **GREEN:** 更新 `README.md` 和 `GEMINI.md`，详细描述所有新添加的 CLI 命令、其功能、参数和使用示例。
        *   **REFACTOR:** 确保文档的准确性、完整性和易读性，考虑添加常见问题解答 (FAQ) 部分。
*   **5.6 代码质量检查与自动化**
    *   **TDD Cycle:**
        *   **RED:** 运行 `ruff` 和其他配置的代码质量工具，识别所有不符合项目规范的代码（例如，格式错误、未使用的导入、潜在的 bug）。
        *   **GREEN:** 修复所有 linting 错误和格式问题，确保代码符合 `ruff.toml` 的要求。
        *   **REFACTOR:** 确保 CI/CD 流程中包含自动化的代码质量检查步骤，防止不符合规范的代码合并。

