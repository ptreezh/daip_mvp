"""
Unit tests for the skills manager.
"""

import pytest

from src.daip_live.skills.base import Skill, SkillMetadata, SkillOutput
from src.daip_live.skills.manager import SkillManager


class TestSkillManager:
    """Test cases for the SkillManager class."""

    @pytest.fixture
    def skill_manager(self):
        """Create a SkillManager instance for testing."""
        return SkillManager()

    @pytest.fixture
    def mock_skill(self):
        """Create a mock skill for testing."""

        class MockSkill(Skill):
            def __init__(self):
                metadata = SkillMetadata(
                    name="test_skill",
                    description="test description",
                    version="1.0",
                    author="test_author",
                    tags=["test", "analysis"],
                    dependencies=[],
                )
                super().__init__(metadata)

            def execute(self, input):
                return SkillOutput("test result", {})

        return MockSkill()

    def test_register_skill(self, skill_manager, mock_skill):
        """Test registering a skill."""
        skill_manager.register_skill(mock_skill)

        assert "test_skill" in skill_manager.list_skills()
        assert skill_manager.get_skill("test_skill") == mock_skill

    def test_unregister_skill(self, skill_manager, mock_skill):
        """Test unregistering a skill."""
        skill_manager.register_skill(mock_skill)
        skill_manager.unregister_skill("test_skill")

        assert "test_skill" not in skill_manager.list_skills()
        assert skill_manager.get_skill("test_skill") is None

    def test_register_duplicate_skill(self, skill_manager, mock_skill):
        """Test registering a duplicate skill."""
        skill_manager.register_skill(mock_skill)

        # Trying to register the same skill again should raise an error
        with pytest.raises(ValueError):
            skill_manager.register_skill(mock_skill)

    def test_get_nonexistent_skill(self, skill_manager):
        """Test getting a non-existent skill."""
        skill = skill_manager.get_skill("nonexistent")
        assert skill is None

    def test_list_skills(self, skill_manager, mock_skill):
        """Test listing registered skills."""
        assert skill_manager.list_skills() == []

        skill_manager.register_skill(mock_skill)
        assert skill_manager.list_skills() == ["test_skill"]

    def test_get_metadata(self, skill_manager, mock_skill):
        """Test getting skill metadata."""
        skill_manager.register_skill(mock_skill)

        metadata = skill_manager.get_metadata("test_skill")
        assert metadata is not None
        assert metadata.name == "test_skill"
        assert metadata.tags == ["test", "analysis"]

    def test_find_skills_by_tag(self, skill_manager):
        """Test finding skills by tag."""

        # Create skills with different tags
        class SkillA(Skill):
            def __init__(self):
                metadata = SkillMetadata(
                    "skill_a", "test", "1.0", "author", ["tag1", "common"]
                )
                super().__init__(metadata)

            def execute(self, input):
                return SkillOutput("result", {})

        class SkillB(Skill):
            def __init__(self):
                metadata = SkillMetadata(
                    "skill_b", "test", "1.0", "author", ["tag2", "common"]
                )
                super().__init__(metadata)

            def execute(self, input):
                return SkillOutput("result", {})

        skill_a = SkillA()
        skill_b = SkillB()

        skill_manager.register_skill(skill_a)
        skill_manager.register_skill(skill_b)

        # Test finding skills by specific tag
        tag1_skills = skill_manager.find_skills_by_tag("tag1")
        assert tag1_skills == ["skill_a"]

        # Test finding skills by common tag
        common_skills = skill_manager.find_skills_by_tag("common")
        assert set(common_skills) == {"skill_a", "skill_b"}

        # Test finding skills by non-existent tag
        nonexistent_skills = skill_manager.find_skills_by_tag("nonexistent")
        assert nonexistent_skills == []

    def test_skill_enable_disable(self, skill_manager, mock_skill):
        """Test enabling and disabling skills."""
        skill_manager.register_skill(mock_skill)

        # Skill should be enabled by default
        assert mock_skill.is_enabled

        # Disable the skill
        mock_skill.disable()
        assert not mock_skill.is_enabled

        # Enable the skill
        mock_skill.enable()
        assert mock_skill.is_enabled
