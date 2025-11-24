"""
Unit tests for the parallel executor.
"""
import pytest
import time
from unittest.mock import Mock, patch
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata
from src.daip_live.execution.parallel import ParallelExecutor


class TestParallelExecutor:
    """Test cases for the ParallelExecutor class."""
    
    @pytest.fixture
    def parallel_executor(self):
        """Create a ParallelExecutor instance for testing."""
        return ParallelExecutor(max_workers=2)
    
    @pytest.fixture
    def mock_skills(self):
        """Create mock skills for testing."""
        skills = []
        
        for i in range(3):
            class MockSkill(Skill):
                def __init__(self, name):
                    metadata = SkillMetadata(name, "test description", "1.0", "author")
                    super().__init__(metadata)
                
                def execute(self, input):
                    # Simulate some work
                    time.sleep(0.01)
                    return SkillOutput(f"result from {self.metadata.name}", {})
            
            skills.append(MockSkill(f"skill_{i}"))
        
        return skills
    
    def test_execute_skills_parallel(self, parallel_executor, mock_skills):
        """Test executing skills in parallel."""
        inputs = [SkillInput(f"data_{i}") for i in range(3)]
        
        outputs = parallel_executor.execute_skills_parallel(mock_skills, inputs)
        
        assert len(outputs) == 3
        for i, output in enumerate(outputs):
            assert isinstance(output, SkillOutput)
            assert output.result == f"result from skill_{i}"
    
    def test_execute_skills_with_disabled_skill(self, parallel_executor):
        """Test executing skills with a disabled skill."""
        class DisabledSkill(Skill):
            def __init__(self):
                metadata = SkillMetadata("disabled_skill", "test", "1.0", "author")
                super().__init__(metadata)
                self.disable()  # Disable the skill
            
            def execute(self, input):
                return SkillOutput("should not execute", {})
        
        class EnabledSkill(Skill):
            def __init__(self):
                metadata = SkillMetadata("enabled_skill", "test", "1.0", "author")
                super().__init__(metadata)
            
            def execute(self, input):
                return SkillOutput("enabled result", {})
        
        skills = [DisabledSkill(), EnabledSkill()]
        inputs = [SkillInput("data1"), SkillInput("data2")]
        
        outputs = parallel_executor.execute_skills_parallel(skills, inputs)
        
        assert len(outputs) == 2
        # First output should indicate disabled skill
        assert "disabled" in outputs[0].metadata
        # Second output should be normal result
        assert outputs[1].result == "enabled result"
    
    def test_execute_skills_with_error(self, parallel_executor):
        """Test executing skills that raise exceptions."""
        class ErrorSkill(Skill):
            def __init__(self):
                metadata = SkillMetadata("error_skill", "test", "1.0", "author")
                super().__init__(metadata)
            
            def execute(self, input):
                raise Exception("Test error")
        
        class NormalSkill(Skill):
            def __init__(self):
                metadata = SkillMetadata("normal_skill", "test", "1.0", "author")
                super().__init__(metadata)
            
            def execute(self, input):
                return SkillOutput("normal result", {})
        
        skills = [ErrorSkill(), NormalSkill()]
        inputs = [SkillInput("data1"), SkillInput("data2")]
        
        outputs = parallel_executor.execute_skills_parallel(skills, inputs)
        
        assert len(outputs) == 2
        # First output should contain error information
        assert "error" in outputs[0].metadata
        # Second output should be normal result
        assert outputs[1].result == "normal result"
    
    def test_execute_with_mismatched_inputs(self, parallel_executor):
        """Test executing skills with mismatched inputs."""
        skills = [Mock(), Mock()]
        inputs = [SkillInput("data1")]  # Only one input for two skills
        
        with pytest.raises(ValueError):
            parallel_executor.execute_skills_parallel(skills, inputs)
    
    def test_shutdown(self, parallel_executor):
        """Test shutting down the executor."""
        # This should not raise an exception
        parallel_executor.shutdown()
    
    def test_execute_skills_empty_lists(self, parallel_executor):
        """Test executing with empty skill and input lists."""
        outputs = parallel_executor.execute_skills_parallel([], [])
        assert outputs == []