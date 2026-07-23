"""Configurações centralizadas do projeto."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Paths:
    data_dir: Path = Path("data")
    raw_dir: Path = data_dir / "raw"
    processed_dir: Path = data_dir / "processed"
    generated_dir: Path = data_dir / "generated"
    external_dir: Path = data_dir / "external"
    outputs_dir: Path = Path("outputs")
    figures_dir: Path = outputs_dir / "figures"
    tables_dir: Path = outputs_dir / "tables"
    reports_dir: Path = outputs_dir / "reports"
    logs_dir: Path = Path("logs")


@dataclass(frozen=True)
class GroqConfig:
    model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    temperature: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("GROQ_MAX_TOKENS", "1900"))
    target_words: int = int(os.getenv("TARGET_WORDS", "5000"))
    acceptable_difference: int = int(os.getenv("ACCEPTABLE_DIFFERENCE", "800"))

    @property
    def api_keys(self) -> list[str]:
        keys = [
            os.getenv("GROQ_API_KEY", "").strip(),
            os.getenv("GROQ_API_KEY_2", "").strip(),
        ]
        return [key for key in keys if key]


@dataclass(frozen=True)
class ExperimentConfig:
    max_books: int = int(os.getenv("MAX_BOOKS", "100"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "5"))
    ids_csv: str = os.getenv(
        "GUTENBERG_IDS_CSV",
        "https://drive.google.com/uc?export=download&id=1GKfNKm2z5BP6phQ3xwMXPSXsZmi9GpMa",
    )
    ids_csv_local: str = "data/external/gutenberg_ids.csv"
    request_timeout: tuple[float, float] = (10.0, 60.0)


@dataclass(frozen=True)
class Settings:
    paths: Paths = field(default_factory=Paths)
    groq: GroqConfig = field(default_factory=GroqConfig)
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)


settings = Settings()
