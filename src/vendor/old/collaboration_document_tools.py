"""协作文档生成工具定义
为虚拟角色提供文档自动生成、归档、溯源的工具接口
"""

import json
from datetime import datetime
from typing import Any, Optional

from src.collaboration_document_generator import (
    collaboration_document_generator,
    create_deliverable_tool,
    create_project_structure_tool,
    generate_final_report_tool,
    get_deliverable_content_tool,
    list_projects_tool,
    search_deliverables_tool,
)

# 工具定义列表（OpenAI Function Calling格式）
COLLABORATION_DOCUMENT_TOOL_DEFINITIONS = [
    {
        "name": "create_project_structure",
        "description": "创建项目归档目录结构，按照标准格式组织项目文档",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "项目唯一标识符"},
                "project_name": {"type": "string", "description": "项目名称"},
            },
            "required": ["project_id", "project_name"],
        },
    },
    {
        "name": "create_deliverable",
        "description": "创建产出物文档，包含完整的元数据和溯源信息",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "项目ID"},
                "deliverable_data": {
                    "type": "object",
                    "description": "产出物定义数据",
                    "properties": {
                        "id": {"type": "string", "description": "产出物ID"},
                        "name": {"type": "string", "description": "产出物名称"},
                        "stage": {"type": "string", "description": "所属阶段"},
                        "role": {"type": "string", "description": "负责角色"},
                        "output_type": {"type": "string", "description": "产出物类型"},
                        "output_format": {"type": "string", "description": "输出格式"},
                        "output_filename": {"type": "string", "description": "输出文件名模板"},
                        "output_metadata": {
                            "type": "object",
                            "description": "产出物元数据",
                            "properties": {
                                "model": {"type": "string", "description": "使用的模型"},
                                "generated_at": {
                                    "type": "string",
                                    "description": "生成时间",
                                },
                                "role_id": {"type": "string", "description": "角色ID"},
                                "prompt": {"type": "string", "description": "生成prompt"},
                                "summary": {"type": "string", "description": "摘要"},
                                "conversation_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "user_requirements": {
                                    "type": "string",
                                    "description": "用户需求",
                                },
                                "parent_task_id": {
                                    "type": "string",
                                    "description": "父任务ID",
                                },
                                "output_format": {
                                    "type": "string",
                                    "description": "输出格式",
                                },
                            },
                            "required": ["model", "generated_at", "role_id", "prompt"],
                        },
                        "requirements": {
                            "type": "object",
                            "description": "产出物要求",
                            "properties": {
                                "min_words": {"type": "integer", "description": "最少字数"},
                                "structure": {"type": "string", "description": "文档结构"},
                                "must_include": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "format_requirements": {
                                    "type": "object",
                                    "description": "格式要求",
                                },
                            },
                        },
                    },
                    "required": [
                        "id",
                        "name",
                        "stage",
                        "role",
                        "output_type",
                        "output_filename",
                        "output_metadata",
                    ],
                },
                "content": {"type": "string", "description": "文档内容"},
            },
            "required": ["project_id", "deliverable_data", "content"],
        },
    },
    {
        "name": "generate_final_report",
        "description": "生成项目最终综合报告，整合所有阶段产出物",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "项目ID"},
                "model": {
                    "type": "string",
                    "description": "使用的模型",
                    "default": "gpt-4-32k",
                },
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "search_deliverables",
        "description": "搜索项目产出物，支持多种过滤条件",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "项目ID"},
                "query": {"type": "string", "description": "搜索查询关键词"},
                "stage": {"type": "string", "description": "阶段过滤"},
                "role": {"type": "string", "description": "角色过滤"},
                "output_type": {"type": "string", "description": "产出物类型过滤"},
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "get_deliverable_content",
        "description": "获取产出物文档内容",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "项目ID"},
                "filename": {"type": "string", "description": "文件名"},
            },
            "required": ["project_id", "filename"],
        },
    },
    {
        "name": "list_projects",
        "description": "列出所有项目",
        "parameters": {"type": "object", "properties": {}},
    },
]


# 工具函数映射
COLLABORATION_DOCUMENT_TOOL_FUNCTIONS = {
    "create_project_structure": create_project_structure_tool,
    "create_deliverable": create_deliverable_tool,
    "generate_final_report": generate_final_report_tool,
    "search_deliverables": search_deliverables_tool,
    "get_deliverable_content": get_deliverable_content_tool,
    "list_projects": list_projects_tool,
}


def get_collaboration_document_tool_definitions() -> list[dict[str, Any]]:
    """获取协作文档生成工具定义"""
    return COLLABORATION_DOCUMENT_TOOL_DEFINITIONS


