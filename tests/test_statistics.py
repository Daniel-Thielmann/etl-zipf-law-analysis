import pandas as pd

from src.analysis.statistics import (
    compute_descriptive_statistics,
    compute_ks_test,
)


class TestComputeDescriptiveStatistics:
    def test_basic_statistics(self):
        results = pd.DataFrame({
            "alpha_cn": [1.0, 2.0, 3.0],
            "alpha_ca": [1.5, 2.5, 3.5],
            "r2_cn": [0.9, 0.95, 0.99],
            "r2_ca": [0.85, 0.92, 0.97],
        })
        stats = compute_descriptive_statistics(results)
        assert stats.loc["mean", "alpha_cn"] == 2.0
        assert stats.loc["mean", "alpha_ca"] == 2.5
        assert stats.loc["min", "alpha_cn"] == 1.0
        assert stats.loc["max", "alpha_ca"] == 3.5

    def test_single_row(self):
        results = pd.DataFrame({
            "alpha_cn": [1.5],
            "alpha_ca": [2.0],
            "r2_cn": [0.9],
            "r2_ca": [0.85],
        })
        stats = compute_descriptive_statistics(results)
        assert stats.loc["mean", "alpha_cn"] == 1.5
        assert pd.isna(stats.loc["std", "alpha_cn"]) or stats.loc["std", "alpha_cn"] == 0.0


class TestComputeKsTest:
    def test_identical_distributions(self):
        results = pd.DataFrame({
            "alpha_cn": [1.0, 1.1, 1.0, 1.1],
            "alpha_ca": [1.0, 1.1, 1.0, 1.1],
        })
        ks = compute_ks_test(results)
        assert ks["p_value"].iloc[0] > 0.05
        assert not ks["reject_h0_at_0_05"].iloc[0]

    def test_different_distributions(self):
        results = pd.DataFrame({
            "alpha_cn": [1.0] * 20,
            "alpha_ca": [2.0] * 20,
        })
        ks = compute_ks_test(results)
        assert ks["p_value"].iloc[0] < 0.05
        assert ks["reject_h0_at_0_05"].iloc[0]
