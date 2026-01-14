import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional

LOG_ROOT = os.getenv("LOG_DIR", "logs")

MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 10
DEFAULT_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

STATUS = "status"
ERROR = "error"
_OS_LOG_FILE_CONSTANT = "LOG_FILE"


class SizedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Rotates logs based on time OR file size.
    """

    def __init__(
        self,
        filename: str,
        max_bytes: int = MAX_BYTES,
        backup_count: int = BACKUP_COUNT,
        when: str = "midnight",
        utc: bool = True,
    ):
        super().__init__(
            filename=filename,
            when=when,
            backupCount=backup_count,
            utc=utc,
        )
        self.maxBytes = max_bytes

    def shouldRollover(self, record):
        if self.stream is None:
            self.stream = self._open()

        if self.maxBytes > 0:
            msg = f"{self.format(record)}\n"
            self.stream.seek(0, os.SEEK_END)
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return True

        current_time = int(time.time())
        if current_time >= self.rolloverAt:
            return True

        return False


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def initialize_logger(
    name: str,
    level: int = logging.INFO,
    log_type: str = STATUS,
    subfolder: Optional[str] = None,
) -> logging.Logger:
    """
    Initialize a logger with:
    - File handler (rotating)
    - Console handler
    """

    logger_name = f"{name}.{log_type}"
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger  # already initialized

    logger.setLevel(level)
    logger.propagate = False

    folder = os.path.join(LOG_ROOT, name)
    if subfolder:
        folder = os.path.join(folder, subfolder)

    _ensure_dir(folder)

    filename = f"{name}-error.log" if log_type == ERROR else f"{name}.log"
    logfile = os.path.join(folder, filename)

    formatter = logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT)

    # File handler
    file_handler = SizedTimedRotatingFileHandler(logfile)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


class Logging:
    """
    Unified logging interface:
    - status logger
    - error logger
    """

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        subfolder: Optional[str] = None,
        initialize: bool = True,
    ):
        self.name = name

        if initialize:
            initialize_logger(
                name=name,
                level=level,
                log_type=STATUS,
                subfolder=subfolder,
            )
            initialize_logger(
                name=name,
                level=level,
                log_type=ERROR,
                subfolder=subfolder,
            )

        self.status = logging.getLogger(f"{name}.{STATUS}")
        self.error = logging.getLogger(f"{name}.{ERROR}")

    def info(self, msg: str):
        self.status.info(msg)

    def debug(self, msg: str):
        self.status.debug(msg)

    def warning(self, msg: str):
        self.status.warning(msg)
        self.error.warning(msg)

    def error(self, msg: str):
        self.status.error(msg)
        self.error.error(msg)

    def exception(self, msg: str):
        self.status.exception(msg)
        self.error.exception(msg)
