"""
场景管理器

创建真实业务场景定义，支持用户自定义场景输入，管理场景执行流程。
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """场景类型"""
    AI_ETHICS = "ai_ethics"
    PRODUCT_STRATEGY = "product_strategy"
    TECHNICAL_RISK = "technical_risk"
    MARKET_ANALYSIS = "market_analysis"
    CUSTOM = "custom"


class ScenarioStatus(Enum):
    """场景状态"""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScenarioParameter:
    """场景参数"""
    name: str
    type: str  # string, number, boolean, list, dict
    description: str
    required: bool = True
    default_value: Any = None
    validation_rules: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioDefinition:
    """场景定义"""
    scenario_id: str
    name: str
    description: str
    scenario_type: ScenarioType
    parameters: List[ScenarioParameter]
    required_roles: List[str]
    workflow_steps: List[Dict[str, Any]]
    expected_outputs: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['scenario_type'] = self.scenario_type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['parameters'] = [param.to_dict() for param in self.parameters]
        return data


@dataclass
class ScenarioInstance:
    """场景实例"""
    instance_id: str
    scenario_id: str
    name: str
    status: ScenarioStatus
    parameter_values: Dict[str, Any]
    assigned_roles: List[str]
    execution_log: List[Dict[str, Any]]
    results: Optional[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


class ScenarioManager:
    """
    场景管理器
    
    负责创建、管理和执行各种业务场景，支持用户自定义场景输入。
    """
    
    def __init__(self):
        """初始化场景管理器"""
        self.scenario_definitions: Dict[str, ScenarioDefinition] = {}
        self.scenario_instances: Dict[str, ScenarioInstance] = {}
        
        # 初始化内置场景
        self._initialize_builtin_scenarios()
        
        logger.info("ScenarioManager initialized")
    
    def _initialize_builtin_scenarios(self):
        """初始化内置场景"""
        # AI伦理决策分析场景
        ai_ethics_scenario = ScenarioDefinition(
            scenario_id="ai_ethics_analysis",
            name="AI伦理决策分析",
            description="分析AI系统的伦理困境，提供决策建议和风险评估",
            scenario_type=ScenarioType.AI_ETHICS,
            parameters=[
                ScenarioParameter(
                    name="ethical_dilemma",
                    type="string",
                    description="需要分析的伦理困境描述",
                    required=True,
                    validation_rules={"min_length": 50, "max_length": 2000}
                ),
                ScenarioParameter(
                    name="stakeholders",
                    type="list",
                    description="利益相关者列表",
                    required=False,
                    default_value=["用户", "开发者", "监管机构", "社会公众"]
                ),
                ScenarioParameter(
                    name="ethical_frameworks",
                    type="list",
                    description="应用的伦理框架",
                    required=False,
                    default_value=["功利主义", "义务论", "美德伦理学"]
                ),
                ScenarioParameter(
                    name="industry_context",
                    type="string",
                    description="行业背景",
                    required=False,
                    default_value="通用AI应用"
                )
            ],
            required_roles=["AI Ethics", "economist", "legal_expert"],
            workflow_steps=[
                {"step": "critical_review", "description": "批判性审查伦理困境"},
                {"step": "multi_perspective", "description": "多视角分析"},
                {"step": "synthesis", "description": "综合分析和建议生成"}
            ],
            expected_outputs=[
                "伦理风险评估报告",
                "利益相关者分析",
                "决策建议",
                "实施指导"
            ],
            metadata={"complexity": "high", "duration_estimate": "15-30分钟"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 产品策略评估场景
        product_strategy_scenario = ScenarioDefinition(
            scenario_id="product_strategy_evaluation",
            name="产品策略评估",
            description="评估产品策略的可行性、市场机会和风险",
            scenario_type=ScenarioType.PRODUCT_STRATEGY,
            parameters=[
                ScenarioParameter(
                    name="product_description",
                    type="string",
                    description="产品详细描述",
                    required=True,
                    validation_rules={"min_length": 100, "max_length": 3000}
                ),
                ScenarioParameter(
                    name="target_market",
                    type="string",
                    description="目标市场描述",
                    required=True
                ),
                ScenarioParameter(
                    name="business_model",
                    type="string",
                    description="商业模式",
                    required=False,
                    default_value="待定"
                ),
                ScenarioParameter(
                    name="competitors",
                    type="list",
                    description="主要竞争对手",
                    required=False,
                    default_value=[]
                ),
                ScenarioParameter(
                    name="budget_range",
                    type="string",
                    description="预算范围",
                    required=False
                )
            ],
            required_roles=["product_manager", "economist", "market_analyst"],
            workflow_steps=[
                {"step": "market_analysis", "description": "市场分析"},
                {"step": "competitive_analysis", "description": "竞争分析"},
                {"step": "risk_assessment", "description": "风险评估"},
                {"step": "strategy_synthesis", "description": "策略综合"}
            ],
            expected_outputs=[
                "市场机会评估",
                "竞争优势分析",
                "风险识别与缓解",
                "实施路线图"
            ],
            metadata={"complexity": "medium", "duration_estimate": "10-20分钟"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 技术风险评估场景
        technical_risk_scenario = ScenarioDefinition(
            scenario_id="technical_risk_assessment",
            name="技术风险评估",
            description="评估技术项目的风险和可行性",
            scenario_type=ScenarioType.TECHNICAL_RISK,
            parameters=[
                ScenarioParameter(
                    name="technology_description",
                    type="string",
                    description="技术或项目描述",
                    required=True,
                    validation_rules={"min_length": 50, "max_length": 2000}
                ),
                ScenarioParameter(
                    name="technical_complexity",
                    type="string",
                    description="技术复杂度",
                    required=False,
                    default_value="中等",
                    validation_rules={"enum": ["低", "中等", "高", "极高"]}
                ),
                ScenarioParameter(
                    name="timeline",
                    type="string",
                    description="项目时间线",
                    required=False
                ),
                ScenarioParameter(
                    name="team_size",
                    type="number",
                    description="团队规模",
                    required=False,
                    default_value=5
                )
            ],
            required_roles=["technical_architect", "project_manager", "quality_assurance"],
            workflow_steps=[
                {"step": "technical_analysis", "description": "技术可行性分析"},
                {"step": "risk_identification", "description": "风险识别"},
                {"step": "mitigation_planning", "description": "缓解策略规划"}
            ],
            expected_outputs=[
                "技术可行性报告",
                "风险矩阵",
                "缓解策略",
                "实施建议"
            ],
            metadata={"complexity": "medium", "duration_estimate": "8-15分钟"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 注册内置场景
        self.scenario_definitions[ai_ethics_scenario.scenario_id] = ai_ethics_scenario
        self.scenario_definitions[product_strategy_scenario.scenario_id] = product_strategy_scenario
        self.scenario_definitions[technical_risk_scenario.scenario_id] = technical_risk_scenario
        
        logger.info(f"Initialized {len(self.scenario_definitions)} builtin scenarios")
    
    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """获取可用场景列表"""
        return [scenario.to_dict() for scenario in self.scenario_definitions.values()]
    
    def get_scenario_definition(self, scenario_id: str) -> Optional[ScenarioDefinition]:
        """获取场景定义"""
        return self.scenario_definitions.get(scenario_id)
    
    def create_custom_scenario(
        self,
        name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        required_roles: List[str],
        workflow_steps: List[Dict[str, Any]],
        expected_outputs: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建自定义场景
        
        Args:
            name: 场景名称
            description: 场景描述
            parameters: 参数定义列表
            required_roles: 必需角色列表
            workflow_steps: 工作流步骤
            expected_outputs: 期望输出
            metadata: 元数据
            
        Returns:
            场景ID
        """
        scenario_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        # 转换参数定义
        scenario_parameters = []
        for param_dict in parameters:
            param = ScenarioParameter(
                name=param_dict["name"],
                type=param_dict["type"],
                description=param_dict["description"],
                required=param_dict.get("required", True),
                default_value=param_dict.get("default_value"),
                validation_rules=param_dict.get("validation_rules")
            )
            scenario_parameters.append(param)
        
        # 创建场景定义
        scenario = ScenarioDefinition(
            scenario_id=scenario_id,
            name=name,
            description=description,
            scenario_type=ScenarioType.CUSTOM,
            parameters=scenario_parameters,
            required_roles=required_roles,
            workflow_steps=workflow_steps,
            expected_outputs=expected_outputs,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.scenario_definitions[scenario_id] = scenario
        
        logger.info(f"Created custom scenario: {scenario_id}")
        return scenario_id
    
    def create_scenario_instance(
        self,
        scenario_id: str,
        instance_name: str,
        parameter_values: Dict[str, Any],
        assigned_roles: Optional[List[str]] = None
    ) -> str:
        """
        创建场景实例
        
        Args:
            scenario_id: 场景ID
            instance_name: 实例名称
            parameter_values: 参数值
            assigned_roles: 分配的角色
            
        Returns:
            实例ID
        """
        if scenario_id not in self.scenario_definitions:
            raise ValueError(f"Scenario not found: {scenario_id}")
        
        scenario_def = self.scenario_definitions[scenario_id]
        
        # 验证参数
        validation_result = self._validate_parameters(scenario_def, parameter_values)
        if not validation_result["valid"]:
            raise ValueError(f"Parameter validation failed: {validation_result['errors']}")
        
        # 使用分配的角色或默认角色
        roles = assigned_roles or scenario_def.required_roles
        
        instance_id = str(uuid.uuid4())
        
        instance = ScenarioInstance(
            instance_id=instance_id,
            scenario_id=scenario_id,
            name=instance_name,
            status=ScenarioStatus.READY,
            parameter_values=parameter_values,
            assigned_roles=roles,
            execution_log=[],
            results=None,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None
        )
        
        self.scenario_instances[instance_id] = instance
        
        logger.info(f"Created scenario instance: {instance_id}")
        return instance_id
    
    def _validate_parameters(
        self, 
        scenario_def: ScenarioDefinition, 
        parameter_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证参数"""
        errors = []
        
        # 检查必需参数
        for param in scenario_def.parameters:
            if param.required and param.name not in parameter_values:
                errors.append(f"Missing required parameter: {param.name}")
                continue
            
            if param.name not in parameter_values:
                # 使用默认值
                if param.default_value is not None:
                    parameter_values[param.name] = param.default_value
                continue
            
            value = parameter_values[param.name]
            
            # 类型验证
            if not self._validate_parameter_type(param, value):
                errors.append(f"Invalid type for parameter {param.name}: expected {param.type}")
            
            # 规则验证
            if param.validation_rules:
                rule_errors = self._validate_parameter_rules(param, value)
                errors.extend(rule_errors)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_parameter_type(self, param: ScenarioParameter, value: Any) -> bool:
        """验证参数类型"""
        if param.type == "string":
            return isinstance(value, str)
        elif param.type == "number":
            return isinstance(value, (int, float))
        elif param.type == "boolean":
            return isinstance(value, bool)
        elif param.type == "list":
            return isinstance(value, list)
        elif param.type == "dict":
            return isinstance(value, dict)
        else:
            return True  # 未知类型，跳过验证
    
    def _validate_parameter_rules(self, param: ScenarioParameter, value: Any) -> List[str]:
        """验证参数规则"""
        errors = []
        rules = param.validation_rules
        
        if "min_length" in rules and isinstance(value, str):
            if len(value) < rules["min_length"]:
                errors.append(f"Parameter {param.name} too short (min: {rules['min_length']})")
        
        if "max_length" in rules and isinstance(value, str):
            if len(value) > rules["max_length"]:
                errors.append(f"Parameter {param.name} too long (max: {rules['max_length']})")
        
        if "enum" in rules:
            if value not in rules["enum"]:
                errors.append(f"Parameter {param.name} must be one of: {rules['enum']}")
        
        if "min_value" in rules and isinstance(value, (int, float)):
            if value < rules["min_value"]:
                errors.append(f"Parameter {param.name} too small (min: {rules['min_value']})")
        
        if "max_value" in rules and isinstance(value, (int, float)):
            if value > rules["max_value"]:
                errors.append(f"Parameter {param.name} too large (max: {rules['max_value']})")
        
        return errors
    
    def start_scenario_execution(self, instance_id: str) -> bool:
        """开始场景执行"""
        if instance_id not in self.scenario_instances:
            return False
        
        instance = self.scenario_instances[instance_id]
        
        if instance.status != ScenarioStatus.READY:
            return False
        
        instance.status = ScenarioStatus.RUNNING
        instance.started_at = datetime.now()
        
        # 记录执行开始
        self._log_instance_event(instance_id, "execution_started", {
            "started_at": instance.started_at.isoformat()
        })
        
        logger.info(f"Started scenario execution: {instance_id}")
        return True
    
    def complete_scenario_execution(
        self, 
        instance_id: str, 
        results: Dict[str, Any],
        success: bool = True
    ) -> bool:
        """完成场景执行"""
        if instance_id not in self.scenario_instances:
            return False
        
        instance = self.scenario_instances[instance_id]
        
        if instance.status != ScenarioStatus.RUNNING:
            return False
        
        instance.status = ScenarioStatus.COMPLETED if success else ScenarioStatus.FAILED
        instance.completed_at = datetime.now()
        instance.results = results
        
        # 记录执行完成
        self._log_instance_event(instance_id, "execution_completed", {
            "completed_at": instance.completed_at.isoformat(),
            "success": success,
            "duration_ms": int((instance.completed_at - instance.started_at).total_seconds() * 1000) if instance.started_at else 0
        })
        
        logger.info(f"Completed scenario execution: {instance_id}, success: {success}")
        return True
    
    def get_scenario_instance(self, instance_id: str) -> Optional[ScenarioInstance]:
        """获取场景实例"""
        return self.scenario_instances.get(instance_id)
    
    def get_instance_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """获取实例状态"""
        instance = self.scenario_instances.get(instance_id)
        if not instance:
            return None
        
        return instance.to_dict()
    
    def list_scenario_instances(
        self, 
        scenario_id: Optional[str] = None,
        status: Optional[ScenarioStatus] = None
    ) -> List[Dict[str, Any]]:
        """列出场景实例"""
        instances = list(self.scenario_instances.values())
        
        # 过滤条件
        if scenario_id:
            instances = [inst for inst in instances if inst.scenario_id == scenario_id]
        
        if status:
            instances = [inst for inst in instances if inst.status == status]
        
        # 按创建时间排序
        instances.sort(key=lambda x: x.created_at, reverse=True)
        
        return [instance.to_dict() for instance in instances]
    
    def _log_instance_event(self, instance_id: str, event_type: str, data: Dict[str, Any]):
        """记录实例事件"""
        if instance_id in self.scenario_instances:
            instance = self.scenario_instances[instance_id]
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data
            }
            instance.execution_log.append(event)
    
    def get_scenario_statistics(self) -> Dict[str, Any]:
        """获取场景统计信息"""
        total_definitions = len(self.scenario_definitions)
        total_instances = len(self.scenario_instances)
        
        # 按类型统计场景定义
        type_distribution = {}
        for scenario in self.scenario_definitions.values():
            scenario_type = scenario.scenario_type.value
            type_distribution[scenario_type] = type_distribution.get(scenario_type, 0) + 1
        
        # 按状态统计实例
        status_distribution = {}
        for instance in self.scenario_instances.values():
            status = instance.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # 计算成功率
        completed_instances = status_distribution.get("completed", 0)
        failed_instances = status_distribution.get("failed", 0)
        total_finished = completed_instances + failed_instances
        success_rate = completed_instances / total_finished if total_finished > 0 else 0
        
        return {
            "scenario_definitions": {
                "total": total_definitions,
                "by_type": type_distribution
            },
            "scenario_instances": {
                "total": total_instances,
                "by_status": status_distribution,
                "success_rate": success_rate
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def export_scenario_catalog(self) -> Dict[str, Any]:
        """导出场景目录"""
        return {
            "export_timestamp": datetime.now().isoformat(),
            "scenario_definitions": [scenario.to_dict() for scenario in self.scenario_definitions.values()],
            "statistics": self.get_scenario_statistics()
        }