"""@Time    : 2025-07-22 15:00:00
@Author  : DAIP-LIVE Team
@File    : task_context_optimizer.py
@Description:
    Task-focused context optimization service that enhances context preparation
    by focusing on current task requirements and essential background information.
"""
import logging
import re
from datetime import datetime
from enum import Enum
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel, Field

from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeQuery, NodeType
from src.core_services.memory_agent import MemAgent
from src.core_services.token_management_service import TokenManagementService

logger = logging.getLogger(__name__)


class ElementType(str, Enum):
    """Types of context elements."""

    INSTRUCTION = "instruction"
    KNOWLEDGE = "knowledge"
    CONVERSATION = "conversation"
    EXAMPLE = "example"
    TASK = "task"
    SYSTEM = "system"


class RequirementType(str, Enum):
    """Types of task requirements."""

    KNOWLEDGE = "knowledge"
    INSTRUCTION = "instruction"
    CONTEXT = "context"
    EXAMPLE = "example"
    TOOL = "tool"


class TaskRequirement(BaseModel):
    """Model for task requirements."""

    requirement_type: RequirementType
    content: str
    importance: float = Field(ge=0.0, le=1.0)
    keywords: list[str] = []


class ContextElement(BaseModel):
    """Model for context elements."""

    content: str
    element_type: ElementType
    relevance_score: float = Field(ge=0.0, le=1.0)
    token_count: int
    metadata: dict[str, Any] = {}


class OptimizedContext(BaseModel):
    """Model for optimized context."""
<<<<<<< HEAD

    elements: List[ContextElement]
=======
    elements: list[ContextElement]
>>>>>>> feature/core-services-refactor
    total_tokens: int
    task_focus: str
    optimization_metrics: dict[str, float]
    excluded_elements: list[ContextElement] = []


class TaskContextOptimizer:
    """Task-focused context optimization service that enhances context preparation
    by focusing on current task requirements and essential background information.
    """

    def __init__(
        self,
        token_service: TokenManagementService,
        sskg_manager: EnhancedSSKGManager,
        mem_agent: Optional[MemAgent] = None
    ):
        """Initialize the Task Context Optimizer.
        
        Args:
            token_service: Service for token counting and management
            sskg_manager: Enhanced SSKG manager for knowledge retrieval
            mem_agent: Optional MemAgent for advanced memory selection

        """
        self.token_service = token_service
        self.sskg_manager = sskg_manager
        self.mem_agent = mem_agent

        # Task analysis keywords
        self.task_keywords = {
            RequirementType.KNOWLEDGE: [
                "explain", "describe", "what is", "how does", "why", "background",
                "information", "details", "context", "knowledge", "understand"
            ],
            RequirementType.INSTRUCTION: [
                "create", "implement", "write", "develop", "build", "design",
                "modify", "update", "change", "add", "remove", "fix", "refactor"
            ],
            RequirementType.CONTEXT: [
                "based on", "referring to", "according to", "in the context of",
                "following", "continuing", "previous", "earlier", "before"
            ],
            RequirementType.EXAMPLE: [
                "example", "sample", "instance", "case", "illustration",
                "demonstration", "template", "pattern", "reference"
            ],
            RequirementType.TOOL: [
                "using", "with", "tool", "library", "framework", "api",
                "function", "method", "class", "module", "package"
            ]
        }

        logger.info("TaskContextOptimizer initialized")
<<<<<<< HEAD

    def extract_task_requirements(self, task: str) -> List[TaskRequirement]:
=======
    
    def extract_task_requirements(self, task: str) -> list[TaskRequirement]:
