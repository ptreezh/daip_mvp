"""@Time    : 2025-08-06 10:15:00
@Author  : DAIP-LIVE Team
@File    : configuration_management_system.py
@Description:
    Unified Configuration Management System
    Provides centralized configuration management for DAIP-LIVE services with environment-specific settings.
"""

import json
import logging
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, TypeVar, Union

import yaml
from jsonschema import ValidationError, validate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigType(Enum):
    """Configuration types."""
    APPLICATION = "application"
    DATABASE = "database"
    SECURITY = "security"
    SERVICES = "services"
    MONITORING = "monitoring"
    FEATURES = "features"


@dataclass
class ConfigSource:
    """Configuration source information."""
    source_type: str  # file, environment, remote, default
    source_path: Optional[str] = None
    priority: int = 0
    is_active: bool = True
    last_updated: Optional[datetime] = None


@dataclass
class ConfigValue:
    """Configuration value with metadata."""
    key: str
    value: Any
    type: str
    source: str
    is_sensitive: bool = False
    is_required: bool = False
    validation_rules: Optional[dict[str, Any]] = None
    description: str = ""
    last_modified: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigSchema:
    """Configuration schema definition."""
    name: str
    version: str
    schema: dict[str, Any]
    description: str = ""
    environment: Optional[Environment] = None


