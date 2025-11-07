
import asyncio
import re
from typing import Any, Dict, List

import yaml

from daip_live.core.models import ProviderConfig
from daip_live.model_provider.provider import LiteLLMProvider


class ScaffoldingManager:
    def __init__(self, model_provider: LiteLLMProvider, max_retries: int = 2):
        self.model_provider = model_provider
        self.max_retries = max_retries

    def _extract_yaml_from_response(self, response: str) -> str:
        """Extracts the YAML content from a markdown code block if present."""
        match = re.search(r"```(?:yaml)?\n(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return response.strip()

    async def generate_structure(self, description: str) -> List[Dict[str, Any]]:
        """
        Generates a project structure in YAML format from a description,
        with validation and self-correction.
        """
        base_prompt = f"""
        Based on the following project description, generate a file structure in YAML format.
        The YAML must be a list of dictionaries, where each dictionary has 'filename' and 'content' keys.
        Ensure the YAML is valid.

        Description: {description}

        Example YAML format:
        ```yaml
        - filename: roles/project_manager.yaml
          content: |
            name: Project Manager
            persona: Manages the project.
        - filename: workflows/main_workflow.yaml
          content: |
            name: Main Workflow
            steps: []
        ```

        YAML:
        """

        prompt = base_prompt
        last_error = ""

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                print(f"YAML validation failed. Retrying... (Attempt {attempt}/{self.max_retries})")
                prompt = f"{base_prompt}\n\nThe previous attempt failed with the following YAML error:\n{last_error}\n\nPlease correct the YAML and provide the full, valid structure again.\nYAML:\n"

            response_text = await self.model_provider.generate(prompt=prompt)
            yaml_text = self._extract_yaml_from_response(response_text)

            try:
                parsed_yaml = yaml.safe_load(yaml_text)
                if isinstance(parsed_yaml, list):
                    # Basic validation for expected structure
                    if all('filename' in item and 'content' in item for item in parsed_yaml):
                        return parsed_yaml
                    else:
                        last_error = "Invalid structure: Each item in the list must have 'filename' and 'content' keys."
                else:
                    last_error = "Invalid format: The root of the YAML must be a list."

            except yaml.YAMLError as e:
                last_error = str(e)

        raise ValueError(f"Failed to generate valid YAML after {self.max_retries} retries. Last error: {last_error}")


# Example usage (for testing)
async def main():
    provider_config = ProviderConfig(model="gpt-3.5-turbo") # Or any other configured model
    model_provider = LiteLLMProvider(provider_config)
    scaffolder = ScaffoldingManager(model_provider)

    description = "A simple project with a project manager role and a main workflow."
    try:
        parsed_structure = await scaffolder.generate_structure(description)
        print("--- Generated and Validated Structure ---")
        print(yaml.dump(parsed_structure, indent=2))
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
