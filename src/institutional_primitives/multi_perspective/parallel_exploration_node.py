"""@Time    : 2025-07-24 16:30:00
@Author  : DAIP-LIVE Team
@File    : parallel_exploration_node.py
@Description:
    ParallelExplorationNode for Multi-perspective Synthesis Workflow.
"""
import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any

from ..base import ExecutionContext, InstitutionalPrimitive
from .models import ExpertViewpoint, SubProblem

logger = logging.getLogger(__name__)


class ParallelExplorationNode(InstitutionalPrimitive):
    """并行探索节点 - Assigns sub-problems to specialized expert AI roles for parallel exploration.
    
    Implements fan-out pattern to simultaneously deploy multiple expert roles
    to analyze different aspects of a complex topic.
    """
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.max_parallel_experts = config.get("max_parallel_experts", 5) if config else 5
        self.expert_roles = config.get("expert_roles", {}) if config else {}
        self.default_expert_role = config.get("default_expert_role", "专家") if config else "专家"
        self.use_tools = config.get("use_tools", True) if config else True
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute parallel exploration of sub-problems by expert roles.
        
        Args:
            inputs: Should contain 'sub_problems' to explore
            context: Execution context
            
        Returns:
            Expert viewpoints on each sub-problem
        """
        context.mark_started()
        
        try:
            # Get sub-problems from inputs or workflow state
            sub_problems_data = inputs.get("sub_problems") or context.state.get("sub_problems", [])
            topic = inputs.get("topic") or context.state.get("topic", "Unknown topic")
            
            if not sub_problems_data:
                raise ValueError("Sub-problems are required for parallel exploration")
            
            # Convert to SubProblem objects
            sub_problems = [SubProblem(**data) for data in sub_problems_data]
            
            # Get services
            llm_interface = context.services.get("llm_interface")
            role_manager = context.services.get("role_manager")
            tool_executor = context.services.get("tool_executor") if self.use_tools else None
            
            if not llm_interface:
                raise ValueError("LLM interface not available")
            
            # Create exploration tasks for each sub-problem
            exploration_tasks = []
            for sub_problem in sub_problems[:self.max_parallel_experts]:
                task = self._create_exploration_task(
                    sub_problem, 
                    topic,
                    llm_interface, 
                    role_manager,
                    tool_executor,
                    context
                )
                exploration_tasks.append(task)
            
            # Execute all explorations in parallel
            exploration_results = await asyncio.gather(*exploration_tasks, return_exceptions=True)
            
            # Process results
            viewpoints = []
            for result in exploration_results:
                if isinstance(result, ExpertViewpoint):
                    viewpoints.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Exploration task failed: {result}")
            
            # Store in workflow state
            context.state["viewpoints"] = [viewpoint.model_dump() for viewpoint in viewpoints]
            
            context.mark_completed()
            
            return {
                "viewpoints": [viewpoint.model_dump() for viewpoint in viewpoints],
                "viewpoint_count": len(viewpoints),
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"ParallelExplorationNode execution failed: {e}")
            return {
                "viewpoints": [],
                "viewpoint_count": 0,
                "success": False,
                "error": str(e)
            }
    
    async def _create_exploration_task(
        self,
        sub_problem: SubProblem,
        topic: str,
        llm_interface,
        role_manager,
        tool_executor,
        context: ExecutionContext
    ) -> ExpertViewpoint:
        """Create and execute a single exploration task."""
        try:
            # Determine expert role based on required expertise
            expert_role_id = self._select_expert_role(sub_problem.expertise_required)
            expert_name = expert_role_id
            
            # Get expert role prompt
            expert_role_prompt = ""
            if role_manager:
                expert_role = role_manager.get_role_by_id(expert_role_id)
                if expert_role:
                    expert_role_prompt = expert_role.system_prompt
                    expert_name = expert_role.name
            
            if not expert_role_prompt:
                expert_role_prompt = f"""你是一位专业的{sub_problem.perspective}领域专家，擅长从{sub_problem.perspective}角度分析问题。
你的任务是对给定的问题提供深入、全面的分析，包括：
1. 从{sub_problem.perspective}角度的详细观点
2. 支持你观点的证据
3. 你的推理过程
4. 你对自己观点的信心水平（0.0-1.0）

请确保你的分析具有专业深度，并考虑到该领域的最新研究和观点。"""
            
            # Prepare exploration prompt
            exploration_prompt = f"""请从{sub_problem.perspective}角度分析以下主题：

主题：{topic}

子问题描述：{sub_problem.description}

需要回答的关键问题：
{self._format_questions(sub_problem.questions)}

请提供：
1. 详细的专业观点
2. 支持你观点的证据
3. 你的推理过程
4. 你对自己观点的信心水平（0.0-1.0）

