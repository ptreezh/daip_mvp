# Data Models: Personal Assistant and Knowledge Base Enhancement

**Date**: 2025-11-19
**Feature**: specs/personal_assistant_knowledge_enhancement/spec.md
**Status**: Designed and Implemented
**Model Focus**: Enhanced intent recognition and knowledge management models

## Intent Data Models

### PersonalAssistantIntent

```python
class PersonalAssistantIntent(BaseModel):
    """
    Represents a user's request to the personal assistant.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    request_type: str = Field(
        description="Type of request: research_assistance, content_creation, translation, explanation, help_request, etc.",
        default="general_assistance"
    )
    specific_request: str = Field(
        description="Specific request content from user",
        default=""
    )
    original_request: str = Field(
        description="Original user input for reference",
        default=""
    )
    use_knowledge_base: bool = Field(
        description="Whether to utilize knowledge base for response",
        default=True
    )
    multi_model_required: bool = Field(
        description="Whether multi-model collaboration is needed",
        default=True
    )
    priority: int = Field(
        description="Request priority (1-5)",
        default=3
    )
    context_requirements: List[str] = Field(
        description="Additional context needed to fulfill request",
        default_factory=list
    )
```

### ClarificationRequest

```python
class ClarificationRequest(BaseModel):
    """
    Request for missing information or clarification from user.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    type: str = Field(
        description="Type of clarification: missing_keywords, missing_parameters, ambiguous_intent",
        default="missing_keywords"
    )
    message: str = Field(
        description="Message to user requesting clarification",
        default=""
    )
    required_parameters: List[str] = Field(
        description="Parameters needed to complete the request",
        default_factory=list
    )
    suggested_values: List[str] = Field(
        description="Suggested values for the missing parameters",
        default_factory=list
    )
    intent_name: str = Field(
        description="Original intent that requires clarification",
        default=""
    )
```

## Knowledge Management Models

### KnowledgeSearchQuery

```python
class KnowledgeSearchQuery(BaseModel):
    """
    Query for searching the knowledge base.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    query_text: str = Field(
        description="Search query text",
        min_length=1
    )
    top_k: int = Field(
        description="Number of top results to return",
        default=5,
        ge=1,
        le=20
    )
    filters: Dict[str, Any] = Field(
        description="Filter conditions for search",
        default_factory=dict
    )
    search_type: str = Field(
        description="Type of search: semantic, full_text, hybrid",
        default="semantic"
    )
    context_window: int = Field(
        description="Size of context window for search",
        default=3,
        ge=1
    )
```

### KnowledgeSearchResult

```python
class KnowledgeSearchResult(BaseModel):
    """
    Result from knowledge base search operation.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    file_path: str = Field(
        description="Path to the relevant document"
    )
    content_snippet: str = Field(
        description="Snippet of content from the document",
        default=""
    )
    distance: float = Field(
        description="Semantic distance to query (lower is better)",
        ge=0.0
    )
    relevance_score: float = Field(
        description="Computed relevance score (higher is better)",
        ge=0.0,
        le=1.0
    )
    indexed_at: datetime = Field(
        description="When document was indexed"
    )
    document_type: str = Field(
        description="Type of document: paper, wiki, article, etc.",
        default="unknown"
    )
    metadata: Dict[str, Any] = Field(
        description="Additional metadata for the result",
        default_factory=dict
    )
```

## Knowledge Base Change Models

### KnowledgeBaseChanges

```python
class KnowledgeBaseChanges(BaseModel):
    """
    Tracks changes in the knowledge base for sync operations.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    added: List[str] = Field(
        description="Paths of newly added documents",
        default_factory=list
    )
    updated: List[Tuple[str, Any]] = Field(  # Tuple[path, old_record]
        description="Paths and old records of updated documents",
        default_factory=list
    )
    deleted: List[Any] = Field(  # List of old KnowledgeSource records
        description="Old records of deleted documents",
        default_factory=list
    )
    unchanged: List[Any] = Field(  # List of KnowledgeSource records
        description="Records of unchanged documents",
        default_factory=list
    )
    scanned_count: int = Field(
        description="Total number of documents scanned",
        default=0
    )
    sync_start_time: datetime = Field(
        description="Time when sync began",
        default_factory=datetime.now
    )
    sync_end_time: Optional[datetime] = Field(
        default=None
    )
```

## Event Models for Communication

### PersonalAssistantRequestEvent

```python
class PersonalAssistantRequestEvent(BaseModel):
    """
    Event for personal assistant request initiation.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    type: Literal["personal_assistant_request"] = "personal_assistant_request"
    session_id: str
    request_type: str
    original_request: str
    context_requirements: List[str] = Field(default_factory=list)
    use_knowledge_base: bool = True
    multi_model_required: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)
```

### ClarificationRequiredEvent

```python  
class ClarificationRequiredEvent(BaseModel):
    """
    Event indicating that additional information is required from user.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    type: Literal["clarification_required"] = "clarification_required"
    session_id: str
    intent_name: str
    required_parameters: List[str]
    clarification_message: str
    suggested_responses: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
```

### KnowledgeSearchEvent

```python
class KnowledgeSearchEvent(BaseModel):
    """
    Event for knowledge base search operation.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    type: Literal["knowledge_search"] = "knowledge_search"
    session_id: str
    query: str
    results: List[KnowledgeSearchResult] = Field(default_factory=list)
    success: bool
    error_message: Optional[str] = None
    search_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
```

## Parameter Extraction Models

### AssistantParams

```python
class AssistantParams(BaseModel):
    """
    Parameters extracted for personal assistant intent.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    request_type: str = Field(default="general_assistance")
    specific_request: str = Field(default="")
    original_request: str
    use_knowledge_base: bool = Field(default=True)
    multi_model_required: bool = Field(default=True)
```

### WikiCreationParams

```python
class WikiCreationParams(BaseModel):
    """
    Parameters for wiki creation intent.
    
    Follows Pydantic BaseModel pattern from core/models.py
    """
    title: str = Field(default="")
    content: str = Field(default="")  
    tags: List[str] = Field(default_factory=list)
    multi_role_collaboration: bool = Field(default=True)
    original_request: str
```

## Model Relationships

### System Integration
- PersonalAssistantIntent integrates with EnhancedIntentRecognizer
- KnowledgeSearchResult used by KnowledgeManager and DebateSystem
- ClarificationRequest triggers clarification workflows in TUI
- Events connect components via event-driven architecture

### Validation Rules
- All models inherit from BaseModel for automatic validation
- Field constraints enforce data integrity at boundaries
- Required fields ensure essential parameters are present
- Default values provide sensible fallbacks

## Schema Evolution Patterns

### Forward Compatibility
- Field defaults prevent breaking changes from new parameters
- Optional fields allow gradual feature addition
- Union types support multiple value formats

### Versioning Approach
- No explicit version numbers (YAGNI principle)
- Field additions are non-breaking
- Breaking changes require new model types
- Migration handled at service layer