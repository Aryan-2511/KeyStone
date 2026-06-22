"""The seam matrix registry — every (attack, financial-crime) pair, in one place.

The framework-level guarantees (the uniform independence property, the uniform
binding rigor, the build-failing drift assertion) are asserted over THIS tuple, so
adding a pair (M1-02..M1-05) automatically subjects it to the same checks. Today it
holds only P1, the framework's first instance; the matrix grows here.
"""

from __future__ import annotations

from .framework import SeamPair
from .seam import P1_PAIR

REGISTERED_PAIRS: tuple[SeamPair, ...] = (P1_PAIR,)
