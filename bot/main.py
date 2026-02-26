import asyncio
import logging

from handlers.channel_listener import client
from tasks import start_scheduler



log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def main():
    # await start_scheduler()
    await client.connect()
    await start_scheduler()

    print("Авторизован, запускаем обработчики…")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())

