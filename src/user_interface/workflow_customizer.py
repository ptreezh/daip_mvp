"""@Time    : 2025-07-24 19:00:00
@Author  : DAIP-LIVE Team
@File    : workflow_customizer.py
@Description:
    Workflow customization and configuration management.
"""
import json
import logging
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

logger = logging.getLogger(__name__)


class WorkflowCustomizer:
    """Manages workflow customization and configuration."""
    
    def __init__(self, console: Console = None):
        """Initialize the workflow customizer."""
        self.console = console or Console()
        self.config_templates = self._load_config_templates()
        self.custom_configs: dict[str, dict[str, Any]] = {}
    
    def _load_config_templates(self) -> dict[str, dict[str, Any]]:
        """Load configuration templates for different workflows."""
        return {
            "critical_review": {
                "generation": {
                    "role_name": {"type": "string", "default": "创作者", "description": "Role name for content generation"},
                    "capture_metadata": {"type": "boolean", "default": True, "description": "Capture generation metadata"}
                },
                "fact_extraction": {
                    "min_confidence": {"type": "float", "default": 0.6, "description": "Minimum confidence for fact extraction"},
                    "max_facts": {"type": "integer", "default": 20, "description": "Maximum number of facts to extract"}
                },
                "parallel_review": {
                    "reviewer_roles": {"type": "list", "default": ["批判者", "验证者"], "description": "List of reviewer roles"},
                    "max_parallel_reviews": {"type": "integer", "default": 5, "description": "Maximum parallel reviews"}
                },
                "consensus": {
                    "consensus_method": {"type": "string", "default": "weighted_average", "choices": ["weighted_average", "majority_vote", "synthesis"], "description": "Consensus calculation method"},
                    "credibility_threshold": {"type": "float", "default": 0.7, "description": "Credibility threshold for revision"}
                },
                "revision": {
                    "revision_role": {"type": "string", "default": "创作者", "description": "Role for content revision"},
                    "max_revision_attempts": {"type": "integer", "default": 3, "description": "Maximum revision attempts"}
                }
            },
            "multi_perspective": {
                "task_decomposition": {
                    "planner_role": {"type": "string", "default": "规划者", "description": "Role for task decomposition"},
                    "default_perspectives": {"type": "list", "default": ["经济", "社会", "技术", "伦理"], "description": "Default perspectives to consider"},
                    "max_sub_problems": {"type": "integer", "default": 5, "description": "Maximum sub-problems to create"}
                },
                "parallel_exploration": {
                    "max_parallel_experts": {"type": "integer", "default": 5, "description": "Maximum parallel expert analyses"},
                    "use_tools": {"type": "boolean", "default": True, "description": "Enable tool usage during exploration"}
                },
                "viewpoint_collection": {
                    "min_viewpoints": {"type": "integer", "default": 2, "description": "Minimum viewpoints required"},
                    "conflict_threshold": {"type": "float", "default": 0.3, "description": "Threshold for conflict detection"},
                    "consensus_threshold": {"type": "float", "default": 0.7, "description": "Threshold for consensus identification"}
                },
                "enhanced_synthesis": {
                    "synthesis_method": {"type": "string", "default": "dialectical", "choices": ["dialectical", "weighted", "hierarchical"], "description": "Synthesis method"},
                    "quality_threshold": {"type": "float", "default": 0.7, "description": "Quality threshold for synthesis"},
                    "include_expert_attribution": {"type": "boolean", "default": True, "description": "Include expert attribution in results"}
                },
                "iterative_refinement": {
                    "max_iterations": {"type": "integer", "default": 3, "description": "Maximum refinement iterations"},
                    "improvement_threshold": {"type": "float", "default": 0.1, "description": "Minimum improvement threshold"}
                }
            }
        }
    
    def create_custom_config(
        self,
        workflow_name: str,
        config_name: str = "custom",
        base_config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Create a custom configuration interactively."""
        self.console.print(f"\n[blue]🎨 Creating Custom Configuration for {workflow_name}[/blue]")
        
        if workflow_name not in self.config_templates:
            self.console.print(f"[red]Unknown workflow: {workflow_name}[/red]")
            return {}
        
        template = self.config_templates[workflow_name]
        config = base_config.copy() if base_config else {}
        
        # Initialize with defaults if not provided
        for section_name, section_template in template.items():
            if section_name not in config:
                config[section_name] = {}
            
            for param_name, param_def in section_template.items():
                if param_name not in config[section_name]:
                    config[section_name][param_name] = param_def["default"]
        
        # Interactive customization
        self.console.print("\n[cyan]Current configuration sections:[/cyan]")
        sections = list(template.keys())
        
        for i, section in enumerate(sections, 1):
            self.console.print(f"  {i}. {section}")
        
        while True:
            self.console.print(f"\n  {len(sections) + 1}. Review and save")
            self.console.print(f"  {len(sections) + 2}. Cancel")
            
            choice = Prompt.ask(
                "Select a section to customize",
                choices=[str(i) for i in range(1, len(sections) + 3)],
                default=str(len(sections) + 1)
            )
            
            choice_num = int(choice)
            
            if choice_num == len(sections) + 1:
                # Review and save
                self._display_config_summary(config)
                if Confirm.ask("Save this configuration?"):
                    self.custom_configs[f"{workflow_name}_{config_name}"] = config
                    return config
                else:
                    continue
            elif choice_num == len(sections) + 2:
                # Cancel
                return {}
            else:
                # Customize section
                section_name = sections[choice_num - 1]
                config[section_name] = self._customize_section(
                    section_name,
                    template[section_name],
                    config[section_name]
                )
        
        return config
    
    def load_config_from_file(self, file_path: str) -> dict[str, Any]:
        """Load configuration from a JSON file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                config = json.load(f)
            
            self.console.print(f"[green]✅ Configuration loaded from {file_path}[/green]")
            return config
        
        except FileNotFoundError:
            self.console.print(f"[red]❌ Configuration file not found: {file_path}[/red]")
            return {}
        except json.JSONDecodeError as e:
            self.console.print(f"[red]❌ Invalid JSON in configuration file: {e}[/red]")
            return {}
    
    def save_config_to_file(
        self,
        config: dict[str, Any],
        file_path: str,
        overwrite: bool = False
    ) -> bool:
        """Save configuration to a JSON file."""
        path = Path(file_path)
        
        if path.exists() and not overwrite:
            if not Confirm.ask(f"File {file_path} exists. Overwrite?"):
                return False
        
        try:
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ Configuration saved to {file_path}[/green]")
            return True
        
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save configuration: {e}[/red]")
            return False
    
    def list_available_configs(self, workflow_name: str = None) -> list[str]:
        """List available configurations."""
        if workflow_name:
            configs = [name for name in self.custom_configs.keys() if name.startswith(workflow_name)]
        else:
            configs = list(self.custom_configs.keys())
        
        return configs
    
    def get_config_recommendations(
        self,
        workflow_name: str,
        use_case: str = "general"
    ) -> dict[str, Any]:
        """Get recommended configuration based on use case."""
        if workflow_name not in self.config_templates:
            return {}
        
        base_config = {}
        template = self.config_templates[workflow_name]
        
        # Initialize with defaults
        for section_name, section_template in template.items():
            base_config[section_name] = {}
            for param_name, param_def in section_template.items():
                base_config[section_name][param_name] = param_def["default"]
        
        # Apply use case specific recommendations
        if workflow_name == "critical_review":
            if use_case == "academic":
                base_config["consensus"]["credibility_threshold"] = 0.8
                base_config["parallel_review"]["reviewer_roles"] = ["学术批判者", "同行评议者", "方法论专家"]
            elif use_case == "journalism":
                base_config["consensus"]["credibility_threshold"] = 0.9
                base_config["parallel_review"]["reviewer_roles"] = ["事实核查员", "来源验证者", "编辑审查员"]
            elif use_case == "casual":
                base_config["consensus"]["credibility_threshold"] = 0.6
                base_config["fact_extraction"]["max_facts"] = 10
        
        elif workflow_name == "multi_perspective":
            if use_case == "policy_analysis":
                base_config["task_decomposition"]["default_perspectives"] = ["政策", "经济", "社会", "法律", "实施"]
                base_config["enhanced_synthesis"]["quality_threshold"] = 0.8
            elif use_case == "technology_assessment":
                base_config["task_decomposition"]["default_perspectives"] = ["技术", "经济", "社会", "伦理", "安全"]
                base_config["iterative_refinement"]["max_iterations"] = 2
            elif use_case == "business_strategy":
                base_config["task_decomposition"]["default_perspectives"] = ["市场", "财务", "运营", "风险", "创新"]
                base_config["enhanced_synthesis"]["quality_threshold"] = 0.75
        
        return base_config
    
    def validate_config(
        self,
        config: dict[str, Any],
        workflow_name: str
    ) -> dict[str, list[str]]:
        """Validate configuration against template."""
        if workflow_name not in self.config_templates:
            return {"errors": [f"Unknown workflow: {workflow_name}"]}
        
        template = self.config_templates[workflow_name]
        errors = []
        warnings = []
        
        # Check for missing sections
        for section_name in template.keys():
            if section_name not in config:
                errors.append(f"Missing section: {section_name}")
                continue
            
            # Check parameters in each section
            section_template = template[section_name]
            section_config = config[section_name]
            
            for param_name, param_def in section_template.items():
                if param_name not in section_config:
                    warnings.append(f"Missing parameter: {section_name}.{param_name}")
                    continue
                
                # Validate parameter type and value
                param_value = section_config[param_name]
                param_type = param_def["type"]
                
                if param_type == "float" and not isinstance(param_value, (int, float)):
                    errors.append(f"Invalid type for {section_name}.{param_name}: expected float")
                elif param_type == "integer" and not isinstance(param_value, int):
                    errors.append(f"Invalid type for {section_name}.{param_name}: expected integer")
                elif param_type == "boolean" and not isinstance(param_value, bool):
                    errors.append(f"Invalid type for {section_name}.{param_name}: expected boolean")
                elif param_type == "list" and not isinstance(param_value, list):
                    errors.append(f"Invalid type for {section_name}.{param_name}: expected list")
                elif param_type == "string" and not isinstance(param_value, str):
                    errors.append(f"Invalid type for {section_name}.{param_name}: expected string")
                
                # Check choices if defined
                if "choices" in param_def and param_value not in param_def["choices"]:
                    errors.append(f"Invalid choice for {section_name}.{param_name}: {param_value}")
        
        return {"errors": errors, "warnings": warnings}
    
    def _customize_section(
        self,
        section_name: str,
        section_template: dict[str, dict[str, Any]],
        current_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Customize a specific configuration section."""
        self.console.print(f"\n[cyan]🔧 Customizing {section_name}[/cyan]")
        
        new_config = current_config.copy()
        
        while True:
            # Display current configuration
            table = Table(title=f"{section_name} Configuration")
            table.add_column("Parameter", style="cyan")
            table.add_column("Current Value", style="magenta")
            table.add_column("Description", style="dim")
            
            for param_name, param_def in section_template.items():
                current_value = new_config.get(param_name, param_def["default"])
                description = param_def.get("description", "")
                table.add_row(param_name, str(current_value), description)
            
            self.console.print(table)
            
            # Show options
            params = list(section_template.keys())
            params.append("Done")
            
            self.console.print("\nSelect parameter to modify:")
            for i, param in enumerate(params, 1):
                self.console.print(f"  {i}. {param}")
            
            choice = Prompt.ask(
                "Select parameter",
                choices=[str(i) for i in range(1, len(params) + 1)],
                default=str(len(params))
            )
            
            if int(choice) == len(params):
                break
            
            param_name = params[int(choice) - 1]
            param_def = section_template[param_name]
            current_value = new_config.get(param_name, param_def["default"])
            
            # Get new value based on parameter definition
            new_value = self._get_parameter_value(param_name, param_def, current_value)
            new_config[param_name] = new_value
        
        return new_config
    
    def _get_parameter_value(
        self,
        param_name: str,
        param_def: dict[str, Any],
        current_value: Any
    ) -> Any:
        """Get a parameter value from user input."""
        param_type = param_def["type"]
        description = param_def.get("description", "")
        choices = param_def.get("choices")
        
        self.console.print(f"\n[yellow]Setting {param_name}[/yellow]")
        self.console.print(f"Description: {description}")
        self.console.print(f"Current value: {current_value}")
        
        if param_type == "string":
            if choices:
                return Prompt.ask(
                    f"Select value for {param_name}",
                    choices=choices,
                    default=str(current_value)
                )
            else:
                return Prompt.ask(
                    f"Enter value for {param_name}",
                    default=str(current_value)
                )
        
        elif param_type == "integer":
            from rich.prompt import IntPrompt
            return IntPrompt.ask(
                f"Enter integer value for {param_name}",
                default=current_value
            )
        
        elif param_type == "float":
            from rich.prompt import FloatPrompt
            return FloatPrompt.ask(
                f"Enter float value for {param_name}",
                default=current_value
            )
        
        elif param_type == "boolean":
            return Confirm.ask(
                f"Enable {param_name}?",
                default=current_value
            )
        
        elif param_type == "list":
            current_str = ",".join(str(v) for v in current_value) if isinstance(current_value, list) else str(current_value)
            value_str = Prompt.ask(
                f"Enter comma-separated values for {param_name}",
                default=current_str
            )
            return [item.strip() for item in value_str.split(",") if item.strip()]
        
        else:
            return Prompt.ask(
                f"Enter value for {param_name}",
                default=str(current_value)
            )
    
    def _display_config_summary(self, config: dict[str, Any]) -> None:
        """Display a summary of the configuration."""
        self.console.print("\n[blue]📋 Configuration Summary[/blue]")
        
        for section_name, section_config in config.items():
            self.console.print(f"\n[cyan]{section_name}:[/cyan]")
            
            if isinstance(section_config, dict):
                for param_name, param_value in section_config.items():
                    self.console.print(f"  • {param_name}: {param_value}")
            else:
                self.console.print(f"  • {section_config}")
    
    def create_config_preset(
        self,
        workflow_name: str,
        preset_name: str,
        description: str,
        config: dict[str, Any]
    ) -> bool:
        """Create a configuration preset."""
        preset_key = f"{workflow_name}_{preset_name}"
        
        preset_data = {
            "name": preset_name,
            "description": description,
            "workflow": workflow_name,
            "config": config,
            "created_at": str(datetime.now())
        }
        
        self.custom_configs[preset_key] = preset_data
        
        self.console.print(f"[green]✅ Created preset '{preset_name}' for {workflow_name}[/green]")
        return True
    
    def list_config_presets(self, workflow_name: str = None) -> list[dict[str, Any]]:
        """List available configuration presets."""
        presets = []
        
        for key, preset_data in self.custom_configs.items():
            if isinstance(preset_data, dict) and "workflow" in preset_data:
                if workflow_name is None or preset_data["workflow"] == workflow_name:
                    presets.append(preset_data)
        
        return presets