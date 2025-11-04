"""
Logging extension for the application.
"""
import os
import time

import logging


LOCAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir_aux = LOCAL_DIR.split(os.sep)
project_dir_aux.pop()
PROJECT_DIR = os.sep.join(project_dir_aux)
log_dir = os.path.join(PROJECT_DIR, "logs")
log_file = os.path.join(log_dir, f"log_{time.strftime('%Y_%m_%d')}.log")


def get_basic_logger():
    """
    Set up and return a basic logger.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("basic_logger")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s [%(filename)s; %(funcName)s; %(lineno)d] => %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

basic_logger = get_basic_logger()
