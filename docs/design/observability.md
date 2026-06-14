# Observability — deferred

**Status: deliberately deferred (not an omission).**

In-harness observability — logs/metrics/traces exposed *to agents* inside the
loop — is a known harness primitive. It is deferred until there is a running
service to observe. Keystone is currently pre-code (empty layer packages), so
there is nothing to instrument; adding telemetry now would violate "simplest
thing that works" (see [core-principles.md](./core-principles.md)).

## When to revisit

Stand this up once the NAT workflow (`KS-0101`) and the evidence ledger
(`KS-0102/0103`) run end-to-end. At that point, the natural surfaces are:

- structured logs around workflow steps and ledger appends;
- a trace/span per agent run, surfaced where an agent can read it back;
- the evidence ledger itself doubles as an audit/observability record.

Until then this file marks the slot so the gap is explicit and tracked.
