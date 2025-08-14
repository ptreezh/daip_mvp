import json
import logging
import os
from typing import Any, Dict, List

try:
    from src.role_utils import standardize_role_dict

    ROLE_UTILS_AVAILABLE = True
except ImportError:
    ROLE_UTILS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExpertService:
    """A service layer for managing experts (roles).
    It encapsulates the business logic for expert creation, searching,
    and batch operations, interacting with the AppState and underlying libraries.
    """

    def __init__(self, app_state: Any): # Use Any to avoid circular import type hint
        self.app_state = app_state
        if not ROLE_UTILS_AVAILABLE:
            logger.warning("role_utils not available. Some functionalities will be disabled.")

    def get_all_experts(self) -> List[Any]:
        """Retrieves all experts from the role details."""
        # Convert role details to expert-like objects
        experts = []
        for name, details in self.app_state.all_roles_details.items():
            expert = type('Expert', (), {
                'name': name,
                'description': details.get('desc', ''),
                'to_dict': lambda self=details: dict(details, name=name)
            })()
            experts.append(expert)
        return experts

    def create_expert(self, expert_data: Dict[str, Any]) -> Any:
        """Creates a single expert, handles validation and saving.
        Raises ValueError if the expert already exists.
        """
        if not ROLE_UTILS_AVAILABLE:
            raise Exception("Role utils are not available for expert creation.")

        # Check if expert already exists
        expert_name = expert_data.get('name', '')
        if expert_name in self.app_state.all_roles_details:
            raise ValueError(f"Expert '{expert_name}' already exists.")

        # Standardize the role data
        standardized_role = standardize_role_dict(expert_data)

        # Save to user-defined roles file
        safe_name = "".join(c for c in expert_name if c.isalnum() or c in ("_", "-")).strip()
        filename = f"{safe_name}.json"
        filepath = os.path.join(self.app_state.user_defined_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(standardized_role, f, ensure_ascii=False, indent=2)

        # Reload roles to include the new expert
        self.app_state.load_all_roles()

        # Return expert-like object
        expert = type('Expert', (), {
            'name': expert_name,
            'description': standardized_role.get('desc', ''),
            'to_dict': lambda: standardized_role
        })()
        return expert

    def batch_import_experts(
        self, roles_data: List[Dict[str, Any]], overwrite: bool, validate_only: bool
    ) -> Dict[str, Any]:
        """Batch imports experts from a list of dictionaries.
        Handles standardization, file writing, validation, and state reloading.
        """
        if not ROLE_UTILS_AVAILABLE:
            raise Exception("Role utils are not available for batch import.")

        results = {
            "total": len(roles_data),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": [],
        }

        for i, role_data in enumerate(roles_data):
            role_name = role_data.get("name", f"UnnamedRole_{i}")
            try:
                standardized_role = standardize_role_dict(role_data)
                role_name = standardized_role.get("name", role_name)
                safe_name = "".join(c for c in role_name if c.isalnum() or c in ("_", "-")).strip()
                filename = f"{safe_name}.json"
                filepath = os.path.join(self.app_state.user_defined_dir, filename)

                if os.path.exists(filepath) and not overwrite:
                    results["skipped"] += 1
                    results["details"].append({"index": i, "name": role_name, "status": "skipped", "reason": "File exists and overwrite is false."})
                    continue

                if not validate_only:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(standardized_role, f, ensure_ascii=False, indent=2)

                results["success"] += 1
                results["details"].append({"index": i, "name": role_name, "status": "success"})

            except Exception as e:
                logger.error(f"Failed to import role '{role_name}': {e}", exc_info=True)
                results["failed"] += 1
                results["details"].append({"index": i, "name": role_name, "status": "failed", "reason": str(e)})

        if not validate_only and results["success"] > 0:
            logger.info("Batch import successful, reloading roles.")
            self.app_state.load_all_roles()

        return results

    def search_experts_by_embedding(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches for experts using vector embeddings and returns a formatted list."""
        search_results = self.app_state.search_roles_by_vector(query, top_k)
        reformatted_results = [
            {"name": r["role"]["name"], "desc": r["role"].get("desc", r["role"].get("description", "")), "score": r["score"]}
            for r in search_results
        ]
        return reformatted_results
