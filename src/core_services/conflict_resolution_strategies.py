
from abc import ABC, abstractmethod
from src.core_services.conflict_resolution_system import Conflict, ResolutionResult, ResolutionStrategy
from datetime import datetime
from collections import Counter

class ConflictResolutionStrategy(ABC):
    """Abstract base class for conflict resolution strategies."""
    
    @abstractmethod
    async def resolve_conflict(self, conflict: Conflict) -> ResolutionResult:
        """Resolve a conflict."""
        pass

class MajorityVoteStrategy(ConflictResolutionStrategy):
    """Resolves conflicts using a majority vote."""
    
    async def resolve_conflict(self, conflict: Conflict) -> ResolutionResult:
        statements = [op.get("content") for op in conflict.conflicting_operations]
        
        # Count votes for each statement
        vote_counts = Counter(statements)
        
        # Find the statement with the most votes
        most_common_statement = vote_counts.most_common(1)[0][0]
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.VOTING,
            resolved_operations=[{"content": most_common_statement}],
            resolution_time=datetime.now(),
            resolver_id="system",
            success=True,
            message="Resolved by majority vote"
        )

class ExpertJudgmentStrategy(ConflictResolutionStrategy):
    """Resolves conflicts using expert judgment (weighted by expert_rating)."""
    
    async def resolve_conflict(self, conflict: Conflict) -> ResolutionResult:
        weighted_statements = []
        for op in conflict.conflicting_operations:
            expert_rating = op.get("expert_rating", 0.5) # Default to 0.5 if not provided
            weighted_statements.append({"content": op.get("content"), "weight": expert_rating})
        
        # Simple weighted average (for numerical) or weighted vote (for categorical)
        # For simplicity, we'll just pick the one with the highest weighted sum
        statement_weights = Counter()
        for item in weighted_statements:
            statement_weights[item["content"]] += item["weight"]
            
        best_statement = statement_weights.most_common(1)[0][0]
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.PRIORITY_BASED,
            resolved_operations=[{"content": best_statement}],
            resolution_time=datetime.now(),
            resolver_id="system",
            success=True,
            message="Resolved by expert judgment"
        )