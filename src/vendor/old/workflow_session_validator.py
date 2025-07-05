import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WorkflowSessionValidator:
    """工作流会话验证器"""

    @staticmethod
    def validate_session_data(data: dict[str, Any]) -> bool:
        """验证会话数据结构"""
        required_fields = ["session_id", "workflow_type", "status", "created_at"]

        for field in required_fields:
            if field not in data:
                logger.error(f"缺少必需字段: {field}")
                return False

        # 验证状态值
        valid_statuses = ["created", "running", "completed", "failed", "paused"]
        if data.get("status") not in valid_statuses:
            logger.error(f"无效状态值: {data.get('status')}")
            return False

        return True

    @staticmethod
    def validate_workflow_steps(steps: list) -> bool:
        """验证工作流步骤"""
        if not isinstance(steps, list):
            logger.error("工作流步骤必须是列表")
            return False

        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                logger.error(f"步骤 {i} 必须是字典")
                return False

            if "step_id" not in step or "step_type" not in step:
                logger.error(f"步骤 {i} 缺少必需字段")
                return False

        return True


def safe_load_session(file_path: str) -> Optional[dict[str, Any]]:
    """安全加载会话文件"""
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        validator = WorkflowSessionValidator()
        if not validator.validate_session_data(data):
            return None

        if "steps" in data and not validator.validate_workflow_steps(data["steps"]):
            return None

        return data
    except Exception as e:
        logger.error(f"加载会话文件失败: {file_path} - {e}")
        return None
