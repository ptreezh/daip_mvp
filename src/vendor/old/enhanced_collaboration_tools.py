"""增强型协作系统工具定义
为虚拟角色提供文档自动生成、归档、溯源的工具接口
"""

from typing import Any

from src.enhanced_collaboration_system import enhanced_collaboration_system

# 工具定义列表（OpenAI Function Calling格式）
ENHANCED_COLLABORATION_TOOL_DEFINITIONS = [
    {
        "name": "create_workflow",
        "description": "创建虚拟团队协作工作流，包含角色分工、阶段定义、产出物清单等",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流唯一标识符"},
                "workflow_config": {
                    "type": "object",
                    "description": "工作流配置，包含名称、描述、阶段、角色、产出物等",
                },
            },
            "required": ["workflow_id", "workflow_config"],
        },
    },
    {
        "name": "create_deliverable",
        "description": "创建产出物文档，自动生成标准化文件名和元数据",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID"},
                "deliverable_data": {
                    "type": "object",
                    "description": "产出物数据，包含ID、名称、阶段、角色、输出类型等",
                },
                "content": {"type": "string", "description": "文档内容（Markdown格式）"},
            },
            "required": ["workflow_id", "deliverable_data", "content"],
        },
    },
    {
        "name": "generate_final_report",
        "description": "生成最终综合报告，整合所有产出物并生成项目总结",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID"},
                "model": {
                    "type": "string",
                    "description": "使用的模型名称",
                    "default": "gpt-4-32k",
                },
            },
            "required": ["workflow_id"],
        },
    },
    {
        "name": "search_documents",
        "description": "搜索工作流中的文档，支持关键词搜索和条件过滤",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID"},
                "query": {"type": "string", "description": "搜索查询关键词"},
                "filters": {"type": "object", "description": "过滤条件，如阶段、角色、输出类型等"},
            },
            "required": ["workflow_id"],
        },
    },
    {
        "name": "trace_document",
        "description": "追踪文档的完整溯源信息，包括创建历史、依赖关系等",
        "parameters": {
            "type": "object",
            "properties": {"document_id": {"type": "string", "description": "文档唯一标识符"}},
            "required": ["document_id"],
        },
    },
    {
        "name": "archive_workflow",
        "description": "归档工作流，将工作流及其所有产出物移动到归档目录",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID"},
                "archive_reason": {"type": "string", "description": "归档原因说明"},
            },
            "required": ["workflow_id"],
        },
    },
    {
        "name": "validate_workflow",
        "description": "验证工作流的完整性和规范性，检查配置、产出物、溯源记录等",
        "parameters": {
            "type": "object",
            "properties": {"workflow_id": {"type": "string", "description": "工作流ID"}},
            "required": ["workflow_id"],
        },
    },
    {
        "name": "get_workflow_summary",
        "description": "获取工作流摘要信息，包括基本信息和统计数字",
        "parameters": {
            "type": "object",
            "properties": {"workflow_id": {"type": "string", "description": "工作流ID"}},
            "required": ["workflow_id"],
        },
    },
]


# 工具函数映射
ENHANCED_COLLABORATION_TOOL_FUNCTIONS = {
    "create_workflow": enhanced_collaboration_system.create_workflow,
    "create_deliverable": enhanced_collaboration_system.create_deliverable,
    "generate_final_report": enhanced_collaboration_system.generate_final_report,
    "search_documents": enhanced_collaboration_system.search_documents,
    "trace_document": enhanced_collaboration_system.trace_document,
    "archive_workflow": enhanced_collaboration_system.archive_workflow,
    "validate_workflow": enhanced_collaboration_system.validate_workflow,
    "get_workflow_summary": enhanced_collaboration_system.get_workflow_summary,
}


def get_enhanced_collaboration_tool_definitions() -> list[dict[str, Any]]:
    """获取增强型协作系统工具定义"""
    return ENHANCED_COLLABORATION_TOOL_DEFINITIONS


def get_enhanced_collaboration_tool_functions() -> dict[str, Any]:
    """获取增强型协作系统工具函数映射"""
    return ENHANCED_COLLABORATION_TOOL_FUNCTIONS


