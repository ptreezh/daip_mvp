"""
Plugin management system for DAIP-LIVE hierarchical architecture.
"""
import os
import json
import requests
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class PluginInfo:
    """Information about a plugin."""
    name: str
    version: str
    description: str
    type: str  # "subagent" or "skill"
    url: str
    checksum: str = ""
    dependencies: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


class PluginManager:
    """Manages plugins (Subagents and Skills) for the hierarchical architecture."""
    
    def __init__(self, subagent_manager, skill_manager):
        self.subagent_manager = subagent_manager
        self.skill_manager = skill_manager
        self._logger = logging.getLogger(__name__)
        self._plugins: Dict[str, PluginInfo] = {}
        self._installed_plugins: Dict[str, PluginInfo] = {}
        
        # Create plugins directory
        self.plugins_dir = os.path.join("data", "plugins")
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # Load installed plugins registry
        self._load_installed_plugins_registry()
    
    def register_plugin_source(self, source_url: str) -> bool:
        """
        Register a plugin source (marketplace/repository).
        
        Args:
            source_url: URL to the plugin source (should return JSON with plugin list)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(source_url, timeout=10)
            response.raise_for_status()
            
            plugins_data = response.json()
            
            # Parse plugin information
            for plugin_data in plugins_data.get("plugins", []):
                plugin_info = PluginInfo(
                    name=plugin_data["name"],
                    version=plugin_data["version"],
                    description=plugin_data["description"],
                    type=plugin_data["type"],
                    url=plugin_data["url"],
                    checksum=plugin_data.get("checksum", ""),
                    dependencies=plugin_data.get("dependencies", []),
                    tags=plugin_data.get("tags", [])
                )
                
                self._plugins[plugin_info.name] = plugin_info
            
            self._logger.info(f"Registered plugin source with {len(self._plugins)} plugins")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to register plugin source {source_url}: {e}")
            return False
    
    def list_available_plugins(self) -> List[PluginInfo]:
        """
        List all available plugins from registered sources.
        
        Returns:
            List of available plugins
        """
        return list(self._plugins.values())
    
    def search_plugins(self, query: str, plugin_type: str = None) -> List[PluginInfo]:
        """
        Search for plugins by name, description, or tags.
        
        Args:
            query: Search query
            plugin_type: Filter by type ("subagent" or "skill")
            
        Returns:
            List of matching plugins
        """
        results = []
        query_lower = query.lower()
        
        for plugin in self._plugins.values():
            # Filter by type if specified
            if plugin_type and plugin.type != plugin_type:
                continue
            
            # Match by name, description, or tags
            if (query_lower in plugin.name.lower() or 
                query_lower in plugin.description.lower() or
                any(query_lower in tag.lower() for tag in plugin.tags)):
                results.append(plugin)
        
        return results
    
    def install_plugin(self, plugin_name: str) -> bool:
        """
        Install a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to install
            
        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self._plugins:
            self._logger.error(f"Plugin {plugin_name} not found in available plugins")
            return False
        
        plugin_info = self._plugins[plugin_name]
        
        # Install dependencies first
        for dependency in plugin_info.dependencies:
            if not self.is_plugin_installed(dependency):
                if not self.install_plugin(dependency):
                    self._logger.error(f"Failed to install dependency {dependency} for {plugin_name}")
                    return False
        
        # Download and install the plugin
        success = False
        if plugin_info.type == "subagent":
            success = self.subagent_manager.download_and_install_subagent(
                plugin_info.url, 
                os.path.join(self.plugins_dir, "subagents")
            )
        elif plugin_info.type == "skill":
            success = self.skill_manager.download_and_install_skill(
                plugin_info.url,
                os.path.join(self.plugins_dir, "skills")
            )
        
        if success:
            # Register as installed
            self._installed_plugins[plugin_name] = plugin_info
            self._save_installed_plugins_registry()
            self._logger.info(f"Successfully installed plugin {plugin_name}")
        
        return success
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """
        Uninstall a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to uninstall
            
        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self._installed_plugins:
            self._logger.warning(f"Plugin {plugin_name} is not installed")
            return False
        
        # TODO: Implement actual uninstallation logic
        # This would involve removing files and unregistering from managers
        
        # Remove from installed registry
        del self._installed_plugins[plugin_name]
        self._save_installed_plugins_registry()
        
        self._logger.info(f"Uninstalled plugin {plugin_name}")
        return True
    
    def is_plugin_installed(self, plugin_name: str) -> bool:
        """
        Check if a plugin is installed.
        
        Args:
            plugin_name: Name of the plugin to check
            
        Returns:
            True if installed, False otherwise
        """
        return plugin_name in self._installed_plugins
    
    def list_installed_plugins(self) -> List[PluginInfo]:
        """
        List all installed plugins.
        
        Returns:
            List of installed plugins
        """
        return list(self._installed_plugins.values())
    
    def update_plugin(self, plugin_name: str) -> bool:
        """
        Update a plugin to the latest version.
        
        Args:
            plugin_name: Name of the plugin to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_plugin_installed(plugin_name):
            self._logger.error(f"Plugin {plugin_name} is not installed")
            return False
        
        # TODO: Implement update logic
        # This would involve checking for newer versions and reinstalling
        
        self._logger.info(f"Updated plugin {plugin_name}")
        return True
    
    def _load_installed_plugins_registry(self):
        """Load the registry of installed plugins."""
        registry_file = os.path.join(self.plugins_dir, "installed_plugins.json")
        
        if os.path.exists(registry_file):
            try:
                with open(registry_file, "r") as f:
                    data = json.load(f)
                    for name, plugin_data in data.items():
                        self._installed_plugins[name] = PluginInfo(**plugin_data)
            except Exception as e:
                self._logger.warning(f"Failed to load installed plugins registry: {e}")
    
    def _save_installed_plugins_registry(self):
        """Save the registry of installed plugins."""
        registry_file = os.path.join(self.plugins_dir, "installed_plugins.json")
        
        try:
            # Convert PluginInfo objects to dictionaries
            data = {}
            for name, plugin_info in self._installed_plugins.items():
                data[name] = asdict(plugin_info)
            
            with open(registry_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self._logger.error(f"Failed to save installed plugins registry: {e}")