"""Ajuste da Lei de Zipf por mínimos quadrados no espaço log-log."""
from __future__ import annotations

from collections import Counter

import numpy as np


def fit_linear_least_squares(
    x: np.ndarray, y: np.ndarray
) -> tuple[float, float, float]:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("x e y devem possuir o mesmo tamanho e ao menos 2 pontos.")

    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    denominator = n * np.sum(x**2) - sum_x**2
    if np.isclose(denominator, 0.0):
        raise ValueError("Não é possível ajustar uma reta: variância de x nula.")

    slope = (n * np.sum(x * y) - sum_x * sum_y) / denominator
    intercept = np.mean(y) - slope * np.mean(x)
    y_pred = intercept + slope * x
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if not np.isclose(ss_tot, 0.0) else 1.0
    return float(slope), float(intercept), float(r2)


def fit_power_law(
    ranks: np.ndarray, frequencies: np.ndarray
) -> tuple[float, float]:
    valid = (ranks > 0) & (frequencies > 0)
    log_ranks = np.log(ranks[valid])
    log_frequencies = np.log(frequencies[valid])
    slope, _, r2 = fit_linear_least_squares(log_ranks, log_frequencies)
    return abs(slope), r2


def compute_zipf_alpha(
    words: list[str],
) -> tuple[float, float, np.ndarray, np.ndarray] | None:
    counts = Counter(words)
    frequencies = np.asarray(
        sorted(counts.values(), reverse=True), dtype=float
    )
    ranks = np.arange(1, len(frequencies) + 1, dtype=float)
    if len(ranks) < 2:
        return None
    alpha, r2 = fit_power_law(ranks, frequencies)
    return alpha, r2, ranks, frequencies