def get_collaboration_document_tool_functions() -> dict[str, Any]:
    """获取协作文档生成工具函数映射"""
    return COLLABORATION_DOCUMENT_TOOL_FUNCTIONS


def execute_collaboration_document_tool(tool_name: str, **kwargs) -> dict[str, Any]:
    """执行协作文档生成工具

    Args:
    ----
        tool_name: 工具名称
        **kwargs: 工具参数

    Returns:
    -------
        执行结果

    """
    if tool_name not in COLLABORATION_DOCUMENT_TOOL_FUNCTIONS:
        return {"status": "error", "message": f"未知的工具: {tool_name}"}

    try:
        tool_function = COLLABORATION_DOCUMENT_TOOL_FUNCTIONS[tool_name]
        result = tool_function(**kwargs)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"工具执行失败: {e!s}",
            "tool_name": tool_name,
        }


# 便捷函数
def create_project_with_deliverables(
    project_id: str,
    project_name: str,
    deliverables: list[dict[str, Any]],
) -> dict[str, Any]:
    """创建项目并初始化产出物清单

    Args:
    ----
        project_id: 项目ID
        project_name: 项目名称
        deliverables: 产出物列表

    Returns:
    -------
        创建结果

    """
    # 创建项目结构
    result = create_project_structure_tool(project_id, project_name)

    if result["status"] != "success":
        return result

    # 初始化产出物清单
    try:
        project_path = collaboration_document_generator.projects_path / project_id
        config_path = project_path / "project_config.json"

        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["deliverables"] = deliverables
            config_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        return {
            "status": "success",
            "message": f"项目 {project_name} 创建成功，包含 {len(deliverables)} 个产出物",
            "project_id": project_id,
            "deliverables_count": len(deliverables),
        }

    except Exception as e:
        return {"status": "error", "message": f"初始化产出物清单失败: {e!s}"}


def generate_deliverable_with_requirements(
    project_id: str,
    task_id: str,
    name: str,
    stage: str,
    role: str,
    output_type: str,
    model: str,
    prompt: str,
    content: str,
    requirements: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """根据要求生成产出物

    Args:
    ----
        project_id: 项目ID
        task_id: 任务ID
        name: 产出物名称
        stage: 阶段
        role: 角色
        output_type: 产出物类型
        model: 模型
        prompt: 生成prompt
        content: 文档内容
        requirements: 产出物要求

    Returns:
    -------
        生成结果

    """
    from src.collaboration_document_generator import (
        Deliverable,
        DeliverableMetadata,
        DeliverableRequirement,
    )

    # 创建元数据
    metadata = DeliverableMetadata(
        model=model,
        generated_at=datetime.now().isoformat(),
        role_id=role,
        prompt=prompt,
    )

    # 创建要求
    req = DeliverableRequirement()
    if requirements:
        if "min_words" in requirements:
            req.min_words = requirements["min_words"]
        if "structure" in requirements:
            req.structure = requirements["structure"]
        if "must_include" in requirements:
            req.must_include = requirements["must_include"]
        if "format_requirements" in requirements:
            req.format_requirements = requirements["format_requirements"]

    # 创建产出物
    deliverable = Deliverable(
        id=task_id,
        name=name,
        stage=stage,
        role=role,
        output_type=output_type,
        output_format="markdown",
        output_filename=f"{task_id}_{output_type}_{role}_{model}_{{timestamp}}.md",
        output_metadata=metadata,
        requirements=req,
    )

    # 创建产出物文档
    return collaboration_document_generator.create_deliverable(
        project_id,
        deliverable,
        content,
    )


def get_project_summary(project_id: str) -> dict[str, Any]:
    """获取项目摘要信息

    Args:
    ----
        project_id: 项目ID

    Returns:
    -------
        项目摘要

    """
    try:
        # 获取项目配置
        project_path = collaboration_document_generator.projects_path / project_id
        config_path = project_path / "project_config.json"

        if not config_path.exists():
            return {"status": "error", "message": f"项目配置不存在: {project_id}"}

        config = json.loads(config_path.read_text(encoding="utf-8"))

        # 统计各阶段产出物
        stage_stats = {}
        for deliverable in config.get("deliverables", []):
            stage = deliverable.get("stage", "unknown")
            if stage not in stage_stats:
                stage_stats[stage] = 0
            stage_stats[stage] += 1

        return {
            "status": "success",
            "project_id": project_id,
            "project_name": config.get("project_name"),
            "total_deliverables": len(config.get("deliverables", [])),
            "stage_stats": stage_stats,
            "created_at": config.get("created_at"),
            "status": config.get("status"),
        }

    except Exception as e:
        return {"status": "error", "message": f"获取项目摘要失败: {e!s}"}
