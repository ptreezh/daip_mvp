# 边界条件测试计划

## 1. 工作流解析器边界条件测试

### 1.1 空YAML内容解析
```python
def test_parse_empty_yaml():
    """测试解析空YAML内容"""
    with pytest.raises(ValueError, match="Invalid workflow definition format"):
        WorkflowParser.parse("")
```

### 1.2 缺少必需字段的工作流定义
```python
def test_parse_missing_required_fields():
    """测试缺少必需字段的工作流定义"""
    yaml_content = """
    version: 1.0.0
    elements:
      task1:
        type: task
        name: "Test Task"
    """
    with pytest.raises(ValueError, match="Workflow name is required"):
        WorkflowParser.parse(yaml_content)
```

### 1.3 无效的YAML格式
```python
def test_parse_invalid_yaml_format():
    """测试解析无效的YAML格式"""
    yaml_content = """
    name: test_workflow
    elements:
      task1:
        type: task
        name: "Test Task"
      # Invalid indentation
       task2:
         type: task
         name: "Another Task"
    """
    with pytest.raises(ValueError, match="Invalid YAML format"):
        WorkflowParser.parse(yaml_content)
```

### 1.4 空元素列表
```python
def test_parse_empty_elements():
    """测试解析空元素列表"""
    yaml_content = """
    name: test_workflow
    elements: {}
    """
    workflow = WorkflowParser.parse(yaml_content)
    assert len(workflow.elements) == 0
    assert workflow.start_element == ""
```

### 1.5 无效元素类型
```python
def test_parse_invalid_element_type():
    """测试解析无效元素类型"""
    yaml_content = """
    name: test_workflow
    elements:
      invalid_element:
        type: invalid_type
        name: "Invalid Element"
    """
    # 应该默认作为任务元素处理
    workflow = WorkflowParser.parse(yaml_content)
    element = workflow.elements["invalid_element"]
    assert isinstance(element, TaskElement)
```

### 1.6 循环引用检测
```python
def test_parse_circular_reference():
    """测试解析循环引用"""
    yaml_content = """
    name: test_workflow
    elements:
      task1:
        type: task
        name: "Task 1"
        next:
          - task2
      task2:
        type: task
        name: "Task 2"
        next:
          - task1
    """
    # 应该能够解析，但在执行时检测循环
    workflow = WorkflowParser.parse(yaml_content)
    assert "task1" in workflow.elements
    assert "task2" in workflow.elements
```

## 2. 工作流执行器边界条件测试

### 2.1 空工作流定义执行
```python
async def test_execute_empty_workflow(agent_executor, mock_services, mock_usage):
    """测试执行空工作流定义"""
    workflow_definition = WorkflowDefinition(name="empty_workflow", elements={})
    
    # 设置mock行为
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # 验证执行结果
    assert any(isinstance(e, ThoughtEvent) and "Invalid workflow definition" in e.content for e in events)
    assert agent_executor.state == AgentState.FAILED
```

### 2.2 无效起始元素
```python
async def test_execute_invalid_start_element(agent_executor, mock_services, mock_usage):
    """测试执行无效起始元素"""
    yaml_content = """
    name: test_workflow
    start: nonexistent_task
    elements:
      task1:
        type: task
        name: "Task 1"
    """
    
    workflow_definition = WorkflowParser.parse(yaml_content)
    
    # 设置mock行为
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # 验证执行结果
    assert any(isinstance(e, ThoughtEvent) and "Element nonexistent_task not found" in e.content for e in events)
    assert agent_executor.state == AgentState.FAILED
```

### 2.3 元素ID不存在
```python
async def test_execute_nonexistent_element_id(agent_executor, mock_services, mock_usage):
    """测试执行不存在的元素ID"""
    yaml_content = """
    name: test_workflow
    elements:
      task1:
        type: task
        name: "Task 1"
        next:
          - nonexistent_task
    start: task1
    """
    
    workflow_definition = WorkflowParser.parse(yaml_content)
    
    # 设置mock行为
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # 验证执行结果
    assert any(isinstance(e, ThoughtEvent) and "Element nonexistent_task not found" in e.content for e in events)
    assert agent_executor.state == AgentState.FAILED
```

