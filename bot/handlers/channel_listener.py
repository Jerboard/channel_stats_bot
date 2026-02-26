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
    # logging.warning(f'message {event.chat.title} {event.chat.id} {message.id}')

    schedule_message_check(
        chat_id=event.chat_id,
        message_id=message.id,
        delay_minutes=1,
    )

