"""Obligations→controls crosswalk as a deterministic LOOKUP (KS-0202).

The crosswalk is a JOIN on `control_id`, NOT a clustering of obligation text:
each obligation already declares the controls it satisfies (`control_ids`), so
control→[obligations] is read directly from the data. This keeps the "N
obligations → M controls" mapping reproducible and auditable.

Enforcement modality is PRESERVED through the grouping: a control satisfied by
both a HARD_LAW article and a SELF_CERTIFICATION sutra exposes BOTH modalities,
which KS-0203's modality contrast reads. Deterministic core: no LLM, no network.
"""

from __future__ import annotations

from dataclasses import dataclass

from keystone.core.obligations import Modality, Obligation

from .models import Control


@dataclass(frozen=True)
class ControlMapping:
    """One control and the obligations that crosswalk onto it (lookup result)."""

    control: Control
    obligations: tuple[Obligation, ...]
    modalities: frozenset[Modality]


def build_crosswalk(
    controls: list[Control], obligations: list[Obligation]
) -> list[ControlMapping]:
    """Return control→[obligations] by lookup on `control_ids`.

    Order follows `controls` (deterministic); within a control, obligations are
    sorted by id. Raises `ValueError` on a `control_id` that does not resolve —
    the same fail-loud stance as the §5b validator (this function assumes
    referential integrity has been or will be enforced).
    """
    buckets: dict[str, list[Obligation]] = {c.id: [] for c in controls}

    for obligation in obligations:
        for control_id in obligation.control_ids:
            if control_id not in buckets:
                raise ValueError(
                    f"{obligation.id}: control_id {control_id!r} does not resolve "
                    "to a known control"
                )
            buckets[control_id].append(obligation)

    mappings: list[ControlMapping] = []
    for control in controls:
        bucket = sorted(buckets[control.id], key=lambda o: o.id)
        modalities = frozenset(o.enforcement_modality for o in bucket)
        mappings.append(
            ControlMapping(
                control=control,
                obligations=tuple(bucket),
                modalities=modalities,
            )
        )
    return mappings
