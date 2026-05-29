from __future__ import annotations

import logging
from typing import Dict


_LOGGERS: Dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """
    Return a cached logger configured for this project.
    Keeps log output readable both in CLI and Streamlit contexts.
    """
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)

    logger.propagate = False
    _LOGGERS[name] = logger
    return logger

