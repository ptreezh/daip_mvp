# 01 - 个人助理 - 任务列表 (TDD重构版)

## 概述
此任务列表涵盖了以TDD方式构建个人助理CLI功能所需的步骤。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 基础聊天功能

-   [x] **GREEN**: **PA-F-01**: 编写一个失败的测试 `test_assistant_chat_command_not_found`。该测试模拟调用 `daip-cli assistant chat "hello"` 命令，并断言命令不存在或未实现。
-   [ ] **GREEN**: **PA-F-02**: 在 `src/cli/main.py` 中为 `assistant` Typer 应用添加 `chat` 命令。实现一个占位符函数，使其能够接收 `query` 参数并打印一个简单的响应，让 `test_assistant_chat_command_not_found` 测试通过。
-   [ ] **REFACTOR**: **PA-F-03**: (可选) 重构 `chat` 命令的实现，将其核心逻辑（例如与个人助理服务的交互）提取到 `src/cli/commands.py` 或 `src/application/personal_assistant_service.py` 中的新函数。确保所有测试仍然通过。

### Epic 2: 与个人助理服务集成

-   [ ] **RED**: **PA-F-04**: 编写一个失败的测试 `test_assistant_chat_integrates_with_service`。该测试模拟调用 `daip-cli assistant chat "summarize this"`，并使用 `mock.patch` 断言 `src/application/personal_assistant_service.py` 中的核心聊天函数被调用，并且CLI输出了模拟的响应。
-   [ ] **GREEN**: **PA-F-05**: 修改 `chat` 命令的实现，使其调用 `src/application/personal_assistant_service.py` 中的实际个人助理服务。确保 `test_assistant_chat_integrates_with_service` 测试通过。
-   [ ] **REFACTOR**: **PA-F-06**: (可选) 优化个人助理服务的调用方式，例如添加错误处理、日志记录或异步支持。确保所有测试仍然通过。

### Epic 3: 错误处理与用户反馈

-   [ ] **RED**: **PA-F-07**: 编写一个失败的测试 `test_assistant_chat_handles_service_errors`。该测试模拟个人助理服务抛出异常，并断言CLI输出了用户友好的错误消息。
-   [ ] **GREEN**: **PA-F-08**: 在 `chat` 命令中添加错误处理逻辑，捕获个人助理服务可能抛出的异常，并向用户显示清晰的错误消息。确保 `test_assistant_chat_handles_service_errors` 测试通过。
-   [ ] **REFACTOR**: **PA-F-09**: (可选) 统一CLI的错误报告机制，确保所有命令都能提供一致的用户反馈。确保所有测试仍然通过。
