assert __name__ != "__main__"

# ---------------------------------- builtin --------------------------------- #
from typing import NoReturn, Dict
from enum import Enum
import logging
import sys 

# -------------------------------- third party ------------------------------- #
from colorama import Fore, Style



class LogLevel(Enum):
    NOTSET = 1
    DEBUG = 2
    INFO = 3
    WARN = 4
    ERROR = 5
    CRITICAL = 6


def _setup_logger():
    
    format = f"[%(color)s%(levelname)s{Style.RESET_ALL}](%(pathname)s:%(lineno)s): %(message)s"
    logging.basicConfig(level=logging.WARN, format=format, datefmt="%H:%M:%S")
    
def set_log_level(level: LogLevel):

    level_map: Dict[LogLevel, int] = {
        LogLevel.NOTSET: logging.NOTSET,
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARN: logging.WARN,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.CRITICAL: logging.CRITICAL
    }

    logging.getLogger().setLevel(level_map[level])


_setup_logger()

def debug(message: str):
    logging.debug(message, extra={"color": Fore.MAGENTA})

def info(message: str):
    logging.info(message, extra={"color": Fore.WHITE})

def warn(message: str):
    logging.warn(message, extra={"color": Fore.YELLOW})

def error(message: str):
    logging.error(message, extra={"color": Fore.RED})

def panic(message: str) -> NoReturn:
    logging.critical(message, extra={"color": Fore.RED})
    sys.exit(1)
