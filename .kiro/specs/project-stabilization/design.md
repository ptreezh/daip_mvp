# Design Document

## Overview

This design addresses the systematic stabilization of the DAIP-LIVE project by resolving configuration inconsistencies, fixing service interface mismatches, implementing missing CLI components, and ensuring end-to-end functionality. The approach prioritizes minimal disruption to the existing excellent architecture while achieving maximum stability gains.

## Architecture

The existing layered architecture will be preserved and strengthened with a **three-tier intelligence design**:

```
Application Layer (CLI + FastAPI)
    ↓
Human User Intelligence Layer (Personal Secretary, Intent Analysis, Context Optimization)
    ↓
Universal Services Layer (Token Management, Context Optimization, Memory Consolidation)
    ↓
Protocol Layer (Debate & Consensus with Pluggable Strategies)
    ↓  
Core Services Layer (Role, Memory, Wiki, Lightweight Role Personalization)
    ↓
Kernel Layer (LLM Interface, Tool Executor, Consensus Registry)
```

### Three-Tier Intelligence Design

**Tier 1: Universal Services (All Roles)**
- **Token Management**: Precise token counting, cost estimation, context window management
- **Context Optimization**: Smart truncation, memory consolidation for all participants
- **Resource Scheduling**: Fair LLM resource allocation across all roles

**Tier 2: Lightweight Role Personalization (AI Roles)**
- **Role Consistency**: Maintain character traits and speaking styles
- **Domain Knowledge**: Access to role-specific expertise and knowledge bases
- **Behavioral Patterns**: Preserve role-specific interaction patterns

**Tier 3: Deep User Intelligence (Human Users)**
- **Intent Analysis**: Deep understanding of user goals and motivations
- **Personal Context**: Individual background, preferences, and interaction history
- **Prompt Optimization**: Context-aware prompt enhancement based on user profile

## Components and Interfaces

### 1. Configuration System Unification

**Problem Analysis:**
- `src/config.py` and `src/config_loader.py` contain duplicate, incompatible configuration logic
- `main.py` imports non-existent `settings` object
- No default `config.yaml` exists

**Design Solution:**
- Consolidate configuration into a single, robust system in `src/config.py`
- Create a global `settings` instance that can be imported
- Implement graceful fallback to defaults when config file is missing
- Use Pydantic for validation with sensible defaults

**Interface Design:**
```python
# src/config.py
class Settings(BaseModel):
    log_level: str = "INFO"
    allowed_origins: List[str] = ["*"]
    # ... other settings

settings = Settings()  # Global instance
```

### 2. Service Interface Standardization

**Problem Analysis:**
- `SynthesisEngine` constructor expects `client` parameter but implementation uses `llm_interface`
- `RoleManager` constructor expects `config_path` but implementation uses `roles_directory`
- Test expectations don't match actual implementations

**Design Solution:**
- Standardize constructor interfaces across all core services
- Update tests to match actual implementations rather than changing working code
- Ensure dependency injection patterns are consistent

**Interface Standards:**
```python
# Standard pattern for core services
class CoreService:
    def __init__(self, dependency: DependencyType, config: Optional[Config] = None):
        # Standard initialization pattern
```

### 3. CLI Implementation

**Problem Analysis:**
- `src/cli/main.py` referenced in tests but doesn't exist
- Project documentation mentions TUI interface but it's missing
- CLI entry point defined in `pyproject.toml` but not implemented

**Design Solution:**
- Create minimal but functional CLI in `src/cli/main.py`
- Implement basic commands: `start`, `status`, `help`
- Use `typer` for CLI framework (already in dependencies as part of FastAPI ecosystem)
- Provide clear path for future TUI enhancement

**CLI Architecture:**
```
src/cli/
├── main.py          # Entry point and command definitions
├── commands/        # Individual command implementations
│   ├── start.py     # Start debate command
│   └── status.py    # System status command
└── utils.py         # CLI utilities
```

### 4. API Service Integration

**Problem Analysis:**
- FastAPI app fails to start due to missing `settings`
- Some endpoints may return mock data instead of real functionality
- Error handling needs improvement

