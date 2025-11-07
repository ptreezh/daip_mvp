"""Permission Service implementation."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .interfaces import (
    IPermissionService,
    PermissionRequest,
    PermissionDecision,
    IDomainService
)

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionStatus(Enum):
    """Permission status enumeration."""
    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass
class PermissionPolicy:
    """Permission policy for a tool or action."""

    tool_name: str
    default_decision: bool
    risk_level: RiskLevel
    requires_user_approval: bool = False
    auto_approval_patterns: List[str] = field(default_factory=list)
    denied_patterns: List[str] = field(default_factory=list)
    time_limit_seconds: Optional[float] = None
    usage_limit: Optional[int] = None
    conditions: List[str] = field(default_factory=list)

    def should_auto_approve(self, request: PermissionRequest) -> bool:
        """Check if request should be auto-approved based on patterns."""
        if not self.default_decision:
            return False

        # Check denied patterns first
        for pattern in self.denied_patterns:
            if pattern.lower() in request.tool_name.lower():
                return False

        # Check approval patterns
        for pattern in self.auto_approval_patterns:
            if pattern.lower() in request.tool_name.lower():
                return True

        # Check if user approval is required
        if self.requires_user_approval:
            return False

        return self.default_decision


@dataclass
class PermissionAuditEntry:
    """Audit log entry for permission decisions."""

    timestamp: float
    request_id: str
    tool_name: str
    permission_type: str
    risk_level: str
    decision: str
    reason: Optional[str]
    user_id: Optional[str]
    session_id: Optional[str]
    granted_at: Optional[float]
    expires_at: Optional[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class PermissionRule(ABC):
    """Abstract base class for permission rules."""

    @abstractmethod
    async def evaluate(
        self,
        request: PermissionRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[PermissionDecision]:
        """
        Evaluate the permission request against this rule.

        Args:
            request: Permission request to evaluate
            context: Optional evaluation context

        Returns:
            Permission decision or None if rule doesn't apply
        """
        pass

    @abstractmethod
    def get_rule_name(self) -> str:
        """Get the name of this rule."""
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """Get rule priority (higher = more important)."""
        pass


class RiskBasedRule(PermissionRule):
    """Risk-based permission rule."""

    def __init__(self):
        """Initialize risk-based rule."""
        self.risk_thresholds = {
            RiskLevel.LOW: 1.0,      # Always allow
            RiskLevel.MEDIUM: 0.7,   # Allow with some conditions
            RiskLevel.HIGH: 0.3,     # Require user approval
            RiskLevel.CRITICAL: 0.0  # Never auto-approve
        }

    async def evaluate(
        self,
        request: PermissionRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[PermissionDecision]:
        """Evaluate based on risk level."""
        try:
            risk_level = RiskLevel(request.risk_level.lower())
            threshold = self.risk_thresholds.get(risk_level, 0.0)

            if threshold >= 1.0:
                return PermissionDecision(
                    granted=True,
                    reason=f"Low risk tool '{request.tool_name}' auto-approved",
                    risk_level=request.risk_level
                )
            elif threshold <= 0.0:
                return PermissionDecision(
                    granted=False,
                    reason=f"Critical risk tool '{request.tool_name}' requires explicit approval",
                    risk_level=request.risk_level
                )
            else:
                return PermissionDecision(
                    granted=True,
                    reason=f"Medium/High risk tool '{request.tool_name}' approved with caution",
                    conditions=[
                        "Monitor tool usage",
                        "Log execution details"
                    ],
                    risk_level=request.risk_level
                )
        except ValueError:
            # Unknown risk level, require approval
            return PermissionDecision(
                granted=False,
                reason=f"Unknown risk level '{request.risk_level}' for tool '{request.tool_name}'",
                risk_level=request.risk_level
            )

    def get_rule_name(self) -> str:
        return "risk_based"

    def get_priority(self) -> int:
        return 100


class TimeBasedRule(PermissionRule):
    """Time-based permission rule."""

    def __init__(self):
        """Initialize time-based rule."""
        self.business_hours_only = True  # Only allow during business hours
        self.business_hours_start = 9  # 9 AM
        self.business_hours_end = 17   # 5 PM
        self.allowed_days = {0, 1, 2, 3, 4}  # Monday to Friday (0=Monday)
        self.max_daily_executions = 10
        self.daily_usage: Dict[str, int] = {}

    async def evaluate(
        self,
        request: PermissionRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[PermissionDecision]:
        """Evaluate based on time constraints."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        current_hour = now.hour
        current_weekday = now.weekday()
        current_date = now.date().isoformat()

        # Check business hours
        if self.business_hours_only:
            if current_weekday not in self.allowed_days:
                return PermissionDecision(
                    granted=False,
                    reason="Tool access restricted to business days",
                    risk_level=request.risk_level
                )

            if not (self.business_hours_start <= current_hour < self.business_hours_end):
                return PermissionDecision(
                    granted=False,
                    reason="Tool access restricted to business hours",
                    risk_level=request.risk_level
                )

        # Check daily usage limit
        if request.tool_name not in self.daily_usage:
            self.daily_usage[request.tool_name] = 0

        if self.daily_usage[request.tool_name] >= self.max_daily_executions:
            return PermissionDecision(
                granted=False,
                reason=f"Daily usage limit ({self.max_daily_executions}) exceeded for tool '{request.tool_name}'",
                risk_level=request.risk_level
            )

        # Increment usage counter
        self.daily_usage[request.tool_name] += 1

        return PermissionDecision(
            granted=True,
            reason="Time-based constraints satisfied",
            expires_at=now.timestamp() + 3600,  # Expire after 1 hour
            risk_level=request.risk_level
        )

    def get_rule_name(self) -> str:
        return "time_based"

    def get_priority(self) -> int:
        return 80


