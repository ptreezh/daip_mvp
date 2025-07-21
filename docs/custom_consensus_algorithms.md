# Custom Consensus Algorithms

## Overview

The DAIP-LIVE project uses a pluggable consensus system that allows for the implementation of custom consensus algorithms. This document explains how to create and register custom consensus strategies for use in debates and other collaborative processes.

## Architecture

The consensus system is built around the following components:

1. **ConsensusStrategy**: Abstract base class that defines the interface for all consensus strategies
2. **ConsensusStrategyFactory**: Factory class that registers and creates consensus strategy instances
3. **UnifiedToolManager**: Service that manages and executes tools, including consensus strategies

### Consensus Strategy Interface

All consensus strategies must implement the `ConsensusStrategy` abstract base class, which defines the `execute` method:

```python
from abc import ABC, abstractmethod
from typing import List, Any

class ConsensusStrategy(ABC):
    @abstractmethod
    async def execute(self, opinions: List[Opinion]) -> ConsensusResult:
        """
        Execute the consensus strategy on a list of opinions.
        
        Args:
            opinions: List of Opinion objects representing different viewpoints
            
        Returns:
            ConsensusResult object containing the consensus outcome
        """
        pass
```

### Opinion and ConsensusResult Models

The consensus system uses the following data models:

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Opinion(BaseModel):
    """
    Represents an opinion or argument in a debate.
    """
    role_id: str
    content: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConsensusResult(BaseModel):
    """
    Represents the result of a consensus process.
    """
    consensus_text: str
    agreement_level: float = Field(default=0.0, ge=0.0, le=1.0)
    dissenting_opinions: List[Opinion] = Field(default_factory=list)
    supporting_opinions: List[Opinion] = Field(default_factory=list)
    method_description: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

## Implementing a Custom Consensus Strategy

### Step 1: Create a New Strategy Class

Create a new Python file in the `src/protocols/consensus_strategies` directory with your custom strategy implementation:

```python
# src/protocols/consensus_strategies/weighted_voting_strategy.py

from typing import List, Dict, Any
from datetime import datetime

from src.protocols.consensus_strategies.base import ConsensusStrategy
from src.models import Opinion, ConsensusResult

class WeightedVotingStrategy(ConsensusStrategy):
    """
    A consensus strategy that weighs opinions based on role expertise and confidence.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the WeightedVotingStrategy.
        
        Args:
            weights: Optional dictionary mapping role_ids to weights
        """
        self.weights = weights or {}
    
    async def execute(self, opinions: List[Opinion]) -> ConsensusResult:
        """
        Execute the weighted voting strategy on a list of opinions.
        
        Args:
            opinions: List of Opinion objects representing different viewpoints
            
        Returns:
            ConsensusResult object containing the consensus outcome
        """
        if not opinions:
            return ConsensusResult(
                consensus_text="No opinions provided",
                agreement_level=0.0,
                method_description="Weighted voting strategy (no opinions)"
            )
        
        # Calculate weights for each opinion
        weighted_opinions = []
        for opinion in opinions:
            # Get weight for the role (default to 1.0 if not specified)
            role_weight = self.weights.get(opinion.role_id, 1.0)
            
            # Calculate final weight based on role weight and confidence
            final_weight = role_weight * opinion.confidence
            
            weighted_opinions.append((opinion, final_weight))
        
        # Sort opinions by weight (descending)
        weighted_opinions.sort(key=lambda x: x[1], reverse=True)
        
        # Select the highest-weighted opinion as the consensus
        consensus_opinion = weighted_opinions[0][0]
        
        # Calculate agreement level based on weight distribution
        total_weight = sum(weight for _, weight in weighted_opinions)
        consensus_weight = weighted_opinions[0][1]
        agreement_level = consensus_weight / total_weight if total_weight > 0 else 0.0
        
        # Separate supporting and dissenting opinions
        supporting_opinions = []
        dissenting_opinions = []
        
        # Simple heuristic: opinions with similar content support the consensus
        for opinion, _ in weighted_opinions[1:]:
            # This is a simplified approach - in a real implementation,
            # you would use more sophisticated text similarity measures
            similarity = self._calculate_similarity(consensus_opinion.content, opinion.content)
            if similarity > 0.7:  # Arbitrary threshold
                supporting_opinions.append(opinion)
            else:
                dissenting_opinions.append(opinion)
        
        return ConsensusResult(
            consensus_text=consensus_opinion.content,
            agreement_level=agreement_level,
            supporting_opinions=supporting_opinions,
            dissenting_opinions=dissenting_opinions,
            method_description="Weighted voting strategy based on role expertise and confidence",
            metadata={
                "weights": self.weights,
                "weighted_distribution": [
                    {"role_id": op.role_id, "weight": w} 
                    for op, w in weighted_opinions
                ]
            }
        )
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.
        
        This is a placeholder implementation. In a real system, you would use
        more sophisticated text similarity measures like cosine similarity
        with embeddings, or other NLP techniques.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
```