>>>>>>> feature/core-services-refactor
        """Extract requirements from a task description.
        
        Args:
            task: The task description
            
        Returns:
            List of task requirements

        """
        requirements = []

        # Check for each requirement type
        for req_type, keywords in self.task_keywords.items():
            # Calculate importance based on keyword matches
            importance = 0.0
            matched_keywords = []

            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', task.lower()):
                    importance += 0.1
                    matched_keywords.append(keyword)

            # Cap importance at 1.0
            importance = min(importance, 1.0)

            # Only add if we found matches
            if importance > 0:
                requirements.append(TaskRequirement(
                    requirement_type=req_type,
                    content=task,
                    importance=importance,
                    keywords=matched_keywords
                ))

        # If no specific requirements were found, add a generic one
        if not requirements:
            requirements.append(TaskRequirement(
                requirement_type=RequirementType.INSTRUCTION,
                content=task,
                importance=0.5,
                keywords=[]
            ))

        return requirements

    def prioritize_context_elements(
<<<<<<< HEAD
        self,
        context_elements: List[Dict[str, Any]],
        task_requirements: List[TaskRequirement]
    ) -> List[ContextElement]:
=======
        self, 
        context_elements: list[dict[str, Any]], 
        task_requirements: list[TaskRequirement]
    ) -> list[ContextElement]:
