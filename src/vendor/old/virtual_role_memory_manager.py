"""虚拟角色记忆银行管理器
集成到现有的工具调用系统中，为虚拟角色提供记忆银行操作能力
"""

import logging
from datetime import datetime
from typing import Any, Optional

from src.function_calling_model_manager import FunctionCallingModelManager
from src.memory_bank_tools import MemoryBankTools
from src.unified_tool_manager import UnifiedToolManager

logger = logging.getLogger(__name__)


class VirtualRoleMemoryManager:
    """虚拟角色记忆银行管理器

    功能：
    1. 管理虚拟角色的记忆银行操作
    2. 集成到现有的工具调用系统
    3. 提供CRCT（Chain of Recursive Thought）支持
    4. 确保记忆银行的一致性和完整性
    """

    def __init__(
        self,
        tool_manager: UnifiedToolManager,
        model_manager: FunctionCallingModelManager,
    ):
        self.tool_manager = tool_manager
        self.model_manager = model_manager
        self.memory_bank_tools = MemoryBankTools()

        # 注册记忆银行工具到统一工具管理器
        self._register_memory_bank_tools()

        # 初始化核心记忆银行文件
        self._initialize_core_memory_files()

        logger.info("虚拟角色记忆银行管理器初始化完成")

    def _register_memory_bank_tools(self):
        """注册记忆银行工具到统一工具管理器"""
        try:
            # 注册工具函数
            self.tool_manager.register_tool(
                name="get_shared_memory",
                description="获取共享记忆银行文件内容",
                function=self.memory_bank_tools.get_shared_memory,
                parameters={"filename": "string"},
                category="memory_bank",
                tags=["memory", "shared", "read"],
            )

            self.tool_manager.register_tool(
                name="set_shared_memory",
                description="设置共享记忆银行文件内容",
                function=self.memory_bank_tools.set_shared_memory,
                parameters={"filename": "string", "content": "string"},
                category="memory_bank",
                tags=["memory", "shared", "write"],
            )

            self.tool_manager.register_tool(
                name="get_private_memory",
                description="获取私有记忆银行文件内容",
                function=self.memory_bank_tools.get_private_memory,
                parameters={"role_id": "string", "filename": "string"},
                category="memory_bank",
                tags=["memory", "private", "read"],
            )

            self.tool_manager.register_tool(
                name="set_private_memory",
                description="设置私有记忆银行文件内容",
                function=self.memory_bank_tools.set_private_memory,
                parameters={
                    "role_id": "string",
                    "filename": "string",
                    "content": "string",
                },
                category="memory_bank",
                tags=["memory", "private", "write"],
            )

            self.tool_manager.register_tool(
                name="search_memory_bank",
                description="搜索记忆银行内容",
                function=self.memory_bank_tools.search_memory_bank,
                parameters={"query": "string", "role_id": "string"},
                category="memory_bank",
                tags=["memory", "search"],
            )

            self.tool_manager.register_tool(
                name="list_memory_files",
                description="列出记忆银行文件",
                function=self.memory_bank_tools.list_memory_files,
                parameters={"role_id": "string"},
                category="memory_bank",
                tags=["memory", "list"],
            )

            logger.info("记忆银行工具已注册到统一工具管理器")

        except Exception as e:
            logger.error(f"注册记忆银行工具失败: {e}")

    def _initialize_core_memory_files(self):
        """初始化核心记忆银行文件"""
        try:
            # 初始化项目简介文件
            project_brief_content = f"""# 项目简介

## 项目概述
这是一个基于DAIP-L.I.V.E.框架的虚拟AI角色协作系统。

## 核心目标
- 实现虚拟AI角色之间的智能协作
- 基于共享记忆银行进行项目协同
- 支持CRCT（Chain of Recursive Thought）推理
- 确保协作的可追溯性和一致性

## 系统架构
- 记忆银行：共享和私有记忆管理
- 工具调用：统一的工具调用接口
- 角色管理：虚拟角色定义和切换
- 协作协议：标准化的协作流程

## 当前状态
- 系统初始化完成
- 记忆银行工具已集成
- 虚拟角色协议已定义

---
*最后更新：{datetime.now().isoformat()}*
"""

            self.memory_bank_tools.set_shared_memory(
                "project_brief.md",
                project_brief_content,
            )

            # 初始化系统架构文件
            system_architecture_content = f"""# 系统架构

## 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   虚拟角色层     │    │   记忆银行层     │    │   工具调用层     │
│                 │    │                 │    │                 │
│ - 项目协调员     │◄──►│ - 共享记忆       │◄──►│ - 统一工具管理器 │
│ - 系统架构师     │    │ - 私有记忆       │    │ - 模型管理器     │
│ - 开发负责人     │    │ - 记忆搜索       │    │ - 执行监控       │
│ - 质量保证       │    │ - 记忆同步       │    │ - 错误处理       │
│ - 用户体验       │    │                 │    │                 │
│ - 文档专家       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 核心组件

### 1. 虚拟角色层
- **角色定义**：基于JSON的角色配置文件
- **角色切换**：动态角色激活和上下文切换
- **协作模式**：支持多种协作模式（辩论、头脑风暴、共识等）

### 2. 记忆银行层
- **共享记忆**：项目相关的共享信息
- **私有记忆**：角色专属的私有信息
- **记忆搜索**：基于关键词的记忆检索
- **记忆同步**：确保记忆的一致性

### 3. 工具调用层
- **统一接口**：所有工具调用通过统一管理器
- **模型支持**：支持Function Calling的专用模型
- **执行监控**：完整的工具执行监控和错误处理

## 数据流
1. 用户输入 → 角色识别 → 工具调用决策
2. 工具调用 → 记忆银行操作 → 结果返回
3. 结果处理 → 记忆更新 → 角色响应

---
*最后更新：{datetime.now().isoformat()}*
"""

            self.memory_bank_tools.set_shared_memory(
                "system_architecture.md",
                system_architecture_content,
            )

            # 初始化任务分配文件
            task_assignments_content = f"""# 任务分配

## 当前任务状态

### 待分配任务
- [ ] 系统初始化验证
- [ ] 角色功能测试
- [ ] 协作流程验证

### 进行中任务
- [x] 记忆银行工具集成
- [x] 虚拟角色协议定义
- [x] 系统架构设计

### 已完成任务
- [x] 项目初始化
- [x] 基础架构搭建

## 角色职责

### 项目协调员 (project_coordinator_001)
- 负责整体项目协调
- 管理任务分配和进度跟踪
- 维护共享记忆银行

### 系统架构师 (system_architect_001)
- 负责系统架构设计
- 技术决策和验证
- 维护架构文档

### 开发负责人 (development_lead_001)
- 负责代码实现
- 开发标准执行
- 技术债务管理

### 质量保证 (quality_assurance_001)
- 负责测试和验证
- 质量标准执行
- 问题跟踪和解决

### 用户体验 (user_experience_001)
- 负责用户体验设计
- 界面优化
- 用户反馈处理

### 文档专家 (documentation_specialist_001)
- 负责文档管理
- 知识库维护
- 用户指南编写

---
*最后更新：{datetime.now().isoformat()}*
"""

            self.memory_bank_tools.set_shared_memory(
                "task_assignments.md",
                task_assignments_content,
            )

            logger.info("核心记忆银行文件初始化完成")

        except Exception as e:
            logger.error(f"初始化核心记忆银行文件失败: {e}")

    def get_memory_bank_tool_definitions(self) -> list[dict[str, Any]]:
        """获取记忆银行工具定义（OpenAI Function Calling格式）"""
        return MEMORY_BANK_TOOL_DEFINITIONS

    def execute_memory_operation(self, operation: str, **kwargs) -> dict[str, Any]:
        """执行记忆银行操作

        Args:
        ----
            operation: 操作类型（get_shared_memory, set_shared_memory等）
            **kwargs: 操作参数

        Returns:
        -------
            操作结果

        """
        try:
            if operation == "get_shared_memory":
                return self.memory_bank_tools.get_shared_memory(kwargs["filename"])
            elif operation == "set_shared_memory":
                return self.memory_bank_tools.set_shared_memory(
                    kwargs["filename"],
                    kwargs["content"],
                )
            elif operation == "get_private_memory":
                return self.memory_bank_tools.get_private_memory(
                    kwargs["role_id"],
                    kwargs["filename"],
                )
            elif operation == "set_private_memory":
                return self.memory_bank_tools.set_private_memory(
                    kwargs["role_id"],
                    kwargs["filename"],
                    kwargs["content"],
                )
            elif operation == "search_memory_bank":
                return self.memory_bank_tools.search_memory_bank(
                    kwargs["query"],
                    kwargs.get("role_id"),
                )
            elif operation == "list_memory_files":
                return self.memory_bank_tools.list_memory_files(kwargs.get("role_id"))
            else:
                return {"status": "error", "message": f"未知的操作类型: {operation}"}
        except Exception as e:
            logger.error(f"执行记忆银行操作失败: {e}")
            return {"status": "error", "message": f"操作执行失败: {e!s}"}

    def get_role_context(self, role_id: str) -> dict[str, Any]:
        """获取角色上下文信息

        Args:
        ----
            role_id: 角色ID

        Returns:
        -------
            角色上下文信息

        """
        try:
            context = {
                "role_id": role_id,
                "shared_memory": {},
                "private_memory": {},
                "timestamp": datetime.now().isoformat(),
            }

            # 获取共享记忆
            shared_files = [
                "project_brief.md",
                "system_architecture.md",
                "task_assignments.md",
            ]
            for filename in shared_files:
                result = self.memory_bank_tools.get_shared_memory(filename)
                if result["status"] == "success":
                    context["shared_memory"][filename] = result["content"]

            # 获取私有记忆
            private_files = self.memory_bank_tools.list_memory_files(role_id)
            if private_files["status"] == "success":
                for file_info in private_files["files"]["private_memory"]:
                    filename = file_info["filename"]
                    result = self.memory_bank_tools.get_private_memory(
                        role_id,
                        filename,
                    )
                    if result["status"] == "success":
                        context["private_memory"][filename] = result["content"]

            return context

        except Exception as e:
            logger.error(f"获取角色上下文失败: {e}")
            return {
                "role_id": role_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def update_role_memory(
        self,
        role_id: str,
        filename: str,
        content: str,
        is_shared: bool = False,
    ) -> dict[str, Any]:
        """更新角色记忆

        Args:
        ----
            role_id: 角色ID
            filename: 文件名
            content: 内容
            is_shared: 是否为共享记忆

        Returns:
        -------
            更新结果

        """
        try:
            if is_shared:
                return self.memory_bank_tools.set_shared_memory(filename, content)
            else:
                return self.memory_bank_tools.set_private_memory(
                    role_id,
                    filename,
                    content,
                )
        except Exception as e:
            logger.error(f"更新角色记忆失败: {e}")
            return {"status": "error", "message": f"更新记忆失败: {e!s}"}

    def search_role_memory(
        self,
        query: str,
        role_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """搜索角色记忆

        Args:
        ----
            query: 搜索查询
            role_id: 可选的角色ID

        Returns:
        -------
            搜索结果

        """
        try:
            return self.memory_bank_tools.search_memory_bank(query, role_id)
        except Exception as e:
            logger.error(f"搜索角色记忆失败: {e}")
            return {"status": "error", "message": f"搜索记忆失败: {e!s}"}

    def validate_memory_integrity(self) -> dict[str, Any]:
        """验证记忆银行完整性

        Returns
        -------
            验证结果

        """
        try:
            validation_result = {
                "status": "success",
                "checks": [],
                "timestamp": datetime.now().isoformat(),
            }

            # 检查核心文件是否存在
            core_files = [
                "project_brief.md",
                "system_architecture.md",
                "task_assignments.md",
            ]
            for filename in core_files:
                result = self.memory_bank_tools.get_shared_memory(filename)
                check = {
                    "file": filename,
                    "exists": result["status"] == "success",
                    "error": result.get("message")
                    if result["status"] == "error"
                    else None,
                }
                validation_result["checks"].append(check)

            # 检查目录结构
            shared_path = self.memory_bank_tools.shared_path
            private_path = self.memory_bank_tools.private_path

            validation_result["checks"].append(
                {
                    "directory": "shared",
                    "exists": shared_path.exists(),
                    "writable": shared_path.exists() and shared_path.is_dir(),
                },
            )

            validation_result["checks"].append(
                {
                    "directory": "private",
                    "exists": private_path.exists(),
                    "writable": private_path.exists() and private_path.is_dir(),
                },
            )

            # 统计检查结果
            total_checks = len(validation_result["checks"])
            passed_checks = sum(
                1 for check in validation_result["checks"] if check.get("exists", False)
            )

            validation_result["summary"] = {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": total_checks - passed_checks,
                "integrity_score": passed_checks / total_checks
                if total_checks > 0
                else 0,
            }

            return validation_result

        except Exception as e:
            logger.error(f"验证记忆银行完整性失败: {e}")
            return {
                "status": "error",
                "message": f"验证失败: {e!s}",
                "timestamp": datetime.now().isoformat(),
            }


# 全局虚拟角色记忆银行管理器实例
virtual_role_memory_manager: Optional[VirtualRoleMemoryManager] = None


def initialize_virtual_role_memory_manager(
    tool_manager: UnifiedToolManager,
    model_manager: FunctionCallingModelManager,
) -> VirtualRoleMemoryManager:
    """初始化虚拟角色记忆银行管理器"""
    global virtual_role_memory_manager
    virtual_role_memory_manager = VirtualRoleMemoryManager(tool_manager, model_manager)
    return virtual_role_memory_manager


def get_virtual_role_memory_manager() -> Optional[VirtualRoleMemoryManager]:
    """获取虚拟角色记忆银行管理器实例"""
    return virtual_role_memory_manager
