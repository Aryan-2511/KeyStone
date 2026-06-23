"""Build the characterized seam-matrix result from REGISTERED_PAIRS (M1-06).

The matrix block of the `RunResult` is DERIVED from
`keystone.assurance.pairs.REGISTERED_PAIRS` — the single source of truth — so adding a
pair makes it appear in the result (and the hero) with nothing hardcoded. This module
holds only the presentation derivation: plain-language typology labels (a judge won't
know the FATF names cold) and the one independence property the shared framework
carries. No detection re-run — the per-pair binding is gate-tested in the seam suites;
here we read the declared mapping (attack class, typology, result, axis).

Boundary: lives in `keystone.demo` (it draws on the assurance edge + the core FATF
typology enum); the core never imports it (import-linter KEPT).
"""

from __future__ import annotations

from keystone.assurance import BOUNDARY_STATEMENT, REGISTERED_PAIRS
from keystone.core.fatf import Typology

from .run_result import MatrixPairView, MatrixView

# Plain-language labels for the FATF typologies (the figure translates every id).
_TYPOLOGY_LABELS: dict[Typology, str] = {
    Typology.STRUCTURING: "Structuring (smurfing)",
    Typology.RAPID_MOVEMENT: "Rapid movement / layering",
    Typology.LARGE_TRANSFER: "Large transfer / threshold breach",
    Typology.UNAUTHORIZED_RECIPIENT: "Unauthorized recipient (sanctions-style)",
}

# The ONE independence property the shared framework carries — stated once for the
# whole matrix (not repeated per pair). This is what defeats "isn't it circular?".
INDEPENDENCE_PROPERTY = (
    "One framework binds all five — the crime detector never reads the attack channel."
)


def build_matrix_view() -> MatrixView:
    """Assemble the `MatrixView` from REGISTERED_PAIRS (derived, never hardcoded)."""
    pairs: list[MatrixPairView] = []
    for pair in REGISTERED_PAIRS:
        typology = pair.crime.typology
        pairs.append(
            MatrixPairView(
                pair_id=pair.pair_id,
                attack_owasp_id=pair.attack.owasp_id,
                attack_name=pair.attack.name,
                typology=typology.value if typology is not None else None,
                typology_label=(
                    _TYPOLOGY_LABELS.get(typology, typology.value)
                    if typology is not None
                    else ""
                ),
                result=pair.result.value.upper(),
                # Axis A holds the attack class (LLM01) and varies the typology; Axis B
                # varies the attack class (beyond injection). Derived from the pair.
                axis="A" if pair.attack.owasp_id == "LLM01" else "B",
            )
        )
    return MatrixView(
        pairs=tuple(pairs),
        clean_count=sum(1 for p in pairs if p.result == "CLEAN"),
        boundary_count=sum(1 for p in pairs if p.result == "BOUNDARY"),
        boundary_statement=BOUNDARY_STATEMENT,
        independence_property=INDEPENDENCE_PROPERTY,
    )
