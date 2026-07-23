import numpy as np
import pytest

from src.analysis.zipf import (
    compute_zipf_alpha,
    fit_linear_least_squares,
    fit_power_law,
)


class TestFitLinearLeastSquares:
    def test_perfect_line(self):
        x = np.array([1.0, 2.0, 3.0])
        y = 2.0 * x + 1.0
        slope, intercept, r2 = fit_linear_least_squares(x, y)
        assert np.isclose(slope, 2.0)
        assert np.isclose(intercept, 1.0)
        assert np.isclose(r2, 1.0)

    def test_negative_slope(self):
        x = np.array([1.0, 2.0, 3.0])
        y = -3.0 * x + 5.0
        slope, intercept, r2 = fit_linear_least_squares(x, y)
        assert np.isclose(slope, -3.0)
        assert np.isclose(intercept, 5.0)
        assert np.isclose(r2, 1.0)

    def test_insufficient_points(self):
        x = np.array([1.0])
        y = np.array([2.0])
        with pytest.raises(ValueError, match="ao menos 2 pontos"):
            fit_linear_least_squares(x, y)

    def test_zero_variance(self):
        x = np.array([1.0, 1.0, 1.0])
        y = np.array([2.0, 3.0, 4.0])
        with pytest.raises(ValueError, match="variância de x nula"):
            fit_linear_least_squares(x, y)

    def test_mismatched_lengths(self):
        x = np.array([1.0, 2.0])
        y = np.array([1.0])
        with pytest.raises(ValueError):
            fit_linear_least_squares(x, y)


class TestFitPowerLaw:
    def test_perfect_power_law(self):
        ranks = np.array([1, 2, 3, 4, 5], dtype=float)
        frequencies = 100.0 / ranks
        alpha, r2 = fit_power_law(ranks, frequencies)
        assert np.isclose(alpha, 1.0, atol=0.05)
        assert r2 > 0.99

    def test_zipf_coefficient_around_one(self):
        rng = np.random.default_rng(42)
        ranks = np.arange(1, 101, dtype=float)
        freqs = 1000.0 / ranks + rng.normal(0, 5, 100)
        freqs = np.clip(freqs, 1, None)
        alpha, r2 = fit_power_law(ranks, freqs)
        assert 0.8 <= alpha <= 1.2
        assert r2 > 0.8


class TestComputeZipfAlpha:
    def test_simple_repeated_words(self):
        words = ["the", "the", "the", "of", "of", "and"]
        result = compute_zipf_alpha(words)
        assert result is not None
        alpha, r2, ranks, freqs = result
        assert alpha > 0
        assert 0 <= r2 <= 1
        assert len(ranks) == 3
        assert list(freqs) == [3, 2, 1]

    def test_single_word_returns_none(self):
        words = ["the"]
        assert compute_zipf_alpha(words) is None

    def test_empty_list_returns_none(self):
        assert compute_zipf_alpha([]) is None
