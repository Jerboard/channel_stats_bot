import logging
import json

from telethon.tl.functions.channels import GetFullChannelRequest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from init import scheduler, client
from settings import conf
from google_sheets import append_stats_row

logger = logging.getLogger(__name__)


async def start_scheduler():
    # await collect_channels_summary()
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



async def get_count_subscribers(chat_id: int) -> int:
    try:
        entity = await client.get_entity(chat_id)
        full = await client(GetFullChannelRequest(entity))
        subscribers = full.full_chat.participants_count or 0
    except Exception as e:
        logging.warning(f"Не удалось получить подписчиков: {e}")
        subscribers = 0

    return subscribers


async def check_message(chat_id: int, message_id: int):
    # logging.warning(f"check_message {chat_id} {message_id}")
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


def schedule_message_check(chat_id: int, message_id: int, delay_minutes: int = 1):
    # logging.warning("schedule_message_check")
    scheduler.add_job(
        check_message,
        trigger="date",
        args=[chat_id, message_id],
        # run_date=datetime.now() + timedelta(seconds=10),
        run_date=datetime.now() + timedelta(days=1),
        id=f"msg_{chat_id}_{message_id}",
        replace_existing=True,
    )


async def collect_channels_summary() -> None:
    """
    Возвращает строку для записи в таблицу.
    Также обновляет subscribers.json
    """
    logging.warning("collect_channels_summary")
    channel_ids = [conf.channel_1, conf.channel_2]

    # --- Время по Москве ---
    moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
    formatted_time = moscow_time.strftime("%d.%m.%Y %H:%M")

    # --- Читаем предыдущие значения ---
    if conf.subscribers_file.exists():
        with open(conf.subscribers_file, "r", encoding="utf-8") as f:
            previous_data = json.load(f)
    else:
        previous_data = {}

    logger.warning(f'previous_data: {conf.subscribers_file.exists()} {previous_data}')
    updated_data = {}
    result_row = [formatted_time]

    since = datetime.now(timezone.utc) - timedelta(days=1)

    await client.get_dialogs()

    for chat_id in channel_ids:
        logging.warning(f'cccc {chat_id}')
        try:
            previous_subscribers = previous_data.get(str(chat_id), 0)

            logging.warning(f'previous_subscribers {previous_subscribers}')

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
            delta = subscribers - previous_subscribers
            subscriptions = delta if delta > 0 else 0
            unsubscriptions = abs(delta) if delta < 0 else 0

            # Добавляем данные в строку
            result_row.extend([
                subscribers,
                round(avg_reach, 2),
                total_engagement,
                round(er, 4),
                subscriptions,
                unsubscriptions,
            ])

            # Сохраняем новое значение
            updated_data[chat_id] = subscribers

        except Exception as e:
            result_row.extend(['-', '-', '-', '-', '-', '-'])


    # --- Обновляем json ---
    with open(conf.subscribers_file, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=2)

    await append_stats_row(row=result_row, worksheet_title=conf.sheet_name_1, table_range='A4')