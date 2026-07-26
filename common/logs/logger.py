"""
logger.py

Shared logging utility for all project layers.
"""

import logging
from pathlib import Path


def setup_logger(
    log_file: str | Path,
    level: str = "INFO"
) -> logging.Logger:
    """
    Configure and return a logger.

    Parameters
    ----------
    log_file : str | Path
        Path to the log file.

    level : str, default="INFO"
        Logging level.

    Returns
    -------
    logging.Logger
    """

    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(log_file.stem)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(getattr(logging, level.upper()))

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger