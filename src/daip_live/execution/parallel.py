"""
Parallel execution engine for the Skills system.
"""
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
from ..skills.base import Skill, SkillInput, SkillOutput


class ParallelExecutor:
    """Executes skills in parallel with dependency management."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute_skills_parallel(self, 
                              skills: List[Skill], 
                              inputs: List[SkillInput],
                              dependencies: Optional[Dict[int, List[int]]] = None) -> List[SkillOutput]:
        """
        Execute multiple skills in parallel.
        
        Args:
            skills: List of skills to execute
            inputs: List of inputs for each skill
            dependencies: Dictionary mapping skill indices to their dependencies
            
        Returns:
            List of outputs from each skill
        """
        if len(skills) != len(inputs):
            raise ValueError("Number of skills must match number of inputs")
        
        dependencies = dependencies or {}
        outputs = [None] * len(skills)
        
        # For simplicity, we'll execute all skills in parallel
        # A more sophisticated implementation would respect dependencies
        futures = []
        for i, (skill, input_data) in enumerate(zip(skills, inputs)):
            if skill.is_enabled:
                future = self.executor.submit(self._execute_skill, skill, input_data)
                futures.append((i, future))
            else:
                outputs[i] = SkillOutput(
                    result=f"Skill {skill.metadata.name} is disabled",
                    metadata={"disabled": True}
                )
        
        # Collect results
        for i, future in futures:
            try:
                outputs[i] = future.result(timeout=30)  # 30 second timeout
            except Exception as e:
                outputs[i] = SkillOutput(
                    result=f"Error executing skill: {str(e)}",
                    metadata={"error": str(e)}
                )
        
        return outputs
    
    def _execute_skill(self, skill: Skill, input_data: SkillInput) -> SkillOutput:
        """Execute a single skill."""
        try:
            return skill.execute(input_data)
        except Exception as e:
            return SkillOutput(
                result=f"Error: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def execute_with_dependencies(self, 
                                skill_graph: Dict[Skill, List[Skill]], 
                                inputs: Dict[Skill, SkillInput]) -> Dict[Skill, SkillOutput]:
        """
        Execute skills with dependency management.
        
        Args:
            skill_graph: Dictionary mapping skills to their dependencies
            inputs: Dictionary mapping skills to their inputs
            
        Returns:
            Dictionary mapping skills to their outputs
        """
        # This is a simplified implementation that executes all skills in parallel
        # A full implementation would need to topologically sort the graph and
        # execute skills in the correct order respecting dependencies
        outputs = {}
        
        # Collect all skills
        all_skills = list(skill_graph.keys())
        all_inputs = [inputs.get(skill) for skill in all_skills]
        
        # Execute all skills in parallel
        skill_outputs = self.execute_skills_parallel(all_skills, all_inputs)
        
        # Map outputs back to skills
        for skill, output in zip(all_skills, skill_outputs):
            outputs[skill] = output
        
        return outputs
    
    def shutdown(self) -> None:
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)