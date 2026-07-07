"""
logger.py

Creates log file for ETL pipeline.
"""

import logging

from scripts.utils.config import LOG_FILE

LOG_FILE.parent.mkdir(
    exist_ok=True,
    parents=True
)

logging.basicConfig(

    filename=LOG_FILE,

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    filemode="a"

)


class Logger:

    @staticmethod
    def info(message):

        print(message)

        logging.info(message)

    @staticmethod
    def warning(message):

        print(message)

        logging.warning(message)

    @staticmethod
    def error(message):

        print(message)

        logging.error(message)