**Design Solution:**
- Fix configuration import to enable successful startup
- Ensure all endpoints connect to actual services
- Implement proper error handling and logging
- Add health check endpoints

### 5. Service Dependency Resolution

**Problem Analysis:**
- Services may have circular dependencies or missing dependencies
- AppState initialization may fail due to missing components
- Database connections and external services need proper initialization

**Design Solution:**
- Implement proper dependency injection in AppState
- Add graceful degradation for optional services (like ChromaDB)
- Ensure services can initialize with minimal external dependencies
- Add proper cleanup and resource management

## Data Models

### Configuration Models
```python
class DatabaseConfig(BaseModel):
    url: str = "sqlite:///data/daip.db"
    
class LLMConfig(BaseModel):
    provider: str = "ollama"
    model: str = "llama3:instruct"
    host: str = "http://localhost:11434"
    
class TokenManagementConfig(BaseModel):
    max_context_tokens: int = 4096
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    enable_cost_tracking: bool = True
    
class Settings(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    token_management: TokenManagementConfig = TokenManagementConfig()
    log_level: str = "INFO"
    allowed_origins: List[str] = ["*"]
```

### Universal Services Models
```python
class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    timestamp: datetime

class ContextWindow(BaseModel):
    messages: List[Dict[str, Any]]
    total_tokens: int
    max_tokens: int
    compression_applied: bool = False
    
class ConversationState(BaseModel):
    participant_id: str  # Can be user_id or role_id
    conversation_history: List[Dict[str, Any]]
    token_usage: TokenUsage
    context_window: ContextWindow
    last_updated: datetime
```

### Future Extension Models

**Personal Secretary Models:**
```python
class UserProfile(BaseModel):
    user_id: str
    preferences: Dict[str, Any]
    background_knowledge: List[str]
    interaction_history: List[str]
    intent_patterns: Dict[str, float]

class IntentAnalysis(BaseModel):
    user_input: str
    detected_intent: str
    confidence: float
    context_requirements: List[str]
    suggested_enhancements: List[str]

class ContextOptimization(BaseModel):
    original_prompt: str
    optimized_prompt: str
    added_context: List[str]
    personalization_factors: Dict[str, Any]
```

**Consensus Algorithm Models:**
```python
class ConsensusStrategy(ABC):
    @abstractmethod
    async def execute(self, opinions: List[Opinion]) -> ConsensusResult
    
class WeightedVotingStrategy(ConsensusStrategy):
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights
        
class ReputationBasedStrategy(ConsensusStrategy):
    def __init__(self, reputation_service: ReputationService):
        self.reputation_service = reputation_service
```

### Service Interface Models
```python
class ServiceConfig(BaseModel):
    """Base configuration for all services"""
    enabled: bool = True
    timeout: int = 30
    
class ServiceResult(BaseModel):
    """Standard result format for service operations"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
```

## Universal Services Design

### 1. Token Management Service

**Core Responsibilities:**
- Precise token counting using tiktoken for all text inputs
- Cost estimation and budget tracking
- Context window management and smart truncation
- Token usage analytics and reporting

**Interface Design:**
```python
class TokenManagementService:
    def __init__(self, config: TokenManagementConfig):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.config = config
        
    def count_tokens(self, text: str, model: str = None) -> int:
        """Count tokens in text using appropriate tokenizer"""
        
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate estimated cost for token usage"""
        
    def check_context_limit(self, messages: List[Dict], model: str) -> bool:
        """Check if messages fit within model's context window"""
        
    def optimize_context_window(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
        """Smart truncation while preserving important context"""
```

### 2. Universal Context Optimization Service

**Core Responsibilities:**
- Intelligent message compression for all participants
- Important information preservation
- Context window sliding and management
- Memory consolidation across conversations

**Interface Design:**
```python
class UniversalContextService:
    def __init__(self, token_service: TokenManagementService, memory_service: MemoryService):
        self.token_service = token_service
        self.memory_service = memory_service
        
    def compress_conversation(self, messages: List[Dict], target_tokens: int) -> List[Dict]:
        """Compress conversation while preserving key information"""
        
    def consolidate_memory(self, participant_id: str, conversation: List[Dict]) -> None:
        """Extract and store important information from conversation"""
        
    def prepare_context(self, participant_id: str, new_message: str) -> List[Dict]:
        """Prepare optimized context for LLM call"""
```

