"""Manages the definitions and capabilities of different roles in the system."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, List

# Define the base directory for roles
ROLES_DIR = Path("roles")


@dataclass
class Role:
    """Represents a role definition."""

    id: str
    name: str
    description: str
    system_prompt: str
    capabilities: List[str]
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Converts the Role object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "capabilities": self.capabilities,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Role":
        """Creates a Role object from a dictionary with enhanced error tolerance."""
        if isinstance(data, list):
            data = data[0] if data and isinstance(data[0], dict) else {}

        if not isinstance(data, dict):
            data = {}

        role_id = data.get("id") or data.get("name") or "unknown_id"
        name = data.get("name") or data.get("id") or "Unknown Role"
        description = data.get("description") or data.get("system_prompt") or f"Role: {name}"
        system_prompt = data.get("system_prompt") or data.get("description") or f"You are {name}."

        capabilities = data.get("capabilities", [])
        if not isinstance(capabilities, list):
            capabilities = [str(capabilities)] if capabilities else []

        if "expertise" in data:
            expertise = data["expertise"]
            if isinstance(expertise, list):
                capabilities.extend(expertise)
            elif isinstance(expertise, str):
                capabilities.append(expertise)

        tags = data.get("tags", [])
        if not isinstance(tags, list):
            tags = [str(tags)] if tags else []

        return cls(
            id=str(role_id),
            name=str(name),
            description=str(description),
            system_prompt=str(system_prompt),
            capabilities=list(set(capabilities)),
            tags=list(set(tags)),
        )


class RoleManager:
    """Loads, manages, and persists role definitions from individual JSON files."""

    def __init__(self, roles_directory: Path = ROLES_DIR) -> None:
        """Initializes the RoleManager by loading roles from JSON files in the specified directory."""
        self.roles_directory = roles_directory
        self._roles: dict[str, Role] = {}
        self._load_roles()
        logging.info(f"RoleManager initialized. Roles directory: {self.roles_directory}")

    def _load_roles(self) -> None:
        """Loads all role definitions from the roles directory."""
        self._roles = {}
        self.roles_directory.mkdir(parents=True, exist_ok=True)

        loaded_count = 0
        for role_file in self.roles_directory.glob("*.json"):
            try:
                with open(role_file, encoding="utf-8") as f:
                    role_data = json.load(f)
                if not isinstance(role_data, dict) or "name" not in role_data or "description" not in role_data:
                    logging.warning(f"Skipping {role_file}: invalid format or missing required fields.")
                    continue
                role = Role.from_dict(role_data)
                self._roles[role.id] = role
                loaded_count += 1
            except (json.JSONDecodeError, KeyError, Exception) as e:
                logging.error(f"Error loading role from {role_file}: {e}")
        logging.info(f"Successfully loaded {loaded_count} roles from {self.roles_directory}")

    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Retrieves a role by its ID. If not in memory, attempts to load from file."""
        if role_id not in self._roles:
            role_file = self.roles_directory / f"{role_id}.json"
            if role_file.exists():
                try:
                    with open(role_file, encoding="utf-8") as f:
                        role_data = json.load(f)
                    role = Role.from_dict(role_data)
                    self._roles[role.id] = role
                    logging.info(f"Dynamically loaded role '{role_id}' from file.")
                    return role
                except Exception as e:
                    logging.error(f"Error loading role '{role_id}' from file {role_file}: {e}")
            else:
                logging.warning(f"Role file for '{role_id}' not found at {role_file}.")
        return self._roles.get(role_id)

    def get_role(self, role_id: str) -> Optional[Role]:
        """Alias for get_role_by_id for compatibility."""
        return self.get_role_by_id(role_id)

    def list_roles(self) -> list[Role]:
        """Returns a list of all available roles (reloads from disk to ensure freshness)."""
        self._load_roles()
        return list(self._roles.values())

    def save_role(self, role: Role) -> bool:
        """Saves a role definition to a JSON file."""
        role_file = self.roles_directory / f"{role.id}.json"
        try:
            with open(role_file, "w", encoding="utf-8") as f:
                json.dump(role.to_dict(), f, indent=4, ensure_ascii=False)
            self._roles[role.id] = role
            logging.info(f"Successfully saved role '{role.id}' to {role_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving role '{role.id}' to {role_file}: {e}")
            return False

    def delete_role(self, role_id: str) -> bool:
        """Deletes a role definition file and removes it from memory."""
        role_file = self.roles_directory / f"{role_id}.json"
        if role_file.exists():
            try:
                role_file.unlink()
                if role_id in self._roles:
                    del self._roles[role_id]
                logging.info(f"Successfully deleted role '{role_id}' and its file.")
                return True
            except Exception as e:
                logging.error(f"Error deleting role file {role_file}: {e}")
                return False
        else:
            logging.warning(f"Attempted to delete non-existent role file for '{role_id}'.")
            return False

    def role_exists(self, role_id: str) -> bool:
        """Check if a role exists by ID or name."""
        # Check by ID first (common case)
        if role_id in self._roles:
            return True
        
        # Check by name
        for role in self._roles.values():
            if role.name == role_id:
                return True
        
        # Check if file exists for dynamic loading
        role_file = self.roles_directory / f"{role_id}.json"
        if role_file.exists():
            return True
        
        return False

    def create_role(self, role_data: dict[str, Any]) -> bool:
        """Create a new role, ensuring all fields are handled."""
        try:
            if "name" not in role_data or not role_data["name"]:
                raise ValueError("Role name is required.")

            # Set defaults for core fields if not provided
            role_data.setdefault("id", role_data["name"].lower().replace(" ", "_"))
            role_data.setdefault("description", "No description provided.")
            role_data.setdefault("system_prompt", f"You are {role_data['name']}. {role_data.get('description')}")
            role_data.setdefault("capabilities", ["general_assistance"])
            role_data.setdefault("tags", [])

            role = Role.from_dict(role_data)
            return self.save_role(role)
            
        except Exception as e:
            logging.error(f"Error creating role: {e}")
            return False

    def update_role(self, role_id: str, update_data: dict[str, Any]) -> bool:
        """Update an existing role."""
        try:
            role = self.get_role(role_id)
            if not role:
                logging.error(f"Role not found: {role_id}")
                return False
            
            role_dict = role.to_dict()
            role_dict.update(update_data)
            
            updated_role = Role.from_dict(role_dict)
            return self.save_role(updated_role)
            
        except Exception as e:
            logging.error(f"Error updating role {role_id}: {e}")
            return False

    def invite_role_to_debate(self, role_id: str, debate_id: str) -> bool:
        """Invite a role to participate in a debate."""
        try:
            if not self.role_exists(role_id):
                logging.error(f"Role not found: {role_id}")
                return False
            
            logging.info(f"Role {role_id} invited to debate {debate_id}")
            # TODO: Integrate with debate system
            return True
            
        except Exception as e:
            logging.error(f"Error inviting role {role_id} to debate {debate_id}: {e}")
            return False

    def match_roles_to_task(self, task_description: str, task_type: str = "general", limit: int = 5) -> List[Dict[str, Any]]:
        """Match roles to a task based on expertise and capabilities.
        
        Args:
            task_description (str): Description of the task
            task_type (str): Type of task (general, debate, wiki_creation, etc.)
            limit (int): Maximum number of roles to return
            
        Returns:
            List[Dict[str, Any]]: List of matched roles with relevance scores
        """
        try:
            # Reload roles to ensure we have the latest
            self._load_roles()
            
            matched_roles = []
            
            for role in self._roles.values():
                # Calculate relevance score
                relevance_score = self._calculate_role_relevance(role, task_description, task_type)
                
                if relevance_score > 0.3:  # Minimum relevance threshold
                    matched_roles.append({
                        "role": role,
                        "relevance_score": relevance_score,
                        "match_reasons": self._get_match_reasons(role, task_description, task_type)
                    })
            
            # Sort by relevance score and return top matches
            matched_roles.sort(key=lambda x: x["relevance_score"], reverse=True)
            return matched_roles[:limit]
            
        except Exception as e:
            logging.error(f"Error matching roles to task: {e}")
            return []

    def _calculate_role_relevance(self, role: 'Role', task_description: str, task_type: str) -> float:
        """Calculate relevance score for a role against a task.
        
        Args:
            role (Role): Role to evaluate
            task_description (str): Task description
            task_type (str): Type of task
            
        Returns:
            float: Relevance score between 0.0 and 1.0
        """
        score = 0.0
        
        # Normalize inputs
        task_lower = task_description.lower()
        role_name_lower = role.name.lower()
        role_desc_lower = role.description.lower()
        role_prompt_lower = role.system_prompt.lower()
        
        # 1. Direct name matching (highest weight)
        if any(keyword in role_name_lower for keyword in task_lower.split()):
            score += 0.4
        
        # 2. Description matching
        desc_keywords = role_desc_lower.split()
        task_keywords = task_lower.split()
        matches = sum(1 for tk in task_keywords if any(tk in dk for dk in desc_keywords))
        if matches > 0:
            score += min(0.3, matches * 0.05)
        
        # 3. System prompt matching
        prompt_keywords = role_prompt_lower.split()
        prompt_matches = sum(1 for tk in task_keywords if any(tk in pk for pk in prompt_keywords))
        if prompt_matches > 0:
            score += min(0.2, prompt_matches * 0.03)
        
        # 4. Capabilities matching
        if hasattr(role, 'capabilities') and role.capabilities:
            for capability in role.capabilities:
                if capability.lower() in task_lower or any(tk in capability.lower() for tk in task_keywords):
                    score += 0.1
        
        # 5. Tags matching
        if hasattr(role, 'tags') and role.tags:
            for tag in role.tags:
                if tag.lower() in task_lower or any(tk in tag.lower() for tk in task_keywords):
                    score += 0.05
        
        # 6. Task type specific adjustments
        task_type_scores = {
            "debate": 0.1 if any(word in role_name_lower for word in ["debate", "argument", "logic", "philosophy"]) else 0,
            "wiki_creation": 0.1 if any(word in role_name_lower for word in ["wiki", "knowledge", "research", "academic"]) else 0,
            "analysis": 0.1 if any(word in role_name_lower for word in ["analysis", "data", "research", "science"]) else 0,
            "creative": 0.1 if any(word in role_name_lower for word in ["creative", "design", "art", "innovation"]) else 0
        }
        
        score += task_type_scores.get(task_type, 0)
        
        return min(1.0, score)

    def _get_match_reasons(self, role: 'Role', task_description: str, task_type: str) -> List[str]:
        """Get reasons why a role matches a task.
        
        Args:
            role (Role): Matched role
            task_description (str): Task description
            task_type (str): Type of task
            
        Returns:
            List[str]: List of match reasons
        """
        reasons = []
        
        task_lower = task_description.lower()
        role_name_lower = role.name.lower()
        role_desc_lower = role.description.lower()
        
        # Check name matches
        if any(keyword in role_name_lower for keyword in task_lower.split()):
            reasons.append(f"Role name '{role.name}' contains relevant keywords")
        
        # Check description matches
        desc_keywords = role_desc_lower.split()
        task_keywords = task_lower.split()
        matches = sum(1 for tk in task_keywords if any(tk in dk for dk in desc_keywords))
        if matches > 0:
            reasons.append(f"Role description contains {matches} relevant keywords")
        
        # Check capabilities
        if hasattr(role, 'capabilities') and role.capabilities:
            relevant_caps = [cap for cap in role.capabilities if cap.lower() in task_lower]
            if relevant_caps:
                reasons.append(f"Role has relevant capabilities: {', '.join(relevant_caps)}")
        
        # Check tags
        if hasattr(role, 'tags') and role.tags:
            relevant_tags = [tag for tag in role.tags if tag.lower() in task_lower]
            if relevant_tags:
                reasons.append(f"Role has relevant tags: {', '.join(relevant_tags)}")
        
        # Task type specific reasons
        if task_type == "debate" and any(word in role_name_lower for word in ["debate", "argument", "logic"]):
            reasons.append("Role has debate-relevant expertise")
        
        if task_type == "wiki_creation" and any(word in role_name_lower for word in ["wiki", "knowledge", "research"]):
            reasons.append("Role has wiki creation relevant expertise")
        
        return reasons if reasons else ["General relevance match"]

    def get_domain_statistics(self) -> Dict[str, Any]:
        """Get statistics about role domains and expertise areas.
        
        Returns:
            Dict[str, Any]: Statistics including domain counts, expertise areas, etc.
        """
        try:
            self._load_roles()
            
            stats = {
                "total_roles": len(self._roles),
                "domains": {},
                "expertise_areas": {},
                "capability_counts": {},
                "tag_counts": {}
            }
            
            for role in self._roles.values():
                # Extract domain from role name or description
                domain = self._extract_domain_from_role(role)
                stats["domains"][domain] = stats["domains"].get(domain, 0) + 1
                
                # Extract expertise areas
                if hasattr(role, 'capabilities') and role.capabilities:
                    for capability in role.capabilities:
                        stats["expertise_areas"][capability] = stats["expertise_areas"].get(capability, 0) + 1
                
                # Count capabilities
                if hasattr(role, 'capabilities') and role.capabilities:
                    for capability in role.capabilities:
                        stats["capability_counts"][capability] = stats["capability_counts"].get(capability, 0) + 1
                
                # Count tags
                if hasattr(role, 'tags') and role.tags:
                    for tag in role.tags:
                        stats["tag_counts"][tag] = stats["tag_counts"].get(tag, 0) + 1
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting domain statistics: {e}")
            return {"total_roles": 0, "error": str(e)}

    def _extract_domain_from_role(self, role: 'Role') -> str:
        """Extract domain category from role information.
        
        Args:
            role (Role): Role to analyze
            
        Returns:
            str: Domain category
        """
        role_text = f"{role.name} {role.description}".lower()
        
        # Domain keyword mapping
        domain_mapping = {
            "ai": ["ai", "artificial intelligence", "machine learning", "llm"],
            "sociology": ["sociology", "social", "cultural", "anthropology"],
            "philosophy": ["philosophy", "ethics", "logic", "theoretical"],
            "technology": ["technology", "digital", "software", "computing"],
            "business": ["business", "management", "corporate", "organizational"],
            "research": ["research", "academic", "scientific", "study"],
            "politics": ["politics", "policy", "government", "governance"],
            "economics": ["economics", "financial", "economic", "market"],
            "psychology": ["psychology", "cognitive", "behavioral", "mental"],
            "environment": ["environment", "climate", "sustainability", "ecological"]
        }
        
        for domain, keywords in domain_mapping.items():
            if any(keyword in role_text for keyword in keywords):
                return domain
        
        return "general"
