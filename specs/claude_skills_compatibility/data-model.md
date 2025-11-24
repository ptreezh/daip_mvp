# Data Models: Claude Skills Format Compatibility

**Date**: 2025-11-19
**Feature**: specs/claude_skills_compatibility/spec.md
**Status**: Designed
**Model Focus**: Claude Skills format models and integration interfaces

## Claude Skills Format Models

### ClaudeSkillManifest
```python
class ClaudeSkillManifest(BaseModel):
    """
    Claude Skills manifest model representing the skill definition file.
    
    Follows Pydantic BaseModel pattern from core/models.py for data validation and serialization.
    """
    manifest_version: str = Field(description="Manifest format version")
    name: str = Field(description="Unique identifier for the skill", min_length=1, max_length=50)
    description: str = Field(description="Human-readable description of the skill", max_length=500)
    version: str = Field(description="Semantic version of the skill", pattern=r"^\d+\.\d+\.\d+$")
    author: Optional[str] = Field(default="", description="Skill author name")
    contact: Optional[str] = Field(default="", description="Contact information for the skill author")
    tags: List[str] = Field(default_factory=list, description="Keywords for skill discovery")
    api: ClaudeSkillAPIConfig = Field(description="API configuration for the skill")
    tos: Optional[str] = Field(default="", description="Terms of service link")
    privacy_policy: Optional[str] = Field(default="", description="Privacy policy link")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="Required dependencies")
    
    @validator('version')
    def validate_version_format(cls, v):
        """Validate semantic version format."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('Version must be in semantic version format (e.g., 1.0.0)')
        return v
```

### ClaudeSkillAPIConfig
```python
class ClaudeSkillAPIConfig(BaseModel):
    """
    API configuration for Claude Skills including authentication and base URL.
    
    Follows Pydantic BaseModel pattern from core/models.py for configuration validation.
    """
    type: str = Field(description="API type (e.g., http, rest, graphql)")
    auth: ClaudeSkillAuthConfig = Field(description="Authentication configuration")
    base_url: str = Field(description="Base URL for API calls")
    description: Optional[str] = Field(default="", description="API description")
    timeout: float = Field(default=30.0, description="API call timeout in seconds", ge=1.0, le=300.0)
```

### ClaudeSkillAuthConfig
```python
class ClaudeSkillAuthConfig(BaseModel):
    """
    Authentication configuration for Claude Skills.
    
    Follows Pydantic BaseModel pattern from core/models.py for secure authentication.
    """
    type: str = Field(description="Authentication type (e.g., bearer, api_key, oauth)")
    instructions: str = Field(description="Instructions for obtaining authentication", max_length=200)
    key_name: Optional[str] = Field(default="Authorization", description="Header name for auth token")
    required: bool = Field(default=True, description="Whether authentication is required")
```

### ClaudeSkillTool
```python
class ClaudeSkillTool(BaseModel):
    """
    Individual tool specification within Claude Skills format.
    
    Follows Pydantic BaseModel pattern from core/models.py for tool definition.
    """
    name: str = Field(description="Unique tool name for API calls", min_length=1, max_length=50)
    description: str = Field(description="Description of what the tool does", max_length=300)
    input_schema: ClaudeSkillInputSchema = Field(description="JSON Schema for tool inputs")
    
    class Config:
        extra = "allow"  # Allow additional fields for flexibility
```

### ClaudeSkillInputSchema  
```python
class ClaudeSkillInputSchema(BaseModel):
    """
    JSON Schema specification for Claude Skill inputs.
    
    Follows JSON Schema specification and Pydantic BaseModel pattern for validation.
    """
    type: str = Field(description="Schema type (usually 'object')")
    properties: Dict[str, ClaudeSkillProperty] = Field(description="Input parameters definition")
    required: List[str] = Field(default_factory=list, description="Required parameter names")
```

