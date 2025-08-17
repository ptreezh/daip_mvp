# 00 - CLI框架 - 设计文档 (TDD重构版)

## 1. 技术方法
交互式CLI将作为一个独立的Python脚本 `interactive_cli.py` 来实现，位于项目的根目录下。它将利用以下库：
- **Typer**: 用于构建CLI应用框架。
- **Rich**: 用于渲染美观的输出，包括菜单、提示、表格和高亮文本。
- **Python `input()` / `prompt_toolkit`**: 用于在菜单循环中捕获用户的输入。
- **Pytest**: 用于单元测试和集成测试。
- **Mock**: (`unittest.mock`) 用于在测试中模拟用户输入和后端服务调用。

核心设计是一个主循环，它显示当前菜单，等待用户输入，然后根据输入调用相应的处理函数。

## 2. 组件交互
- **`interactive_cli.py`**: 主入口点。
    - `main()`: 初始化应用，启动主菜单循环。
    - `show_main_menu()`: 使用 `rich` 组件显示主菜单选项。
    - `handle_main_menu_input()`: 解析用户输入，并根据选项调用相应模块的启动函数（例如 `start_personal_assistant()`）。
- **模块处理器**: 每个功能模块将有自己的处理器函数（例如 `start_role_management()`），负责该模块的子菜单显示和逻辑处理。
- **后端服务 (`src/` 下的服务)**: 模块处理器将直接导入并调用 `src` 目录下的相关服务类。**所有对后端服务的调用都必须严格参照 `documentation/GLOBAL_API_DICTIONARY.md` 中定义的API**。

## 3. CLI流程 / 用户界面
**启动流程:**
1.  用户在终端运行 `python interactive_cli.py`。
2.  屏幕清空，显示欢迎标题。
3.  显示主菜单。

**交互逻辑:**
- 用户输入 `5`。
- `handle_main_menu_input()` 调用 `start_role_management()`。
- `start_role_management()` 函数接管，显示角色管理的子菜单。
- 在角色管理子菜单中，用户选择 `0` (返回)。
- `start_role_management()` 函数返回，主循环继续，重新显示主菜单。

## 4. 错误处理
- **无效输入**: 使用 `try-except` 块来捕获 `ValueError`。
- **范围外选项**: 使用 `if-elif-else` 结构检查输入的整数是否在有效选项范围内。
- **后端异常**: 调用后端服务时，使用 `try-except` 捕获可能发生的异常，并向用户显示友好的错误信息。

## 5. 测试策略 (Testing Strategy)
- **单元测试**:
    - **目标**: 独立测试CLI的UI逻辑，无需启动后端服务。
    - **方法**:
        - 使用 `unittest.mock.patch` 来模拟 `input()` 函数，以编程方式提供用户输入。
        - 使用 `unittest.mock.patch` 来模拟所有后端服务（例如 `RoleManager`, `WikiService`）。Mock对象将返回预设的数据，以验证CLI是否能正确处理这些数据并将其显示给用户。
        - 捕获 `stdout`（例如，使用 `contextlib.redirect_stdout`）来验证CLI的输出是否符合预期（例如，菜单是否正确显示，错误消息是否出现）。
    - **示例**: `test_main_menu_navigation.py` 将包含一个测试，模拟用户输入 "5"，并断言 `start_role_management` 函数被调用。
- **集成测试**:
    - **目标**: 测试CLI与真实后端服务（在测试模式下）的集成。
    - **方法**:
        - 测试将实例化真实的CLI应用和真实的后端服务（例如 `RoleManager`）。
        - 对于需要文件系统或网络的服务，测试将在一个临时的、受控的环境中运行（例如，`RoleManager` 将指向一个临时的测试角色目录）。
        - 测试将使用 `pexpect` 或类似的库来驱动CLI应用，发送输入并断言其输出。
    - **范围**: 由于集成的复杂性，集成测试将主要覆盖核心的用户流程（"Happy Path"）。