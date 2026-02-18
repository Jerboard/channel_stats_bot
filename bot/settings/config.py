from os import getenv

from dotenv import load_dotenv


load_dotenv(".env")


class Config:
    debug = getenv('DEBUG') == '1'
    if debug:
        api_id = getenv('STATS_API_ID_TEST')
        api_hash = getenv('STATS_API_HASH_TEST')

        phone = getenv('STATS_PHONE_TEST')
        session_name = getenv('STATS_SESSION_NAME_TEST')
        sheet_id = getenv('SHEET_ID_TEST')

    else:
        api_id = getenv('STATS_API_ID_TEST')
        api_hash = getenv('STATS_API_HASH_TEST')

        phone = getenv('STATS_PHONE_TEST')
        session_name = getenv('STATS_SESSION_NAME_TEST')

    # redis_host = getenv('REDIS_HOST')
    # redis_port = int(getenv('REDIS_PORT'))


conf: Config = Config()