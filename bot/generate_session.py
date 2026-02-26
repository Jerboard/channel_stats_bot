import asyncio
import logging
import base64

from telethon import TelegramClient

from settings import conf


async def main():
    async with TelegramClient(
            conf.session_name,
            conf.api_id,
            conf.api_hash,
    ) as client:
        await client.start(phone=conf.phone)
        print("✅ Сессия создана")
        print(f"Файл: {conf.session_name}.session")


if __name__ == "__main__":
    logging.warning(f'{conf.api_id} {conf.api_hash} {conf.session_name} {conf.phone}')
    # logging.warning(f'{conf1.api_id} {conf1.api_hash} {conf1.session_name}')
    asyncio.run(main())