### Step 2: Register the Strategy in the Factory

Update the `src/protocols/consensus_strategies/__init__.py` file to include your new strategy:

```python
from src.protocols.consensus_strategies.base import ConsensusStrategy, ConsensusStrategyFactory
from src.protocols.consensus_strategies.simple_majority_vote import SimpleMajorityVoteStrategy
from src.protocols.consensus_strategies.weighted_voting_strategy import WeightedVotingStrategy

__all__ = [
    "ConsensusStrategy",
    "ConsensusStrategyFactory",
    "SimpleMajorityVoteStrategy",
    "WeightedVotingStrategy",
]
```

### Step 3: Register the Strategy in the Application Startup

Update the application startup code in `src/main.py` to register your new strategy:

```python
@app.on_event("startup")
async def startup_event():
    """Initializes the application state on startup."""
    logger.info("Starting up and initializing application state...")
    dependencies.app_state = AppState()
    logger.info("Application state initialized successfully.")

    logger.info("Initializing and registering consensus strategies...")
    # 1. Create the factory for consensus strategies.
    consensus_factory = ConsensusStrategyFactory()

    # 2. Register all available strategies in the factory.
    consensus_factory.register("simple_majority_vote", SimpleMajorityVoteStrategy)
    consensus_factory.register("weighted_voting", WeightedVotingStrategy)  # Add your new strategy

    # 3. Use the factory to register those strategies as tools in the UnifiedToolManager,
    #    which is managed by the central AppState.
    dependencies.app_state.unified_tool_manager.register_strategies_from_factory(consensus_factory)
    logger.info("Consensus strategies successfully registered as executable tools.")
```

## Advanced Consensus Strategies

### Reputation-Based Strategy

This strategy weighs opinions based on the reputation of the roles, which can be dynamically updated based on the quality of their contributions.

