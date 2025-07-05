import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import subprocess
import time
from datetime import datetime
from typing import Optional

import uvicorn
import yaml
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

# 加载环境变量
load_dotenv()

from sqlalchemy.orm import Session

# 导入智能聊天室API
from src.chatroom_api import chat_router
from src.collaborative_analysis_api import collaborative_analysis_router
from src.config import CHROMA_PATH, DATABASE_PATH, get_tool_definitions_path
from src.consensus_api import consensus_router

# 导入辩论API
from src.debate_api import debate_router
from src.dependencies import get_db_session, init_db
from src.document_analysis_api import document_router

# 导入专家库API
from src.expert_api import expert_library_router, expert_router

# 导入财务报告API
from src.financial_report_api import financial_report_router

# 在导入部分添加轻量级记忆服务
from src.lightweight_memory_api import app as lightweight_memory_app
from src.lightweight_memory_service import LightweightMemoryService

# 导入多角色协作聊天室API
from src.multi_chat_api import multi_chat_router

# 导入MVP工作流API
from src.mvp_workflow_api import mvp_workflow_router
from src.observability import (
    add_error_to_span,
    add_event_to_span,
    create_span,
)
from src.orchestrator import Orchestrator

# 导入新创建的API
from src.protocol_api import protocol_router
from src.sskg_new import SSKG

# 导入系统管理API
from src.system_api import system_router

# 导入虚拟团队API
from src.virtual_team_api import virtual_team_router

# 新增统一工具配置
# 导入新的Wiki协同编辑API、共识系统API和协同文档分析API
from src.wiki_collaboration_api import wiki_router

# 创建FastAPI应用实例
app = FastAPI(title="DAIP Insight Engine", description="智能文档分析与报告生成器", version="1.0.0")

# 包含Wiki协同编辑路由、共识系统路由和协同文档分析路由
app.include_router(wiki_router)
app.include_router(consensus_router)
app.include_router(collaborative_analysis_router)

# 包含MVP工作流路由
app.include_router(mvp_workflow_router)

# 包含智能聊天室路由
app.include_router(chat_router)

# 包含多角色协作聊天室路由
app.include_router(multi_chat_router)

# 包含虚拟团队路由
app.include_router(virtual_team_router)

# 包含专家库路由
app.include_router(expert_router)
app.include_router(expert_library_router)  # 兼容性路由

# 包含系统管理路由
app.include_router(system_router)

# 包含新创建的API路由
app.include_router(protocol_router)
app.include_router(document_router)

# 添加轻量级记忆服务路由
app.mount("/lightweight-memory", lightweight_memory_app)

# 包含辩论路由
app.include_router(debate_router)

# 包含财务报告路由
app.include_router(financial_report_router)

# 全局变量存储实例
sskg_instance: Optional[SSKG] = None
orchestrator_instance: Optional[Orchestrator] = None
lightweight_memory_service: Optional[LightweightMemoryService] = None


# 请求模型
class DocumentAnalysisRequest(BaseModel):
    content: str
    use_all_tools: bool = False


# 响应模型
class DocumentAnalysisResponse(BaseModel):
    type: str
    content: str
    tool_calls: Optional[list] = None


# 依赖注入函数
def get_sskg() -> SSKG:
    global sskg_instance
    if sskg_instance is None:
        raise HTTPException(status_code=500, detail="SSKG not initialized")
    return sskg_instance


def get_orchestrator() -> Orchestrator:
    global orchestrator_instance
    if orchestrator_instance is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    return orchestrator_instance


