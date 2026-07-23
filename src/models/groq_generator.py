"""Geração de texto artificial via API Groq."""
from __future__ import annotations

import logging
from pathlib import Path

from groq import Groq

from src.data.preprocessing import clean_text
from src.utils.file_manager import load_word_list, save_word_list
from src.utils.helpers import exponential_backoff

LOGGER = logging.getLogger(__name__)


def setup_client(api_key: str) -> Groq:
    if not api_key:
        raise ValueError("Chave da Groq não configurada.")
    return Groq(api_key=api_key)


def load_generated_words(filepath: Path) -> list[str] | None:
    return load_word_list(filepath)


def generate_artificial_text(
    client: Groq,
    book_id: int,
    human_words: list[str],
    generated_path: Path,
    reports_dir: Path,
    model: str = "llama-3.1-8b-instant",
    max_retries: int = 5,
    target_words: int = 5000,
    acceptable_difference: int = 800,
    temperature: float = 0.7,
    max_tokens: int = 1900,
) -> list[str] | None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    minimum_words = max(1, target_words - acceptable_difference)

    sample_start = " ".join(human_words[:50])
    midpoint = min(2500, max(0, len(human_words) // 2))
    sample_mid = " ".join(human_words[midpoint : midpoint + 50])

    current_prompt = (
        f"I am providing two excerpts from a classic literary work "
        f"as a stylistic anchor.\n\n"
        f"Excerpt 1 (Beginning):\n{sample_start}\n\n"
        f"Excerpt 2 (Middle):\n{sample_mid}\n\n"
        f"Write a seamless and original continuation. Mimic the tone "
        f"and era-appropriate language, use varied vocabulary, avoid "
        f"repetitive structures, and include rich descriptions and "
        f"character reflections. Produce a cohesive passage approaching "
        f"{target_words} words."
    )

    prompt_file = reports_dir / f"prompt_book_{book_id}.md"
    prompt_file.write_text("", encoding="utf-8")

    accumulated_words: list[str] = []

    while len(accumulated_words) < minimum_words:
        with prompt_file.open("a", encoding="utf-8") as f:
            f.write(current_prompt + "\n\n---\n\n")

        chunk_generated = False
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a skilled writer of classic "
                                "English literature. Use diverse vocabulary "
                                "and avoid repetitive phrasing."
                            ),
                        },
                        {"role": "user", "content": current_prompt},
                    ],
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                generated_text = response.choices[0].message.content or ""
                accumulated_words.extend(
                    clean_text(generated_text).split()
                )
                last_words = " ".join(accumulated_words[-30:])
                remaining = max(
                    0, target_words - len(accumulated_words)
                )
                current_prompt = (
                    f'Continue the narrative seamlessly from: '
                    f'"{last_words}".\n'
                    f"Maintain varied, sophisticated vocabulary; "
                    f"introduce new scenes or dialogue; avoid repetition. "
                    f"Produce approximately {remaining} additional words."
                )
                chunk_generated = True
                break
            except Exception as error:
                exponential_backoff(
                    attempt, error, f"Geração IA livro {book_id}"
                )

        if not chunk_generated:
            LOGGER.error("Falha definitiva na geração do livro %s", book_id)
            return None

    result = accumulated_words[:target_words]
    save_word_list(result, generated_path)
    return result