def execute_enhanced_collaboration_tool(tool_name: str, **kwargs) -> dict[str, Any]:
    """执行增强型协作系统工具

    Args:
    ----
        tool_name: 工具名称
        **kwargs: 工具参数

    Returns:
    -------
        执行结果

    """
    if tool_name not in ENHANCED_COLLABORATION_TOOL_FUNCTIONS:
        return {"status": "error", "message": f"未知的工具: {tool_name}"}

    try:
        tool_function = ENHANCED_COLLABORATION_TOOL_FUNCTIONS[tool_name]
        result = tool_function(**kwargs)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"工具执行失败: {e!s}",
            "tool_name": tool_name,
        }


# 便捷函数
def create_workflow_with_deliverables(
    workflow_id: str,
    workflow_config: dict[str, Any],
    deliverables: list[dict[str, Any]],
) -> dict[str, Any]:
    """创建工作流并初始化产出物

    Args:
    ----
        workflow_id: 工作流ID
        workflow_config: 工作流配置
        deliverables: 产出物列表

    Returns:
    -------
        创建结果

    """
    try:
        # 创建工作流
        workflow_result = enhanced_collaboration_system.create_workflow(
            workflow_id,
            workflow_config,
        )
        if workflow_result["status"] != "success":
            return workflow_result

        # 创建产出物
        created_deliverables = []
        for deliverable in deliverables:
            deliverable_result = enhanced_collaboration_system.create_deliverable(
                workflow_id=workflow_id,
                deliverable_data=deliverable,
                content=deliverable.get("content", ""),
            )
            if deliverable_result["status"] == "success":
                created_deliverables.append(deliverable_result)

        return {
            "status": "success",
            "message": f"工作流 {workflow_id} 创建成功，包含 {len(created_deliverables)} 个产出物",
            "workflow_id": workflow_id,
            "created_deliverables": created_deliverables,
        }

    except Exception as e:
        return {"status": "error", "message": f"创建工作流和产出物失败: {e!s}"}


async def generate_complete_project_report(
    workflow_id: str,
    model: str = "gpt-4-32k",
) -> dict[str, Any]:
    """生成完整的项目报告，包括最终报告和归档

    Args:
    ----
        workflow_id: 工作流ID
        model: 使用的模型

    Returns:
    -------
        生成结果

    """
    try:
        # 生成最终报告
        report_result = await enhanced_collaboration_system.generate_final_report(
            workflow_id,
            model,
        )
        if report_result["status"] != "success":
            return report_result

        # 获取工作流摘要
        summary_result = enhanced_collaboration_system.get_workflow_summary(workflow_id)

        return {
            "status": "success",
            "message": f"项目 {workflow_id} 完整报告生成成功",
            "workflow_id": workflow_id,
            "final_report": report_result,
            "summary": summary_result.get("summary", {}),
        }

    except Exception as e:
        return {"status": "error", "message": f"生成完整项目报告失败: {e!s}"}


def search_and_trace_documents(
    workflow_id: str,
    query: str = "",
    filters: dict[str, Any] = {},
) -> dict[str, Any]:
    """搜索文档并获取溯源信息

    Args:
    ----
        workflow_id: 工作流ID
        query: 搜索查询
        filters: 过滤条件

    Returns:
    -------
        搜索结果和溯源信息

    """
    try:
        # 搜索文档
        search_result = enhanced_collaboration_system.search_documents(
            workflow_id,
            query,
            filters,
        )
        if search_result["status"] != "success":
            return search_result

        # 获取溯源信息
        traces = []
        for deliverable in search_result.get("deliverables", []):
            if "trace" in deliverable:
                traces.append(deliverable["trace"])

        return {
            "status": "success",
            "search_results": search_result,
            "traces": traces,
            "total_documents": len(search_result.get("deliverables", [])),
            "total_traces": len(traces),
        }

    except Exception as e:
        return {"status": "error", "message": f"搜索和溯源文档失败: {e!s}"}
