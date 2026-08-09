"""
Unit tests for skill caching and dependency management.
"""

import time

import pytest

from src.daip_live.skills.base import Skill, SkillInput, SkillMetadata, SkillOutput
from src.daip_live.skills.cache import SkillCache
from src.daip_live.skills.dependency import (
    DependencyStatus,
    SkillDependencyGraph,
)
from src.daip_live.skills.manager import SkillManager


class TestSkillCache:
    """Test cases for SkillCache."""

    @pytest.fixture
    def cache(self):
        """Create a SkillCache instance for testing."""
        return SkillCache(max_size=10, default_ttl=60.0, enabled=True)

    @pytest.fixture
    def skill_input(self):
        """Create a test skill input."""
        return SkillInput(data="test data", context={"key": "value"})

    @pytest.fixture
    def skill_output(self):
        """Create a test skill output."""
        return SkillOutput(
            result="test result",
            metadata={"info": "test"},
            confidence=0.9,
            execution_time=0.1,
        )

    def test_cache_get_put(self, cache, skill_input, skill_output):
        """Test basic cache get and put operations."""
        # Put an entry
        cache.put("test_skill", skill_input, skill_output)

        # Get it back
        result = cache.get("test_skill", skill_input)
        assert result is not None
        assert result.result == "test result"
        assert result.confidence == 0.9

    def test_cache_miss(self, cache, skill_input):
        """Test cache miss returns None."""
        result = cache.get("nonexistent_skill", skill_input)
        assert result is None

    def test_cache_disabled(self, cache, skill_input, skill_output):
        """Test cache when disabled."""
        cache.enabled = False

        # Put should do nothing
        cache.put("test_skill", skill_input, skill_output)

        # Get should return None
        result = cache.get("test_skill", skill_input)
        assert result is None

    def test_cache_ttl(self, cache, skill_input, skill_output):
        """Test cache TTL expiration."""
        # Put with short TTL
        cache.put("test_skill", skill_input, skill_output, ttl=0.5)

        # Should be available immediately
        result = cache.get("test_skill", skill_input, ttl=0.5)
        assert result is not None

        # Wait for expiration
        time.sleep(0.6)

        # Should be expired
        result = cache.get("test_skill", skill_input, ttl=0.5)
        assert result is None

    def test_cache_no_ttl(self, cache, skill_input, skill_output):
        """Test cache with no TTL (never expires)."""
        cache_no_ttl = SkillCache(max_size=10, default_ttl=None, enabled=True)

        # Put without TTL
        cache_no_ttl.put("test_skill", skill_input, skill_output)

        # Should be available regardless of time
        time.sleep(0.1)
        result = cache_no_ttl.get("test_skill", skill_input)
        assert result is not None

    def test_cache_lru_eviction(self, cache, skill_input, skill_output):
        """Test LRU eviction when max_size is exceeded."""
        # Fill cache to max size
        for i in range(12):  # 12 > max_size (10)
            input_i = SkillInput(data=f"data_{i}")
            output_i = SkillOutput(result=f"result_{i}")
            cache.put(f"skill_{i}", input_i, output_i)

        # Cache should only have 10 entries
        assert cache.size == 10

        # Oldest entries should be evicted
        # Access entries 2-11 to verify they exist
        found_entries = 0
        for i in range(2, 12):
            input_i = SkillInput(data=f"data_{i}")
            if cache.get(f"skill_{i}", input_i) is not None:
                found_entries += 1

        assert found_entries == 10

    def test_cache_statistics(self, cache, skill_input, skill_output):
        """Test cache statistics tracking."""
        # Initial stats
        stats = cache.statistics
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.hit_rate == 0.0

        # Put an entry
        cache.put("test_skill", skill_input, skill_output)

        # Hit
        cache.get("test_skill", skill_input)
        stats = cache.statistics
        assert stats.hits == 1
        assert stats.misses == 0

        # Miss
        cache.get("nonexistent", skill_input)
        stats = cache.statistics
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.hit_rate == 0.5

    def test_cache_invalidate(self, cache, skill_input, skill_output):
        """Test cache invalidation."""
        # Put multiple entries for the same skill
        cache.put("test_skill", skill_input, skill_output)
        input2 = SkillInput(data="different data")
        output2 = SkillOutput(result="different result")
        cache.put("test_skill", input2, output2)

        # Invalidate all entries for the skill
        invalidated = cache.invalidate("test_skill")
        assert invalidated > 0

        # Both entries should be gone
        assert cache.get("test_skill", skill_input) is None
        assert cache.get("test_skill", input2) is None

    def test_cache_invalidate_specific(self, cache, skill_input, skill_output):
        """Test cache invalidation of specific entry."""
        # Put multiple entries
        cache.put("test_skill", skill_input, skill_output)
        input2 = SkillInput(data="different data")
        output2 = SkillOutput(result="different result")
        cache.put("test_skill", input2, output2)

        # Invalidate specific entry
        invalidated = cache.invalidate("test_skill", skill_input)
        assert invalidated == 1

        # First entry should be gone, second should remain
        assert cache.get("test_skill", skill_input) is None
        assert cache.get("test_skill", input2) is not None

    def test_cache_clear(self, cache, skill_input, skill_output):
        """Test cache clear."""
        # Add entries
        for i in range(5):
            input_i = SkillInput(data=f"data_{i}")
            output_i = SkillOutput(result=f"result_{i}")
            cache.put(f"skill_{i}", input_i, output_i)

        assert cache.size > 0

        # Clear cache
        cache.clear()

        assert cache.size == 0

    def test_cache_cleanup_expired(self, cache, skill_input, skill_output):
        """Test cleanup of expired entries."""
        # Add entries with short TTL
        cache.put("skill_1", skill_input, skill_output, ttl=0.3)
        input2 = SkillInput(data="data_2")
        output2 = SkillOutput(result="result_2")
        cache.put("skill_2", input2, output2, ttl=0.3)

        # Wait for expiration
        time.sleep(0.4)

        # Cleanup expired
        removed = cache.cleanup_expired(ttl=0.3)
        assert removed == 2

        # Cache should be empty
        assert cache.size == 0


