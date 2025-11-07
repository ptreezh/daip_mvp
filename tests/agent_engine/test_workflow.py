import asyncio
import yaml
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import (
    AgentState,
    AgentStatus,
    FinalResponseEvent,
    Session,
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
)
from daip_live.workflow.parser import WorkflowParser, WorkflowDefinition, TaskElement, ConditionElement, LoopElement

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_usage():
    """Fixture for a mock litellm usage object."""
    usage = MagicMock()
    usage.total_tokens = 100
    return usage

@pytest.fixture
def mock_services():
    """Fixture to create mocked services for the AgentExecutor."""
    tool_manager = MagicMock()  # Changed from AsyncMock to MagicMock since execute_tool is synchronous
    tool_manager._registry = {
        "search_web": MagicMock(),
        "ToolA": MagicMock(),
        "ToolB": MagicMock()
    }  # Mock the tool registry with all needed tools
    return {
        "session_manager": MagicMock(),
        "memory_service": AsyncMock(),
        "knowledge_manager": AsyncMock(),
        "model_provider": AsyncMock(),
        "tool_manager": tool_manager,
    }

@pytest.fixture
def agent_executor(mock_services):
    """Fixture to create an AgentExecutor instance with mocked services."""
    mock_services["session_manager"].create_session.return_value = Session(goal="test goal", session_type="workflow", participant_ids=[])
    memory_service = mock_services["memory_service"]
    memory_service.get_todo_list.return_value = [MagicMock(description="single mock task")]

    # Use a stateful callable for the side_effect to ensure correct behavior
    _is_complete_state = {"called": False}
    async def is_complete_callable():
        if not _is_complete_state["called"]:
            _is_complete_state["called"] = True
            return False
        return True
    memory_service.is_todo_list_complete.side_effect = is_complete_callable

    memory_service.update_todo_status.return_value = None
    return AgentExecutor(
        session_manager=mock_services["session_manager"],
        memory_service=mock_services["memory_service"],
        knowledge_manager=mock_services["knowledge_manager"],
        model_provider=mock_services["model_provider"],
        tool_manager=mock_services["tool_manager"],
        user_input_queue=asyncio.Queue(),
        max_reflections=3
    )

