"""Manages the state and data of debates."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Define the base directory for debates
DEBATES_DIR = Path("data/debates")

class DebateManager:
    """Handles loading, modifying, and saving debate data from JSON files."""

    def __init__(self, debates_directory: Path = DEBATES_DIR) -> None:
        """Initializes the DebateManager."""
        self.debates_directory = debates_directory
        self.debates_directory.mkdir(parents=True, exist_ok=True)
        logging.info(f"DebateManager initialized. Debates directory: {self.debates_directory}")

    def _get_debate_path(self, debate_id: str) -> Path:
        """Constructs the file path for a given debate ID."""
        return self.debates_directory / f"{debate_id}.json"

    def debate_exists(self, debate_id: str) -> bool:
        """Checks if a debate with the given ID exists."""
        return self._get_debate_path(debate_id).exists()

    def get_debate(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the data for a specific debate."""
        if not self.debate_exists(debate_id):
            return None
        try:
            with open(self._get_debate_path(debate_id), 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error reading debate file for {debate_id}: {e}")
            return None

    def save_debate(self, debate_id: str, debate_data: Dict[str, Any]) -> bool:
        """Saves the data for a specific debate."""
        try:
            with open(self._get_debate_path(debate_id), 'w', encoding='utf-8') as f:
                json.dump(debate_data, f, indent=4, ensure_ascii=False)
            logging.info(f"Successfully saved debate '{debate_id}'.")
            return True
        except IOError as e:
            logging.error(f"Error saving debate file for {debate_id}: {e}")
            return False

    def is_role_invited(self, debate_id: str, role_id: str) -> bool:
        """Checks if a role is already a participant in a debate."""
        debate_data = self.get_debate(debate_id)
        if debate_data and 'participants' in debate_data:
            return role_id in debate_data['participants']
        return False

    def add_role_to_debate(self, debate_id: str, role_id: str) -> bool:
        """Adds a role to the participants list of a debate."""
        debate_data = self.get_debate(debate_id)
        if not debate_data:
            logging.error(f"Cannot add role to non-existent debate '{debate_id}'.")
            return False
        
        if 'participants' not in debate_data:
            debate_data['participants'] = []

        debate_data['participants'].append(role_id)
        # Remove duplicates, preserving order of first appearance
        seen = set()
        debate_data['participants'] = [x for x in debate_data['participants'] if not (x in seen or seen.add(x))]
        
        return self.save_debate(debate_id, debate_data)
