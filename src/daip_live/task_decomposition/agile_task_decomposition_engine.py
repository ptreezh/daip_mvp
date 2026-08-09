"""
敏捷任务分解系统入口
"""

from collections.abc import AsyncGenerator


class AgileTaskDecompositionManager:
    """敏捷任务分解管理器 - 主要的系统入口"""

    def __init__(self, model_provider=None, skill_manager=None):
        from daip_live.task_decomposition.agile_task_system_core import (
            AgileTaskSystemCore,
        )

        self._core_system = AgileTaskSystemCore(model_provider, skill_manager)

    async def should_process_with_agile_decomposition(self, user_request: str) -> bool:
        """判断是否应该用敏捷分解处理"""
        return await self._core_system.should_decompose_request(user_request)

    async def process_complex_request(
        self, user_request: str
    ) -> AsyncGenerator[str, None]:
        """处理复杂请求（核心方法）"""
        async for event in self._core_system.process_request(user_request):
            yield event

    @property
    def project_memory(self):
        """访问项目记忆系统"""
        return self._core_system.project_memory


# 导入核心系统
from daip_live.task_decomposition.agile_task_system_core import (  # noqa: E402
    AgileTask,
    AgileTaskMemory,
    AgileTaskSystemCore,
    Sprint,
    TaskStatus,
)

# 确保模块结构正确
__all__ = [
    "AgileTaskDecompositionManager",
    "AgileTaskSystemCore",
    "AgileTask",
    "TaskStatus",
    "Sprint",
    "AgileTaskMemory",
]
