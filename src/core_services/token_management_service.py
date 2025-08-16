"""Token Management Service for DAIP-LIVE

This service provides universal token management capabilities including:
- Precise token counting using tiktoken
- Cost estimation and budget tracking
- Context window management and smart truncation
- Token usage analytics and reporting

This service is designed to be used by all AI participants (roles and users)
to optimize token usage and manage context windows effectively.
"""

import logging
from datetime import datetime
from typing import Any, Optional

import tiktoken
from pydantic import BaseModel

from src.config import TokenManagementConfig

logger = logging.getLogger(__name__)


class TokenUsage(BaseModel):
    """Model for tracking token usage statistics."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    timestamp: datetime
    model: str
    participant_id: Optional[str] = None


class ContextWindow(BaseModel):
    """Model for managing context window state."""
<<<<<<< HEAD

    messages: List[Dict[str, Any]]
=======
    messages: list[dict[str, Any]]
>>>>>>> feature/core-services-refactor
    total_tokens: int
    max_tokens: int
    compression_applied: bool = False
    truncation_applied: bool = False
    preserved_messages: int = 0  # Number of messages preserved during optimization


class TokenManagementService:
    """Universal Token Management Service for all AI participants.
    
    Provides token counting, cost estimation, and context optimization
    for efficient LLM usage across all roles and users.
    """

    def __init__(self, config: TokenManagementConfig):
        """Initialize the token management service."""
        self.config = config
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-3.5/4 encoding
<<<<<<< HEAD
        self.usage_history: List[TokenUsage] = []

=======
        self.usage_history: list[TokenUsage] = []
        
>>>>>>> feature/core-services-refactor
        # Model-specific token limits (can be extended)
        self.model_limits = {
            "gpt-3.5-turbo": 4096,
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "llama3:instruct": 4096,
            "llama3:8b": 4096,
            "llama3:70b": 4096,
        }

        # Model-specific cost rates (tokens per dollar)
        self.cost_rates = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            # Ollama models are typically free
            "llama3:instruct": {"input": 0.0, "output": 0.0},
            "llama3:8b": {"input": 0.0, "output": 0.0},
            "llama3:70b": {"input": 0.0, "output": 0.0},
        }

        logger.info("TokenManagementService initialized")

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens in text using appropriate tokenizer.
        
        Args:
            text: The text to count tokens for
            model: Optional model name for model-specific counting
            
        Returns:
            Number of tokens in the text

        """
        try:
            if not text:
                return 0
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: rough estimation (4 chars per token)
            return len(text) // 4
<<<<<<< HEAD

    def count_messages_tokens(self, messages: List[Dict[str, Any]], model: Optional[str] = None) -> int:
=======
    
    def count_messages_tokens(self, messages: list[dict[str, Any]], model: Optional[str] = None) -> int:
