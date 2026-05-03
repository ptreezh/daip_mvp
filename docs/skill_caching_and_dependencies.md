# Skill Caching and Dependency Management

## Overview

The DAIP-LIVE Skills system now includes powerful caching and dependency management features to improve performance and enable complex skill chains.

## Features

### 1. Skill Execution Caching

Skill execution caching stores the results of skill executions to avoid redundant computations for identical inputs.

#### Benefits
- **Performance**: Avoid re-executing skills with the same input
- **Reduced API calls**: Minimize external API usage
- **Consistency**: Same input always produces same cached output
- **Configurable**: Enable/disable caching per execution

#### Key Components

**SkillCache Class**
- LRU (Least Recently Used) eviction policy
- TTL (Time To Live) support for automatic expiration
- Cache statistics tracking (hits, misses, hit rate)
- Manual invalidation support

**CacheEntry Structure**
```python
@dataclass
class CacheEntry:
    output: SkillOutput          # Cached result
    skill_name: str              # Name of the skill
    timestamp: float             # When the entry was created
    access_count: int            # Number of times accessed
    last_access: float           # Last access timestamp
```

#### Usage Examples

**Basic Caching**
```python
from daip_live.skills import SkillManager, SkillInput

# Create manager with caching enabled
manager = SkillManager(
    enable_cache=True,
    cache_max_size=100,         # Max 100 entries
    cache_default_ttl=300.0       # 5 minute TTL
)

# Execute with caching
input_data = SkillInput(data="process this text")
result = manager.execute("summarization", input_data, use_cache=True)

# Same input will hit cache
result2 = manager.execute("summarization", input_data, use_cache=True)
```

**Cache Management**
```python
# Get cache statistics
stats = manager.get_cache().statistics
print(f"Hit rate: {stats.hit_rate:.2%}")
print(f"Hits: {stats.hits}, Misses: {stats.misses}")

# Invalidate specific skill cache
manager.invalidate_skill_cache("summarization")

# Invalidate all cache
manager.clear_all_cache()

# Clean up expired entries
expired_count = manager.cleanup_expired_cache()
```

**TTL Configuration**
```python
# Per-execution TTL override
result = manager.execute(
    "summarization",
    input_data,
    use_cache=True,
    cache_ttl=60.0  # 1 minute TTL for this execution
)

# No TTL (cache never expires)
manager_no_ttl = SkillManager(
    enable_cache=True,
    cache_default_ttl=None
)
```

#### Cache Key Generation

Cache keys are generated deterministically from:
1. Skill name
2. Input data
3. Input context
4. Input metadata

```python
cache_key = hashlib.md5(f"{skill_name}:{input_str}").hexdigest()
```

#### Cache Statistics

Track cache performance with detailed metrics:

```python
@dataclass
class CacheStatistics:
    hits: int              # Number of cache hits
    misses: int            # Number of cache misses
    evictions: int         # Number of entries evicted
    total_entries: int      # Current number of cached entries

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
```

### 2. Skill Dependency Management

Skill dependencies allow skills to declare which other skills they require, enabling automatic dependency resolution and execution ordering.

#### Benefits
- **Automatic Resolution**: Dependencies are automatically executed in correct order
- **Validation**: Detect missing or circular dependencies
- **Safety**: Prevent execution when dependencies are unavailable
- **Flexibility**: Support for complex skill chains

#### Declaring Dependencies

Skills declare dependencies in their metadata:

```python
from daip_live.skills.base import Skill, SkillMetadata, SkillInput, SkillOutput

class AdvancedSummary(Skill):
    def __init__(self):
        metadata = SkillMetadata(
            name="advanced_summary",
            description="Advanced summarization with preprocessing",
            version="1.0",
            author="DAIP-LIVE",
            tags=["summarization", "text"],
            dependencies=["preprocess", "summarization"]  # Declares dependencies
        )
        super().__init__(metadata)

    def execute(self, input: SkillInput) -> SkillOutput:
        # This skill depends on preprocess and summarization
        return SkillOutput(
            result="Advanced summary result",
            metadata={"processed": True}
        )
```

#### Dependency Graph

The system maintains a dependency graph to manage relationships:

**SkillDependencyGraph Features**
- Build dependency graph from skill metadata
- Detect circular dependencies
- Topological sort for execution order
- Get dependents of a skill
- Validate all dependencies

