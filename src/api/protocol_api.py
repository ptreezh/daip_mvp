#@AI-Generated: 2024-07-23, Confidence: 0.99, Model: Gemini-Code-Assist
"""
API Endpoints for Protocol Generation and Execution.
"""
import logging
import os
import subprocess
import sys
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from src.intelligent_protocol_generator import intelligent_protocol_generator
from src.protocol_executor import protocol_executor
from src.task_classifier import task_classifier

router = APIRouter(
    tags=["Protocol Generation & Execution"],
)
logger = logging.getLogger(__name__)


class IntelligentProtocolRequest(BaseModel):
    user_request: str = Field(..., description="用户的自然语言需求")
    use_analysis: bool = Field(True, description="是否使用任务分析增强")
    validate: bool = Field(True, description="是否验证生成的协议")
    save_to_file: bool = Field(False, description="是否保存到文件")
    output_path: Optional[str] = Field(None, description="输出文件路径")


class ProtocolExecutionRequest(BaseModel):
    protocol_id: str = Field(..., description="协议ID")
    inputs: dict[str, Any] = Field(default_factory=dict, description="输入参数")


@router.post("/generate_protocol")
async def generate_protocol(
    nl_text: str = Body(..., embed=True, description="自然语言协议描述"),
    biz_type: str = Body(..., embed=True, description="业务类型"),
    output_name: str = Body(..., embed=True, description="输出协议文件名，如 my_protocol.yaml"),
):
    """用户输入自然语言协议描述，自动生成结构化协议并持久化保存到 protocols 目录"""
    try:
        temp_txt = f"temp_protocol_{uuid.uuid4().hex}.txt"
        with open(temp_txt, "w", encoding="utf-8") as f:
            f.write(nl_text)
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "scripts", "protocol_nl_to_yaml.py"
        )
        result = subprocess.run(
            [sys.executable, script_path, temp_txt, biz_type, output_name],
            capture_output=True,
            text=True,
        )
        os.remove(temp_txt)
        if result.returncode != 0:
            raise Exception(result.stderr)
        protocol_path = os.path.join("protocols", biz_type, output_name)
        if not os.path.exists(protocol_path):
            raise Exception("协议文件未生成")
        return {"success": True, "protocol_path": protocol_path}
    except Exception as e:
        logger.error(f"协议生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"协议生成失败: {str(e)}")


@router.post("/intelligent_protocol/generate")
async def generate_intelligent_protocol(req: IntelligentProtocolRequest):
    """使用大模型智能生成DAIP协议"""
    try:
        if req.use_analysis:
            result = await intelligent_protocol_generator.generate_protocol_with_analysis(
                req.user_request, validate=req.validate
            )
        else:
            result = await intelligent_protocol_generator.generate_protocol(
                req.user_request, validate=req.validate
            )
        if req.save_to_file and result["success"] and req.output_path:
            os.makedirs(os.path.dirname(req.output_path), exist_ok=True)
            with open(req.output_path, "w", encoding="utf-8") as f:
                f.write(result["yaml_content"])
            result["saved_path"] = req.output_path
        return result
    except Exception as e:
        logger.error(f"智能协议生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"智能协议生成失败: {str(e)}")


@router.post("/intelligent_protocol/generate_smart")
async def generate_smart_protocol(req: IntelligentProtocolRequest):
    """智能协议生成 - 自动任务分类版本"""
    try:
        result = await intelligent_protocol_generator.generate_protocol_smart(
            req.user_request, validate=req.validate
        )
        if req.save_to_file and result["success"] and req.output_path:
            os.makedirs(os.path.dirname(req.output_path), exist_ok=True)
            with open(req.output_path, "w", encoding="utf-8") as f:
                f.write(result["yaml_content"])
            result["saved_path"] = req.output_path
        return result
    except Exception as e:
        logger.error(f"智能协议生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"智能协议生成失败: {str(e)}")


@router.post("/intelligent_protocol/classify")
async def classify_task(user_request: str = Body(..., embed=True)):
    """任务分类接口"""
    try:
        task_type, confidence, classification_info = task_classifier.classify_task(
            user_request
        )
        recommended_workflow = task_classifier.get_recommended_workflow(task_type)
        return {
            "success": True,
            "task_type": task_type.value,
            "confidence": confidence,
            "classification_info": classification_info,
            "recommended_workflow": recommended_workflow,
            "message": f"任务分类完成: {task_type.value}",
        }
    except Exception as e:
        logger.error(f"任务分类失败: {e}")
        raise HTTPException(status_code=500, detail=f"任务分类失败: {str(e)}")


@router.post("/protocols/execute")
async def execute_protocol(request: ProtocolExecutionRequest):
    """执行协议"""
    try:
        result = await protocol_executor.execute_protocol(
            request.protocol_id, request.inputs
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocols/{protocol_id}/status")
async def get_protocol_status(protocol_id: str):
    """获取协议执行状态"""
    try:
        status = protocol_executor.get_execution_status(protocol_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocols/{protocol_id}/history")
async def get_protocol_history(protocol_id: str):
    """获取协议执行历史"""
    try:
        history = protocol_executor.get_execution_history(protocol_id)
        return {"history": [result.dict() for result in history]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))