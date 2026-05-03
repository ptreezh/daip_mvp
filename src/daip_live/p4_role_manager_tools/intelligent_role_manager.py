"""Intelligent role management system with dynamic role creation and model availability checking."""

import asyncio
import os
import yaml
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from daip_live.core.models import Role
from daip_live.p4_role_manager_tools.role_model_config import EnhancedRole, RoleModelConfig
from daip_live.p8_debate_system.role_selector import IntelligentRoleSelector
from daip_live.model_provider.provider import LiteLLMProvider

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class RoleCreationRequest:
    """Request for creating a new role based on a topic."""
    topic: str
    role_name: str
    role_description: str
    domain_expertise: List[str]
    personality_traits: List[str]
    model_requirements: Optional[Dict] = None


class IntelligentRoleManager:
    """Enhanced role manager that intelligently creates and manages roles based on topics."""

    def __init__(self, roles_dir: str = "roles", model_provider: Optional[LiteLLMProvider] = None):
        # Resolve the roles directory with the same robust approach as base RoleManager
        self.roles_dir = Path(self._resolve_roles_path(roles_dir))
        try:
            self.roles_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            logger.error(f"Failed to create roles directory {self.roles_dir}: {e}")
            # Fallback to current directory
            self.roles_dir = Path.cwd() / "roles"
            try:
                self.roles_dir.mkdir(exist_ok=True, parents=True)
            except Exception as e2:
                logger.error(f"Failed to create fallback roles directory: {e2}")
                # Last resort: use a temp directory
                import tempfile
                self.roles_dir = Path(tempfile.mkdtemp()) / "roles"
                self.roles_dir.mkdir(exist_ok=True, parents=True)

        self.role_selector = IntelligentRoleSelector()
        self.model_provider = model_provider
        self.available_models_cache: Optional[List[str]] = None

    def _resolve_roles_path(self, roles_dir_path: str) -> str:
        """Resolve the roles directory path with multiple fallback strategies."""
        import os
        from pathlib import Path

        # First try our advanced path resolver utility
        try:
            from daip_live.utils.path_resolver import get_configured_roles_path
            return str(get_configured_roles_path(roles_dir_path))
        except ImportError:
            # If the utility module is not available, fall back to the original logic
            pass

        # Strategy 1: If it's already an absolute path
        if os.path.isabs(roles_dir_path) and os.path.exists(roles_dir_path):
            return roles_dir_path

        # Strategy 2: Check relative to current working directory
        current_path = Path(roles_dir_path)
        if current_path.exists():
            return str(current_path.resolve())

        # Strategy 3: Check relative to project root
        possible_roots = [
            Path(__file__).parent.parent.parent.parent,  # Project root (4 levels up)
            Path(__file__).parent.parent.parent,         # src/daip_live (3 levels up)
            Path.cwd(),                                  # Current working directory
        ]

        for root_path in possible_roots:
            try:
                abs_roles_path = root_path / roles_dir_path
                if abs_roles_path.exists() and abs_roles_path.is_dir():
                    return str(abs_roles_path.resolve())
            except:
                continue

        # Strategy 4: Search for roles directory in common locations
        search_paths = [
            Path.cwd() / "roles",
            Path.cwd() / "src" / "daip_live" / "roles",
            Path(__file__).parent.parent / "roles",  # Relative to current file
        ]

        for search_path in search_paths:
            if search_path.exists():
                return str(search_path.resolve())

        # If nothing found, return the original path (it will be created if needed)
        return roles_dir_path

    def analyze_topic(self, topic: str) -> Dict:
        """Analyze a debate topic to extract characteristics for role creation."""
        topic_analysis = self.role_selector.analyze_topic(topic)
        return {
            'topic': topic_analysis.topic,
            'domains': topic_analysis.domains,
            'keywords': topic_analysis.keywords,
            'complexity_score': topic_analysis.complexity_score,
            'debate_type': topic_analysis.debate_type
        }

    def suggest_roles_for_topic(self, topic: str, available_roles: List[EnhancedRole],
                               num_suggestions: int = 3) -> List[EnhancedRole]:
        """Suggest the best roles for a given topic."""
        suggestions = self.role_selector.suggest_roles(topic, available_roles, num_suggestions)
        return [suggestion.role for suggestion in suggestions]

    def auto_select_roles(self, topic: str, available_roles: List[EnhancedRole],
                         num_roles: int = 2) -> List[EnhancedRole]:
        """Automatically select the best roles for a debate topic."""
        return self.role_selector.auto_select_roles(topic, available_roles, num_roles)

    def create_role_from_topic(self, 
                             topic: str, 
                             role_position: str = "supporting", 
                             custom_persona: Optional[str] = None) -> EnhancedRole:
        """
        Create a new role based on a topic and position.
        
        Args:
            topic: The debate topic
            role_position: Position in the debate ('supporting', 'opposing', 'neutral', 'moderator')
            custom_persona: Custom persona to use instead of generating one
        
        Returns:
            EnhancedRole: The newly created role
        """
        # Analyze the topic
        topic_analysis = self.analyze_topic(topic)
        
        # Generate role name based on topic and position
        if custom_persona:
            persona = custom_persona
            role_name = self._generate_role_name_from_persona(custom_persona)
        else:
            persona = self._generate_role_persona(topic, role_position, topic_analysis)
            role_name = self._generate_role_name(topic, role_position)
        
        # Determine appropriate model configuration based on the topic
        model_config = self._generate_model_config_for_topic(topic_analysis)
        
        # Create and return the role
        role = EnhancedRole(
            name=role_name,
            persona=persona,
            tools=[],
            model_configs=[model_config],
            debate_model_config=model_config
        )
        
        return role

    def _generate_role_name(self, topic: str, position: str) -> str:
        """Generate an appropriate role name based on topic and position."""
        # Extract key terms from topic
        words = topic.lower().replace('?', '').replace('!', '').replace('.', '').split()
        # Filter to significant words
        significant_words = [w for w in words if len(w) > 3 and w not in ['the', 'and', 'for', 'with', 'are', 'you']]
        
        if significant_words:
            base_name = significant_words[0].capitalize()
        else:
            base_name = "Expert"
            
        position_suffixes = {
            'supporting': 'Supporter',
            'opposing': 'Challenger',
            'neutral': 'Observer',
            'moderator': 'Moderator'
        }
        
        suffix = position_suffixes.get(position, 'Expert')
        role_name = f"{base_name}{suffix}"
        
        # Ensure it's a valid filename
        role_name = "".join(c for c in role_name if c.isalnum() or c == '_')[:50]
        
        return role_name

    def _generate_role_name_from_persona(self, persona: str) -> str:
        """Generate a role name based on the persona description."""
        # Extract key terms from persona
        import re
        words = re.findall(r'\b\w+\b', persona.lower())
        # Find profession-related words
        profession_keywords = [
            'expert', 'analyst', 'specialist', 'advocate', 'champion', 'critic', 
            'advisor', 'consultant', 'researcher', 'scholar', 'philosopher',
            'engineer', 'scientist', 'economist', 'lawyer', 'doctor', 'teacher'
        ]
        
        for word in words:
            if word in profession_keywords:
                return word.capitalize()
        
        # If no profession word found, use first significant word
        significant_words = [w for w in words if len(w) > 4 and w not in ['this', 'that', 'with', 'have', 'from']]
        if significant_words:
            return significant_words[0].capitalize()[:20]
        
        return "NewRole"

    def _generate_role_persona(self, topic: str, position: str, topic_analysis: Dict) -> str:
        """Generate a persona for the role based on topic and position."""
        # Define base templates for different positions
        templates = {
            'supporting': f"You are a strong advocate for the topic: '{topic}'. Your role is to present arguments in favor of this position, highlighting benefits, opportunities, and positive outcomes. Focus on constructive solutions and optimistic perspectives.",
            'opposing': f"You are a critical thinker analyzing the topic: '{topic}'. Your role is to present counter-arguments, identify risks, challenges, and potential negative consequences. Focus on critical analysis and constructive skepticism.",
            'neutral': f"You are an impartial observer of the topic: '{topic}'. Your role is to provide balanced perspective, consider multiple viewpoints, and facilitate understanding of different positions. Focus on objective analysis.",
            'moderator': f"You are a debate moderator discussing the topic: '{topic}'. Your role is to facilitate fair discussion, ensure all viewpoints are heard, and guide participants toward deeper understanding. Focus on process and balanced inquiry."
        }
        
        base_persona = templates.get(position, f"You are an expert discussing: '{topic}'. Provide thoughtful insights on this subject.")
        
        # Enhance the persona based on domain expertise
        domains = topic_analysis.get('domains', [])
        if domains:
            domain_specific = f" You specialize in {', '.join(domains)}."
            base_persona += domain_specific
            
        return base_persona

    def _generate_model_config_for_topic(self, topic_analysis: Dict) -> RoleModelConfig:
        """Generate appropriate model configuration based on topic analysis."""
        # Default configuration
        temperature = 0.7
        max_tokens = 4000
        
        # Adjust based on complexity
        complexity = topic_analysis.get('complexity_score', 0.5)
        if complexity > 0.7:
            # More complex topics may need more creativity
            temperature = min(0.9, 0.5 + complexity * 0.5)
        else:
            # Simpler topics can use lower temperature for consistency
            temperature = max(0.3, 0.5 - (0.5 - complexity) * 0.4)
        
        # Determine appropriate model based on debate type
        debate_type = topic_analysis.get('debate_type', 'general')
        model_providers = {
            'technical': 'ollama/deepseek-coder:6.7b',
            'ethical': 'ollama/yi:9b',
            'social': 'ollama/qwen:7b',
            'political': 'ollama/gemma:7b',
            'economic': 'ollama/mistral:7b'
        }
        
        model_name = model_providers.get(debate_type, 'ollama/llama3:8b')
        
        return RoleModelConfig(
            model_name=model_name,
            provider='ollama',  # Default to Ollama for local models
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.2,
            is_primary=True
        )

    def save_role_to_file(self, role: EnhancedRole, file_path: Optional[str] = None) -> bool:
        """
        Save a role to a YAML file.

        Args:
            role: The role to save
            file_path: Optional specific file path; if not provided, uses role name

        Returns:
            bool: True if successful, False otherwise
        """
        if file_path is None:
            # Sanitize role name for use as filename
            sanitized_name = re.sub(r'[^\w\s-]', '_', role.name)
            sanitized_name = re.sub(r'[-\s]+', '_', sanitized_name).strip('_')
            file_path = self.roles_dir / f"{sanitized_name}.yaml"
        else:
            file_path = Path(file_path)

        try:
            # Validate role before saving
            if not role.name or not role.persona:
                logger.error("Role must have both name and persona to be saved")
                return False

            # Check if file already exists and warn user
            if file_path.exists():
                logger.warning(f"Role file already exists: {file_path}, will be overwritten")

            # Convert role to dictionary for YAML serialization
            role_dict = {
                'name': role.name,  # Include the role name in the file
                'persona': role.persona,
                'tools': role.tools,
                'model_configs': [
                    {
                        'model_name': config.model_name,
                        'provider': config.provider,
                        'max_tokens': config.max_tokens,
                        'temperature': config.temperature,
                        'top_p': config.top_p,
                        'frequency_penalty': config.frequency_penalty,
                        'presence_penalty': config.presence_penalty,
                        'is_primary': config.is_primary
                    }
                    for config in role.model_configs
                ]
            }

            # Add debate model config if present
            if role.debate_model_config:
                role_dict['debate_model_config'] = {
                    'model_name': role.debate_model_config.model_name,
                    'provider': role.debate_model_config.provider,
                    'max_tokens': role.debate_model_config.max_tokens,
                    'temperature': role.debate_model_config.temperature,
                    'top_p': role.debate_model_config.top_p,
                    'frequency_penalty': role.debate_model_config.frequency_penalty,
                    'presence_penalty': role.debate_model_config.presence_penalty,
                    'is_primary': role.debate_model_config.is_primary
                }

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(role_dict, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"Successfully saved role '{role.name}' to {file_path}")
            return True
        except PermissionError:
            logger.error(f"Permission denied when saving role to {file_path}")
            return False
        except OSError as e:
            logger.error(f"OS error when saving role to {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving role to file: {e}")
            return False

    def load_role_from_file(self, file_name: str) -> Optional[EnhancedRole]:
        """Load a role from a YAML file."""
        # Sanitize file_name to prevent directory traversal
        sanitized_name = re.sub(r'[^\w\s-]', '_', file_name)
        sanitized_name = re.sub(r'[-\s]+', '_', sanitized_name).strip('_')

        file_path = self.roles_dir / f"{sanitized_name}.yaml"

        if not file_path.exists():
            logger.warning(f"Role file does not exist: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                role_data = yaml.safe_load(f)

            if not isinstance(role_data, dict):
                logger.error(f"Role file {file_path} does not contain valid YAML dictionary")
                return None

            # Validate required fields
            if 'persona' not in role_data:
                logger.error(f"Role file {file_path} missing required 'persona' field")
                return None

            # Process model configs with validation
            model_configs_data = role_data.get('model_configs', [])
            model_configs = []

            for config_data in model_configs_data:
                try:
                    config = RoleModelConfig(
                        model_name=config_data.get('model_name'),
                        provider=config_data.get('provider', 'openai'),
                        max_tokens=config_data.get('max_tokens', 4000),
                        temperature=config_data.get('temperature', 0.7),
                        top_p=config_data.get('top_p', 1.0),
                        frequency_penalty=config_data.get('frequency_penalty', 0.0),
                        presence_penalty=config_data.get('presence_penalty', 0.0),
                        is_primary=config_data.get('is_primary', False)
                    )
                    model_configs.append(config)
                except Exception as e:
                    logger.error(f"Error creating RoleModelConfig from data {config_data}: {e}")
                    # Skip invalid configs but continue with others

            # If no valid model configs were created, add a default one
            if not model_configs:
                logger.warning(f"No valid model configs found for role {file_name}, using default")
                model_configs.append(RoleModelConfig(
                    model_name="ollama/llama3:8b",
                    provider="ollama",
                    max_tokens=4000,
                    temperature=0.7,
                    is_primary=True
                ))

            # Create the role object with the file name as the role name
            role_name = role_data.get('name', file_name)  # Use name from file or default to file_name
            role = EnhancedRole(
                name=role_name,
                persona=role_data.get('persona', ''),
                tools=role_data.get('tools', []),
                model_configs=model_configs
            )

            # Load debate model config if present
            debate_config_data = role_data.get('debate_model_config')
            if debate_config_data:
                try:
                    role.debate_model_config = RoleModelConfig(
                        model_name=debate_config_data.get('model_name'),
                        provider=debate_config_data.get('provider', 'openai'),
                        max_tokens=debate_config_data.get('max_tokens', 4000),
                        temperature=debate_config_data.get('temperature', 0.7),
                        top_p=debate_config_data.get('top_p', 1.0),
                        frequency_penalty=debate_config_data.get('frequency_penalty', 0.0),
                        presence_penalty=debate_config_data.get('presence_penalty', 0.0),
                        is_primary=debate_config_data.get('is_primary', False)
                    )
                except Exception as e:
                    logger.error(f"Error creating debate model config from data {debate_config_data}: {e}")

            logger.info(f"Successfully loaded role '{role.name}' from {file_path}")
            return role
        except PermissionError:
            logger.error(f"Permission denied when reading role file: {file_path}")
            return None
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in role file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading role from file {file_path}: {e}")
            return None

    async def check_model_availability(self) -> List[str]:
        """Check and return available models."""
        if self.available_models_cache is not None:
            logger.debug("Returning cached model availability list")
            return self.available_models_cache

        available_models = []

        if self.model_provider:
            try:
                available_models = self.model_provider.get_model_list()
                self.available_models_cache = available_models
                logger.info(f"Retrieved {len(available_models)} models from provider")
            except Exception as e:
                logger.error(f"Error checking model availability from provider: {e}")
                # Continue to fallback option
        else:
            logger.info("No model provider specified, checking local Ollama models")

        # Fallback: scan Ollama models if no provider or provider failed
        if not available_models:
            try:
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    # Parse model names from ollama list output
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():  # Skip empty lines
                            parts = line.split()
                            if parts:
                                model_name = parts[0]  # First column is model name
                                # Only add if not already present and format properly
                                full_model_name = f"ollama/{model_name}" if not model_name.startswith("ollama/") else model_name
                                if full_model_name not in available_models:
                                    available_models.append(full_model_name)
                    logger.info(f"Found {len(available_models)} local models via Ollama")
                else:
                    logger.warning("Ollama command returned non-zero exit code")
            except FileNotFoundError:
                logger.warning("Ollama not found. Please install Ollama to use local models.")
            except subprocess.TimeoutExpired:
                logger.warning("Ollama command timed out. Please check if Ollama is running.")
            except Exception as e:
                logger.error(f"Error checking Ollama models: {e}")

        self.available_models_cache = available_models
        return available_models

    async def update_role_models(self, role: EnhancedRole) -> EnhancedRole:
        """
        Update role's model configurations based on available models.
        If the configured models are not available, find suitable replacements.
        """
        try:
            available_models = await self.check_model_availability()

            if not available_models:
                logger.warning(f"No models available for role {role.name}, keeping original model configurations")
                return role

            updated_configs = []
            for config in role.model_configs:
                if config.model_name in available_models:
                    # Model is available, keep as is
                    updated_configs.append(config)
                else:
                    logger.info(f"Model {config.model_name} not available for role {role.name}, finding replacement")
                    # Find a suitable replacement
                    replacement = self._find_best_model_replacement(config, available_models)
                    if replacement:
                        new_config = RoleModelConfig(
                            model_name=replacement,
                            provider=config.provider,
                            max_tokens=config.max_tokens,
                            temperature=config.temperature,
                            top_p=config.top_p,
                            frequency_penalty=config.frequency_penalty,
                            presence_penalty=config.presence_penalty,
                            is_primary=config.is_primary
                        )
                        updated_configs.append(new_config)
                        logger.info(f"Replaced model {config.model_name} with {replacement} for role {role.name}")
                    else:
                        logger.warning(f"Could not find replacement for model {config.model_name} for role {role.name}")
                        # Keep the original config as fallback if no replacement is found
                        updated_configs.append(config)

            # Update debate model config if it exists
            updated_debate_config = None
            if role.debate_model_config:
                if role.debate_model_config.model_name in available_models:
                    updated_debate_config = role.debate_model_config
                    logger.debug(f"Debate model {role.debate_model_config.model_name} is available for role {role.name}")
                else:
                    logger.info(f"Debate model {role.debate_model_config.model_name} not available for role {role.name}, finding replacement")
                    replacement = self._find_best_model_replacement(
                        role.debate_model_config,
                        available_models
                    )
                    if replacement:
                        updated_debate_config = RoleModelConfig(
                            model_name=replacement,
                            provider=role.debate_model_config.provider,
                            max_tokens=role.debate_model_config.max_tokens,
                            temperature=role.debate_model_config.temperature,
                            top_p=role.debate_model_config.top_p,
                            frequency_penalty=role.debate_model_config.frequency_penalty,
                            presence_penalty=role.debate_model_config.presence_penalty,
                            is_primary=role.debate_model_config.is_primary
                        )
                        logger.info(f"Replaced debate model {role.debate_model_config.model_name} with {replacement} for role {role.name}")
                    else:
                        logger.warning(f"Could not find replacement for debate model {role.debate_model_config.model_name} for role {role.name}")

            # Create updated role
            updated_role = EnhancedRole(
                name=role.name,
                persona=role.persona,
                tools=role.tools,
                model_configs=updated_configs,
                debate_model_config=updated_debate_config
            )

            logger.info(f"Successfully updated models for role {role.name}")
            return updated_role
        except Exception as e:
            logger.error(f"Error updating models for role {role.name}: {e}")
            # Return original role if update fails
            return role

    def _find_best_model_replacement(self, original_config: RoleModelConfig, 
                                   available_models: List[str]) -> Optional[str]:
        """Find the best available model to replace the original."""
        original_model = original_config.model_name
        original_provider = original_config.provider
        
        # First try to find a model from the same provider
        same_provider_models = [model for model in available_models 
                              if model.startswith(f"{original_provider}/")]
        
        if same_provider_models:
            # If same provider models exist, return the first one
            return same_provider_models[0]
        
        # If no same provider models, look for similar model types
        # Extract keywords from original model name
        original_parts = original_model.split('/')
        model_name = original_parts[-1] if len(original_parts) > 1 else original_parts[0]
        
        # Look for models with similar names or characteristics
        similarity_keywords = [
            'llama', 'gemma', 'mistral', 'qwen', 'yi', 'yi', 'deepseek'
        ]
        
        for keyword in similarity_keywords:
            if keyword in model_name.lower():
                for available_model in available_models:
                    if keyword in available_model.lower():
                        return available_model
        
        # If no similar models found, return the first available model
        if available_models:
            return available_models[0]
        
        return None

    async def create_and_save_role_for_topic(self, topic: str, position: str = "supporting") -> Optional[EnhancedRole]:
        """
        Create and save a role for a specified topic.
        
        Args:
            topic: The debate topic
            position: Position in the debate ('supporting', 'opposing', 'neutral')
        
        Returns:
            EnhancedRole if successful, None otherwise
        """
        # Create the role
        role = self.create_role_from_topic(topic, position)
        
        # Update models based on availability
        updated_role = await self.update_role_models(role)
        
        # Save to file
        success = self.save_role_to_file(updated_role)
        
        if success:
            return updated_role
        else:
            print(f"Failed to save role {updated_role.name}")
            return None