"""
增强权限服务

集成智能风险评估器和上下文感知权限控制的权限服务。
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.interfaces import (
    IPermissionService,
    PermissionRequest,
    PermissionDecision
)
from ..services.permission_service import RiskLevel
from .intelligent_risk_assessor import IntelligentRiskAssessor


logger = logging.getLogger(__name__)


class EnhancedPermissionService(IPermissionService):
    """增强权限服务"""

    def __init__(self):
        """初始化增强权限服务"""
        super().__init__()
        self.risk_assessor = IntelligentRiskAssessor()
        self._audit_log = []  # 审计日志
        self.service_name = "enhanced_permission_service"
        self._health_status = False

    async def start(self) -> None:
        """启动服务"""
        logger.info("Enhanced Permission Service starting...")
        self._health_status = True
        logger.info("Enhanced Permission Service started successfully")

    async def stop(self) -> None:
        """停止服务"""
        logger.info("Enhanced Permission Service stopping...")
        self._health_status = False
        logger.info("Enhanced Permission Service stopped")

    def is_healthy(self) -> bool:
        """检查服务健康状态"""
        return self._health_status

    async def check_permission(self, request: PermissionRequest) -> PermissionDecision:
        """
        检查权限 - 增强版本

        Args:
            request: 权限请求

        Returns:
            权限决策结果
        """
        start_time = datetime.now()

        try:
            # 1. 智能风险评估
            assessed_risk = self.risk_assessor.assess_risk(
                request.tool_name,
                request.tool_args,
                request.context
            )

            # 2. 权限决策
            granted = self._make_permission_decision(request, assessed_risk)

            # 3. 计算置信度
            confidence = self._calculate_confidence(request, assessed_risk, granted)

            # 4. 创建决策结果
            decision = PermissionDecision(
                granted=granted,
                reason=self._generate_reason(request, assessed_risk, granted),
                risk_level=assessed_risk.value if hasattr(assessed_risk, 'value') else str(assessed_risk),
                conditions=self._get_applied_rules(request, assessed_risk),
                expires_at=None
            )

            # 存储额外的增强信息
            decision.confidence = confidence
            decision.timestamp = start_time
            decision.request_id = request.context.get("request_id") if request.context else None

            # 5. 审计记录
            self._audit_permission_request(request, decision)

            logger.info(
                f"Permission decision: {request.tool_name} -> "
                f"{'ALLOWED' if granted else 'DENIED'} "
                f"(risk: {assessed_risk.value}, confidence: {confidence:.2f})"
            )

            return decision

        except Exception as e:
            logger.error(f"Error in permission check: {e}")
            # 出错时采取保守策略
            decision = PermissionDecision(
                granted=False,
                reason=f"Permission check failed: {str(e)}",
                risk_level=RiskLevel.CRITICAL.value,
                conditions=["error_handling"],
                expires_at=None
            )

            # 存储额外的增强信息
            decision.confidence = 1.0
            decision.timestamp = start_time
            decision.request_id = request.context.get("request_id") if request.context else None
            self._audit_permission_request(request, decision)
            return decision

    def _make_permission_decision(
        self,
        request: PermissionRequest,
        assessed_risk: RiskLevel
    ) -> bool:
        """
        做出权限决策

        Args:
            request: 权限请求
            assessed_risk: 评估的风险等级

        Returns:
            是否允许权限
        """
        # 获取用户角色
        user_role = request.context.get("user_role", "user") if request.context else "user"

        # 基于风险等级和用户角色的决策矩阵
        if user_role == "admin":
            # 管理员：允许所有操作（除了极端危险的操作）
            return assessed_risk != RiskLevel.CRITICAL or self._is_admin_critical_allowed(request)

        elif user_role == "developer":
            # 开发者：允许低到中等风险操作
            return assessed_risk in [RiskLevel.LOW, RiskLevel.MEDIUM]

        elif user_role == "user":
            # 普通用户：仅允许低风险操作
            return assessed_risk == RiskLevel.LOW

        else:  # guest or unknown
            # 访客：仅允许最低风险操作
            return assessed_risk == RiskLevel.LOW and self._is_safe_operation(request)

    def _is_admin_critical_allowed(self, request: PermissionRequest) -> bool:
        """判断管理员的关键操作是否被允许"""
        # 某些关键操作即使是管理员也需要特殊考虑
        dangerous_tools = ["system_shutdown", "database_drop", "security_bypass"]
        return request.tool_name not in dangerous_tools

    def _is_safe_operation(self, request: PermissionRequest) -> bool:
        """判断操作是否安全"""
        # 定义访客可以执行的安全操作
        safe_tools = ["file_read", "help", "status", "info"]
        safe_paths = ["/public", "/docs", "/help"]

        # 检查工具名称
        if request.tool_name not in safe_tools:
            return False

        # 检查文件路径
        if "file_path" in request.tool_args:
            file_path = request.tool_args["file_path"]
            if not any(path in file_path for path in safe_paths):
                return False

        return True

    def _calculate_confidence(
        self,
        request: PermissionRequest,
        risk_level: RiskLevel,
        granted: bool
    ) -> float:
        """
        计算决策置信度

        Args:
            request: 权限请求
            risk_level: 风险等级
            granted: 是否允许

        Returns:
            置信度 (0.0 - 1.0)
        """
        base_confidence = 0.8

        # 用户角色明确性
        user_role = request.context.get("user_role", "") if request.context else ""
        if user_role in ["admin", "developer", "user", "guest"]:
            base_confidence += 0.1

        # 上下文完整性
        if request.context and len(request.context) >= 3:
            base_confidence += 0.05

        # 风险等级明确性
        if risk_level != RiskLevel.MEDIUM:  # 非中等风险通常更明确
            base_confidence += 0.05

        # 决策一致性（高风险拒绝，低风险允许）
        if (risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] and not granted) or \
           (risk_level == RiskLevel.LOW and granted):
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    def _generate_reason(
        self,
        request: PermissionRequest,
        risk_level: RiskLevel,
        granted: bool
    ) -> str:
        """生成决策原因"""
        user_role = request.context.get("user_role", "unknown") if request.context else "unknown"

        if granted:
            return f"Permission granted for {user_role} to perform {risk_level.value} risk operation"
        else:
            if risk_level == RiskLevel.CRITICAL:
                return f"Permission denied: {risk_level.value} risk operation requires elevated privileges"
            elif user_role == "user":
                return f"Permission denied: {user_role} role not authorized for {risk_level.value} risk operations"
            elif user_role == "guest":
                return f"Permission denied: guest access limited to low risk operations"
            else:
                return f"Permission denied: insufficient privileges for {risk_level.value} risk operation"

    def _get_applied_rules(
        self,
        request: PermissionRequest,
        risk_level: RiskLevel
    ) -> list:
        """获取应用的规则列表"""
        rules = ["risk_based_assessment"]

        user_role = request.context.get("user_role", "") if request.context else ""
        if user_role:
            rules.append(f"role_based_{user_role}")

        if risk_level == RiskLevel.CRITICAL:
            rules.append("critical_operation_review")

        if request.context and request.context.get("environment") == "production":
            rules.append("production_environment_policy")

        return rules

    def _audit_permission_request(
        self,
        request: PermissionRequest,
        decision: PermissionDecision
    ) -> None:
        """审计权限请求"""
        audit_entry = {
            "timestamp": decision.timestamp,
            "request_id": decision.request_id,
            "tool_name": request.tool_name,
            "tool_args": request.tool_args,
            "user_context": request.context,
            "decision": "granted" if decision.granted else "denied",
            "risk_level": decision.risk_level.value if hasattr(decision.risk_level, 'value') else str(decision.risk_level),
            "confidence": decision.confidence,
            "reason": decision.reason
        }

        self._audit_log.append(audit_entry)

        # 保持审计日志大小
        if len(self._audit_log) > 10000:
            self._audit_log = self._audit_log[-5000:]

    def get_audit_log(self, limit: Optional[int] = None) -> list:
        """获取审计日志"""
        if limit:
            return self._audit_log[-limit:]
        return self._audit_log.copy()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.is_healthy() else "unhealthy",
            "service": self.service_name,
            "audit_log_size": len(self._audit_log),
            "risk_assessor": "operational"
        }

    # 实现抽象方法
    async def batch_check_permissions(self, requests: list) -> list:
        """批量权限检查"""
        results = []
        for request in requests:
            result = await self.check_permission(request)
            results.append(result)
        return results

    async def get_permission_policy(self, policy_id: str) -> Dict[str, Any]:
        """获取权限策略"""
        return {
            "policy_id": policy_id,
            "name": "Enhanced Risk-Based Policy",
            "description": "智能风险评估和角色权限控制策略",
            "risk_matrix": "operational",
            "role_mapping": "operational"
        }

    async def grant_permission(self, user_id: str, permission: str, context: Dict[str, Any]) -> bool:
        """授予权限"""
        # 记录权限授予
        audit_entry = {
            "timestamp": datetime.now(),
            "action": "grant_permission",
            "user_id": user_id,
            "permission": permission,
            "context": context,
            "granted_by": "enhanced_permission_service"
        }
        self._audit_log.append(audit_entry)
        return True

    async def revoke_permission(self, user_id: str, permission: str, context: Dict[str, Any]) -> bool:
        """撤销权限"""
        # 记录权限撤销
        audit_entry = {
            "timestamp": datetime.now(),
            "action": "revoke_permission",
            "user_id": user_id,
            "permission": permission,
            "context": context,
            "revoked_by": "enhanced_permission_service"
        }
        self._audit_log.append(audit_entry)
        return True

    async def set_permission_policy(self, policy_id: str, policy: Dict[str, Any]) -> bool:
        """设置权限策略"""
        audit_entry = {
            "timestamp": datetime.now(),
            "action": "set_permission_policy",
            "policy_id": policy_id,
            "policy": policy,
            "set_by": "enhanced_permission_service"
        }
        self._audit_log.append(audit_entry)
        return True