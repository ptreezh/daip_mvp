"""
智能风险评估器

提供多维度的风险评估，考虑操作类型、用户角色、资源敏感度、时间环境等因素。
"""

from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, time as dt_time
import logging

from ..services.permission_service import RiskLevel


logger = logging.getLogger(__name__)


class OperationType(Enum):
    """操作类型枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    CONFIG = "config"


class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"


class ResourceSensitivity(Enum):
    """资源敏感度枚举"""
    PUBLIC = "public"
    PRIVATE = "private"
    SHARED = "shared"
    SYSTEM = "system"
    CRITICAL = "critical"


class IntelligentRiskAssessor:
    """智能风险评估器"""

    def __init__(self):
        """初始化智能风险评估器"""
        # 基础风险矩阵：操作类型 x 资源敏感度
        self.base_risk_matrix = {
            (OperationType.READ, ResourceSensitivity.PUBLIC): RiskLevel.LOW,
            (OperationType.READ, ResourceSensitivity.PRIVATE): RiskLevel.MEDIUM,
            (OperationType.READ, ResourceSensitivity.SHARED): RiskLevel.MEDIUM,
            (OperationType.READ, ResourceSensitivity.SYSTEM): RiskLevel.HIGH,
            (OperationType.READ, ResourceSensitivity.CRITICAL): RiskLevel.HIGH,

            (OperationType.WRITE, ResourceSensitivity.PUBLIC): RiskLevel.MEDIUM,
            (OperationType.WRITE, ResourceSensitivity.PRIVATE): RiskLevel.MEDIUM,
            (OperationType.WRITE, ResourceSensitivity.SHARED): RiskLevel.HIGH,
            (OperationType.WRITE, ResourceSensitivity.SYSTEM): RiskLevel.HIGH,
            (OperationType.WRITE, ResourceSensitivity.CRITICAL): RiskLevel.CRITICAL,

            (OperationType.DELETE, ResourceSensitivity.PUBLIC): RiskLevel.MEDIUM,
            (OperationType.DELETE, ResourceSensitivity.PRIVATE): RiskLevel.HIGH,
            (OperationType.DELETE, ResourceSensitivity.SHARED): RiskLevel.HIGH,
            (OperationType.DELETE, ResourceSensitivity.SYSTEM): RiskLevel.CRITICAL,
            (OperationType.DELETE, ResourceSensitivity.CRITICAL): RiskLevel.CRITICAL,

            (OperationType.EXECUTE, ResourceSensitivity.PUBLIC): RiskLevel.MEDIUM,
            (OperationType.EXECUTE, ResourceSensitivity.PRIVATE): RiskLevel.HIGH,
            (OperationType.EXECUTE, ResourceSensitivity.SHARED): RiskLevel.HIGH,
            (OperationType.EXECUTE, ResourceSensitivity.SYSTEM): RiskLevel.CRITICAL,
            (OperationType.EXECUTE, ResourceSensitivity.CRITICAL): RiskLevel.CRITICAL,

            (OperationType.CONFIG, ResourceSensitivity.PUBLIC): RiskLevel.MEDIUM,
            (OperationType.CONFIG, ResourceSensitivity.PRIVATE): RiskLevel.HIGH,
            (OperationType.CONFIG, ResourceSensitivity.SHARED): RiskLevel.HIGH,
            (OperationType.CONFIG, ResourceSensitivity.SYSTEM): RiskLevel.CRITICAL,
            (OperationType.CONFIG, ResourceSensitivity.CRITICAL): RiskLevel.CRITICAL,
        }

        # 用户角色风险调整因子
        self.role_risk_factors = {
            UserRole.ADMIN: 0.0,      # 管理员：不增加风险
            UserRole.DEVELOPER: 0.2,  # 开发者：轻微增加风险
            UserRole.USER: 0.5,       # 普通用户：中等增加风险
            UserRole.GUEST: 1.0,      # 访客：大幅增加风险
        }

        # 环境风险调整因子
        self.environment_risk_factors = {
            "development": 0.0,    # 开发环境：不增加风险
            "staging": 0.2,       # 测试环境：轻微增加风险
            "production": 0.5,    # 生产环境：大幅增加风险
        }

        # 时间风险调整因子
        self.time_risk_factor = 0.2  # 非工作时间增加的风险

    def assess_risk(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> RiskLevel:
        """
        智能风险评估

        Args:
            tool_name: 工具名称
            tool_args: 工具参数
            context: 上下文信息

        Returns:
            评估后的风险等级
        """
        if not context:
            context = {}

        # 1. 识别操作类型和资源敏感度
        operation_type = self._extract_operation_type(tool_name, tool_args, context)
        resource_sensitivity = self._extract_resource_sensitivity(tool_args, context)

        # 2. 获取基础风险等级
        base_risk = self._get_base_risk(operation_type, resource_sensitivity)

        # 3. 应用用户角色调整
        role_adjusted_risk = self._apply_role_adjustment(base_risk, context)

        # 4. 应用环境因素调整
        environment_adjusted_risk = self._apply_environment_adjustment(
            role_adjusted_risk, context
        )

        # 5. 应用时间因素调整
        final_risk = self._apply_time_adjustment(environment_adjusted_risk, context)

        logger.debug(
            f"Risk assessment: {tool_name} -> {operation_type.value} on "
            f"{resource_sensitivity.value} = {final_risk.value}"
        )

        return final_risk

    def _extract_operation_type(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        context: Dict[str, Any]
    ) -> OperationType:
        """从工具信息中提取操作类型"""
        # 首先从上下文中获取
        if "operation_type" in context:
            try:
                return OperationType(context["operation_type"])
            except ValueError:
                pass

        # 从工具参数中获取
        if "operation" in tool_args:
            try:
                return OperationType(tool_args["operation"])
            except ValueError:
                pass

        # 从工具名称推断
        tool_name_lower = tool_name.lower()
        if any(keyword in tool_name_lower for keyword in ["read", "view", "get", "list"]):
            return OperationType.READ
        elif any(keyword in tool_name_lower for keyword in ["write", "create", "add", "update"]):
            return OperationType.WRITE
        elif any(keyword in tool_name_lower for keyword in ["delete", "remove", "clean"]):
            return OperationType.DELETE
        elif any(keyword in tool_name_lower for keyword in ["config", "setting", "modify"]):
            return OperationType.CONFIG
        else:
            return OperationType.EXECUTE

    def _extract_resource_sensitivity(
        self,
        tool_args: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ResourceSensitivity:
        """从参数和上下文中提取资源敏感度"""
        # 从上下文中获取
        if "resource_sensitivity" in context:
            try:
                return ResourceSensitivity(context["resource_sensitivity"])
            except ValueError:
                pass

        # 从文件路径推断敏感度
        if "file_path" in tool_args:
            file_path = tool_args["file_path"].lower()
            if "/public/" in file_path or "/docs/" in file_path:
                return ResourceSensitivity.PUBLIC
            elif "/system/" in file_path or "/config/" in file_path:
                return ResourceSensitivity.SYSTEM
            elif "/security/" in file_path or "key" in file_path or "crypto" in file_path:
                return ResourceSensitivity.CRITICAL
            elif "/users/" in file_path or "/private/" in file_path:
                return ResourceSensitivity.PRIVATE
            elif "/shared/" in file_path or "/team/" in file_path:
                return ResourceSensitivity.SHARED

        # 从工具名称推断
        if "system" in tool_args.get("target", "").lower():
            return ResourceSensitivity.SYSTEM

        # 默认为中等敏感度
        return ResourceSensitivity.SHARED

    def _get_base_risk(
        self,
        operation_type: OperationType,
        resource_sensitivity: ResourceSensitivity
    ) -> RiskLevel:
        """获取基础风险等级"""
        return self.base_risk_matrix.get(
            (operation_type, resource_sensitivity),
            RiskLevel.MEDIUM  # 默认中等风险
        )

    def _apply_role_adjustment(
        self,
        base_risk: RiskLevel,
        context: Dict[str, Any]
    ) -> RiskLevel:
        """应用用户角色调整"""
        user_role_str = context.get("user_role", "user")
        try:
            user_role = UserRole(user_role_str)
        except ValueError:
            user_role = UserRole.USER

        risk_factor = self.role_risk_factors.get(user_role, 0.5)

        # 管理员不降低风险，但其他角色会增加风险
        if risk_factor == 0.0:
            return base_risk

        # 应用风险调整因子
        risk_level_value = self._risk_level_to_numeric(base_risk)
        adjusted_value = risk_level_value + risk_factor

        return self._numeric_to_risk_level(adjusted_value)

    def _apply_environment_adjustment(
        self,
        base_risk: RiskLevel,
        context: Dict[str, Any]
    ) -> RiskLevel:
        """应用环境因素调整"""
        environment = context.get("environment", "development")
        risk_factor = self.environment_risk_factors.get(environment, 0.0)

        if risk_factor == 0.0:
            return base_risk

        risk_level_value = self._risk_level_to_numeric(base_risk)
        adjusted_value = risk_level_value + risk_factor

        return self._numeric_to_risk_level(adjusted_value)

    def _apply_time_adjustment(
        self,
        base_risk: RiskLevel,
        context: Dict[str, Any]
    ) -> RiskLevel:
        """应用时间因素调整"""
        is_business_hours = context.get("is_business_hours", True)

        if is_business_hours:
            return base_risk

        # 非工作时间增加风险
        risk_level_value = self._risk_level_to_numeric(base_risk)
        adjusted_value = risk_level_value + self.time_risk_factor

        return self._numeric_to_risk_level(adjusted_value)

    def _risk_level_to_numeric(self, risk_level: RiskLevel) -> float:
        """将风险等级转换为数值"""
        mapping = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 2.0,
            RiskLevel.HIGH: 3.0,
            RiskLevel.CRITICAL: 4.0
        }
        return mapping.get(risk_level, 2.0)

    def _numeric_to_risk_level(self, value: float) -> RiskLevel:
        """将数值转换为风险等级"""
        if value <= 1.5:
            return RiskLevel.LOW
        elif value <= 2.5:
            return RiskLevel.MEDIUM
        elif value <= 3.5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL