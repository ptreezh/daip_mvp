# 02 - 辩论大厅 - 任务列表 (TDD重构版)

## 概述
此任务列表以TDD方式涵盖了将辩论大厅功能集成到交互式CLI中的所有步骤。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 发起与记录辩论

-   [ ] **RED**: **T-DH-01**: 创建测试文件 `tests/test_debate_hall.py`。编写失败测试 `test_start_debate_success`。该测试将mock `MultiRoleDialogueEngine` 和文件I/O。它将模拟用户输入 "1" (发起辩论) 和主题 "Test Topic"。
-   [ ] **GREEN**: **T-DH-02**: 在 `interactive_cli.py` 中实现 `start_debate_hall` 和 `handle_start_debate` 函数。在 `handle_start_debate` 中，调用 `dialogue_engine.start_dialogue`，并将返回的 `session_id` 写入（mock的）`debate_memory.json`。让 `test_start_debate_success` 测试通过。
-   [ ] **RED**: **T-DH-03**: 编写失败测试 `test_start_debate_api_failure`。配置mock的 `start_dialogue` 方法以抛出异常。断言CLI捕获异常，向stdout打印错误消息，并且没有向 `debate_memory.json` 写入任何内容。
-   [ ] **GREEN**: **T-DH-04**: 在 `handle_start_debate` 中添加 `try-except` 块来包裹API调用，并在 `except` 块中打印错误，让 `test_start_debate_api_failure` 测试通过。

### Epic 2: 查看与推进辩论

-   [ ] **RED**: **T-DH-05**: 编写失败测试 `test_get_summary_success`。模拟用户输入 "2" (查看摘要) 和一个 `session_id`。配置mock的 `get_dialogue_summary` 以返回一个包含特定键值（如 `topic`, `total_turns`）的字典。断言该API被正确调用，并且这些键值被打印到stdout。
-   [ ] **GREEN**: **T-DH-06**: 实现 `handle_get_summary` 函数。它应提示用户输入ID，调用 `dialogue_engine.get_dialogue_summary`，并格式化输出，让 `test_get_summary_success` 测试通过。
-   [ ] **RED**: **T-DH-07**: 编写失败测试 `test_continue_debate_success`。模拟用户输入 "3" (继续辩论) 和一个 `session_id`。断言 `dialogue_engine.continue_dialogue` 被以正确的 `session_id` 调用。
-   [ ] **GREEN**: **T-DH-08**: 实现 `handle_continue_debate` 函数，让 `test_continue_debate_success` 测试通过。

### Epic 3: 结束辩论与重构

-   [ ] **RED**: **T-DH-09**: 编写失败测试 `test_end_debate_success`。模拟用户输入 "4" (结束辩论) 和一个 `session_id`。断言 `dialogue_engine.end_dialogue` 被调用，随后 `dialogue_engine.get_dialogue_summary` 也被调用，并且最终的摘要被打印出来。
-   [ ] **GREEN**: **T-DH-10**: 实现 `handle_end_debate` 函数，让 `test_end_debate_success` 测试通过。
-   [ ] **REFACTOR**: **T-DH-11**: 重构 `start_debate_hall` 及其所有处理函数。确保代码清晰，将文件I/O操作封装到辅助函数中，并验证所有测试仍然通过。