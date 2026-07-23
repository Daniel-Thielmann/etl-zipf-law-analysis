"""Ponto de entrada do projeto."""
from __future__ import annotations

from src.config import settings
from src.utils.logger import setup_logger
from src.pipelines.pipeline import run_pipeline


def main() -> None:
    logger = setup_logger(settings.paths.logs_dir)
    logger.info("=" * 60)
    logger.info("Iniciando experimento Zipf: humano vs. IA")
    logger.info("=" * 60)

    try:
        results = run_pipeline(settings)
        logger.info(
            "Concluído: %d livros processados.", len(results)
        )
        logger.info(
            "Resultados salvos em: %s",
            settings.paths.outputs_dir.resolve(),
        )
    except Exception as exc:
        logger.exception("Pipeline interrompido por erro: %s", exc)
        raise


if __name__ == "__main__":
    main()