>>>>>>> feature/core-services-refactor
        """Prioritize context elements based on task requirements.
        
        Args:
            context_elements: List of context elements (messages, knowledge, etc.)
            task_requirements: List of task requirements
            
        Returns:
            List of prioritized context elements with relevance scores

        """
        prioritized_elements = []

        # Extract keywords from all requirements
        all_keywords = []
        for req in task_requirements:
            all_keywords.extend(req.keywords)

        # Process each context element
        for element in context_elements:
            element_type = ElementType.CONVERSATION
            content = element.get("content", "")
            role = element.get("role", "")

            # Determine element type
            if role == "system":
                element_type = ElementType.SYSTEM
            elif "instruction" in content.lower() or "task" in content.lower():
                element_type = ElementType.INSTRUCTION
            elif role == "user" and any(kw in content.lower() for kw in ["example", "sample", "instance"]):
                element_type = ElementType.EXAMPLE

            # Calculate token count
            token_count = self.token_service.count_tokens(content)

            # Calculate relevance score
            relevance_score = 0.3  # Base score

            # System messages are always relevant
            if role == "system":
                relevance_score = 0.9

            # Recent messages are more relevant
            recency = element.get("recency", 0.0)
            relevance_score += recency * 0.2

            # Check for keyword matches
            keyword_matches = sum(1 for kw in all_keywords if kw in content.lower())
            relevance_score += min(keyword_matches * 0.05, 0.3)

            # Check for task-specific content
            if "task" in content.lower() or "instruction" in content.lower():
                relevance_score += 0.2

            # Cap at 1.0
            relevance_score = min(relevance_score, 1.0)

            # Create context element
            context_element = ContextElement(
                content=content,
                element_type=element_type,
                relevance_score=relevance_score,
                token_count=token_count,
                metadata={
                    "role": role,
                    "timestamp": element.get("timestamp", datetime.now().isoformat()),
                    **element.get("metadata", {})
                }
            )

            prioritized_elements.append(context_element)

        # Sort by relevance score (descending)
        prioritized_elements.sort(key=lambda x: x.relevance_score, reverse=True)

        return prioritized_elements

    def blend_context_sources(
        self,
        task_instructions: str,
        background_knowledge: list[str],
        conversation_history: list[dict[str, Any]],
        max_tokens: int
    ) -> OptimizedContext:
        """Blend multiple context sources into an optimized context.
        
        Args:
            task_instructions: Task instructions
            background_knowledge: Background knowledge items
            conversation_history: Conversation history
            max_tokens: Maximum tokens for the context
            
        Returns:
            Optimized context

        """
        # Extract task requirements
        task_requirements = self.extract_task_requirements(task_instructions)

        # Create context elements
        context_elements = []

        # Add task instructions (highest priority)
        context_elements.append({
            "content": task_instructions,
            "role": "system",
            "recency": 1.0,
            "metadata": {"type": "instruction"}
        })

        # Add background knowledge
        for i, knowledge in enumerate(background_knowledge):
            context_elements.append({
                "content": knowledge,
                "role": "system",
                "recency": 0.5,
                "metadata": {"type": "knowledge", "index": i}
            })

        # Add conversation history with recency scores
        history_length = len(conversation_history)
        for i, message in enumerate(conversation_history):
            # Calculate recency (0.0 to 1.0, with 1.0 being most recent)
            recency = i / history_length if history_length > 0 else 0.0

            context_elements.append({
                "content": message.get("content", ""),
                "role": message.get("role", "user"),
                "recency": recency,
                "timestamp": message.get("timestamp", datetime.now().isoformat()),
                "metadata": message.get("metadata", {})
            })

        # Prioritize elements
        prioritized_elements = self.prioritize_context_elements(context_elements, task_requirements)

        # Select elements to include (respecting token limit)
        included_elements = []
        excluded_elements = []
        total_tokens = 0

        # Always include system instructions first
        system_instructions = [e for e in prioritized_elements if e.element_type == ElementType.SYSTEM]
        for element in system_instructions:
            if total_tokens + element.token_count <= max_tokens:
                included_elements.append(element)
                total_tokens += element.token_count
            else:
                excluded_elements.append(element)

        # Then include task-specific elements
        task_elements = [e for e in prioritized_elements if e.element_type == ElementType.INSTRUCTION
                        and e not in included_elements]
        for element in task_elements:
            if total_tokens + element.token_count <= max_tokens:
                included_elements.append(element)
                total_tokens += element.token_count
            else:
                excluded_elements.append(element)

        # Then include other elements by relevance score
        other_elements = [e for e in prioritized_elements if e not in included_elements
                         and e not in excluded_elements]
        for element in other_elements:
            if total_tokens + element.token_count <= max_tokens:
                included_elements.append(element)
                total_tokens += element.token_count
            else:
                excluded_elements.append(element)

        # Calculate optimization metrics
        optimization_metrics = {
            "compression_ratio": len(included_elements) / (len(included_elements) + len(excluded_elements))
                                if (len(included_elements) + len(excluded_elements)) > 0 else 1.0,
            "average_relevance": sum(e.relevance_score for e in included_elements) / len(included_elements)
                                if len(included_elements) > 0 else 0.0,
            "token_utilization": total_tokens / max_tokens if max_tokens > 0 else 0.0,
            "system_instruction_ratio": len([e for e in included_elements if e.element_type == ElementType.SYSTEM])
                                      / len(included_elements) if len(included_elements) > 0 else 0.0,
        }

        return OptimizedContext(
            elements=included_elements,
            total_tokens=total_tokens,
            task_focus=task_instructions,
            optimization_metrics=optimization_metrics,
            excluded_elements=excluded_elements
        )
    def maintain_task_coherence(
        self,
        context: list[dict[str, Any]],
        task: str
<<<<<<< HEAD
    ) -> List[Dict[str, Any]]:
