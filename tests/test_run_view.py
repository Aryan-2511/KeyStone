"""The live-execution view (UI-02) — the five real arc steps, derived not fabricated.

Deterministic, fast — no Streamlit. `arc_steps` is the pure derivation the progressive
reveal renders; these assert it surfaces the FIVE REAL milestone stages with their REAL
artifacts (from the ledger + the typed views), and that RECORDED mode reveals the SAME
steps a fresh build does — proving recorded is a paced REAL replay, not a fabrication.
"""

from __future__ import annotations

from keystone.demo import build_run_result, load_recorded_run
from keystone.ui.run_view import HERO_DESTINATIONS, arc_steps


def test_arc_steps_are_the_five_real_milestone_stages() -> None:
    r = load_recorded_run()
    steps = arc_steps(r)
    # The five revealed steps ARE the run's real arc stages, in order.
    assert tuple(s.stage for s in steps) == r.arc.stages
    assert tuple(s.stage for s in steps) == (
        "ingested",
        "detected",
        "seam_bound",
        "reported",
        "signed",
    )
    # The hash-chained ledger grows entry by entry to the run's real entry count.
    assert tuple(s.ledger_entries for s in steps) == (1, 2, 3, 4, 5)
    assert steps[-1].ledger_entries == r.arc.entry_count


def test_steps_reveal_real_artifacts_not_fabricated() -> None:
    r = load_recorded_run()
    by_stage = {s.stage: s for s in arc_steps(r)}
    # DETECT shows the real FATF finding implicating the real seam tx.
    assert r.financial_crime.typology in by_stage["detected"].title
    assert r.binding.transaction_id in by_stage["detected"].title
    # SEAM-BIND shows the real binding (the canonical signature).
    assert r.binding.signature_name in by_stage["seam_bound"].title
    # REPORT shows the real report format; SIGN the real signer + chain state.
    assert r.report.report_format in by_stage["reported"].title
    assert r.report.signed_by in by_stage["signed"].detail
    expected_chain = "verified" if r.arc.chain_verified else "TAMPERED"
    assert expected_chain in by_stage["signed"].title


def test_recorded_reveals_the_same_steps_as_a_fresh_build() -> None:
    # Recorded mode is a PACED REAL REPLAY: the steps it reveals are the genuine run's
    # steps — identical (the offline template narrative is deterministic) to a fresh
    # build's. NOT fabricated, NOT a different/instant thing.
    recorded = arc_steps(load_recorded_run())
    fresh = arc_steps(build_run_result())
    assert tuple(s.stage for s in recorded) == tuple(s.stage for s in fresh)
    assert tuple(s.title for s in recorded) == tuple(s.title for s in fresh)


def test_the_run_arrives_at_the_four_heroes() -> None:
    # The destinations the run reaches — the four result heroes (not standalone pictures).
    assert len(HERO_DESTINATIONS) == 4
    names = {name for name, _ in HERO_DESTINATIONS}
    assert names == {"Seam", "Jurisdictions", "Seam matrix", "Convergence"}
