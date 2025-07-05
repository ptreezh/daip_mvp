"""协作协议Schema扩展
包含deliverables清单和产出物元数据定义
"""

import re
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class DeliverableMetadataModel(BaseModel):
    """产出物元数据模型"""

    model: str = Field(..., description="调用的大模型名称/版本")
    generated_at: str = Field(..., description="生成时间戳")
    role_id: str = Field(..., description="产出角色ID")
    prompt: str = Field(..., description="生成时的主prompt内容")
    summary: Optional[str] = Field(None, description="本次产出的摘要")
    conversation_ids: Optional[list[str]] = Field(None, description="相关对话历史ID或片段")
    user_requirements: Optional[str] = Field(None, description="用户原始需求")
    parent_task_id: Optional[str] = Field(None, description="上级任务ID")
    output_format: str = Field(default="markdown", description="输出格式")


class DeliverableRequirementModel(BaseModel):
    """产出物要求模型"""

    min_words: Optional[int] = Field(None, description="最少字数要求")
    structure: Optional[str] = Field(None, description="文档结构要求")
    must_include: Optional[list[str]] = Field(None, description="必须包含的内容")
    format_requirements: Optional[dict[str, Any]] = Field(None, description="格式要求")


class DeliverableModel(BaseModel):
    """产出物定义模型"""

    id: str = Field(..., description="产出物唯一标识")
    name: str = Field(..., description="产出物名称")
    stage: str = Field(..., description="所属阶段")
    role: str = Field(..., description="负责角色")
    output_type: str = Field(..., description="产出物类型")
    output_format: str = Field(default="markdown", description="输出格式")
    output_filename: str = Field(..., description="输出文件名模板")
    output_metadata: DeliverableMetadataModel = Field(..., description="产出物元数据")
    requirements: DeliverableRequirementModel = Field(..., description="产出物要求")

    @validator("id")
    def validate_deliverable_id(cls, v):
        """验证产出物ID格式"""
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError("deliverable_id must be in snake_case format")
        return v

    @validator("output_filename")
    def validate_output_filename(cls, v):
        """验证输出文件名模板格式"""
        required_placeholders = ["{model}", "{timestamp}"]
        for placeholder in required_placeholders:
            if placeholder not in v:
                raise ValueError(f"output_filename must contain {placeholder}")
        return v


class CollaborationStageModel(BaseModel):
    """协作阶段模型（扩展版）"""

    stage_id: str = Field(..., description="阶段唯一标识")
    stage_name: str = Field(..., description="阶段名称")
    roles: list[str] = Field(..., description="参与角色列表")
    tasks: list[str] = Field(..., description="任务列表")
    input: Optional[str] = Field(None, description="输入数据标识")
    output: Optional[str] = Field(None, description="输出数据标识")
    dependencies: Optional[list[str]] = Field(None, description="依赖阶段列表")
    conditions: Optional[dict[str, Any]] = Field(None, description="执行条件")
    timeout: Optional[int] = Field(None, description="超时时间（秒）")
    deliverables: Optional[list[DeliverableModel]] = Field(None, description="阶段产出物列表")

    @validator("stage_id")
    def validate_stage_id(cls, v):
        """验证阶段ID格式"""
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError("stage_id must be in UPPER_SNAKE_CASE format")
        return v


class CollaborationProtocolModel(BaseModel):
    """协作协议模型（扩展版）"""

    workflow_id: str = Field(..., description="协议唯一标识")
    name: str = Field(..., description="协议名称")
    description: str = Field(..., description="协议描述")
    version: str = Field(default="1.0.0", description="协议版本")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    # 核心角色定义
    roles: list[dict[str, Any]] = Field(..., description="角色定义列表")

    # 协作阶段
    stages: list[CollaborationStageModel] = Field(..., description="协作阶段列表")

    # 产出物清单
    deliverables: list[DeliverableModel] = Field(..., description="全局产出物清单")

    # 协作模式
    collaboration_patterns: Optional[list[dict[str, Any]]] = Field(
        None,
        description="协作模式定义",
    )

    # 通信协议
    communication_protocols: Optional[list[dict[str, Any]]] = Field(
        None,
        description="通信协议定义",
    )

    # 质量保证
    quality_assurance: Optional[dict[str, Any]] = Field(None, description="质量保证配置")

    # 成功指标
    success_metrics: Optional[dict[str, Any]] = Field(None, description="成功指标定义")

    @validator("workflow_id")
    def validate_workflow_id(cls, v):
        """验证工作流ID格式"""
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError("workflow_id must be in snake_case format")
        return v

    @validator("stages")
    def validate_stages(cls, v):
        """验证阶段列表"""
        if not v:
            raise ValueError("stages must contain at least one stage")

        # 检查阶段ID唯一性
        stage_ids = [stage.stage_id for stage in v]
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("All stage_ids must be unique")

        return v

    @validator("deliverables")
    def validate_deliverables(cls, v):
        """验证产出物列表"""
        if not v:
            raise ValueError("deliverables must contain at least one deliverable")

        # 检查产出物ID唯一性
        deliverable_ids = [deliverable.id for deliverable in v]
        if len(deliverable_ids) != len(set(deliverable_ids)):
            raise ValueError("All deliverable ids must be unique")

        return v


