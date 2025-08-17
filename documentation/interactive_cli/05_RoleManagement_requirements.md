# 05 - 角色管理 - 需求文档 (TDD重构版)

## 1. 简介
该模块为用户提供了查看、创建、删除和管理系统中所有AI角色的能力。

## 2. 用户故事
- **As a user**, I want to see a list of all available AI roles in the system.
- **As a user**, I want to create a new AI role by providing its essential details.
- **As a user**, I want to view the detailed information of a specific role.
- **As a user**, I want to delete an existing role.

## 3. 功能性需求
- **FR-RM-01**: **必须**提供一个角色管理子菜单，包含以下选项：
    - `[1]` 列出所有角色
    - `[2]` 创建新角色
    - `[3]` 查看角色详情
    - `[4]` 删除角色
    - `[0]` 返回主菜单
- **FR-RM-02**: **列出所有角色**:
    - **必须**调用 `RoleManager.list_roles` API。
    - **必须**以表格形式清晰地展示所有角色的ID、名称和简短描述。
- **FR-RM-03**: **创建新角色**:
    - **必须**提示用户输入角色ID(文件名)、名称、描述和system_prompt。
    - **必须**调用 `RoleManager.save_role` API来持久化这个新角色。
- **FR-RM-04**: **查看角色详情**:
    - **必须**提示用户输入角色ID。
    - **必须**调用 `RoleManager.get_role_by_id` API。
    - **必须**将返回的角色所有详细信息格式化并展示。
- **FR-RM-05**: **删除角色**:
    - **必须**提示用户输入角色ID。
    - **必须**调用 `RoleManager.delete_role` API。
    - **必须**向用户显示操作成功的确认信息。

## 4. 验收测试用例
- **ATC-RM-01: 成功创建并列出角色**
    - **Given**: 用户在角色管理子菜单。
    - **When**: 用户选择 "创建" -> 输入角色信息 -> 然后选择 "列出所有角色"。
    - **Then**: `RoleManager.save_role` **必须**被以一个包含正确信息的 `Role` 对象为参数调用。
    - **And**: `RoleManager.list_roles` **必须**被调用。
    - **And**: 新创建的角色的信息**必须**出现在终端显示的表格中。
- **ATC-RM-02: 成功删除角色**
    - **Given**: 一个ID为 "test_role" 的角色存在。
    - **When**: 用户选择 "删除角色" 并输入 "test_role"。
    - **Then**: `RoleManager.delete_role` **必须**被以 `role_id='test_role'` 为参数调用。
    - **And**: 终端**必须**显示成功删除的消息。
- **ATC-RM-03: 查看不存在的角色**
    - **Given**: 用户在角色管理子菜单。
    - **When**: 用户选择 "查看角色详情" 并输入一个不存在的ID "non_existent_role"。
    - **Then**: `RoleManager.get_role_by_id` **必须**被调用并返回 `None`。
    - **And**: CLI**必须**显示一条清晰的“角色未找到”错误消息。