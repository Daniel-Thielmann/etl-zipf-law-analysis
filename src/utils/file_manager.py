"""Operações de arquivo do projeto."""
from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_text(text: str, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(text, encoding="utf-8")


def load_text(filepath: Path) -> str | None:
    if not filepath.exists():
        return None
    return filepath.read_text(encoding="utf-8")


def save_word_list(words: list[str], filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text("\n".join(words), encoding="utf-8")


def load_word_list(filepath: Path) -> list[str] | None:
    if not filepath.exists():
        return None
    text = filepath.read_text(encoding="utf-8").strip()
    return text.split("\n") if text else []
