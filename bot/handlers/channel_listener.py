import logging

from telethon import events
from telethon.types import Message

from init import client
from tasks import schedule_message_check

@client.on(events.NewMessage)
async def channel_message_handler(event):
    if not event.is_channel:
        return

    message = event.message
    logging.warning(f'message {event.chat_id} {message.id}: ')

    schedule_message_check(
        chat_id=event.chat_id,
        message_id=message.id,
        delay_minutes=1,
    )

    # text = (message.text or "")[:30]
    # views = message.views or 0
    #
    # reactions_info = {}
    # if message.reactions:
    #     for r in message.reactions.results:
    #         reactions_info[r.reaction.emoticon] = r.count

    # logging.warning("\n---")
    # logging.warning(f"Текст: {text}")
    # logging.warning(f"Просмотры: {views}")
    # logging.warning(f"Реакции: {reactions_info}")
