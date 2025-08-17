# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 07:00:00
@Author  : DAIP-LIVE Team
@File    : role_customization.py
@Description:
    Dynamic role configuration and customization system.
    Implements requirement 7.4 - dynamic role configuration capabilities.
"""
import logging
import json
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class InteractionMode(str, Enum):
    """Modes of role interaction."""
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    CRITICAL = "critical"
    SUPPORTIVE = "supportive"
    NEUTRAL = "neutral"


class ExpertiseLevel(str, Enum):
    """Levels of expertise."""
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class CognitiveStyle(str, Enum):
    """Cognitive styles for reasoning."""
    LOGICAL = "logical"
    INTUITIVE = "intuitive"
    SYSTEMATIC = "systematic"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    HOLISTIC = "holistic"


class RolePersonality(BaseModel):
    """Personality traits for a role."""
    openness: float = Field(ge=0.0, le=1.0, default=0.5)
    conscientiousness: float = Field(ge=0.0, le=1.0, default=0.5)
    extraversion: float = Field(ge=0.0, le=1.0, default=0.5)
    agreeableness: float = Field(ge=0.0, le=1.0, default=0.5)
    neuroticism: float = Field(ge=0.0, le=1.0, default=0.5)
    
    def get_personality_description(self) -> str:
        """Generate a personality description."""
        traits = []
        
        if self.openness > 0.7:
            traits.append("highly creative and open to new ideas")
        elif self.openness < 0.3:
            traits.append("practical and conventional")
        
        if self.conscientiousness > 0.7:
            traits.append("highly organized and detail-oriented")
        elif self.conscientiousness < 0.3:
            traits.append("flexible and spontaneous")
        
        if self.extraversion > 0.7:
            traits.append("outgoing and assertive")
        elif self.extraversion < 0.3:
            traits.append("reserved and thoughtful")
        
        if self.agreeableness > 0.7:
            traits.append("cooperative and trusting")
        elif self.agreeableness < 0.3:
            traits.append("competitive and skeptical")
        
        if self.neuroticism > 0.7:
            traits.append("emotionally sensitive")
        elif self.neuroticism < 0.3:
            traits.append("emotionally stable")
        
        return ", ".join(traits) if traits else "balanced personality"


class ExpertiseProfile(BaseModel):
    """Expertise profile for a role."""
    domain: str
    level: ExpertiseLevel
    specializations: List[str] = Field(default_factory=list)
    years_experience: Optional[int] = None
    key_skills: List[str] = Field(default_factory=list)
    knowledge_areas: List[str] = Field(default_factory=list)
    
    def get_expertise_description(self) -> str:
        """Generate an expertise description."""
        desc = f"{self.level.value} level expertise in {self.domain}"
        
        if self.specializations:
            desc += f", specializing in {', '.join(self.specializations)}"
        
        if self.years_experience:
            desc += f" with {self.years_experience} years of experience"
        
        return desc


class RolePromptTemplate(BaseModel):
    """Template for role prompts."""
    system_prompt: str
    task_prompt_template: str
    interaction_prompt_template: str
    context_prompt_template: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    
    def render_prompt(self, prompt_type: str, **kwargs) -> str:
        """Render a prompt with variables."""
        template_map = {
            "system": self.system_prompt,
            "task": self.task_prompt_template,
            "interaction": self.interaction_prompt_template,
            "context": self.context_prompt_template
        }
        
        template = template_map.get(prompt_type, "")
        if not template:
            return ""
        
        # Merge variables with kwargs
        render_vars = {**self.variables, **kwargs}
        
        # Simple template rendering
        try:
            return template.format(**render_vars)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return template


class RoleConfiguration(BaseModel):
    """Complete configuration for a role."""
    role_id: str
    name: str
    description: str
    
    # Core characteristics
    expertise_profile: ExpertiseProfile
    personality: RolePersonality
    cognitive_style: CognitiveStyle
    interaction_mode: InteractionMode
    
    # Prompts and behavior
    prompt_template: RolePromptTemplate
    
    # Behavioral parameters
    confidence_threshold: float = Field(ge=0.0, le=1.0, default=0.7)
    risk_tolerance: float = Field(ge=0.0, le=1.0, default=0.5)
    collaboration_preference: float = Field(ge=0.0, le=1.0, default=0.7)
    
    # Constraints and preferences
    max_response_length: int = Field(gt=0, default=1000)
    preferred_evidence_types: List[str] = Field(default_factory=list)
    communication_style: str = "professional"
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: List[str] = Field(default_factory=list)
    
    def update_configuration(self, updates: Dict[str, Any]) -> None:
        """Update role configuration."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def get_role_context(self) -> Dict[str, Any]:
        """Get role context for LLM interactions."""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "expertise": self.expertise_profile.get_expertise_description(),
            "personality": self.personality.get_personality_description(),
            "cognitive_style": self.cognitive_style.value,
            "interaction_mode": self.interaction_mode.value,
            "confidence_threshold": self.confidence_threshold,
            "communication_style": self.communication_style
        }


