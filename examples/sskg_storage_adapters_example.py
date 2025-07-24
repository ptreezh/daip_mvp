"""
Example demonstrating the use of unified storage adapters.

This script shows how to use different storage adapters to manage
various types of data in the SSKG.
"""

import logging
from pathlib import Path

from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
from src.core_services.sskg_storage_adapters import (
    RoleMemoryAdapter,
    WikiAdapter,
    SessionAdapter,
    StorageAdapterManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the storage adapters example."""
    # Create data directory if it doesn't exist
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize SSKG manager
    sskg_manager = EnhancedSSKGManager(
        graph_path=data_dir / "sskg.graphml",
        vector_store_path=data_dir / "vector_store",
        enable_vector_search=True
    )
    
    # Initialize storage adapter manager
    adapter_manager = StorageAdapterManager(sskg_manager)
    
    print("\n=== Storage Adapters Example ===\n")
    
    # Example 1: Role Memory Adapter
    print("1. Role Memory Adapter Example")
    print("-" * 40)
    
    role_data = {
        "role_id": "expert_scientist",
        "name": "Dr. Sarah Chen",
        "personality": {
            "traits": ["analytical", "curious", "methodical"],
            "expertise": "quantum physics",
            "communication_style": "precise and technical"
        },
        "cognitive_framework": {
            "reasoning_type": "scientific_method",
            "bias_awareness": "high",
            "uncertainty_tolerance": "high"
        },
        "memories": [
            {
                "content": "Published groundbreaking research on quantum entanglement in 2023",
                "type": "episodic",
                "importance": 0.9,
                "context": {"domain": "research", "year": "2023"}
            },
            {
                "content": "Quantum mechanics principles and mathematical formulations",
                "type": "semantic",
                "importance": 0.8,
                "context": {"domain": "knowledge", "field": "physics"}
            }
        ]
    }
    
    # Store role data
    role_id = adapter_manager.store_data("role_memory", role_data)
    print(f"Stored role with ID: {role_id}")
    
    # Retrieve role data
    retrieved_role = adapter_manager.retrieve_data("role_memory", "expert_scientist")
    print(f"Retrieved role: {retrieved_role['name']}")
    print(f"Number of memories: {len(retrieved_role['memories'])}")
    
    # Example 2: Wiki Adapter
    print("\n2. Wiki Adapter Example")
    print("-" * 40)
    
    wiki_data = {
        "page_id": "quantum_computing_basics",
        "title": "Quantum Computing Fundamentals",
        "content": """
        Quantum computing is a revolutionary approach to computation that leverages
        the principles of quantum mechanics to process information in fundamentally
        new ways. Unlike classical computers that use bits (0 or 1), quantum
        computers use quantum bits or 'qubits' that can exist in superposition.
        """,
        "tags": ["quantum", "computing", "physics", "technology"],
        "category": "science",
        "author": "Dr. Sarah Chen"
    }
    
    # Store wiki page
    wiki_id = adapter_manager.store_data("wiki", wiki_data)
    print(f"Stored wiki page with ID: {wiki_id}")
    
    # Retrieve wiki page
    retrieved_wiki = adapter_manager.retrieve_data("wiki", "quantum_computing_basics")
    print(f"Retrieved wiki page: {retrieved_wiki['title']}")
    print(f"Tags: {', '.join(retrieved_wiki['tags'])}")
    
    # Example 3: Session Adapter
    print("\n3. Session Adapter Example")
    print("-" * 40)
    
    session_data = {
        "session_id": "user_session_001",
        "user_id": "user_123",
        "state": {
            "current_topic": "quantum computing",
            "user_expertise_level": "beginner",
            "preferred_explanation_style": "visual"
        },
        "conversation_history": [
            {
                "timestamp": "2025-01-15T10:00:00Z",
                "speaker": "user",
                "message": "Can you explain quantum computing?"
            },
            {
                "timestamp": "2025-01-15T10:00:30Z",
                "speaker": "assistant",
                "message": "Quantum computing uses quantum mechanics principles..."
            }
        ],
        "context": {
            "session_start": "2025-01-15T10:00:00Z",
            "active_roles": ["expert_scientist"],
            "current_workflow": "educational_explanation"
        }
    }
    
    # Store session data
    session_id = adapter_manager.store_data("session", session_data)
    print(f"Stored session with ID: {session_id}")
    
    # Retrieve session data
    retrieved_session = adapter_manager.retrieve_data("session", "user_session_001")
    print(f"Retrieved session for user: {retrieved_session['user_id']}")
    print(f"Current topic: {retrieved_session['state']['current_topic']}")
    print(f"Conversation messages: {len(retrieved_session['conversation_history'])}")
    
    # Example 4: Hierarchical Organization
    print("\n4. Hierarchical Organization Example")
    print("-" * 40)
    
    # Create related wiki pages to demonstrate hierarchical organization
    related_pages = [
        {
            "page_id": "quantum_algorithms",
            "title": "Quantum Algorithms",
            "content": "Overview of quantum algorithms including Shor's and Grover's algorithms.",
            "tags": ["quantum", "algorithms", "computing"],
            "category": "science"
        },
        {
            "page_id": "quantum_hardware",
            "title": "Quantum Hardware",
            "content": "Physical implementations of quantum computers including superconducting qubits.",
            "tags": ["quantum", "hardware", "engineering"],
            "category": "science"
        }
    ]
    
    for page_data in related_pages:
        page_id = adapter_manager.store_data("wiki", page_data)
        print(f"Stored related page: {page_data['title']} (ID: {page_id})")
    
    # Example 5: Cross-Adapter Integration
    print("\n5. Cross-Adapter Integration Example")
    print("-" * 40)
    
    # Update role with new memory based on wiki interaction
    new_memory = {
        "content": "Explained quantum computing fundamentals to a beginner user",
        "type": "episodic",
        "importance": 0.7,
        "context": {
            "interaction_type": "educational",
            "user_level": "beginner",
            "wiki_page": "quantum_computing_basics"
        }
    }
    
    # Get current role data and add new memory
    current_role = adapter_manager.retrieve_data("role_memory", "expert_scientist")
    current_role["memories"].append(new_memory)
    
    # Update role with new memory
    role_adapter = adapter_manager.get_adapter("role_memory")
    role_adapter.update("expert_scientist", current_role)
    print("Updated role with new memory from wiki interaction")
    
    # Update session with new conversation turn
    current_session = adapter_manager.retrieve_data("session", "user_session_001")
    current_session["conversation_history"].append({
        "timestamp": "2025-01-15T10:05:00Z",
        "speaker": "assistant",
        "message": "I've also created a wiki page about quantum computing fundamentals for future reference."
    })
    
    # Update session
    session_adapter = adapter_manager.get_adapter("session")
    session_adapter.update("user_session_001", current_session)
    print("Updated session with new conversation turn")
    
    # Save the graph
    sskg_manager.save_graph()
    print("\nGraph saved successfully.")
    
    # Display summary
    print("\n=== Summary ===")
    print(f"Available adapters: {', '.join(adapter_manager.list_adapters())}")
    print(f"Total nodes in SSKG: {sskg_manager.graph.number_of_nodes()}")
    print(f"Total edges in SSKG: {sskg_manager.graph.number_of_edges()}")


if __name__ == "__main__":
    main()