class ConfigurationManager:
    """Unified configuration management system."""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.config_values: dict[str, ConfigValue] = {}
        self.config_schemas: dict[str, ConfigSchema] = {}
        self.config_sources: list[ConfigSource] = []
        self.watchers: dict[str, list[callable]] = {}
        self.lock = threading.Lock()
        self.config_dir = Path("config")
        self.cache_dir = Path("cache/config")
        
        # Create directories
        self.config_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize default configuration
        self._initialize_default_config()
        self._initialize_schemas()
        
        logger.info(f"Configuration Manager initialized for {environment.value} environment")
    
    def _initialize_default_config(self):
        """Initialize default configuration values."""
        default_config = {
            # Application configuration
            "app.name": "DAIP-LIVE",
            "app.version": "1.0.0",
            "app.debug": self.environment == Environment.DEVELOPMENT,
            "app.log_level": "DEBUG" if self.environment == Environment.DEVELOPMENT else "INFO",
            "app.host": "0.0.0.0",
            "app.port": 8000,
            
            # Database configuration
            "database.url": "sqlite:///daip_live.db",
            "database.pool_size": 10,
            "database.max_overflow": 20,
            "database.pool_timeout": 30,
            "database.pool_recycle": 3600,
            
            # Security configuration
            "security.secret_key": "your-secret-key-change-in-production",
            "security.jwt_algorithm": "HS256",
            "security.jwt_expiration": 3600,
            "security.password_min_length": 8,
            "security.session_timeout": 3600,
            "security.rate_limit_requests": 100,
            "security.rate_limit_window": 60,
            
            # Service configuration
            "services.backend.host": "localhost",
            "services.backend.port": 8002,
            "services.web.host": "localhost",
            "services.web.port": 8001,
            "services.gateway.host": "localhost",
            "services.gateway.port": 8000,
            "services.registry.host": "localhost",
            "services.registry.port": 8003,
            
            # Monitoring configuration
            "monitoring.enabled": True,
            "monitoring.health_check_interval": 30,
            "monitoring.metrics_collection_interval": 60,
            "monitoring.alert_enabled": True,
            "monitoring.log_retention_days": 30,
            
            # Feature flags
            "features.api_documentation": True,
            "features.service_discovery": True,
            "features.load_balancing": True,
            "features.caching": True,
            "features.monitoring": True,
            "features.authentication": True,
            "features.rate_limiting": True
        }
        
        for key, value in default_config.items():
            self.config_values[key] = ConfigValue(
                key=key,
                value=value,
                type=type(value).__name__,
                source="default",
                description=f"Default {key} configuration"
            )
        
        # Add default source
        self.config_sources.append(ConfigSource(
            source_type="default",
            priority=0,
            is_active=True
        ))
    
    def _initialize_schemas(self):
        """Initialize configuration schemas."""
        # Application schema
        app_schema = ConfigSchema(
            name="application",
            version="1.0.0",
            environment=self.environment,
            description="Application configuration schema",
            schema={
                "type": "object",
                "properties": {
                    "app.name": {"type": "string", "minLength": 1},
                    "app.version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                    "app.debug": {"type": "boolean"},
                    "app.log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                    "app.host": {"type": "string", "format": "hostname"},
                    "app.port": {"type": "integer", "minimum": 1, "maximum": 65535}
                },
                "required": ["app.name", "app.version", "app.debug", "app.log_level"]
            }
        )
        
        # Database schema
        db_schema = ConfigSchema(
            name="database",
            version="1.0.0",
            environment=self.environment,
            description="Database configuration schema",
            schema={
                "type": "object",
                "properties": {
                    "database.url": {"type": "string", "minLength": 1},
                    "database.pool_size": {"type": "integer", "minimum": 1, "maximum": 100},
                    "database.max_overflow": {"type": "integer", "minimum": 0, "maximum": 100},
                    "database.pool_timeout": {"type": "integer", "minimum": 1, "maximum": 300},
                    "database.pool_recycle": {"type": "integer", "minimum": 300}
                },
                "required": ["database.url"]
            }
        )
        
        # Security schema
        security_schema = ConfigSchema(
            name="security",
            version="1.0.0",
            environment=self.environment,
            description="Security configuration schema",
            schema={
                "type": "object",
                "properties": {
                    "security.secret_key": {"type": "string", "minLength": 16},
                    "security.jwt_algorithm": {"type": "string", "enum": ["HS256", "RS256"]},
                    "security.jwt_expiration": {"type": "integer", "minimum": 60, "maximum": 86400},
                    "security.password_min_length": {"type": "integer", "minimum": 4, "maximum": 32},
                    "security.session_timeout": {"type": "integer", "minimum": 60, "maximum": 86400},
                    "security.rate_limit_requests": {"type": "integer", "minimum": 1, "maximum": 10000},
                    "security.rate_limit_window": {"type": "integer", "minimum": 1, "maximum": 3600}
                },
                "required": ["security.secret_key", "security.jwt_algorithm", "security.jwt_expiration"]
            }
        )
        
        self.config_schemas = {
            "application": app_schema,
            "database": db_schema,
            "security": security_schema
        }
    
    def load_config_from_file(self, file_path: Union[str, Path], config_type: ConfigType = ConfigType.APPLICATION):
        """Load configuration from file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            return False
        
        try:
            with open(file_path, encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Override environment-specific configuration
            if self.environment.value in config_data:
                env_config = config_data[self.environment.value]
                self._merge_config(env_config, f"file:{file_path}")
            
            # Merge base configuration
            base_config = {k: v for k, v in config_data.items() if k not in [env.value for env in Environment]}
            self._merge_config(base_config, f"file:{file_path}")
            
            # Add source
            self.config_sources.append(ConfigSource(
                source_type="file",
                source_path=str(file_path),
                priority=10,
                is_active=True,
                last_updated=datetime.now()
            ))
            
            logger.info(f"Configuration loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            return False
    
    def load_config_from_environment(self, prefix: str = "DAIP_"):
        """Load configuration from environment variables."""
        loaded_count = 0
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace('_', '.')
                
                # Convert string value to appropriate type
                converted_value = self._convert_env_value(value)
                
                self.config_values[config_key] = ConfigValue(
                    key=config_key,
                    value=converted_value,
                    type=type(converted_value).__name__,
                    source="environment",
                    description=f"Environment variable {key}"
                )
                
                loaded_count += 1
        
        if loaded_count > 0:
            self.config_sources.append(ConfigSource(
                source_type="environment",
                priority=20,
                is_active=True,
                last_updated=datetime.now()
            ))
            
            logger.info(f"Loaded {loaded_count} configuration values from environment variables")
        
        return loaded_count > 0
    
    def load_config_from_remote(self, url: str, headers: Optional[dict[str, str]] = None):
        """Load configuration from remote source."""
        import asyncio

        import aiohttp
        
        async def _load_remote():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers or {}) as response:
                        if response.status == 200:
                            config_data = await response.json()
                            self._merge_config(config_data, f"remote:{url}")
                            
                            self.config_sources.append(ConfigSource(
                                source_type="remote",
                                source_path=url,
                                priority=30,
                                is_active=True,
                                last_updated=datetime.now()
                            ))
                            
                            logger.info(f"Configuration loaded from remote source: {url}")
                            return True
                        else:
                            logger.error(f"Failed to load remote configuration: {response.status}")
                            return False
            except Exception as e:
                logger.error(f"Error loading remote configuration: {e}")
                return False
        
        return asyncio.run(_load_remote())
    
    def _merge_config(self, config_data: dict[str, Any], source: str):
        """Merge configuration data with existing configuration."""
        for key, value in config_data.items():
            if isinstance(value, dict):
                # Handle nested configuration
                for sub_key, sub_value in value.items():
                    full_key = f"{key}.{sub_key}"
                    self.config_values[full_key] = ConfigValue(
                        key=full_key,
                        value=sub_value,
                        type=type(sub_value).__name__,
                        source=source,
                        description=f"Merged from {source}"
                    )
            else:
                self.config_values[key] = ConfigValue(
                    key=key,
                    value=value,
                    type=type(value).__name__,
                    source=source,
                    description=f"Merged from {source}"
                )
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable value to appropriate type."""
        # Try boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """Get configuration value."""
        config_value = self.config_values.get(key)
        
        if config_value is None:
            if required:
                raise ValueError(f"Required configuration key '{key}' not found")
            return default
        
        return config_value.value
    
    def get_config_section(self, prefix: str) -> dict[str, Any]:
        """Get configuration section with given prefix."""
        section = {}
        
        for key, config_value in self.config_values.items():
            if key.startswith(prefix + '.'):
                section_key = key[len(prefix + 1):]
                section[section_key] = config_value.value
        
        return section
    
    def set(self, key: str, value: Any, source: str = "runtime"):
        """Set configuration value."""
        self.config_values[key] = ConfigValue(
            key=key,
            value=value,
            type=type(value).__name__,
            source=source,
            last_modified=datetime.now()
        )
        
        # Notify watchers
        self._notify_watchers(key, value)
    
    def validate_config(self, schema_name: str = None) -> dict[str, Any]:
        """Validate configuration against schema."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        schemas_to_validate = [schema_name] if schema_name else list(self.config_schemas.keys())
        
        for schema_name in schemas_to_validate:
            if schema_name not in self.config_schemas:
                validation_results["errors"].append(f"Schema '{schema_name}' not found")
                validation_results["valid"] = False
                continue
            
            schema = self.config_schemas[schema_name]
            config_section = self.get_config_section(schema_name)
            
            try:
                validate(instance=config_section, schema=schema.schema)
                logger.info(f"Configuration validation passed for schema: {schema_name}")
            except ValidationError as e:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Schema '{schema_name}' validation failed: {e.message}")
                logger.error(f"Configuration validation failed for schema '{schema_name}': {e}")
        
        return validation_results
    
    def watch(self, key: str, callback: callable):
        """Watch for configuration changes."""
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
    
    def _notify_watchers(self, key: str, value: Any):
        """Notify watchers of configuration changes."""
        if key in self.watchers:
            for callback in self.watchers[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    logger.error(f"Error in configuration watcher callback: {e}")
    
    def export_config(self, format: str = "yaml", include_sensitive: bool = False) -> str:
        """Export configuration to string."""
        config_data = {}
        
        for key, config_value in self.config_values.items():
            if not config_value.is_sensitive or include_sensitive:
                # Split nested keys
                keys = key.split('.')
                current = config_data
                
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                current[keys[-1]] = config_value.value
        
        if format.lower() == "yaml":
            return yaml.dump(config_data, default_flow_style=False, indent=2)
        else:
            return json.dumps(config_data, indent=2)
    
    def save_config(self, file_path: Union[str, Path], format: str = "yaml"):
        """Save configuration to file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = self.export_config(format, include_sensitive=False)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(config_data)
        
        logger.info(f"Configuration saved to {file_path}")
    
    def get_config_sources(self) -> list[dict[str, Any]]:
        """Get configuration sources information."""
        return [
            {
                "source_type": source.source_type,
                "source_path": source.source_path,
                "priority": source.priority,
                "is_active": source.is_active,
                "last_updated": source.last_updated.isoformat() if source.last_updated else None
            }
            for source in self.config_sources
        ]
    
    def get_config_stats(self) -> dict[str, Any]:
        """Get configuration statistics."""
        total_configs = len(self.config_values)
        source_counts = {}
        type_counts = {}
        
        for config_value in self.config_values.values():
            source_counts[config_value.source] = source_counts.get(config_value.source, 0) + 1
            type_counts[config_value.type] = type_counts.get(config_value.type, 0) + 1
        
        return {
            "total_configurations": total_configs,
            "environment": self.environment.value,
            "sources": source_counts,
            "types": type_counts,
            "active_watchers": len(self.watchers),
            "last_updated": max(cv.last_modified for cv in self.config_values.values()).isoformat()
        }


