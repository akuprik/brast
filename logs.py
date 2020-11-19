"""
Логирование
"""
import logging
import logging.handlers

import sys
import os

# эти параметры можно изменить при создании логера
LOG_PATH = './logs'
LOG_FILE = os.path.split(
    os.path.abspath(sys.modules['__main__'].__file__)
    )[1].replace('.py', '')+'.log'

# параметры для всего проекта
BACKUP_COUNT = 10
UTC = False
DELAY = True

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR


class Logger:
    """
    Логер для каждого модуля:
        -ротация фалов по дате в полночь
        -формат дата время:уровень:логер:сообщение
        -log_level по умолчанию WARNING
        -log_name желательно указать назавние модуля иначе COMMON
        -При создании логера проверяет наличие папки логов,
            создает если нет такой
    """
    def __init__(self, log_path=LOG_PATH,  log_file=LOG_FILE,
                 log_name='COMMON', log_level=WARNING):

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        file_name = f'{log_path}/{log_file}'.replace('//', '/')
        self.logger = logging.getLogger(log_name.upper())
        self.logger.setLevel(log_level)
        self.file_handler = logging.handlers.TimedRotatingFileHandler(
            file_name, when='midnight', interval=1,
            backupCount=BACKUP_COUNT, utc=UTC, delay=DELAY
            )
        self.file_handler.setFormatter(
            logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
            )
        self.logger.addHandler(self.file_handler)
        self.logger.debug(f"Создан логер {log_name}")

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

