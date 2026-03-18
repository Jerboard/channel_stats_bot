import typing as t

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, begin_connection


class ChannelMetricsSnapshot(Base):
    __tablename__ = "channel_metrics_snapshot"

    channel_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    subscribers: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    avg_reach: Mapped[float] = mapped_column(sa.Float, nullable=False, default=0, server_default="0")
    total_engagement: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    er: Mapped[float] = mapped_column(sa.Float, nullable=False, default=0, server_default="0")
    joins: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    leaves: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")

    @classmethod
    async def create(
        cls,
        channel_id: int,
        subscribers: int,
        avg_reach: float,
        total_engagement: int,
        er: float,
        joins: int,
        leaves: int,
    ) -> int:
        stmt = (
            psql.insert(cls)
            .values(
                channel_id=channel_id,
                subscribers=subscribers,
                avg_reach=avg_reach,
                total_engagement=total_engagement,
                er=er,
                joins=joins,
                leaves=leaves,
            )
            .returning(cls.id)
        )

        async with begin_connection() as conn:
            result = await conn.execute(stmt)
            await conn.commit()

        return result.scalar_one()