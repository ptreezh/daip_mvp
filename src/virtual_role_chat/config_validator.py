"""Configuration validation for the Virtual Role Chat System.

This module provides functionality to validate chat room configurations,
including mode-specific validation and interaction rules validation.
"""

import logging
from typing import Any

from .models import ChatRoomConfig, ValidationResult

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""
    pass


class ConfigValidator:
    """Validator for chat room configurations."""
    
    # Define valid modes and their required parameters
    VALID_MODES = ["free_form", "structured", "debate"]
    
    MODE_SCHEMAS = {
        "free_form": {
            "required": [],
            "optional": ["max_response_length", "allow_interruptions", "moderation_level"]
        },
        "structured": {
            "required": ["phases"],
            "optional": ["time_limit_per_phase", "moderation_level", "allow_phase_skipping"]
        },
        "debate": {
            "required": ["debate_format"],
            "optional": [
                "time_limit", 
                "turn_based", 
                "moderation_level", 
                "consensus_strategy",
                "proposition_roles",
                "opposition_roles"
            ]
        }
    }
    
    # Define valid values for specific parameters
    VALID_VALUES = {
        "moderation_level": ["light", "moderate", "strict"],
        "debate_format": ["oxford", "lincoln_douglas", "cross_examination", "parliamentary", "free_form"],
        "consensus_strategy": ["simple_majority_vote", "weighted_vote", "consensus_building"]
    }
    
    def __init__(self):
        """Initialize the ConfigValidator."""
        pass
    
    def validate_config(self, config: ChatRoomConfig) -> ValidationResult:
        """Validate a chat room configuration.
        
        Args:
            config: The configuration to validate.
            
        Returns:
            ValidationResult indicating whether the configuration is valid.
        """
        # Check that the mode is valid
        if config.mode not in self.VALID_MODES:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Invalid mode: {config.mode}. Valid modes are: {', '.join(self.VALID_MODES)}",
                suggested_correction=f"Use one of the valid modes: {', '.join(self.VALID_MODES)}"
            )
        
        # Validate mode-specific configuration
        mode_validation = self._validate_mode_config(config.mode, config.interaction_rules)
        if not mode_validation.is_valid:
            return mode_validation
        
        # Validate general configuration
        if not config.name:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning="Chat room name is required",
                suggested_correction="Provide a name for the chat room"
            )
        
        if not config.topic:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning="Chat room topic is required",
                suggested_correction="Provide a topic for the chat room"
            )
        
        # All validations passed
        return ValidationResult(
            is_valid=True,
            confidence=1.0,
            reasoning="Chat room configuration is valid",
            suggested_correction=None
        )
    
    def _validate_mode_config(self, mode: str, interaction_rules: dict[str, Any]) -> ValidationResult:
        """Validate mode-specific configuration.
        
        Args:
            mode: The chat room mode.
            interaction_rules: The interaction rules for the mode.
            
        Returns:
            ValidationResult indicating whether the configuration is valid.
        """
        # Check if mode is valid
        if mode not in self.VALID_MODES:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Invalid mode: {mode}. Valid modes are: {', '.join(self.VALID_MODES)}",
                suggested_correction=f"Use one of the valid modes: {', '.join(self.VALID_MODES)}"
            )
        
        schema = self.MODE_SCHEMAS.get(mode, {"required": [], "optional": []})
        
        # Check required parameters
        missing_params = []
        for param in schema["required"]:
            if param not in interaction_rules:
                missing_params.append(param)
        
        if missing_params:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Missing required parameters for {mode} mode: {', '.join(missing_params)}",
                suggested_correction=f"Add the following parameters to interaction_rules: {', '.join(missing_params)}"
            )
        
        # Check for invalid parameters
        valid_params = schema["required"] + schema["optional"]
        invalid_params = []
        for param in interaction_rules:
            if param not in valid_params:
                invalid_params.append(param)
        
        if invalid_params:
            return ValidationResult(
                is_valid=False,
                confidence=0.8,  # Lower confidence as these are warnings
                reasoning=f"Invalid parameters for {mode} mode: {', '.join(invalid_params)}",
                suggested_correction=f"Remove or rename the following parameters: {', '.join(invalid_params)}"
            )
        
        # Validate parameter values
        for param, value in interaction_rules.items():
            if param in self.VALID_VALUES and value not in self.VALID_VALUES[param]:
                return ValidationResult(
                    is_valid=False,
                    confidence=1.0,
                    reasoning=f"Invalid value for {param}: {value}. Valid values are: {', '.join(self.VALID_VALUES[param])}",
                    suggested_correction=f"Use one of the valid values for {param}: {', '.join(self.VALID_VALUES[param])}"
                )
        
        # Mode-specific validations
        if mode == "structured":
            return self._validate_structured_mode(interaction_rules)
        elif mode == "debate":
            return self._validate_debate_mode(interaction_rules)
        
        # All validations passed
        return ValidationResult(
            is_valid=True,
            confidence=1.0,
            reasoning=f"Configuration for {mode} mode is valid",
            suggested_correction=None
        )
    
    def _validate_structured_mode(self, interaction_rules: dict[str, Any]) -> ValidationResult:
        """Validate structured mode configuration.
        
        Args:
            interaction_rules: The interaction rules for structured mode.
            
        Returns:
            ValidationResult indicating whether the configuration is valid.
        """
        phases = interaction_rules.get("phases", [])
        
        if not isinstance(phases, list) or len(phases) == 0:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning="Structured mode requires at least one phase",
                suggested_correction="Define at least one phase in the phases list"
            )
        
        # Check that phases are strings
        invalid_phases = []
        for phase in phases:
            if not isinstance(phase, str):
                invalid_phases.append(str(phase))
        
        if invalid_phases:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Invalid phases: {', '.join(invalid_phases)}. Phases must be strings.",
                suggested_correction="Ensure all phases are strings"
            )
        
        # Check time limits if specified
        time_limits = interaction_rules.get("time_limit_per_phase", {})
        if time_limits and not isinstance(time_limits, dict):
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning="time_limit_per_phase must be a dictionary mapping phase names to time limits",
                suggested_correction="Format time_limit_per_phase as a dictionary: {'phase_name': seconds}"
            )
        
        # All validations passed
        return ValidationResult(
            is_valid=True,
            confidence=1.0,
            reasoning="Structured mode configuration is valid",
            suggested_correction=None
        )
    
    def _validate_debate_mode(self, interaction_rules: dict[str, Any]) -> ValidationResult:
        """Validate debate mode configuration.
        
        Args:
            interaction_rules: The interaction rules for debate mode.
            
        Returns:
            ValidationResult indicating whether the configuration is valid.
        """
        debate_format = interaction_rules.get("debate_format")
        
        # Validate debate_format value
        if debate_format not in self.VALID_VALUES.get("debate_format", []):
            valid_formats = self.VALID_VALUES.get("debate_format", [])
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Invalid debate format: {debate_format}. Valid formats are: {', '.join(valid_formats)}",
                suggested_correction=f"Use one of the valid debate formats: {', '.join(valid_formats)}"
            )
        
        # Additional validations for specific debate formats
        if debate_format == "oxford":
            if "proposition_roles" not in interaction_rules or "opposition_roles" not in interaction_rules:
                return ValidationResult(
                    is_valid=False,
                    confidence=1.0,
                    reasoning="Oxford debate format requires proposition_roles and opposition_roles",
                    suggested_correction="Define proposition_roles and opposition_roles lists"
                )
            
            # Check that proposition_roles and opposition_roles are lists
            if not isinstance(interaction_rules.get("proposition_roles"), list):
                return ValidationResult(
                    is_valid=False,
                    confidence=1.0,
                    reasoning="proposition_roles must be a list",
                    suggested_correction="Define proposition_roles as a list of role IDs"
                )
            
            if not isinstance(interaction_rules.get("opposition_roles"), list):
                return ValidationResult(
                    is_valid=False,
                    confidence=1.0,
                    reasoning="opposition_roles must be a list",
                    suggested_correction="Define opposition_roles as a list of role IDs"
                )
        
        # Check turn_based parameter
        turn_based = interaction_rules.get("turn_based")
        if turn_based is not None and not isinstance(turn_based, bool):
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning="turn_based must be a boolean value",
                suggested_correction="Set turn_based to true or false"
            )
        
        # Check time_limit parameter
        time_limit = interaction_rules.get("time_limit")
        if time_limit is not None:
            if not isinstance(time_limit, int) or time_limit <= 0:
                return ValidationResult(
                    is_valid=False,
                    confidence=1.0,
                    reasoning="time_limit must be a positive integer",
                    suggested_correction="Set time_limit to a positive number of seconds"
                )
        
        # All validations passed
        return ValidationResult(
            is_valid=True,
            confidence=1.0,
            reasoning="Debate mode configuration is valid",
            suggested_correction=None
        )
    
    def generate_mode_template(self, mode: str) -> dict[str, Any]:
        """Generate a template configuration for a specific mode.
        
        Args:
            mode: The chat room mode.
            
        Returns:
            A template configuration for the specified mode.
            
        Raises:
            ValueError: If the mode is invalid.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Valid modes are: {', '.join(self.VALID_MODES)}")
        
        if mode == "free_form":
            return {
                "max_response_length": 500,
                "allow_interruptions": True,
                "moderation_level": "moderate"
            }
        elif mode == "structured":
            return {
                "phases": ["introduction", "exploration", "synthesis"],
                "time_limit_per_phase": {
                    "introduction": 300,
                    "exploration": 600,
                    "synthesis": 300
                },
                "allow_phase_skipping": False,
                "moderation_level": "moderate"
            }
        elif mode == "debate":
            return {
                "debate_format": "oxford",
                "proposition_roles": [],
                "opposition_roles": [],
                "turn_based": True,
                "time_limit": 300,
                "consensus_strategy": "consensus_building",
                "moderation_level": "moderate"
            }
    
    def get_mode_schema(self, mode: str) -> dict[str, list[str]]:
        """Get the schema for a specific mode.
        
        Args:
            mode: The chat room mode.
            
        Returns:
            The schema for the specified mode.
            
        Raises:
            ValueError: If the mode is invalid.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Valid modes are: {', '.join(self.VALID_MODES)}")
        
        return self.MODE_SCHEMAS[mode]
    
    def get_valid_modes(self) -> list[str]:
        """Get all valid chat room modes.
        
        Returns:
            List of valid mode names.
        """
        return self.VALID_MODES
    
    def get_mode_requirements(self, mode: str) -> dict[str, Any]:
        """Get requirements for a specific chat mode.
        
        Args:
            mode: The mode to get requirements for.
            
        Returns:
            Dictionary containing mode requirements.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Valid modes are: {', '.join(self.VALID_MODES)}")
        
        schema = self.MODE_SCHEMAS[mode]
        return {
            "required_params": schema["required"],
            "optional_params": schema["optional"],
            "valid_values": {
                param: self.VALID_VALUES[param]
                for param in schema["required"] + schema["optional"]
                if param in self.VALID_VALUES
            }
        }
    
    def suggest_rules_for_mode(self, mode: str) -> dict[str, Any]:
        """Get suggested rules for a specific mode.
        
        Args:
            mode: The mode to get suggestions for.
            
        Returns:
            Dictionary with suggested rules.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Valid modes are: {', '.join(self.VALID_MODES)}")
        
        return self.generate_mode_template(mode)
    
    def _validate_interaction_rules(self, rules: dict[str, Any], mode: str) -> ValidationResult:
        """Validate interaction rules for a specific mode.
        
        Args:
            rules: The interaction rules to validate.
            mode: The chat mode.
            
        Returns:
            ValidationResult indicating whether the rules are valid.
        """
        if mode not in self.VALID_MODES:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Invalid mode: {mode}. Valid modes are: {', '.join(self.VALID_MODES)}",
                suggested_correction=f"Use one of the valid modes: {', '.join(self.VALID_MODES)}"
            )
        
        return self._validate_mode_config(mode, rules)