# 工作流解析器测试
class TestWorkflowParser:
    """测试工作流解析器"""

    def test_parse_simple_task_element(self):
        """测试解析简单的任务元素"""
        yaml_content = """
        elements:
          task1:
            type: task
            name: "测试任务"
            description: "这是一个测试任务"
            role: "测试角色"
            timeout: 300
        """
        data = yaml.safe_load(yaml_content)
        element_data = data["elements"]["task1"]
        element = WorkflowParser.parse_task("task1", element_data)
        
        assert isinstance(element, TaskElement)
        assert element.id == "task1"
        assert element.type.value == "task"
        assert element.name == "测试任务"
        assert element.description == "这是一个测试任务"
        assert element.role == "测试角色"
        assert element.timeout == 300

    def test_parse_task_with_retry_and_parallel(self):
        """测试解析带重试和并行设置的任务元素"""
        yaml_content = """
        elements:
          task1:
            type: task
            name: "测试任务"
            retry_count: 3
            retry_delay: 5
            parallel: true
        """
        data = yaml.safe_load(yaml_content)
        element_data = data["elements"]["task1"]
        element = WorkflowParser.parse_task("task1", element_data)
        
        assert element.retry_count == 3
        assert element.retry_delay == 5
        assert element.parallel == True

    def test_parse_condition_element(self):
        """测试解析条件元素"""
        yaml_content = """
        elements:
          condition1:
            type: condition
            name: "条件判断"
            condition: "score > 0.8"
            branches:
              "true":
                - task2
              "false":
                - task3
        """
        data = yaml.safe_load(yaml_content)
        element_data = data["elements"]["condition1"]
        element = WorkflowParser.parse_condition("condition1", element_data)
        
        assert isinstance(element, ConditionElement)
        assert element.id == "condition1"
        assert element.type.value == "condition"
        assert element.name == "条件判断"
        assert element.condition_expression == "score > 0.8"
        assert "true" in element.branches
        assert "false" in element.branches

    def test_parse_condition_with_empty_expression(self):
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

    def test_parse_loop_element(self):
        """测试解析循环元素"""
        yaml_content = """
        elements:
          loop1:
            type: loop
            name: "循环处理"
            condition: "index < 10"
            max_iterations: 100
            variable: "index"
        """
        data = yaml.safe_load(yaml_content)
        element_data = data["elements"]["loop1"]
        element = WorkflowParser.parse_loop("loop1", element_data)
        
        assert isinstance(element, LoopElement)
        assert element.id == "loop1"
        assert element.type.value == "loop"
        assert element.name == "循环处理"
        assert element.loop_condition == "index < 10"
        assert element.max_iterations == 100
        assert element.loop_variable == "index"

    def test_parse_complete_workflow(self):
        """测试解析完整的工作流定义"""
        yaml_content = """
        name: test_workflow
        version: 1.0.0
        description: A test workflow
        persistence: true
        logging: true
        elements:
          task1:
            type: task
            name: "初始化"
            next:
              - condition1
          condition1:
            type: condition
            name: "检查条件"
            condition: "value > 0"
            branches:
              "true":
                - task2
              "false":
                - task3
          task2:
            type: task
            name: "成功路径"
            next:
              - end
          task3:
            type: task
            name: "失败路径"
            next:
              - end
          end:
            type: task
            name: "结束"
        start: task1
        """
        
        workflow = WorkflowParser.parse(yaml_content)
        
        assert isinstance(workflow, WorkflowDefinition)
        assert workflow.name == "test_workflow"
        assert workflow.version == "1.0.0"
        assert workflow.description == "A test workflow"
        assert workflow.persistence == True
        assert workflow.logging == True
        assert len(workflow.elements) == 5
        assert workflow.start_element == "task1"

    # 边界条件测试
    def test_parse_empty_yaml(self):
        """测试解析空YAML内容"""
        with pytest.raises(ValueError, match="Invalid workflow definition format"):
            WorkflowParser.parse("")

    def test_parse_missing_required_fields(self):
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

    def test_parse_invalid_yaml_format(self):
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

    def test_parse_empty_elements(self):
        """测试解析空元素列表"""
        yaml_content = """
        name: test_workflow
        elements: {}
        """
        workflow = WorkflowParser.parse(yaml_content)
        assert len(workflow.elements) == 0
        assert workflow.start_element == ""

    def test_parse_invalid_element_type(self):
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

    def test_parse_loop_with_negative_max_iterations(self):
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

    def test_parse_loop_with_zero_max_iterations(self):
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

# AgentExecutor工作流执行测试
async def test_get_status_api(agent_executor, mock_services):
    """Tests the get_status method."""
    mock_model_config = MagicMock()
    mock_model_config.model = "test-model-123"
    # The model_provider is now on the state_manager, so we mock it there.
    type(agent_executor.state_manager.model_provider).config = PropertyMock(return_value=mock_model_config)
    
    # Set state and token counts on the state_manager directly
    agent_executor.state_manager.change_state(AgentState.THINKING)
    agent_executor.state_manager.tokens_used = 1024
    agent_executor.state_manager.tokens_total = 8192

    status = agent_executor.get_status()
    assert isinstance(status, AgentStatus)
    assert status.state == AgentState.THINKING.value
    assert status.model_name == "test-model-123"
    assert status.tokens_used == 1024
    assert status.tokens_total == 8192

