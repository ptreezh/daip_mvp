"""Prompt Optimization Service for enhancing prompts based on user profile and intent.

This service provides functionality for enhancing prompts based on user profile and intent analysis,
adding relevant context and background information, optimizing for user's communication style and
expertise level, and personalizing based on user's goals and preferences. It serves as a key
component of the Human User Intelligence Layer.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.core_services.user_profile_service import UserProfile

logger = logging.getLogger(__name__)


class ContextOptimization(BaseModel):
    """Represents the result of optimizing a prompt with context.
    """
    original_prompt: str
    optimized_prompt: str
    added_context: list[str] = Field(default_factory=list)
    personalization_factors: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class PromptOptimizationServiceInterface(ABC):
    """Abstract interface for prompt optimization services.
    
    This interface defines the contract that all prompt optimization services must implement.
    It provides methods for optimizing prompts based on user profile and intent analysis,
    adding relevant context, and personalizing based on user's goals and preferences.
    """
    
    @abstractmethod
    async def optimize_prompt(
        self, 
        original_prompt: str, 
        user_id: str, 
        context: dict[str, Any]
    ) -> ContextOptimization:
        """Optimize prompt based on user profile and intent.
        
        Args:
            original_prompt: The original prompt to optimize
            user_id: The ID of the user
            context: Additional context for optimization
            
        Returns:
            ContextOptimization object with optimized prompt and metadata
        """
        pass
    
    @abstractmethod
    def add_personal_context(
        self, 
        prompt: str, 
        user_profile: UserProfile, 
        topic: str
    ) -> str:
        """Add relevant personal context to enhance understanding.
        
        Args:
            prompt: The prompt to enhance
            user_profile: The user's profile
            topic: The topic of the prompt
            
        Returns:
            Enhanced prompt with personal context
        """
        pass
    
    @abstractmethod
    def adapt_to_expertise_level(
        self, 
        prompt: str, 
        expertise_level: str, 
        topic: str
    ) -> str:
        """Adapt prompt to user's expertise level.
        
        Args:
            prompt: The prompt to adapt
            expertise_level: The user's expertise level (e.g., "beginner", "intermediate", "expert")
            topic: The topic of the prompt
            
        Returns:
            Adapted prompt for the user's expertise level
        """
        pass
    
    @abstractmethod
    def optimize_for_communication_style(
        self, 
        prompt: str, 
        communication_preferences: dict[str, Any]
    ) -> str:
        """Optimize prompt for user's communication style.
        
        Args:
            prompt: The prompt to optimize
            communication_preferences: The user's communication preferences
            
        Returns:
            Optimized prompt for the user's communication style
        """
        pass


class BasicPromptOptimizationService(PromptOptimizationServiceInterface):
    """Basic implementation of the PromptOptimizationService interface.
    
    This implementation provides simple prompt optimization functionality
    using the user profile and intent analysis. It serves as a placeholder
    that can be replaced with more sophisticated implementations in the future.
    """
    
    def __init__(self, intent_service, personal_context_service, llm_interface=None):
        """Initialize the BasicPromptOptimizationService.
        
        Args:
            intent_service: The IntentAnalysisService instance to use
            personal_context_service: The PersonalContextService instance to use
            llm_interface: Optional LLMInterface for more advanced optimization
        """
        self.intent_service = intent_service
        self.personal_context_service = personal_context_service
        self.llm_interface = llm_interface
        logger.info("BasicPromptOptimizationService initialized")
    
    async def optimize_prompt(
        self, 
        original_prompt: str, 
        user_id: str, 
        context: dict[str, Any]
    ) -> ContextOptimization:
        """Optimize prompt based on user profile and intent.
        
        Args:
            original_prompt: The original prompt to optimize
            user_id: The ID of the user
            context: Additional context for optimization
            
        Returns:
            ContextOptimization object with optimized prompt and metadata
        """
        try:
            # Get user profile
            user_profile = self.personal_context_service.get_user_profile(user_id)
            if not user_profile:
                return ContextOptimization(
                    original_prompt=original_prompt,
                    optimized_prompt=original_prompt
                )
            
            # Analyze intent if not provided in context
            intent_analysis = context.get("intent_analysis")
            if not intent_analysis:
                intent_analysis = await self.intent_service.analyze_intent(
                    original_prompt,
                    user_id,
                    context.get("conversation_history", [])
                )
            
            # Start with the original prompt
            optimized_prompt = original_prompt
            added_context = []
            personalization_factors = {}
            
            # Add personal context based on topic
            topic = context.get("topic", "")
            if not topic and intent_analysis:
                topic = intent_analysis.detected_intent
            
            if topic:
                with_context = self.add_personal_context(optimized_prompt, user_profile, topic)
                if with_context != optimized_prompt:
                    optimized_prompt = with_context
                    added_context.append(f"Added personal context for topic: {topic}")
                    personalization_factors["personal_context"] = True
            
            # Adapt to expertise level
            expertise_level = user_profile.preferences.get("expertise_level", "intermediate")
            with_expertise = self.adapt_to_expertise_level(optimized_prompt, expertise_level, topic)
            if with_expertise != optimized_prompt:
                optimized_prompt = with_expertise
                added_context.append(f"Adapted to expertise level: {expertise_level}")
                personalization_factors["expertise_adaptation"] = expertise_level
            
            # Optimize for communication style
            communication_preferences = user_profile.preferences.get("communication", {})
            if communication_preferences:
                with_style = self.optimize_for_communication_style(
                    optimized_prompt,
                    communication_preferences
                )
                if with_style != optimized_prompt:
                    optimized_prompt = with_style
                    added_context.append("Optimized for communication style")
                    personalization_factors["style_optimization"] = True
            
            # Use LLM for more advanced optimization if available
            if self.llm_interface and len(original_prompt) > 20:
                try:
                    # This is a placeholder for more sophisticated LLM-based optimization
                    # In a real implementation, this would use the LLM to optimize the prompt
                    pass
                except Exception as e:
                    logger.warning(f"Error using LLM for prompt optimization: {e}")
            
            return ContextOptimization(
                original_prompt=original_prompt,
                optimized_prompt=optimized_prompt,
                added_context=added_context,
                personalization_factors=personalization_factors
            )
        except Exception as e:
            logger.warning(f"Error optimizing prompt: {e}")
            return ContextOptimization(
                original_prompt=original_prompt,
                optimized_prompt=original_prompt
            )
    
    def add_personal_context(
        self, 
        prompt: str, 
        user_profile: UserProfile, 
        topic: str
    ) -> str:
        """Add relevant personal context to enhance understanding.
        
        Args:
            prompt: The prompt to enhance
            user_profile: The user's profile
            topic: The topic of the prompt
            
        Returns:
            Enhanced prompt with personal context
        """
        try:
            # Get relevant background knowledge
            relevant_background = self.personal_context_service.get_relevant_background(
                user_profile.user_id,
                topic
            )
            
            if not relevant_background:
                return prompt
            
            # Add context to prompt
            context_items = [item.get("content", "") for item in relevant_background[:2]]
            context_str = "\n".join(context_items)
            
            # Simple template for adding context
            enhanced_prompt = f"""Context: {context_str}