>>>>>>> feature/core-services-refactor
        """Count total tokens in a list of messages.
        
        Args:
            messages: List of message dictionaries
            model: Optional model name for model-specific counting
            
        Returns:
            Total number of tokens in all messages

        """
        total_tokens = 0

        for message in messages:
            # Count tokens for role and content
            if "role" in message:
                total_tokens += self.count_tokens(message["role"], model)
            if "content" in message:
                total_tokens += self.count_tokens(str(message["content"]), model)

            # Add overhead tokens for message formatting (typically 3-4 tokens per message)
            total_tokens += 4

        # Add overhead for conversation formatting
        total_tokens += 3

        return total_tokens

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate estimated cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name for cost calculation
            
        Returns:
            Estimated cost in dollars

        """
        if not self.config.enable_cost_tracking:
            return 0.0

        rates = self.cost_rates.get(model, {"input": 0.0, "output": 0.0})

        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]

        return input_cost + output_cost

    def get_context_limit(self, model: str) -> int:
        """Get the context token limit for a specific model.
        
        Args:
            model: Model name
            
        Returns:
            Maximum context tokens for the model

        """
        return self.model_limits.get(model, self.config.max_context_tokens)
<<<<<<< HEAD

    def check_context_limit(self, messages: List[Dict[str, Any]], model: str) -> Tuple[bool, int, int]:
=======
    
    def check_context_limit(self, messages: list[dict[str, Any]], model: str) -> tuple[bool, int, int]:
>>>>>>> feature/core-services-refactor
        """Check if messages fit within model's context window.
        
        Args:
            messages: List of message dictionaries
            model: Model name
            
        Returns:
            Tuple of (fits_in_context, current_tokens, max_tokens)

        """
        current_tokens = self.count_messages_tokens(messages, model)
        max_tokens = self.get_context_limit(model)

        return current_tokens <= max_tokens, current_tokens, max_tokens
<<<<<<< HEAD

    def optimize_context_window(self, messages: List[Dict[str, Any]], model: str,
=======
    
    def optimize_context_window(self, messages: list[dict[str, Any]], model: str, 
>>>>>>> feature/core-services-refactor
                              target_tokens: Optional[int] = None) -> ContextWindow:
        """Smart truncation while preserving important context.
        
        This method implements intelligent context optimization by:
        1. Preserving system messages and recent messages
        2. Compressing middle conversation history
        3. Maintaining conversation coherence
        
        Args:
            messages: List of message dictionaries
            model: Model name for token limits
            target_tokens: Optional target token count (defaults to model limit * compression_threshold)
            
        Returns:
            ContextWindow object with optimized messages

        """
        max_tokens = self.get_context_limit(model)
        if target_tokens is None:
            target_tokens = int(max_tokens * self.config.compression_threshold)

        current_tokens = self.count_messages_tokens(messages, model)

        # If already within limits, return as-is
        if current_tokens <= target_tokens:
            return ContextWindow(
                messages=messages,
                total_tokens=current_tokens,
                max_tokens=max_tokens,
                preserved_messages=len(messages)
            )

        # Separate system messages, recent messages, and middle messages
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        non_system_messages = [msg for msg in messages if msg.get("role") != "system"]

        # Always preserve system messages and last few messages
        preserve_recent = min(3, len(non_system_messages))
        recent_messages = non_system_messages[-preserve_recent:] if preserve_recent > 0 else []
        middle_messages = non_system_messages[:-preserve_recent] if preserve_recent > 0 else non_system_messages

        # Calculate tokens for preserved messages
        preserved_tokens = (
            self.count_messages_tokens(system_messages, model) +
            self.count_messages_tokens(recent_messages, model)
        )

        # Determine how many middle messages we can keep
        remaining_tokens = target_tokens - preserved_tokens
        selected_middle = []

        if remaining_tokens > 0 and middle_messages:
            # Select middle messages starting from most recent
            for msg in reversed(middle_messages):
                msg_tokens = self.count_messages_tokens([msg], model)
                if remaining_tokens >= msg_tokens:
                    selected_middle.insert(0, msg)  # Insert at beginning to maintain order
                    remaining_tokens -= msg_tokens
                else:
                    break

        # Combine optimized messages
        optimized_messages = system_messages + selected_middle + recent_messages
        final_tokens = self.count_messages_tokens(optimized_messages, model)

        return ContextWindow(
            messages=optimized_messages,
            total_tokens=final_tokens,
            max_tokens=max_tokens,
            compression_applied=len(optimized_messages) < len(messages),
            truncation_applied=len(selected_middle) < len(middle_messages),
            preserved_messages=len(optimized_messages)
        )

    def record_usage(self, input_tokens: int, output_tokens: int, model: str,
                    participant_id: Optional[str] = None) -> TokenUsage:
        """Record token usage for analytics and tracking.
        
        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            model: Model name used
            participant_id: Optional identifier for the participant (user_id or role_id)
            
        Returns:
            TokenUsage object with recorded information

        """
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost=self.estimate_cost(input_tokens, output_tokens, model),
            timestamp=datetime.now(),
            model=model,
            participant_id=participant_id
        )

        self.usage_history.append(usage)

        # Keep only recent usage history (last 1000 entries)
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]

        logger.debug(f"Recorded token usage: {usage.total_tokens} tokens, ${usage.estimated_cost:.4f}")

        return usage
<<<<<<< HEAD

    def get_usage_stats(self, participant_id: Optional[str] = None,
                       hours: Optional[int] = None) -> Dict[str, Any]:
=======
    
    def get_usage_stats(self, participant_id: Optional[str] = None, 
                       hours: Optional[int] = None) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get token usage statistics.
        
        Args:
            participant_id: Optional filter by participant
            hours: Optional filter by last N hours
            
        Returns:
            Dictionary with usage statistics

        """
        filtered_usage = self.usage_history

        # Filter by participant if specified
        if participant_id:
            filtered_usage = [u for u in filtered_usage if u.participant_id == participant_id]

        # Filter by time if specified
        if hours:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            filtered_usage = [u for u in filtered_usage if u.timestamp.timestamp() >= cutoff_time]

        if not filtered_usage:
            return {
                "total_tokens": 0,
                "total_cost": 0.0,
                "request_count": 0,
                "average_tokens_per_request": 0,
                "models_used": []
            }

        total_tokens = sum(u.total_tokens for u in filtered_usage)
        total_cost = sum(u.estimated_cost for u in filtered_usage)
        models_used = list(set(u.model for u in filtered_usage))

        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "request_count": len(filtered_usage),
            "average_tokens_per_request": total_tokens / len(filtered_usage),
            "models_used": models_used,
            "input_tokens": sum(u.input_tokens for u in filtered_usage),
            "output_tokens": sum(u.output_tokens for u in filtered_usage)
        }
<<<<<<< HEAD

    def prepare_context_for_llm(self, messages: List[Dict[str, Any]], model: str,
=======
    
    def prepare_context_for_llm(self, messages: list[dict[str, Any]], model: str, 
>>>>>>> feature/core-services-refactor
                               participant_id: Optional[str] = None) -> ContextWindow:
        """Prepare optimized context for LLM call.
        
        This is the main method that should be called before making LLM requests.
        It handles context optimization and prepares the messages for efficient processing.
        
        Args:
            messages: Original list of messages
            model: Model name for optimization
            participant_id: Optional participant identifier
            
        Returns:
            ContextWindow with optimized messages ready for LLM

        """
        if not self.config.enable_context_optimization:
            # If optimization is disabled, just return current state
            current_tokens = self.count_messages_tokens(messages, model)
            max_tokens = self.get_context_limit(model)

            return ContextWindow(
                messages=messages,
                total_tokens=current_tokens,
                max_tokens=max_tokens,
                preserved_messages=len(messages)
            )

        # Optimize context window
        context_window = self.optimize_context_window(messages, model)

        logger.debug(f"Context prepared for {participant_id or 'unknown'}: "
                    f"{context_window.total_tokens}/{context_window.max_tokens} tokens, "
                    f"compression: {context_window.compression_applied}")

        return context_window