## 3. 数据流边界条件测试

### 3.1 空数据输入/输出
```python
async def test_execute_workflow_with_empty_data_flow(agent_executor, mock_services, mock_usage):
    """测试执行具有空数据流的工作流"""
    yaml_content = """
    name: test_workflow
    elements:
      task1:
        type: task
        name: "Task 1"
        data_outputs: []
        next:
          - task2
      task2:
        type: task
        name: "Task 2"
        data_inputs: {}
    start: task1
    data_flow: {}
    """
    
    workflow_definition = WorkflowParser.parse(yaml_content)
    
    # 设置mock行为
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # 验证执行结果
    assert agent_executor.state == AgentState.COMPLETED
```

### 3.2 无效数据引用
```python
async def test_execute_workflow_with_invalid_data_reference(agent_executor, mock_services, mock_usage):
    """测试执行具有无效数据引用的工作流"""
    yaml_content = """
    name: test_workflow
    elements:
      task1:
        type: task
        name: "Task 1"
        next:
          - task2
      task2:
        type: task
        name: "Task 2"
        data_inputs:
          input_data: "nonexistent_task.result"
    start: task1
    data_flow:
      nonexistent_task:
        result: task2.input_data
    """
    
    workflow_definition = WorkflowParser.parse(yaml_content)
    
    # 设置mock行为
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # 验证执行结果（应该能正常执行，只是数据为空）
    assert agent_executor.state == AgentState.COMPLETED
```

## 4. 条件分支边界条件测试

### 4.1 空条件表达式
```python
def test_parse_condition_with_empty_expression():
    """测试解析具有空条件表达式的条件元素"""
    yaml_content = """
    elements:
      condition1:
        type: condition
        name: "Empty Condition"
        condition: ""
        branches:
          "true":
            - task2
    """
    data = yaml.safe_load(yaml_content)
    element_data = data["elements"]["condition1"]
    element = WorkflowParser.parse_condition("condition1", element_data)
    
    assert element.condition_expression == ""
```

### 4.2 无效条件表达式
```python
def test_parse_condition_with_invalid_expression():
    """测试解析具有无效条件表达式的条件元素"""
    yaml_content = """
    elements:
      condition1:
        type: condition
        name: "Invalid Condition"
        condition: "invalid expression @@@"
        branches:
          "true":
            - task2
    """
    data = yaml.safe_load(yaml_content)
    element_data = data["elements"]["condition1"]
    element = WorkflowParser.parse_condition("condition1", element_data)
    
    assert element.condition_expression == "invalid expression @@@"
```

## 5. 循环元素边界条件测试

### 5.1 负数最大迭代次数
```python
def test_parse_loop_with_negative_max_iterations():
    """测试解析具有负数最大迭代次数的循环元素"""
    yaml_content = """
    elements:
      loop1:
        type: loop
        name: "Negative Loop"
        condition: "index < 10"
        max_iterations: -5
        variable: "index"
    """
    data = yaml.safe_load(yaml_content)
    element_data = data["elements"]["loop1"]
    element = WorkflowParser.parse_loop("loop1", element_data)
    
    assert element.max_iterations == -5
```

### 5.2 零迭代次数
```python
def test_parse_loop_with_zero_max_iterations():
    """测试解析具有零最大迭代次数的循环元素"""
    yaml_content = """
    elements:
      loop1:
        type: loop
        name: "Zero Loop"
        condition: "index < 10"
        max_iterations: 0
        variable: "index"
    """
    data = yaml.safe_load(yaml_content)
    element_data = data["elements"]["loop1"]
    element = WorkflowParser.parse_loop("loop1", element_data)
    
    assert element.max_iterations == 0
```

## 实施优先级

1. **高优先级**（直接影响功能正确性）：
   - 空YAML内容解析
   - 缺少必需字段的工作流定义
   - 无效的YAML格式
   - 空工作流定义执行
   - 无效起始元素

2. **中优先级**（影响健壮性）：
   - 无效元素类型
   - 元素ID不存在
   - 空数据输入/输出
   - 负数最大迭代次数

3. **低优先级**（边缘情况）：
   - 循环引用检测
   - 无效数据引用
   - 空条件表达式
   - 零迭代次数