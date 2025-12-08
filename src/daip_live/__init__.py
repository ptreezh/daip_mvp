"""DAIP-LIVE main package initialization."""

# Initialize the configuration bridge when the package is imported
from .config import ConfigManager
from .config_bridge import config_bridge

# Initialize the global config manager as early as possible
try:
    # Create and register the config manager with the bridge
    _global_config_manager = ConfigManager()
    config_bridge.set_config_manager(_global_config_manager)
except Exception as e:
    # If config initialization fails, the bridge will use default values
    print(f"Warning: Could not initialize config manager during package loading: {e}")

__all__ = ['config_bridge']