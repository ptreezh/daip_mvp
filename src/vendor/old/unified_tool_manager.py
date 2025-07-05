"""统一的工具管理器
整合工具注册、执行、监控、优化等所有功能
"""

import json
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional

from src.config import TOOL_CALLING_CONFIG, get_tool_definitions_path
from src.constants import *
from src.enhanced_tool_retrieval import EnhancedToolRetrieval
from src.function_calling_model_manager import FunctionCallingModelManager
from src.mth import ModularToolHandlers
from src.tool_calling_optimizer import ToolCallingOptimizer
from src.tool_execution_monitor import ToolExecutionMonitor


@dataclass
class ToolDefinition:
    """统一的工具定义"""

    name: str
    description: str
    function: Callable
    parameters: dict[str, Any]
    category: str
    tags: list[str]


class UnifiedToolManager:
    """统一的工具管理器 - 唯一入口点

    功能：
    1. 工具注册和管理
    2. 智能工具调用决策
    3. 执行监控和错误处理
    4. 性能统计和优化
    5. 工具检索和推荐
    """

    def __init__(self, sskg_instance=None, config: Optional[dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.sskg_instance = sskg_instance
        self.config = config or TOOL_CALLING_CONFIG

        # 核心组件
        self.execution_monitor = ToolExecutionMonitor()
        self.tool_optimizer = ToolCallingOptimizer(self.config)
        self.model_manager = FunctionCallingModelManager()

        # 工具存储
        self.tools: dict[str, ToolDefinition] = {}
        self.tool_definitions: list[dict[str, Any]] = []

        # 初始化
        self._load_builtin_tools()
        self._load_tool_definitions()
        self._initialize_retrieval()

    def _load_builtin_tools(self):
        """加载内置工具"""
        # 基础工具
        basic_tools = {
            "create_task": {
                "description": "创建新任务",
                "category": "task_management",
                "tags": ["task", "create", "项目管理"],
            },
            "get_task_info": {
                "description": "获取任务信息",
                "category": "task_management",
                "tags": ["task", "query", "信息"],
            },
            "list_tasks": {
                "description": "列出所有任务",
                "category": "task_management",
                "tags": ["task", "list", "查看"],
            },
            "delete_task": {
                "description": "删除任务",
                "category": "task_management",
                "tags": ["task", "delete", "删除"],
            },
            "list_roles": {
                "description": "列出所有角色",
                "category": "collaboration",
                "tags": ["role", "list", "协作"],
            },
            "set_active_role": {
                "description": "设置活跃角色",
                "category": "collaboration",
                "tags": ["role", "set", "切换"],
            },
            "validate_protocol": {
                "description": "验证协议格式",
                "category": "validation",
                "tags": ["protocol", "validate", "验证"],
            },
        }

        # 注册基础工具
        if self.sskg_instance:
            mth = ModularToolHandlers(self.sskg_instance)
            for tool_name, tool_info in basic_tools.items():
                if hasattr(mth, tool_name):
                    self.register_tool(
                        name=tool_name,
                        description=tool_info["description"],
                        function=getattr(mth, tool_name),
                        parameters={},  # 从函数签名自动提取
                        category=tool_info["category"],
                        tags=tool_info["tags"],
                    )

    def _load_tool_definitions(self):
        """加载工具定义文件"""
        try:
            tool_path = get_tool_definitions_path()
            if os.path.exists(tool_path):
                with open(tool_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self.tool_definitions = data.get("tools", [])
                    self.logger.info(f"加载了 {len(self.tool_definitions)} 个工具定义")
        except Exception as e:
            self.logger.warning(f"加载工具定义失败: {e}")
            self.tool_definitions = []

    def _initialize_retrieval(self):
        """初始化工具检索系统"""
        if self.tool_definitions:
            self.tool_retrieval = EnhancedToolRetrieval(self.tool_definitions)
        else:
            self.tool_retrieval = None

    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: dict[str, Any],
        category: str,
        tags: list[str],
    ):
        """注册工具"""
        tool_def = ToolDefinition(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category,
            tags=tags,
        )
        self.tools[name] = tool_def
        self.logger.info(f"注册工具: {name}")

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """执行工具（统一接口）- 唯一执行入口

        所有工具执行都必须通过此接口，确保：
        1. 统一的监控和错误处理
        2. 完整的性能统计
        3. 一致的返回格式
        """
        if tool_name not in self.tools:
            return {"status": "error", "message": f"未知的工具: {tool_name}"}

        tool = self.tools[tool_name]

        # 使用监控器执行，确保一致性
        return self.execution_monitor.execute_tool_with_monitoring(
            tool_name=tool_name,
            tool_function=tool.function,
            arguments=arguments,
            context=context,
        )

    def should_use_tools(
        self,
        user_input: str,
        context: Optional[dict[str, Any]] = None,
    ):
        """判断是否应该使用工具"""
        return self.tool_optimizer.should_use_tools(user_input, context or {})

    def get_recommended_tools(
        self,
        user_input: str,
        context: Optional[dict[str, Any]] = None,
    ) -> list[str]:
        """获取推荐工具"""
        if self.tool_retrieval:
            matches = self.tool_retrieval.search_tools(
                user_input,
                k=5,
                context=context or {},
            )
            return [match.tool_name for match in matches]
        return []

    def get_tool_definitions(
        self,
        session_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """获取工具定义列表"""
        if session_id:
            # 加载会话特定的工具定义
            tool_path = get_tool_definitions_path(session_id)
            if os.path.exists(tool_path):
                try:
                    with open(tool_path, encoding="utf-8") as f:
                        data = json.load(f)
                        return data.get("tools", [])
                except Exception as e:
                    self.logger.warning(f"加载会话工具定义失败: {e}")

        return self.tool_definitions

    def get_performance_report(self) -> dict[str, Any]:
        """获取性能报告"""
        return {
            "tools_count": len(self.tools),
            "definitions_count": len(self.tool_definitions),
            "execution_stats": self.execution_monitor.get_performance_report(),
            "model_stats": self.model_manager.get_performance_report(),
        }

    def list_available_tools(self) -> list[dict[str, Any]]:
        """列出所有可用工具"""
        tools_info = []
        for name, tool in self.tools.items():
            tools_info.append(
                {
                    "name": name,
                    "description": tool.description,
                    "category": tool.category,
                    "tags": tool.tags,
                },
            )
        return tools_info


# 全局统一工具管理器实例
unified_tool_manager_instance = None


def get_unified_tool_manager(
    sskg_instance=None,
    config: Optional[dict[str, Any]] = None,
) -> UnifiedToolManager:
    """获取全局统一工具管理器实例"""
    global unified_tool_manager_instance
    if unified_tool_manager_instance is None:
        unified_tool_manager_instance = UnifiedToolManager(sskg_instance, config)
    return unified_tool_manager_instance