```python
class ReputationBasedStrategy(ConsensusStrategy):
    """
    A consensus strategy that weighs opinions based on role reputation.
    """
    
    def __init__(self, reputation_service):
        """
        Initialize the ReputationBasedStrategy.
        
        Args:
            reputation_service: Service that provides reputation scores for roles
        """
        self.reputation_service = reputation_service
    
    async def execute(self, opinions: List[Opinion]) -> ConsensusResult:
        """
        Execute the reputation-based strategy on a list of opinions.
        
        Args:
            opinions: List of Opinion objects representing different viewpoints
            
        Returns:
            ConsensusResult object containing the consensus outcome
        """
        if not opinions:
            return ConsensusResult(
                consensus_text="No opinions provided",
                agreement_level=0.0,
                method_description="Reputation-based strategy (no opinions)"
            )
        
        # Get reputation scores for each role
        reputation_scores = {}
        for opinion in opinions:
            reputation_scores[opinion.role_id] = await self.reputation_service.get_reputation(opinion.role_id)
        
        # Calculate weighted opinions based on reputation
        weighted_opinions = []
        for opinion in opinions:
            reputation = reputation_scores.get(opinion.role_id, 0.5)
            weighted_opinions.append((opinion, reputation * opinion.confidence))
        
        # Sort opinions by weight (descending)
        weighted_opinions.sort(key=lambda x: x[1], reverse=True)
        
        # Select the highest-weighted opinion as the consensus
        consensus_opinion = weighted_opinions[0][0]
        
        # Calculate agreement level and separate supporting/dissenting opinions
        # ... (similar to WeightedVotingStrategy)
        
        return ConsensusResult(
            consensus_text=consensus_opinion.content,
            agreement_level=agreement_level,
            supporting_opinions=supporting_opinions,
            dissenting_opinions=dissenting_opinions,
            method_description="Reputation-based consensus strategy",
            metadata={
                "reputation_scores": reputation_scores,
                "weighted_distribution": [
                    {"role_id": op.role_id, "weight": w} 
                    for op, w in weighted_opinions
                ]
            }
        )
```

### Clustering Strategy

This strategy uses clustering algorithms to group similar opinions and identify the most representative opinion from the largest cluster.

```python
class ClusteringStrategy(ConsensusStrategy):
    """
    A consensus strategy that uses clustering to group similar opinions.
    """
    
    def __init__(self, embedding_service):
        """
        Initialize the ClusteringStrategy.
        
        Args:
            embedding_service: Service that provides text embeddings
        """
        self.embedding_service = embedding_service
    
    async def execute(self, opinions: List[Opinion]) -> ConsensusResult:
        """
        Execute the clustering strategy on a list of opinions.
        
        Args:
            opinions: List of Opinion objects representing different viewpoints
            
        Returns:
            ConsensusResult object containing the consensus outcome
        """
        if not opinions:
            return ConsensusResult(
                consensus_text="No opinions provided",
                agreement_level=0.0,
                method_description="Clustering strategy (no opinions)"
            )
        
        # Generate embeddings for each opinion
        embeddings = []
        for opinion in opinions:
            embedding = await self.embedding_service.get_embedding(opinion.content)
            embeddings.append(embedding)
        
        # Perform clustering on embeddings
        clusters = self._cluster_embeddings(embeddings)
        
        # Find the largest cluster
        largest_cluster_idx = max(range(len(clusters)), key=lambda i: len(clusters[i]))
        largest_cluster = clusters[largest_cluster_idx]
        
        # Find the opinion closest to the centroid of the largest cluster
        centroid = self._calculate_centroid(largest_cluster)
        closest_idx = self._find_closest_to_centroid(largest_cluster, centroid)
        
        # Get the consensus opinion
        consensus_opinion_idx = largest_cluster[closest_idx]
        consensus_opinion = opinions[consensus_opinion_idx]
        
        # Calculate agreement level based on cluster sizes
        total_opinions = len(opinions)
        largest_cluster_size = len(largest_cluster)
        agreement_level = largest_cluster_size / total_opinions
        
        # Separate supporting and dissenting opinions
        supporting_opinions = [opinions[i] for i in largest_cluster if i != consensus_opinion_idx]
        dissenting_opinions = [
            opinions[i] for i in range(len(opinions))
            if i not in largest_cluster
        ]
        
        return ConsensusResult(
            consensus_text=consensus_opinion.content,
            agreement_level=agreement_level,
            supporting_opinions=supporting_opinions,
            dissenting_opinions=dissenting_opinions,
            method_description="Clustering-based consensus strategy",
            metadata={
                "num_clusters": len(clusters),
                "cluster_sizes": [len(c) for c in clusters],
                "largest_cluster_idx": largest_cluster_idx
            }
        )
    
    def _cluster_embeddings(self, embeddings):
        """
        Cluster embeddings using a clustering algorithm.
        
        This is a placeholder implementation. In a real system, you would use
        a proper clustering algorithm like K-means, DBSCAN, or hierarchical clustering.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            List of clusters, where each cluster is a list of indices into the original opinions list
        """
        # Placeholder implementation - in a real system, use scikit-learn or similar
        # For simplicity, this just creates a single cluster with all opinions
        return [[i for i in range(len(embeddings))]]
    
    def _calculate_centroid(self, cluster):
        """Calculate the centroid of a cluster."""
        # Placeholder implementation
        return [0.0] * 768  # Assuming 768-dimensional embeddings
    
    def _find_closest_to_centroid(self, cluster, centroid):
        """Find the index in the cluster that is closest to the centroid."""
        # Placeholder implementation
        return 0  # Just return the first element
```

