
"""
Sample Dynamic Skill Plugin.
"""
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata


class DynamicSkill(Skill):
    """A dynamically loaded skill."""
    
    def __init__(self):
        metadata = SkillMetadata(
            name="dynamic_skill",
            description="A dynamically loaded skill",
            version="1.0.0",
            author="DAIP-LIVE Demo",
            tags=["dynamic", "sample"]
        )
        super().__init__(metadata)
    
    def execute(self, input):
        """Execute the skill."""
        return SkillOutput(
            result=f"Dynamic skill processed: {input.data[:30]}...",
            metadata={"processed_by": "dynamic_skill"},
            confidence=0.90,
            execution_time=0.1
        )
