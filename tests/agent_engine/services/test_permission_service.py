"""Tests for PermissionService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import asyncio

from daip_live.agent_engine_v1.services.permission_service import (
    PermissionService,
    RiskLevel,
    PermissionPolicy,
    PermissionAuditEntry
)
from daip_live.agent_engine_v1.services.interfaces import PermissionDecision


class TestPermissionDecision:
    """Test PermissionDecision class."""

    def test_permission_decision_creation(self):
        """Test creating permission decision."""
        decision = PermissionDecision(
            allowed=True,
            confidence=0.85,
            reason="Safe operation",
            conditions={"user_role": "admin"},
            risk_level=RiskLevel.LOW,
            rules_applied=["rule_1"],
            evaluation_time_ms=50.0
        )

        assert decision.allowed is True
        assert decision.confidence == 0.85
        assert decision.reason == "Safe operation"
        assert decision.conditions["user_role"] == "admin"
        assert decision.risk_level == RiskLevel.LOW
        assert decision.rules_applied == ["rule_1"]
        assert decision.evaluation_time_ms == 50.0
        assert decision.timestamp > 0

    def test_permission_decision_with_risk_assessment(self):
        """Test permission decision with risk assessment."""
        decision = PermissionDecision(
            allowed=True,
            confidence=0.6,
            reason="Medium risk operation approved",
            risk_level=RiskLevel.MEDIUM,
            suggested_conditions={"timeout": 300}
        )

        assert decision.risk_level == RiskLevel.MEDIUM
        assert decision.suggested_conditions["timeout"] == 300


class TestRule:
    """Test Rule class."""

    def test_rule_creation(self):
        """Test creating a rule."""
        rule = Rule(
            id="test_rule",
            name="Test Rule",
            description="Test rule for unit testing",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={
                "user_role": {"equals": "admin"},
                "action_type": {"in": ["file_read", "file_write"]}
            },
            actions=["file_read", "file_write"],
            permission_level=PermissionLevel.ALLOW,
            risk_level=RiskLevel.LOW,
            enabled=True,
            metadata={"created_by": "test"}
        )

        assert rule.id == "test_rule"
        assert rule.name == "Test Rule"
        assert rule.rule_type == RuleType.ALLOW
        assert rule.priority == 100
        assert rule.conditions["user_role"]["equals"] == "admin"
        assert rule.actions == ["file_read", "file_write"]
        assert rule.permission_level == PermissionLevel.ALLOW
        assert rule.risk_level == RiskLevel.LOW
        assert rule.enabled is True
        assert rule.metadata["created_by"] == "test"

    def test_rule_validation(self):
        """Test rule validation."""
        # Valid rule should not raise exception
        valid_rule = Rule(
            id="valid_rule",
            name="Valid Rule",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={"user_role": "admin"},
            actions=["file_read"],
            permission_level=PermissionLevel.ALLOW
        )
        # Should not raise
        valid_rule.validate()

        # Invalid rule (negative priority) should raise exception
        with pytest.raises(ValueError, match="Priority must be non-negative"):
            invalid_rule = Rule(
                id="invalid_rule",
                name="Invalid Rule",
                rule_type=RuleType.ALLOW,
                priority=-1,
                conditions={"user_role": "admin"},
                actions=["file_read"],
                permission_level=PermissionLevel.ALLOW
            )
            invalid_rule.validate()

    def test_rule_to_dict(self):
        """Test rule serialization to dict."""
        rule = Rule(
            id="test_rule",
            name="Test Rule",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={"user_role": "admin"},
            actions=["file_read"],
            permission_level=PermissionLevel.ALLOW
        )

        rule_dict = rule.to_dict()
        assert rule_dict["id"] == "test_rule"
        assert rule_dict["name"] == "Test Rule"
        assert rule_dict["rule_type"] == RuleType.ALLOW
        assert rule_dict["priority"] == 100
        assert rule_dict["conditions"]["user_role"] == "admin"

    @classmethod
    def test_rule_from_dict(cls):
        """Test rule deserialization from dict."""
        rule_dict = {
            "id": "test_rule",
            "name": "Test Rule",
            "description": "Test rule",
            "rule_type": RuleType.ALLOW,
            "priority": 100,
            "conditions": {"user_role": "admin"},
            "actions": ["file_read"],
            "permission_level": PermissionLevel.ALLOW,
            "risk_level": RiskLevel.LOW,
            "enabled": True,
            "metadata": {}
        }

        rule = Rule.from_dict(rule_dict)
        assert rule.id == "test_rule"
        assert rule.name == "Test Rule"
        assert rule.rule_type == RuleType.ALLOW


class TestInMemoryRuleRepository:
    """Test InMemoryRuleRepository."""

    @pytest.fixture
    def repository(self):
        """Create a repository instance for testing."""
        return InMemoryRuleRepository()

    @pytest.fixture
    def sample_rule(self):
        """Create a sample rule for testing."""
        return Rule(
            id="test_rule",
            name="Test Rule",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={"user_role": "admin"},
            actions=["file_read"],
            permission_level=PermissionLevel.ALLOW
        )

    @pytest.mark.asyncio
    async def test_save_and_get_rule(self, repository, sample_rule):
        """Test saving and retrieving a rule."""
        await repository.save_rule(sample_rule)
        retrieved_rule = await repository.get_rule(sample_rule.id)

        assert retrieved_rule is not None
        assert retrieved_rule.id == sample_rule.id
        assert retrieved_rule.name == sample_rule.name

    @pytest.mark.asyncio
    async def test_get_nonexistent_rule(self, repository):
        """Test retrieving a non-existent rule."""
        rule = await repository.get_rule("nonexistent")
        assert rule is None

    @pytest.mark.asyncio
    async def test_list_all_rules(self, repository, sample_rule):
        """Test listing all rules."""
        await repository.save_rule(sample_rule)

        rules = await repository.list_all_rules()
        assert len(rules) == 1
        assert rules[0].id == sample_rule.id

    @pytest.mark.asyncio
    async def test_find_rules_by_action(self, repository, sample_rule):
        """Test finding rules by action."""
        await repository.save_rule(sample_rule)

        rules = await repository.find_rules_by_action("file_read")
        assert len(rules) == 1
        assert rules[0].id == sample_rule.id

        # Test non-matching action
        rules = await repository.find_rules_by_action("file_delete")
        assert len(rules) == 0

    @pytest.mark.asyncio
    async def test_find_rules_by_priority_range(self, repository, sample_rule):
        """Test finding rules by priority range."""
        await repository.save_rule(sample_rule)

        rules = await repository.find_rules_by_priority_range(50, 150)
        assert len(rules) == 1
        assert rules[0].id == sample_rule.id

        # Test non-matching range
        rules = await repository.find_rules_by_priority_range(200, 300)
        assert len(rules) == 0

    @pytest.mark.asyncio
    async def test_delete_rule(self, repository, sample_rule):
        """Test deleting a rule."""
        await repository.save_rule(sample_rule)

        # Verify rule exists
        rule = await repository.get_rule(sample_rule.id)
        assert rule is not None

        # Delete rule
        deleted = await repository.delete_rule(sample_rule.id)
        assert deleted is True

        # Verify rule is gone
        rule = await repository.get_rule(sample_rule.id)
        assert rule is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_rule(self, repository):
        """Test deleting a non-existent rule."""
        deleted = await repository.delete_rule("nonexistent")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_clear(self, repository, sample_rule):
        """Test clearing all rules."""
        await repository.save_rule(sample_rule)
        assert len(await repository.list_all_rules()) == 1

        await repository.clear()
        assert len(await repository.list_all_rules()) == 0


class TestFileRuleRepository:
    """Test FileRuleRepository."""

    @pytest.fixture
    def temp_file(self, tmp_path):
        """Create a temporary file for testing."""
        return tmp_path / "test_rules.json"

    @pytest.fixture
    def repository(self, temp_file):
        """Create a repository instance for testing."""
        return FileRuleRepository(str(temp_file))

    @pytest.fixture
    def sample_rule(self):
        """Create a sample rule for testing."""
        return Rule(
            id="test_rule",
            name="Test Rule",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={"user_role": "admin"},
            actions=["file_read"],
            permission_level=PermissionLevel.ALLOW
        )

    @pytest.mark.asyncio
    async def test_persistence(self, repository, sample_rule, temp_file):
        """Test that rules persist across repository instances."""
        # Save rule in first instance
        await repository.save_rule(sample_rule)

        # Create new instance with same file
        new_repository = FileRuleRepository(str(temp_file))
        retrieved_rule = await new_repository.get_rule(sample_rule.id)

        assert retrieved_rule is not None
        assert retrieved_rule.id == sample_rule.id


class TestLoggingAuditStore:
    """Test LoggingAuditStore."""

    @pytest.fixture
    def audit_store(self):
        """Create an audit store instance for testing."""
        return LoggingAuditStore()

    @pytest.mark.asyncio
    async def test_log_permission_decision(self, audit_store):
        """Test logging permission decision."""
        decision = PermissionDecision(
            allowed=True,
            confidence=0.8,
            reason="Test decision",
            risk_level=RiskLevel.LOW,
            rules_applied=["rule_1"]
        )

        # Should not raise exception
        await audit_store.log_permission_decision(
            context={"user": "test_user"},
            action="file_read",
            decision=decision
        )

    @pytest.mark.asyncio
    async def test_log_rule_execution(self, audit_store):
        """Test logging rule execution."""
        await audit_store.log_rule_execution(
            rule_id="test_rule",
            context={"user": "test_user"},
            action="file_read",
            result=True,
            execution_time_ms=10.0
        )

    @pytest.mark.asyncio
    async def test_log_security_event(self, audit_store):
        """Test logging security event."""
        await audit_store.log_security_event(
            event_type="UNAUTHORIZED_ACCESS_ATTEMPT",
            context={"user": "test_user", "action": "file_delete"},
            severity="high"
        )


class TestPermissionService:
    """Test PermissionService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return PermissionService()

    @pytest.fixture
    def sample_rule(self):
        """Create a sample rule for testing."""
        return Rule(
            id="test_rule",
            name="Test Rule",
            description="Test rule for unit testing",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={
                "user_role": {"equals": "admin"}
            },
            actions=["file_read"],
            permission_level=PermissionLevel.ALLOW,
            risk_level=RiskLevel.LOW,
            enabled=True
        )

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, service):
        """Test service start/stop lifecycle."""
        assert not service.is_healthy()

        await service.start()
        assert service.is_healthy()

        await service.stop()
        assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_add_rule(self, service, sample_rule):
        """Test adding a rule."""
        await service.start()

        rule_id = await service.add_rule(sample_rule)
        assert rule_id == sample_rule.id

        # Verify rule was added
        rule = await service.get_rule(sample_rule.id)
        assert rule is not None
        assert rule.id == sample_rule.id

        await service.stop()

    @pytest.mark.asyncio
    async def test_remove_rule(self, service, sample_rule):
        """Test removing a rule."""
        await service.start()

        # Add rule first
        rule_id = await service.add_rule(sample_rule)
        assert rule_id == sample_rule.id

        # Remove rule
        removed = await service.remove_rule(sample_rule.id)
        assert removed is True

        # Verify rule is gone
        rule = await service.get_rule(sample_rule.id)
        assert rule is None

        await service.stop()

    @pytest.mark.asyncio
    async def test_check_permission_allowed(self, service, sample_rule):
        """Test permission check that should be allowed."""
        await service.start()

        # Add rule
        await service.add_rule(sample_rule)

        # Check permission
        decision = await service.check_permission(
            action="file_read",
            context={"user_role": "admin"}
        )

        assert decision.allowed is True
        assert decision.confidence > 0.0
        assert decision.risk_level == RiskLevel.LOW
        assert sample_rule.id in decision.rules_applied

        await service.stop()

    @pytest.mark.asyncio
    async def test_check_permission_denied(self, service):
        """Test permission check that should be denied."""
        await service.start()

        # Check permission without any matching rules
        decision = await service.check_permission(
            action="file_delete",
            context={"user_role": "user"}
        )

        assert decision.allowed is False
        assert decision.confidence > 0.0
        assert "Default deny" in decision.reason

        await service.stop()

    @pytest.mark.asyncio
    async def test_check_permission_with_disabled_rule(self, service, sample_rule):
        """Test permission check with disabled rule."""
        # Disable the rule
        sample_rule.enabled = False

        await service.start()
        await service.add_rule(sample_rule)

        # Check permission (should be denied since rule is disabled)
        decision = await service.check_permission(
            action="file_read",
            context={"user_role": "admin"}
        )

        assert decision.allowed is False

        await service.stop()

    @pytest.mark.asyncio
    async def test_check_permission_with_conditions(self, service):
        """Test permission check with complex conditions."""
        rule = Rule(
            id="complex_rule",
            name="Complex Rule",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={
                "user_role": {"equals": "admin"},
                "time_of_day": {"between": [9, 17]},  # Business hours
                "risk_score": {"lte": 50}
            },
            actions=["file_write"],
            permission_level=PermissionLevel.ALLOW,
            risk_level=RiskLevel.MEDIUM
        )

        await service.start()
        await service.add_rule(rule)

        # Test with matching conditions
        decision = await service.check_permission(
            action="file_write",
            context={
                "user_role": "admin",
                "time_of_day": 14,
                "risk_score": 30
            }
        )
        assert decision.allowed is True

        # Test with non-matching conditions
        decision = await service.check_permission(
            action="file_write",
            context={
                "user_role": "user",  # Wrong role
                "time_of_day": 14,
                "risk_score": 30
            }
        )
        assert decision.allowed is False

        await service.stop()

    @pytest.mark.asyncio
    async def test_batch_check_permission(self, service, sample_rule):
        """Test batch permission checking."""
        await service.start()
        await service.add_rule(sample_rule)

        requests = [
            {
                "action": "file_read",
                "context": {"user_role": "admin"}
            },
            {
                "action": "file_read",
                "context": {"user_role": "user"}
            },
            {
                "action": "file_write",
                "context": {"user_role": "admin"}
            }
        ]

        decisions = await service.batch_check_permission(requests)

        assert len(decisions) == 3
        assert decisions[0].allowed is True  # admin, file_read
        assert decisions[1].allowed is False  # user, file_read
        assert decisions[2].allowed is False  # admin, file_write (not in rule actions)

        await service.stop()

    @pytest.mark.asyncio
    async def test_assess_risk(self, service):
        """Test risk assessment."""
        await service.start()

        # Low risk action
        risk = await service.assess_risk(
            action="file_read",
            context={"user_role": "admin", "target_file": "/tmp/harmless.txt"}
        )
        assert risk == RiskLevel.LOW

        # High risk action
        risk = await service.assess_risk(
            action="system_delete",
            context={"user_role": "user", "target": "/system"}
        )
        assert risk == RiskLevel.HIGH

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_rules(self, service, sample_rule):
        """Test getting rules."""
        await service.start()
        await service.add_rule(sample_rule)

        # Get all rules
        rules = await service.get_rules()
        assert len(rules) == 1
        assert rules[0].id == sample_rule.id

        # Get rules by action
        rules = await service.get_rules(action="file_read")
        assert len(rules) == 1
        assert rules[0].id == sample_rule.id

        # Get rules by non-matching action
        rules = await service.get_rules(action="file_write")
        assert len(rules) == 0

        await service.stop()

    @pytest.mark.asyncio
    async def test_service_metrics(self, service, sample_rule):
        """Test service metrics collection."""
        await service.start()
        await service.add_rule(sample_rule)

        # Perform some operations
        await service.check_permission("file_read", {"user_role": "admin"})
        await service.check_permission("file_write", {"user_role": "user"})
        await service.batch_check_permission([
            {"action": "file_read", "context": {"user_role": "admin"}},
            {"action": "file_delete", "context": {"user_role": "user"}}
        ])

        # Get metrics
        metrics = service.get_metrics()
        assert metrics["rules_count"] == 1
        assert metrics["checks_performed"] == 4  # 2 individual + 2 batch
        assert metrics["cache_enabled"] is True
        assert metrics["evaluation_time_avg_ms"] >= 0.0

        await service.stop()

    @pytest.mark.asyncio
    async def test_caching_behavior(self, service, sample_rule):
        """Test that caching improves performance."""
        await service.start()
        await service.add_rule(sample_rule)

        # First check (should populate cache)
        decision1 = await service.check_permission(
            "file_read",
            {"user_role": "admin"}
        )

        # Second check (should use cache)
        decision2 = await service.check_permission(
            "file_read",
            {"user_role": "admin"}
        )

        # Decisions should be identical
        assert decision1.allowed == decision2.allowed
        assert decision1.confidence == decision2.confidence

        # Check cache metrics
        metrics = service.get_metrics()
        assert metrics["cache_hit_rate"] > 0

        await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self, service):
        """Test error handling when service is not running."""
        # Should raise error when not running
        with pytest.raises(RuntimeError, match="not running"):
            await service.check_permission("file_read", {"user_role": "admin"})

        with pytest.raises(RuntimeError, match="not running"):
            await service.batch_check_permission([{"action": "file_read", "context": {}}])

        with pytest.raises(RuntimeError, match="not running"):
            await service.add_rule(sample_rule)

    @pytest.mark.asyncio
    async def test_rule_priority_ordering(self, service):
        """Test that rules are evaluated in priority order."""
        # Create rules with different priorities
        low_priority_rule = Rule(
            id="low_priority",
            name="Low Priority Rule",
            rule_type=RuleType.DENY,
            priority=100,  # Lower priority number = higher priority
            conditions={"user_role": "admin"},
            actions=["file_read"],
            permission_level=PermissionLevel.DENY
        )

        high_priority_rule = Rule(
            id="high_priority",
            name="High Priority Rule",
            rule_type=RuleType.ALLOW,
            priority=10,  # Higher priority
            conditions={"user_role": "admin"},
            actions=["file_read"],
            permission_level=PermissionLevel.ALLOW
        )

        await service.start()

        # Add rules in reverse priority order
        await service.add_rule(low_priority_rule)
        await service.add_rule(high_priority_rule)

        # Check permission (high priority allow should win)
        decision = await service.check_permission(
            "file_read",
            {"user_role": "admin"}
        )

        assert decision.allowed is True
        assert high_priority_rule.id in decision.rules_applied

        await service.stop()

    @pytest.mark.asyncio
    async def test_time_based_rules(self, service):
        """Test time-based rule conditions."""
        rule = Rule(
            id="time_based_rule",
            name="Time Based Rule",
            rule_type=RuleType.ALLOW,
            priority=100,
            conditions={
                "current_time": {
                    "between": ["09:00", "17:00"]  # Business hours
                }
            },
            actions=["file_read"],
            permission_level=PermissionLevel.ALLOW
        )

        await service.start()
        await service.add_rule(rule)

        # Mock current time to be within business hours
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.strptime("10:30", "%H:%M")

            decision = await service.check_permission(
                "file_read",
                {"user_role": "admin"}
            )
            assert decision.allowed is True

        await service.stop()