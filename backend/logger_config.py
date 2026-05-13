import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), 'app_usage.log')

def setup_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = TimedRotatingFileHandler(
        LOG_PATH,
        when='H',
        interval=2,
        backupCount=1,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger