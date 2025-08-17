# 05 - 角色管理 - 任务列表 (TDD重构版)

## 概述
此任务列表以TDD方式涵盖了将角色管理功能集成到交互式CLI中的所有步骤。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 列表与查看功能

-   [ ] **RED**: **T-RM-01**: 创建测试文件 `tests/test_role_management.py`。编写失败测试 `test_list_roles_success`。该测试将mock `RoleManager`，配置 `list_roles` 方法返回一个包含两个 `Role` 对象的列表。断言API被调用，并且stdout打印出一个包含两行角色数据的表格。
-   [ ] **GREEN**: **T-RM-02**: 在 `interactive_cli.py` 中实现 `start_role_management` 和 `handle_list_roles` 函数。实现逻辑以调用API并使用 `rich.table` 渲染结果。让 `test_list_roles_success` 测试通过。
-   [ ] **RED**: **T-RM-03**: 编写失败测试 `test_view_role_details_success`。配置mock的 `get_role_by_id` 方法以返回一个固定的 `Role` 对象。断言API被调用，并且该角色的所有属性都被打印到stdout。
-   [ ] **GREEN**: **T-RM-04**: 实现 `handle_view_role_details` 函数，调用API并使用 `rich.panel` 格式化输出，让 `test_view_role_details_success` 测试通过。
-   [ ] **RED**: **T-RM-05**: 编写失败测试 `test_view_role_not_found`。配置mock的 `get_role_by_id` 方法以返回 `None`。断言stdout打印了“未找到”的错误消息。
-   [ ] **GREEN**: **T-RM-06**: 在 `handle_view_role_details` 中添加对 `None` 返回值的处理，让 `test_view_role_not_found` 测试通过。

### Epic 2: 创建与删除功能

-   [ ] **RED**: **T-RM-07**: 编写失败测试 `test_create_role_success`。模拟用户输入 "2" (创建) 及角色数据。断言 `role_manager.save_role` 被以一个正确构造的 `Role` 对象为参数调用。
-   [ ] **GREEN**: **T-RM-08**: 实现 `handle_create_role` 函数，收集用户输入，构造 `Role` 对象并调用API，让 `test_create_role_success` 测试通过。
-   [ ] **RED**: **T-RM-09**: 编写失败测试 `test_delete_role_success`。模拟用户输入 "4" (删除) 和一个 `role_id`。断言 `role_manager.delete_role` 被以正确的 `role_id` 调用。
-   [ ] **GREEN**: **T-RM-10**: 实现 `handle_delete_role` 函数，让 `test_delete_role_success` 测试通过。
-   [ ] **REFACTOR**: **T-RM-11**: 重构 `start_role_management` 及其所有处理函数。确保代码清晰，错误处理健壮，并验证所有测试仍然通过。