class ContextBasedRule(PermissionRule):
    """Context-based permission rule."""

    def __init__(self):
        """Initialize context-based rule."""
        self.required_context_keys: Set[str] = set()
        self.blocked_context_patterns: List[str] = []

    async def evaluate(
        self,
        request: PermissionRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[PermissionDecision]:
        """Evaluate based on context information."""
        if not context:
            return PermissionDecision(
                granted=False,
                reason="No context information provided",
                risk_level=request.risk_level
            )

        # Check required context
        missing_keys = self.required_context_keys - set(context.keys())
        if missing_keys:
            return PermissionDecision(
                granted=False,
                reason=f"Missing required context: {', '.join(missing_keys)}",
                risk_level=request.risk_level
            )

        # Check blocked patterns
        for pattern in self.blocked_context_patterns:
            for key, value in context.items():
                if pattern.lower() in str(value).lower():
                    return PermissionDecision(
                        granted=False,
                        reason=f"Blocked context pattern found: {pattern}",
                        risk_level=request.risk_level
                    )

        return PermissionDecision(
            granted=True,
            reason="Context requirements satisfied",
            risk_level=request.risk_level
        )

    def get_rule_name(self) -> str:
        return "context_based"

    def get_priority(self) -> int:
        return 60


class PermissionCache:
    """Simple cache for permission decisions."""

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300.0):
        """
        Initialize permission cache.

        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time to live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[PermissionDecision, float]] = {}

    def get(self, key: str) -> Optional[PermissionDecision]:
        """Get cached decision."""
        if key in self._cache:
            decision, timestamp = self._cache[key]
            current_time = time.time()

            # Check if decision has expired
            if decision.expires_at and current_time > decision.expires_at:
                del self._cache[key]
                return None

            # Check if cache entry has expired
            if current_time - timestamp < self.ttl_seconds:
                return decision
            else:
                del self._cache[key]
        return None

    def put(self, key: str, decision: PermissionDecision) -> None:
        """Cache decision."""
        # Remove expired entries
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]

        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[key] = (decision, current_time)

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()


class PermissionService(IPermissionService):
    """
    Permission Service implementation.

    This service manages access control for tools and actions,
    with support for multiple evaluation strategies and comprehensive auditing.
    """

    def __init__(
        self,
        enable_caching: bool = True,
        cache_size: int = 1000,
        cache_ttl: float = 300.0,
        enable_audit_log: bool = True,
        audit_log_size: int = 10000
    ):
        """
        Initialize permission service.

        Args:
            enable_caching: Whether to enable decision caching
            cache_size: Maximum cache size
            cache_ttl: Cache TTL in seconds
            enable_audit_log: Whether to enable audit logging
            audit_log_size: Maximum audit log size
        """
        self.enable_caching = enable_caching
        self.enable_audit_log = enable_audit_log

        self._policies: Dict[str, PermissionPolicy] = {}
        self._rules: List[PermissionRule] = []
        self._granted_permissions: Dict[str, PermissionDecision] = {}
        self._cache = PermissionCache(cache_size, cache_ttl) if enable_caching else None
        self._audit_log: List[PermissionAuditEntry] = []
        self._audit_log_size = audit_log_size
        self._running = False

        self._metrics = {
            "requests_processed": 0,
            "permissions_granted": 0,
            "permissions_denied": 0,
            "cache_hits": 0,
            "rule_usage": {},
            "policy_usage": {},
            "avg_evaluation_time_ms": 0.0,
            "evaluation_time_total": 0.0
        }

        # Initialize default rules
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default permission rules."""
        self._rules = [
            RiskBasedRule(),
            TimeBasedRule(),
            ContextBasedRule()
        ]

        # Sort rules by priority (highest first)
        self._rules.sort(key=lambda rule: rule.get_priority(), reverse=True)

    async def start(self) -> None:
        """Start the permission service."""
        if self._running:
            return

        self._running = True
        logger.info("PermissionService started")

    async def stop(self) -> None:
        """Stop the permission service."""
        if not self._running:
            return

        self._running = False

        # Clear caches
        if self._cache:
            self._cache.clear()

        self._granted_permissions.clear()
        logger.info("PermissionService stopped")

    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return self._running

    async def check_permission(
        self,
        request: PermissionRequest
    ) -> PermissionDecision:
        """
        Check if a permission request should be granted.

        Args:
            request: Permission request to evaluate

        Returns:
            Permission decision
        """
        if not self._running:
            raise RuntimeError("PermissionService is not running")

        start_time = time.time()
        self._metrics["requests_processed"] += 1

        # Check cache first
        cache_key = f"{request.tool_name}:{hash(str(request.tool_args))}"
        if self._cache:
            cached_decision = self._cache.get(cache_key)
            if cached_decision:
                self._metrics["cache_hits"] += 1
                self._metrics["evaluation_time_total"] += time.time() - start_time
                return cached_decision

        # Evaluate rules
        decision = await self._evaluate_rules(request)

        # Apply policy if no rule matched
        if not decision:
            decision = await self._apply_policy(request)

        # Update granted permissions cache
        if decision.granted:
            self._granted_permissions[request.tool_name] = decision

        # Update metrics
        evaluation_time = (time.time() - start_time) * 1000
        self._metrics["evaluation_time_total"] += evaluation_time / 1000
        total_requests = self._metrics["requests_processed"]
        if total_requests > 0:
            self._metrics["avg_evaluation_time_ms"] = (
                self._metrics["evaluation_time_total"] * 1000 / total_requests
            )

        if decision.granted:
            self._metrics["permissions_granted"] += 1
        else:
            self._metrics["permissions_denied"] += 1

        # Cache decision
        if self._cache:
            self._cache.put(cache_key, decision)

        # Log audit entry
        if self.enable_audit_log:
            await self._log_audit_entry(request, decision)

        logger.debug(f"Permission decision for '{request.tool_name}': {'GRANTED' if decision.granted else 'DENIED'}")
        return decision

    async def _evaluate_rules(self, request: PermissionRequest) -> Optional[PermissionDecision]:
        """Evaluate permission request against all rules."""
        for rule in self._rules:
            try:
                decision = await rule.evaluate(request, request.context)
                if decision:
                    self._metrics["rule_usage"][rule.get_rule_name()] = (
                        self._metrics["rule_usage"].get(rule.get_rule_name(), 0) + 1
                    )
                    return decision
            except Exception as e:
                logger.error(f"Rule '{rule.get_rule_name()}' failed: {e}")

        return None

    async def _apply_policy(self, request: PermissionRequest) -> PermissionDecision:
        """Apply default policy if no rules matched."""
        policy = self._policies.get(request.tool_name)

        if not policy:
            # Default policy for unknown tools
            policy = PermissionPolicy(
                tool_name=request.tool_name,
                default_decision=False,
                risk_level=RiskLevel.MEDIUM,
                requires_user_approval=True
            )

        self._metrics["policy_usage"][policy.tool_name] = (
            self._metrics["policy_usage"].get(policy.tool_name, 0) + 1
        )

        granted = policy.should_auto_approve(request)

        return PermissionDecision(
            granted=granted,
            reason=f"Policy decision: {'auto-approved' if granted else 'manual approval required'}",
            conditions=policy.conditions if granted else [],
            expires_at=(
                time.time() + policy.time_limit_seconds
                if policy.time_limit_seconds else None
            ),
            risk_level=request.risk_level
        )

    async def batch_check_permissions(
        self,
        requests: List[PermissionRequest]
    ) -> List[PermissionDecision]:
        """
        Check multiple permission requests.

        Args:
            requests: List of permission requests

        Returns:
            List of permission decisions
        """
        if not self._running:
            raise RuntimeError("PermissionService is not running")

        # Process in parallel
        tasks = [
            self.check_permission(request)
            for request in requests
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing permission request {i}: {result}")
                processed_results.append(PermissionDecision(
                    granted=False,
                    reason=f"Processing error: {str(result)}",
                    risk_level="medium"
                ))
            else:
                processed_results.append(result)

        return processed_results

    async def grant_permission(
        self,
        tool_name: str,
        conditions: Optional[List[str]] = None,
        expires_at: Optional[float] = None
    ) -> None:
        """
        Grant permission for a tool.

        Args:
            tool_name: Tool name
            conditions: Any conditions
            expires_at: Expiration time
        """
        decision = PermissionDecision(
            granted=True,
            reason="Manually granted permission",
            conditions=conditions or [],
            expires_at=expires_at,
            risk_level="low"
        )

        self._granted_permissions[tool_name] = decision
        logger.info(f"Manually granted permission for tool '{tool_name}'")

    async def revoke_permission(
        self,
        tool_name: str,
        reason: Optional[str] = None
    ) -> None:
        """
        Revoke permission for a tool.

        Args:
            tool_name: Tool name
            reason: Reason for revocation
        """
        if tool_name in self._granted_permissions:
            del self._granted_permissions[tool_name]
            logger.info(f"Revoked permission for tool '{tool_name}': {reason or 'No reason provided'}")

    def get_permission_policy(
        self,
        tool_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get permission policy for a tool.

        Args:
            tool_name: Tool name

        Returns:
            Permission policy or None
        """
        policy = self._policies.get(tool_name)
        if not policy:
            return None

        return {
            "tool_name": policy.tool_name,
            "default_decision": policy.default_decision,
            "risk_level": policy.risk_level.value,
            "requires_user_approval": policy.requires_user_approval,
            "auto_approval_patterns": policy.auto_approval_patterns,
            "denied_patterns": policy.denied_patterns,
            "time_limit_seconds": policy.time_limit_seconds,
            "usage_limit": policy.usage_limit,
            "conditions": policy.conditions
        }

    def set_permission_policy(
        self,
        tool_name: str,
        policy: Dict[str, Any]
    ) -> None:
        """
        Set permission policy for a tool.

        Args:
            tool_name: Tool name
            policy: Permission policy
        """
        try:
            risk_level = RiskLevel(policy.get("risk_level", "medium"))
            permission_policy = PermissionPolicy(
                tool_name=tool_name,
                default_decision=policy.get("default_decision", False),
                risk_level=risk_level,
                requires_user_approval=policy.get("requires_user_approval", True),
                auto_approval_patterns=policy.get("auto_approval_patterns", []),
                denied_patterns=policy.get("denied_patterns", []),
                time_limit_seconds=policy.get("time_limit_seconds"),
                usage_limit=policy.get("usage_limit"),
                conditions=policy.get("conditions", [])
            )

            self._policies[tool_name] = permission_policy
            logger.info(f"Set permission policy for tool '{tool_name}'")
        except Exception as e:
            logger.error(f"Failed to set permission policy for '{tool_name}': {e}")
            raise

    def get_audit_log(
        self,
        limit: int = 100,
        tool_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get permission audit log.

        Args:
            limit: Maximum number of entries
            tool_name: Optional tool name filter

        Returns:
            List of audit log entries
        """
        entries = self._audit_log

        if tool_name:
            entries = [e for e in entries if e.tool_name == tool_name]

        # Return most recent entries
        recent_entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)[:limit]

        return [
            {
                "timestamp": entry.timestamp,
                "request_id": entry.request_id,
                "tool_name": entry.tool_name,
                "permission_type": entry.permission_type,
                "risk_level": entry.risk_level,
                "decision": entry.decision,
                "reason": entry.reason,
                "user_id": entry.user_id,
                "session_id": entry.session_id,
                "granted_at": entry.granted_at,
                "expires_at": entry.expires_at,
                "metadata": entry.metadata
            }
            for entry in recent_entries
        ]

    async def _log_audit_entry(
        self,
        request: PermissionRequest,
        decision: PermissionDecision
    ) -> None:
        """Log audit entry for permission decision."""
        entry = PermissionAuditEntry(
            timestamp=time.time(),
            request_id=request.request_id,
            tool_name=request.tool_name,
            permission_type=request.permission_type,
            risk_level=request.risk_level,
            decision="granted" if decision.granted else "denied",
            reason=decision.reason,
            user_id=request.context.get("user_id") if request.context else None,
            session_id=request.context.get("session_id") if request.context else None,
            granted_at=time.time() if decision.granted else None,
            expires_at=decision.expires_at,
            metadata={
                "tool_args": request.tool_args,
                "conditions": decision.conditions,
                "risk_assessment": request.risk_level
            }
        )

        self._audit_log.append(entry)

        # Maintain audit log size
        if len(self._audit_log) > self._audit_log_size:
            self._audit_log = self._audit_log[-self._audit_log_size:]

    def add_rule(self, rule: PermissionRule) -> None:
        """Add a custom permission rule."""
        self._rules.append(rule)
        # Sort by priority
        self._rules.sort(key=lambda r: r.get_priority(), reverse=True)
        logger.info(f"Added permission rule '{rule.get_rule_name()}'")

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a permission rule by name."""
        for i, rule in enumerate(self._rules):
            if rule.get_rule_name() == rule_name:
                self._rules.pop(i)
                logger.info(f"Removed permission rule '{rule_name}'")
                return True
        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        total_requests = self._metrics["requests_processed"]
        return {
            **self._metrics,
            "success_rate": (
                self._metrics["permissions_granted"] / total_requests
                if total_requests > 0 else 0.0
            ),
            "denial_rate": (
                self._metrics["permissions_denied"] / total_requests
                if total_requests > 0 else 0.0
            ),
            "cache_hit_rate": (
                self._metrics["cache_hits"] / total_requests
                if total_requests > 0 else 0.0
            ),
            "policies_configured": len(self._policies),
            "rules_configured": len(self._rules),
            "active_grants": len(self._granted_permissions),
            "audit_log_size": len(self._audit_log),
            "cache_enabled": self.enable_caching
        }