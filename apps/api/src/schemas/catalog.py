"""Catalog schemas"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.catalog import CatalogCategory

# JSON value types for specifications
type JSONValue = str | int | float | bool | None | list[JSONValue] | dict[str, JSONValue]


class CatalogBase(BaseModel):
    """Base catalog schema"""

    name: str = Field(min_length=1, max_length=255)
    manufacturer: str = Field(min_length=1, max_length=255)
    model_number: str = Field(min_length=1, max_length=100)
    category: CatalogCategory
    sku_code: str | None = Field(default=None, max_length=50)
    description: str | None = None
    specifications: dict[str, JSONValue] | None = None  # JSONB field for flexible specs
    weight_grams: int | None = Field(default=None, gt=0)
    max_flight_time_minutes: int | None = Field(default=None, gt=0)
    max_range_meters: int | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    spec_document_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class CatalogCreate(CatalogBase):
    """Catalog creation schema"""

    organization_id: UUID


class CatalogUpdate(BaseModel):
    """Catalog update schema"""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, min_length=1, max_length=255)
    model_number: str | None = Field(default=None, min_length=1, max_length=100)
    category: CatalogCategory | None = None
    sku_code: str | None = Field(default=None, max_length=50)
    description: str | None = None
    specifications: dict[str, JSONValue] | None = None
    weight_grams: int | None = Field(default=None, gt=0)
    max_flight_time_minutes: int | None = Field(default=None, gt=0)
    max_range_meters: int | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    spec_document_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class CatalogResponse(CatalogBase):
    """Catalog response schema"""

    id: UUID
    organization_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CatalogListResponse(BaseModel):
    """Catalog list response schema"""

    catalogs: list[CatalogResponse]
    total: int
    page: int
    page_size: int
