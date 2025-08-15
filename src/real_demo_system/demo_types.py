#!/usr/bin/env python3
"""演示系统类型定义
"""

from enum import Enum


class DemoScenarioType(Enum):
    """演示场景类型"""
    MULTI_ROLE_DEBATE = "multi_role_debate"
    ETHICAL_ANALYSIS = "ethical_analysis"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    DECISION_SUPPORT = "decision_support"
    CONFLICT_RESOLUTION = "conflict_resolution"
    CUSTOM = "custom"


class DemoStepStatus(Enum):
    """演示步骤状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DemoStatus(Enum):
    """演示状态"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"