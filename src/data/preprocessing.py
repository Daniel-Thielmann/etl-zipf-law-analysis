"""Pré-processamento e limpeza de textos."""
from __future__ import annotations

import re


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_gutenberg_header(text: str) -> str:
    start_match = re.search(
        r"\*\*\* START OF THE PROJECT GUTENBERG.*?\*\*\*",
        text,
        re.IGNORECASE,
    )
    end_match = re.search(
        r"\*\*\* END OF THE PROJECT GUTENBERG.*?\*\*\*",
        text,
        re.IGNORECASE,
    )
    if start_match and end_match and start_match.end() < end_match.start():
        text = text[start_match.end() : end_match.start()]
    return text


def extract_n_words(text: str, n: int = 5000) -> list[str] | None:
    words = text.split()
    return words[:n] if len(words) >= n else None


def preprocess_gutenberg(raw_text: str, target_words: int) -> list[str] | None:
    cleaned = strip_gutenberg_header(raw_text)
    cleaned = clean_text(cleaned)
    return extract_n_words(cleaned, target_words)
