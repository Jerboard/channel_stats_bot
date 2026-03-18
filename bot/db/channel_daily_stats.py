import typing as t
from datetime import datetime, timezone, timedelta

import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, begin_connection


class ChannelDailyStats(Base):
    __tablename__ = "channel_daily_stats"

    channel_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    joins_count: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    leaves_count: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    @classmethod
    async def create(
        cls,
        channel_id: int,
        joins_count: int,
        leaves_count: int,
    ) -> int:
        stmt = (
            psql.insert(cls)
            .values(
                channel_id=channel_id,
                joins_count=joins_count,
                leaves_count=leaves_count,
            )
            .returning(cls.id)
        )

        async with begin_connection() as conn:
            result = await conn.execute(stmt)
            await conn.commit()

        return result.scalar_one()

    @classmethod
    async def get_last_created_at_by_channel(cls, channel_id: int) -> datetime | None:
        stmt = sa.select(sa.func.max(cls.created_at)).where(cls.channel_id == channel_id)

        async with begin_connection() as conn:
            result = await conn.execute(stmt)

        return result.scalar_one_or_none()

    @classmethod
    async def get_last_24h_sum_by_channel(cls, channel_id: int) -> tuple[int, int]:
        dt_from = datetime.now() - timedelta(days=1)

        stmt = sa.select(
            sa.func.coalesce(sa.func.sum(cls.joins_count), 0),
            sa.func.coalesce(sa.func.sum(cls.leaves_count), 0),
        ).where(
            cls.channel_id == channel_id,
            cls.created_at >= dt_from,
        )

        async with begin_connection() as conn:
            result = await conn.execute(stmt)

        joins_count, leaves_count = result.one()
        return joins_count, leaves_count
