# -*- coding: utf-8 -*-
"""
Universal Context Optimization Service for DAIP-LIVE

This service provides universal context optimization capabilities including:
- Intelligent message compression for all participants
- Important information preservation during context truncation
- Context window sliding and management
- Memory consolidation across conversations

This service works in conjunction with the TokenManagementService to provide
comprehensive context optimization for all AI participants.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from src.core_services.token_management_service import TokenManagementService, ContextWindow
from src.core_services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class ConversationState(BaseModel):
    """Model for tracking conversation state across participants."""
    participant_id: str  # Can be user_id or role_id
    conversation_history: List[Dict[str, Any]]
    context_window: ContextWindow
    last_updated: datetime
    session_id: Optional[str] = None
    project_id: Optional[str] = None


class ImportantInformation(BaseModel):
    """Model for tracking important information extracted from conversations."""
    content: str
    importance_score: float
    source_message_index: int
    participant_id: str
    timestamp: datetime
    tags: List[str] = []


class UniversalContextService:
    """
    Universal Context Optimization Service for all AI participants.
    
    Provides intelligent context management, message compression, and
    memory consolidation to optimize LLM interactions across all roles and users.
    """
    
    def __init__(self, token_service: TokenManagementService, memory_service: MemoryService):
        """Initialize the universal context service."""
        self.token_service = token_service
        self.memory_service = memory_service
        self.conversation_states: Dict[str, ConversationState] = {}
        
        # Configuration for context optimization
        self.importance_threshold = 0.5  # Minimum importance score to preserve information
        self.max_conversation_history = 50  # Maximum messages to keep in memory
        self.compression_keywords = [
            "important", "critical", "key", "main", "primary", "essential",
            "conclusion", "decision", "result", "outcome", "summary"
        ]
        
        logger.info("UniversalContextService initialized")
    
    def _calculate_importance_score(self, message: Dict[str, Any], context: List[Dict[str, Any]]) -> float:
        """
        Calculate importance score for a message based on content and context.
        
        Args:
            message: The message to score
            context: Surrounding conversation context
            
        Returns:
            Importance score between 0.0 and 1.0
        """
        content = str(message.get("content", "")).lower()
        role = message.get("role", "")
        
        # Base score
        score = 0.3
        
        # System messages are always important
        if role == "system":
            score = 0.9
        
        # Check for importance keywords
        keyword_count = sum(1 for keyword in self.compression_keywords if keyword in content)
        score += min(keyword_count * 0.1, 0.3)
        
        # Longer messages might be more important
        if len(content) > 100:
            score += 0.1
        
        # Questions are often important
        if "?" in content:
            score += 0.1
        
        # Messages with specific formatting (lists, numbers) might be important
        if any(marker in content for marker in ["1.", "2.", "•", "-", "*"]):
            score += 0.1
        
        # Recent messages get slight boost
        if context and len(context) > 0:
            position_from_end = len(context) - context.index(message) if message in context else len(context)
            if position_from_end <= 3:  # Last 3 messages
                score += 0.1
        
        return min(score, 1.0)
    
    def compress_conversation(self, messages: List[Dict[str, Any]], target_tokens: int, 
                            model: str, participant_id: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[ImportantInformation]]:
        """
        Compress conversation while preserving key information.
        
        Args:
            messages: List of conversation messages
            target_tokens: Target token count after compression
            model: Model name for token counting
            participant_id: Optional participant identifier
            
        Returns:
            Tuple of (compressed_messages, extracted_important_info)
        """
        if not messages:
            return [], []
        
        # Calculate importance scores for all messages
        message_scores = []
        for i, message in enumerate(messages):
            score = self._calculate_importance_score(message, messages)
            message_scores.append((i, message, score))
        
        # Sort by importance (descending)
        message_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Always preserve system messages and recent messages
        system_messages = [(i, msg, score) for i, msg, score in message_scores if msg.get("role") == "system"]
        recent_messages = message_scores[-3:] if len(message_scores) > 3 else message_scores  # Last 3 messages
        
        # Start with system and recent messages
        preserved_indices = set()
        compressed_messages = []
        
        # Add system messages first
        for i, msg, score in system_messages:
            if i not in preserved_indices:
                compressed_messages.append((i, msg))
                preserved_indices.add(i)
        
        # Calculate tokens used by system messages
        system_msgs = [msg for _, msg in compressed_messages]
        current_tokens = self.token_service.count_messages_tokens(system_msgs, model)
        
        # Add recent messages
        for i, msg, score in recent_messages:
            if i not in preserved_indices:
                msg_tokens = self.token_service.count_messages_tokens([msg], model)
                if current_tokens + msg_tokens <= target_tokens:
                    compressed_messages.append((i, msg))
                    preserved_indices.add(i)
                    current_tokens += msg_tokens
        
        # Add other important messages if space allows
        for i, msg, score in message_scores:
            if i not in preserved_indices and score >= self.importance_threshold:
                msg_tokens = self.token_service.count_messages_tokens([msg], model)
                if current_tokens + msg_tokens <= target_tokens:
                    compressed_messages.append((i, msg))
                    preserved_indices.add(i)
                    current_tokens += msg_tokens
                else:
                    break  # No more space
        
        # Sort compressed messages by original order
        compressed_messages.sort(key=lambda x: x[0])
        final_messages = [msg for _, msg in compressed_messages]
        
        # Extract important information from removed messages
        important_info = []
        for i, msg, score in message_scores:
            if i not in preserved_indices and score >= self.importance_threshold:
                info = ImportantInformation(
                    content=str(msg.get("content", "")),
                    importance_score=score,
                    source_message_index=i,
                    participant_id=participant_id or "unknown",
                    timestamp=datetime.now(),
                    tags=["compressed", "important"]
                )
                important_info.append(info)
        
        logger.debug(f"Compressed {len(messages)} messages to {len(final_messages)} messages, "
                    f"extracted {len(important_info)} important items")
        
        return final_messages, important_info
    
    def consolidate_memory(self, participant_id: str, conversation: List[Dict[str, Any]], 
                          session_id: Optional[str] = None, project_id: Optional[str] = None) -> None:
        """
        Extract and store important information from conversation in memory.
        
        Args:
            participant_id: Identifier for the participant
            conversation: List of conversation messages
            session_id: Optional session identifier
            project_id: Optional project identifier
        """
        if not conversation:
            return
        
        # Extract important information
        important_items = []
        for i, message in enumerate(conversation):
            score = self._calculate_importance_score(message, conversation)
            if score >= self.importance_threshold:
                important_items.append((message, score))
        
        # Store important information in memory
        for message, score in important_items:
            content = str(message.get("content", ""))
            role = message.get("role", "")
            
            # Create memory entry
            memory_content = f"[{role}] {content}"
            
            # Determine memory type based on content
            memory_type = "dialogue"
            if role == "system":
                memory_type = "identity"
            elif any(keyword in content.lower() for keyword in ["decision", "conclusion", "result"]):
                memory_type = "knowledge"
            
            # Store in memory service
            self.memory_service.add_memory(
                role_id=participant_id,
                content=memory_content,
                memory_type=memory_type,
                importance=score,
                project_id=project_id,
                session_id=session_id,
                tags=["conversation", "consolidated"],
                metadata={
                    "original_role": role,
                    "consolidation_timestamp": datetime.now().isoformat(),
                    "importance_score": score
                }
            )
        
        logger.info(f"Consolidated {len(important_items)} important items to memory for {participant_id}")
    
    def prepare_context(self, participant_id: str, new_message: str, model: str,
                       conversation_history: Optional[List[Dict[str, Any]]] = None,
                       session_id: Optional[str] = None, project_id: Optional[str] = None) -> ContextWindow:
        """
        Prepare optimized context for LLM call with memory integration.
        
        Args:
            participant_id: Identifier for the participant
            new_message: New message to add to context
            model: Model name for optimization
            conversation_history: Optional conversation history
            session_id: Optional session identifier
            project_id: Optional project identifier
            
        Returns:
            ContextWindow with optimized messages ready for LLM
        """
        # Get or create conversation state
        if participant_id not in self.conversation_states:
            self.conversation_states[participant_id] = ConversationState(
                participant_id=participant_id,
                conversation_history=conversation_history or [],
                context_window=ContextWindow(messages=[], total_tokens=0, max_tokens=4096),
                last_updated=datetime.now(),
                session_id=session_id,
                project_id=project_id
            )
        
        state = self.conversation_states[participant_id]
        
        # Add new message to history
        if new_message:
            state.conversation_history.append({
                "role": "user",
                "content": new_message,
                "timestamp": datetime.now().isoformat()
            })
        
        # Retrieve relevant memories to enhance context
        relevant_memories = self.memory_service.retrieve_memories(
            role_id=participant_id,
            memory_types=["identity", "knowledge", "dialogue"],
            project_id=project_id,
            session_id=session_id,
            limit=5,
            min_importance=0.6
        )
        
        # Create enhanced context with memories
        enhanced_messages = []
        
        # Add system message with relevant memories
        if relevant_memories:
            memory_context = "\n".join([
                f"- {memory.content}" for memory in relevant_memories[:3]  # Top 3 memories
            ])
            system_message = {
                "role": "system",
                "content": f"Relevant context from previous conversations:\n{memory_context}\n\n"
                          f"You are assisting {participant_id}. Use this context to provide more personalized responses."
            }
            enhanced_messages.append(system_message)
        
        # Add conversation history
        enhanced_messages.extend(state.conversation_history)
        
        # Optimize context using token management
        context_window = self.token_service.prepare_context_for_llm(
            enhanced_messages, model, participant_id
        )
        
        # Update conversation state
        state.context_window = context_window
        state.last_updated = datetime.now()
        
        # Consolidate memory if conversation is getting long
        if len(state.conversation_history) > self.max_conversation_history:
            # Consolidate older messages to memory
            old_messages = state.conversation_history[:-self.max_conversation_history//2]
            self.consolidate_memory(participant_id, old_messages, session_id, project_id)
            
            # Keep only recent messages in active history
            state.conversation_history = state.conversation_history[-self.max_conversation_history//2:]
        
        logger.debug(f"Prepared context for {participant_id}: {context_window.total_tokens} tokens, "
                    f"compression: {context_window.compression_applied}")
        
        return context_window
    
    def get_conversation_summary(self, participant_id: str, model: str) -> Optional[str]:
        """
        Get a summary of the conversation for a participant.
        
        Args:
            participant_id: Identifier for the participant
            model: Model name for token counting
            
        Returns:
            Summary string or None if no conversation exists
        """
        if participant_id not in self.conversation_states:
            return None
        
        state = self.conversation_states[participant_id]
        if not state.conversation_history:
            return None
        
        # Create summary of key points
        important_messages = []
        for message in state.conversation_history:
            score = self._calculate_importance_score(message, state.conversation_history)
            if score >= self.importance_threshold:
                important_messages.append(message)
        
        if not important_messages:
            return "No significant conversation points to summarize."
        
        # Format summary
        summary_parts = []
        for msg in important_messages[-5:]:  # Last 5 important messages
            role = msg.get("role", "")
            content = str(msg.get("content", ""))[:100]  # Truncate long messages
            summary_parts.append(f"[{role}] {content}...")
        
        return "Key conversation points:\n" + "\n".join(summary_parts)
    
    def clear_conversation_state(self, participant_id: str) -> None:
        """
        Clear conversation state for a participant.
        
        Args:
            participant_id: Identifier for the participant
        """
        if participant_id in self.conversation_states:
            # Consolidate final conversation to memory before clearing
            state = self.conversation_states[participant_id]
            if state.conversation_history:
                self.consolidate_memory(
                    participant_id, 
                    state.conversation_history,
                    state.session_id,
                    state.project_id
                )
            
            del self.conversation_states[participant_id]
            logger.info(f"Cleared conversation state for {participant_id}")
    
    def get_context_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about context optimization across all participants.
        
        Returns:
            Dictionary with context optimization statistics
        """
        total_conversations = len(self.conversation_states)
        total_messages = sum(len(state.conversation_history) for state in self.conversation_states.values())
        
        compressed_conversations = sum(
            1 for state in self.conversation_states.values() 
            if state.context_window.compression_applied
        )
        
        avg_context_tokens = (
            sum(state.context_window.total_tokens for state in self.conversation_states.values()) 
            / total_conversations if total_conversations > 0 else 0
        )
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "compressed_conversations": compressed_conversations,
            "compression_rate": compressed_conversations / total_conversations if total_conversations > 0 else 0,
            "average_context_tokens": avg_context_tokens,
            "active_participants": list(self.conversation_states.keys())
        }