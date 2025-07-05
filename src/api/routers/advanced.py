import logging

from fastapi import APIRouter, HTTPException

from src.api.dependencies import AppStateDep
from src.blockchain_consensus import ConsensusAlgorithm
from src.cognitive_conflict_gan import ConflictIntensity

router = APIRouter(
    prefix="/advanced",
    tags=["Advanced Engines"],
)

logger = logging.getLogger(__name__)


@router.post("/consensus/create_session")
async def create_consensus_session(
    state: AppStateDep, session_id: str, algorithm: str = "proof_of_authority"
):
    """Create a new blockchain consensus session."""
    try:
        from src.blockchain_consensus import BlockchainConsensusEngine
        algo = ConsensusAlgorithm(algorithm)
        engine = BlockchainConsensusEngine(algo)
        state.consensus_engines[session_id] = engine
        return {"success": True, "session_id": session_id, "algorithm": algorithm}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid consensus algorithm: {algorithm}")
    except Exception as e:
        logger.error(f"Failed to create consensus session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shor_decomposer/decompose")
async def decompose_task(state: AppStateDep, task_description: str):
    """Decompose a complex task using the Shor-inspired decomposer."""
    try:
        # This is a simplified interaction. A real implementation would use a TaskNode model.
        from src.shor_task_decomposer import TaskNode, TaskComplexity
        task = TaskNode(name="decomposed_task", description=task_description, complexity=TaskComplexity.COMPLEX)
        result = state.task_decomposer.decompose_task(task)
        # Convert result to a serializable dict
        result_dict = result.dict()
        result_dict.pop('original_task', None) # Avoid circular reference if any
        return {"success": True, "decomposition": result_dict}
    except Exception as e:
        logger.error(f"Task decomposition failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cognitive_gan/generate_conflict")
async def generate_cognitive_conflict(
    state: AppStateDep, session_id: str, context: dict, primary_concept: str
):
    """Generate a cognitive conflict using the GAN engine."""
    if session_id not in state.conflict_gan_engines:
        from src.cognitive_conflict_gan import CognitiveConflictGAN
        state.conflict_gan_engines[session_id] = CognitiveConflictGAN()

    gan_engine = state.conflict_gan_engines[session_id]
    try:
        context["primary_concept"] = primary_concept
        conflict = gan_engine.generator.generate_conflict(context, ConflictIntensity.MODERATE)
        evaluation = gan_engine.discriminator.evaluate_conflict(conflict)
        return {"success": True, "conflict": conflict.dict(), "evaluation": evaluation}
    except Exception as e:
        logger.error(f"Cognitive conflict generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))