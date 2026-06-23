"""The seam matrix registry — every (attack, financial-crime) pair, in one place.

The framework-level guarantees (the uniform independence property, the uniform
binding rigor, the build-failing drift assertion) are asserted over THIS tuple, so
adding a pair (M1-02..M1-05) automatically subjects it to the same checks. Today it
holds only P1, the framework's first instance; the matrix grows here.
"""

from __future__ import annotations

from .framework import SeamPair
from .seam import P1_PAIR
from .seam_p2 import P2_PAIR
from .seam_p3 import P3_PAIR
from .seam_p4 import P4_PAIR
from .seam_p5 import P5_PAIR

REGISTERED_PAIRS: tuple[SeamPair, ...] = (
    P1_PAIR,
    P2_PAIR,
    P3_PAIR,
    P4_PAIR,
    P5_PAIR,
)
