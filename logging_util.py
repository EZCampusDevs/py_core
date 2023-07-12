import logging
import os
import sys

from . import constants

__loggers__: set[str] = set()


def create_setup_logger(name: str = None, log_file: str = "", log_level=logging.DEBUG):
    """Creates a logger adding a stdout hook and a file hook (if log_file is given) and sets its
    log level.

    Args:
        name:
        log_file:
        log_level:

    Notes:
        Each logger can only be setup once. Multiple calls to this with the same logger will only
        change the log level.
    """
    logger = logging.getLogger(name)

    logger.setLevel(log_level)

    if name in __loggers__:
        return logger

    __loggers__.add(name)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        except:
            pass
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.addHandler(stdout_handler)

    return logger


def setup_logging(log_file: str = "", log_level=logging.DEBUG):
    """Creates and setup loggers.

    Args:
        log_file: Set log_file for the LOGGER_INSTANCE and builtin python logger.
        log_level: Set log_level for the LOGGER_INSTANCE and builtin python logger.

    Notes:
        Once this function has set up the loggers, you can simply use the default logging module
        from anywhere.

    Examples:
        >>> import logging
        >>> logging.info("hello world")
        >>> logging.error("error")
    """
    create_setup_logger(log_file=log_file, log_level=log_level)
    create_setup_logger(constants.BRAND, log_file, log_level)


def add_unhandled_exception_hook(replace=False):
    """Add an unhandled exception hook which will log unhandled exceptions with the global logger.

    Args:
        replace: If True completely replace the builtin python unhandled exception hook instead of
            wrapping it.
    """
    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

        if not replace:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_unhandled_exception
