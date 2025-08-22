#!/usr/bin/env python3
"""
Test script for debate commands functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_debate_commands():
    """Test the debate commands functions."""
    
    print("🧪 Testing debate commands...")
    
    # Test 1: Import functions
    try:
        from src.cli.commands.debate_commands import (
            view_debate_disagreements,
            select_consensus_algorithm,
            export_debate_to_wiki
        )
        print("✅ Successfully imported debate command functions")
    except Exception as e:
        print(f"❌ Failed to import debate command functions: {e}")
        return False
    
    # Test 2: Create sample debate data
    sample_debate = {
        "topic": "AI Ethics Test Debate",
        "history": [
            {
                "role": "AI Ethicist",
                "opinion": "AI should be developed with strong ethical guidelines to ensure safety."
            },
            {
                "role": "Technologist",
                "opinion": "AI innovation should not be overly restricted by ethical concerns."
            }
        ],
        "consensus": "Balanced approach needed",
        "consensus_algorithm": "simple_majority_vote"
    }
    
    # Test 3: Test disagreement extraction
    try:
        from src.cli.commands.debate_commands import _extract_disagreements
        disagreements = _extract_disagreements(sample_debate)
        print(f"✅ Successfully extracted {len(disagreements)} disagreements")
    except Exception as e:
        print(f"❌ Failed to extract disagreements: {e}")
        return False
    
    # Test 4: Test consensus recalculation
    try:
        from src.cli.commands.debate_commands import _recalculate_consensus
        new_consensus = _recalculate_consensus(sample_debate, "weighted_vote")
        print(f"✅ Successfully recalculated consensus: {new_consensus}")
    except Exception as e:
        print(f"❌ Failed to recalculate consensus: {e}")
        return False
    
    print("🎉 All debate command tests passed!")
    return True

if __name__ == "__main__":
    success = test_debate_commands()
    sys.exit(0 if success else 1)