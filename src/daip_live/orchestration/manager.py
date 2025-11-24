"""
Subagent management system for the hierarchical architecture.
"""
import os
import importlib.util
import requests
import tempfile
import zipfile
import hashlib
import logging
from typing import Dict, List, Optional, Type
from ..subagents.base import TheorySubagent, SubagentCapabilities


class SubagentManager:
    """Manages registration, discovery, and allocation of Subagents."""
    
    def __init__(self):
        self._subagents: Dict[str, TheorySubagent] = {}
        self._capabilities: Dict[str, SubagentCapabilities] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_subagent(self, subagent: TheorySubagent) -> None:
        """
        Register a Subagent with the manager.
        
        Args:
            subagent: The Subagent to register
        """
        name = subagent.name
        if name in self._subagents:
            raise ValueError(f"Subagent with name '{name}' already registered")
        
        self._subagents[name] = subagent
        self._capabilities[name] = subagent.get_capabilities()
        
        # Initialize the Subagent
        subagent.initialize()
    
    def unregister_subagent(self, name: str) -> None:
        """
        Unregister a Subagent from the manager.
        
        Args:
            name: The name of the Subagent to unregister
        """
        if name in self._subagents:
            # Cleanup the Subagent
            self._subagents[name].cleanup()
            del self._subagents[name]
            del self._capabilities[name]
    
    def get_subagent(self, name: str) -> Optional[TheorySubagent]:
        """
        Get a registered Subagent by name.
        
        Args:
            name: The name of the Subagent to retrieve
            
        Returns:
            The Subagent if found, None otherwise
        """
        return self._subagents.get(name)
    
    def list_subagents(self) -> List[str]:
        """
        List all registered Subagent names.
        
        Returns:
            List of Subagent names
        """
        return list(self._subagents.keys())
    
    def get_capabilities(self, name: str) -> Optional[SubagentCapabilities]:
        """
        Get capabilities for a specific Subagent.
        
        Args:
            name: The name of the Subagent
            
        Returns:
            SubagentCapabilities if Subagent exists, None otherwise
        """
        return self._capabilities.get(name)
    
    def find_subagents_by_capability(self, capability: str) -> List[str]:
        """
        Find Subagents that support a specific capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            List of Subagent names that support the capability
        """
        matching_subagents = []
        for name, capabilities in self._capabilities.items():
            if capability in capabilities.supported_domains:
                matching_subagents.append(name)
        return matching_subagents
    
    def match_subagent_to_task(self, task_domain: str, required_skills: List[str] = None) -> Optional[str]:
        """
        Match the most appropriate Subagent to a task based on domain and skills.
        
        Args:
            task_domain: The domain of the task
            required_skills: List of required skills for the task
            
        Returns:
            Name of the best matching Subagent, or None if no match found
        """
        required_skills = required_skills or []
        
        # Find all Subagents that support the task domain
        candidates = self.find_subagents_by_capability(task_domain)
        if not candidates:
            return None
        
        # If no specific skills required, return the first candidate
        if not required_skills:
            return candidates[0]
        
        # Score candidates based on skill matching
        best_match = None
        best_score = -1
        
        for candidate_name in candidates:
            capabilities = self._capabilities[candidate_name]
            score = 0
            
            # Score based on skill matching
            for skill in required_skills:
                if skill in capabilities.required_skills:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = candidate_name
        
        return best_match
    
    def load_subagents_from_directory(self, directory: str) -> int:
        """
        Dynamically load Subagents from a directory.
        
        Args:
            directory: The directory to load Subagents from
            
        Returns:
            Number of Subagents loaded
        """
        subagents_loaded = 0
        
        if not os.path.exists(directory):
            self._logger.warning(f"Subagents directory not found: {directory}")
            return subagents_loaded
        
        # Look for Python files in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    # Import the module
                    module_name = filename[:-3]  # Remove .py extension
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(directory, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for Subagent classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, TheorySubagent) and 
                            attr != TheorySubagent):
                            # Try to instantiate the Subagent
                            try:
                                subagent_instance = attr()
                                self.register_subagent(subagent_instance)
                                subagents_loaded += 1
                                self._logger.info(f"Loaded Subagent: {subagent_instance.name}")
                            except Exception as e:
                                self._logger.warning(f"Failed to instantiate Subagent from {filename}: {e}")
                                pass
                except Exception as e:
                    self._logger.warning(f"Failed to import Subagent module {filename}: {e}")
                    pass
        
        return subagents_loaded
    
    def download_and_install_subagent(self, url: str, target_directory: str = None) -> bool:
        """
        Download and install a Subagent from a URL.
        
        Args:
            url: The URL to download the Subagent from
            target_directory: The directory to install the Subagent to
            
        Returns:
            True if successful, False otherwise
        """
        if target_directory is None:
            target_directory = os.path.join("data", "subagents")
        
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_directory, exist_ok=True)
            
            # Download the file
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_filename = tmp_file.name
            
            # If it's a zip file, extract it
            if url.endswith('.zip'):
                with zipfile.ZipFile(tmp_filename, 'r') as zip_ref:
                    zip_ref.extractall(target_directory)
            else:
                # Save as a Python file
                filename = os.path.basename(url)
                target_path = os.path.join(target_directory, filename)
                os.rename(tmp_filename, target_path)
            
            # Load the Subagents from the directory
            loaded_count = self.load_subagents_from_directory(target_directory)
            
            self._logger.info(f"Successfully downloaded and installed {loaded_count} Subagents from {url}")
            return loaded_count > 0
            
        except Exception as e:
            self._logger.error(f"Failed to download and install Subagent from {url}: {e}")
            return False