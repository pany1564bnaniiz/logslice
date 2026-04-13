"""Sampling utilities for logslice — reduce output by keeping every Nth record
or a random percentage of records."""

from __future__ import annotations

import random
from typing import Iterable, Iterator


class SamplerError(Exception):
    """Raised when sampler configuration is invalid."""


def sample_nth(
    records: Iterable[dict],
    n: int,
) -> Iterator[dict]:
    """Yield every *n*-th record (1-based).  ``n=1`` keeps all records.

    Args:
        records: Iterable of parsed log record dicts.
        n: Keep one record for every *n* records seen.

    Raises:
        SamplerError: If *n* is less than 1.
    """
    if n < 1:
        raise SamplerError(f"n must be >= 1, got {n}")
    for i, record in enumerate(records):
        if i % n == 0:
            yield record


def sample_random(
    records: Iterable[dict],
    rate: float,
    seed: int | None = None,
) -> Iterator[dict]:
    """Yield each record with probability *rate* (0.0 – 1.0).

    Args:
        records: Iterable of parsed log record dicts.
        rate: Fraction of records to keep, e.g. ``0.1`` keeps ~10 %.
        seed: Optional RNG seed for reproducible sampling.

    Raises:
        SamplerError: If *rate* is outside [0.0, 1.0].
    """
    if not (0.0 <= rate <= 1.0):
        raise SamplerError(f"rate must be between 0.0 and 1.0, got {rate}")
    rng = random.Random(seed)
    for record in records:
        if rng.random() < rate:
            yield record


def apply_sampler(
    records: Iterable[dict],
    nth: int | None = None,
    rate: float | None = None,
    seed: int | None = None,
) -> Iterator[dict]:
    """Convenience wrapper that applies nth or rate sampling (not both).

    Args:
        records: Iterable of parsed log record dicts.
        nth: If set, keep every nth record.
        rate: If set, keep each record with this probability.
        seed: RNG seed used only when *rate* is given.

    Raises:
        SamplerError: If both *nth* and *rate* are supplied, or configuration
            is otherwise invalid.
    """
    if nth is not None and rate is not None:
        raise SamplerError("Specify either 'nth' or 'rate', not both.")
    if nth is not None:
        yield from sample_nth(records, nth)
    elif rate is not None:
        yield from sample_random(records, rate, seed=seed)
    else:
        yield from records
