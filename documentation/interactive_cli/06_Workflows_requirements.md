# 06 - 工作流与制度原语 - 需求文档 (TDD重构版)

## 1. 简介
该模块允许用户管理和执行“制度原语”工作流。**注意**: 根据API分析，虽然工作流的编排引擎功能完整，但具体的执行节点（原语）均为桩实现。因此，执行工作流将完成端到端流程，但返回的是模拟数据。

## 2. 用户故事
- **As a user**, I want to see a list of all available workflow primitives.
- **As a user**, I want to instantiate a primitive to see if it's valid.
- **As a user**, I want to execute a pre-defined workflow to understand the orchestration process.

## 3. 功能性需求
- **FR-WF-01**: **必须**提供一个工作流子菜单，包含以下选项：
    - `[1]` 列出所有已注册的原语
    - `[2]` 验证一个原语定义
    - `[3]` 执行一个工作流
    - `[0]` 返回主菜单
- **FR-WF-02**: **列出所有原语**:
    - **必须**调用 `PrimitiveRegistry.list_primitives` API。
    - **必须**以表格形式展示所有已注册原语的类型、名称和描述。
- **FR-WF-03**: **验证原语定义**:
    - **必须**提示用户输入一个JSON格式的原语定义字符串。
    - **必须**调用 `PrimitiveRegistry.validate_primitive` API。
    - **必须**向用户显示验证结果（成功或失败及原因）。
- **FR--WF-04**: **执行工作流**:
    - **必须**提示用户输入一个JSON格式的工作流定义字符串。
    - **必须**调用 `WorkflowEngine.execute_workflow` API。
    - **必须**向用户显示最终的执行结果，并明确指出结果是基于桩实现生成的模拟数据。

## 4. 验收测试用例
- **ATC-WF-01: 成功列出原语**
    - **Given**: `PrimitiveRegistry` 中已注册了三个原语。
    - **When**: 用户选择 "列出所有已注册的原语"。
    - **Then**: `PrimitiveRegistry.list_primitives` **必须**被调用。
    - **And**: 终端**必须**显示一个包含三个原语信息的表格。
- **ATC-WF-02: 成功执行一个工作流**
    - **Given**: 用户在工作流子菜单。
    - **When**: 用户选择 "执行一个工作流" 并提供一个有效的JSON工作流定义。
    - **Then**: `WorkflowEngine.execute_workflow` **必须**被以一个正确构造的 `WorkflowDefinition` 对象为参数调用。
    - **And**: 终端**必须**显示来自桩原语的模拟输出结果。
- **ATC-WF-03: 验证一个无效的原语定义**
    - **Given**: 用户在工作流子菜单。
    - **When**: 用户选择 "验证一个原语定义" 并提供一个缺少 `type` 字段的JSON字符串。
    - **Then**: `PrimitiveRegistry.validate_primitive` **必须**被调用。
    - **And**: CLI**必须**显示一条包含“Missing required field 'type'”的验证失败消息。