## Testing Custom Consensus Strategies

### Unit Testing

Create unit tests for your custom consensus strategy to ensure it works as expected:

```python
# tests/test_consensus_strategies.py

import unittest
from src.models import Opinion, ConsensusResult
from src.protocols.consensus_strategies import WeightedVotingStrategy

class TestWeightedVotingStrategy(unittest.TestCase):
    """Test cases for the WeightedVotingStrategy."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a strategy with predefined weights
        self.weights = {
            "expert": 2.0,
            "novice": 0.5,
            "standard": 1.0
        }
        self.strategy = WeightedVotingStrategy(weights=self.weights)
        
        # Create test opinions
        self.opinions = [
            Opinion(
                role_id="expert",
                content="The solution is to use a distributed system",
                confidence=0.9
            ),
            Opinion(
                role_id="novice",
                content="We should use a centralized approach",
                confidence=0.7
            ),
            Opinion(
                role_id="standard",
                content="A hybrid approach would be best",
                confidence=0.8
            )
        ]
    
    async def test_execute_with_opinions(self):
        """Test executing the strategy with opinions."""
        result = await self.strategy.execute(self.opinions)
        
        # Verify the result
        self.assertEqual(result.consensus_text, "The solution is to use a distributed system")
        self.assertGreater(result.agreement_level, 0.0)
        self.assertEqual(len(result.supporting_opinions) + len(result.dissenting_opinions), 2)
    
    async def test_execute_with_empty_opinions(self):
        """Test executing the strategy with no opinions."""
        result = await self.strategy.execute([])
        
        # Verify the result
        self.assertEqual(result.consensus_text, "No opinions provided")
        self.assertEqual(result.agreement_level, 0.0)
        self.assertEqual(len(result.supporting_opinions), 0)
        self.assertEqual(len(result.dissenting_opinions), 0)
    
    async def test_execute_with_equal_weights(self):
        """Test executing the strategy with equal weights."""
        # Create a strategy with equal weights
        equal_strategy = WeightedVotingStrategy(weights={"expert": 1.0, "novice": 1.0, "standard": 1.0})
        
        result = await equal_strategy.execute(self.opinions)
        
        # With equal weights, the highest confidence opinion should win
        self.assertEqual(result.consensus_text, "The solution is to use a distributed system")
```

### Integration Testing

Create integration tests to ensure your strategy works with the rest of the system:

