"""Funções utilitárias auxiliares."""
from __future__ import annotations

import logging
import time

LOGGER = logging.getLogger(__name__)


def exponential_backoff(attempt: int, error: Exception, context: str) -> None:
    wait_time = 2**attempt
    LOGGER.warning(
        "%s | Tentativa %d falhou: %s. Nova tentativa em %d s.",
        context,
        attempt + 1,
        error,
        wait_time,
    )
    time.sleep(wait_time)
