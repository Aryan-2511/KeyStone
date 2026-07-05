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

from .run_result import RunResult, TriageView


def _rule(char: str = "=") -> str:
    return char * 60


def _headline(redteam_is_live: bool, triage_is_live: bool) -> str:
    """The banner — honest about which agents ran live this run (if any)."""
    live = [
        name
        for name, on in (("red-team", redteam_is_live), ("triage", triage_is_live))
        if on
    ]
    if live:
        return f"KEYSTONE - end-to-end assurance arc (LIVE {' + '.join(live)}; rest offline)"
    return "KEYSTONE - end-to-end assurance arc (offline, deterministic)"


def _closing(
    reasoner: str,
    source: str,
    scan_scope: str,
    redteam_is_live: bool,
    triage_is_live: bool,
) -> str:
    """The footer — states which agents ran live honestly, or the fully-offline guarantee."""
    parts: list[str] = []
    if redteam_is_live:
        parts.append(
            f"Red-Team ran LIVE on real Garak scans ({source}, {scan_scope} scope)"
        )
    if triage_is_live:
        parts.append(f"Triage ran LIVE on {reasoner[len('llm:') :]} (a real LLM call)")
    if parts:
        return (
            f"{'; '.join(parts)}; the rest of the arc ran offline & deterministic. "
            "Re-run without a --live flag for the fully offline front door."
        )
    return (
        "Ran offline from a clean clone - no Ollama, no network, no Garak. "
        "Deterministic by design."
    )


def _triage_lines(tr: TriageView) -> list[str]:
    """The Triage Agent (MB-01) block — the supervisor's route over the signal interplay."""
    return [
        "4. Triage Agent - supervisor",
        f"   {tr.mechanism}",
        f"   reasoner: {tr.reasoner}",
        f"   route: {tr.route.upper()}  "
        f"(seam={tr.seam_result} | severity={tr.severity} | "
        f"failure_rate={tr.failure_rate:.2f})",
        f"   options: {' / '.join(tr.routes_available)}",
        f"   {tr.rationale}",
        "",
    ]


def _defense_lines(result: RunResult) -> list[str]:
    """The Defense Agent (MC-01) block — the third agent's remediation choice, or empty.

    Optional: a run recorded before the Defense Agent existed has no `defense` block.
    """
    df = result.defense
    if df is None:
        return []
    return [
        "4b. Defense Agent - defender",
        f"   {df.mechanism}",
        f"   reasoner: {df.reasoner}",
        f"   chose: {df.control} [{df.side}]  "
        f"(failure_rate={df.failure_rate:.2f} | financial_gap={df.financial_gap})",
        f"   menu: {' / '.join(df.remediations_available)}",
        f"   {df.rationale}",
        "",
    ]


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

    # Which agents ran LIVE this run: the Red-Team over real Garak scans (OPT-A-02) and
    # the Triage over an LLM (OPT-A-01). The rest of the arc is always offline.
    redteam_is_live, triage_is_live = (
        rt.source == "garak_live",
        tr.reasoner.startswith("llm:"),
    )

    add(_headline(redteam_is_live, triage_is_live))
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
    add(f"   source: {rt.source}")
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

    for line in _triage_lines(tr):
        add(line)

    # 4b. Defense Agent (MC-01) — the third agent, present when the run recorded a choice.
    for line in _defense_lines(result):
        add(line)

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
        _closing(tr.reasoner, rt.source, rt.scan_scope, redteam_is_live, triage_is_live)
    )
    return "\n".join(lines)
