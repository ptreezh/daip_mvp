#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the system components we want to test
from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
from src.core_services.role_manager import RoleManager


@pytest.fixture
def role_manager() -> RoleManager:
    """Pytest fixture to provide a RoleManager instance."""
    return RoleManager()


@pytest.fixture
def llm_integrator() -> RealLLMIntegrator:
    """Pytest fixture to provide a RealLLMIntegrator instance."""
    return RealLLMIntegrator()


@pytest.fixture
def debate_system(llm_integrator: RealLLMIntegrator, role_manager: RoleManager) -> MultiRoleDebateSystem:
    """Pytest fixture to provide a fully initialized MultiRoleDebateSystem."""
    return MultiRoleDebateSystem(llm_integrator, role_manager)


@pytest.mark.asyncio
async def test_system_initialization(debate_system: MultiRoleDebateSystem):
    """Tests that the main debate system and its components initialize correctly."""
    assert debate_system is not None, "Debate system should not be None"
    assert debate_system.llm_integrator is not None, "LLM integrator should be initialized"
    assert debate_system.role_manager is not None, "Role manager should be initialized"


@pytest.mark.asyncio
async def test_role_loading(role_manager: RoleManager):
    """Tests that roles are loaded correctly."""
    assert len(role_manager.list_roles()) > 10, "Should load a significant number of roles"
    ai_ethics_role = role_manager.get_role("AI Ethics")
    assert ai_ethics_role is not None, "AI Ethics role should exist"
    assert ai_ethics_role.name is not None, "Role should have a name"


@pytest.mark.asyncio
async def test_debate_creation_success(debate_system: MultiRoleDebateSystem):
    """Tests the successful creation of a debate with valid roles."""
    topic = "Testing debate creation"
    roles = ["AI Ethics", "Business Ethics"]
    result = await debate_system.start_debate(debate_topic=topic, participating_roles=roles)
    
    assert "error" not in result, f"Debate creation failed with error: {result.get('error')}"
    assert "debate_id" in result, "Debate result should contain a debate_id"
    assert result["topic"] == topic
    assert len(result["participating_roles"]) == 2


@pytest.mark.asyncio
async def test_debate_creation_insufficient_roles(debate_system: MultiRoleDebateSystem):
    """Tests that debate creation fails gracefully with fewer than 2 roles."""
    topic = "Testing with insufficient roles"
    roles = ["AI Ethics"]
    result = await debate_system.start_debate(debate_topic=topic, participating_roles=roles)
    
    assert "error" in result, "Debate should have failed but didn't"
    assert "At least 2 valid roles are required" in result["error"], "Error message is not as expected"


@pytest.mark.asyncio
async def test_debate_creation_with_invalid_role(debate_system: MultiRoleDebateSystem):
    """Tests that debate creation proceeds even if one role is invalid, as long as enough valid roles remain."""
    topic = "Testing with an invalid role"
    roles = ["AI Ethics", "Business Ethics", "InvalidRole99"]
    result = await debate_system.start_debate(debate_topic=topic, participating_roles=roles)
    
    assert "error" not in result, "Debate creation failed unexpectedly"
    assert len(result["participating_roles"]) == 2, "Should have proceeded with the 2 valid roles"


@pytest.mark.asyncio
async def test_get_debate_status(debate_system: MultiRoleDebateSystem):
    """Tests retrieving the status of an active debate."""
    topic = "Testing status retrieval"
    roles = ["AI Ethics", "Data Governance Expert"]
    creation_result = await debate_system.start_debate(debate_topic=topic, participating_roles=roles)
    debate_id = creation_result["debate_id"]
    
    status = debate_system.get_debate_status(debate_id)
    
    assert "error" not in status, "Failed to get status"
    assert status["debate_id"] == debate_id
    assert status["topic"] == topic
    assert status["phase"] == "initialization"

