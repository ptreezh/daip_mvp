import logging
import os
from typing import Any, Dict, List

from src.app_state import AppState
from src.models import DebateConfig, DebateResult, IntelligentProtocolRequest
from src.protocols.debate_protocol import DebateProtocol

logger = logging.getLogger(__name__)


class ProtocolService:
    """
    Service layer for handling protocol generation, classification, and execution.
    """

    def __init__(self, app_state: AppState):
        self.app_state = app_state

    async def generate_intelligent_protocol(self, req: IntelligentProtocolRequest) -> Dict[str, Any]:
        """Generates a DAIP protocol from a user's natural language request."""
        generator = self.app_state.intelligent_protocol_generator
        if req.use_analysis:
            result = await generator.generate_protocol_with_analysis(
                req.user_request, validate=req.should_validate
            )
        else:
            result = await generator.generate_protocol(
                req.user_request, validate=req.should_validate
            )

        if req.save_to_file and result.get("success") and req.output_path:
            os.makedirs(os.path.dirname(req.output_path), exist_ok=True)
            with open(req.output_path, "w", encoding="utf-8") as f:
                f.write(result.get("yaml_content", ""))
            result["saved_path"] = req.output_path
        return result

    def classify_task(self, user_request: str) -> Dict[str, Any]:
        """Classifies a user task and recommends a workflow."""
        classifier = self.app_state.task_classifier
        task_type, confidence, info = classifier.classify_task(user_request)
        workflow = classifier.get_recommended_workflow(task_type)
        return {
            "success": True,
            "task_type": task_type.value,
            "confidence": confidence,
            "classification_info": info,
            "recommended_workflow": workflow,
        }

    async def execute_protocol(self, protocol_id: str, inputs: Dict[str, Any]) -> Any:
        """Executes a given protocol by its ID."""
        return await self.app_state.protocol_executor.execute_protocol(protocol_id, inputs)

    def get_protocol_status(self, protocol_id: str) -> Any:
        """Gets the execution status of a protocol."""
        status = self.app_state.protocol_executor.get_execution_status(protocol_id)
        if status is None:
            raise ValueError("Protocol execution not found.")
        return status

    def get_protocol_history(self, protocol_id: str) -> List[Any]:
        """Gets the execution history of a protocol."""
        history = self.app_state.protocol_executor.get_execution_history(protocol_id)
        if history is None:
            raise ValueError("Protocol history not found.")
        return history

    async def run_debate(self, config: DebateConfig) -> DebateResult:
        """Runs a full, multi-round debate."""
        debate_protocol = DebateProtocol(
            interaction_manager=self.app_state.interaction_manager,
            synthesis_engine=self.app_state.synthesis_engine,
            tool_executor=self.app_state.tool_executor,
        )
        return await debate_protocol.execute(config)