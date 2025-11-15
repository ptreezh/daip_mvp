"""Model manager for handling local model detection and switching."""

import subprocess
import json
from typing import Dict, List, Optional, Tuple
from daip_live.core.exceptions import ModelError


class ModelManager:
    """Manages local model detection and switching functionality."""
    
    def __init__(self):
        self._cached_models: Optional[List[Dict]] = None
        self._current_model: Optional[str] = None
    
    def get_available_models(self, force_refresh: bool = False) -> List[Dict]:
        """Get list of available local non-embedding models."""
        if self._cached_models and not force_refresh:
            return self._cached_models
        
        models = []
        
        # Get Ollama models
        ollama_models = self._get_ollama_models()
        models.extend(ollama_models)
        
        # Cache the results
        self._cached_models = models
        return models
    
    def _get_ollama_models(self) -> List[Dict]:
        """Get models from Ollama local installation."""
        models = []
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse Ollama output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header line
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 2:
                            model_name = parts[0]
                            # Filter out embedding models
                            if not self._is_embedding_model(model_name):
                                models.append({
                                    "name": model_name,
                                    "provider": "ollama",
                                    "size": parts[1] if len(parts) > 1 else "unknown",
                                    "modified": parts[2] if len(parts) > 2 else "unknown"
                                })
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Ollama not installed or not running
            pass
        
        return models
    
    def _is_embedding_model(self, model_name: str) -> bool:
        """Check if a model is an embedding model."""
        embedding_keywords = ["embed", "embedding", "bge", "e5", "text-embedding", "minilm", "all-minilm"]
        model_lower = model_name.lower()
        return any(keyword in model_lower for keyword in embedding_keywords)
    
    def switch_model(self, model_name: str, provider: str = "ollama") -> bool:
        """Switch to a different model and update configuration."""
        # Verify the model exists
        available_models = self.get_available_models()
        model_found = any(
            model["name"] == model_name and model["provider"] == provider 
            for model in available_models
        )
        
        if not model_found:
            raise ModelError(f"Model {model_name} not found in available models")
        
        # Update current model
        self._current_model = f"{provider}/{model_name}"
        
        # Update configuration file
        return self._update_config_file(model_name, provider)
    
    def _update_config_file(self, model_name: str, provider: str) -> bool:
        """Update the configuration file with the new model."""
        try:
            import yaml
            config_path = "config.yaml"
            
            # Read current config
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Update the model
            config["llm_provider"]["default_model"] = f"{provider}/{model_name}"
            
            # Write back to file
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            raise ModelError(f"Failed to update configuration: {e}")
    
    def get_current_model(self) -> Optional[Dict]:
        """Get the current model information."""
        if self._current_model and isinstance(self._current_model, dict):
            return self._current_model

        # Try to read from config
        try:
            import yaml
            with open("config.yaml", 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                model = config.get("llm_provider", {}).get("default_model")
                if model:
                    # Parse model name from provider/model format
                    if "/" in model:
                        provider, name = model.split("/", 1)
                        model_info = {
                            'name': name,
                            'provider': provider,
                            'status': 'ready',
                            'uptime': 'Unknown'
                        }
                    else:
                        model_info = {
                            'name': model,
                            'provider': 'unknown',
                            'status': 'ready',
                            'uptime': 'Unknown'
                        }
                    self._current_model = model_info
                    return model_info
        except Exception:
            pass

        return None

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a specific model."""
        available_models = self.get_available_models()

        for model in available_models:
            if model.get('name') == model_name:
                return model

        return None
    
    def format_model_list(self) -> str:
        """Format the model list for display."""
        models = self.get_available_models()
        if not models:
            return "No local models found. Make sure Ollama is installed and running."
        
        current_model = self.get_current_model()
        result = []
        
        for model in models:
            indicator = "👉 " if f"{model['provider']}/{model['name']}" == current_model else "   "
            result.append(f"{indicator}{model['name']} ({model['provider']}) - {model['size']}")
        
        return "\n".join(result)