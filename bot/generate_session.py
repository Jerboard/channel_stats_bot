import asyncio
import logging
import base64

from telethon import TelegramClient

from settings import conf

proxy = (
    "mtproto",
    "95.217.135.241",
    443,
    base64.b64decode("7pJZSUjIp-43RmluNUkNmWNkbnMuZ11vZ2xlLmNvbQ==")
)



async def main():
    async with TelegramClient(
            conf.session_name,
            conf.api_id,
            conf.api_hash,
            proxy=proxy
    ) as client:
        await client.start(phone=conf.phone)
        print("✅ Сессия создана")
        print(f"Файл: {conf.session_name}.session")


if __name__ == "__main__":
    logging.warning(f'{conf.api_id} {conf.api_hash} {conf.session_name} {conf.phone}')
    # logging.warning(f'{conf1.api_id} {conf1.api_hash} {conf1.session_name}')
    asyncio.run(main())