### ClaudeSkillProperty
```python
class ClaudeSkillProperty(BaseModel):
    """
    Property definition in Claude Skill input schema.
    
    Follows JSON Schema property definitions and Pydantic BaseModel pattern.
    """
    type: str = Field(description="Property type (string, integer, number, boolean, array, object)")
    description: Optional[str] = Field(default="", description="Description of the property")
    format: Optional[str] = Field(default=None, description="Format for the property (e.g., email, uri)")
    minimum: Optional[float] = Field(default=None, description="Minimum value for numeric types")
    maximum: Optional[float] = Field(default=None, description="Maximum value for numeric types")
    minLength: Optional[int] = Field(default=None, description="Minimum length for strings")
    maxLength: Optional[int] = Field(default=None, description="Maximum length for strings") 
    enum: Optional[List[str]] = Field(default=None, description="Allowed values for enum properties")
```

## Integration Models

### ClaudeSkillAdapter
```python
class ClaudeSkillAdapter(Skill):
    """
    Adapter to convert Claude Skills format to DAIP-LIVE internal skill format.
    
    Extends Skill base class from skills/base.py to ensure compatibility with existing skill system.
    """
    def __init__(self, manifest: ClaudeSkillManifest, tools: List[ClaudeSkillTool]):
        self.manifest = manifest
        self.tools = tools
        self.http_client = None  # Initialized with security policy
        
        metadata = SkillMetadata(
            name=manifest.name,
            description=manifest.description,
            version=manifest.version,
            author=manifest.author or "Claude Skills Community",
            tags=manifest.tags
        )
        super().__init__(metadata)
    
    async def execute(self, input: SkillInput) -> SkillOutput:
        """Execute the Claude Skill via API call."""
        # Implementation details
        pass
```

### ClaudeSkillSecurityPolicy
```python
class ClaudeSkillSecurityPolicy(BaseModel):
    """
    Security policy for Claude Skills execution including resource limits and network access.
    
    Follows Pydantic BaseModel pattern from core/models.py for security configuration.
    """
    max_execution_time: float = Field(default=30.0, description="Maximum execution time in seconds", ge=1.0, le=300.0)
    network_access: Literal["allow", "restrict", "block"] = Field(default="restrict", description="Network access level")
    allowed_domains: List[str] = Field(default_factory=list, description="List of allowed domains for API calls")
    max_network_calls: int = Field(default=5, description="Maximum number of network calls per execution", ge=1, le=20)
    resource_limits: Dict[str, Any] = Field(default_factory=dict, description="CPU/Memory resource limits")
    timeout_per_request: float = Field(default=10.0, description="Timeout per individual request", ge=1.0, le=60.0)
```

### ClaudeSkillExecutionRequest
```python
class ClaudeSkillExecutionRequest(BaseModel):
    """
    Request model for Claude Skills execution with authentication and parameters.
    
    Follows Pydantic BaseModel pattern with security considerations.
    """
    skill_name: str = Field(description="Name of the skill to execute")
    tool_name: str = Field(description="Name of the specific tool within the skill") 
    parameters: Dict[str, Any] = Field(description="Input parameters for the skill")
    authentication: Optional[Dict[str, str]] = Field(default=None, description="Authentication credentials")
    security_policy: ClaudeSkillSecurityPolicy = Field(default_factory=ClaudeSkillSecurityPolicy, description="Security policy for execution")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context information for the request")
```

### ClaudeSkillExecutionResult
```python  
class ClaudeSkillExecutionResult(BaseModel):
    """
    Result model for Claude Skills execution with security and performance metrics.
    
    Follows Pydantic BaseModel pattern for secure result reporting.
    """
    success: bool = Field(description="Whether skill execution was successful")
    result: str = Field(description="Result of skill execution")
    security_metrics: Dict[str, Any] = Field(default_factory=dict, description="Security-related execution metrics")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    error_message: Optional[str] = Field(default=None, description="Error message if execution failed")
    execution_time: float = Field(description="Total execution time in seconds")
    api_calls_made: int = Field(default=0, description="Number of API calls made during execution")
```