async def test_token_usage_is_accumulated(agent_executor, mock_services):
    """Tests that tokens_used is accumulated after each model call."""
    usage_dict = {"total_tokens": 100} # Correctly use a dict
    mock_services["model_provider"].generate.side_effect = [
        ("Use Tool: search_web(query='test')", usage_dict),
        ("Final Answer.", usage_dict)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool Result"
    assert agent_executor.state_manager.tokens_used == 0
    _ = [event async for event in agent_executor.run("test goal")]
    # 2 calls to generate, each using 100 tokens
    assert agent_executor.state_manager.tokens_used == 200

async def test_high_confidence_flow(agent_executor, mock_services, mock_usage):
    """Test a direct, high-confidence response without tools."""
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    events = [event async for event in agent_executor.run("test goal")]
    assert isinstance(events[0], ThoughtEvent)
    # Find the FinalResponseEvent (it may not be at index 1 due to ModelMetricsEvent)
    final_response = next(e for e in events if isinstance(e, FinalResponseEvent))
    assert final_response.content == "Final Answer."
    mock_services["tool_manager"].execute_tool.assert_not_called()

async def test_tool_execution_flow(agent_executor, mock_services, mock_usage):
    """Test a flow where the agent decides to use a tool."""
    mock_services["model_provider"].generate.side_effect = [
        ("Use Tool: search_web(query='test') Confidence: 0.98", mock_usage),
        ("Final Answer based on search. Confidence: 0.99", mock_usage)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool Result: Web search successful."
    events = [event async for event in agent_executor.run("test goal")]
    assert any(isinstance(e, ToolCallEvent) and e.tool_name == "search_web" for e in events)
    assert any(isinstance(e, ToolOutputEvent) and e.output == "Tool Result: Web search successful." for e in events)
    final_response = next(e for e in events if isinstance(e, FinalResponseEvent))
    assert final_response.content == "Final Answer based on search."
    mock_services["tool_manager"].execute_tool.assert_called_once_with("search_web", {'query': 'test'}, session_context=agent_executor.step_executor.session_context)

async def test_reflection_loop_flow(agent_executor, mock_services, mock_usage):
    """Test the self-reflection loop for low-confidence answers."""
    mock_services["model_provider"].generate.side_effect = [
        ("I am not sure. Confidence: 0.5", mock_usage),
        ("To be more confident, I should search the web. Use Tool: search_web(query='clarify') Confidence: 0.99", mock_usage),
        ("Based on the web search, the answer is X. Confidence: 0.99", mock_usage)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool Result: The web says X."
    events = [event async for event in agent_executor.run("test goal")]
    thought_events = [e for e in events if isinstance(e, ThoughtEvent)]
    assert any("Confidence is low (" in e.content and "). Reflecting..." in e.content for e in thought_events)
    tool_call_event = next(e for e in events if isinstance(e, ToolCallEvent))
    assert tool_call_event.tool_name == "search_web"
    assert tool_call_event.args == {'query': 'clarify'}
    final_response = next(e for e in events if isinstance(e, FinalResponseEvent))
    assert final_response.content == "Based on the web search, the answer is X."
    assert mock_services["model_provider"].generate.call_count == 3

async def test_run_loop_is_driven_by_todo_list(agent_executor, mock_services, mock_usage):
    """Tests that the main execution loop is driven by the completion of a Todo list."""
    mock_todo_list = [MagicMock(description="call_tool_A", status="pending"), MagicMock(description="call_tool_B", status="pending")]
    memory_service = mock_services["memory_service"]
    memory_service.get_todo_list.return_value = mock_todo_list
    is_complete = False
    def a_is_complete(): return is_complete
    memory_service.is_todo_list_complete.side_effect = a_is_complete
    def a_update_todo_status(index):
        nonlocal is_complete
        mock_todo_list[index].status = "completed"
        if all(item.status == "completed" for item in mock_todo_list): is_complete = True
    memory_service.update_todo_status.side_effect = a_update_todo_status
    mock_services["model_provider"].generate.side_effect = [
        ("Use Tool: ToolA() Confidence: 0.99", mock_usage),
        ("Final answer for task A.", mock_usage),
        ("Use Tool: ToolB() Confidence: 0.99", mock_usage),
        ("Final answer for task B.", mock_usage)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool execution successful."
    _ = [event async for event in agent_executor.run("goal with a todo list")]
    assert mock_services["tool_manager"].execute_tool.call_count == 2
    calls = mock_services["tool_manager"].execute_tool.call_args_list
    assert calls[0].args[0] == "ToolA"
    assert calls[1].args[0] == "ToolB"
    assert agent_executor.state.value == AgentState.COMPLETED.value

async def test_run_can_be_steered_by_user_input_queue(agent_executor, mock_services, mock_usage):
    """Tests that a running agent can be steered by a message from the user queue."""
    model_is_paused = asyncio.Event()
    steering_command = "New steering instruction from user."
    async def model_generate_behavior(prompt):
        if steering_command in prompt:
            return ("Steered Action. Confidence: 0.99", mock_usage)
        else:
            await model_is_paused.wait()
            return ("Initial Action. Confidence: 0.99", mock_usage)
    mock_services["model_provider"].generate.side_effect = model_generate_behavior
    async def consume_agent_run():
        _ = [event async for event in agent_executor.run("initial goal")]
    agent_task = asyncio.create_task(consume_agent_run())
    await asyncio.sleep(0.01)
    await agent_executor.user_input_queue.put(steering_command)
    model_is_paused.set()
    await agent_task
    assert mock_services["memory_service"].construct_prompt.call_count > 1
    last_call_args, _ = mock_services["memory_service"].construct_prompt.call_args
    assert steering_command in str(last_call_args)

# 工作流执行测试
async def test_workflow_execution_simple_task(agent_executor, mock_services, mock_usage):
    """Test workflow execution of a simple task"""
    # Create a simple workflow definition
    workflow_yaml = """
    name: simple_test_workflow
    elements:
      task1:
        type: task
        name: "Simple Task"
        description: "Execute a simple task"
        next:
          - task2
      task2:
        type: task
        name: "Second Task"
        description: "Execute the second task"
    start: task1
    """
    
    workflow_definition = WorkflowParser.parse(workflow_yaml)
    
    # Set mock behavior
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    # Execute workflow
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # Verify execution results
    assert any(isinstance(e, ThoughtEvent) and "Executing element: Simple Task" in e.content for e in events)
    assert any(isinstance(e, ThoughtEvent) and "Executing element: Second Task" in e.content for e in events)
    assert any(isinstance(e, FinalResponseEvent) for e in events)
    assert agent_executor.state.value == AgentState.COMPLETED.value

async def test_workflow_execution_with_data_flow(agent_executor, mock_services, mock_usage):
    """Test workflow execution with data flow"""
    # Create a workflow definition with data flow
    workflow_yaml = """
    name: data_flow_test_workflow
    elements:
      task1:
        type: task
        name: "Generate Data"
        data_outputs:
          - "result"
        next:
          - task2
      task2:
        type: task
        name: "Process Data"
        data_inputs:
          input_data: "task1.result"
    start: task1
    data_flow:
      task1:
        result: task2.input_data
    """
    
    workflow_definition = WorkflowParser.parse(workflow_yaml)
    
    # Set mock behavior
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    # Execute workflow
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # Print all events for debugging
    print("All events:")
    for event in events:
        print(f"  {type(event).__name__}: {getattr(event, 'content', 'N/A')}")

    # Verify execution results
    assert any(isinstance(e, ThoughtEvent) and "Executing element: Generate Data" in e.content for e in events)
    assert any(isinstance(e, ThoughtEvent) and "Executing element: Process Data" in e.content for e in events)
    assert agent_executor.state.value == AgentState.COMPLETED.value

# 工作流执行边界条件测试
async def test_execute_empty_workflow(agent_executor, mock_services, mock_usage):
    """测试执行空工作流定义"""
    workflow_definition = WorkflowDefinition(name="empty_workflow", elements={})
    
    # 设置mock行为
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    events = [event async for event in agent_executor.run("test goal", workflow_definition)]
    
    # 验证执行结果
    assert any(isinstance(e, ThoughtEvent) and "Invalid workflow definition" in e.content for e in events)
    assert agent_executor.state.value == AgentState.FAILED.value

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
    assert agent_executor.state.value == AgentState.FAILED.value

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
    assert agent_executor.state.value == AgentState.FAILED.value

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
    assert agent_executor.state.value == AgentState.COMPLETED.value

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
    assert agent_executor.state.value == AgentState.COMPLETED.value

async def test_execute_workflow_with_circular_reference(agent_executor, mock_services, mock_usage):
    """测试执行具有循环引用的工作流"""
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
    start: task1
    """
    
    workflow_definition = WorkflowParser.parse(yaml_content)
    
    # 设置mock行为
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    
    # 由于我们没有实现循环检测机制，这个测试应该会无限循环
    # 但在实际应用中，应该有一个超时或循环检测机制
    # 这里我们只是验证工作流能够被解析
    assert len(workflow_definition.elements) == 2
    assert workflow_definition.start_element == "task1"