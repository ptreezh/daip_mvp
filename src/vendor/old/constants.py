"""DAIP Insight Engine - 统一常量定义模块

本模块集中定义全局业务常量，所有业务代码、测试代码、文档均应引用本文件中的常量，避免魔法字符串。
支持自动化API文档工具提取。
"""

from typing import Final

# 任务状态常量
TASK_STATUS_PENDING: Final[str] = "pending"
TASK_STATUS_IN_PROGRESS: Final[str] = "in_progress"
TASK_STATUS_WAITING_REVIEW: Final[str] = "waiting_review"
TASK_STATUS_COMPLETED: Final[str] = "completed"
TASK_STATUS_BLOCKED: Final[str] = "blocked"
TASK_STATUS_CANCELLED: Final[str] = "cancelled"

# 项目状态常量
PROJECT_STATUS_CREATED: Final[str] = "created"
PROJECT_STATUS_PLANNING: Final[str] = "planning"
PROJECT_STATUS_EXECUTING: Final[str] = "executing"
PROJECT_STATUS_REVIEWING: Final[str] = "reviewing"
PROJECT_STATUS_COMPLETED: Final[str] = "completed"
PROJECT_STATUS_PAUSED: Final[str] = "paused"
PROJECT_STATUS_CANCELLED: Final[str] = "cancelled"

# 任务执行结果状态
EXECUTION_STATUS_SUCCESS: Final[str] = "success"
EXECUTION_STATUS_COMPLETED: Final[str] = "completed"
EXECUTION_STATUS_FAILED: Final[str] = "failed"
EXECUTION_STATUS_PARTIAL: Final[str] = "partial_success"

# 记忆银行操作状态
MEMORY_STATUS_SUCCESS: Final[str] = "success"
MEMORY_STATUS_FAILED: Final[str] = "failed"

# 角色分配状态
ROLE_ASSIGNMENT_SUCCESS: Final[str] = "success"
ROLE_ASSIGNMENT_FAILED: Final[str] = "failed"

# 测试结果状态
TEST_STATUS_SUCCESS: Final[str] = "success"
TEST_STATUS_FAILED: Final[str] = "failed"
TEST_STATUS_WARNING: Final[str] = "warning"
TEST_STATUS_PARTIAL_SUCCESS: Final[str] = "partial_success"

# --- API文档片段 ---
# 本模块所有常量均已补充类型注解和用途说明，支持Sphinx/自动化API文档工具提取。
