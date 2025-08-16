"""@Time    : 2025-07-24 16:30:00
@Author  : DAIP-LIVE Team
@File    : task_decomposition_node.py
@Description:
    TaskDecompositionNode for Multi-perspective Synthesis Workflow.
"""
import json
import logging
import re
from datetime import datetime
from typing import Any

from ..base import ExecutionContext, InstitutionalPrimitive
from .models import SubProblem

logger = logging.getLogger(__name__)


class TaskDecompositionNode(InstitutionalPrimitive):
    """任务分解节点 - Decomposes complex topics into multiple sub-problems representing different perspectives.
    
    Uses a "规划者" role to break down complex topics into sub-problems that can be
    analyzed from different perspectives (e.g., economic, social, technical, ethical).
    """
<<<<<<< HEAD

    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
=======
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
>>>>>>> feature/core-services-refactor
        super().__init__(primitive_id, config)
        self.planner_role = config.get("planner_role", "规划者") if config else "规划者"
        self.default_perspectives = config.get("default_perspectives", ["经济", "社会", "技术", "伦理"]) if config else ["经济", "社会", "技术", "伦理"]
        self.max_sub_problems = config.get("max_sub_problems", 5) if config else 5
<<<<<<< HEAD

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
=======
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Execute task decomposition for a complex topic.
        
        Args:
            inputs: Should contain 'topic' to decompose
            context: Execution context
            
        Returns:
            List of decomposed sub-problems

        """
        context.mark_started()

        try:
            # Extract inputs
            topic = inputs.get("topic", "")
            custom_perspectives = inputs.get("perspectives", [])

            if not topic:
                raise ValueError("Topic is required for task decomposition")

            # Get LLM interface from services
            llm_interface = context.services.get("llm_interface")
            if not llm_interface:
                raise ValueError("LLM interface not available in execution context")

            # Get role manager from services
            role_manager = context.services.get("role_manager")

            # Prepare perspectives to use
            perspectives = custom_perspectives if custom_perspectives else self.default_perspectives

            # Prepare decomposition prompt
            planner_role_prompt = ""
            if role_manager:
                planner_role = role_manager.get_role_by_id(self.planner_role)
                if planner_role:
                    planner_role_prompt = planner_role.system_prompt

            if not planner_role_prompt:
                planner_role_prompt = """你是一位专业的任务分解专家，擅长将复杂问题分解为多个子问题，以便从不同角度进行分析。
你的任务是将给定的主题分解为多个子问题，每个子问题代表一个不同的视角。
对于每个子问题，你需要提供：
1. 视角名称（如经济、社会、技术、伦理等）
2. 详细描述
3. 关键问题列表
4. 所需专业知识领域
5. 优先级（1-5，1为最高）"""

            decomposition_prompt = f"""请将以下复杂主题分解为多个子问题，以便从不同角度进行分析：

主题：{topic}

请考虑以下视角：{', '.join(perspectives)}

对于每个视角，请提供：
1. 视角名称
2. 详细描述
3. 关键问题列表（3-5个问题）
4. 所需专业知识领域
5. 优先级（1-5，1为最高）

请以JSON格式输出，格式如下：
```json
[
  {{
    "perspective": "视角名称",
    "description": "详细描述",
    "questions": ["问题1", "问题2", "问题3"],
    "expertise_required": ["专业领域1", "专业领域2"],
    "priority": 优先级数字
  }},
  ...
]
```"""

            # Generate decomposition
            messages = [
                {"role": "system", "content": planner_role_prompt},
                {"role": "user", "content": decomposition_prompt}
            ]

            response = await llm_interface.generate(messages)
            decomposition_text = response.get("content", "")

            # Extract JSON from response
            sub_problems_data = self._extract_json_from_text(decomposition_text)

            # Convert to SubProblem objects
            sub_problems = []
            for i, data in enumerate(sub_problems_data[:self.max_sub_problems]):
                sub_problem = SubProblem(
                    id=f"sub_problem_{context.execution_id}_{i}",
                    perspective=data.get("perspective", "Unknown"),
                    description=data.get("description", ""),
                    questions=data.get("questions", []),
                    expertise_required=data.get("expertise_required", []),
                    priority=data.get("priority", 5),
                    metadata={
                        "topic": topic,
                        "decomposition_timestamp": datetime.now().isoformat()
                    }
                )
                sub_problems.append(sub_problem)

            # Store in workflow state
            context.state["topic"] = topic
            context.state["sub_problems"] = [problem.model_dump() for problem in sub_problems]

            context.mark_completed()

            return {
                "topic": topic,
                "sub_problems": [problem.model_dump() for problem in sub_problems],
                "sub_problem_count": len(sub_problems),
                "success": True
            }

        except Exception as e:
            context.mark_failed()
            logger.error(f"TaskDecompositionNode execution failed: {e}")
            return {
                "topic": inputs.get("topic", ""),
                "sub_problems": [],
                "sub_problem_count": 0,
                "success": False,
                "error": str(e)
            }
<<<<<<< HEAD

    def _extract_json_from_text(self, text: str) -> List[Dict[str, Any]]:
=======
    
    def _extract_json_from_text(self, text: str) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Extract JSON data from text response."""
        # Find JSON content between triple backticks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON array directly
            json_match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', text)
            if json_match:
                json_str = json_match.group(0)
            else:
                logger.warning("Could not extract JSON from response")
                return []

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return []
<<<<<<< HEAD

    def get_input_schema(self) -> Dict[str, Any]:
=======
    
    def get_input_schema(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Return input schema for the task decomposition node."""
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Complex topic to decompose"
                },
                "perspectives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of perspectives to consider"
                }
            },
            "required": ["topic"]
        }
<<<<<<< HEAD

    def get_output_schema(self) -> Dict[str, Any]:
=======
    
    def get_output_schema(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Return output schema for the task decomposition node."""
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Original topic"
                },
                "sub_problems": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of decomposed sub-problems"
                },
                "sub_problem_count": {
                    "type": "integer",
                    "description": "Number of sub-problems"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether decomposition was successful"
                }
            },
            "required": ["topic", "sub_problems", "sub_problem_count", "success"]
        }
