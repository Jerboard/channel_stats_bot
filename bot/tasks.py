import logging

from telethon.tl.functions.channels import GetFullChannelRequest
from datetime import datetime, timedelta

from init import scheduler, client
from google_sheets import append_stats_row


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
    msg = await client.get_messages(chat_id, ids=message_id)

    if not msg:
        logging.warning("Сообщение не найдено")
        return

    text = (msg.text or "-")[:30]
    views = msg.views or 0
    subscribers = await get_count_subscribers(chat_id)
    msg_type = str(type(msg.media))[33:-2] if msg.media else 'text'

    reactions_info = {}
    if msg.reactions:
        for r in msg.reactions.results:
            reactions_info[r.reaction.emoticon] = r.count

    await append_stats_row(
        channel_id=chat_id,
        message_id=message_id,
        channel_name=msg.chat.title,
        message_text=text,
        views=views,
        reactions=reactions_info,
        subscribers=subscribers,
        msg_type=msg_type
    )

    # logging.warning(f"\n⏳ Обновлённая статистика {chat_id} {message_id}:")
    # logging.warning(f"Текст: {text}")
    # logging.warning(f"Просмотры: {views}")
    # logging.warning(f"Реакции: {reactions_info}")
    # logging.warning(f"Подписчики: {subscribers}")
    # logging.warning(f"------")


def schedule_message_check(chat_id: int, message_id: int, delay_minutes: int = 1):
    scheduler.add_job(
        check_message,
        trigger="date",
        args=[chat_id, message_id],
        # run_date=datetime.now() + timedelta(minutes=delay_minutes),
        run_date=datetime.now() + timedelta(days=1),
        id=f"msg_{chat_id}_{message_id}",
        replace_existing=True,
    )
