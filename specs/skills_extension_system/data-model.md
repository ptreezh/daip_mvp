# Data Models: Skills Extension System

**Date**: 2025-11-19
**Feature**: specs/skills_extension_system/spec.md
**Status**: Designed and Implemented
**Model Focus**: Skill interfaces, data transfer objects, and communication models

## Core Skill Models

### SkillMetadata

```python
@dataclass
class SkillMetadata:
    """
    Defines metadata for a skill including description, tags, and dependencies.
    
    Follows dataclass pattern from Python standard library for clean data modeling.
    """
    name: str = Field(description="Unique identifier for the skill")
    description: str = Field(description="Human-readable description of what the skill does")
    version: str = Field(description="Semantic version of the skill", default="1.0.0")
    author: str = Field(description="Creator of the skill", default="Anonymous")
    tags: List[str] = Field(description="Keywords to help with skill discovery", default_factory=list)
    dependencies: List[str] = Field(description="Other skills this skill depends on", default_factory=list)
    created_at: datetime = Field(description="Timestamp when skill was created", default_factory=datetime.now)
    updated_at: datetime = Field(description="Timestamp when skill was last updated", default_factory=datetime.now)
```

### SkillInput and SkillOutput

```python
@dataclass
class SkillInput:
    """
    Standardized input format for all skills.
    
    Follows dataclass pattern for lightweight data transfer objects.
    """
    data: str = Field(description="Main input data for the skill")
    context: Dict[str, Any] = Field(description="Context information for the skill", default_factory=dict)
    metadata: Dict[str, Any] = Field(description="Additional metadata for execution", default_factory=dict)


@dataclass
class SkillOutput:
    """
    Standardized output format for all skills.
    
    Follows dataclass pattern for consistent skill results.
    """
    result: str = Field(description="Main result of skill execution")
    metadata: Dict[str, Any] = Field(description="Additional output metadata", default_factory=dict)
    confidence: float = Field(description="Confidence level in result (0.0-1.0)", default=1.0)
    execution_time: float = Field(description="Execution time in seconds", default=0.0)
    success: bool = Field(description="Whether skill execution was successful", default=True)
    error_message: Optional[str] = Field(description="Error message if execution failed", default=None)
```

## Skill Base Classes

### Skill Abstract Base Class

```python
class Skill(ABC):
    """
    Abstract base class for all skills in the system.
    
    Defines the standard interface that all skills must implement.
    """
    metadata: SkillMetadata
    is_enabled: bool

    @abstractmethod
    def execute(self, input: SkillInput) -> SkillOutput:
        """
        Execute the skill with the provided input.
        
        Args:
            input: SkillInput containing the data and context
            
        Returns:
            SkillOutput containing the result and metadata
        """
        pass

    def validate_input(self, input: SkillInput) -> bool:
        """
        Validate the input before execution.
        
        Args:
            input: SkillInput to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        return True

    def enable(self) -> None:
        """Enable the skill for execution."""
        self.is_enabled = True

    def disable(self) -> None:
        """Disable the skill from execution."""
        self.is_enabled = False
```

## Skill Management Models

### KnowledgeBaseChanges for Skills

```python
@dataclass
class SkillChanges:
    """
    Tracks changes to the skill system for sync operations.
    """
    added: List[str] = Field(description="Names of newly added skills", default_factory=list)
    removed: List[str] = Field(description="Names of removed skills", default_factory=list)
    updated: List[str] = Field(description="Names of updated skills", default_factory=list)
    unchanged: List[str] = Field(description="Names of unchanged skills", default_factory=list)
    scan_time: float = Field(description="Time taken to scan for changes", default=0.0)
    error_skills: List[Tuple[str, str]] = Field(description="Skills that failed loading with error messages", default_factory=list)
```

### SkillRegistry

```python
@dataclass 
class SkillRegistry:
    """
    Registry model for tracking all registered skills.
    """
    skills: Dict[str, SkillMetadata] = Field(description="Mapping of skill names to their metadata", default_factory=dict)
    categories: Dict[str, List[str]] = Field(description="Skills organized by category/tag", default_factory=dict)
    dependencies_graph: Dict[str, List[str]] = Field(description="Dependency relationships between skills", default_factory=dict)
    last_sync_time: datetime = Field(description="Last time the registry was synchronized", default_factory=datetime.now)
    total_skills: int = Field(description="Total number of registered skills", default=0)
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the registry."""
        self.skills[skill.metadata.name] = skill.metadata
        self.total_skills += 1
        
        # Update categories
        for tag in skill.metadata.tags:
            if tag not in self.categories:
                self.categories[tag] = []
            self.categories[tag].append(skill.metadata.name)
    
    def find_skills_by_tag(self, tag: str) -> List[str]:
        """Find all skills that have a specific tag."""
        return self.categories.get(tag, [])
    
    def get_skill_dependencies(self, skill_name: str) -> List[str]:
        """Get dependencies for a specific skill."""
        return self.dependencies_graph.get(skill_name, [])
```

