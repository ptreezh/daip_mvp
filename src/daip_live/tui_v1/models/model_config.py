"""
Model Configuration for Model Switching System

Handles model configuration management, validation, and serialization.
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Configuration types"""

    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CUSTOM = "custom"


class ModelConfig:
    """Model configuration management"""

    def __init__(
        self,
        name: str,
        provider: str,
        model_type: str,
        api_key: str,
        config_type: ConfigType = ConfigType.CHAT,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        base_url: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        rate_limit_rpm: Optional[int] = None,
        specialization: Optional[str] = None,
        description: str = "",
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        config_id: Optional[str] = None,
    ):
        self.id = config_id or str(uuid.uuid4())
        self.name = name
        self.provider = provider
        self.model_type = model_type
        self.config_type = config_type
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.base_url = base_url
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.rate_limit_rpm = rate_limit_rpm
        self.specialization = specialization
        self.description = description
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.is_active = True
        self.usage_count = 0
        self.last_used: Optional[datetime] = None

    def update_parameter(self, parameter: str, value: Any) -> None:
        """Update a configuration parameter"""
        if hasattr(self, parameter):
            setattr(self, parameter, value)
            self.updated_at = datetime.now()
            logger.debug(
                f"Updated parameter {parameter} to {value} for model {self.name}"
            )
        else:
            logger.warning(f"Unknown parameter: {parameter}")

    def get_parameters(self) -> dict[str, Any]:
        """Get all model parameters"""
        return {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
        }

    def is_valid(self) -> bool:
        """Validate model configuration"""
        # Check required fields
        if not self.name or not self.provider or not self.model_type:
            return False

        # Check API key
        if not self.api_key or len(self.api_key) < 3:
            return False

        # Validate numeric parameters
        if not (0.0 <= self.temperature <= 2.0):
            return False

        if not (0.0 <= self.top_p <= 1.0):
            return False

        if not (-2.0 <= self.frequency_penalty <= 2.0):
            return False

        if not (-2.0 <= self.presence_penalty <= 2.0):
            return False

        if self.max_tokens <= 0:
            return False

        if self.timeout <= 0:
            return False

        if self.retry_attempts < 0:
            return False

        return True

    def validate_for_task(self, task_type: str) -> bool:
        """Validate if configuration is suitable for specific task type"""
        if self.specialization and self.specialization.lower() == task_type.lower():
            return True

        # Check if tags indicate suitability
        if task_type.lower() in [tag.lower() for tag in self.tags]:
            return True

        # Default validation based on config type
        if (
            task_type in ["chat", "conversation"]
            and self.config_type == ConfigType.CHAT
        ):
            return True

        if (
            task_type in ["completion", "generation"]
            and self.config_type == ConfigType.COMPLETION
        ):
            return True

        if (
            task_type in ["embedding", "vector"]
            and self.config_type == ConfigType.EMBEDDING
        ):
            return True

        return False

    def record_usage(self) -> None:
        """Record model usage"""
        self.usage_count += 1
        self.last_used = datetime.now()

    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics"""
        return {
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat(),
            "days_since_creation": (datetime.now() - self.created_at).days,
        }

    def clone(self, new_name: Optional[str] = None) -> "ModelConfig":
        """Create a copy of the configuration"""
        return ModelConfig(
            name=new_name or f"{self.name}_copy",
            provider=self.provider,
            model_type=self.model_type,
            api_key=self.api_key,
            config_type=self.config_type,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            base_url=self.base_url,
            timeout=self.timeout,
            retry_attempts=self.retry_attempts,
            rate_limit_rpm=self.rate_limit_rpm,
            specialization=self.specialization,
            description=self.description,
            tags=self.tags.copy(),
            metadata=self.metadata.copy(),
        )

    def to_dict(self, include_sensitive: bool = False) -> dict[str, Any]:
        """Convert configuration to dictionary"""
        data = {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "model_type": self.model_type,
            "config_type": self.config_type.value,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "rate_limit_rpm": self.rate_limit_rpm,
            "specialization": self.specialization,
            "description": self.description,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }

        # Include API key only if explicitly requested
        if include_sensitive:
            data["api_key"] = self.api_key

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelConfig":
        """Create configuration from dictionary"""
        # Handle config_type enum
        if "config_type" in data and isinstance(data["config_type"], str):
            data["config_type"] = ConfigType(data["config_type"])

        # Handle datetime fields
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        if "last_used" in data and data["last_used"]:
            if isinstance(data["last_used"], str):
                data["last_used"] = datetime.fromisoformat(data["last_used"])

        config = cls(
            name=data["name"],
            provider=data["provider"],
            model_type=data["model_type"],
            api_key=data.get("api_key", ""),
            config_type=data.get("config_type", ConfigType.CHAT),
            max_tokens=data.get("max_tokens", 2048),
            temperature=data.get("temperature", 0.7),
            top_p=data.get("top_p", 1.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            presence_penalty=data.get("presence_penalty", 0.0),
            base_url=data.get("base_url"),
            timeout=data.get("timeout", 30),
            retry_attempts=data.get("retry_attempts", 3),
            rate_limit_rpm=data.get("rate_limit_rpm"),
            specialization=data.get("specialization"),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            config_id=data.get("id"),
        )

        # Restore additional attributes
        if "created_at" in data:
            config.created_at = data["created_at"]

        if "updated_at" in data:
            config.updated_at = data["updated_at"]

        if "last_used" in data:
            config.last_used = data["last_used"]

        if "is_active" in data:
            config.is_active = data["is_active"]

        if "usage_count" in data:
            config.usage_count = data["usage_count"]

        return config

    def to_json(self, include_sensitive: bool = False, indent: int = 2) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.to_dict(include_sensitive), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "ModelConfig":
        """Create configuration from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def merge_with(self, other: "ModelConfig") -> "ModelConfig":
        """Merge this configuration with another, with other taking precedence"""
        merged_data = self.to_dict(include_sensitive=True)
        other_data = other.to_dict(include_sensitive=True)

        # Merge dictionaries, with other taking precedence
        for key, value in other_data.items():
            if value is not None:
                merged_data[key] = value

        return ModelConfig.from_dict(merged_data)

    def get_effective_parameters(
        self, overrides: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Get effective parameters with optional overrides"""
        params = self.get_parameters()

        if overrides:
            params.update(overrides)

        return params

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> dict[str, float]:
        """Estimate cost for a given request"""
        # This is a simplified cost estimation
        # In a real implementation, you'd use actual pricing from providers

        # Default pricing (per 1K tokens)
        pricing = {
            "openai": {"input": 0.001, "output": 0.002},
            "anthropic": {"input": 0.0008, "output": 0.0024},
            "local": {"input": 0.0, "output": 0.0},
            "custom": {"input": 0.001, "output": 0.002},
        }

        provider_pricing = pricing.get(self.provider.lower(), pricing["custom"])

        input_cost = (input_tokens / 1000) * provider_pricing["input"]
        output_cost = (output_tokens / 1000) * provider_pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "currency": "USD",
        }

    def __str__(self) -> str:
        """String representation"""
        return f"ModelConfig({self.name}@{self.provider})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"ModelConfig(id={self.id[:8]}..., name='{self.name}', "
            f"provider='{self.provider}', type={self.model_type}, "
            f"active={self.is_active}, usage={self.usage_count})"
        )

    def __eq__(self, other) -> bool:
        """Equality comparison based on ID"""
        if isinstance(other, ModelConfig):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id)
