"""Orchestration — NeMo Agent Toolkit (`nvidia-nat`) workflows.

The orchestration entry point. TODAY this package holds DETERMINISTIC orchestration:
NAT sequences fixed workflow stages (the chassis fan-out, the assurance loop, the
Layer-1 milestone arc) — no reasoning, and no agent chooses the next step (the stubs'
own docstrings say "no LLM — just orchestration"). The package name looks FORWARD: this
is where the genuine agents being added in Movements A/B — the offensive Red-Team agent
(observe -> reason -> adapt over the Garak probe library) and the supervisory Triage
agent — will sit, within this orchestration. Until those land, nothing here is an agent
in the reasoning sense.

May depend inward on the deterministic core; the core must not depend on it.
"""