## Communication Event Models

### SkillExecutionEvent

```python
class SkillExecutionEvent(BaseModel):
    """
    Event fired when a skill is executed.
    
    Follows Pydantic BaseModel pattern from core/models.py for event-driven communication.
    """
    type: Literal["skill_execution"] = "skill_execution"
    skill_name: str = Field(description="Name of the skill being executed")
    input_data: str = Field(description="Input provided to the skill")
    session_id: str = Field(description="Session identifier")
    start_time: datetime = Field(description="When execution started", default_factory=datetime.now)
    success: bool = Field(description="Whether execution was successful", default=True)
    result: Optional[str] = Field(description="Result of skill execution", default=None)
    execution_time: Optional[float] = Field(description="Execution time in seconds", default=None)
    error_message: Optional[str] = Field(description="Error message if execution failed", default=None)
```

### SkillRegistrationEvent

```python
class SkillRegistrationEvent(BaseModel):
    """
    Event fired when a skill is registered or unregistered.
    
    Follows Pydantic BaseModel pattern for event-driven communication.
    """
    type: Literal["skill_registration"] = "skill_registration"
    skill_name: str = Field(description="Name of the skill")
    action: Literal["register", "unregister"] = Field(description="Action performed")
    skill_metadata: SkillMetadata = Field(description="Metadata of the skill")
    timestamp: datetime = Field(description="When the event occurred", default_factory=datetime.now)
```

### SkillDiscoveryEvent

```python
class SkillDiscoveryEvent(BaseModel):
    """
    Event fired when skills are discovered or searched.
    
    Follows Pydantic BaseModel pattern for event-driven communication.
    """
    type: Literal["skill_discovery"] = "skill_discovery"
    query: str = Field(description="Search query used for discovery")
    results: List[SkillMetadata] = Field(description="Matching skill metadata", default_factory=list)
    tags_filter: Optional[List[str]] = Field(description="Tags used for filtering", default=None)
    session_id: str = Field(description="Session identifier")
    discovery_time: float = Field(description="Time taken for discovery", default=0.0)
    timestamp: datetime = Field(description="When the event occurred", default_factory=datetime.now)
```

## Integration Models

### SkillIntegrationRequest

```python
class SkillIntegrationRequest(BaseModel):
    """
    Request model for integrating skills with intent recognition.
    
    Follows Pydantic BaseModel pattern for structured requests.
    """
    intent_name: str = Field(description="Name of the recognized intent")
    skill_candidates: List[str] = Field(description="Skills that could satisfy the intent", default_factory=list)
    context: Dict[str, Any] = Field(description="Context for skill selection", default_factory=dict)
    required_parameters: List[str] = Field(description="Parameters needed for skill execution", default_factory=list)
    confidence_threshold: float = Field(description="Minimum confidence to execute skill", default=0.7)
```

### SkillIntegrationResponse

```python
class SkillIntegrationResponse(BaseModel):
    """
    Response model for skill-intent integration results.
    
    Follows Pydantic BaseModel pattern for structured responses.
    """
    skill_selected: Optional[str] = Field(description="Skill selected for execution", default=None)
    parameters_extracted: Dict[str, Any] = Field(description="Parameters extracted for skill", default_factory=dict)
    confidence: float = Field(description="Confidence in skill selection", default=0.0)
    requires_clarification: bool = Field(description="Whether additional information is needed", default=False)
    clarification_message: Optional[str] = Field(description="Message for user clarification", default=None)
    execution_result: Optional[SkillOutput] = Field(description="Result of skill execution", default=None)
    success: bool = Field(description="Whether integration was successful", default=True)
    processed_time: float = Field(description="Time taken to process integration", default=0.0)
```

## Model Relationships

### System Integration
- SkillMetadata integrated with all skill implementations
- SkillInput/SkillOutput used by SkillManager for standard I/O
- Events connect skills with other system components via event-driven architecture
- SkillRegistry enables discovery and dependency management

### Validation Rules
- All models follow appropriate validation patterns (Pydantic for event models, dataclass for internal models)
- Required fields ensure essential parameters are present
- Default values provide sensible fallbacks for optional parameters
- Type hints enable IDE support and static analysis

## Serialization Patterns

### JSON Serialization
- All Pydantic models support automatic JSON serialization/deserialization
- SkillMetadata supports serialization for storage and transmission
- Events support serialization for persistence and logging

### Data Transfer
- Skill input/output optimized for minimal serialization overhead
- Metadata stored for efficient skill discovery and search
- Dependencies tracked for execution ordering and validation

## Extensibility Considerations

### New Skill Types
- Skill base class allows easy extension with new skill types
- Standard input/output models ensure consistency across skill implementations
- Metadata system enables discovery of new skill types

### Integration Points
- Skill events provide hooks for external system integration
- Registry model supports advanced skill management features
- Integration models enable AI systems to use skills programmatically