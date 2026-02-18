from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from zoneinfo import ZoneInfo
import base64


from settings import conf


proxy = (
    "mtproto",
    "95.217.135.241",
    443,
    base64.b64decode("7pJZSUjIp-43RmluNUkNmWNkbnMuZ11vZ2xlLmNvbQ==")
)

client = TelegramClient(conf.session_name, conf.api_id, conf.api_hash, proxy=proxy)

jobstores = {
    "default": SQLAlchemyJobStore(
        url="sqlite:///scheduler.db"
    )
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
)
