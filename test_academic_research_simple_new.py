#!/usr/bin/env python3
"""Quick test for academic research scenario functionality
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_academic_research_scenario():
    """Test academic research scenario with minimal setup"""
    try:
        from src.core_services.academic_research_scenario import AcademicResearchScenario, ResearchPaper, ResearchType
        
        print("Testing Academic Research Scenario...")
        
        # Create scenario with minimal initialization
        scenario = AcademicResearchScenario()
        print("AcademicResearchScenario initialized")
        
        # Create a simple test paper
        paper = ResearchPaper(
            id="test_001",
            title="Test Research Paper",
            abstract="This is a test research paper for validation purposes.",
            authors=["Test Author"],
            keywords=["test", "research"],
            research_type=ResearchType.EMPIRICAL_RESEARCH,
            methodology="Simple test methodology",
            data_sources=["Test data source"],
            findings=["Test finding 1", "Test finding 2"],
            limitations=["Test limitation"],
            references=[{"title": "Test reference", "authors": ["Test Author"], "year": 2023}],
            word_count=5000,
            submission_date=datetime.now()
        )
        print("ResearchPaper created")
        
        # Test initial assessment (should be fast)
        assessment = scenario._initial_paper_assessment(paper)
        print("Initial assessment completed")
        print(f"  - Word count: {assessment['basic_criteria']['word_count']}")
        print(f"  - Meets standards: {assessment['meets_standards']}")
        
        # Test peer reviewer selection (minimal)
        reviewer_selection = await scenario._select_peer_reviewers(paper)
        print("Peer reviewer selection completed")
        print(f"  - Success: {reviewer_selection['success']}")
        
        if reviewer_selection['success']:
            print(f"  - Selected {len(reviewer_selection['selected_reviewers'])} reviewers")
        
        print("Academic research scenario test completed successfully")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_academic_research_scenario())
    sys.exit(0 if success else 1)