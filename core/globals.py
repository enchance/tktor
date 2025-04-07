import os
import logging, arrow
from logging.handlers import RotatingFileHandler
from fastapi.logger import logger
from icecream import IceCreamDebugger
# from pythonjsonlogger import jsonlogger
from pythonjsonlogger.json import JsonFormatter
from dotenv import load_dotenv

from core import Envs


load_dotenv()
ic = IceCreamDebugger(prefix='')
try:
    env = Envs(os.getenv('ENV'))
except Exception as e:
    env = Envs.production
if env == Envs.production:
    ic.disable()

now = arrow.utcnow().datetime
# formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(funcName)s:%(lineno)d - %(message)s')
# formatter = logging.Formatter('{"datetime": "%(asctime)s", "level": "%(levelname)s", "filename": "%(filename)s", "lineno": %(lineno)d, "message": "%(message)s}"')
formatter = JsonFormatter("{asctime}{levelname}{filename}{lineno}{funcName}{message}{exc_info}", style="{")
maxBytes = 1024 * 1024 * 2  # 2MB

warning_handler = RotatingFileHandler(f'logs/{now:%Y-%m} warning.log', maxBytes=maxBytes, backupCount=10)
warning_handler.setFormatter(formatter)
warning_handler.setLevel(logging.WARNING)
logger.addHandler(warning_handler)

error_handler = RotatingFileHandler(f'logs/{now:%Y-%m} error.log', maxBytes=maxBytes, backupCount=10)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)
logger.addHandler(error_handler)

critical_handler = RotatingFileHandler(f'logs/{now:%Y-%m} critical.log', maxBytes=maxBytes, backupCount=10)
critical_handler.setFormatter(formatter)
critical_handler.setLevel(logging.CRITICAL)
logger.addHandler(critical_handler)
