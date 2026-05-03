"""
IntelligentRoleManager Wrapper
Provides backward compatibility with RoleManager API while using IntelligentRoleManager functionality
"""

import os
import glob
import asyncio
from pathlib import Path


class IntelligentRoleManagerWrapper:
    """
    Wrapper for IntelligentRoleManager to maintain backward compatibility
    with RoleManager API while providing intelligent model checking features.
    """

    def __init__(self, roles_dir_path=None, model_provider=None):
        from daip_live.p4_role_manager_tools.intelligent_role_manager import IntelligentRoleManager
        from daip_live.p4_role_manager_tools.role_manager import RoleManager

        self._internal_manager = IntelligentRoleManager(
            roles_dir=roles_dir_path or "roles",
            model_provider=model_provider
        )
        self._roles_dir_path = roles_dir_path or "roles"

        # Also maintain a standard RoleManager for fallback
        self._fallback_manager = RoleManager(roles_dir_path=roles_dir_path)

    def get_role_by_name(self, name):
        """
        Get role by name - check if file exists first to avoid creating default roles
        """
        # Check if role file exists
        role_file_path = os.path.join(self._internal_manager.roles_dir, f"{name}.yaml")

        if os.path.exists(role_file_path):
            # File exists, use intelligent manager to load it
            return self._internal_manager.load_role_from_file(name)
        else:
            # File doesn't exist, use fallback manager
            return self._fallback_manager.get_role_by_name(name)

    def list_roles(self):
        """
        List all available roles - mimic standard RoleManager.list_roles behavior
        """
        roles = []
        # Find all yaml files in roles directory
        role_files = glob.glob(os.path.join(self._roles_dir_path, "*.yaml"))

        for file_path in role_files:
            role_name = os.path.splitext(os.path.basename(file_path))[0]
            role = self.get_role_by_name(role_name)
            if role is not None:
                roles.append(role)

        return roles

    def update_role_models(self, role):
        """
        Update role models using intelligent model replacement logic
        """
        return asyncio.run(self._internal_manager.update_role_models(role))

    def check_model_availability(self):
        """
        Check model availability using internal manager
        """
        return asyncio.run(self._internal_manager.check_model_availability())