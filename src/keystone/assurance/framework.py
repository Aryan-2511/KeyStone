"""The Seam Framework (M1-01) — bind ANY (attack, financial-crime) pair uniformly.

Generalizes the single `TXN-000016` seam (KS-0403) into a *characterized class*.
A **seam pair** binds one OWASP LLM attack class to one FATF financial-crime
typology under ONE uniform independence guarantee and ONE uniform build-failing
drift assertion. P1 (prompt-injection × structuring) is the framework's FIRST
instance (see `keystone.assurance.seam`); it still passes through the framework,
which is how we prove the abstraction is faithful.

The paper-critical invariants, encoded structurally here (not re-implemented per
pair):

1. **Uniform independence guarantee — a PROPERTY, not a per-pair test.** The crime
   detector NEVER consumes the channel the attack rides. `bind` only ever hands the
   detector a `FinancialProjection` — the event stripped of every attack channel
   (`project_financial`) — and the detector is *typed* to accept that wrapper and
   nothing else, so it structurally cannot read the attack-bearing field. This is
   what defeats "isn't it circular?" at the level of the whole matrix.

2. **Uniform binding rigor.** Every CLEAN/OPEN pair inherits the same three
   mechanisms the P1 seam has, enforced once in `bind`:
   (a) single source of truth — the attack side resolves to the SAME canonical
       `VulnerabilitySignature` object (identity, not a copy);
   (b) demonstration, not coincidence — the crime finding and the resolvable attack
       implicate the SAME operative transaction id;
   (c) build-failing drift — if the two sides disagree, `bind` raises
       `SeamDriftError` and the build fails.

3. **BOUNDARY is first-class.** A pair that provably does NOT bind (P4: data-loss
   moves no money) lives in the same structure: its result is the *negative* —
   `bind` asserts the crime detector fires ZERO typologies, and that assertion IS
   the result, not an error.

Boundary: this lives in `keystone.assurance` (the edge) because it imports the core
transaction/FATF pieces; the core never imports it (import-linter KEPT). The core
stays unaware of attacks, exactly as today.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum

from keystone.core.fatf import Finding, Typology
from keystone.core.transactions import Transaction

from .signature import VulnerabilitySignature


class AttackChannel(StrEnum):
    """The carrier an attack rides — the field a memo-blind detector must NOT read."""

    MEMO = "memo"
    TOOL_CALL = "tool_call"
    EXFIL = "exfil"


class SeamResult(StrEnum):
    """How a pair classifies, per the M1-00 result distribution.

    CLEAN — the seam binds (attack and crime are the same event).
    BOUNDARY — the seam provably does NOT bind; the negative IS the result (P4).
    OPEN — outcome reported as-found (hypothesised clean, not yet certain; P5).
    """

    CLEAN = "clean"
    BOUNDARY = "boundary"
    OPEN = "open"


class SeamDriftError(Exception):
    """Raised when a pair's two sides drift apart — the build-failing assertion.

    For CLEAN/OPEN pairs: the crime finding and the canonical attack stopped
    implicating the SAME transaction. For BOUNDARY pairs: a typology unexpectedly
    fired, so the boundary no longer holds.
    """


@dataclass(frozen=True)
class FinancialProjection:
    """The ONLY view a crime detector receives: the event stripped of attack channels.

    Constructed solely by `project_financial`. A `CrimeSide.detect` is typed to take
    this wrapper — never a raw `Transaction` stream — so the detector structurally
    cannot read the attack-bearing field. `channel` records which carrier was
    stripped (audit / the framework-level independence test).
    """

    transactions: tuple[Transaction, ...]
    channel: AttackChannel


def project_financial(
    stream: Sequence[Transaction], channel: AttackChannel
) -> FinancialProjection:
    """Strip every attack channel from `stream`, leaving only the financial signal.

    The financial signal is amounts, timing, accounts, recipients, type — never the
    free-text `memo` (the only attack-bearing field a `Transaction` carries; the
    tool-call / exfil channels do not ride the transaction record at all). Blanking
    the memo regardless of `channel` makes the independence guarantee structural:
    whatever the attack rode, the detector receives a memo-free event.
    """
    stripped = tuple(txn.model_copy(update={"memo": ""}) for txn in stream)
    return FinancialProjection(transactions=stripped, channel=channel)


@dataclass(frozen=True)
class AttackSide:
    """The attack half of a pair: an OWASP class + its canonical signature + channel.

    `recognize` reads the attack channel of a transaction and resolves it to the
    canonical `signature` (by identity) or `None`. It is the ONLY thing in a pair
    permitted to read the attack channel — the crime side never can.
    """

    owasp_id: str
    name: str
    channel: AttackChannel
    signature: VulnerabilitySignature
    recognize: Callable[[Transaction], VulnerabilitySignature | None]


@dataclass(frozen=True)
class CrimeSide:
    """The financial-crime half: a FATF typology + a memo-blind detector.

    `detect` is typed to accept a `FinancialProjection` and nothing else — the
    structural expression of the independence guarantee. `typology` is the FATF
    pattern this pair binds to, or `None` for a BOUNDARY pair (no typology should
    fire at all).
    """

    typology: Typology | None
    detect: Callable[[FinancialProjection], list[Finding]]


@dataclass(frozen=True)
class SeamEvent:
    """What a pair's `plant` produces: the event the binding is asserted over.

    `stream` is the financial substrate (possibly empty for a BOUNDARY pair where no
    money moves). `operative_tx_id` is the transaction that carries the canonical
    attack AND must be implicated by the crime detector — `None` for BOUNDARY.
    """

    stream: tuple[Transaction, ...]
    operative_tx_id: str | None


@dataclass(frozen=True)
class SeamPair:
    """One (attack, financial-crime) pair, bound uniformly by `bind`."""

    pair_id: str
    title: str
    attack: AttackSide
    crime: CrimeSide
    result: SeamResult
    plant: Callable[[], SeamEvent]


@dataclass(frozen=True)
class PairBinding:
    """The result of binding a pair.

    For CLEAN/OPEN: `transaction_id`, `crime_finding`, and `signature` are all
    present and bound on the one shared id. For BOUNDARY: all three are `None` — the
    proven absence of a typology IS the result.
    """

    pair: SeamPair
    result: SeamResult
    transaction_id: str | None
    crime_finding: Finding | None
    signature: VulnerabilitySignature | None


def financial_projection_for(pair: SeamPair) -> FinancialProjection:
    """The exact projection `bind` hands `pair`'s crime detector — for the test.

    Exposes the independence property for inspection: the framework-level test
    asserts this carries NO attack-channel content for every registered pair.
    """
    return project_financial(pair.plant().stream, pair.attack.channel)


def bind(pair: SeamPair) -> PairBinding:
    """Bind a pair under the uniform independence guarantee + drift assertion.

    Runs the crime detector ONLY on the financial projection (never the raw,
    attack-bearing stream), then binds the two sides on a shared transaction id.
    Raises `SeamDriftError` if the sides disagree (CLEAN/OPEN) or if any typology
    fires (BOUNDARY) — the build-failing assertion.
    """
    event = pair.plant()
    # INDEPENDENCE: the detector is handed the projection ONLY — never event.stream.
    projection = project_financial(event.stream, pair.attack.channel)
    findings = pair.crime.detect(projection)
    typed = [
        f
        for f in findings
        if pair.crime.typology is None or f.typology is pair.crime.typology
    ]

    if pair.result is SeamResult.BOUNDARY:
        # The negative IS the result: a fund-movement typology must NOT fire on an
        # attack that moves no money. If one does, the boundary drifted — fail loud.
        if typed:
            fired = sorted({f.typology.value for f in typed})
            raise SeamDriftError(
                f"{pair.pair_id}: BOUNDARY pair expected NO typology to fire, but the "
                f"crime detector fired {fired} — the boundary no longer holds."
            )
        return PairBinding(
            pair=pair,
            result=SeamResult.BOUNDARY,
            transaction_id=None,
            crime_finding=None,
            signature=None,
        )

    # CLEAN / OPEN: bind the SAME transaction on both sides.
    if event.operative_tx_id is None:
        raise SeamDriftError(
            f"{pair.pair_id}: a {pair.result.value} pair must name an operative "
            "transaction to bind on."
        )
    crime_finding = next(
        (f for f in typed if event.operative_tx_id in f.transaction_ids), None
    )
    if crime_finding is None:
        raise SeamDriftError(
            f"{pair.pair_id}: crime detector ({pair.crime.typology}) did not implicate "
            f"the operative transaction {event.operative_tx_id} — financial side "
            "drifted."
        )
    operative = next((t for t in event.stream if t.id == event.operative_tx_id), None)
    if operative is None:
        raise SeamDriftError(
            f"{pair.pair_id}: operative transaction {event.operative_tx_id} is not in "
            "the event stream."
        )
    # SINGLE SOURCE OF TRUTH: the attack must resolve to the SAME canonical object.
    signature = pair.attack.recognize(operative)
    if signature is not pair.attack.signature:
        raise SeamDriftError(
            f"{pair.pair_id}: operative transaction {event.operative_tx_id} attack "
            f"channel ({pair.attack.channel.value}) does not resolve to the canonical "
            f"signature {pair.attack.signature.name} — attack side drifted."
        )
    return PairBinding(
        pair=pair,
        result=pair.result,
        transaction_id=event.operative_tx_id,
        crime_finding=crime_finding,
        signature=signature,
    )
