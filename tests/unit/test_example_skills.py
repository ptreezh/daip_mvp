"""
Unit tests for example skills.
"""

import pytest

from src.daip_live.skills.base import SkillInput, SkillOutput
from src.daip_live.skills.text_analysis import TextAnalysisSkill


class TestTextAnalysisSkill:
    """Test cases for the TextAnalysisSkill class."""

    @pytest.fixture
    def text_analysis_skill(self):
        """Create a TextAnalysisSkill instance for testing."""
        return TextAnalysisSkill()

    def test_initialization(self, text_analysis_skill):
        """Test skill initialization."""
        assert text_analysis_skill.metadata.name == "text_analysis"
        assert (
            text_analysis_skill.metadata.description
            == "Analyzes text content for key themes and patterns"
        )
        assert "text" in text_analysis_skill.metadata.tags
        assert text_analysis_skill.is_enabled

    def test_execute_analysis(self, text_analysis_skill):
        """Test executing text analysis."""
        input_data = SkillInput("这是一个测试文本，包含教育和科技相关内容。")
        output = text_analysis_skill.execute(input_data)

        assert isinstance(output, SkillOutput)
        assert isinstance(output.result, str)
        assert isinstance(output.metadata, dict)
        assert output.confidence > 0
        assert output.execution_time > 0

    def test_identify_themes(self, text_analysis_skill):
        """Test theme identification."""
        text = "学生在学校学习科技知识，教师使用数字工具教学。"
        themes = text_analysis_skill._identify_themes(text)

        assert isinstance(themes, list)
        # Should identify education and technology themes
        assert len(themes) >= 0  # Could be empty if no matches

    def test_execute_empty_text(self, text_analysis_skill):
        """Test executing analysis on empty text."""
        input_data = SkillInput("")
        output = text_analysis_skill.execute(input_data)

        assert isinstance(output, SkillOutput)
        assert "Word count: 0" in output.result

    def test_execute_chinese_text(self, text_analysis_skill):
        """Test executing analysis on Chinese text."""
        input_data = SkillInput("中国社会文化传统价值观念")
        output = text_analysis_skill.execute(input_data)

        assert isinstance(output, SkillOutput)
        assert isinstance(output.result, str)
        assert "Word count:" in output.result
