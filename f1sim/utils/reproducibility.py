"""Reproducibility helpers."""

from __future__ import annotations

import random

import numpy as np


def set_global_seed(seed: int) -> None:
    """Set common pseudo-random seeds for deterministic experiments."""

    random.seed(seed)
    np.random.seed(seed)
