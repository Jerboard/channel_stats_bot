import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, begin_connection


class ChannelMessageStats(Base):
    __tablename__ = "channel_message_stats"

    channel_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    message_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    channel_title: Mapped[str] = mapped_column(sa.String, nullable=True)
    message_type: Mapped[str] = mapped_column(sa.String(50), nullable=True, default="text", server_default="text")
    message_text: Mapped[str] = mapped_column(sa.String, nullable=True, default="-", server_default="-")
    views: Mapped[int] = mapped_column(sa.Integer, nullable=True, default=0, server_default="0")
    reactions: Mapped[str] = mapped_column(sa.String, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint("channel_id", "message_id", name="uq_channel_message_stats_channel_message"),
    )

    @classmethod
    async def add_or_update(
        cls,
        channel_id: int,
        message_id: int,
        channel_title: str | None,
        message_type: str,
        message_text: str,
        views: int,
        reactions: str | None,
    ) -> int:
        stmt = (
            psql.insert(cls)
            .values(
                channel_id=channel_id,
                message_id=message_id,
                channel_title=channel_title,
                message_type=message_type,
                message_text=message_text,
                views=views,
                reactions=reactions,
            )
            .on_conflict_do_update(
                index_elements=[cls.channel_id, cls.message_id],
                set_={
                    "channel_title": channel_title,
                    "message_type": message_type,
                    "message_text": message_text,
                    "views": views,
                    "reactions": reactions,
                }
            )
            .returning(cls.id)
        )

        async with begin_connection() as conn:
            result = await conn.execute(stmt)
            await conn.commit()

        return result.scalar_one()