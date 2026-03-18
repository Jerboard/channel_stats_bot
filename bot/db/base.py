import typing as t
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from init import ENGINE
from settings import conf

METADATA = sa.MetaData ()


begin_connection = sessionmaker(bind=ENGINE, class_=AsyncSession, expire_on_commit=False)


# async def init_models():
#     async with ENGINE.begin () as conn:
#         await conn.run_sync (METADATA.create_all)


class Base(DeclarativeBase):
    metadata = METADATA

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=sa.func.now(), server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
        default=sa.func.now(),
        onupdate=sa.func.now()
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"

    @classmethod
    async def get_all(cls) -> t.Optional[list[t.Self]]:
        """Возвращает строку по id"""

        query = sa.select(cls).where(cls.is_active == True)

        async with begin_connection() as conn:
            result = await conn.execute(query)

        return result.scalars().all()
        # return result.all()

    @classmethod
    async def get_by_id(cls, entry_id: int) -> t.Optional[t.Self]:
        """Возвращает строку по id"""

        query = sa.select(cls).where(cls.id == entry_id)

        async with begin_connection() as conn:
            result = await conn.execute(query)

        return result.scalars().first()