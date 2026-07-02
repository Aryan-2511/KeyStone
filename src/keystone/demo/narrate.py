"""Human-readable terminal narration of a real `RunResult`.

`narrate_run` renders the end-to-end arc a `RunResult` captured — the FATF finding,
the Red-Team Agent's landed exploit, the seam bind, the Triage Agent's route, and
the sealed ledger — as plain text for the console front door (`keystone demo`).

It is a *pure view*: every line is read from an actual `RunResult` produced by the
genuine arc (`keystone.demo.build_run_result`). Nothing here fabricates or hardcodes
a result — if a field is missing, that is a schema break to fix, not to paper over.

Output is ASCII-only so the front door renders correctly from a clean clone on any
console encoding (including Windows cp1252), with no stdout reconfiguration.
"""

from __future__ import annotations

from .run_result import RunResult


def _rule(char: str = "=") -> str:
    return char * 60


def narrate_run(result: RunResult) -> str:
    """Render `result` as a readable terminal narration of the real arc."""
    tx = result.seam_transaction
    fc = result.financial_crime
    ais = result.ai_security
    rt = result.red_team
    bind = result.binding
    tr = result.triage
    rep = result.report
    arc = result.arc

    lines: list[str] = []
    add = lines.append

    add("KEYSTONE - end-to-end assurance arc (offline, deterministic)")
    add(_rule())
    add("")
    add("The seam transaction (the one object both findings bind to)")
    add(
        f"  {tx.id} | {tx.sender_account} -> {tx.recipient_account} | "
        f"{tx.amount:,.2f} {tx.currency} | {tx.tx_type}"
    )
    add(f'  memo: "{tx.memo}"')
    add("")

    add("1. Financial-crime detection  (Layer 1 | FATF, memo-blind)")
    add(
        f"   {fc.typology} | severity {fc.severity} | account {fc.account} | "
        f"{len(fc.transaction_ids)} transactions"
    )
    add(f"   {fc.rationale}")
    add("")

    add("2. Red-Team Agent - offensive worker")
    add(f"   {rt.mechanism}")
    landed = "yes" if (rt.decisions and rt.decisions[-1].got_through) else "no"
    final_rate = rt.decisions[-1].failure_rate if rt.decisions else 0.0
    add(
        f"   ran {rt.probes_run} probes over {len(rt.families_available)} families; "
        f"exploited family: {rt.exploited_family}"
    )
    add(
        f"   landed exploit: {ais.outcome} via {ais.exploit_tool} "
        f"(final observed failure rate {final_rate:.2f}, got through: {landed})"
    )
    add("")

    add("3. The seam bind  (the thesis)")
    add(
        f"   ONE transaction ({bind.transaction_id}) is BOTH a {bind.fatf_typology} "
        f"financial crime AND"
    )
    add(f"   the {bind.signature_name} vulnerability - bound on the shared tx id.")
    add(f"   {bind.thesis}")
    add("")

    add("4. Triage Agent - supervisor")
    add(f"   {tr.mechanism}")
    add(
        f"   route: {tr.route.upper()}  "
        f"(seam={tr.seam_result} | severity={tr.severity} | "
        f"failure_rate={tr.failure_rate:.2f})"
    )
    add(f"   options: {' / '.join(tr.routes_available)}")
    add(f"   {tr.rationale}")
    add("")

    add("5. Evidence ledger  (sealed, hash-chained)")
    add(f"   arc: {' -> '.join(arc.stages)}")
    add(
        f"   {rep.report_format} report {rep.status} by {rep.signed_by}"
        + ("  (narrative fell back to template)" if rep.narrative_fell_back else "")
    )
    add(
        f"   hash chain verified: {'yes' if arc.chain_verified else 'NO'} | "
        f"{arc.entry_count} entries | arc complete: "
        f"{'yes' if arc.arc_complete else 'NO'}"
    )
    add("")
    add(_rule("-"))
    add(
        "Ran offline from a clean clone - no Ollama, no network, no Garak. "
        "Deterministic by design."
    )
    return "\n".join(lines)
