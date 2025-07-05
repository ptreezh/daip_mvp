import logging
import os

from fastapi import APIRouter, Body, HTTPException

from src.api.dependencies import AppStateDep
from src.models import (
    DebateConfig,
    DebateResult,
    IntelligentProtocolRequest,
    ProtocolExecutionRequest,
)
from src.protocols.debate_protocol import DebateProtocol


router = APIRouter(
    prefix="/protocols",
    tags=["Protocol Management"],
)

logger = logging.getLogger(__name__)


@router.post("/generate_intelligent")
async def generate_intelligent_protocol(state: AppStateDep, req: IntelligentProtocolRequest):
    """
    Intelligently generate a DAIP protocol using an LLM.
    Supports natural language understanding, multi-stage decomposition, and role assignment.
    """
    try:
        generator = state.intelligent_protocol_generator
        if req.use_analysis:
            result = await generator.generate_protocol_with_analysis(
                req.user_request, validate=req.validate
            )
        else:
            result = await generator.generate_protocol(
                req.user_request, validate=req.validate
            )

        if req.save_to_file and result.get("success") and req.output_path:
            os.makedirs(os.path.dirname(req.output_path), exist_ok=True)
            with open(req.output_path, "w", encoding="utf-8") as f:
                f.write(result.get("yaml_content", ""))
            result["saved_path"] = req.output_path

        return result
    except Exception as e:
        logger.error(f"Intelligent protocol generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Protocol generation failed: {str(e)}")


@router.post("/classify_task")
async def classify_task(state: AppStateDep, user_request: str = Body(..., embed=True)):
    """
    Classify a user's request as either content creation or document analysis.
    """
    try:
        classifier = state.task_classifier
        task_type, confidence, info = classifier.classify_task(user_request)
        workflow = classifier.get_recommended_workflow(task_type)

        return {
            "success": True,
            "task_type": task_type.value,
            "confidence": confidence,
            "classification_info": info,
            "recommended_workflow": workflow,
        }
    except Exception as e:
        logger.error(f"Task classification failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Task classification failed: {str(e)}")


@router.post("/execute")
async def execute_protocol(state: AppStateDep, request: ProtocolExecutionRequest):
    """Execute a given protocol by its ID."""
    try:
        executor = state.protocol_executor
        result = await executor.execute_protocol(request.protocol_id, request.inputs)
        return result
    except Exception as e:
        logger.error(f"Protocol execution failed for ID {request.protocol_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Protocol execution failed: {str(e)}")


@router.get("/{protocol_id}/status")
async def get_protocol_status(state: AppStateDep, protocol_id: str):
    """Get the execution status of a protocol."""
    try:
        executor = state.protocol_executor
        status = executor.get_execution_status(protocol_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Protocol execution not found.")
        return status
    except Exception as e:
        logger.error(f"Failed to get protocol status for ID {protocol_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get protocol status: {str(e)}")


@router.get("/{protocol_id}/history")
async def get_protocol_history(state: AppStateDep, protocol_id: str):
    """Get the execution history of a protocol."""
    try:
        executor = state.protocol_executor
        history = executor.get_execution_history(protocol_id)
        if history is None:
            raise HTTPException(status_code=404, detail="Protocol history not found.")
        return {"history": [result.dict() for result in history]}
    except Exception as e:
        logger.error(f"Failed to get protocol history for ID {protocol_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get protocol history: {str(e)}")


@router.post("/run-debate", response_model=DebateResult, summary="Execute a Debate Protocol")
async def run_debate(
    config: DebateConfig,
    state: AppStateDep,
):
    """
    Run a full, multi-round debate based on the provided configuration.

    This endpoint orchestrates a debate by:
    1.  Initializing the `DebateProtocol` with required system services.
    2.  Executing the debate flow, including role turn-taking.
    3.  Invoking a specified consensus strategy tool.
    4.  Synthesizing the final results into a structured summary.

    Returns a `DebateResult` object containing the full history and outcomes.
    """
    try:
        # Instantiate the protocol with dependencies from the app state
        debate_protocol = DebateProtocol(
            interaction_manager=state.interaction_manager,
            synthesis_engine=state.synthesis_engine,
            tool_executor=state.tool_executor,
        )
        return await debate_protocol.execute(config)
    except Exception as e:
        logger.exception(f"An error occurred during debate execution: {e}")
        raise HTTPException(status_code=500, detail=f"Debate execution failed: {str(e)}")