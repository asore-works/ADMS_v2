"""Catalog APIテスト"""

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from src.models.catalog import Catalog, CatalogCategory
from src.models.organization import Organization

if TYPE_CHECKING:
    import httpx


@pytest.mark.asyncio
class TestCatalogRoutes:
    """Catalog APIエンドポイントテスト"""

    async def test_get_catalogs_success(
        self,
        client: httpx.AsyncClient,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """カタログ一覧取得成功"""
        response = await client.get("/api/v1/catalogs", headers=auth_headers_manager)

        assert response.status_code == 200
        data = response.json()
        assert "catalogs" in data
        assert "total" in data
        assert data["total"] >= 1

    async def test_get_catalogs_with_filters(
        self,
        client: httpx.AsyncClient,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """フィルタ付きカタログ一覧取得"""
        response = await client.get(
            "/api/v1/catalogs",
            headers=auth_headers_manager,
            params={"category": "drone", "is_active": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_get_catalogs_with_search(
        self,
        client: httpx.AsyncClient,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """検索付きカタログ一覧取得"""
        response = await client.get(
            "/api/v1/catalogs",
            headers=auth_headers_manager,
            params={"search": "Mavic"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_get_catalogs_pagination(
        self,
        client: httpx.AsyncClient,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """ページネーション"""
        response = await client.get(
            "/api/v1/catalogs",
            headers=auth_headers_manager,
            params={"page": 1, "page_size": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    async def test_get_catalogs_unauthorized(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        """認証なしでアクセス"""
        response = await client.get("/api/v1/catalogs")
        assert response.status_code == 401

    async def test_get_catalog_by_id_success(
        self,
        client: httpx.AsyncClient,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """ID指定でカタログ取得成功"""
        response = await client.get(
            f"/api/v1/catalogs/{test_catalog.id}",
            headers=auth_headers_manager,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_catalog.id)
        assert data["name"] == test_catalog.name

    async def test_get_catalog_not_found(
        self,
        client: httpx.AsyncClient,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """存在しないカタログ取得"""
        non_existent_id = uuid4()
        response = await client.get(
            f"/api/v1/catalogs/{non_existent_id}",
            headers=auth_headers_manager,
        )

        assert response.status_code == 404

    async def test_get_catalog_forbidden_different_org(
        self,
        client: httpx.AsyncClient,
        db_session: AsyncSession,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """別組織のカタログアクセス禁止"""
        # 別組織のカタログを作成
        other_org = Organization(name="Other Org", code="OTHER", is_active=True)
        db_session.add(other_org)
        await db_session.commit()
        await db_session.refresh(other_org)

        other_catalog = Catalog(
            organization_id=other_org.id,
            name="Other Catalog",
            category=CatalogCategory.DRONE,
            manufacturer="Test",
            model_number="TEST-001",
            is_active=True,
            version=1,
        )
        db_session.add(other_catalog)
        await db_session.commit()
        await db_session.refresh(other_catalog)

        response = await client.get(
            f"/api/v1/catalogs/{other_catalog.id}",
            headers=auth_headers_manager,
        )

        assert response.status_code == 403

    async def test_create_catalog_success(
        self,
        client: httpx.AsyncClient,
        test_organization: Organization,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """カタログ作成成功"""
        catalog_data = {
            "organization_id": str(test_organization.id),
            "name": "New Test Catalog",
            "category": "battery",
            "manufacturer": "Test Manufacturer",
            "model_number": "TEST-NEW-001",
            "price": 50000,
        }

        response = await client.post(
            "/api/v1/catalogs",
            headers=auth_headers_manager,
            json=catalog_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == catalog_data["name"]
        assert data["category"] == catalog_data["category"]

    async def test_create_catalog_forbidden_different_org(
        self,
        client: httpx.AsyncClient,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """別組織のカタログ作成禁止"""
        other_org_id = uuid4()
        catalog_data = {
            "organization_id": str(other_org_id),
            "name": "Forbidden Catalog",
            "category": "drone",
            "manufacturer": "Test",
            "model_number": "TEST-001",
        }

        response = await client.post(
            "/api/v1/catalogs",
            headers=auth_headers_manager,
            json=catalog_data,
        )

        assert response.status_code == 403

    async def test_create_catalog_invalid_data(
        self,
        client: httpx.AsyncClient,
        test_organization: Organization,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """不正なデータでカタログ作成"""
        catalog_data = {
            "organization_id": str(test_organization.id),
            # name が欠けている
            "category": "drone",
        }

        response = await client.post(
            "/api/v1/catalogs",
            headers=auth_headers_manager,
            json=catalog_data,
        )

        assert response.status_code == 422

    async def test_update_catalog_success(
        self,
        client: httpx.AsyncClient,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """カタログ更新成功"""
        # 現在のバージョンを取得
        get_response = await client.get(
            f"/api/v1/catalogs/{test_catalog.id}",
            headers=auth_headers_manager,
        )
        current_version = get_response.json()["version"]

        update_data = {
            "name": "Updated Catalog Name",
            "price": 350000,
        }

        response = await client.patch(
            f"/api/v1/catalogs/{test_catalog.id}",
            headers=auth_headers_manager,
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
        assert data["version"] == current_version + 1

    async def test_update_catalog_not_found(
        self,
        client: httpx.AsyncClient,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """存在しないカタログ更新"""
        non_existent_id = uuid4()
        update_data = {"name": "Updated Name"}

        response = await client.patch(
            f"/api/v1/catalogs/{non_existent_id}",
            headers=auth_headers_manager,
            json=update_data,
        )

        assert response.status_code == 404

    async def test_update_catalog_forbidden(
        self,
        client: httpx.AsyncClient,
        db_session: AsyncSession,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """別組織のカタログ更新禁止"""
        other_org = Organization(name="Other Org", code="OTHER", is_active=True)
        db_session.add(other_org)
        await db_session.commit()
        await db_session.refresh(other_org)

        other_catalog = Catalog(
            organization_id=other_org.id,
            name="Other Catalog",
            category=CatalogCategory.DRONE,
            manufacturer="Test",
            model_number="TEST-001",
            is_active=True,
            version=1,
        )
        db_session.add(other_catalog)
        await db_session.commit()
        await db_session.refresh(other_catalog)

        update_data = {"name": "Forbidden Update"}

        response = await client.patch(
            f"/api/v1/catalogs/{other_catalog.id}",
            headers=auth_headers_manager,
            json=update_data,
        )

        assert response.status_code == 403

    async def test_delete_catalog_success(
        self,
        client: httpx.AsyncClient,
        test_catalog: Catalog,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """カタログ削除成功（ソフトデリート）"""
        response = await client.delete(
            f"/api/v1/catalogs/{test_catalog.id}",
            headers=auth_headers_manager,
        )

        assert response.status_code == 204

        # 削除後は is_active = False になっているか確認
        get_response = await client.get(
            f"/api/v1/catalogs/{test_catalog.id}",
            headers=auth_headers_manager,
        )
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] is False

    async def test_delete_catalog_not_found(
        self,
        client: httpx.AsyncClient,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """存在しないカタログ削除"""
        non_existent_id = uuid4()

        response = await client.delete(
            f"/api/v1/catalogs/{non_existent_id}",
            headers=auth_headers_manager,
        )

        assert response.status_code == 404

    async def test_delete_catalog_forbidden(
        self,
        client: httpx.AsyncClient,
        db_session: AsyncSession,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """別組織のカタログ削除禁止"""
        other_org = Organization(name="Other Org", code="OTHER", is_active=True)
        db_session.add(other_org)
        await db_session.commit()
        await db_session.refresh(other_org)

        other_catalog = Catalog(
            organization_id=other_org.id,
            name="Other Catalog",
            category=CatalogCategory.DRONE,
            manufacturer="Test",
            model_number="TEST-001",
            is_active=True,
            version=1,
        )
        db_session.add(other_catalog)
        await db_session.commit()
        await db_session.refresh(other_catalog)

        response = await client.delete(
            f"/api/v1/catalogs/{other_catalog.id}",
            headers=auth_headers_manager,
        )

        assert response.status_code == 403
