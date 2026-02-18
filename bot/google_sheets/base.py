import asyncio
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo

from settings import conf


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# def _get_worksheet(spreadsheet_name: str, worksheet_name: str):
#     creds = Credentials.from_service_account_file(
#         "cred.json",
#         scopes=SCOPES,
#     )
#     gc = gspread.authorize(creds)
#     sh = gc.open(spreadsheet_name)
#     return sh.worksheet(worksheet_name)


def _get_worksheet(spreadsheet_id: str):
    creds = Credentials.from_service_account_file(
        "cred.json",
        scopes=SCOPES,
    )
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(spreadsheet_id)
    return sh.sheet1


async def append_stats_row(
        channel_id: int,
        message_id: int,
        channel_name: int,
        message_text: int,
        views: int,
        reactions: dict,
        subscribers: int,
        msg_type: str,

    ):
    """
    Асинхронно добавляет строку в таблицу.
    """

    def _write():
        ws = _get_worksheet(conf.sheet_id)

        # Получаем все значения первой колонки
        col = ws.col_values(1)

        reactions_str = ", ".join(
            f"{k}:{v}" for k, v in reactions.items()
        )
        if not reactions_str:
            reactions_str = '-'

        # 📅 Московское время
        moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
        formatted_time = moscow_time.strftime("%Y-%m-%d %H:%M:%S")

        ws.append_row(
            values=[formatted_time, channel_name, msg_type, message_text, views, reactions_str, subscribers],
            table_range="A1",
        )

    await asyncio.to_thread(_write)
