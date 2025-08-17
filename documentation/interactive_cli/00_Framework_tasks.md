# 00 - CLI框架 - 任务列表 (TDD重构版)

## 概述
此任务列表涵盖了以TDD方式构建交互式CLI基础框架所需的步骤。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 主菜单显示与退出功能

-   [x] **RED**: **T-FMW-01**: 创建测试文件 `tests/test_cli_framework.py`。编写一个失败的测试 `test_main_menu_is_displayed_on_start`，该测试捕获stdout并断言主菜单的标题和所有选项（FR-FMW-02）都被打印出来。
-   [x] **GREEN**: **T-FMW-02**: 创建 `interactive_cli.py`。在 `pyproject.toml` 或 `requirements.txt` 中添加 `rich` 依赖。实现一个最简单的 `main` 函数和 `show_main_menu` 函数，使其刚好能打印出主菜单，让 `test_main_menu_is_displayed_on_start` 测试通过。
-   [x] **RED**: **T-FMW-03**: 编写一个失败的测试 `test_app_exits_when_user_inputs_zero`，该测试模拟用户输入 "0" 并断言应用正常退出。
-   [x] **GREEN**: **T-FMW-04**: 在 `main` 函数中添加主循环和输入处理逻辑。当用户输入 "0" 时，`break` 循环，让 `test_app_exits_when_user_inputs_zero` 测试通过。
-   [x] **REFACTOR**: **T-FMW-05**: (可选) 重构 `main` 和 `show_main_menu` 函数的代码，提高可读性，清理魔法字符串，同时确保所有测试仍然通过。

### Epic 2: 菜单导航与无效输入处理

-   [x] **RED**: **T-FMW-06**: 编写一个失败的测试 `test_navigation_to_submenu_on_valid_input`。该测试模拟用户输入 "5"，并使用 `mock.patch` 断言一个名为 `start_role_management` 的占位符函数被准确调用了一次。
-   [x] **GREEN**: **T-FMW-07**: 在 `interactive_cli.py` 中创建所有菜单选项对应的占位符函数（例如 `start_role_management`, `start_wiki_service` 等）。在主循环中添加 `if/elif` 逻辑，根据用户输入调用正确的占位符函数，让 `test_navigation_to_submenu_on_valid_input` 测试通过。
-   [x] **RED**: **T-FMW-08**: 编写一个失败的测试 `test_error_message_on_non_numeric_input`，模拟用户输入 "abc"，捕获stdout并断言输出了清晰的错误消息。
-   [x] **GREEN**: **T-FMW-09**: 在输入处理逻辑中添加 `try-except ValueError` 块，以处理非数字输入。在 `except` 块中打印错误消息，让 `test_error_message_on_non_numeric_input` 测试通过。
-   [x] **RED**: **T-FMW-10**: 编写一个失败的测试 `test_error_message_on_out_of_range_input`，模拟用户输入 "99"，并断言输出了清晰的错误消息。
-   [x] **GREEN**: **T-FMW-11**: 在 `if/elif` 逻辑中添加一个 `else` 块，以处理范围之外的数字输入，让 `test_error_message_on_out_of_range_input` 测试通过。
-   [x] **REFACTOR**: **T-FMW-12**: (可选) 重构主循环的输入处理逻辑，可能将其提取到一个单独的 `handle_main_menu_input` 函数中，以保持 `main` 函数的整洁。确保所有测试仍然通过。
