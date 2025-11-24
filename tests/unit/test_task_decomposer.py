"""
Unit tests for the task decomposer.
"""
import pytest
from src.daip_live.orchestration.decomposer import TaskDecomposer, TaskType, Subtask, DecomposedTask


class TestTaskDecomposer:
    """Test cases for the TaskDecomposer class."""
    
    @pytest.fixture
    def task_decomposer(self):
        """Create a TaskDecomposer instance for testing."""
        return TaskDecomposer()
    
    def test_decompose_simple_task(self, task_decomposer):
        """Test decomposing a simple task."""
        task = "Analyze social network data using grounded theory approach"
        result = task_decomposer.decompose(task)
        
        assert isinstance(result, DecomposedTask)
        assert result.original_task == task
        assert len(result.subtasks) > 0
        assert isinstance(result.dependencies, dict)
    
    def test_decompose_chinese_task(self, task_decomposer):
        """Test decomposing a Chinese task."""
        task = "使用扎根理论分析社会网络数据"
        result = task_decomposer.decompose(task)
        
        assert isinstance(result, DecomposedTask)
        assert result.original_task == task
        assert len(result.subtasks) > 0
    
    def test_decompose_task_with_context(self, task_decomposer):
        """Test decomposing a task with context."""
        task = "Analyze qualitative interview data"
        context = {"domain": "education", "language": "chinese"}
        result = task_decomposer.decompose(task, context)
        
        assert isinstance(result, DecomposedTask)
        assert result.original_task == task
        assert result.subtasks is not None
    
    def test_subtask_creation(self):
        """Test Subtask creation."""
        subtask = Subtask(
            id="test_1",
            description="Test subtask",
            task_type=TaskType.ANALYSIS,
            domain="test_domain",
            required_skills=["skill1", "skill2"],
            dependencies=["dep1", "dep2"],
            priority=2,
            metadata={"key": "value"}
        )
        
        assert subtask.id == "test_1"
        assert subtask.description == "Test subtask"
        assert subtask.task_type == TaskType.ANALYSIS
        assert subtask.domain == "test_domain"
        assert subtask.required_skills == ["skill1", "skill2"]
        assert subtask.dependencies == ["dep1", "dep2"]
        assert subtask.priority == 2
        assert subtask.metadata == {"key": "value"}
    
    def test_decomposed_task_creation(self):
        """Test DecomposedTask creation."""
        subtasks = [
            Subtask("1", "Test 1", TaskType.ANALYSIS, "domain1", [], []),
            Subtask("2", "Test 2", TaskType.SYNTHESIS, "domain2", [], [])
        ]
        dependencies = {"1": [], "2": ["1"]}
        
        decomposed_task = DecomposedTask(
            original_task="Test task",
            subtasks=subtasks,
            dependencies=dependencies
        )
        
        assert decomposed_task.original_task == "Test task"
        assert decomposed_task.subtasks == subtasks
        assert decomposed_task.dependencies == dependencies
    
    def test_domain_identification(self, task_decomposer):
        """Test domain identification in tasks."""
        # Test grounded theory keywords
        task1 = "Perform coding and category development on interview data"
        result1 = task_decomposer.decompose(task1)
        assert len(result1.subtasks) > 0
        
        # Test SNA keywords
        task2 = "Analyze social network relationships and connections"
        result2 = task_decomposer.decompose(task2)
        assert len(result2.subtasks) > 0
        
        # Test field analysis keywords
        task3 = "Examine academic field structures and capital distribution"
        result3 = task_decomposer.decompose(task3)
        assert len(result3.subtasks) > 0
    
    def test_empty_task_decomposition(self, task_decomposer):
        """Test decomposing an empty task."""
        task = ""
        result = task_decomposer.decompose(task)
        
        assert isinstance(result, DecomposedTask)
        assert result.original_task == ""
        # Should still create at least one default subtask
        assert len(result.subtasks) > 0