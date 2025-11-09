"""
Access control - Permission and policy management.

Manages access permissions for agents and tools with
policy-based authorization.
"""

import logging
from typing import Dict, Set, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Available permissions."""
    CREATE_AGENT = "create_agent"
    DELETE_AGENT = "delete_agent"
    COMMAND_AGENT = "command_agent"
    BROWSER_USE = "browser_use"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    ADMIN = "admin"


class AccessControl:
    """
    Policy-based access control system.

    Manages permissions for agents and operations.
    Uses secure defaults: deny-by-default policy.

    Example:
        >>> access = AccessControl()
        >>> access.grant_permission("user1", Permission.CREATE_AGENT)
        >>> if access.check_permission("user1", Permission.CREATE_AGENT):
        ...     # Allow operation
    """

    def __init__(self, allow_system_admin: bool = False):
        """
        Initialize access control.

        Args:
            allow_system_admin: Whether to grant admin permission to "system" user.
                               Default is False for security. Enable only if needed.
        """
        self.permissions: Dict[str, Set[Permission]] = {}
        self.policies: List[Dict[str, Any]] = []

        # Only grant system admin if explicitly enabled
        if allow_system_admin:
            self.grant_permission("system", Permission.ADMIN)
            logger.warning(
                "System admin user enabled. This grants full permissions to 'system' user. "
                "Use only in trusted environments."
            )

    def grant_permission(self, user: str, permission: Permission) -> None:
        """
        Grant permission to user.

        Args:
            user: User identifier
            permission: Permission to grant
        """
        if user not in self.permissions:
            self.permissions[user] = set()

        self.permissions[user].add(permission)
        logger.info(f"Granted {permission.value} to {user}")

    def revoke_permission(self, user: str, permission: Permission) -> None:
        """Revoke permission from user."""
        if user in self.permissions:
            self.permissions[user].discard(permission)
            logger.info(f"Revoked {permission.value} from {user}")

    def check_permission(
        self,
        user: str,
        permission: Permission
    ) -> bool:
        """
        Check if user has permission.

        Args:
            user: User identifier
            permission: Permission to check

        Returns:
            True if user has permission
        """
        user_perms = self.permissions.get(user, set())

        # Admin has all permissions
        if Permission.ADMIN in user_perms:
            return True

        # Check specific permission
        return permission in user_perms

    def add_policy(
        self,
        policy_id: str,
        description: str,
        rules: Dict[str, Any]
    ) -> None:
        """Add access control policy."""
        policy = {
            "policy_id": policy_id,
            "description": description,
            "rules": rules,
        }
        self.policies.append(policy)
        logger.info(f"Added policy: {policy_id}")

    def check_policy(
        self,
        user: str,
        operation: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if operation allowed by policies.

        Args:
            user: User identifier
            operation: Operation name
            context: Operation context

        Returns:
            True if allowed by policies

        Note:
            Uses secure default: deny-by-default if no policies are configured.
            Administrators must explicitly configure allow policies.
        """
        # Secure default: deny if no policies configured
        if not self.policies:
            logger.warning(
                f"No policies configured - denying {operation} for {user}. "
                "Configure explicit allow policies for operations."
            )
            return False

        # Check each policy
        allowed = False
        for policy in self.policies:
            rules = policy.get("rules", {})

            # Block list check (takes precedence)
            if operation in rules.get("blocked_operations", []):
                logger.warning(
                    f"Policy {policy['policy_id']} blocked {operation} for {user}"
                )
                return False

            # Allow list check
            if operation in rules.get("allowed_operations", []):
                allowed = True

        if not allowed:
            logger.info(f"No policy allows {operation} for {user}")

        return allowed

    def get_user_permissions(self, user: str) -> List[str]:
        """Get all permissions for user."""
        perms = self.permissions.get(user, set())
        return [p.value for p in perms]
