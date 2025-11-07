"""
Fine-grained permission management system for DAIP-LIVE.
Controls access to tools and features based on user roles and permissions.
"""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class PermissionLevel(Enum):
    """Permission levels for tools and features."""
    DENIED = "denied"
    READ_ONLY = "read_only"
    BASIC = "basic"
    ADVANCED = "advanced"
    ADMIN = "admin"


class ToolPermission:
    """Permission settings for a specific tool."""

    def __init__(self, tool_name: str, level: PermissionLevel, granted_by: Optional[str] = None):
        self.tool_name = tool_name
        self.level = level
        self.granted_by = granted_by
        self.granted_at = datetime.now()
        self.last_used = None
        self.usage_count = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "tool_name": self.tool_name,
            "level": self.level.value,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ToolPermission":
        """Create from dictionary."""
        permission = cls(
            tool_name=data["tool_name"],
            level=PermissionLevel(data["level"]),
            granted_by=data.get("granted_by")
        )
        if data.get("granted_at"):
            permission.granted_at = datetime.fromisoformat(data["granted_at"])
        if data.get("last_used"):
            permission.last_used = datetime.fromisoformat(data["last_used"])
        permission.usage_count = data.get("usage_count", 0)
        return permission


class PermissionManager:
    """Manages permissions for tools and features."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_file()
        self.user_permissions: Dict[str, Dict[str, ToolPermission]] = {}
        self.default_permissions: Dict[str, PermissionLevel] = self._get_default_tool_permissions()
        self.load_permissions()

    def _get_default_config_file(self) -> str:
        """Get default permission configuration file path."""
        config_dir = Path.home() / ".daip"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "permissions.json")

    def _get_default_tool_permissions(self) -> Dict[str, PermissionLevel]:
        """Get default permission levels for tools."""
        return {
            # Core tools
            "gemini-cli": PermissionLevel.BASIC,
            "context7": PermissionLevel.BASIC,

            # Advanced tools
            "playwright": PermissionLevel.ADVANCED,
            "exa-search": PermissionLevel.BASIC,

            # Research tools
            "deepwiki": PermissionLevel.BASIC,
            "paper-downloader": PermissionLevel.BASIC,
            "format-converter": PermissionLevel.BASIC,

            # System tools
            "file-system": PermissionLevel.ADVANCED,
            "network-tools": PermissionLevel.ADVANCED,
            "system-commands": PermissionLevel.ADMIN,
        }

    def load_permissions(self) -> None:
        """Load permissions from configuration file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Load user permissions
                for user_id, tools in data.get("user_permissions", {}).items():
                    self.user_permissions[user_id] = {}
                    for tool_name, tool_data in tools.items():
                        self.user_permissions[user_id][tool_name] = ToolPermission.from_dict(tool_data)

                # Load default permissions
                for tool_name, level in data.get("default_permissions", {}).items():
                    try:
                        self.default_permissions[tool_name] = PermissionLevel(level)
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Warning: Could not load permissions from {self.config_file}: {e}")

    def save_permissions(self) -> None:
        """Save permissions to configuration file."""
        try:
            data = {
                "user_permissions": {},
                "default_permissions": {tool: level.value for tool, level in self.default_permissions.items()}
            }

            for user_id, tools in self.user_permissions.items():
                data["user_permissions"][user_id] = {}
                for tool_name, permission in tools.items():
                    data["user_permissions"][user_id][tool_name] = permission.to_dict()

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save permissions to {self.config_file}: {e}")

    def check_permission(self, user_id: str, tool_name: str) -> PermissionLevel:
        """Check if a user has permission to use a tool."""
        # Check user-specific permissions first
        if user_id in self.user_permissions and tool_name in self.user_permissions[user_id]:
            permission = self.user_permissions[user_id][tool_name]
            permission.last_used = datetime.now()
            permission.usage_count += 1
            return permission.level

        # Fall back to default permissions
        return self.default_permissions.get(tool_name, PermissionLevel.DENIED)

    def grant_permission(self, user_id: str, tool_name: str, level: PermissionLevel, granted_by: str) -> bool:
        """Grant permission to a user for a specific tool."""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = {}

        self.user_permissions[user_id][tool_name] = ToolPermission(tool_name, level, granted_by)
        self.save_permissions()
        return True

    def revoke_permission(self, user_id: str, tool_name: str) -> bool:
        """Revoke permission from a user for a specific tool."""
        if user_id in self.user_permissions and tool_name in self.user_permissions[user_id]:
            del self.user_permissions[user_id][tool_name]
            if not self.user_permissions[user_id]:  # Remove empty user entry
                del self.user_permissions[user_id]
            self.save_permissions()
            return True
        return False

    def list_user_permissions(self, user_id: str) -> Dict[str, ToolPermission]:
        """List all permissions for a specific user."""
        return self.user_permissions.get(user_id, {})

    def list_all_users(self) -> List[str]:
        """List all users with permissions."""
        return list(self.user_permissions.keys())

    def get_tool_users(self, tool_name: str) -> List[str]:
        """Get all users who have permission for a specific tool."""
        users = []
        for user_id, tools in self.user_permissions.items():
            if tool_name in tools:
                users.append(user_id)
        return users

    def reset_user_permissions(self, user_id: str) -> bool:
        """Reset all permissions for a user."""
        if user_id in self.user_permissions:
            del self.user_permissions[user_id]
            self.save_permissions()
            return True
        return False

    def get_permission_stats(self) -> Dict:
        """Get permission statistics."""
        stats = {
            "total_users": len(self.user_permissions),
            "total_tool_permissions": sum(len(tools) for tools in self.user_permissions.values()),
            "tools_by_level": {level.value: 0 for level in PermissionLevel},
            "most_used_tools": {},
            "recently_active": []
        }

        # Count tools by permission level
        for tools in self.user_permissions.values():
            for permission in tools.values():
                stats["tools_by_level"][permission.level.value] += 1

                # Track most used tools
                tool_name = permission.tool_name
                stats["most_used_tools"][tool_name] = stats["most_used_tools"].get(tool_name, 0) + permission.usage_count

        # Sort most used tools
        stats["most_used_tools"] = dict(sorted(stats["most_used_tools"].items(), key=lambda x: x[1], reverse=True)[:10])

        # Find recently active permissions (used in last 24 hours)
        now = datetime.now()
        for tools in self.user_permissions.values():
            for permission in tools.values():
                if permission.last_used and (now - permission.last_used).days < 1:
                    stats["recently_active"].append({
                        "tool": permission.tool_name,
                        "last_used": permission.last_used.isoformat(),
                        "usage_count": permission.usage_count
                    })

        return stats

    def cleanup_unused_permissions(self, days: int = 30) -> int:
        """Remove permissions that haven't been used in specified days."""
        removed_count = 0
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)

        users_to_remove = []
        for user_id, tools in self.user_permissions.items():
            tools_to_remove = []
            for tool_name, permission in tools.items():
                if permission.last_used and permission.last_used.timestamp() < cutoff_date:
                    tools_to_remove.append(tool_name)

            for tool_name in tools_to_remove:
                del tools[tool_name]
                removed_count += 1

            if not tools:  # Remove empty user entry
                users_to_remove.append(user_id)

        for user_id in users_to_remove:
            del self.user_permissions[user_id]

        if removed_count > 0 or users_to_remove:
            self.save_permissions()

        return removed_count