"""Visualizações produzidas pelo experimento."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def create_all_plots(
    results: pd.DataFrame, sample: dict, output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    mean_cn, std_cn = results.alpha_cn.mean(), results.alpha_cn.std()
    mean_ca, std_ca = results.alpha_ca.mean(), results.alpha_ca.std()

    plt.figure(figsize=(10, 6))
    plt.hist(
        results.alpha_cn, bins=15, alpha=0.6,
        label=f"CN (μ={mean_cn:.3f}, σ={std_cn:.3f})",
    )
    plt.hist(
        results.alpha_ca, bins=15, alpha=0.6,
        label=f"CA (μ={mean_ca:.3f}, σ={std_ca:.3f})",
    )
    plt.axvline(mean_cn, linestyle="--", linewidth=1.5)
    plt.axvline(mean_ca, linestyle="--", linewidth=1.5)
    plt.title("Distribuição dos coeficientes α")
    plt.xlabel("α")
    plt.ylabel("Quantidade de livros")
    plt.legend()
    plt.grid(alpha=0.3)
    _save(output_dir / "alpha_histogram.png")

    plt.figure(figsize=(8, 6))
    plt.boxplot(
        [results.alpha_cn, results.alpha_ca],
        tick_labels=["Humano", "IA"],
    )
    plt.title("Comparação dos coeficientes α")
    plt.grid(alpha=0.3)
    _save(output_dir / "alpha_boxplot.png")

    if len(results) >= 2:
        plt.figure(figsize=(10, 6))
        results.alpha_cn.plot(kind="density", label="CN")
        results.alpha_ca.plot(kind="density", label="CA")
        plt.title("Densidade dos coeficientes α")
        plt.legend()
        plt.grid(alpha=0.3)
        _save(output_dir / "alpha_density.png")

    plt.figure(figsize=(10, 6))
    plt.hist(results.r2_cn, alpha=0.5, bins=15, label="CN")
    plt.hist(results.r2_ca, alpha=0.5, bins=15, label="CA")
    plt.title("Distribuição dos valores de R²")
    plt.legend()
    plt.grid(alpha=0.3)
    _save(output_dir / "r2_histogram.png")

    plt.figure(figsize=(10, 6))
    for suffix, label in (("cn", "CN"), ("ca", "CA")):
        ranks = np.asarray(sample[f"r_{suffix}"])
        freqs = np.asarray(sample[f"f_{suffix}"])
        alpha = sample[f"a_{suffix}"]
        coefs = np.polyfit(np.log(ranks), np.log(freqs), 1)
        predicted = np.exp(coefs[1]) * ranks ** coefs[0]
        plt.scatter(ranks, freqs, alpha=0.35, s=10, label=f"{label}: dados")
        plt.plot(
            ranks, predicted, linewidth=2, label=f"{label}: α={alpha:.3f}"
        )
    plt.xscale("log")
    plt.yscale("log")
    plt.title(f"Ajuste da Lei de Zipf — livro {sample['book_id']}")
    plt.xlabel("Ranking da palavra")
    plt.ylabel("Frequência")
    plt.legend()
    plt.grid(which="both", linestyle="--", alpha=0.3)
    _save(output_dir / "zipf_loglog_fit.png")
