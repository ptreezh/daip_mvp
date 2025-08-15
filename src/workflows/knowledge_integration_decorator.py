"""@Time    : 2025-07-24 23:00:00
@Author  : DAIP-LIVE Team
@File    : knowledge_integration_decorator.py
@Description:
    Decorator for automatically integrating knowledge persistence into workflows.
"""
import functools
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.wiki_service import WikiService
from ..core_services.workflow_knowledge_integrator import WorkflowIntegrationConfig, WorkflowKnowledgeIntegrator

logger = logging.getLogger(__name__)


class KnowledgeIntegrationDecorator:
    """Decorator class for integrating knowledge persistence into workflows.
    
    This decorator automatically enhances workflow execution results with
    knowledge persistence capabilities, implementing requirements 6.1 and 6.2.
    """
    
    def __init__(
        self,
        sskg_manager: EnhancedSSKGManager,
        wiki_service: WikiService,
        config: WorkflowIntegrationConfig = None
    ):
        """Initialize the knowledge integration decorator.
        
        Args:
            sskg_manager: Enhanced SSKG manager for knowledge storage
            wiki_service: Wiki service for structured documentation
            config: Configuration for integration behavior
        """
        self.integrator = WorkflowKnowledgeIntegrator(
            sskg_manager=sskg_manager,
            wiki_service=wiki_service,
            config=config
        )
    
    def integrate_critical_review(
        self,
        auto_persist: bool = True,
        create_wiki: bool = True,
        min_confidence: float = 0.5
    ):
        """Decorator for Critical Review workflows.
        
        Args:
            auto_persist: Whether to automatically persist validated facts
            create_wiki: Whether to create wiki pages for results
            min_confidence: Minimum confidence threshold for persistence
        """
        def decorator(func: Callable[..., Awaitable[dict[str, Any]]]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Execute original workflow
                result = await func(*args, **kwargs)
                
                # Extract execution ID from result or generate one
                execution_id = result.get("execution_id", f"critical_review_{id(result)}")
                
                # Configure integrator for this execution
                self.integrator.configure_integration(
                    auto_persist_facts=auto_persist,
                    create_wiki_pages=create_wiki,
                    min_confidence_threshold=min_confidence
                )
                
                # Integrate knowledge persistence
                enhanced_result = await self.integrator.integrate_critical_review_workflow(
                    workflow_result=result,
                    execution_id=execution_id,
                    workflow_instance=args[0] if args else None
                )
                
                return enhanced_result
            
            return wrapper
        return decorator
    
    def integrate_multi_perspective(
        self,
        auto_persist: bool = True,
        create_wiki: bool = True,
        min_confidence: float = 0.6
    ):
        """Decorator for Multi-perspective Synthesis workflows.
        
        Args:
            auto_persist: Whether to automatically persist synthesis results
            create_wiki: Whether to create wiki pages for results
            min_confidence: Minimum confidence threshold for persistence
        """
        def decorator(func: Callable[..., Awaitable[dict[str, Any]]]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Execute original workflow
                result = await func(*args, **kwargs)
                
                # Extract execution ID from result or generate one
                execution_id = result.get("execution_id", f"multi_perspective_{id(result)}")
                
                # Configure integrator for this execution
                self.integrator.configure_integration(
                    auto_persist_synthesis=auto_persist,
                    create_wiki_pages=create_wiki,
                    min_confidence_threshold=min_confidence
                )
                
                # Integrate knowledge persistence
                enhanced_result = await self.integrator.integrate_multi_perspective_workflow(
                    workflow_result=result,
                    execution_id=execution_id,
                    workflow_instance=args[0] if args else None
                )
                
                return enhanced_result
            
            return wrapper
        return decorator
    
    def add_persistence_callback(
        self,
        callback: Callable[[str, Any], None]
    ) -> None:
        """Add a callback for persistence events."""
        self.integrator.add_persistence_callback(callback)
    
    def add_conflict_callback(
        self,
        callback: Callable[[str, list], None]
    ) -> None:
        """Add a callback for conflict events."""
        self.integrator.add_conflict_callback(callback)


# Global decorator instance (will be initialized by the application)
_global_decorator: Optional[KnowledgeIntegrationDecorator] = None


def initialize_knowledge_integration(
    sskg_manager: EnhancedSSKGManager,
    wiki_service: WikiService,
    config: WorkflowIntegrationConfig = None
) -> KnowledgeIntegrationDecorator:
    """Initialize the global knowledge integration decorator.
    
    Args:
        sskg_manager: Enhanced SSKG manager for knowledge storage
        wiki_service: Wiki service for structured documentation
        config: Configuration for integration behavior
        
    Returns:
        The initialized decorator instance
    """
    global _global_decorator
    _global_decorator = KnowledgeIntegrationDecorator(
        sskg_manager=sskg_manager,
        wiki_service=wiki_service,
        config=config
    )
    return _global_decorator


def get_knowledge_integration_decorator() -> Optional[KnowledgeIntegrationDecorator]:
    """Get the global knowledge integration decorator."""
    return _global_decorator


# Convenience decorators using the global instance
def with_critical_review_persistence(
    auto_persist: bool = True,
    create_wiki: bool = True,
    min_confidence: float = 0.5
):
    """Convenience decorator for Critical Review workflows using global instance.
    
    Args:
        auto_persist: Whether to automatically persist validated facts
        create_wiki: Whether to create wiki pages for results
        min_confidence: Minimum confidence threshold for persistence
    """
    def decorator(func: Callable[..., Awaitable[dict[str, Any]]]):
        if _global_decorator is None:
            logger.warning("Knowledge integration decorator not initialized. Skipping integration.")
            return func
        
        return _global_decorator.integrate_critical_review(
            auto_persist=auto_persist,
            create_wiki=create_wiki,
            min_confidence=min_confidence
        )(func)
    
    return decorator


def with_multi_perspective_persistence(
    auto_persist: bool = True,
    create_wiki: bool = True,
    min_confidence: float = 0.6
):
    """Convenience decorator for Multi-perspective Synthesis workflows using global instance.
    
    Args:
        auto_persist: Whether to automatically persist synthesis results
        create_wiki: Whether to create wiki pages for results
        min_confidence: Minimum confidence threshold for persistence
    """
    def decorator(func: Callable[..., Awaitable[dict[str, Any]]]):
        if _global_decorator is None:
            logger.warning("Knowledge integration decorator not initialized. Skipping integration.")
            return func
        
        return _global_decorator.integrate_multi_perspective(
            auto_persist=auto_persist,
            create_wiki=create_wiki,
            min_confidence=min_confidence
        )(func)
    
    return decorator


# Example usage functions for demonstration
async def example_critical_review_integration():
    """Example of how to use the Critical Review integration."""
    # This would typically be done in your application initialization
    from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
    from ..core_services.wiki_service import WikiService
    
    sskg_manager = EnhancedSSKGManager()
    wiki_service = WikiService()
    
    # Initialize global decorator
    decorator = initialize_knowledge_integration(sskg_manager, wiki_service)
    
    # Example workflow function with integration
    @decorator.integrate_critical_review(
        auto_persist=True,
        create_wiki=True,
        min_confidence=0.7
    )
    async def critical_review_workflow(content: str) -> dict[str, Any]:
        # Simulate workflow execution
        return {
            "success": True,
            "execution_id": "example_001",
            "original_content": content,
            "extracted_facts": [
                {
                    "id": "fact_001",
                    "content": "Example fact",
                    "confidence": 0.8,
                    "source_location": "paragraph 1"
                }
            ],
            "credibility_scores": {"fact_001": 0.8},
            "revised_content": "Revised content with corrections"
        }
    
    # Execute workflow with automatic knowledge integration
    result = await critical_review_workflow("Example content to review")
    
    # Result will now include knowledge persistence information
    print("Knowledge persistence info:", result.get("knowledge_persistence"))
    
    return result


async def example_multi_perspective_integration():
    """Example of how to use the Multi-perspective Synthesis integration."""
    
    # Example workflow function with integration
    @with_multi_perspective_persistence(
        auto_persist=True,
        create_wiki=True,
        min_confidence=0.6
    )
    async def multi_perspective_workflow(topic: str, perspectives: list) -> dict[str, Any]:
        # Simulate workflow execution
        return {
            "success": True,
            "execution_id": "example_002",
            "topic": topic,
            "perspectives": perspectives,
            "synthesis": "Comprehensive analysis from multiple perspectives",
            "quality_score": 0.85,
            "confidence": 0.78,
            "expert_contributions": {
                "经济专家": ["Economic analysis point 1", "Economic analysis point 2"],
                "社会专家": ["Social analysis point 1", "Social analysis point 2"]
            },
            "key_insights": ["Insight 1", "Insight 2", "Insight 3"]
        }
    
    # Execute workflow with automatic knowledge integration
    result = await multi_perspective_workflow("AI impact on jobs", ["经济", "社会", "技术"])
    
    # Result will now include knowledge persistence information
    print("Knowledge persistence info:", result.get("knowledge_persistence"))
    
    return result


# Callback examples
def persistence_notification_callback(execution_id: str, persistence_result: Any):
    """Example callback for persistence notifications."""
    logger.info(f"Knowledge persisted for execution {execution_id}: {persistence_result.success}")


def conflict_notification_callback(execution_id: str, conflicts: list):
    """Example callback for conflict notifications."""
    logger.warning(f"Conflicts detected in execution {execution_id}: {len(conflicts)} conflicts")


# Usage example for setting up callbacks
def setup_integration_callbacks():
    """Example of how to set up integration callbacks."""
    decorator = get_knowledge_integration_decorator()
    if decorator:
        decorator.add_persistence_callback(persistence_notification_callback)
        decorator.add_conflict_callback(conflict_notification_callback)