import logging
import typing as t


def init_logger(level: int = logging.INFO) -> logging.StreamHandler[t.TextIO]:
    FMT = "({asctime}) [{levelname:^7}] {name}: {message}"
    FORMATS = {
        logging.DEBUG: FMT,
        logging.INFO: f"\33[34m{FMT}\33[0m",
        logging.WARNING: f"\33[33m{FMT}\33[0m",
        logging.ERROR: f"\33[31m{FMT}\33[0m",
        logging.CRITICAL: f"\33[31m;1m{FMT}\33[0m",
    }

    class CustomFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_fmt = FORMATS[record.levelno]
            formatter = logging.Formatter(log_fmt, style="{", datefmt="%Y-%m-%d %H:%M:%S")
            return formatter.format(record)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(level=level, handlers=[handler])
    return handler
