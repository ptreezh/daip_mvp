import os
from pathlib import Path

import typer
import yaml
from rich import print
from rich.panel import Panel
from rich.syntax import Syntax

from daip_live.core.interfaces import IModelProvider

SCAFFOLD_META_PROMPT = """
You are an expert system architect. Based on the user's project description, generate a complete set of YAML configuration files for all necessary roles and workflows. The output should be a single, valid YAML document containing a list of files.

Example Output:
---
files:
  - path: roles/backend_developer.yaml
    content: |
      persona: A senior backend developer specializing in Python and FastAPI.
      tools: [bash, python_repl]
  - path: workflows/development.yaml
    content: |
      name: Standard Development Workflow
      steps: [...] 
---

User Project Description:
"""

CORRECTION_PROMPT_TEMPLATE = """
Your previous YAML output was invalid and could not be parsed. 
Error: {error}
Please correct the YAML syntax and provide the full, valid YAML document again.
Original Description: {description}
Previous Invalid Output:
---
{invalid_yaml}
---
"""

class Scaffolder:
    """Generates project structure from a natural language description."""

    def __init__(self, model_provider: IModelProvider, max_retries: int = 2):
        self.model_provider = model_provider
        self.max_retries = max_retries

    async def execute(self, description: str):
        """The main orchestration method for the scaffolding process."""
        print("[yellow]Generating project configuration from description...[/yellow]")
        generated_plan = await self.generate_from_description(description)

        print("[bold green]AI has generated the following plan:[/bold green]")
        preview = ""
        for file_info in generated_plan.get("files", []):
            path = file_info.get("path", "_No path specified_")
            content = file_info.get("content", "_No content specified_")
            preview += f"- [cyan]{path}[/cyan]\n"
            panel_content = Syntax(content, "yaml", theme="monokai", line_numbers=True)
            print(Panel(panel_content, title=f"Preview of {path}", border_style="blue"))

        prompt_text = f"\n[bold]Ready to create the following files?[/bold]\n{preview}"
        confirmed = typer.confirm(prompt_text, abort=True)

        if confirmed:
            print("\n[bold green]Confirmed! Writing files...[/bold green]")
            for file_info in generated_plan.get("files", []):
                file_path = Path(file_info.get("path"))
                content = file_info.get("content", "")

                # Ensure parent directory exists
                if file_path.parent:
                    os.makedirs(file_path.parent, exist_ok=True)

                # Write the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"- [green]Created {file_path}[/green]")
            print("[bold blue]Scaffolding complete![/bold blue]")

    async def generate_from_description(self, description: str) -> dict:
        """Generates file configurations by calling the LLM, with a self-correction loop."""
        prompt = SCAFFOLD_META_PROMPT + "\n" + description
        last_error = None

        for attempt in range(self.max_retries + 1):
            generated_yaml_str = await self.model_provider.generate(prompt)

            try:
                parsed_output = yaml.safe_load(generated_yaml_str)
                if not isinstance(parsed_output, dict) or "files" not in parsed_output:
                    raise ValueError("Root object must be a dictionary with a 'files' key.")
                return parsed_output
            except (yaml.YAMLError, ValueError) as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed: Invalid YAML from LLM. Retrying...")
                prompt = CORRECTION_PROMPT_TEMPLATE.format(
                    error=str(e),
                    description=description,
                    invalid_yaml=generated_yaml_str
                )

        raise ValueError(f"Failed to generate valid YAML after {self.max_retries} retries.") from last_error
