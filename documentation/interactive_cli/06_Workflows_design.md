# 06 - 工作流与制度原语 - 设计文档 (TDD重构版)

## 1. 技术方法
工作流功能将由 `start_workflows()` 函数入口进行管理。

- **API依赖**: 此模块将严格依赖 `PrimitiveRegistry` 和 `WorkflowEngine` 提供的API。所有方法的调用都必须参照 `documentation/GLOBAL_API_DICTIONARY.md`。
- **数据显示**: 使用 `rich.table` 显示原语列表。使用 `rich.json` 或 `rich.pretty` 来格式化和显示工作流执行结果。
- **用户输入**: 对于需要复杂输入的“验证原语”和“执行工作流”，将要求用户提供一个JSON字符串。CLI将负责基本的JSON解析和验证，然后将解析后的字典传递给后端API。
- **桩实现说明**: 在执行工作流后，CLI的输出将**明确**包含一条提示信息，告知用户结果是基于桩实现的模拟数据，例如 `[bold yellow]注意: 工作流执行成功，但所有节点（原语）均为桩实现，返回的是模拟数据。[/bold yellow]`。

## 2. 组件交互
- **`start_workflows()`**:
    - 初始化 `PrimitiveRegistry` 和 `WorkflowEngine` 的实例。
    - **关键**: 需要手动将 `src.institutional_primitives.primitives` 中定义的桩原语类（`ConsensusBuilding`, `CriticalReview` 等）注册到 `PrimitiveRegistry` 实例中，否则引擎将一无所知。
    - 显示工作流子菜单。
- **`handle_list_primitives()`**:
    - 调用 `primitive_registry.list_primitives()`。
    - 使用 `rich.table` 格式化并显示返回的原语信息列表。
- **`handle_validate_primitive()`**:
    - 提示用户输入JSON字符串。
    - 使用 `json.loads()` 解析字符串。
    - 调用 `primitive_registry.validate_primitive(parsed_dict)`。
    - 打印验证结果。
- **`handle_execute_workflow()`**:
    - 提示用户输入工作流定义的JSON字符串。
    - 使用 `pydantic` 的 `WorkflowDefinition.model_validate_json()` 来解析和验证输入。
    - 调用 `workflow_engine.execute_workflow(workflow_definition_object)`。
    - 打印返回的 `WorkflowResult`，并附带桩实现说明。

## 3. CLI流程 / 用户界面
**执行工作流:**
```
> 请粘贴工作流定义的JSON字符串: {"id": "test-wf", "name": "Test", "nodes": [...]}
(CLI calls execute_workflow)

Workflow Result:
{
 'execution_id': '...',
 'status': 'completed',
 'outputs': {'final_output': '模拟数据'},
 ...
}
[bold yellow]注意: 工作流执行成功，但所有节点（原语）均为桩实现，返回的是模拟数据。[/bold yellow]
```

## 4. 测试策略
- **单元测试 (`tests/test_workflows.py`)**:
    - **目标**: 独立测试工作流CLI的UI和流程逻辑。
    - **Mock**:
        - `PrimitiveRegistry` 和 `WorkflowEngine` 将被完全mock。
        - `list_primitives` 将返回一个固定的原语信息列表。
        - `validate_primitive` 将返回一个固定的 `ValidationResult` 对象。
        - `execute_workflow` 将返回一个固定的 `WorkflowResult` 对象。
    - **断言**:
        - 验证当用户执行各项操作时，对应的 `PrimitiveRegistry` 和 `WorkflowEngine` 方法被以正确的参数调用。
        - 验证用户输入的JSON字符串被正确解析并传递给API。
        - 验证 `execute_workflow` 的返回结果被正确打印，并且包含了“桩实现”的警告信息。
        - 验证当用户输入无效的JSON时，CLI能捕获 `json.JSONDecodeError` 并显示友好错误。