#### Usage Examples

**Validate Dependencies**
```python
# Check if all dependencies are valid
validation = manager.validate_dependencies()

if validation.status == DependencyStatus.VALID:
    print("All dependencies are valid!")
    print(f"Execution order: {validation.execution_order}")
elif validation.status == DependencyStatus.MISSING_DEPENDENCY:
    print(f"Missing dependencies: {validation.missing_dependencies}")
elif validation.status == DependencyStatus.CIRCULAR_DEPENDENCY:
    print(f"Circular dependency: {' -> '.join(validation.circular_path)}")
```

**Get Execution Order**
```python
# Get correct execution order for a skill and its dependencies
order = manager.get_execution_order("advanced_summary")
print(order)  # ['preprocess', 'summarization', 'advanced_summary']
```

**Check Can Execute**
```python
# Check if a skill can be executed
if manager.can_execute("advanced_summary"):
    result = manager.execute("advanced_summary", input_data)
else:
    print("Cannot execute - missing or disabled dependencies")
```

### 3. Skill Chaining

Execute a skill and all its dependencies in the correct order.

#### Basic Chaining

```python
# Execute skill and all dependencies
results = manager.execute_chain(
    skill_name="advanced_summary",
    input=input_data,
    use_cache=True  # Optional: use cached results
)

# Results contains all executed skills
for skill_name, output in results.items():
    print(f"{skill_name}: {output.result}")
```

#### Chaining with Failure Handling

```python
# Stop on first failure
results = manager.execute_chain(
    "advanced_summary",
    input_data,
    stop_on_failure=True
)

# Continue despite failures
results = manager.execute_chain(
    "advanced_summary",
    input_data,
    stop_on_failure=False,
    require_all_dependencies=False  # Don't require all dependencies
)
```

#### Output Transform Chaining

Pass the output of one skill as input to the next:

```python
def transform_output(output: SkillOutput) -> SkillInput:
    """Transform output into input for next skill."""
    return SkillInput(
        data=output.result,
        context=output.metadata
    )

# Execute chain with output transformation
results = manager.execute_chain_with_output_transform(
    skill_name="final_analysis",
    initial_input=input_data,
    output_transform=transform_output,
    use_cache=True
)
```

#### Dependency Graph API

```python
graph = manager.get_dependency_graph()

# Get dependencies of a skill
deps = graph.get_dependencies("advanced_summary")
print(deps)  # {'preprocess', 'summarization'}

# Get dependents of a skill
dependents = graph.get_dependents("preprocess")
print(dependents)  # {'advanced_summary', 'other_skills...'}

# Detect circular dependencies
cycles = graph.detect_circular_dependencies()
if cycles:
    print(f"Circular dependencies found: {cycles}")

# Topological sort
order = graph.topological_sort()
print(order)  # Correct execution order
```

## Best Practices

### Caching

1. **Use Appropriate TTL**: Set TTL based on how often data changes
   - Static data: Longer TTL or no TTL
   - Dynamic data: Shorter TTL

2. **Monitor Hit Rate**: Track cache statistics to optimize TTL and size
   ```python
   stats = manager.get_cache().statistics
   if stats.hit_rate < 0.5:
       # Consider adjusting TTL or cache size
       pass
   ```

3. **Selective Caching**: Disable caching for stateful operations
   ```python
   # Don't cache operations that have side effects
   result = manager.execute("write_to_db", input_data, use_cache=False)
   ```

4. **Regular Cleanup**: Periodically clean up expired entries
   ```python
   import time
   while True:
       time.sleep(300)  # Every 5 minutes
       manager.cleanup_expired_cache()
   ```

### Dependencies

1. **Keep Dependencies Minimal**: Only declare essential dependencies
   ```python
   # Good: Minimal dependencies
   dependencies=["core_processor"]

   # Bad: Unnecessary dependencies
   dependencies=["core_processor", "helper_a", "helper_b", "helper_c"]
   ```

2. **Avoid Circular Dependencies**: Ensure dependency graph is a DAG
   ```python
   # Bad: Circular dependency
   class SkillA(Skill):
       dependencies=["skill_b"]

   class SkillB(Skill):
       dependencies=["skill_a"]  # Circular!
   ```

