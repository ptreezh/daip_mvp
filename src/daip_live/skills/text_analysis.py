"""
Example skill for text analysis.
"""
from typing import List, Dict, Any
from ..skills.base import Skill, SkillInput, SkillOutput, SkillMetadata


class TextAnalysisSkill(Skill):
    """Example skill for analyzing text content."""
    
    def __init__(self):
        metadata = SkillMetadata(
            name="text_analysis",
            description="Analyzes text content for key themes and patterns",
            version="1.0",
            author="DAIP-LIVE",
            tags=["text", "analysis", "nlp"]
        )
        super().__init__(metadata)
    
    def execute(self, input: SkillInput) -> SkillOutput:
        """
        Execute text analysis on the input data.
        
        Args:
            input: SkillInput containing text to analyze
            
        Returns:
            SkillOutput with analysis results
        """
        # Simple text analysis
        text = input.data
        word_count = len(text.split())
        char_count = len(text)
        
        # Identify key themes (simplified)
        themes = self._identify_themes(text)
        
        result = f"""Text Analysis Results:
- Word count: {word_count}
- Character count: {char_count}
- Key themes: {', '.join(themes) if themes else 'None identified'}"""

        metadata = {
            "word_count": word_count,
            "char_count": char_count,
            "themes": themes,
            "skill_name": self.metadata.name
        }
        
        return SkillOutput(
            result=result,
            metadata=metadata,
            confidence=0.75,
            execution_time=0.1  # Simulated execution time
        )
    
    def _identify_themes(self, text: str) -> List[str]:
        """Identify key themes in the text."""
        # Simplified theme identification
        themes = []
        text_lower = text.lower()
        
        # Check for common themes
        theme_keywords = {
            "education": ["学习", "教育", "学校", "老师", "学生"],
            "technology": ["技术", "科技", "网络", "数字", "智能"],
            "social": ["社会", "关系", "人际", "群体", "社区"],
            "culture": ["文化", "传统", "价值", "观念", "习俗"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes