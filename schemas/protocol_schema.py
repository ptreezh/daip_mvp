import re
from typing import Optional

from pydantic import BaseModel, Field, validator


class StageInputModel(BaseModel):
    type: str = Field(..., description="输入类型，external或stage")
    key: str = Field(..., description="输入字段名")
    from_stage: Optional[str] = Field(None, description="如为stage类型，指定来源stage名称")


class StageModel(BaseModel):
    """单个阶段的模型定义"""

    stage_name: str = Field(..., description="阶段名称，使用UPPER_SNAKE_CASE格式")
    role: str = Field(..., description="执行该阶段的AI专家角色描述")
    prompt_template: str = Field(..., description="详细的AI指令模板，可包含占位符")
    output_schema: str = Field(..., description="输出数据的Pydantic模型导入路径")
    inputs: Optional[list[StageInputModel]] = Field(None, description="本阶段输入依赖")
    outputs: Optional[list[str]] = Field(None, description="本阶段输出字段名列表")
    depends_on: Optional[list[str]] = Field(None, description="依赖的上游阶段名称列表")
    acceptance_required: Optional[bool] = Field(False, description="是否为人工验收节点")

    @validator("stage_name")
    def validate_stage_name(cls, v):
        """验证阶段名称格式"""
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError(
                "stage_name must be in UPPER_SNAKE_CASE format (e.g., EXTRACT_KEY_METRICS)",
            )
        return v

    @validator("output_schema")
    def validate_output_schema(cls, v):
        """验证输出模式路径格式"""
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", v):
            raise ValueError("output_schema must be a valid Python import path")
        return v

    @validator("inputs", each_item=True)
    def validate_inputs(cls, v):
        if v.type not in ("external", "stage"):
            raise ValueError('inputs.type must be "external" or "stage"')
        if v.type == "stage" and not v.from_stage:
            raise ValueError('inputs of type "stage" must specify from_stage')
        return v


class ProtocolModel(BaseModel):
    """DAIP协议模型定义"""

    workflow_id: str = Field(..., description="工作流唯一标识符，使用snake_case格式")
    description: str = Field(..., description="协议用途的人类可读描述")
    stages: list[StageModel] = Field(..., min_length=1, description="阶段列表，至少包含一个阶段")

    @validator("workflow_id")
    def validate_workflow_id(cls, v):
        """验证工作流ID格式"""
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(
                "workflow_id must be in snake_case format (e.g., financial_report_analyzer_v1)",
            )
        return v

    @validator("stages")
    def validate_unique_stage_names(cls, v):
        """验证阶段名称唯一性"""
        stage_names = [stage.stage_name for stage in v]
        if len(stage_names) != len(set(stage_names)):
            raise ValueError("All stage names must be unique")
        return v
