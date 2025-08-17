# 02 - 辩论大厅 - 设计文档 (TDD重构版)

## 1. 技术方法
辩论大厅模块将由 `start_debate_hall()` 函数管理。该函数将显示辩论子菜单并根据用户选择调用相应的处理函数。

- **API依赖**: 此模块将严格依赖 `MultiRoleDialogueEngine` 提供的API。所有方法的调用都必须参照 `documentation/GLOBAL_API_DICTIONARY.md`。
- **状态管理**: CLI本身不存储辩论的复杂状态（如对话历史）。它只负责管理一个简单的 `debate_memory.json` 文件，用于存储 `session_id` 与辩论主题的映射关系，以便用户可以方便地回顾和管理他们发起的辩论。所有实时的、复杂的辩论状态都通过API从 `MultiRoleDialogueEngine` 中获取。
- **数据显示**: 使用 `rich.table` 来显示辩论列表。使用 `rich.panel` 和 `rich.markdown` 来格式化和显示从 `get_dialogue_summary` API返回的详细摘要。

## 2. 组件交互
- **`start_debate_hall()`**:
    - 初始化 `MultiRoleDialogueEngine` 的一个实例。
    - 加载 `debate_memory.json` 的内容。
    - 显示辩论子菜单，并可能附带一个当前已知辩论的列表。
- **`handle_start_debate()`**:
    - 提示用户输入 `topic`。
    - **注意**: `start_dialogue` API需要一个 `DebateSession` 对象。CLI需要根据 `topic` 创建一个最小化的 `DebateSession` 实例来传递。
    - 调用 `dialogue_engine.start_dialogue(session, topic)`。
    - 获取返回的 `session_id`。
    - 将 `session_id` 和 `topic` 保存到 `debate_memory.json` 中。
    - 向用户显示成功信息和 `session_id`。
- **`handle_get_summary()`**:
    - 提示用户输入 `session_id`。
    - 调用 `dialogue_engine.get_dialogue_summary(session_id)`。
    - 格式化响应内容并美观地打印出来。
- **`handle_continue_debate()`**:
    - 提示用户输入 `session_id`。
    - 调用 `dialogue_engine.continue_dialogue(session_id)`。
    - 打印成功信息。
- **`handle_end_debate()`**:
    - 提示用户输入 `session_id`。
    - 调用 `dialogue_engine.end_dialogue(session_id)`。
    - 接着调用 `dialogue_engine.get_dialogue_summary(session_id)` 获取最终总结。
    - 打印最终总结。

## 3. 持久化存储 (`debate_memory.json`)
一个简单的JSON文件，用于追踪用户通过CLI创建的辩论。
```json
[
  {
    "session_id": "session-abcde",
    "topic": "AI伦理的重要性",
    "created_at": "..."
  },
  {
    "session_id": "session-fghij",
    "topic": "探索太空的必要性",
    "created_at": "..."
  }
]
```

## 4. 测试策略
- **单元测试 (`tests/test_debate_hall.py`)**:
    - **目标**: 独立测试辩论大厅CLI的UI和流程逻辑。
    - **Mock**:
        - `MultiRoleDialogueEngine` 将被完全mock。
        - `start_dialogue` 将被配置为返回一个固定的 `session_id`。
        - `get_dialogue_summary` 将被配置为返回一个固定的摘要字典。
        - `continue_dialogue` 和 `end_dialogue` 将被配置为返回 `True`。
        - 文件操作（读写 `debate_memory.json`）将被mock，以使用临时的测试文件。
    - **断言**:
        - 验证当用户发起辩论时，`start_dialogue` 被以正确的参数调用。
        - 验证 `session_id` 被正确地写入了mock的文件中。
        - 验证当用户查询摘要时，`get_dialogue_summary` 被正确调用，并且其返回内容被正确格式化并打印到 `stdout`。
        - 验证所有API调用都被包裹在 `try-except` 块中，并且在mock的API抛出异常时，能够正确显示错误消息。