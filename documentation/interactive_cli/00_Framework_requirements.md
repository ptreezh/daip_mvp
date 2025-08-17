# 00 - CLI框架 - 需求文档 (TDD重构版)

## 1. 简介
本文档定义了DAIP-LIVE交互式CLI的基础框架需求。该框架是所有功能模块的入口和宿主环境，提供一致的用户导航和交互体验。

## 2. 用户故事
- **As a user**, I want to see a clear main menu when I start the interactive CLI, so that I can easily understand the available high-level functions.
- **As a user**, I want to navigate between the main menu and different feature sub-menus, so that I can perform various tasks within a single session.
- **As a user**, I want to be able to exit the application gracefully from the main menu, so that I can terminate the session cleanly.
- **As a user**, I want to receive clear prompts and feedback for my inputs, so that the interaction is intuitive and easy to follow.

## 3. 功能性需求
- **FR-FMW-01**: 启动时，系统**必须**显示一个主菜单。
- **FR-FMW-02**: 主菜单**必须**包含以下选项：
    - `[1]` 个人助手 (Personal Assistant)
    - `[2]` 辩论大厅 (Debate Hall)
    - `[3]` 实时聊天室 (Chat Room)
    - `[4]` 知识维基 (Knowledge Wiki)
    - `[5]` 角色管理 (Role Management)
    - `[6]` 工作流与制度原语 (Workflows & Primitives)
    - `[0]` 退出 (Exit)
- **FR-FMW-03**: 系统**必须**能接收用户输入的数字选项。
- **FR-FMW-04**: 系统**必须**根据用户的有效输入导航到对应的功能子菜单。
- **FR-FMW-05**: 如果用户输入无效（例如，非数字或范围外的数字），系统**必须**显示一条清晰的错误消息并重新显示当前菜单。
- **FR-FMW-06**: 在每个子菜单中，**必须**提供一个返回主菜单的选项（通常是 `[0]`）。
- **FR-FMW-07**: 选择主菜单中的“退出”选项**必须**终止应用程序。

## 4. 非功能性需求
- **NFR-FMW-01**: 界面文本**应**使用 `rich` 库进行美化（如颜色、样式），以提高可读性。
- **NFR-FMW-02**: CLI的响应时间**应**是即时的，用户输入后不应有可感知的延迟。
- **NFR-FMW-03**: 错误消息**必须**清晰、友好，并能指导用户进行下一步操作。

## 5. 验收测试用例 (Acceptance Test Cases)
- **ATC-FMW-01: 成功显示主菜单**
    - **Given**: 用户启动 `interactive_cli.py`。
    - **When**: 应用启动完成。
    - **Then**: 终端**必须**显示包含 FR-FMW-02 中所有选项的主菜单。
- **ATC-FMW-02: 成功导航到子菜单**
    - **Given**: 主菜单已显示。
    - **When**: 用户输入一个有效选项（例如 `5`）。
    - **Then**: 终端**必须**显示“角色管理”的子菜单。
- **ATC-FMW-03: 成功从子菜单返回**
    - **Given**: 用户处于“角色管理”子菜单。
    - **When**: 用户输入返回选项（例如 `0`）。
    - **Then**: 终端**必须**重新显示主菜单。
- **ATC-FMW-04: 处理无效的非数字输入**
    - **Given**: 主菜单已显示。
    - **When**: 用户输入 `abc`。
    - **Then**: 终端**必须**显示一条错误消息，并重新显示主菜单。
- **ATC-FMW-05: 处理无效的范围外输入**
    - **Given**: 主菜单已显示。
    - **When**: 用户输入 `99`。
    - **Then**: 终端**必须**显示一条错误消息，并重新显示主菜单。
- **ATC-FMW-06: 成功退出应用**
    - **Given**: 主菜单已显示。
    - **When**: 用户输入退出选项 (`0`)。
    - **Then**: 应用程序**必须**终止。