"""Tests for logslice.sampler."""

from __future__ import annotations

import pytest

from logslice.sampler import (
    SamplerError,
    apply_sampler,
    sample_nth,
    sample_random,
)

_RECORDS = [{"i": i, "msg": f"line {i}"} for i in range(10)]


# ---------------------------------------------------------------------------
# sample_nth
# ---------------------------------------------------------------------------

def test_sample_nth_keeps_all_when_n_is_1():
    result = list(sample_nth(_RECORDS, 1))
    assert result == _RECORDS


def test_sample_nth_keeps_every_second():
    result = list(sample_nth(_RECORDS, 2))
    assert [r["i"] for r in result] == [0, 2, 4, 6, 8]


def test_sample_nth_keeps_every_third():
    result = list(sample_nth(_RECORDS, 3))
    assert [r["i"] for r in result] == [0, 3, 6, 9]


def test_sample_nth_n_larger_than_records():
    result = list(sample_nth(_RECORDS, 100))
    assert result == [_RECORDS[0]]


def test_sample_nth_invalid_n_raises():
    with pytest.raises(SamplerError, match=">= 1"):
        list(sample_nth(_RECORDS, 0))


def test_sample_nth_negative_n_raises():
    with pytest.raises(SamplerError):
        list(sample_nth(_RECORDS, -5))


# ---------------------------------------------------------------------------
# sample_random
# ---------------------------------------------------------------------------

def test_sample_random_rate_zero_keeps_nothing():
    result = list(sample_random(_RECORDS, rate=0.0, seed=42))
    assert result == []


def test_sample_random_rate_one_keeps_all():
    result = list(sample_random(_RECORDS, rate=1.0, seed=42))
    assert result == _RECORDS


def test_sample_random_reproducible_with_seed():
    r1 = list(sample_random(_RECORDS, rate=0.5, seed=7))
    r2 = list(sample_random(_RECORDS, rate=0.5, seed=7))
    assert r1 == r2


def test_sample_random_different_seeds_differ():
    r1 = list(sample_random(_RECORDS, rate=0.5, seed=1))
    r2 = list(sample_random(_RECORDS, rate=0.5, seed=2))
    # With 10 records and rate 0.5 it is astronomically unlikely they match
    assert r1 != r2


def test_sample_random_invalid_rate_high_raises():
    with pytest.raises(SamplerError, match="0.0 and 1.0"):
        list(sample_random(_RECORDS, rate=1.5))


def test_sample_random_invalid_rate_negative_raises():
    with pytest.raises(SamplerError):
        list(sample_random(_RECORDS, rate=-0.1))


# ---------------------------------------------------------------------------
# apply_sampler
# ---------------------------------------------------------------------------

def test_apply_sampler_no_options_passes_all():
    result = list(apply_sampler(_RECORDS))
    assert result == _RECORDS


def test_apply_sampler_nth():
    result = list(apply_sampler(_RECORDS, nth=2))
    assert [r["i"] for r in result] == [0, 2, 4, 6, 8]


def test_apply_sampler_rate():
    result = list(apply_sampler(_RECORDS, rate=1.0))
    assert result == _RECORDS


def test_apply_sampler_both_raises():
    with pytest.raises(SamplerError, match="not both"):
        list(apply_sampler(_RECORDS, nth=2, rate=0.5))
