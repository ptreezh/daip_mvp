import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class WorkflowElementType(Enum):
    """工作流元素类型枚举"""
    TASK = "task"
    CONDITION = "condition"
    LOOP = "loop"
    SUBWORKFLOW = "subworkflow"


@dataclass
class WorkflowElement:
    """工作流元素基类"""
    id: str
    type: WorkflowElementType
    name: str
    description: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    next_elements: List[str] = field(default_factory=list)
    data_inputs: Dict[str, str] = field(default_factory=dict)  # 数据输入映射: 参数名 -> 前驱元素输出引用
    data_outputs: List[str] = field(default_factory=list)  # 数据输出列表
    logging: bool = True  # 是否启用日志记录


@dataclass
class TaskElement(WorkflowElement):
    """任务元素"""
    role: Optional[str] = None
    timeout: Optional[int] = None
    retry_count: int = 0
    parallel: bool = False
    retry_delay: int = 0  # 重试延迟（秒）
    permissions: List[str] = field(default_factory=list)  # 所需权限


@dataclass
class ConditionElement(WorkflowElement):
    """条件分支元素"""
    condition_expression: str = ""
    branches: Dict[str, List[str]] = field(default_factory=dict)  # 条件值到下一元素列表的映射


@dataclass
class LoopElement(WorkflowElement):
    """循环元素"""
    loop_condition: str = ""
    max_iterations: int = 100
    loop_variable: Optional[str] = None


@dataclass
class SubWorkflowElement(WorkflowElement):
    """子工作流元素"""
    workflow_ref: str = ""  # 引用的子工作流名称或路径


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    elements: Dict[str, WorkflowElement] = field(default_factory=dict)
    start_element: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    data_flow: Dict[str, Dict[str, str]] = field(default_factory=dict)  # 数据流定义: element_id -> {output_name -> target_element_id.input_name}
    persistence: bool = True  # 是否启用持久化
    logging: bool = True  # 是否启用日志记录
    permissions: List[str] = field(default_factory=list)  # 工作流所需权限


class WorkflowParser:
    """YAML工作流定义解析器"""
    
    @staticmethod
    def parse_task(element_id: str, element_data: Dict[str, Any]) -> TaskElement:
        """解析任务元素"""
        return TaskElement(
            id=element_id,
            type=WorkflowElementType.TASK,
            name=element_data.get("name", element_id),
            description=element_data.get("description"),
            dependencies=element_data.get("dependencies", []),
            properties=element_data.get("properties", {}),
            next_elements=element_data.get("next", []),
            data_inputs=element_data.get("data_inputs", {}),
            data_outputs=element_data.get("data_outputs", []),
            role=element_data.get("role"),
            timeout=element_data.get("timeout"),
            retry_count=element_data.get("retry_count", 0),
            parallel=element_data.get("parallel", False),
            retry_delay=element_data.get("retry_delay", 0),
            permissions=element_data.get("permissions", []),
            logging=element_data.get("logging", True)
        )
    
    @staticmethod
    def parse_condition(element_id: str, element_data: Dict[str, Any]) -> ConditionElement:
        """解析条件元素"""
        return ConditionElement(
            id=element_id,
            type=WorkflowElementType.CONDITION,
            name=element_data.get("name", element_id),
            description=element_data.get("description"),
            dependencies=element_data.get("dependencies", []),
            properties=element_data.get("properties", {}),
            next_elements=element_data.get("next", []),
            data_inputs=element_data.get("data_inputs", {}),
            data_outputs=element_data.get("data_outputs", []),
            condition_expression=element_data.get("condition", ""),
            branches=element_data.get("branches", {}),
            logging=element_data.get("logging", True)
        )
    
    @staticmethod
    def parse_loop(element_id: str, element_data: Dict[str, Any]) -> LoopElement:
        """解析循环元素"""
        return LoopElement(
            id=element_id,
            type=WorkflowElementType.LOOP,
            name=element_data.get("name", element_id),
            description=element_data.get("description"),
            dependencies=element_data.get("dependencies", []),
            properties=element_data.get("properties", {}),
            next_elements=element_data.get("next", []),
            data_inputs=element_data.get("data_inputs", {}),
            data_outputs=element_data.get("data_outputs", []),
            loop_condition=element_data.get("condition", ""),
            max_iterations=element_data.get("max_iterations", 100),
            loop_variable=element_data.get("variable"),
            logging=element_data.get("logging", True)
        )
    
    @staticmethod
    def parse_subworkflow(element_id: str, element_data: Dict[str, Any]) -> SubWorkflowElement:
        """解析子工作流元素"""
        return SubWorkflowElement(
            id=element_id,
            type=WorkflowElementType.SUBWORKFLOW,
            name=element_data.get("name", element_id),
            description=element_data.get("description"),
            dependencies=element_data.get("dependencies", []),
            properties=element_data.get("properties", {}),
            next_elements=element_data.get("next", []),
            data_inputs=element_data.get("data_inputs", {}),
            data_outputs=element_data.get("data_outputs", []),
            workflow_ref=element_data.get("workflow_ref", ""),
            logging=element_data.get("logging", True)
        )
    
    @staticmethod
    def parse_element(element_id: str, element_data: Dict[str, Any]) -> WorkflowElement:
        """解析工作流元素"""
        element_type = element_data.get("type", "").lower()
        
        if element_type == "task":
            return WorkflowParser.parse_task(element_id, element_data)
        elif element_type == "condition":
            return WorkflowParser.parse_condition(element_id, element_data)
        elif element_type == "loop":
            return WorkflowParser.parse_loop(element_id, element_data)
        elif element_type == "subworkflow":
            return WorkflowParser.parse_subworkflow(element_id, element_data)
        else:
            # 默认作为任务元素处理
            return WorkflowParser.parse_task(element_id, element_data)
    
    @staticmethod
    def parse(yaml_content: str) -> WorkflowDefinition:
        """解析YAML工作流定义"""
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        
        if not isinstance(data, dict):
            raise ValueError("Invalid workflow definition format")
        
        # 解析工作流基本信息
        workflow_name = data.get("name")
        if not workflow_name:
            raise ValueError("Workflow name is required")
        
        workflow = WorkflowDefinition(
            name=workflow_name,
            version=data.get("version", "1.0.0"),
            description=data.get("description"),
            start_element=data.get("start", ""),
            variables=data.get("variables", {}),
            data_flow=data.get("data_flow", {}),
            persistence=data.get("persistence", True),
            logging=data.get("logging", True),
            permissions=data.get("permissions", [])
        )
        
        # 解析工作流元素
        elements_data = data.get("elements", {})
        if not isinstance(elements_data, dict):
            raise ValueError("Invalid elements format")
        
        for element_id, element_data in elements_data.items():
            if not isinstance(element_data, dict):
                raise ValueError(f"Invalid element format for {element_id}")
            
            element = WorkflowParser.parse_element(element_id, element_data)
            workflow.elements[element_id] = element
        
        # 如果没有指定起始元素，使用第一个元素
        if not workflow.start_element and workflow.elements:
            workflow.start_element = next(iter(workflow.elements))
        
        return workflow