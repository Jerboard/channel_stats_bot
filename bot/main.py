import asyncio
import logging

from init import scheduler
from handlers.channel_listener import client


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def main():
    scheduler.start()
    await client.start()
    await client.connect()
    print("Авторизован, запускаем обработчики…")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())