Based on the above context, please respond to: {prompt}"""
            
            return enhanced_prompt
        except Exception as e:
            logger.warning(f"Error adding personal context: {e}")
            return prompt
    
    def adapt_to_expertise_level(
        self, 
        prompt: str, 
        expertise_level: str, 
        topic: str
    ) -> str:
        """Adapt prompt to user's expertise level.
        
        Args:
            prompt: The prompt to adapt
            expertise_level: The user's expertise level (e.g., "beginner", "intermediate", "expert")
            topic: The topic of the prompt
            
        Returns:
            Adapted prompt for the user's expertise level
        """
        try:
            # Simple adaptation based on expertise level
            if expertise_level == "beginner":
                return f"{prompt}\n\nPlease provide a beginner-friendly explanation with simple terms and examples."
            elif expertise_level == "expert":
                return f"{prompt}\n\nPlease provide a detailed technical explanation assuming expert knowledge in {topic}."
            else:  # intermediate or default
                return prompt
        except Exception as e:
            logger.warning(f"Error adapting to expertise level: {e}")
            return prompt
    
    def optimize_for_communication_style(
        self, 
        prompt: str, 
        communication_preferences: dict[str, Any]
    ) -> str:
        """Optimize prompt for user's communication style.
        
        Args:
            prompt: The prompt to optimize
            communication_preferences: The user's communication preferences
            
        Returns:
            Optimized prompt for the user's communication style
        """
        try:
            # Extract communication preferences
            verbosity = communication_preferences.get("verbosity", "normal")
            formality = communication_preferences.get("formality", "neutral")
            
            # Apply style optimizations
            optimized = prompt
            
            # Adjust for verbosity
            if verbosity == "concise":
                optimized += "\n\nPlease provide a concise response."
            elif verbosity == "detailed":
                optimized += "\n\nPlease provide a detailed response with thorough explanations."
            
            # Adjust for formality
            if formality == "formal":
                optimized += "\n\nPlease use formal language in your response."
            elif formality == "casual":
                optimized += "\n\nPlease use casual, conversational language in your response."
            
            return optimized
        except Exception as e:
            logger.warning(f"Error optimizing for communication style: {e}")
            return prompt