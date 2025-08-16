"""@Time    : 2025-07-22 17:00:00
@Author  : DAIP-LIVE Team
@File    : enhanced_llm_interface.py
@Description:
    Enhanced LLM Interface with integrated task-focused context optimization
    at the lowest level. This ensures all LLM interactions automatically
    benefit from optimal context preparation without requiring higher-level
    components to manage this complexity.
"""
import logging
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List, Optional, Tuple
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel

from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.memory_agent import MemAgent
from src.core_services.task_context_optimizer import TaskContextOptimizer
from src.core_services.token_management_service import TokenManagementService
from src.kernel.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class OptimizationMetadata(BaseModel):
    """Metadata about context optimization applied to an LLM call."""

    original_context_tokens: int
    optimized_context_tokens: int
    compression_ratio: float
    included_memories: list[str]
    excluded_memories: list[str]
    task_focus: str
    optimization_strategy: str
    processing_time_ms: float


class EnhancedLLMResponse(BaseModel):
    """Enhanced LLM response with optimization metadata."""

    content: str
    model: str
    token_usage: Optional[dict[str, int]] = None
    optimization_metadata: Optional[OptimizationMetadata] = None
    raw_response: Optional[dict[str, Any]] = None


class EnhancedLLMInterface:
    """Enhanced LLM Interface with integrated task-focused context optimization.
    
    This class wraps the standard LLMInterface and automatically applies
    task-focused context optimization to all LLM interactions at the lowest level.
    """

    def __init__(
        self,
        base_llm_interface: LLMInterface,
        sskg_manager: EnhancedSSKGManager,
        mem_agent: MemAgent,
        token_service: TokenManagementService,
        enable_optimization: bool = True
    ):
        """Initialize the Enhanced LLM Interface.
        
        Args:
            base_llm_interface: The base LLM interface to wrap
            sskg_manager: Enhanced SSKG manager for knowledge retrieval
            mem_agent: Memory agent for intelligent memory selection
            token_service: Token management service for counting and limits
            enable_optimization: Whether to enable context optimization

        """
        self.base_llm = base_llm_interface
        self.sskg_manager = sskg_manager
        self.mem_agent = mem_agent
        self.token_service = token_service
        self.enable_optimization = enable_optimization

        # Initialize task context optimizer
        self.task_optimizer = TaskContextOptimizer(
            token_service=token_service,
            sskg_manager=sskg_manager,
            mem_agent=mem_agent
        )

        logger.info("EnhancedLLMInterface initialized with context optimization")

    async def generate(
        self,
        messages: list[dict[str, Any]],
        model: str = "gpt-3.5-turbo",
        participant_id: Optional[str] = None,
        task_context: Optional[str] = None,
        **kwargs
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Generate a response using the LLM with automatic context optimization.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            participant_id: Optional participant identifier
            task_context: Optional explicit task context
            **kwargs: Additional arguments for the LLM
            
        Returns:
            Enhanced response with optimization metadata

        """
        start_time = datetime.now()

        try:
            # Apply context optimization if enabled
            if self.enable_optimization:
                optimized_messages, optimization_metadata = await self._optimize_context(
                    messages, model, participant_id, task_context
                )
            else:
                optimized_messages = messages
                optimization_metadata = None

            # Call the base LLM interface
            response = await self.base_llm.generate(
                optimized_messages,
                model=model,
                participant_id=participant_id,
                **kwargs
            )

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            # Update optimization metadata with processing time
            if optimization_metadata:
                optimization_metadata.processing_time_ms = processing_time

            # Return enhanced response
            return {
                "content": response.get("content", ""),
                "model": model,
                "token_usage": response.get("token_usage"),
                "optimization_metadata": optimization_metadata.dict() if optimization_metadata else None,
                "raw_response": response
            }

        except Exception as e:
            logger.error(f"Error in enhanced LLM generation: {e}")
            # Fall back to base LLM interface
            return await self.base_llm.generate(messages, model=model, participant_id=participant_id, **kwargs)

    async def _optimize_context(
        self,
        messages: list[dict[str, Any]],
        model: str,
        participant_id: Optional[str] = None,
        task_context: Optional[str] = None
<<<<<<< HEAD
    ) -> Tuple[List[Dict[str, Any]], OptimizationMetadata]:
=======
    ) -> tuple[list[dict[str, Any]], OptimizationMetadata]:
>>>>>>> feature/core-services-refactor
        """Apply task-focused context optimization to messages.
        
        Args:
            messages: Original messages
            model: Model name for token counting
            participant_id: Optional participant identifier
            task_context: Optional explicit task context
            
        Returns:
            Tuple of (optimized_messages, optimization_metadata)

        """
        # Calculate original token count
        original_tokens = self.token_service.count_messages_tokens(messages, model)

        # Detect task context if not provided
        if not task_context:
            task_context = self._detect_task_context(messages)

        # Get max tokens for the model
        max_tokens = self.token_service.get_max_context_tokens(model)

        # Reserve tokens for response (typically 25% of max tokens)
        max_context_tokens = max(max_tokens - (max_tokens // 4), max_tokens // 2)

        # Apply task-focused optimization
        optimized_messages = self.task_optimizer.prepare_context_for_llm(
            messages, task_context, model
        )

        # Calculate optimized token count
        optimized_tokens = self.token_service.count_messages_tokens(optimized_messages, model)

        # Get memory information from the optimization process
        included_memories, excluded_memories = await self._get_memory_info(
            task_context, participant_id
        )

        # Create optimization metadata
        metadata = OptimizationMetadata(
            original_context_tokens=original_tokens,
            optimized_context_tokens=optimized_tokens,
            compression_ratio=optimized_tokens / original_tokens if original_tokens > 0 else 1.0,
            included_memories=included_memories,
            excluded_memories=excluded_memories,
            task_focus=task_context,
            optimization_strategy=self._determine_optimization_strategy(
                original_tokens, optimized_tokens, max_context_tokens
            ),
            processing_time_ms=0.0  # Will be set later
        )

        return optimized_messages, metadata
<<<<<<< HEAD

    def _detect_task_context(self, messages: List[Dict[str, Any]]) -> str:
=======
    
    def _detect_task_context(self, messages: list[dict[str, Any]]) -> str:
>>>>>>> feature/core-services-refactor
        """Automatically detect task context from messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Detected task context

        """
        # Look for explicit task indicators
        task_indicators = [
            "task:", "instruction:", "please", "implement", "create", "write",
            "analyze", "explain", "describe", "help me", "i need", "can you"
        ]

        # Check recent messages for task context
        recent_messages = messages[-3:] if len(messages) > 3 else messages

        for message in reversed(recent_messages):
            content = message.get("content", "").lower()

            # Look for explicit task statements
            for indicator in task_indicators:
                if indicator in content:
                    # Extract the sentence containing the task
                    sentences = content.split('.')
                    for sentence in sentences:
                        if indicator in sentence:
                            return sentence.strip()

            # If it's a user message, it's likely a task
            if message.get("role") == "user":
                return content[:200]  # First 200 characters as task context

        # Default task context
        return "general assistance and conversation"

    async def _get_memory_info(
        self,
        task_context: str,
        participant_id: Optional[str] = None
<<<<<<< HEAD
    ) -> Tuple[List[str], List[str]]:
=======
    ) -> tuple[list[str], list[str]]:
>>>>>>> feature/core-services-refactor
        """Get information about memories included and excluded in optimization.
        
        Args:
            task_context: The task context
            participant_id: Optional participant identifier
            
        Returns:
            Tuple of (included_memory_ids, excluded_memory_ids)

        """
        try:
            # Get relevant memories from MemAgent
            memories = self.mem_agent.retrieve_memories(task_context, limit=10)

            # For this implementation, we'll assume the top 5 are included
            # and the rest are excluded (in a real implementation, this would
            # be determined by the actual optimization process)
            included = [m.id for m in memories[:5] if m.id]
            excluded = [m.id for m in memories[5:] if m.id]

            return included, excluded

        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return [], []

    def _determine_optimization_strategy(
        self,
        original_tokens: int,
        optimized_tokens: int,
        max_tokens: int
    ) -> str:
        """Determine the optimization strategy used.
        
        Args:
            original_tokens: Original token count
            optimized_tokens: Optimized token count
            max_tokens: Maximum allowed tokens
            
        Returns:
            Strategy description

        """
        compression_ratio = optimized_tokens / original_tokens if original_tokens > 0 else 1.0

        if original_tokens <= max_tokens and compression_ratio > 0.95:
            return "no_compression_needed"
        elif compression_ratio > 0.8:
            return "light_task_focused_filtering"
        elif compression_ratio > 0.6:
            return "moderate_task_focused_compression"
        elif compression_ratio > 0.4:
            return "aggressive_task_focused_compression"
        else:
            return "maximum_task_focused_compression"

    # Delegate other methods to base LLM interface

    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text."""
        return self.base_llm.count_tokens(text, model)

    def get_max_tokens(self, model: str = "gpt-3.5-turbo") -> int:
        """Get maximum tokens for model."""
        return self.base_llm.get_max_tokens(model)

    async def generate_streaming(
        self,
        messages: list[dict[str, Any]],
        model: str = "gpt-3.5-turbo",
        participant_id: Optional[str] = None,
        task_context: Optional[str] = None,
        **kwargs
    ):
        """Generate streaming response with context optimization.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            participant_id: Optional participant identifier
            task_context: Optional explicit task context
            **kwargs: Additional arguments for the LLM
            
        Yields:
            Streaming response chunks

        """
        try:
            # Apply context optimization if enabled
            if self.enable_optimization:
                optimized_messages, _ = await self._optimize_context(
                    messages, model, participant_id, task_context
                )
            else:
                optimized_messages = messages

            # Stream from base LLM interface
            async for chunk in self.base_llm.generate_streaming(
                optimized_messages,
                model=model,
                participant_id=participant_id,
                **kwargs
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error in enhanced streaming generation: {e}")
            # Fall back to base LLM interface
            async for chunk in self.base_llm.generate_streaming(
                messages, model=model, participant_id=participant_id, **kwargs
            ):
                yield chunk
<<<<<<< HEAD

    def get_optimization_stats(self) -> Dict[str, Any]:
=======
    
    def get_optimization_stats(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get statistics about context optimization performance.
        
        Returns:
            Dictionary with optimization statistics

        """
        # In a real implementation, this would track statistics over time
        return {
            "optimization_enabled": self.enable_optimization,
            "total_optimizations": 0,  # Would be tracked
            "average_compression_ratio": 0.0,  # Would be calculated
            "average_processing_time_ms": 0.0,  # Would be tracked
            "optimization_strategies_used": {},  # Would be tracked
            "memory_retrieval_stats": {}  # Would be tracked from MemAgent
        }

    def enable_context_optimization(self):
        """Enable context optimization."""
        self.enable_optimization = True
        logger.info("Context optimization enabled")

    def disable_context_optimization(self):
        """Disable context optimization."""
        self.enable_optimization = False
        logger.info("Context optimization disabled")

    def is_optimization_enabled(self) -> bool:
        """Check if context optimization is enabled."""
        return self.enable_optimization
