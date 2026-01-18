"""Catalogサービステスト"""

from typing import TYPE_CHECKING

import pytest

from src.models.catalog import Catalog, CatalogCategory
from src.schemas.catalog import CatalogCreate, CatalogUpdate
from src.services.catalog import CatalogService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models.organization import Organization


@pytest.mark.asyncio
class TestCatalogService:
    """CatalogServiceのテスト"""

    async def test_get_catalog_success(
        self,
        db_session: AsyncSession,
        test_catalog: Catalog,
    ) -> None:
        """カタログ取得成功"""
        catalog = await CatalogService.get_catalog(db_session, test_catalog.id)
        assert catalog is not None
        assert catalog.id == test_catalog.id
        assert catalog.name == test_catalog.name

    async def test_get_catalog_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """存在しないカタログ取得"""
        from uuid import uuid4

        catalog = await CatalogService.get_catalog(db_session, uuid4())
        assert catalog is None

    async def test_get_catalogs_all(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_catalog: Catalog,
    ) -> None:
        """全カタログ取得"""
        catalogs, total = await CatalogService.get_catalogs(
            db=db_session,
            organization_id=test_organization.id,
        )
        assert total == 1
        assert len(catalogs) == 1
        assert catalogs[0].id == test_catalog.id

    async def test_get_catalogs_filter_by_category(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_catalog: Catalog,
    ) -> None:
        """カテゴリーでフィルタ"""
        # ドローンカテゴリーで検索
        catalogs, total = await CatalogService.get_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            category=CatalogCategory.DRONE,
        )
        assert total == 1
        assert len(catalogs) == 1

        # バッテリーカテゴリーで検索（該当なし）
        catalogs, total = await CatalogService.get_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            category=CatalogCategory.BATTERY,
        )
        assert total == 0
        assert len(catalogs) == 0

    async def test_get_catalogs_filter_by_active_status(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_catalog: Catalog,
    ) -> None:
        """有効/無効でフィルタ"""
        # 有効なカタログのみ
        catalogs, total = await CatalogService.get_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            is_active=True,
        )
        assert total == 1

        # 無効なカタログのみ
        _catalogs, total = await CatalogService.get_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            is_active=False,
        )
        assert total == 0

    async def test_get_catalogs_pagination(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
    ) -> None:
        """ページネーション"""
        # 複数カタログ作成
        for i in range(5):
            catalog = Catalog(
                organization_id=test_organization.id,
                name=f"Catalog {i}",
                category=CatalogCategory.DRONE,
                manufacturer="Test",
                model_number=f"TEST-{i}",
                is_active=True,
                version=1,
            )
            db_session.add(catalog)
        await db_session.commit()

        # ページ1（2件）
        catalogs, total = await CatalogService.get_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            skip=0,
            limit=2,
        )
        assert total == 5
        assert len(catalogs) == 2

        # ページ2（2件）
        catalogs, total = await CatalogService.get_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            skip=2,
            limit=2,
        )
        assert total == 5
        assert len(catalogs) == 2

    async def test_create_catalog_success(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
    ) -> None:
        """カタログ作成成功"""
        catalog_data = CatalogCreate(
            organization_id=test_organization.id,
            name="New Catalog",
            category=CatalogCategory.BATTERY,
            manufacturer="Test Manufacturer",
            model_number="TEST-001",
            price=50000,
        )

        catalog = await CatalogService.create_catalog(db_session, catalog_data)
        assert catalog.id is not None
        assert catalog.name == "New Catalog"
        assert catalog.category == CatalogCategory.BATTERY
        assert catalog.price == 50000
        assert catalog.version == 1

    async def test_update_catalog_success(
        self,
        db_session: AsyncSession,
        test_catalog: Catalog,
    ) -> None:
        """カタログ更新成功"""
        original_version = test_catalog.version

        catalog_data = CatalogUpdate(
            name="Updated Name",
            price=250000,
        )

        updated_catalog = await CatalogService.update_catalog(
            db=db_session,
            catalog=test_catalog,
            catalog_data=catalog_data,
        )

        assert updated_catalog.name == "Updated Name"
        assert updated_catalog.price == 250000
        assert updated_catalog.version == original_version + 1

    async def test_update_catalog_partial(
        self,
        db_session: AsyncSession,
        test_catalog: Catalog,
    ) -> None:
        """部分更新"""
        original_name = test_catalog.name

        catalog_data = CatalogUpdate(price=300000)

        updated_catalog = await CatalogService.update_catalog(
            db=db_session,
            catalog=test_catalog,
            catalog_data=catalog_data,
        )

        assert updated_catalog.name == original_name  # 変更されていない
        assert updated_catalog.price == 300000  # 更新された

    async def test_delete_catalog_soft_delete(
        self,
        db_session: AsyncSession,
        test_catalog: Catalog,
    ) -> None:
        """ソフトデリート"""
        assert test_catalog.is_active is True

        await CatalogService.delete_catalog(db_session, test_catalog)

        # リフレッシュして確認
        await db_session.refresh(test_catalog)
        assert test_catalog.is_active is False

    async def test_search_catalogs_by_name(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_catalog: Catalog,
    ) -> None:
        """名前で検索"""
        catalogs, total = await CatalogService.search_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            search_query="Mavic",
        )
        assert total == 1
        assert catalogs[0].id == test_catalog.id

    async def test_search_catalogs_by_manufacturer(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_catalog: Catalog,
    ) -> None:
        """メーカーで検索"""
        catalogs, total = await CatalogService.search_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            search_query="DJI",
        )
        assert total == 1
        assert catalogs[0].id == test_catalog.id

    async def test_search_catalogs_by_model_number(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_catalog: Catalog,
    ) -> None:
        """型番で検索"""
        catalogs, total = await CatalogService.search_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            search_query="CP.MA",
        )
        assert total == 1
        assert catalogs[0].id == test_catalog.id

    async def test_search_catalogs_no_results(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
    ) -> None:
        """検索結果なし"""
        catalogs, total = await CatalogService.search_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            search_query="NonExistent",
        )
        assert total == 0
        assert len(catalogs) == 0

    async def test_search_catalogs_pagination(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
    ) -> None:
        """検索結果のページネーション"""
        # 複数カタログ作成
        for i in range(5):
            catalog = Catalog(
                organization_id=test_organization.id,
                name=f"DJI Drone {i}",
                category=CatalogCategory.DRONE,
                manufacturer="DJI",
                model_number=f"DJI-{i}",
                is_active=True,
                version=1,
            )
            db_session.add(catalog)
        await db_session.commit()

        # ページ1
        catalogs, total = await CatalogService.search_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            search_query="DJI",
            skip=0,
            limit=2,
        )
        assert total == 5
        assert len(catalogs) == 2

        # ページ2
        catalogs, total = await CatalogService.search_catalogs(
            db=db_session,
            organization_id=test_organization.id,
            search_query="DJI",
            skip=2,
            limit=2,
        )
        assert total == 5
        assert len(catalogs) == 2
