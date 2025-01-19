import logging
import os
from pathlib import Path


def setup_logger(
    name: str,
    log_file: Path | str | None = None,
    level: int = logging.INFO,
    use_console: bool = True,
) -> logging.Logger:
    """Configure a logger with consistent formatting for file and/or console output"""
    # assert use_console is not False and log_file is None, "Must either use console or provide log file, or both."

    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # console handler
    if use_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # file handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