class TestSkillDependencyGraph:
    """Test cases for SkillDependencyGraph."""

    @pytest.fixture
    def graph(self):
        """Create a SkillDependencyGraph instance for testing."""
        return SkillDependencyGraph()

    def test_add_skill(self, graph):
        """Test adding a skill to the dependency graph."""
        graph.add_skill("skill_a", [])
        deps = graph.get_dependencies("skill_a")
        assert deps == set()

    def test_add_skill_with_dependencies(self, graph):
        """Test adding a skill with dependencies."""
        graph.add_skill("skill_b", ["skill_a"])
        deps = graph.get_dependencies("skill_b")
        assert deps == {"skill_a"}

    def test_get_dependents(self, graph):
        """Test getting dependents of a skill."""
        graph.add_skill("skill_a", [])
        graph.add_skill("skill_b", ["skill_a"])
        graph.add_skill("skill_c", ["skill_a"])

        dependents = graph.get_dependents("skill_a")
        assert dependents == {"skill_b", "skill_c"}

    def test_detect_no_circular_dependencies(self, graph):
        """Test detecting no circular dependencies in a DAG."""
        graph.add_skill("skill_a", [])
        graph.add_skill("skill_b", ["skill_a"])
        graph.add_skill("skill_c", ["skill_b"])

        cycles = graph.detect_circular_dependencies()
        assert len(cycles) == 0

    def test_detect_circular_dependencies(self, graph):
        """Test detecting circular dependencies."""
        graph.add_skill("skill_a", ["skill_b"])
        graph.add_skill("skill_b", ["skill_c"])
        graph.add_skill("skill_c", ["skill_a"])

        cycles = graph.detect_circular_dependencies()
        assert len(cycles) > 0
        assert "skill_a" in cycles[0]
        assert "skill_b" in cycles[0]
        assert "skill_c" in cycles[0]

    def test_topological_sort(self, graph):
        """Test topological sort."""
        graph.add_skill("skill_a", [])
        graph.add_skill("skill_b", ["skill_a"])
        graph.add_skill("skill_c", ["skill_b"])

        order = graph.topological_sort()
        assert len(order) == 3

        # Check dependencies come before dependents
        assert order.index("skill_a") < order.index("skill_b")
        assert order.index("skill_b") < order.index("skill_c")

    def test_topological_sort_with_cycles(self, graph):
        """Test topological sort returns empty list with cycles."""
        graph.add_skill("skill_a", ["skill_b"])
        graph.add_skill("skill_b", ["skill_a"])

        order = graph.topological_sort()
        assert order == []

    def test_get_execution_order(self, graph):
        """Test getting execution order for a skill."""
        graph.add_skill("skill_a", [])
        graph.add_skill("skill_b", ["skill_a"])
        graph.add_skill("skill_c", ["skill_b"])

        order = graph.get_execution_order("skill_c")
        assert len(order) == 3
        assert order[0] == "skill_a"
        assert order[1] == "skill_b"
        assert order[2] == "skill_c"

    def test_can_execute(self, graph):
        """Test checking if a skill can be executed."""
        graph.add_skill("skill_a", [])
        graph.add_skill("skill_b", ["skill_a"])

        # Can execute if all dependencies are enabled
        enabled_skills = {"skill_a", "skill_b"}
        assert graph.can_execute("skill_b", enabled_skills) is True

        # Cannot execute if dependency is disabled
        enabled_skills = {"skill_b"}
        assert graph.can_execute("skill_b", enabled_skills) is False

    def test_validate_dependencies_missing(self, graph):
        """Test validation with missing dependencies."""
        metadata = {
            "skill_a": SkillMetadata("skill_a", "test", "1.0", "author", [], []),
            "skill_b": SkillMetadata(
                "skill_b", "test", "1.0", "author", [], ["nonexistent"]
            ),
        }

        result = graph.validate_dependencies(metadata)
        assert result.status == DependencyStatus.MISSING_DEPENDENCY
        assert len(result.missing_dependencies) > 0

    def test_validate_dependencies_circular(self, graph):
        """Test validation with circular dependencies."""
        metadata = {
            "skill_a": SkillMetadata(
                "skill_a", "test", "1.0", "author", [], ["skill_b"]
            ),
            "skill_b": SkillMetadata(
                "skill_b", "test", "1.0", "author", [], ["skill_a"]
            ),
        }

        result = graph.validate_dependencies(metadata)
        assert result.status == DependencyStatus.CIRCULAR_DEPENDENCY
        assert len(result.circular_path) > 0

    def test_validate_dependencies_valid(self, graph):
        """Test validation with valid dependencies."""
        metadata = {
            "skill_a": SkillMetadata("skill_a", "test", "1.0", "author", [], []),
            "skill_b": SkillMetadata(
                "skill_b", "test", "1.0", "author", [], ["skill_a"]
            ),
        }

        result = graph.validate_dependencies(metadata)
        assert result.status == DependencyStatus.VALID
        assert len(result.execution_order) == 2


class TestSkillManagerCachingAndDependency:
    """Test cases for SkillManager caching and dependency features."""

    @pytest.fixture
    def skill_manager(self):
        """Create a SkillManager instance with caching enabled."""
        return SkillManager(enable_cache=True, cache_max_size=10)

    @pytest.fixture
    def sample_skills(self, skill_manager):
        """Register sample skills for testing."""

        class SkillA(Skill):
            def __init__(self):
                super().__init__(
                    SkillMetadata(
                        name="skill_a",
                        description="Test skill A",
                        version="1.0",
                        author="test",
                        tags=["test"],
                        dependencies=[],
                    )
                )

            def execute(self, input):
                return SkillOutput(
                    result=f"Skill A executed with: {input.data}",
                    metadata={"skill": "A"},
                )

        class SkillB(Skill):
            def __init__(self):
                super().__init__(
                    SkillMetadata(
                        name="skill_b",
                        description="Test skill B",
                        version="1.0",
                        author="test",
                        tags=["test"],
                        dependencies=["skill_a"],
                    )
                )

            def execute(self, input):
                return SkillOutput(
                    result=f"Skill B executed with: {input.data}",
                    metadata={"skill": "B"},
                )

        skill_manager.register_skill(SkillA())
        skill_manager.register_skill(SkillB())

        return skill_manager

    def test_execute_with_cache(self, sample_skills):
        """Test skill execution with caching."""
        skill_input = SkillInput(data="test data")

        # First execution
        result1 = sample_skills.execute("skill_a", skill_input, use_cache=True)
        assert result1 is not None

        # Second execution should hit cache
        result2 = sample_skills.execute("skill_a", skill_input, use_cache=True)
        assert result2 is not None
        assert result2.result == result1.result

        # Verify cache statistics
        cache_stats = sample_skills.get_cache().statistics
        assert cache_stats.hits >= 1

    def test_execute_without_cache(self, sample_skills):
        """Test skill execution without caching."""
        skill_input = SkillInput(data="test data")

        # Execute without cache
        result = sample_skills.execute("skill_a", skill_input, use_cache=False)

        assert result is not None
        assert "Skill A executed" in result.result

    def test_validate_dependencies(self, sample_skills):
        """Test dependency validation."""
        result = sample_skills.validate_dependencies()

        assert result.status == DependencyStatus.VALID
        assert "skill_a" in result.execution_order
        assert "skill_b" in result.execution_order

    def test_get_execution_order(self, sample_skills):
        """Test getting execution order."""
        order = sample_skills.get_execution_order("skill_b")

        assert len(order) == 2
        assert order[0] == "skill_a"  # Dependency comes first
        assert order[1] == "skill_b"

    def test_can_execute(self, sample_skills):
        """Test checking if skill can execute."""
        assert sample_skills.can_execute("skill_b") is True

        # Disable dependency
        sample_skills.get_skill("skill_a").disable()

        assert sample_skills.can_execute("skill_b") is False

    def test_execute_chain(self, sample_skills):
        """Test executing skill chain."""
        skill_input = SkillInput(data="test data")

        results = sample_skills.execute_chain("skill_b", skill_input)

        assert "skill_a" in results
        assert "skill_b" in results

    def test_execute_chain_with_failure(self, sample_skills):
        """Test executing chain with stop on failure."""
        # Disable a skill to cause failure
        sample_skills.get_skill("skill_a").disable()

        skill_input = SkillInput(data="test data")

        # Should not raise error when require_all_dependencies=False, but return partial results  # noqa: E501
        results = sample_skills.execute_chain(
            "skill_b",
            skill_input,
            stop_on_failure=False,
            require_all_dependencies=False,
        )

        # Should have empty or partial results (skill_a is disabled)
        assert "skill_a" not in results
        assert "skill_b" not in results  # Can't execute because dependency is missing

    def test_invalidate_skill_cache(self, sample_skills):
        """Test invalidating skill cache."""
        skill_input = SkillInput(data="test data")

        # Execute to populate cache (first time = miss)
        sample_skills.execute("skill_a", skill_input, use_cache=True)

        # Get stats before invalidation
        cache = sample_skills.get_cache()
        hits_before = cache.statistics.hits

        # Execute again (should hit cache)
        result = sample_skills.execute("skill_a", skill_input, use_cache=True)
        assert result is not None

        # Verify we got a hit
        hits_after_second = cache.statistics.hits
        assert hits_after_second > hits_before

        # Invalidate cache
        invalidated = sample_skills.invalidate_skill_cache("skill_a")
        assert invalidated > 0

        # Execute again after invalidation (should miss)
        misses_after_invalidation = cache.statistics.misses
        result = sample_skills.execute("skill_a", skill_input, use_cache=True)
        misses_final = cache.statistics.misses

        # New execution should have increased misses
        assert misses_final > misses_after_invalidation

    def test_clear_all_cache(self, sample_skills):
        """Test clearing all cache."""
        skill_input = SkillInput(data="test data")

        # Execute multiple skills
        sample_skills.execute("skill_a", skill_input, use_cache=True)
        sample_skills.execute("skill_b", skill_input, use_cache=True)

        # Clear all cache
        sample_skills.clear_all_cache()

        cache = sample_skills.get_cache()
        assert cache.size == 0

    def test_get_cache_statistics(self, sample_skills):
        """Test getting cache statistics."""
        cache_stats = sample_skills.get_cache().statistics

        assert cache_stats is not None
        assert cache_stats.hits == 0
        assert cache_stats.misses == 0