请以JSON格式输出，格式如下：
```json
{{
  "viewpoint": "你的详细观点",
  "supporting_evidence": ["证据1", "证据2", "证据3"],
  "reasoning_process": "你的推理过程",
  "confidence": 0.8  // 0.0到1.0之间的数字
}}
```"""
            
            # Execute tool if available
            tool_results = ""
            if tool_executor and self.use_tools:
                try:
                    tool_response = await self._execute_research_tool(
                        tool_executor, 
                        topic, 
                        sub_problem.perspective, 
                        sub_problem.questions
                    )
                    if tool_response:
                        tool_results = f"\n\n研究工具提供的相关信息：\n{tool_response}"
                except Exception as e:
                    logger.warning(f"Tool execution failed: {e}")
            
            # Generate expert viewpoint
            messages = [
                {"role": "system", "content": expert_role_prompt},
                {"role": "user", "content": exploration_prompt + tool_results}
            ]
            
            response = await llm_interface.generate(messages)
            viewpoint_text = response.get("content", "")
            
            # Extract JSON from response
            viewpoint_data = self._extract_json_from_text(viewpoint_text)
            
            # Create ExpertViewpoint object
            expert_viewpoint = ExpertViewpoint(
                expert_id=expert_role_id,
                expert_name=expert_name,
                expertise_areas=sub_problem.expertise_required,
                sub_problem_id=sub_problem.id,
                viewpoint=viewpoint_data.get("viewpoint", ""),
                supporting_evidence=viewpoint_data.get("supporting_evidence", []),
                confidence=viewpoint_data.get("confidence", 0.7),
                reasoning_process=viewpoint_data.get("reasoning_process", ""),
                metadata={
                    "perspective": sub_problem.perspective,
                    "topic": topic,
                    "exploration_timestamp": datetime.now().isoformat()
                }
            )
            
            return expert_viewpoint
            
        except Exception as e:
            logger.error(f"Exploration task failed for sub-problem {sub_problem.id}: {e}")
            # Return empty viewpoint on failure
            return ExpertViewpoint(
                expert_id="error",
                expert_name="Error",
                sub_problem_id=sub_problem.id,
                viewpoint=f"Exploration failed: {str(e)}",
                supporting_evidence=[],
                confidence=0.0,
                reasoning_process="",
                metadata={
                    "error": str(e),
                    "perspective": sub_problem.perspective
                }
            )
    
    def _select_expert_role(self, required_expertise: list[str]) -> str:
        """Select the most appropriate expert role based on required expertise."""
        if not required_expertise or not self.expert_roles:
            return self.default_expert_role
        
        # Find the expert role with the most matching expertise
        best_match = None
        best_match_count = 0
        
        for role_id, expertise_areas in self.expert_roles.items():
            match_count = sum(1 for exp in required_expertise if exp in expertise_areas)
            if match_count > best_match_count:
                best_match = role_id
                best_match_count = match_count
        
        return best_match if best_match else self.default_expert_role
    
    def _format_questions(self, questions: list[str]) -> str:
        """Format a list of questions for the prompt."""
        return "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
    
    async def _execute_research_tool(
        self, 
        tool_executor, 
        topic: str, 
        perspective: str, 
        questions: list[str]
    ) -> str:
        """Execute research tool to gather information."""
        try:
            # Try to execute a research tool if available
            result = tool_executor.execute(
                tool_name="research",
                topic=topic,
                perspective=perspective,
                questions=questions
            )
            
            if result.get("status") == "success":
                return result.get("result", "")
            else:
                logger.warning(f"Research tool execution failed: {result.get('message', 'Unknown error')}")
                return ""
        except Exception as e:
            logger.warning(f"Failed to execute research tool: {e}")
            return ""
    
    def _extract_json_from_text(self, text: str) -> dict[str, Any]:
        """Extract JSON data from text response."""
        # Find JSON content between triple backticks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{\s*"[^"]+"\s*:', text)
            if json_match:
                # Find the start of the JSON object
                start_idx = json_match.start()
                # Find the end by matching braces
                brace_count = 0
                end_idx = start_idx
                in_string = False
                escape_next = False
                
                for i in range(start_idx, len(text)):
                    char = text[i]
                    
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                
                json_str = text[start_idx:end_idx]
            else:
                logger.warning("Could not extract JSON from response")
                return {}
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            # Try to create a basic structure from the text
            return {
                "viewpoint": text[:1000] if len(text) > 1000 else text,
                "supporting_evidence": [],
                "reasoning_process": "",
                "confidence": 0.5
            }
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return input schema for the parallel exploration node."""
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
                    "description": "List of sub-problems to explore"
                }
            },
            "required": ["sub_problems"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema for the parallel exploration node."""
        return {
            "type": "object",
            "properties": {
                "viewpoints": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of expert viewpoints"
                },
                "viewpoint_count": {
                    "type": "integer",
                    "description": "Number of viewpoints"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether exploration was successful"
                }
            },
            "required": ["viewpoints", "viewpoint_count", "success"]
        }