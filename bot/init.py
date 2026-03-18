from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.ext.asyncio import create_async_engine

from zoneinfo import ZoneInfo
import base64


from settings import conf

client = TelegramClient(conf.session_name, conf.api_id, conf.api_hash)

jobstores = {
    "default": SQLAlchemyJobStore(
        url="sqlite:///scheduler.db"
    )
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
)

ENGINE = create_async_engine(url=conf.db_url)
