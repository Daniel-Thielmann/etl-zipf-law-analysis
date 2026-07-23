"""Carregamento de livros do Project Gutenberg."""
from __future__ import annotations

import io
import logging
from pathlib import Path

import pandas as pd
import requests

from src.utils.file_manager import ensure_dir
from src.utils.helpers import exponential_backoff

LOGGER = logging.getLogger(__name__)


def load_gutenberg_ids(
    csv_source: str, external_dir: Path | None = None
) -> list[int]:
    local_path = (
        external_dir / "gutenberg_ids.csv" if external_dir else Path(csv_source)
    )

    if local_path.exists():
        LOGGER.info("Carregando lista de IDs de %s", local_path)
        frame = pd.read_csv(local_path)
    else:
        LOGGER.info("Baixando lista de IDs de %s", csv_source)
        try:
            response = requests.get(csv_source, timeout=30)
            response.raise_for_status()
            content = response.text
            if external_dir:
                dest = ensure_dir(external_dir) / "gutenberg_ids.csv"
                dest.write_text(content, encoding="utf-8")
                LOGGER.info("Lista de IDs cacheada em %s", dest)
            frame = pd.read_csv(io.StringIO(content))
        except requests.RequestException as exc:
            LOGGER.error("Falha ao baixar CSV de IDs: %s", exc)
            raise RuntimeError(
                f"Não foi possível carregar a lista de IDs: {exc}"
            ) from exc

    if "book_id" not in frame.columns:
        raise ValueError("O CSV deve conter a coluna 'book_id'.")

    ids = frame["book_id"].dropna().astype(int).tolist()
    LOGGER.info("%d IDs de livros carregados.", len(ids))
    return ids


def download_gutenberg(
    book_id: int,
    max_retries: int = 5,
    timeout: tuple[float, float] = (10, 60),
) -> str | None:
    url = f"https://gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            exponential_backoff(attempt, error, f"Download livro {book_id}")

    LOGGER.error("Falha definitiva no download do livro %s", book_id)
    return None
