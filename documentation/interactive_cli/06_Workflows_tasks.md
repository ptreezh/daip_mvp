# 06 - 工作流与制度原语 - 任务列表 (TDD重构版)

## 概述
此任务列表以TDD方式涵盖了将工作流管理功能集成到交互式CLI中的所有步骤。

## TDD任务分解 (Red-Green-Refactor)

### Epic 1: 注册与发现原语

-   [ ] **RED**: **T-WF-01**: 创建测试文件 `tests/test_workflows.py`。编写失败测试 `test_list_primitives_success`。该测试将mock `PrimitiveRegistry`，配置 `list_primitives` 方法返回一个包含两个原语信息的列表。断言API被调用，并且stdout打印出一个包含两行原语数据的表格。
-   [ ] **GREEN**: **T-WF-02**: 在 `interactive_cli.py` 中实现 `start_workflows` 和 `handle_list_primitives` 函数。在 `start_workflows` 中，确保桩原语被注册到 `PrimitiveRegistry` 实例中。在 `handle_list_primitives` 中调用API并使用 `rich.table` 渲染结果。让 `test_list_primitives_success` 测试通过。
-   [ ] **RED**: **T-WF-03**: 编写失败测试 `test_validate_primitive_success`。配置mock的 `validate_primitive` 方法以返回一个成功的 `ValidationResult` 对象。模拟用户输入一个JSON字符串，断言API被以解析后的字典调用，并且stdout打印了成功信息。
-   [ ] **GREEN**: **T-WF-04**: 实现 `handle_validate_primitive` 函数，处理JSON输入和API调用，让 `test_validate_primitive_success` 测试通过。
-   [ ] **RED**: **T-WF-05**: 编写失败测试 `test_validate_invalid_json`。模拟用户输入一个无效的JSON字符串。断言CLI捕获了 `json.JSONDecodeError` 并打印了错误消息。
-   [ ] **GREEN**: **T-WF-06**: 在 `handle_validate_primitive` 中添加 `try-except` 块来处理无效JSON，让 `test_validate_invalid_json` 测试通过。

### Epic 2: 执行工作流

-   [ ] **RED**: **T-WF-07**: 编写失败测试 `test_execute_workflow_success`。Mock `WorkflowEngine`，配置 `execute_workflow` 方法返回一个固定的 `WorkflowResult` 对象。模拟用户输入一个有效的JSON工作流定义。
-   [ ] **GREEN**: **T-WF-08**: 实现 `handle_execute_workflow` 函数。使用 `pydantic` 模型来解析和验证JSON输入，然后调用API。让 `test_execute_workflow_success` 测试通过。
-   [ ] **RED**: **T-WF-09**: 编写失败测试 `test_execute_workflow_shows_stub_warning`。基于 `test_execute_workflow_success`，额外断言stdout中**必须**包含明确的“桩实现”警告信息。
-   [ ] **GREEN**: **T-WF-10**: 在 `handle_execute_workflow` 的输出部分，添加打印桩实现警告的逻辑，让 `test_execute_workflow_shows_stub_warning` 测试通过。
-   [ ] **REFACTOR**: **T-WF-11**: 重构 `start_workflows` 及其所有处理函数。确保代码清晰，JSON处理健壮，并验证所有测试仍然通过。