"""Pipeline principal de orquestração do experimento."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.config import Settings
from src.data.loader import download_gutenberg, load_gutenberg_ids
from src.data.preprocessing import preprocess_gutenberg
from src.models.groq_generator import (
    generate_artificial_text,
    load_generated_words,
    setup_client,
)
from src.analysis.zipf import compute_zipf_alpha
from src.analysis.statistics import (
    compute_descriptive_statistics,
    compute_ks_test,
)
from src.visualization.plots import create_all_plots
from src.utils.file_manager import ensure_dir, save_text

LOGGER = logging.getLogger(__name__)


def _read_existing_results(results_path: Path) -> pd.DataFrame:
    if results_path.exists():
        return pd.read_csv(results_path)
    return pd.DataFrame()


def _get_processed_ids(results_path: Path) -> set[int]:
    df = _read_existing_results(results_path)
    if df.empty or "book_id" not in df.columns:
        return set()
    return set(df["book_id"].astype(int).tolist())


def run_pipeline(settings: Settings) -> pd.DataFrame:
    paths = settings.paths
    groq = settings.groq
    exp = settings.experiment

    for dir_path in [
        paths.raw_dir, paths.processed_dir, paths.generated_dir,
        paths.outputs_dir, paths.figures_dir, paths.tables_dir,
        paths.reports_dir, paths.logs_dir,
    ]:
        ensure_dir(dir_path)

    api_keys = groq.api_keys
    if not api_keys:
        raise RuntimeError("Defina GROQ_API_KEY no arquivo .env antes de executar.")

    book_ids = load_gutenberg_ids(exp.ids_csv, paths.external_dir)
    results_path = paths.outputs_dir / "zipf_results.csv"
    processed_ids = _get_processed_ids(results_path)

    LOGGER.info(
        "Pipeline iniciado — %d livros disponíveis, %d já processados",
        len(book_ids),
        len(processed_ids),
    )

    key_index = 0
    client = setup_client(api_keys[key_index])
    results = _read_existing_results(results_path)
    sample: dict = {}

    for book_id in book_ids:
        if book_id in processed_ids:
            LOGGER.info("Livro %s já processado. Pulando.", book_id)
            continue

        if len(results) >= exp.max_books:
            LOGGER.info("Limite de %d livros atingido.", exp.max_books)
            break

        LOGGER.info("Livro %d iniciado", book_id)

        raw_text = download_gutenberg(
            book_id, exp.max_retries, exp.request_timeout
        )
        if raw_text is None:
            LOGGER.error("Livro %s: falha no download. Pulando.", book_id)
            continue

        raw_path = paths.raw_dir / f"{book_id}.txt"
        save_text(raw_text, raw_path)
        LOGGER.info("Livro %s: texto bruto salvo em %s", book_id, raw_path)

        human_words = preprocess_gutenberg(raw_text, groq.target_words)
        if human_words is None:
            LOGGER.warning(
                "Livro %s descartado: texto insuficiente.", book_id
            )
            continue

        processed_path = paths.processed_dir / f"{book_id}.txt"
        save_text(" ".join(human_words), processed_path)
        LOGGER.info(
            "Livro %s: texto processado salvo em %s", book_id, processed_path
        )

        human_fit = compute_zipf_alpha(human_words)
        if human_fit is None:
            LOGGER.warning(
                "Livro %s: não foi possível calcular Zipf no texto humano.",
                book_id,
            )
            continue
        alpha_cn, r2_cn, ranks_cn, freqs_cn = human_fit

        generated_path = paths.generated_dir / f"{book_id}.txt"
        artificial_words = load_generated_words(generated_path)

        if artificial_words is not None:
            LOGGER.info(
                "Livro %s: texto IA carregado do cache", book_id
            )
        else:
            LOGGER.info("Livro %s: gerando texto artificial...", book_id)
            artificial_words = generate_artificial_text(
                client=client,
                book_id=book_id,
                human_words=human_words,
                generated_path=generated_path,
                reports_dir=paths.reports_dir,
                model=groq.model,
                max_retries=exp.max_retries,
                target_words=groq.target_words,
                acceptable_difference=groq.acceptable_difference,
                temperature=groq.temperature,
                max_tokens=groq.max_tokens,
            )

            while artificial_words is None and key_index + 1 < len(api_keys):
                key_index += 1
                LOGGER.warning(
                    "Alternando para a chave Groq %d.", key_index + 1
                )
                client = setup_client(api_keys[key_index])
                artificial_words = generate_artificial_text(
                    client=client,
                    book_id=book_id,
                    human_words=human_words,
                    generated_path=generated_path,
                    reports_dir=paths.reports_dir,
                    model=groq.model,
                    max_retries=exp.max_retries,
                    target_words=groq.target_words,
                    acceptable_difference=groq.acceptable_difference,
                    temperature=groq.temperature,
                    max_tokens=groq.max_tokens,
                )

            if artificial_words is not None:
                LOGGER.info(
                    "Livro %s: texto artificial salvo em %s",
                    book_id, generated_path,
                )

        if artificial_words is None:
            LOGGER.error(
                "Livro %s descartado por falha na geração artificial.",
                book_id,
            )
            continue

        artificial_fit = compute_zipf_alpha(artificial_words)
        if artificial_fit is None:
            LOGGER.warning(
                "Livro %s: não foi possível calcular Zipf no texto IA.",
                book_id,
            )
            continue
        alpha_ca, r2_ca, ranks_ca, freqs_ca = artificial_fit

        row = pd.DataFrame([{
            "book_id": book_id,
            "alpha_cn": alpha_cn,
            "alpha_ca": alpha_ca,
            "r2_cn": r2_cn,
            "r2_ca": r2_ca,
        }])
        row.to_csv(
            results_path, mode="a",
            header=not results_path.exists(), index=False,
        )
        results = pd.concat([results, row], ignore_index=True)
        LOGGER.info(
            "Livro %s: α_cn=%.4f, α_ca=%.4f — resultado salvo",
            book_id, alpha_cn, alpha_ca,
        )

        if not sample:
            sample = {
                "book_id": book_id,
                "r_cn": ranks_cn,
                "f_cn": freqs_cn,
                "a_cn": alpha_cn,
                "r_ca": ranks_ca,
                "f_ca": freqs_ca,
                "a_ca": alpha_ca,
            }
            create_all_plots(results, sample, paths.figures_dir)
            LOGGER.info(
                "Livro %s: gráfico salvo em %s", book_id, paths.figures_dir
            )

        processed_ids.add(book_id)

    if results.empty:
        raise RuntimeError("Nenhum livro foi processado com sucesso.")

    desc_stats = compute_descriptive_statistics(results)
    desc_path = paths.tables_dir / "descriptive_statistics.csv"
    desc_stats.to_csv(desc_path)
    LOGGER.info("Estatísticas descritivas salvas em %s", desc_path)

    ks_result = compute_ks_test(results)
    ks_path = paths.tables_dir / "ks_test.csv"
    ks_result.to_csv(ks_path, index=False)
    LOGGER.info("Teste KS salvo em %s", ks_path)

    create_all_plots(results, sample, paths.figures_dir)
    LOGGER.info("Gráficos finais salvos em %s", paths.figures_dir)

    LOGGER.info(
        "Pipeline concluído — %d livros processados.", len(results)
    )
    return results