# DAIP-LIVE Configuration Manager Factory
def create_daip_config_manager(environment: Environment = Environment.DEVELOPMENT) -> ConfigurationManager:
    """Create DAIP-LIVE configuration manager."""
    config_manager = ConfigurationManager(environment)
    
    # Load configuration files
    config_files = [
        "config/config.yaml",
        "config/config.json",
        "config/database.yaml",
        "config/security.yaml",
        "config/services.yaml"
    ]
    
    for config_file in config_files:
        config_manager.load_config_from_file(config_file)
    
    # Load environment variables
    config_manager.load_config_from_environment()
    
    # Validate configuration
    validation_result = config_manager.validate_config()
    if not validation_result["valid"]:
        logger.warning(f"Configuration validation failed: {validation_result['errors']}")
    
    return config_manager


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_config() -> ConfigurationManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        # Get environment from environment variable
        env_name = os.getenv("DAIP_ENV", "development").lower()
        environment = Environment(env_name) if env_name in [e.value for e in Environment] else Environment.DEVELOPMENT
        
        _config_manager = create_daip_config_manager(environment)
    
    return _config_manager


def get_config_value(key: str, default: Any = None, required: bool = False) -> Any:
    """Get configuration value from global manager."""
    return get_config().get(key, default, required)


if __name__ == "__main__":
    # Example usage
    config = get_config()
    
    print("DAIP-LIVE Configuration Manager")
    print("=" * 40)
    print(f"Environment: {config.environment.value}")
    print(f"App Name: {config.get('app.name')}")
    print(f"App Version: {config.get('app.version')}")
    print(f"Debug Mode: {config.get('app.debug')}")
    print(f"Database URL: {config.get('database.url')}")
    print(f"Backend Service: {config.get('services.backend.host')}:{config.get('services.backend.port')}")
    
    # Get configuration section
    services_config = config.get_config_section('services')
    print(f"\nServices Configuration: {services_config}")
    
    # Get configuration statistics
    stats = config.get_config_stats()
    print(f"\nConfiguration Statistics: {stats}")
    
    # Export configuration
    print("\nConfiguration Export (YAML):")
    print(config.export_config('yaml'))