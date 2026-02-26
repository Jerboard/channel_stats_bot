from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv(".env")

@dataclass()
class Config:

    def __post_init__(self):
        self.session_dir.mkdir(exist_ok=True)

    # debug = getenv('DEBUG') == '1'
    debug = getenv('DEBUG') == '0'
    if debug:
        api_id = getenv('STATS_API_ID_TEST')
        api_hash = getenv('STATS_API_HASH_TEST')

        phone = getenv('STATS_PHONE_TEST')
        session_name = getenv('STATS_SESSION_NAME_TEST')
        sheet_id = getenv('SHEET_ID_TEST')

        channel_1 = -1003888452085
        channel_2 = -1003888452085

    else:
        api_id = getenv('STATS_API_ID')
        api_hash = getenv('STATS_API_HASH')

        phone = getenv('STATS_PHONE')
        session_name = getenv('STATS_SESSION_NAME')

        sheet_id = getenv('SHEET_ID')

        channel_1 = -1001342572355
        channel_2 = -1001613808696

    sheet_name_1 = 'СтатТГбот'
    sheet_name_2 = 'СтатТГбот (посты)'

    session_dir = Path('sessions')
    session_path = session_dir / session_name

    subscribers_file = Path("subscribers.json")

    # redis_host = getenv('REDIS_HOST')
    # redis_port = int(getenv('REDIS_PORT'))


conf: Config = Config()



'''
Канал
Анисимова Анастасия ✨Formagiclife
@ForMagicLife_RU
id: -1001342572355

Канал
Центр трансформации и развития личности Анастасии Анисимовой
@neirografica_formagiclife
id: -1001613808696
'''
