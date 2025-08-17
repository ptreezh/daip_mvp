# 05 - 角色管理 - 设计文档 (TDD重构版)

## 1. 技术方法
角色管理功能将由 `start_role_management()` 函数入口进行管理。

- **API依赖**: 此模块将严格依赖 `RoleManager` 提供的API，所有方法的调用都必须参照 `documentation/GLOBAL_API_DICTIONARY.md`。
- **数据显示**: `rich.table` 是展示角色列表的理想选择。对于单个角色的详细信息，使用 `rich.panel` 配合格式化的文本可以提供良好的阅读体验。
- **用户输入**: 对于创建角色这类涉及多字段输入的操作，将采用分步提示的方式收集信息。

## 2. 组件交互
- **`start_role_management()`**:
    - 初始化 `RoleManager` 的一个实例。
    - 显示角色管理子菜单。
- **`handle_list_roles()`**:
    - 调用 `role_manager.list_roles()`。
    - 创建一个 `rich.table` 并设置列（ID, Name, Description）。
    - 遍历返回的 `Role` 对象列表，将数据填充到表格中并打印。
- **`handle_create_role()`**:
    - 分别提示用户输入 `id`, `name`, `description`, `system_prompt`, `capabilities`。
    - 创建一个 `Role` 数据类的实例。
    - 调用 `role_manager.save_role(role_object)`。
    - 打印成功信息。
- **`handle_view_role_details()`**:
    - 提示用户输入 `role_id`。
    - 调用 `role_manager.get_role_by_id(role_id)`。
    - 如果找到角色，使用 `rich.panel` 格式化并显示其所有属性。否则，打印未找到的错误消息。
- **`handle_delete_role()`**:
    - 提示用户输入 `role_id`。
    - 调用 `role_manager.delete_role(role_id)`。
    - 根据返回的布尔值打印成功或失败信息。

## 3. CLI流程 / 用户界面
**列出角色:**
```
+---------------+------------------+-------------------------------------+
| Role ID       | Name             | Description                         |
+---------------+------------------+-------------------------------------+
| ai_ethicist   | AI Ethicist      | Specializes in the ethics of AI...  |
| tech_innovator| Tech Innovator   | Focuses on breakthrough technology...|
+---------------+------------------+-------------------------------------+
```

## 4. 测试策略
- **单元测试 (`tests/test_role_management.py`)**:
    - **目标**: 独立测试角色管理CLI的UI和流程逻辑。
    - **Mock**:
        - `RoleManager` 将被完全mock。
        - `list_roles` 将返回一个固定的 `Role` 对象列表。
        - `get_role_by_id` 将根据输入返回一个固定的 `Role` 对象或 `None`。
        - `save_role` 和 `delete_role` 将返回 `True`。
    - **断言**:
        - 验证当用户执行各项操作时，对应的 `RoleManager` 方法被以正确的参数调用。
        - 验证 `list_roles` 的返回结果被正确地格式化为表格并打印到 `stdout`。
        - 验证 `get_role_by_id` 的返回结果被正确地格式化为 `rich.panel` 并打印。
        - 验证当 `get_role_by_id` 返回 `None` 时，CLI能打印出“未找到”的错误消息。
        - 验证所有API调用都被 `try-except` 块包裹，能正确处理mock的API抛出异常时的情况。