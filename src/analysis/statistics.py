"""Indicadores estatísticos do experimento."""
from __future__ import annotations

import pandas as pd
from scipy import stats


def compute_descriptive_statistics(results: pd.DataFrame) -> pd.DataFrame:
    return results[["alpha_cn", "alpha_ca", "r2_cn", "r2_ca"]].agg(
        ["mean", "median", "std", "min", "max"]
    )


def compute_ks_test(results: pd.DataFrame) -> pd.DataFrame:
    ks_stat, p_value = stats.ks_2samp(
        results.alpha_cn, results.alpha_ca
    )
    return pd.DataFrame([{
        "delta_alpha": results.alpha_cn.mean() - results.alpha_ca.mean(),
        "ks_statistic": ks_stat,
        "p_value": p_value,
        "reject_h0_at_0_05": p_value < 0.05,
    }])