### ProgressiveSkillInfo
```python
class ProgressiveSkillInfo(BaseModel):
    """
    Progressive information disclosure model for Claude Skills.
    
    Follows Pydantic BaseModel pattern for structured skill information.
    """
    skill_name: str = Field(description="Name of the skill")
    current_stage: Literal["discovery", "parameters", "authentication", "execution", "results"] = Field(
        description="Current stage of skill information disclosure"
    )
    available_information: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Information available to user at current stage"
    )
    required_actions: List[str] = Field(
        default_factory=list, 
        description="Actions required from user to progress"
    )
    next_steps: List[str] = Field(
        default_factory=list, 
        description="Suggested next steps for user"
    )
    json_schema_info: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="JSON Schema information if in parameters stage"
    )
```

## Event Models for Communication

### ClaudeSkillExecutionEvent
```python
class ClaudeSkillExecutionEvent(BaseModel):
    """
    Event model for Claude Skills execution workflow.
    
    Follows event-driven architecture pattern from core/models.py.
    """
    type: Literal["claude_skill_execution"] = "claude_skill_execution"
    skill_name: str = Field(description="Name of executed skill")
    tool_name: str = Field(description="Name of executed tool")
    parameters_used: Dict[str, Any] = Field(description="Parameters provided to skill")
    result_preview: str = Field(description="Preview of result (for TUI display)")
    execution_time: float = Field(description="Time taken for execution")
    security_compliance: bool = Field(description="Whether execution complied with security policy")
    session_id: str = Field(description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="When event occurred")
```

### ClaudeSkillDiscoveryEvent  
```python
class ClaudeSkillDiscoveryEvent(BaseModel):
    """
    Event model for Claude Skills discovery and registration.
    
    Follows event-driven architecture pattern from core/models.py.
    """
    type: Literal["claude_skill_discovery"] = "claude_skill_discovery"
    discovered_skills: List[str] = Field(description="List of discovered skill names")
    source_repository: str = Field(description="GitHub repository URL or local path")
    discovery_time: float = Field(description="Time taken to discover skills")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="Any errors during discovery")
    session_id: str = Field(description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="When event occurred")
```

## Model Relationships

### Integration with Existing Models
- ClaudeSkillManifest and ClaudeSkillTool integrate with core Skill interface
- ClaudeSkillExecutionEvent extends AgentEvent for event-driven communication  
- ClaudeSkillSecurityPolicy relates to existing permission/authorization models
- ProgressiveSkillInfo connects with existing dialogue/conversation models

### Validation Chain
- ClaudeSkillManifest validates top-level skill metadata
- ClaudeSkillTool validates individual tool specifications
- ClaudeSkillInputSchema enforces JSON Schema compliance for inputs
- ClaudeSkillExecutionRequest ensures security policy compliance
- All models inherit validation from BaseModel

## Serialization Patterns

### JSON Serialization
- All models support automatic JSON serialization/deserialization via Pydantic
- ClaudeSkillManifest stores skill definition in standard Claude format
- ClaudeSkillExecutionResult serializes with security and performance metrics
- Event models serialize for event system transport

### Data Validation
- Field constraints ensure data integrity
- Custom validators check complex requirements (version format, URL validity)
- Type hints enable IDE support and static analysis
- Nested models validated recursively

## Extensibility Considerations

### Add New Claude Skill Types
- ClaudeSkillInputSchema supports flexible JSON Schema definitions
- ClaudeSkillTool supports various parameter types and validation schemas
- ClaudeSkillSecurityPolicy allows custom security configurations

### Integration Points
- ClaudeSkillAdapter enables integration with existing skill ecosystem
- Event models provide hooks for external system integration  
- ProgressiveSkillInfo enables advanced user interaction flows
- Security Policy models provide customizable security enforcement