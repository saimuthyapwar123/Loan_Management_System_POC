import logging
import os

LOG_DIR = "data/log_data"
LOG_FILE = os.path.join(LOG_DIR, "data_log.log")

def get_logger(name):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('[%(asctime)s]  [%(levelname)s] ["Line_no" : %(lineno)d] [%(funcName)s()] [%(message)s]')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger

    