3. **Validate Before Use**: Always validate dependencies
   ```python
   validation = manager.validate_dependencies()
   if validation.status != DependencyStatus.VALID:
       raise ValueError("Invalid dependency configuration")
   ```

4. **Enable/Disable Carefully**: Be aware of dependencies when disabling skills
   ```python
   # Check what depends on a skill before disabling
   graph = manager.get_dependency_graph()
   dependents = graph.get_dependents("preprocess")
   if dependents:
       print(f"Warning: {dependents} depend on 'preprocess'")
   ```

### Chaining

1. **Understand Execution Order**: Dependencies execute first
   ```python
   order = manager.get_execution_order("final_skill")
   print(order)  # Check order before executing
   ```

2. **Handle Failures Gracefully**: Decide whether to stop or continue
   ```python
   # Strict mode: stop on first failure
   results = manager.execute_chain("complex_task", input, stop_on_failure=True)

   # Lenient mode: continue despite failures
   results = manager.execute_chain("complex_task", input, stop_on_failure=False)
   ```

3. **Use Caching**: Leverage cache for repeated chain executions
   ```python
   # First execution
   results1 = manager.execute_chain("complex_task", input, use_cache=True)

   # Second execution will be faster (from cache)
   results2 = manager.execute_chain("complex_task", input, use_cache=True)
   ```

## API Reference

### SkillCache

```python
class SkillCache:
    def __init__(
        self,
        max_size: int = 100,
        default_ttl: Optional[float] = None,
        enabled: bool = True
    )

    def get(
        self,
        skill_name: str,
        input: SkillInput,
        ttl: Optional[float] = None
    ) -> Optional[SkillOutput]

    def put(
        self,
        skill_name: str,
        input: SkillInput,
        output: SkillOutput,
        ttl: Optional[float] = None
    ) -> None

    def invalidate(
        self,
        skill_name: str,
        input: Optional[SkillInput] = None
    ) -> int

    def clear(self) -> None
    def cleanup_expired(self, ttl: Optional[float] = None) -> int

    @property
    def enabled(self) -> bool
    @property
    def size(self) -> int
    @property
    def statistics(self) -> CacheStatistics
```

### SkillManager (Caching Methods)

```python
class SkillManager:
    def __init__(
        self,
        enable_cache: bool = True,
        cache_max_size: int = 100,
        cache_default_ttl: Optional[float] = None
    )

    def execute(
        self,
        skill_name: str,
        input: SkillInput,
        use_cache: bool = True,
        cache_ttl: Optional[float] = None
    ) -> SkillOutput

    def get_cache(self) -> SkillCache
    def invalidate_skill_cache(
        self,
        skill_name: str,
        input: Optional[SkillInput] = None
    ) -> int
    def clear_all_cache(self) -> None
    def cleanup_expired_cache(self) -> int
```

### SkillManager (Dependency Methods)

```python
class SkillManager:
    def validate_dependencies(
        self,
        enabled_skills: Optional[Set[str]] = None
    ) -> DependencyValidationResult

    def get_dependency_graph(self) -> SkillDependencyGraph
    def get_execution_order(self, skill_name: str) -> List[str]
    def can_execute(self, skill_name: str) -> bool

    def execute_chain(
        self,
        skill_name: str,
        input: SkillInput,
        stop_on_failure: bool = False,
        use_cache: bool = True,
        require_all_dependencies: bool = True
    ) -> Dict[str, SkillOutput]

    def execute_chain_with_output_transform(
        self,
        skill_name: str,
        initial_input: SkillInput,
        output_transform: Optional[Callable],
        stop_on_failure: bool = False,
        use_cache: bool = True
    ) -> Dict[str, SkillOutput]
```

### SkillDependencyGraph

```python
class SkillDependencyGraph:
    def build_graph(self, skills_metadata: Dict[str, SkillMetadata]) -> None
    def add_skill(self, skill_name: str, dependencies: List[str]) -> None
    def remove_skill(self, skill_name: str) -> None

    def get_dependencies(self, skill_name: str) -> Set[str]
    def get_dependents(self, skill_name: str) -> Set[str]

    def detect_circular_dependencies(self) -> List[List[str]]
    def topological_sort(self) -> List[str]

    def validate_dependencies(
        self,
        skills_metadata: Dict[str, SkillMetadata],
        enabled_skills: Optional[Set[str]] = None
    ) -> DependencyValidationResult

    def get_execution_order(self, skill_name: str) -> List[str]
    def can_execute(self, skill_name: str, enabled_skills: Set[str]) -> bool
```

## Examples

### Example 1: Basic Caching

```python
from daip_live.skills import SkillManager, SkillInput

manager = SkillManager(enable_cache=True, cache_default_ttl=300.0)

input_data = SkillInput(data="Hello world")
result1 = manager.execute("summarization", input_data)
result2 = manager.execute("summarization", input_data)  # Cache hit

print(f"Cache hit rate: {manager.get_cache().statistics.hit_rate:.2%}")
```

### Example 2: Complex Dependency Chain

```python
# Define skills with dependencies
manager.register_skill(TextPreprocessor())      # No dependencies
manager.register_skill(Summarizer())             # deps: ["text_preprocessor"]
manager.register_skill(Translator())               # deps: ["summarizer"]
manager.register_skill(Publisher())                # deps: ["translator"]

# Validate dependencies
validation = manager.validate_dependencies()
if validation.status != DependencyStatus.VALID:
    print(f"Dependency error: {validation.message}")
    exit(1)

# Execute the entire chain
results = manager.execute_chain("publisher", initial_input)
for skill, output in results.items():
    print(f"{skill}: {output.result[:50]}...")
```

### Example 3: Cache Management

```python
manager = SkillManager(enable_cache=True)

# Execute skills
for i in range(100):
    input_data = SkillInput(data=f"item_{i % 10}")  # 10 unique inputs
    manager.execute("summarization", input_data)

# Check statistics
stats = manager.get_cache().statistics
print(f"Total executions: 100")
print(f"Cache hits: {stats.hits}")
print(f"Cache misses: {stats.misses}")
print(f"Hit rate: {stats.hit_rate:.2%}")

# Clean up old entries
expired = manager.cleanup_expired_cache()
print(f"Removed {expired} expired entries")
```

### Example 4: Failure Handling in Chains

```python
manager = SkillManager(enable_cache=True)

# Execute with failure handling
try:
    results = manager.execute_chain(
        "complex_task",
        input_data,
        stop_on_failure=False,
        require_all_dependencies=False
    )

    # Check which skills failed
    executed = set(results.keys())
    all_skills = set(manager.get_execution_order("complex_task"))
    failed = all_skills - executed

    if failed:
        print(f"Failed skills: {failed}")
        print(f"Successful: {executed}")

except Exception as e:
    print(f"Chain execution error: {e}")
```

## Performance Considerations

### Caching Performance

- **Cache Size**: Larger cache = higher hit rate but more memory usage
- **TTL**: Shorter TTL = more frequent cache misses but fresher data
- **Key Generation**: MD5 hashing is fast but adds small overhead
- **LRU Eviction**: O(1) operations using OrderedDict

### Dependency Resolution Performance

- **Graph Building**: O(V + E) where V = vertices, E = edges
- **Circular Detection**: O(V + E) using DFS
- **Topological Sort**: O(V + E) using Kahn's algorithm
- **Validation**: Combines all above operations

### Recommendations

1. Start with cache size of 100-500 entries
2. Set TTL based on data freshness requirements
3. Keep dependency graphs shallow (3-4 levels max)
4. Use caching for expensive operations
5. Monitor cache hit rates and adjust accordingly

## Troubleshooting

### Low Cache Hit Rate

**Symptom**: Cache hit rate < 50%

**Solutions**:
- Check if inputs vary too much (consider normalization)
- Increase cache TTL
- Increase cache size
- Check if caching is actually enabled

### Circular Dependency Errors

**Symptom**: `DependencyStatus.CIRCULAR_DEPENDENCY`

**Solutions**:
- Review skill dependencies
- Remove circular references
- Refactor to avoid mutual dependencies

### Cache Not Working

**Symptom**: Every execution is a cache miss

**Solutions**:
- Check `enable_cache` parameter
- Verify TTL isn't too short
- Check input data - small variations create different cache keys
- Look for cache invalidation calls

### Chain Execution Fails

**Symptom**: Skills in chain don't execute

**Solutions**:
- Check dependencies are enabled
- Verify dependencies are registered
- Use `require_all_dependencies=False` for partial execution
- Check logs for specific error messages