def get_lightweight_memory_service() -> LightweightMemoryService:
    global lightweight_memory_service
    if lightweight_memory_service is None:
        raise HTTPException(status_code=503, detail="轻量级记忆服务未初始化")
    return lightweight_memory_service


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化组件"""
    global sskg_instance, orchestrator_instance, lightweight_memory_service

    print("DAIP Insight Engine 正在启动...")

    try:
        # 初始化数据库
        init_db()
        print("数据库初始化成功。")

        # 1. 初始化 SSKG
        sskg_instance = SSKG(DATABASE_PATH, CHROMA_PATH)
        sskg_instance.init_db()
        print("SSKG 初始化成功。")

        # 2. 初始化 Orchestrator（已统一工具管理和配置）
        orchestrator_instance = Orchestrator(sskg_instance)
        print("Orchestrator 初始化成功。")

        # 3. 初始化轻量级记忆服务
        lightweight_memory_service = LightweightMemoryService(
            data_dir="data/lightweight_memory",
            enable_redis=os.getenv("ENABLE_REDIS_CACHE", "false").lower() == "true",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        )
        print("轻量级记忆服务初始化成功。")

        print("DAIP Insight Engine 启动完成！")

    except Exception as e:
        print(f"ERROR: Failed to initialize DAIP Insight Engine components: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    global sskg_instance, lightweight_memory_service

    print("Closing database connections...")
    if sskg_instance:
        sskg_instance.close()
        print("Database connections closed.")

    if lightweight_memory_service:
        await lightweight_memory_service.close()
        print("轻量级记忆服务已关闭。")

    print("DAIP Insight Engine 已关闭。")


@app.get("/")
async def root():
    """根路径，返回服务状态"""
    return {
        "message": "DAIP Insight Engine API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    global sskg_instance, orchestrator_instance

    if sskg_instance is None or orchestrator_instance is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    return {
        "status": "healthy",
        "sskg_ready": sskg_instance is not None,
        "orchestrator_ready": orchestrator_instance is not None,
    }


@app.post("/analyze_document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    request: DocumentAnalysisRequest,
    biz_type: str = Query("financial_report"),
    session_id: Optional[str] = Query(None),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db_session),
):
    """分析文档内容并生成结构化报告
    - **content**: 文档内容
    - **use_all_tools**: 是否使用所有工具（默认False，使用动态筛选）
    - **biz_type**: 业务类型（如 financial_report, textbook_editor）
    - **session_id**: 会话ID，用于加载特定的工具和知识
    """
    span = create_span(
        "analyze_document",
        {
            "biz_type": biz_type,
            "content_length": len(request.content),
            "use_all_tools": request.use_all_tools,
            "session_id": session_id,
        },
    )
    try:
        add_event_to_span(span, "analysis_started")
        print(
            f"收到文档分析请求，会话ID: {session_id}, 内容长度: {len(request.content)} 字符，业务类型: {biz_type}",
        )

        orchestrator.set_biz_type(biz_type)
        add_event_to_span(span, "orchestrator_configured")

        result = await orchestrator.process_command(
            request.content,
            use_all_tools=request.use_all_tools,
            session_id=session_id,
        )
        add_event_to_span(span, "analysis_completed")
        # 兼容原有API返回格式
        return DocumentAnalysisResponse(
            type=result.get("type", "text"),
            content=result.get("content", ""),
            tool_calls=result.get("tool_calls"),
        )
    except Exception as e:
        add_error_to_span(span, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_tools(
    session_id: Optional[str] = Query(None),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """获取指定会话或默认的可用工具列表"""
    orchestrator._load_tool_definitions(session_id)
    tools = orchestrator.all_loaded_tool_definitions
    return {
        "session_id": session_id or "default",
        "total_tools": len(tools),
        "tools": [tool["function"]["name"] for tool in tools],
    }


@app.get("/analysis/{task_id}/status")
async def get_analysis_status(task_id: str, db: Session = Depends(get_db_session)):
    """获取分析任务状态"""
    with create_span("get_analysis_status", {"task_id": task_id}) as span:
        try:
            # 从数据库查询任务状态
            from sqlalchemy import select

            from src.sskg_new import Task

            stmt = select(Task).where(Task.task_id == task_id)
            task = db.exec(stmt).first()

            if not task:
                add_event_to_span(span, "task_not_found")
                raise HTTPException(status_code=404, detail="Task not found")

            add_event_to_span(span, "task_found", {"status": task.status})

            return {
                "task_id": task_id,
                "status": task.status,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "progress": task.progress if hasattr(task, "progress") else 0,
            }
        except Exception as e:
            add_error_to_span(span, e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get task status: {e!s}",
            )


@app.get("/analysis/{task_id}/sources")
async def get_analysis_sources(task_id: str, db: Session = Depends(get_db_session)):
    """获取分析结果的溯源信息"""
    span = create_span("get_analysis_sources", {"task_id": task_id})
    try:
        from sqlalchemy import select

        from src.models import DialogueMessage

        # 假设业务上task_id与message有关，实际应有外键或额外字段，这里仅演示修复
        # stmt = select(DialogueMessage).where(DialogueMessage.task_id == task_id)
        # messages = db.exec(stmt).all()
        # 这里暂时查询所有消息，实际应根据业务字段过滤
        stmt = select(DialogueMessage)
        messages = db.execute(stmt).scalars().all()

        sources = []
        for msg in messages:
            if msg.role == "assistant" and msg.content:
                source_info = {
                    "message_id": msg.message_id,
                    "content": msg.content,
                    "source_chunks": getattr(msg, "source_chunks", []),
                    "timestamp": msg.timestamp if msg.timestamp else None,
                }
                sources.append(source_info)

        add_event_to_span(span, "sources_retrieved", {"source_count": len(sources)})

        return {"task_id": task_id, "total_sources": len(sources), "sources": sources}
    except Exception as e:
        add_error_to_span(span, e)
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {e!s}")


@app.get("/analysis/{task_id}/source/{source_id}")
async def get_source_detail(
    task_id: str,
    source_id: str,
    db: Session = Depends(get_db_session),
):
    """获取特定溯源信息的详细信息"""
    try:
        from sqlalchemy import select

        from src.models import DialogueMessage

        stmt = select(DialogueMessage).where(DialogueMessage.message_id == source_id)
        message = db.execute(stmt).scalars().first()

        if not message:
            raise HTTPException(status_code=404, detail="Source not found")

        return {
            "source_id": source_id,
            "task_id": task_id,
            "content": message.content,
            "source_chunks": getattr(message, "source_chunks", []),
            "original_context": getattr(message, "original_context", ""),
            "timestamp": message.timestamp if message.timestamp else None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get source detail: {e!s}",
        )


@app.post("/tools/generate")
async def generate_tool_from_nl(
    session_id: str = Query(None),
    description: str = Body(..., embed=True),
):
    """用自然语言描述生成工具定义，并自动注册到本会话工具库"""
    prompt = f"""你是工具定义专家，请将下述需求转为OpenAI function-calling格式的JSON工具定义，要求字段完整、参数类型清晰、描述详细：\n需求：{description}\n"""
    from src.orchestrator import orchestrator_instance

    llm_result = await orchestrator_instance.llm_interaction_module.get_llm_response(
        prompt,
        [],
    )
    try:
        tool_def = json.loads(llm_result["content"])
    except Exception as e:
        return {"status": "error", "msg": f"解析失败: {e}", "raw": llm_result}
    path = get_tool_definitions_path(session_id)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            tools_data = json.load(f)
    else:
        tools_data = {"tools": []}
    tools_data["tools"].append(tool_def)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tools_data, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "tool": tool_def}


@app.post("/upload_knowledge")
async def upload_knowledge(session_id: str = Query(None), file: UploadFile = File(...)):
    """上传知识文档，自动分块入库，带session_id元数据"""
    from src.sskg_new import SSKG

    sskg = SSKG(DATABASE_PATH, CHROMA_PATH)
    sskg.init_db()
    content = await file.read()
    filename = file.filename
    # 简单分块（可根据实际分块逻辑优化）
    text = content.decode("utf-8", errors="ignore")
    chunk_size = 1000
    blocks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    block_ids = []
    for idx, block in enumerate(blocks):
        meta = {"session_id": session_id, "filename": filename, "block_idx": idx}
        block_id = sskg.add_knowledge_block(block, meta)
        block_ids.append(block_id)
    sskg.close()
    return {"status": "ok", "block_ids": block_ids}


@app.get("/knowledge_blocks")
async def get_knowledge_blocks(session_id: str = Query(None)):
    from src.sskg_new import SSKG

    sskg = SSKG(DATABASE_PATH, CHROMA_PATH)
    sskg.init_db()
    blocks = sskg.get_knowledge_blocks_by_session(session_id)
    sskg.close()
    return {"blocks": blocks}


@app.delete("/knowledge_blocks/{block_id}")
async def delete_knowledge_block(block_id: str, session_id: str = Query(None)):
    from src.sskg_new import SSKG

    sskg = SSKG(DATABASE_PATH, CHROMA_PATH)
    sskg.init_db()
    ok = sskg.delete_knowledge_block(block_id, session_id)
    sskg.close()
    return {"status": "ok" if ok else "not found"}


@app.post("/execute_wiki_protocol")
async def execute_wiki_protocol(file: UploadFile = File(...)):
    protocol_path = f"protocols/{file.filename}"
    with open(protocol_path, "wb") as f:
        f.write(await file.read())
    # 解析协议
    with open(protocol_path, encoding="utf-8") as f:
        protocol = yaml.safe_load(f)
    entry = protocol["entry"]
    topic = protocol["topic"]
    experts = protocol["experts"]
    workflow = protocol["workflow"]
    voting_rule = protocol.get("voting", {})
    conflict_rule = protocol.get("conflict", {})
    versioning = protocol.get("versioning", {})
    # 获取当前内容
    current_content = load_wiki_content(entry)
    # 执行workflow
    context = {"entry": entry, "topic": topic, "current_content": current_content}
    expert_suggestions = []
    fit_scores = [e.get("fit_score", 5) for e in experts]
    revisions = []
    votes = []
    consensus = ""
    for step in workflow:
        if step["step"] == "independent_edit":
            expert_suggestions = [
                generate_expert_suggestion(entry, topic, expert, current_content)
                for expert in experts
            ]
        elif step["step"] == "conflict_detection":
            revisions = detect_and_resolve_conflicts(
                expert_suggestions,
                experts,
                threshold=conflict_rule.get("threshold", 0.5),
            )
        elif step["step"] == "voting":
            consensus, votes = consensus_voting(
                expert_suggestions,
                experts,
                fit_scores,
                method=voting_rule.get("method", "weighted_majority"),
            )
            context["consensus"] = consensus
            context["votes"] = votes
        elif step["step"] == "consensus":
            pass
        elif step["step"] == "versioning":
            save_wiki_version(
                entry,
                context["consensus"],
                "专家共识",
                time.strftime("%Y-%m-%d %H:%M:%S"),
            )
    # 存储本轮中间结果
    round_id = len(
        [v for v in load_wiki_history(entry) if v.get("editor") == "专家共识"],
    )  # 轮次
    result_path = f"protocols/{entry}_round{round_id}_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "experts": [
                    {
                        "role": e["name"],
                        "suggestion": s,
                        "fit_score": e.get("fit_score", 5),
                    }
                    for e, s in zip(experts, expert_suggestions, strict=False)
                ],
                "revisions": revisions,
                "votes": votes,
                "consensus": consensus,
                "conflicts": [],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    return {"status": "ok"}


@app.get("/wiki_protocol_result")
def wiki_protocol_result(entry: str = Query(...), round: int = Query(1)):
    result_path = f"protocols/{entry}_round{round}_result.json"
    if not os.path.exists(result_path):
        return {
            "experts": [],
            "revisions": [],
            "votes": [],
            "consensus": "",
            "conflicts": [],
        }
    with open(result_path, encoding="utf-8") as f:
        return json.load(f)


# 兼容性函数
import json
import os
import time


def load_wiki_content(entry):
    path = f"wiki_entries/{entry}.json"
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("content", "")


def load_wiki_history(entry):
    path = f"wiki_entries/{entry}.json"
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("history", [])


def save_wiki_version(entry, content, editor, timestamp):
    path = f"wiki_entries/{entry}.json"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"content": "", "history": []}
    data["content"] = content
    data["history"].append(
        {
            "version": max([v["version"] for v in data["history"]], default=0) + 1,
            "content": content,
            "editor": editor,
            "timestamp": timestamp,
        },
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.get("/ollama_models")
def ollama_models():
    # 调用ollama list命令获取本地模型
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=False
        )
        lines = result.stdout.strip().split("\n")
        models = []
        for line in lines[1:]:  # 跳过表头
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            # 简单规则：embedding模型名里有embed，其他为llm
            mtype = "embedding" if "embed" in name or "bge" in name else "llm"
            models.append({"name": name, "type": mtype})
        return {"models": models}
    except Exception:
        return {"models": []}


# 添加轻量级记忆服务健康检查
@app.get("/lightweight-memory/health")
async def lightweight_memory_health_check():
    """轻量级记忆服务健康检查"""
    global lightweight_memory_service

    if lightweight_memory_service is None:
        raise HTTPException(status_code=503, detail="轻量级记忆服务未初始化")

    try:
        metrics = lightweight_memory_service.get_performance_metrics()
        return {
            "status": "healthy",
            "service": "lightweight_memory_service",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"轻量级记忆服务异常: {e!s}")


# 添加记忆服务选择端点
@app.get("/memory/service/status")
async def get_memory_service_status():
    """获取记忆服务状态"""
    global lightweight_memory_service

    status = {
        "lightweight_memory_service": {
            "status": "available" if lightweight_memory_service else "unavailable",
            "type": "lightweight",
            "features": [
                "high_performance",
                "async_processing",
                "smart_caching",
                "fault_tolerance",
                "priority_queue",
            ],
        },
        "unified_memory_service": {
            "status": "available",
            "type": "unified",
            "features": [
                "cross_model_validation",
                "consensus_building",
                "multi_system_integration",
            ],
        },
    }

    return status


if __name__ == "__main__":
    # 开发环境运行
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
