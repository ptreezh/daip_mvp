"""工作流错误处理器
统一处理422等HTTP错误
"""

import logging

from fastapi import HTTPException, status
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class WorkflowErrorHandler:
    """工作流错误处理器"""

    @staticmethod
    def handle_validation_error(error: ValidationError) -> HTTPException:
        """处理参数验证错误"""
        error_details = []
        for err in error.errors():
            field = " -> ".join(str(loc) for loc in err["loc"])
            message = err["msg"]
            error_details.append(f"{field}: {message}")

        error_message = "; ".join(error_details)
        logger.warning(f"参数验证失败: {error_message}")

        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "参数验证失败",
                "details": error_details,
                "error_code": "VALIDATION_ERROR",
            },
        )

    @staticmethod
    def handle_workflow_error(
        error: Exception,
        error_code: str = "WORKFLOW_ERROR",
    ) -> HTTPException:
        """处理工作流执行错误"""
        logger.error(f"工作流执行错误: {error}")

        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "工作流执行失败",
                "message": str(error),
                "error_code": error_code,
            },
        )

    @staticmethod
    def handle_session_not_found(session_id: str) -> HTTPException:
        """处理会话不存在错误"""
        logger.warning(f"会话不存在: {session_id}")

        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "会话不存在",
                "session_id": session_id,
                "error_code": "SESSION_NOT_FOUND",
            },
        )

    @staticmethod
    def handle_invalid_state_transition(
        current_state: str,
        target_state: str,
    ) -> HTTPException:
        """处理无效状态转换错误"""
        logger.warning(f"无效状态转换: {current_state} -> {target_state}")

        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "无效的状态转换",
                "current_state": current_state,
                "target_state": target_state,
                "error_code": "INVALID_STATE_TRANSITION",
            },
        )


def safe_workflow_execution(func):
    """工作流执行安全装饰器"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            raise WorkflowErrorHandler.handle_validation_error(e)
        except Exception as e:
            raise WorkflowErrorHandler.handle_workflow_error(e)

    return wrapper
