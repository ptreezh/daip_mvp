# 02 - 辩论大厅 - 需求文档 (TDD重构版)

## 1. 简介
辩论大厅是系统的核心功能之一。用户应能通过CLI发起、跟进和总结由AI角色参与的辩论。

## 2. 用户故事
- **As a user**, I want to start a new debate by providing a topic.
- **As a user**, I want to follow the progress of an ongoing debate.
- **As a user**, I want to get a summary of a completed debate.
- **As a user**, I want to be able to explicitly end a debate.

## 3. 功能性需求
- **FR-DH-01**: **必须**提供一个辩论大厅子菜单，包含以下选项：
    - `[1]` 发起新辩论
    - `[2]` 查看辩论状态/摘要
    - `[3]` 继续/推进辩论
    - `[4]` 结束辩论
    - `[0]` 返回主菜单
- **FR-DH-02**: **发起新辩论**:
    - **必须**提示用户输入辩论主题。
    - **必须**调用 `MultiRoleDialogueEngine.start_dialogue` API来启动辩论。
    - **必须**在辩论创建后向用户显示一个唯一的会话ID (`session_id`)。
    - **必须**将 `session_id` 和主题持久化存储（例如，在 `debate_memory.json` 中）。
- **FR-DH-03**: **查看辩论状态/摘要**:
    - **必须**提示用户输入 `session_id`。
    - **必须**调用 `MultiRoleDialogueEngine.get_dialogue_summary` API。
    - **必须**将返回的摘要信息格式化并显示给用户。
- **FR-DH-04**: **继续/推进辩论**:
    - **必须**提示用户输入 `session_id`。
    - **必须**调用 `MultiRoleDialogueEngine.continue_dialogue` API来推进辩论一轮。
    - **必须**向用户显示操作成功的确认信息。
- **FR-DH-05**: **结束辩论**:
    - **必须**提示用户输入 `session_id`。
    - **必须**调用 `MultiRoleDialogueEngine.end_dialogue` API。
    - **必须**调用 `MultiRoleDialogueEngine.get_dialogue_summary` API获取最终摘要并显示给用户。

## 4. 验收测试用例
- **ATC-DH-01: 成功发起一场辩论**
    - **Given**: 用户在辩论大厅子菜单。
    - **When**: 用户选择 "发起新辩论" 并输入主题 "AI伦理"。
    - **Then**: `MultiRoleDialogueEngine.start_dialogue` **必须**被调用，其 `topic` 参数为 "AI伦理"。
    - **And**: 一个新的 `session_id` **必须**被显示给用户。
    - **And**: 该 `session_id` 和主题**必须**被保存在持久化存储中。
- **ATC-DH-02: 成功获取辩论摘要**
    - **Given**: 一场ID为 `session-123` 的辩论正在进行。
    - **When**: 用户选择 "查看辩论状态/摘要" 并输入 `session-123`。
    - **Then**: `MultiRoleDialogueEngine.get_dialogue_summary` **必须**被以 `session_id='session-123'` 为参数调用。
    - **And**: 返回的摘要信息（如总轮次、参与角色等）**必须**被显示在终端。
- **ATC-DH-03: API调用失败**
    - **Given**: 用户尝试发起一场新辩论。
    - **When**: `MultiRoleDialogueEngine.start_dialogue` API调用抛出异常。
    - **Then**: CLI**必须**显示一条清晰的错误消息。
    - **And**: CLI**不能**崩溃，并**必须**返回到辩论大厅子菜单。