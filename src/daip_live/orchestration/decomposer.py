"""
Task decomposition system for the hierarchical architecture.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """Types of tasks that can be decomposed."""
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    TRANSFORMATION = "transformation"
    EVALUATION = "evaluation"


@dataclass
class Subtask:
    """Represents a decomposed subtask."""
    id: str
    description: str
    task_type: TaskType
    domain: str
    required_skills: List[str]
    dependencies: List[str]
    priority: int = 1
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DecomposedTask:
    """Represents a task that has been decomposed into subtasks."""
    original_task: str
    subtasks: List[Subtask]
    dependencies: Dict[str, List[str]]  # subtask_id -> list of dependent subtask_ids


class TaskDecomposer:
    """Decomposes complex tasks into manageable subtasks."""
    
    def __init__(self):
        # Simple keyword-based domain mapping for demonstration
        self._domain_keywords = {
            "grounded_theory": ["coding", "categories", "theory", "qualitative"],
            "sna": ["network", "relationship", "social", "connection"],
            "field_analysis": ["field", "capital", "institution", "education", "academic"],
            "ant": ["actor", "network", "technology", "policy", "healthcare"],
            "localization": ["chinese", "localization", "translation", "culture"]
        }
    
    def decompose(self, task: str, context: Optional[Dict[str, Any]] = None) -> DecomposedTask:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task: The task to decompose
            context: Additional context for decomposition
            
        Returns:
            DecomposedTask containing the original task and its subtasks
        """
        context = context or {}
        
        # Simple decomposition logic based on keywords
        subtasks = self._identify_subtasks(task, context)
        dependencies = self._analyze_dependencies(subtasks)
        
        return DecomposedTask(
            original_task=task,
            subtasks=subtasks,
            dependencies=dependencies
        )
    
    def _identify_subtasks(self, task: str, context: Dict[str, Any]) -> List[Subtask]:
        """Identify subtasks based on task content and context."""
        subtasks = []
        task_lower = task.lower()
        
        # Identify potential domains based on keywords
        domains = []
        for domain, keywords in self._domain_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                domains.append(domain)
        
        # If no domains identified, use a default
        if not domains:
            domains = ["analysis"]
        
        # Create subtasks for each identified domain
        for i, domain in enumerate(domains):
            subtask = Subtask(
                id=f"subtask_{i}",
                description=f"Analyze task using {domain} approach",
                task_type=TaskType.ANALYSIS,
                domain=domain,
                required_skills=[],
                dependencies=[],
                metadata={"original_task": task}
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def _analyze_dependencies(self, subtasks: List[Subtask]) -> Dict[str, List[str]]:
        """Analyze and determine dependencies between subtasks."""
        # For now, assume no dependencies between subtasks
        # In a more sophisticated implementation, this would analyze task relationships
        return {subtask.id: [] for subtask in subtasks}