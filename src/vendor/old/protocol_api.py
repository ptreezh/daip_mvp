"""协议管理API
提供协议生成、验证和管理功能
"""

import logging
from typing import Any, Optional

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 创建路由器
protocol_router = APIRouter(prefix="/protocols", tags=["protocols"])


# 请求模型
class ProtocolGenerationRequest(BaseModel):
    request: str
    business_type: str = "general"
    complexity: str = "medium"  # simple, medium, complex
    participants: Optional[list[str]] = None
    constraints: Optional[dict[str, Any]] = None
    description: Optional[str] = None
    requirements: Optional[list[str]] = None


class ProtocolValidationRequest(BaseModel):
    yaml_content: str
    validate_schema: bool = True
    validate_logic: bool = True
    protocol: Optional[dict[str, Any]] = None


# 响应模型
class ProtocolGenerationResponse(BaseModel):
    success: bool
    protocol_id: Optional[str] = None
    yaml_content: Optional[str] = None
    error: Optional[str] = None


class ProtocolValidationResponse(BaseModel):
    success: bool
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []


@protocol_router.post("/generate", response_model=ProtocolGenerationResponse)
async def generate_protocol(request: ProtocolGenerationRequest):
    """智能协议生成"""
    try:
        # 处理兼容字段
        request_text = request.request
        if request.description and not request.request:
            request_text = request.description

        # 模拟协议生成逻辑
        protocol_id = f"protocol_{request.business_type}_{hash(request_text) % 10000}"

        # 生成示例协议YAML
        yaml_content = f"""
workflow_id: {protocol_id}
description: 基于"{request_text}"生成的协议
business_type: {request.business_type}
complexity: {request.complexity}
stages:
  - stage_name: INITIAL_ANALYSIS
    role: "分析专家"
    prompt_template: "请分析以下需求: {request_text}"
    output_schema: "src.schemas.analysis.AnalysisResult"
  - stage_name: SOLUTION_DESIGN
    role: "设计专家"
    prompt_template: "基于分析结果设计解决方案"
    output_schema: "src.schemas.design.SolutionDesign"
  - stage_name: IMPLEMENTATION
    role: "实施专家"
    prompt_template: "实施设计的解决方案"
    output_schema: "src.schemas.implementation.ImplementationResult"
"""

        return ProtocolGenerationResponse(
            success=True,
            protocol_id=protocol_id,
            yaml_content=yaml_content,
        )
    except Exception as e:
        logging.error(f"协议生成失败: {e!s}")
        return ProtocolGenerationResponse(success=False, error=f"协议生成失败: {e!s}")


@protocol_router.post("/validate", response_model=ProtocolValidationResponse)
async def validate_protocol(request: ProtocolValidationRequest):
    """协议格式验证"""
    try:
        errors = []
        warnings = []

        # 处理兼容字段
        yaml_content = request.yaml_content
        if request.protocol and not request.yaml_content:
            # 将protocol字典转换为YAML格式
            yaml_content = yaml.dump(
                request.protocol,
                default_flow_style=False,
                allow_unicode=True,
            )

        # 基本YAML格式验证
        if not yaml_content.strip():
            errors.append("协议内容不能为空")
            return ProtocolValidationResponse(
                success=False,
                is_valid=False,
                errors=errors,
            )

        # 检查必需字段
        required_fields = ["workflow_id", "description", "stages"]
        yaml_lower = yaml_content.lower()

        for field in required_fields:
            if field not in yaml_lower:
                errors.append(f"缺少必需字段: {field}")

        # 检查stages结构
        if "stages:" in yaml_lower and "stage_name:" not in yaml_lower:
            errors.append("stages必须包含stage_name字段")

        # 检查角色定义
        if "role:" in yaml_lower and "prompt_template:" not in yaml_lower:
            warnings.append("建议为每个角色定义prompt_template")

        is_valid = len(errors) == 0

        return ProtocolValidationResponse(
            success=True,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
        )
    except Exception as e:
        logging.error(f"协议验证失败: {e!s}")
        return ProtocolValidationResponse(
            success=False,
            is_valid=False,
            errors=[f"协议验证失败: {e!s}"],
        )


@protocol_router.get("/types")
async def get_protocol_types():
    """获取支持的协议类型"""
    try:
        protocol_types = [
            {"type": "financial", "name": "财务分析协议", "description": "用于财务报告分析和风险评估"},
            {"type": "legal", "name": "法律文档协议", "description": "用于法律文档审查和合规分析"},
            {"type": "research", "name": "研究分析协议", "description": "用于学术研究和文献分析"},
            {"type": "business", "name": "商业分析协议", "description": "用于商业计划和市场分析"},
            {"type": "technical", "name": "技术文档协议", "description": "用于技术规范和架构设计"},
        ]

        return {"success": True, "protocol_types": protocol_types}
    except Exception as e:
        logging.error(f"获取协议类型失败: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))
