"""SQLAlchemy Baseクラスと共通カラム定義"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# UUIDv7を主キーとして使用するための型定義
# PostgreSQL 18のuuidv7()関数を使用
uuid_pk = Annotated[
    UUID,
    mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),  # PostgreSQL 18 native UUIDv7 support
    ),
]

# タイムスタンプカラムの型定義
created_at_column = Annotated[
    datetime,
    mapped_column(
        server_default=func.now(),
        nullable=False,
    ),
]

updated_at_column = Annotated[
    datetime,
    mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
]


class Base(AsyncAttrs, DeclarativeBase):
    """全モデルの基底クラス

    AsyncAttrsを継承することで非同期コンテキストでの属性アクセスをサポート
    """

    pass


class TimestampMixin:
    """作成日時・更新日時を持つモデル用のMixin"""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
