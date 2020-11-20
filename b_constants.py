import os
from dotenv import load_dotenv

import logs

log_level = logs.WARNING  # уровень логов для данного модуля
log = logs.Logger(log_name='b_constants', log_level=log_level)

try:
    load_dotenv()

    TELEGA_TOKEN = os.getenv('TELEGA_TOKEN')
    API_PATH = os.getenv('API_PATH')
    log.debug(
        f"Получены константы:\n"
        f"TELEGA_TOKEN={TELEGA_TOKEN}\n"
        f"API_PATH={API_PATH}\n"
    )
except Exception as e:
    log.error(f"Ошибка загрузки констант \n{str(e)}")
