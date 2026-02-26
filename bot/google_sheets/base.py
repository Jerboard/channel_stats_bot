import asyncio
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo

from settings import conf


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_worksheet(worksheet_title: str = None):
    creds = Credentials.from_service_account_file(
        "cred.json",
        scopes=SCOPES,
    )
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(conf.sheet_id)
    if worksheet_title:
        return sh.worksheet(worksheet_title)

    return sh.sheet1


async def append_stats_row(
        row: list,
        table_range: str = 'A1',
        worksheet_title: str = None,
    ):
    """
    Асинхронно добавляет строку в таблицу.
    """

    def _write():
        ws = _get_worksheet(worksheet_title=worksheet_title)

        ws.append_row(
            values=row,
            table_range=table_range,
        )

    await asyncio.to_thread(_write)
