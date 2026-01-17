"""Catalog router"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.dependencies.auth import ManagerUser
from src.models.catalog import CatalogCategory
from src.schemas.catalog import (
    CatalogCreate,
    CatalogListResponse,
    CatalogResponse,
    CatalogUpdate,
)
from src.services.catalog import CatalogService

router = APIRouter(prefix="/catalogs", tags=["catalogs"])

DatabaseDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=CatalogListResponse)
async def get_catalogs(
    db: DatabaseDep,
    current_user: ManagerUser,
    category: CatalogCategory | None = None,
    is_active: bool | None = Query(default=True),
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> CatalogListResponse:
    """Get catalogs with optional filters"""
    skip = (page - 1) * page_size

    if search:
        catalogs, total = await CatalogService.search_catalogs(
            db=db,
            organization_id=current_user.organization_id,
            search_query=search,
            skip=skip,
            limit=page_size,
        )
    else:
        catalogs, total = await CatalogService.get_catalogs(
            db=db,
            organization_id=current_user.organization_id,
            category=category,
            is_active=is_active,
            skip=skip,
            limit=page_size,
        )

    return CatalogListResponse(
        catalogs=[CatalogResponse.model_validate(c) for c in catalogs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{catalog_id}", response_model=CatalogResponse)
async def get_catalog(
    catalog_id: UUID,
    db: DatabaseDep,
    current_user: ManagerUser,
) -> CatalogResponse:
    """Get a catalog by ID"""
    catalog = await CatalogService.get_catalog(db=db, catalog_id=catalog_id)

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found",
        )

    # Check organization access
    if catalog.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this catalog",
        )

    return CatalogResponse.model_validate(catalog)


@router.post("", response_model=CatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_catalog(
    catalog_data: CatalogCreate,
    db: DatabaseDep,
    current_user: ManagerUser,
) -> CatalogResponse:
    """Create a new catalog"""
    # Ensure the organization_id matches the current user's organization
    if catalog_data.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create catalog for a different organization",
        )

    catalog = await CatalogService.create_catalog(db=db, catalog_data=catalog_data)
    return CatalogResponse.model_validate(catalog)


@router.patch("/{catalog_id}", response_model=CatalogResponse)
async def update_catalog(
    catalog_id: UUID,
    catalog_data: CatalogUpdate,
    db: DatabaseDep,
    current_user: ManagerUser,
) -> CatalogResponse:
    """Update a catalog"""
    catalog = await CatalogService.get_catalog(db=db, catalog_id=catalog_id)

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found",
        )

    # Check organization access
    if catalog.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this catalog",
        )

    updated_catalog = await CatalogService.update_catalog(
        db=db,
        catalog=catalog,
        catalog_data=catalog_data,
    )

    return CatalogResponse.model_validate(updated_catalog)


@router.delete("/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog(
    catalog_id: UUID,
    db: DatabaseDep,
    current_user: ManagerUser,
) -> None:
    """Delete a catalog (soft delete)"""
    catalog = await CatalogService.get_catalog(db=db, catalog_id=catalog_id)

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found",
        )

    # Check organization access
    if catalog.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this catalog",
        )

    await CatalogService.delete_catalog(db=db, catalog=catalog)