```python
# tests/test_consensus_integration.py

import unittest
from unittest.mock import MagicMock, patch
from src.models import Opinion, ConsensusResult
from src.protocols.consensus_strategies import ConsensusStrategyFactory, WeightedVotingStrategy
from src.unified_tool_manager import UnifiedToolManager

class TestConsensusIntegration(unittest.TestCase):
    """Integration tests for consensus strategies."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a factory and register strategies
        self.factory = ConsensusStrategyFactory()
        self.factory.register("weighted_voting", WeightedVotingStrategy)
        
        # Create a mock tool manager
        self.tool_manager = MagicMock(spec=UnifiedToolManager)
        
        # Register strategies with the tool manager
        self.factory.register_strategies_with_tool_manager(self.tool_manager)
        
        # Create test opinions
        self.opinions = [
            Opinion(
                role_id="expert",
                content="The solution is to use a distributed system",
                confidence=0.9
            ),
            Opinion(
                role_id="novice",
                content="We should use a centralized approach",
                confidence=0.7
            )
        ]
    
    def test_strategy_registration(self):
        """Test that strategies are properly registered."""
        # Verify that the tool manager's register_tool method was called
        self.tool_manager.register_tool.assert_any_call(
            "consensus.weighted_voting",
            WeightedVotingStrategy,
            description="Weighted voting consensus strategy"
        )
    
    @patch("src.unified_tool_manager.UnifiedToolManager.execute_tool")
    async def test_strategy_execution(self, mock_execute_tool):
        """Test executing a strategy through the tool manager."""
        # Set up the mock to return a consensus result
        mock_result = ConsensusResult(
            consensus_text="The solution is to use a distributed system",
            agreement_level=0.8,
            method_description="Weighted voting strategy"
        )
        mock_execute_tool.return_value = mock_result
        
        # Create a real tool manager with the factory
        tool_manager = UnifiedToolManager(config={})
        self.factory.register_strategies_with_tool_manager(tool_manager)
        
        # Execute the strategy through the tool manager
        result = await tool_manager.execute_tool(
            "consensus.weighted_voting",
            opinions=self.opinions,
            weights={"expert": 2.0, "novice": 0.5}
        )
        
        # Verify the result
        self.assertEqual(result.consensus_text, "The solution is to use a distributed system")
        self.assertEqual(result.agreement_level, 0.8)
```

## Using Custom Consensus Strategies in Debates

Once your custom consensus strategy is registered, you can use it in debates by specifying it in the debate configuration:

```python
from src.models import DebateConfig

# Create a debate configuration with your custom strategy
debate_config = DebateConfig(
    topic="What is the best approach for scaling our system?",
    roles=["software_architect", "database_expert", "devops_engineer"],
    rounds=3,
    consensus_strategy="weighted_voting"  # Use your custom strategy
)

# Start the debate
debate_result = await debate_service.run_debate(debate_config)
```

You can also pass parameters to your strategy through the debate configuration:

```python
from src.models import DebateConfig

# Create a debate configuration with parameters for your custom strategy
debate_config = DebateConfig(
    topic="What is the best approach for scaling our system?",
    roles=["software_architect", "database_expert", "devops_engineer"],
    rounds=3,
    consensus_strategy="weighted_voting",
    consensus_params={
        "weights": {
            "software_architect": 2.0,
            "database_expert": 1.5,
            "devops_engineer": 1.0
        }
    }
)

# Start the debate
debate_result = await debate_service.run_debate(debate_config)
```

## Best Practices

When creating custom consensus strategies, follow these best practices:

1. **Clear Documentation**: Document your strategy's purpose, algorithm, and parameters.

2. **Error Handling**: Handle edge cases gracefully, such as empty opinion lists or missing parameters.

3. **Performance Considerations**: Be mindful of performance, especially for computationally intensive algorithms.

4. **Testing**: Write comprehensive tests for your strategy to ensure it works as expected.

5. **Extensibility**: Design your strategy to be configurable and extensible.

6. **Transparency**: Make your strategy's decision-making process transparent and explainable.

7. **Fairness**: Ensure your strategy treats all opinions fairly and doesn't introduce unintended bias.

## Conclusion

Custom consensus strategies allow you to tailor the debate process to your specific needs. By implementing the `ConsensusStrategy` interface and registering your strategy with the factory, you can create sophisticated consensus algorithms that leverage domain-specific knowledge, reputation systems, or advanced NLP techniques.

The pluggable consensus system is a key part of the DAIP-LIVE project's extensibility, enabling continuous improvement and adaptation to different use cases and domains.