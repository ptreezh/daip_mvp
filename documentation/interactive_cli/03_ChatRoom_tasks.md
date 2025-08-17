# 03 - 聊天室 - 任务列表 (TDD重构版)

## 概述
此任务列表以TDD方式涵盖了将聊天室**管理**功能集成到交互式CLI中的所有步骤。消息传递功能被明确排除。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 创建与列出聊天室

-   [ ] **RED**: **T-CR-01**: 创建测试文件 `tests/test_chat_room.py`。编写失败测试 `test_create_chat_room_success`。该测试将mock `ChatRoomManager`，模拟用户输入 "1" (创建) 及房间配置，并断言 `chat_room_manager.create_chat_room` 被以正确的 `ChatRoomConfig` 对象调用。
-   [ ] **GREEN**: **T-CR-02**: 在 `interactive_cli.py` 中实现 `start_chat_room` 和 `handle_create_chat_room` 函数。实现逻辑以收集用户输入，构造 `ChatRoomConfig`，并调用API。让 `test_create_chat_room_success` 测试通过。
-   [ ] **RED**: **T-CR-03**: 编写失败测试 `test_list_chat_rooms_success`。配置mock的 `list_chat_rooms` 方法以返回一个包含两个房间摘要的列表。断言API被调用，并且stdout中打印出一个包含两行数据的表格。
-   [ ] **GREEN**: **T-CR-04**: 实现 `handle_list_chat_rooms` 函数，调用API并使用 `rich.table` 渲染结果，让 `test_list_chat_rooms_success` 测试通过。

### Epic 2: 删除与处理未实现功能

-   [ ] **RED**: **T-CR-05**: 编写失败测试 `test_delete_chat_room_success`。模拟用户输入 "3" (删除) 和一个 `room_id`。断言 `chat_room_manager.delete_chat_room` 被以正确的 `room_id` 调用。
-   [ ] **GREEN**: **T-CR-06**: 实现 `handle_delete_chat_room` 函数，让 `test_delete_chat_room_success` 测试通过。
-   [ ] **RED**: **T-CR-07**: 编写失败测试 `test_join_chat_room_shows_error_message`。模拟用户输入 "4" (加入)。断言stdout打印了明确的“功能未实现”错误消息，并且**没有**调用任何 `ChatRoomManager` 的方法（除了初始化）。
-   [ ] **GREEN**: **T-CR-08**: 实现 `handle_join_chat_room` 函数，使其只打印错误消息，让 `test_join_chat_room_shows_error_message` 测试通过。
-   [ ] **REFACTOR**: **T-CR-09**: 重构 `start_chat_room` 及其所有处理函数。确保代码清晰，错误处理到位（例如，当 `create_chat_room` 抛出异常时），并验证所有测试仍然通过。