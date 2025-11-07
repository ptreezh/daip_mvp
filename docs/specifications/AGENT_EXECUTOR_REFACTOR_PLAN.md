# AgentExecutor重构计划

## 目标
根据SOLID原则中的单一职责原则，将AgentExecutor类拆分为多个专门的类，每个类只负责一个明确的职责。

## 识别的职责

### 1. 会话管理器 (SessionManager)
- 职责：管理会话的创建、保存和状态更新
- 方法：
  - create_session
  - save_session
  - update_session_status

### 2. 工作流执行器 (WorkflowExecutor)
- 职责：执行工作流定义
- 方法：
  - execute_workflow
  - _execute_workflow_element_events
  - _get_next_element_id
  - _recover_workflow_state
  - _persist_workflow_state
  - _execute_task_element_events
  - _execute_condition_element_events
  - _execute_loop_element_events
  - _execute_subworkflow_element_events
  - _get_task_next_element_id
  - _get_condition_next_element_id
  - _get_loop_next_element_id
  - _get_subworkflow_next_element_id

### 3. 聊天执行器 (ChatExecutor)
- 职责：执行聊天模式
- 方法：
  - chat_run
  - _process_chat_turn

### 4. 步骤执行器 (StepExecutor)
- 职责：执行单个步骤
- 方法：
  - _execute_step
  - _execute_tool_with_permission_check
  - _parse_tool_call
  - _assess_tool_risk

### 5. 状态管理器 (StateManager)
- 职责：管理执行器状态
- 方法：
  - _change_state
  - get_status

## 重构步骤

### 第一阶段：创建专门的类
1. 创建SessionManager类
2. 创建WorkflowExecutor类
3. 创建ChatExecutor类
4. 创建StepExecutor类
5. 创建StateManager类

### 第二阶段：迁移方法和属性
1. 将会话相关的方法和属性迁移到SessionManager
2. 将工作流相关的方法和属性迁移到WorkflowExecutor
3. 将聊天相关的方法和属性迁移到ChatExecutor
4. 将步骤执行相关的方法和属性迁移到StepExecutor
5. 将状态管理相关的方法和属性迁移到StateManager

### 第三阶段：更新AgentExecutor
1. 修改AgentExecutor以使用这些新类
2. 确保所有功能保持不变
3. 运行所有测试确保没有破坏现有功能

## 设计原则
- 遵循KISS原则：保持每个类简单明了
- 遵循YAGNI原则：只实现当前需要的功能
- 遵循SOLID原则：特别是单一职责原则和依赖倒置原则
- 遵循开闭原则：对扩展开放，对修改关闭