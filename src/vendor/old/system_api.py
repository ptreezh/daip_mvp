"""系统管理API接口
提供RESTful API支持系统管理功能
"""

import os
import subprocess
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel


# 请求模型
class SystemConfigRequest(BaseModel):
    config: dict[str, Any]


# 创建路由器
system_router = APIRouter(prefix="/system", tags=["system"])


@system_router.get("/status")
async def get_system_status():
    """获取系统状态"""
    try:
        # 检查核心组件状态
        status = {
            "status": "running",
            "sskg_ready": True,  # 这里应该检查实际的SSKG状态
            "orchestrator_ready": True,  # 这里应该检查实际的Orchestrator状态
            "timestamp": datetime.now().isoformat(),
        }
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@system_router.get("/config")
async def get_system_config():
    """获取系统配置"""
    try:
        # 从配置文件或环境变量获取配置
        config = {
            "max_concurrent_tasks": int(os.getenv("MAX_CONCURRENT_TASKS", "10")),
            "default_analysis_type": os.getenv(
                "DEFAULT_ANALYSIS_TYPE",
                "financial_report",
            ),
            "model_config": {
                "default_model": os.getenv("DEFAULT_MODEL", "llama3.1:8b"),
                "api_timeout": int(os.getenv("API_TIMEOUT", "30")),
            },
            "database_config": {
                "max_connections": int(os.getenv("DB_MAX_CONNECTIONS", "20")),
            },
        }
        return {"config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@system_router.put("/config")
async def update_system_config(request: SystemConfigRequest):
    """更新系统配置"""
    try:
        # 这里应该实现实际的配置更新逻辑
        # 目前只是返回成功响应
        return {
            "status": "success",
            "message": "系统配置更新成功",
            "updated_config": request.config,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@system_router.get("/ollama_models")
async def get_ollama_models():
    """获取Ollama模型列表"""
    try:
        # 调用ollama list命令获取本地模型
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode != 0:
            raise Exception(f"Ollama命令执行失败: {result.stderr}")

        # 解析ollama list输出
        lines = result.stdout.strip().split("\n")[1:]  # 跳过标题行
        models = []

        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    model_info = {
                        "name": parts[0],
                        "size": parts[1],
                        "modified_at": parts[2] if len(parts) > 2 else "",
                        "digest": parts[3] if len(parts) > 3 else "",
                    }
                    models.append(model_info)

        return {"models": models}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="获取模型列表超时")
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Ollama未安装或不在PATH中")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@system_router.post("/execute_wiki_protocol")
async def execute_wiki_protocol(file: UploadFile = File(...)):
    """执行Wiki协议"""
    try:
        # 读取协议文件
        content = await file.read()
        protocol_content = content.decode("utf-8")

        # 生成协议ID
        protocol_id = f"protocol_{int(datetime.now().timestamp())}"

        # 这里应该实现实际的协议执行逻辑
        # 目前只是返回成功响应

        return {
            "protocol_id": protocol_id,
            "status": "executing",
            "message": "Protocol execution started",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@system_router.get("/wiki_protocol_result")
async def get_wiki_protocol_result(
    entry: str = Query(...),
    round: int = Query(1, ge=1),
):
    """获取Wiki协议执行结果"""
    try:
        # 这里应该实现实际的协议结果获取逻辑
        # 目前返回模拟结果

        result = {
            "entry": entry,
            "round": round,
            "result": f"协议执行结果 - {entry} 第{round}轮",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
