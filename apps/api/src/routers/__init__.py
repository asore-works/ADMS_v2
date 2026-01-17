"""API routers"""

from src.routers.auth import router as auth_router
from src.routers.catalog import router as catalog_router

__all__ = ["auth_router", "catalog_router"]