=======
    ) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Maintain task coherence by preserving causal relationships and dependencies.
        
        Args:
            context: List of context elements
            task: The current task
            
        Returns:
            Modified context with preserved coherence

        """
        # Extract task requirements
        task_requirements = self.extract_task_requirements(task)

        # Identify key elements that must be preserved for coherence
        key_elements = []

        # Find elements that contain references to other elements
        reference_patterns = [
            r"as mentioned (above|earlier|previously)",
            r"referring to",
            r"according to",
            r"based on",
            r"in response to",
            r"following up on"
        ]

        # Identify elements with references
        elements_with_references = []
        referenced_elements = set()

        for i, element in enumerate(context):
            content = element.get("content", "").lower()

            # Check for reference patterns
            for pattern in reference_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    elements_with_references.append(i)

                    # Try to identify which element is being referenced
                    # This is a simple heuristic - in a real system, you'd want more sophisticated reference resolution
                    for j in range(max(0, i-5), i):
                        referenced_elements.add(j)

        # Mark key elements for preservation
        for i, element in enumerate(context):
            # System messages are always key
            if element.get("role") == "system":
                key_elements.append(i)

            # Elements with task-specific content are key
            content = element.get("content", "").lower()
            if any(req.content.lower() in content for req in task_requirements):
                key_elements.append(i)

            # Referenced elements are key
            if i in referenced_elements:
                key_elements.append(i)

            # Elements with references are key
            if i in elements_with_references:
                key_elements.append(i)

        # Ensure we preserve the coherence by keeping key elements
        coherent_context = []
        for i, element in enumerate(context):
            if i in key_elements:
                # Add key elements
                coherent_context.append(element)
            else:
                # For non-key elements, check if they're needed for coherence
                # For example, we might want to keep some elements to maintain conversation flow
                # This is a simple heuristic - in a real system, you'd want more sophisticated coherence analysis
                if i > 0 and i < len(context) - 1:
                    prev_is_key = i - 1 in key_elements
                    next_is_key = i + 1 in key_elements

                    # Keep elements that connect key elements
                    if prev_is_key and next_is_key:
                        coherent_context.append(element)
                    else:
                        # Otherwise, include based on relevance to task
                        content = element.get("content", "").lower()
                        if any(kw in content for req in task_requirements for kw in req.keywords):
                            coherent_context.append(element)
                else:
                    # Include boundary elements based on relevance to task
                    content = element.get("content", "").lower()
                    if any(kw in content for req in task_requirements for kw in req.keywords):
                        coherent_context.append(element)

        return coherent_context

    def delineate_task_boundaries(
        self,
        context: list[dict[str, Any]],
        current_task: str
<<<<<<< HEAD
    ) -> List[Dict[str, Any]]:
=======
    ) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Clearly delineate task boundaries in the context.
        
        Args:
            context: List of context elements
            current_task: The current active task
            
        Returns:
            Context with clear task boundaries

        """
        # Check if we have multiple tasks in the context
        tasks = []
        task_boundaries = []

        for i, element in enumerate(context):
            content = element.get("content", "").lower()

            # Look for task indicators
            if (element.get("role") == "system" and
                ("task:" in content or "instruction:" in content)):
                tasks.append((i, content))
                task_boundaries.append(i)

        # If we have multiple tasks, add clear boundary markers
        if len(tasks) > 1:
            modified_context = []
            current_task_index = -1

            # Find the current task index
            for i, (idx, task_content) in enumerate(tasks):
                if current_task.lower() in task_content:
                    current_task_index = i
                    break

            # If we couldn't find the current task, assume it's the last one
            if current_task_index == -1:
                current_task_index = len(tasks) - 1

            # Add elements with task boundary markers
            for i, element in enumerate(context):
                if i in task_boundaries:
                    task_index = task_boundaries.index(i)

                    # Add a boundary marker before the task
                    if task_index > 0:
                        boundary_marker = {
                            "role": "system",
                            "content": "--- End of Previous Task ---\n\n",
                            "metadata": {"type": "boundary_marker"}
                        }
                        modified_context.append(boundary_marker)

                    # Highlight the current task
                    if task_index == current_task_index:
                        current_task_marker = {
                            "role": "system",
                            "content": "--- CURRENT ACTIVE TASK ---\n\n",
                            "metadata": {"type": "current_task_marker"}
                        }
                        modified_context.append(current_task_marker)

                # Add the original element
                modified_context.append(element)

                # Add a marker after the last task
                if i == task_boundaries[-1]:
                    end_marker = {
                        "role": "system",
                        "content": "\n\n--- Focus on the current task above ---",
                        "metadata": {"type": "end_marker"}
                    }
                    modified_context.append(end_marker)

            return modified_context
        else:
            # If there's only one task, no need for boundaries
            return context

    def optimize_context_for_task(
        self,
        context: list[dict[str, Any]],
        task: str,
        max_tokens: int
    ) -> OptimizedContext:
        """Optimize context for a specific task.
        
        Args:
            context: List of context elements
            task: The current task
            max_tokens: Maximum tokens for the context
            
        Returns:
            Optimized context

        """
        # Extract task requirements
        task_requirements = self.extract_task_requirements(task)

        # Maintain task coherence
        coherent_context = self.maintain_task_coherence(context, task)

        # Delineate task boundaries
        bounded_context = self.delineate_task_boundaries(coherent_context, task)

        # Prioritize elements
        prioritized_elements = self.prioritize_context_elements(bounded_context, task_requirements)

        # Fetch relevant knowledge from SSKG if available
        background_knowledge = []
        if self.sskg_manager:
            # Build query based on task requirements
            knowledge_keywords = []
            for req in task_requirements:
                if req.requirement_type == RequirementType.KNOWLEDGE:
                    knowledge_keywords.extend(req.keywords)

            if knowledge_keywords:
                # Query SSKG for relevant knowledge
                query = KnowledgeQuery(
                    node_types=[NodeType.FACT, NodeType.WIKI, NodeType.CONCEPT],
                    content_query=" ".join(knowledge_keywords),
                    min_confidence=0.6,
                    limit=3
                )

                knowledge_nodes = self.sskg_manager.query(query)

                # Add knowledge to background
                for node in knowledge_nodes:
                    background_knowledge.append(node.content)

        # Use MemAgent for memory selection if available
        if self.mem_agent:
            try:
                # Get relevant memories
                memories = self.mem_agent.retrieve_memories(task, limit=3)

                # Add memories to background knowledge
                for memory in memories:
                    background_knowledge.append(memory.content)
            except Exception as e:
                logger.error(f"Error retrieving memories from MemAgent: {e}")

        # Create task instruction
        task_instruction = f"Current Task: {task}\n\nFocus on completing this specific task."

        # Blend context sources
        optimized_context = self.blend_context_sources(
            task_instruction,
            background_knowledge,
            bounded_context,
            max_tokens
        )

        return optimized_context

    def prepare_context_for_llm(
        self,
        context: list[dict[str, Any]],
        task: str,
        model: str
<<<<<<< HEAD
    ) -> List[Dict[str, Any]]:
