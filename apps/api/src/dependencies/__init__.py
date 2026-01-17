"""FastAPI dependencies"""

from src.dependencies.auth import (
    AdminUser,
    CurrentUser,
    ManagerUser,
    OperatorUser,
    get_current_active_user,
    get_current_user,
    oauth2_scheme,
    require_admin,
    require_manager,
    require_operator,
    require_roles,
)

__all__ = [
    "AdminUser",
    "CurrentUser",
    "ManagerUser",
    "OperatorUser",
    "get_current_active_user",
    "get_current_user",
    "oauth2_scheme",
    "require_admin",
    "require_manager",
    "require_operator",
    "require_roles",
]
