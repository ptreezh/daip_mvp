"""
Example demonstrating knowledge conflict detection and resolution.

This script shows how to use the KnowledgeConflictResolver to detect and resolve
conflicts between knowledge facts in the SSKG.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from src.core_services.enhanced_sskg_manager import (
    EnhancedSSKGManager,
    KnowledgeNode,
    KnowledgeRelation,
    NodeType,
    RelationType
)
from src.core_services.knowledge_conflict_resolver import (
    KnowledgeConflictResolver,
    ConflictType,
    ResolutionStrategy
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the knowledge conflict resolution example."""
    # Create data directory if it doesn't exist
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize SSKG manager
    sskg_manager = EnhancedSSKGManager(
        graph_path=data_dir / "sskg.graphml",
        vector_store_path=data_dir / "vector_store",
        enable_vector_search=True
    )
    
    # Initialize conflict resolver
    conflict_resolver = KnowledgeConflictResolver(sskg_manager)
    
    # Create example knowledge facts with conflicts
    print("\n=== Creating Example Knowledge Facts ===\n")
    
    # Fact 1: High confidence fact from reputable source
    fact1_id = sskg_manager.add_node(KnowledgeNode(
        id="fact1",
        node_type=NodeType.FACT,
        content="The Earth orbits the Sun in approximately 365.25 days.",
        confidence=0.95,
        metadata={
            "source": "reputable_publication",
            "domain": "astronomy",
            "temporal_context": {
                "time_period": "present",
                "valid_from": "1543-01-01"  # Copernican model publication
            }
        }
    ))
    print(f"Created fact 1: {fact1_id}")
    
    # Fact 2: Direct contradiction with lower confidence
    fact2_id = sskg_manager.add_node(KnowledgeNode(
        id="fact2",
        node_type=NodeType.FACT,
        content="The Sun orbits the Earth.",
        confidence=0.3,
        metadata={
            "source": "unverified_source",
            "domain": "astronomy",
            "temporal_context": {
                "time_period": "historical",
                "valid_until": "1543-01-01"  # Copernican model publication
            }
        }
    ))
    print(f"Created fact 2: {fact2_id}")
    
    # Fact 3: Partial overlap with different details
    fact3_id = sskg_manager.add_node(KnowledgeNode(
        id="fact3",
        node_type=NodeType.FACT,
        content="The Earth completes one orbit around the Sun in 365 days, 6 hours, and 9 minutes.",
        confidence=0.85,
        metadata={
            "source": "verified_database",
            "domain": "astronomy",
            "temporal_context": {
                "time_period": "present",
                "valid_from": "1900-01-01"  # Modern measurement
            }
        }
    ))
    print(f"Created fact 3: {fact3_id}")
    
    # Fact 4: Similar to fact 1 but from different source
    fact4_id = sskg_manager.add_node(KnowledgeNode(
        id="fact4",
        node_type=NodeType.FACT,
        content="The Earth orbits the Sun in approximately 365.25 days.",
        confidence=0.9,
        metadata={
            "source": "expert_opinion",
            "domain": "astronomy",
            "temporal_context": {
                "time_period": "present",
                "valid_from": "1900-01-01"
            }
        }
    ))
    print(f"Created fact 4: {fact4_id}")
    
    # Detect conflicts
    print("\n=== Detecting Conflicts ===\n")
    
    # Detect conflicts for fact 1
    conflicts1 = conflict_resolver.detect_conflicts(fact1_id)
    print(f"Detected {len(conflicts1)} conflicts for fact 1:")
    for i, conflict in enumerate(conflicts1, 1):
        print(f"  Conflict {i}:")
        print(f"    Type: {conflict.conflict_type}")
        print(f"    Conflicting nodes: {conflict.conflicting_nodes}")
        print(f"    Confidence: {conflict.confidence:.2f}")
        print(f"    Description: {conflict.description}")
    
    # Detect conflicts for fact 3
    conflicts3 = conflict_resolver.detect_conflicts(fact3_id)
    print(f"\nDetected {len(conflicts3)} conflicts for fact 3:")
    for i, conflict in enumerate(conflicts3, 1):
        print(f"  Conflict {i}:")
        print(f"    Type: {conflict.conflict_type}")
        print(f"    Conflicting nodes: {conflict.conflicting_nodes}")
        print(f"    Confidence: {conflict.confidence:.2f}")
        print(f"    Description: {conflict.description}")
    
    # Resolve conflicts
    print("\n=== Resolving Conflicts ===\n")
    
    # Resolve conflicts for fact 1 with automatic strategy selection
    resolutions1 = conflict_resolver.resolve_conflicts(conflicts1)
    print(f"Resolved {len(resolutions1)} conflicts for fact 1:")
    for i, resolution in enumerate(resolutions1, 1):
        print(f"  Resolution {i}:")
        print(f"    Strategy: {resolution.resolution_strategy}")
        print(f"    Resolved node: {resolution.resolved_node_id}")
        print(f"    Confidence: {resolution.confidence:.2f}")
        print(f"    Reasoning: {resolution.reasoning}")
    
    # Resolve conflicts for fact 3 with specific strategies
    if conflicts3:
        # Use synthesis strategy for the first conflict
        resolutions3 = conflict_resolver.resolve_conflicts(
            [conflicts3[0]], 
            strategy=ResolutionStrategy.SYNTHESIS
        )
        print(f"\nResolved conflict for fact 3 using synthesis:")
        resolution = resolutions3[0]
        print(f"  Strategy: {resolution.resolution_strategy}")
        print(f"  Resolved node: {resolution.resolved_node_id}")
        print(f"  Confidence: {resolution.confidence:.2f}")
        print(f"  Reasoning: {resolution.reasoning}")
        
        # Get the synthesized node
        synthesized_node = sskg_manager.get_node(resolution.resolved_node_id)
        print(f"\nSynthesized node content: {synthesized_node.content}")
        print(f"Synthesized node confidence: {synthesized_node.confidence:.2f}")
    
    # Track knowledge evolution
    print("\n=== Tracking Knowledge Evolution ===\n")
    
    # Track evolution of fact 1
    evolution1 = conflict_resolver.track_knowledge_evolution(fact1_id)
    print(f"Evolution events for fact 1 ({len(evolution1)} events):")
    for i, event in enumerate(evolution1, 1):
        print(f"  Event {i}:")
        print(f"    Type: {event['event_type']}")
        print(f"    Node: {event['node_id']}")
        print(f"    Timestamp: {event['timestamp']}")
        print(f"    Description: {event['description']}")
        print(f"    Confidence change: {event['confidence_change']:.2f}")
    
    # Save the graph
    sskg_manager.save_graph()
    print("\nGraph saved successfully.")


if __name__ == "__main__":
    main()