class RoleTemplate(BaseModel):
    """Template for creating role configurations."""
    template_id: str
    name: str
    description: str
    category: str
    
    # Template parameters
    default_config: RoleConfiguration
    customizable_fields: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)
    
    # Metadata
    author: str
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    
    def create_role_from_template(
        self,
        role_id: str,
        customizations: Dict[str, Any] = None
    ) -> RoleConfiguration:
        """Create a role configuration from this template."""
        # Start with default configuration
        config_dict = self.default_config.dict()
        config_dict["role_id"] = role_id
        
        # Apply customizations
        if customizations:
            for field, value in customizations.items():
                if field in self.customizable_fields:
                    config_dict[field] = value
                else:
                    logger.warning(f"Field '{field}' is not customizable in template '{self.template_id}'")
        
        # Validate required fields
        for field in self.required_fields:
            if field not in config_dict or config_dict[field] is None:
                raise ValueError(f"Required field '{field}' is missing")
        
        return RoleConfiguration(**config_dict)


class RoleConfigurationManager:
    """
    Manager for role configurations and templates.
    
    This class provides dynamic role configuration capabilities,
    allowing for custom prompts, expertise profiles, and interaction patterns.
    """
    
    def __init__(self):
        """Initialize the role configuration manager."""
        self.configurations: Dict[str, RoleConfiguration] = {}
        self.templates: Dict[str, RoleTemplate] = {}
        self.active_roles: Dict[str, str] = {}  # role_instance_id -> config_id
        
        # Initialize with standard templates
        self._initialize_standard_templates()
        
        logger.info("RoleConfigurationManager initialized")
    
    def _initialize_standard_templates(self) -> None:
        """Initialize standard role templates."""
        # Critical Reviewer Template
        critical_reviewer = RoleTemplate(
            template_id="critical_reviewer",
            name="Critical Reviewer",
            description="Role for critical analysis and fact-checking",
            category="analysis",
            author="system",
            default_config=RoleConfiguration(
                role_id="template_critical_reviewer",
                name="Critical Reviewer",
                description="Analyzes content critically and identifies potential issues",
                expertise_profile=ExpertiseProfile(
                    domain="critical_analysis",
                    level=ExpertiseLevel.EXPERT,
                    specializations=["fact_checking", "logical_analysis", "evidence_evaluation"],
                    key_skills=["critical_thinking", "research", "skeptical_inquiry"]
                ),
                personality=RolePersonality(
                    openness=0.8,
                    conscientiousness=0.9,
                    extraversion=0.4,
                    agreeableness=0.3,
                    neuroticism=0.2
                ),
                cognitive_style=CognitiveStyle.ANALYTICAL,
                interaction_mode=InteractionMode.CRITICAL,
                prompt_template=RolePromptTemplate(
                    system_prompt="You are a critical reviewer with expertise in {expertise}. Your role is to analyze content skeptically, identify potential issues, and seek counter-evidence. You are {personality} and approach tasks with {cognitive_style} thinking.",
                    task_prompt_template="Critically analyze the following content: {content}\n\nFocus on: {focus_areas}\n\nProvide detailed analysis with evidence.",
                    interaction_prompt_template="As a critical reviewer, respond to: {message}\n\nMaintain your skeptical perspective while being constructive.",
                    context_prompt_template="Given the context: {context}\n\nApply your critical analysis skills to evaluate the situation."
                ),
                confidence_threshold=0.8,
                risk_tolerance=0.3,
                collaboration_preference=0.5,
                communication_style="direct and analytical"
            ),
            customizable_fields=["expertise_profile", "personality", "confidence_threshold", "communication_style"],
            required_fields=["role_id", "name"],
            tags=["critical", "analysis", "fact-checking"]
        )
        
        # Synthesis Expert Template
        synthesis_expert = RoleTemplate(
            template_id="synthesis_expert",
            name="Synthesis Expert",
            description="Role for synthesizing multiple perspectives",
            category="synthesis",
            author="system",
            default_config=RoleConfiguration(
                role_id="template_synthesis_expert",
                name="Synthesis Expert",
                description="Combines multiple viewpoints into coherent synthesis",
                expertise_profile=ExpertiseProfile(
                    domain="knowledge_synthesis",
                    level=ExpertiseLevel.EXPERT,
                    specializations=["perspective_integration", "consensus_building", "knowledge_fusion"],
                    key_skills=["synthesis", "integration", "holistic_thinking"]
                ),
                personality=RolePersonality(
                    openness=0.9,
                    conscientiousness=0.8,
                    extraversion=0.6,
                    agreeableness=0.8,
                    neuroticism=0.2
                ),
                cognitive_style=CognitiveStyle.HOLISTIC,
                interaction_mode=InteractionMode.COLLABORATIVE,
                prompt_template=RolePromptTemplate(
                    system_prompt="You are a synthesis expert with {expertise}. Your role is to integrate diverse perspectives into coherent wholes. You are {personality} and use {cognitive_style} thinking to find connections and patterns.",
                    task_prompt_template="Synthesize the following perspectives: {perspectives}\n\nCreate a comprehensive synthesis that captures key insights while resolving conflicts.",
                    interaction_prompt_template="As a synthesis expert, help integrate: {message}\n\nFocus on finding common ground and complementary insights.",
                    context_prompt_template="In the context of: {context}\n\nApply your synthesis skills to create unified understanding."
                ),
                confidence_threshold=0.7,
                risk_tolerance=0.6,
                collaboration_preference=0.9,
                communication_style="integrative and balanced"
            ),
            customizable_fields=["expertise_profile", "personality", "collaboration_preference", "communication_style"],
            required_fields=["role_id", "name"],
            tags=["synthesis", "integration", "collaboration"]
        )
        
        # Domain Expert Template
        domain_expert = RoleTemplate(
            template_id="domain_expert",
            name="Domain Expert",
            description="Customizable expert in specific domain",
            category="expertise",
            author="system",
            default_config=RoleConfiguration(
                role_id="template_domain_expert",
                name="Domain Expert",
                description="Expert with deep knowledge in specific domain",
                expertise_profile=ExpertiseProfile(
                    domain="general",
                    level=ExpertiseLevel.EXPERT,
                    specializations=[],
                    key_skills=["domain_knowledge", "technical_analysis", "problem_solving"]
                ),
                personality=RolePersonality(
                    openness=0.7,
                    conscientiousness=0.8,
                    extraversion=0.5,
                    agreeableness=0.6,
                    neuroticism=0.3
                ),
                cognitive_style=CognitiveStyle.SYSTEMATIC,
                interaction_mode=InteractionMode.ANALYTICAL,
                prompt_template=RolePromptTemplate(
                    system_prompt="You are a domain expert in {domain} with {expertise}. You are {personality} and approach problems with {cognitive_style} methodology.",
                    task_prompt_template="Apply your expertise in {domain} to analyze: {content}\n\nProvide expert insights and recommendations.",
                    interaction_prompt_template="As a {domain} expert, respond to: {message}\n\nShare your specialized knowledge and perspective.",
                    context_prompt_template="Given your expertise in {domain} and the context: {context}\n\nProvide expert analysis and guidance."
                ),
                confidence_threshold=0.8,
                risk_tolerance=0.4,
                collaboration_preference=0.7,
                communication_style="authoritative and informative"
            ),
            customizable_fields=["expertise_profile", "personality", "cognitive_style", "interaction_mode", "communication_style"],
            required_fields=["role_id", "name", "expertise_profile"],
            tags=["expert", "domain", "customizable"]
        )
        
        # Register templates
        self.templates[critical_reviewer.template_id] = critical_reviewer
        self.templates[synthesis_expert.template_id] = synthesis_expert
        self.templates[domain_expert.template_id] = domain_expert
        
        logger.info("Initialized standard role templates")
    
    def register_role_template(self, template: RoleTemplate) -> bool:
        """
        Register a role template.
        
        Args:
            template: Role template to register
            
        Returns:
            True if registration was successful
        """
        if template.template_id in self.templates:
            logger.warning(f"Template '{template.template_id}' already exists. Overwriting.")
        
        self.templates[template.template_id] = template
        logger.info(f"Registered role template: {template.template_id}")
        return True
    
    def create_role_from_template(
        self,
        template_id: str,
        role_id: str,
        customizations: Dict[str, Any] = None
    ) -> Optional[RoleConfiguration]:
        """
        Create a role configuration from a template.
        
        Args:
            template_id: ID of the template to use
            role_id: ID for the new role configuration
            customizations: Customizations to apply
            
        Returns:
            Created role configuration, or None if creation failed
        """
        if template_id not in self.templates:
            logger.error(f"Template '{template_id}' not found")
            return None
        
        try:
            template = self.templates[template_id]
            config = template.create_role_from_template(role_id, customizations)
            
            # Register the configuration
            self.configurations[role_id] = config
            
            logger.info(f"Created role '{role_id}' from template '{template_id}'")
            return config
            
        except Exception as e:
            logger.error(f"Error creating role from template: {e}")
            return None
    
    def register_role_configuration(self, config: RoleConfiguration) -> bool:
        """
        Register a role configuration.
        
        Args:
            config: Role configuration to register
            
        Returns:
            True if registration was successful
        """
        if config.role_id in self.configurations:
            logger.warning(f"Role configuration '{config.role_id}' already exists. Overwriting.")
        
        self.configurations[config.role_id] = config
        logger.info(f"Registered role configuration: {config.role_id}")
        return True
    
    def get_role_configuration(self, role_id: str) -> Optional[RoleConfiguration]:
        """Get a role configuration by ID."""
        return self.configurations.get(role_id)
    
    def update_role_configuration(
        self,
        role_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a role configuration.
        
        Args:
            role_id: ID of the role to update
            updates: Updates to apply
            
        Returns:
            True if update was successful
        """
        if role_id not in self.configurations:
            logger.error(f"Role configuration '{role_id}' not found")
            return False
        
        try:
            config = self.configurations[role_id]
            config.update_configuration(updates)
            
            logger.info(f"Updated role configuration: {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating role configuration: {e}")
            return False
    
    def list_role_configurations(self) -> List[RoleConfiguration]:
        """List all role configurations."""
        return list(self.configurations.values())
    
    def list_role_templates(self) -> List[RoleTemplate]:
        """List all role templates."""
        return list(self.templates.values())
    
    def search_templates(
        self,
        category: str = None,
        tags: List[str] = None,
        query: str = None
    ) -> List[RoleTemplate]:
        """
        Search role templates by criteria.
        
        Args:
            category: Template category to filter by
            tags: Tags to filter by
            query: Text query to search in name and description
            
        Returns:
            List of matching templates
        """
        templates = list(self.templates.values())
        results = []
        
        for template in templates:
            # Category filter
            if category and template.category != category:
                continue
            
            # Tags filter
            if tags and not any(tag in template.tags for tag in tags):
                continue
            
            # Text query filter
            if query:
                query_lower = query.lower()
                if (query_lower not in template.name.lower() and 
                    query_lower not in template.description.lower()):
                    continue
            
            results.append(template)
        
        return results
    
    def activate_role(self, role_instance_id: str, config_id: str) -> bool:
        """
        Activate a role with a specific configuration.
        
        Args:
            role_instance_id: ID of the role instance
            config_id: ID of the configuration to use
            
        Returns:
            True if activation was successful
        """
        if config_id not in self.configurations:
            logger.error(f"Configuration '{config_id}' not found")
            return False
        
        self.active_roles[role_instance_id] = config_id
        logger.info(f"Activated role instance '{role_instance_id}' with config '{config_id}'")
        return True
    
    def get_active_role_config(self, role_instance_id: str) -> Optional[RoleConfiguration]:
        """Get the configuration for an active role instance."""
        config_id = self.active_roles.get(role_instance_id)
        if config_id:
            return self.configurations.get(config_id)
        return None
    
    def deactivate_role(self, role_instance_id: str) -> bool:
        """Deactivate a role instance."""
        if role_instance_id in self.active_roles:
            del self.active_roles[role_instance_id]
            logger.info(f"Deactivated role instance: {role_instance_id}")
            return True
        return False
    
    def get_role_prompt(
        self,
        role_id: str,
        prompt_type: str,
        **kwargs
    ) -> str:
        """
        Get a rendered prompt for a role.
        
        Args:
            role_id: ID of the role configuration
            prompt_type: Type of prompt (system, task, interaction, context)
            **kwargs: Variables for prompt rendering
            
        Returns:
            Rendered prompt string
        """
        config = self.configurations.get(role_id)
        if not config:
            logger.error(f"Role configuration '{role_id}' not found")
            return ""
        
        # Add role context to kwargs
        role_context = config.get_role_context()
        render_kwargs = {**role_context, **kwargs}
        
        return config.prompt_template.render_prompt(prompt_type, **render_kwargs)
    
    def export_configuration(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Export a role configuration to dictionary."""
        config = self.configurations.get(role_id)
        if config:
            return config.dict()
        return None
    
    def import_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Import a role configuration from dictionary."""
        try:
            config = RoleConfiguration(**config_data)
            return self.register_role_configuration(config)
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information."""
        return {
            "total_configurations": len(self.configurations),
            "total_templates": len(self.templates),
            "active_roles": len(self.active_roles),
            "template_categories": list(set(t.category for t in self.templates.values())),
            "configuration_ids": list(self.configurations.keys()),
            "template_ids": list(self.templates.keys()),
            "active_role_instances": list(self.active_roles.keys())
        }