=======
    ) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Prepare optimized context for LLM call.
        
        Args:
            context: List of context messages
            task: The current task
            model: Model name for token counting
            
        Returns:
            Optimized context messages ready for LLM

        """
        # Get max tokens for the model
        max_tokens = self.token_service.get_max_context_tokens(model)

        # Reserve tokens for response
        max_context_tokens = max(max_tokens - 1000, max_tokens // 2)

        # Optimize context
        optimized = self.optimize_context_for_task(context, task, max_context_tokens)

        # Convert back to message format
        messages = []

        # Add task focus as system message if not already present
        task_in_context = any(
            e.element_type == ElementType.SYSTEM and task.lower() in e.content.lower()
            for e in optimized.elements
        )

        if not task_in_context:
            messages.append({
                "role": "system",
                "content": f"Current Task: {task}\n\nFocus on completing this specific task."
            })

        # Add other elements
        for element in optimized.elements:
            # Skip if already added task focus
            if element.element_type == ElementType.SYSTEM and task.lower() in element.content.lower() and task_in_context:
                continue

            # Convert to message format
            message = {
                "role": element.metadata.get("role", "user"),
                "content": element.content
            }

            messages.append(message)

        # Log optimization metrics
        logger.debug(f"Context optimization metrics: {optimized.optimization_metrics}")
        logger.debug(f"Optimized context: {len(messages)} messages, {optimized.total_tokens} tokens")

        return messages
