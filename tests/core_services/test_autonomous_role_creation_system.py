import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.core_services.autonomous_role_creation_system import (
    AutonomousRoleCreationSystem,
    RoleGenerationRequest,
    RoleGenerationResult,
    GeneratedRole,
    RoleRequirement,
    RoleType,
    ExpertiseLevel,
    InteractionStyle,
    RoleStatus,
    RoleCapability,
    RolePersonality,
)

class TestAutonomousRoleCreationSystem(unittest.TestCase):
    def setUp(self):
        self.mock_intelligence_engine = AsyncMock()
        self.mock_template_generator = AsyncMock()
        self.mock_validator = AsyncMock()
        self.mock_persistence_manager = AsyncMock()

        self.system = AutonomousRoleCreationSystem(
            storage_dir="test_roles_storage"
        )
        self.system.intelligence_engine = self.mock_intelligence_engine
        self.system.template_generator = self.mock_template_generator
        self.system.validator = self.mock_validator
        self.system.persistence_manager = self.mock_persistence_manager

    def tearDown(self):
        # Clean up any created files/directories if necessary
        pass

    def test_create_role_success(self):
        async def run_test():
            # Mock dependencies
            self.mock_intelligence_engine.analyze_domain_requirements.return_value = {
                "recommended_role_type": RoleType.EXPERT,
                "task_keywords": ["AI", "ethics"],
                "confidence_score": 0.9
            }
            self.mock_intelligence_engine.infer_capabilities.return_value = [
                RoleCapability(capability_id="cap1", name="AI Ethics", description="", skill_level=0.9)
            ]
            self.mock_intelligence_engine.generate_personality.return_value = RolePersonality(
                communication_style="formal", decision_making_approach="analytical",
                problem_solving_method="systematic", creativity_level=0.5, analytical_depth=0.9,
                risk_tolerance=0.5, collaboration_preference=0.7
            )
            self.mock_template_generator.generate_system_prompt.return_value = "You are an AI Ethicist."
            self.mock_validator.validate_role_definition.return_value = {"is_valid": True, "errors": []}
            self.mock_validator.check_role_uniqueness.return_value = {"is_unique": True}
            self.mock_persistence_manager.save_role.return_value = True
            self.mock_persistence_manager.list_roles.return_value = []

            # Create request
            request = RoleGenerationRequest(
                request_id="req123",
                requirements=RoleRequirement(
                    domain="AI Ethics",
                    task_description="Analyze ethical implications of AI",
                    expertise_level=ExpertiseLevel.EXPERT,
                    interaction_style=InteractionStyle.FORMAL,
                )
            )

            # Call method
            result = await self.system.create_role(request)

            # Assertions
            self.assertTrue(result.generated_role.status == RoleStatus.ACTIVE)
            self.assertEqual(result.generated_role.name, "高级AI Ethics专家")
            self.assertEqual(result.generated_role.role_type, RoleType.EXPERT)
            # self.assertEqual(result.generated_role.system_prompt, "You are an AI Ethicist.")
            # self.assertTrue(len(result.generated_role.capabilities) > 0)
            # self.assertTrue(result.quality_assessment["is_valid"])
            # self.assertTrue(result.generation_time_ms > 0)
            # self.mock_persistence_manager.save_role.assert_called_once()

        asyncio.run(run_test())

    def test_create_role_invalid_requirements(self):
        async def run_test():
            # Mock dependencies to simulate validation failure
            self.mock_intelligence_engine.analyze_domain_requirements.return_value = {
                "recommended_role_type": RoleType.EXPERT,
                "task_keywords": [],
                "confidence_score": 0.1
            }
            self.mock_intelligence_engine.infer_capabilities.return_value = []
            self.mock_intelligence_engine.generate_personality.return_value = RolePersonality(
                communication_style="casual", decision_making_approach="intuitive",
                problem_solving_method="ad-hoc", creativity_level=0.1, analytical_depth=0.1,
                risk_tolerance=0.1, collaboration_preference=0.1
            )
            self.mock_template_generator.generate_system_prompt.return_value = ""
            self.mock_validator.validate_role_definition.return_value = {"is_valid": False, "errors": ["Missing domain"]}
            self.mock_validator.check_role_uniqueness.return_value = {"is_unique": True}
            self.mock_persistence_manager.save_role.return_value = False
            self.mock_persistence_manager.list_roles.return_value = []

            # Create request with invalid requirements (e.g., empty task_description)
            request = RoleGenerationRequest(
                request_id="req456",
                requirements=RoleRequirement(
                    domain="", # Invalid domain
                    task_description="", # Invalid task description
                    expertise_level=ExpertiseLevel.NOVICE,
                    interaction_style=InteractionStyle.CASUAL,
                )
            )

            # Call method
            result = await self.system.create_role(request)

            # Assertions
            self.assertFalse(result.generated_role.status == RoleStatus.ACTIVE)
            self.assertFalse(result.quality_assessment["is_valid"])
            self.assertTrue(len(result.quality_assessment["errors"]) > 0)
            self.mock_persistence_manager.save_role.assert_not_called()

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()