# Copyright (C) 2022-2023 EZCampus 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import sys

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse

from . import constants

__loggers__: set[str] = set()

LOG_LEVEL_MAP = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARN: "WARN",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
}


def get_level_map_pretty():
    return ", ".join(f"{value}={key}" for key, value in LOG_LEVEL_MAP.items())


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

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

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
        replace: If True replace the builtin python unhandled exception hook instead of wrapping it.
    """

    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        if not replace:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_unhandled_exception


def log_endpoint(h: HTTPException | FileResponse, r: Request, msg: str = ""):
    """Log general endpoint."""
    logging.info(f"{r.method} {r.scope['path']} {h.status_code} {msg}")
