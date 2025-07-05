import json
import logging
import os
from typing import Any, Dict, List

from src.app_state import AppState

try:
    from src.role_utils import standardize_role_dict

    ROLE_UTILS_AVAILABLE = True
except ImportError:
    ROLE_UTILS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExpertService:
    """
    A service layer for managing experts (roles).
    It encapsulates the business logic for expert creation, searching,
    and batch operations, interacting with the AppState and underlying libraries.
    """

    def __init__(self, app_state: AppState):
        self.app_state = app_state
        if not ROLE_UTILS_AVAILABLE:
            logger.warning("role_utils not available. Some functionalities will be disabled.")

    def get_all_experts(self) -> List[Any]:
        """Retrieves all experts from the expert library."""
        return self.app_state.expert_library.get_all_experts()

    def create_expert(self, expert_data: Dict[str, Any]) -> Any:
        """
        Creates a single expert, handles validation and saving.
        Raises ValueError if the expert already exists.
        """
        # The expert_library's add_expert_manually should handle the logic
        # of checking for existence and saving the file.
        return self.app_state.expert_library.add_expert_manually(expert_data)

    def batch_import_experts(
        self, roles_data: List[Dict[str, Any]], overwrite: bool, validate_only: bool
    ) -> Dict[str, Any]:
        """
        Batch imports experts from a list of dictionaries.
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
            logger.info("Batch import successful, reloading expert library.")
            self.app_state.expert_library.load_experts_from_directory(force_reload=True)

        return results

    def search_experts_by_embedding(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches for experts using vector embeddings and returns a formatted list."""
        search_results = self.app_state.search_roles_by_vector(query, top_k)
        reformatted_results = [
            {"name": r["role"]["name"], "desc": r["role"].get("desc", r["role"].get("description", "")), "score": r["score"]}
            for r in search_results
        ]
        return reformatted_results