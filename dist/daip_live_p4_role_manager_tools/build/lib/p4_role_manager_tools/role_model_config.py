"""
Role-Model Configuration Support

This module extends the base Role model to include model-specific configurations,
allowing different roles to use different models during debates and conversations.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from daip_live.core.models import Role


class RoleModelConfig(BaseModel):
    """Configuration for a specific model used by a role."""
    
    model_name: str = Field(..., description="Name of the model (e.g., 'gpt-4', 'claude-3')")
    provider: str = Field(..., description="Model provider (e.g., 'openai', 'anthropic')")
    max_tokens: int = Field(4000, description="Maximum tokens for responses")
    temperature: float = Field(0.7, description="Model temperature (0.0-1.0)")
    top_p: float = Field(1.0, description="Model top-p parameter")
    frequency_penalty: float = Field(0.0, description="Frequency penalty")
    presence_penalty: float = Field(0.0, description="Presence penalty")
    is_primary: bool = Field(True, description="Whether this is the primary model for the role")
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Temperature must be between 0.0 and 1.0')
        return v
    
    
class EnhancedRole(Role):
    """Extended role model with model configuration support."""
    
    model_configs: List[RoleModelConfig] = Field(
        default_factory=lambda: [RoleModelConfig(
            model_name="gpt-3.5-turbo",
            provider="openai",
            max_tokens=4000,
            temperature=0.7,
            is_primary=True
        )],
        description="List of model configurations for this role"
    )
    
    debate_model_config: Optional[RoleModelConfig] = Field(
        None,
        description="Specific model configuration for debates (if different from primary)"
    )
    
    @classmethod
    def from_base_role(cls, base_role: Role) -> "EnhancedRole":
        """Create an EnhancedRole from a base Role for backward compatibility."""
        return cls(
            name=base_role.name,
            persona=base_role.persona,
            tools=base_role.tools,
            model_configs=[RoleModelConfig(
                model_name="gpt-3.5-turbo",
                provider="openai",
                max_tokens=4000,
                temperature=0.7,
                is_primary=True
            )]
        )
    
    def get_primary_model_config(self) -> RoleModelConfig:
        """Get the primary model configuration for this role."""
        # Find the primary model config
        for config in self.model_configs:
            if config.is_primary:
                return config
        
        # If no primary is marked, return the first one
        if self.model_configs:
            return self.model_configs[0]
        
        # Fallback to default
        return RoleModelConfig(
            model_name="gpt-3.5-turbo",
            provider="openai",
            max_tokens=4000,
            temperature=0.7,
            is_primary=True
        )
    
    def get_debate_model_config(self) -> RoleModelConfig:
        """Get the model configuration for debates."""
        if self.debate_model_config:
            return self.debate_model_config
        
        # If no specific debate config, use primary model config
        return self.get_primary_model_config()
    
    def get_model_config_by_name(self, model_name: str) -> Optional[RoleModelConfig]:
        """Get a specific model configuration by name."""
        for config in self.model_configs:
            if config.model_name == model_name:
                return config
        return None
    
    def get_all_model_names(self) -> List[str]:
        """Get all available model names for this role."""
        return [config.model_name for config in self.model_configs]


class RoleModelMapping(BaseModel):
    """Maps roles to their model configurations for debates."""
    
    role_name: str
    role_model_config: RoleModelConfig = Field(..., description="Model configuration for this role")
    priority: int = Field(1, description="Priority for model selection (higher = preferred)")
    
    @classmethod
    def from_role(cls, role: EnhancedRole, use_debate_config: bool = True) -> "RoleModelMapping":
        """Create a mapping from an enhanced role."""
        if use_debate_config and role.debate_model_config:
            model_config = role.debate_model_config
        else:
            model_config = role.get_primary_model_config()
        
        return cls(
            role_name=role.name,
            role_model_config=model_config,
            priority=1
        )