class ProjectConfigModel(BaseModel):
    """项目配置模型"""

    project_id: str = Field(..., description="项目唯一标识")
    project_name: str = Field(..., description="项目名称")
    created_at: str = Field(..., description="创建时间")
    status: str = Field(default="initialized", description="项目状态")
    deliverables: list[dict[str, Any]] = Field(
        default_factory=list,
        description="产出物记录列表",
    )
    stages: list[str] = Field(..., description="项目阶段列表")

    # 项目元数据
    metadata: Optional[dict[str, Any]] = Field(None, description="项目元数据")

    # 协作配置
    collaboration_config: Optional[dict[str, Any]] = Field(None, description="协作配置")

    # 文档配置
    document_config: Optional[dict[str, Any]] = Field(None, description="文档配置")

    @validator("project_id")
    def validate_project_id(cls, v):
        """验证项目ID格式"""
        if not re.match(r"^[a-z][a-z0-9_-]*$", v):
            raise ValueError(
                "project_id must be in snake_case format with optional hyphens",
            )
        return v


class DeliverableRecordModel(BaseModel):
    """产出物记录模型"""

    id: str = Field(..., description="产出物ID")
    name: str = Field(..., description="产出物名称")
    stage: str = Field(..., description="所属阶段")
    role: str = Field(..., description="负责角色")
    output_type: str = Field(..., description="产出物类型")
    filename: str = Field(..., description="文件名")
    created_at: str = Field(..., description="创建时间")
    model: str = Field(..., description="使用的模型")

    # 文件元数据
    file_metadata: Optional[dict[str, Any]] = Field(None, description="文件元数据")

    # 状态信息
    status: str = Field(default="created", description="产出物状态")


# 工具函数
def create_deliverable_metadata(
    model: str,
    role_id: str,
    prompt: str,
    summary: Optional[str] = None,
    conversation_ids: Optional[list[str]] = None,
    user_requirements: Optional[str] = None,
    parent_task_id: Optional[str] = None,
    output_format: str = "markdown",
) -> DeliverableMetadataModel:
    """创建产出物元数据"""
    return DeliverableMetadataModel(
        model=model,
        generated_at=datetime.now().isoformat(),
        role_id=role_id,
        prompt=prompt,
        summary=summary,
        conversation_ids=conversation_ids,
        user_requirements=user_requirements,
        parent_task_id=parent_task_id,
        output_format=output_format,
    )


def create_deliverable_requirement(
    min_words: Optional[int] = None,
    structure: Optional[str] = None,
    must_include: Optional[list[str]] = None,
    format_requirements: Optional[dict[str, Any]] = None,
) -> DeliverableRequirementModel:
    """创建产出物要求"""
    return DeliverableRequirementModel(
        min_words=min_words,
        structure=structure,
        must_include=must_include,
        format_requirements=format_requirements,
    )


def create_deliverable(
    deliverable_id: str,
    name: str,
    stage: str,
    role: str,
    output_type: str,
    output_filename: str,
    output_metadata: DeliverableMetadataModel,
    requirements: DeliverableRequirementModel,
    output_format: str = "markdown",
) -> DeliverableModel:
    """创建产出物定义"""
    return DeliverableModel(
        id=deliverable_id,
        name=name,
        stage=stage,
        role=role,
        output_type=output_type,
        output_format=output_format,
        output_filename=output_filename,
        output_metadata=output_metadata,
        requirements=requirements,
    )


def validate_collaboration_protocol(protocol_data: dict[str, Any]) -> dict[str, Any]:
    """验证协作协议"""
    try:
        protocol = CollaborationProtocolModel(**protocol_data)
        return {"status": "success", "message": "协议验证通过", "protocol": protocol.dict()}
    except Exception as e:
        return {"status": "error", "message": f"协议验证失败: {e!s}", "errors": str(e)}


def validate_project_config(config_data: dict[str, Any]) -> dict[str, Any]:
    """验证项目配置"""
    try:
        config = ProjectConfigModel(**config_data)
        return {"status": "success", "message": "项目配置验证通过", "config": config.dict()}
    except Exception as e:
        return {"status": "error", "message": f"项目配置验证失败: {e!s}", "errors": str(e)}
