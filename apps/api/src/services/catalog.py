"""Catalog service"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.catalog import Catalog, CatalogCategory
from src.schemas.catalog import CatalogCreate, CatalogUpdate


class CatalogService:
    """Service for catalog operations"""

    @staticmethod
    async def get_catalog(db: AsyncSession, catalog_id: UUID) -> Catalog | None:
        """Get catalog by ID"""
        result = await db.execute(select(Catalog).where(Catalog.id == catalog_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_catalogs(
        db: AsyncSession,
        organization_id: UUID,
        category: CatalogCategory | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Catalog], int]:
        """Get catalogs with optional filters and pagination"""
        query = select(Catalog).where(Catalog.organization_id == organization_id)

        # Apply filters
        if category is not None:
            query = query.where(Catalog.category == category)
        if is_active is not None:
            query = query.where(Catalog.is_active == is_active)

        # Get total count
        count_query = select(Catalog).where(Catalog.organization_id == organization_id)
        if category is not None:
            count_query = count_query.where(Catalog.category == category)
        if is_active is not None:
            count_query = count_query.where(Catalog.is_active == is_active)

        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Apply pagination and ordering
        query = query.order_by(Catalog.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        catalogs = result.scalars().all()

        return list(catalogs), total

    @staticmethod
    async def create_catalog(db: AsyncSession, catalog_data: CatalogCreate) -> Catalog:
        """Create a new catalog"""
        catalog = Catalog(**catalog_data.model_dump())
        db.add(catalog)
        await db.commit()
        await db.refresh(catalog)
        return catalog

    @staticmethod
    async def update_catalog(
        db: AsyncSession,
        catalog: Catalog,
        catalog_data: CatalogUpdate,
    ) -> Catalog:
        """Update an existing catalog"""
        update_data = catalog_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(catalog, field, value)

        # Increment version on update
        catalog.version += 1

        await db.commit()
        await db.refresh(catalog)
        return catalog

    @staticmethod
    async def delete_catalog(db: AsyncSession, catalog: Catalog) -> None:
        """Delete a catalog (soft delete by setting is_active=False)"""
        catalog.is_active = False
        await db.commit()

    @staticmethod
    async def search_catalogs(
        db: AsyncSession,
        organization_id: UUID,
        search_query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Catalog], int]:
        """Search catalogs by name, manufacturer, or model number"""
        search_pattern = f"%{search_query}%"

        query = (
            select(Catalog)
            .where(Catalog.organization_id == organization_id)
            .where(
                (Catalog.name.ilike(search_pattern))
                | (Catalog.manufacturer.ilike(search_pattern))
                | (Catalog.model_number.ilike(search_pattern))
            )
        )

        # Get total count
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # Apply pagination
        query = query.order_by(Catalog.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        catalogs = result.scalars().all()

        return list(catalogs), total
