import logging
import json

from telethon import functions, types
from telethon.tl.functions.channels import GetFullChannelRequest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from init import scheduler, client
from settings import conf
from google_sheets import append_stats_row
from db import ChannelDailyStats, ChannelMessageStats, ChannelMetricsSnapshot

logger = logging.getLogger(__name__)


async def start_scheduler():
    pass
    # await collect_channels_summary()
    # await save_channel_delta()

    scheduler.add_job(
        save_channel_delta,
        trigger="cron",
        minute="*/10",
        id="save_channel_delta",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        collect_channels_summary,
        trigger="cron",
        hour=21,
        minute=0,
        id="collect_channels_summary",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    scheduler.start()


async def check_message(chat_id: int, message_id: int):
    logging.warning(f"check_message {chat_id} {message_id}")
    msg = await client.get_messages(chat_id, ids=message_id)

    if not msg:
        logging.warning("Сообщение не найдено")
        return

    text = (msg.text or "-")[:30]
    views = msg.views or 0
    # subscribers = await get_count_subscribers(chat_id)
    msg_type = str(type(msg.media))[33:-2] if msg.media else 'text'

    reactions_info = {}
    if msg.reactions:
        for r in msg.reactions.results:
            reactions_info[r.reaction.emoticon] = r.count

    reactions_str = ", ".join(
        f"{k}:{v}" for k, v in reactions_info.items()
    )

    # 📅 Московское время
    moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
    formatted_time = moscow_time.strftime("%Y-%m-%d %H:%M:%S")

    row = [formatted_time, msg.chat.title, msg_type, text, views, reactions_str]
    await append_stats_row(row=row, worksheet_title=conf.sheet_name_2, table_range='A2')

    await ChannelMessageStats.add_or_update(
        channel_id=chat_id,
        message_id=message_id,
        channel_title=getattr(msg.chat, "title", None),
        message_type=msg_type,
        message_text=text,
        views=views,
        reactions=reactions_str or None,
    )
    logger.warning(f'cfdt')


def schedule_message_check(chat_id: int, message_id: int):
    logging.warning("schedule_message_check")
    scheduler.add_job(
        check_message,
        trigger="date",
        args=[chat_id, message_id],
        run_date=datetime.now() + timedelta(seconds=10),
        # run_date=datetime.now() + timedelta(days=1),
        id=f"msg_{chat_id}_{message_id}",
        replace_existing=True,
    )


async def collect_channels_summary() -> None:
    """
    Возвращает строку для записи в таблицу.
    Также обновляет subscribers.json
    """
    logging.warning("collect_channels_summary")
    # channel_ids = [conf.channel_1, conf.channel_2]

    # --- Время по Москве ---
    moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
    formatted_time = moscow_time.strftime("%d.%m.%Y %H:%M")

    result_row = [formatted_time]

    since = datetime.now(timezone.utc) - timedelta(days=1)

    await client.get_dialogs()

    for chat_id in conf.channel_ids:
        logging.warning(f'cccc {chat_id}')
        try:
            # previous_subscribers = previous_data.get(str(chat_id), 0)

            # logging.warning(f'previous_subscribers {previous_subscribers}')

            # --- Подписчики сейчас ---
            entity = await client.get_entity(chat_id)
            # entity = await client.get_entity('tuschkan_test_channal_1')
            full = await client(GetFullChannelRequest(entity))
            subscribers = full.full_chat.participants_count or 0

            # --- Сообщения за 24 часа ---
            messages = await client.get_messages(chat_id, limit=200)

            posts = [
                m for m in messages
                if m.date >= since and m.post
            ]

            # Средний охват (средние просмотры)
            if posts:
                avg_reach = sum(m.views or 0 for m in posts) / len(posts)
            else:
                avg_reach = 0

            # Взаимодействия
            total_reactions = 0
            total_comments = 0

            for m in posts:
                if m.reactions:
                    total_reactions += sum(r.count for r in m.reactions.results)
                if m.replies:
                    total_comments += m.replies.replies or 0

            total_engagement = total_reactions + total_comments

            # ER
            er = (total_engagement / subscribers) if subscribers else 0

            # Подписки / отписки
            joins, leaves = await ChannelDailyStats.get_last_24h_sum_by_channel(channel_id=chat_id)

            # Добавляем данные в строку
            result_row.extend([
                subscribers,
                round(avg_reach, 2),
                total_engagement,
                round(er, 4),
                joins,
                leaves,
            ])

            await ChannelMetricsSnapshot.create(
                channel_id=chat_id,
                subscribers=subscribers,
                avg_reach=round(avg_reach, 2),
                total_engagement=total_engagement,
                er=round(er, 4),
                joins=joins,
                leaves=leaves,
            )

        except Exception as e:
            result_row.extend(['-', '-', '-', '-', '-', '-'])

    await append_stats_row(row=result_row, worksheet_title=conf.sheet_name_1, table_range='A4')


async def get_count_joins_leaves_last(channel_id: int):
    channel = await client.get_entity(channel_id)

    since = await ChannelDailyStats.get_last_created_at_by_channel(channel_id)
    if not since:
        since = datetime.now(timezone.utc) - timedelta(minutes=10)

    result = await client(functions.channels.GetAdminLogRequest(
        channel=channel,
        q='',
        events_filter=types.ChannelAdminLogEventsFilter(
            join=True,
            leave=True,
        ),
        admins=[],
        max_id=0,
        min_id=0,
        limit=100,
    ))

    joins = 0
    leaves = 0

    for event in result.events:
        # logger.warning(f'event.date: {event.date < since} {event.date}')
        if event.date < since:
            break

        action = event.action
        # logger.warning(f'event.date: {event.id}')

        if isinstance(action, types.ChannelAdminLogEventActionParticipantJoin):
            joins += 1
        elif isinstance(action, types.ChannelAdminLogEventActionParticipantLeave):
            leaves += 1

    await ChannelDailyStats.create(
        channel_id=channel_id,
        joins_count=joins,
        leaves_count=leaves,
    )

    result = {
        "joins_24h": joins,
        "leaves_24h": leaves,
    }
    logger.warning(f'result: {result}')


async def save_channel_delta():
    for channel_id in conf.channel_ids:
        await get_count_joins_leaves_last(channel_id)