## Human User Intelligence Layer Design

### 1. Intent Analysis Service

**Core Responsibilities:**
- Deep analysis of user input to understand goals and motivations
- Context requirement identification
- Conversation flow prediction
- Personalization opportunity detection

**Interface Design:**
```python
class IntentAnalysisService:
    def __init__(self, llm_interface: LLMInterface, user_profile_service: UserProfileService):
        self.llm_interface = llm_interface
        self.user_profile_service = user_profile_service
        
    async def analyze_intent(self, user_input: str, user_id: str, conversation_context: List[Dict]) -> IntentAnalysis:
        """Analyze user intent and provide enhancement suggestions"""
        
    async def predict_user_needs(self, user_id: str, current_context: str) -> List[str]:
        """Predict what the user might need based on their profile and context"""
```

### 2. Personal Context Service

**Core Responsibilities:**
- Maintain individual user profiles and preferences
- Track interaction patterns and learning preferences
- Store personal background knowledge and expertise areas
- Manage user-specific conversation history

**Interface Design:**
```python
class PersonalContextService:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
        
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Retrieve comprehensive user profile"""
        
    def update_user_preferences(self, user_id: str, interaction_data: Dict) -> None:
        """Learn from user interactions to improve personalization"""
        
    def get_relevant_background(self, user_id: str, topic: str) -> List[str]:
        """Get user's relevant background knowledge for a topic"""
```

### 3. Prompt Optimization Service

**Core Responsibilities:**
- Enhance prompts based on user profile and intent analysis
- Add relevant context and background information
- Optimize for user's communication style and expertise level
- Personalize based on user's goals and preferences

**Interface Design:**
```python
class PromptOptimizationService:
    def __init__(self, intent_service: IntentAnalysisService, context_service: PersonalContextService):
        self.intent_service = intent_service
        self.context_service = context_service
        
    async def optimize_prompt(self, original_prompt: str, user_id: str, context: Dict) -> ContextOptimization:
        """Optimize prompt based on user profile and intent"""
        
    def add_personal_context(self, prompt: str, user_profile: UserProfile, topic: str) -> str:
        """Add relevant personal context to enhance understanding"""
```

## Error Handling

### Graceful Degradation Strategy
1. **Configuration Errors**: Use defaults and log warnings
2. **Service Initialization Errors**: Disable non-critical services
3. **Runtime Errors**: Log and return appropriate error responses
4. **External Service Failures**: Implement retry logic and fallbacks

### Error Response Format
```python
class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime
    request_id: str
```

## Testing Strategy

### Test Fixes Priority
1. **Constructor Interface Mismatches**: Update test fixtures to match actual implementations
2. **Mock Configuration**: Ensure tests use consistent mock configurations
3. **Integration Tests**: Fix service dependency mocking
4. **CLI Tests**: Create tests for new CLI implementation

### Test Categories
- **Unit Tests**: Individual service functionality
- **Integration Tests**: Service interaction and API endpoints
- **CLI Tests**: Command-line interface functionality
- **Configuration Tests**: Configuration loading and validation

## Implementation Phases

### Phase 1: Core Stabilization (Days 1-3)
1. Fix configuration system and settings import
2. Resolve service constructor interface mismatches
3. Ensure FastAPI application starts successfully
4. Fix critical test failures

### Phase 2: CLI Implementation (Days 4-5)
1. Create basic CLI structure
2. Implement essential commands
3. Add CLI tests
4. Update documentation

### Phase 3: Integration & Polish (Days 6-7)
1. End-to-end testing
2. Documentation updates
3. Performance verification
4. Final test suite validation

## Security Considerations

- Configuration files should not contain sensitive data in plain text
- API endpoints should have proper input validation
- CLI should validate user inputs
- Error messages should not leak sensitive information

## Performance Considerations

- Configuration loading should be cached
- Service initialization should be lazy where possible
- Database connections should be pooled
- LLM calls should have proper timeout handling

## Monitoring and Logging

- Structured logging with consistent format
- Service health checks
- Performance metrics collection
- Error tracking and alerting