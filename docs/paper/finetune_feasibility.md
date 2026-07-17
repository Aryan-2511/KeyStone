# Fine-tuning feasibility for the agent decisions — an honest assessment

**Probe:** `probe-finetune-feasibility` · **Date:** 2026-07-13 · **Mode:** READ-ONLY
(this doc is the only artifact — **no training, no data generation, no code change**)

> **RESOLVED (2026-07-18) — FINETUNE-SPIKE-01 ran the one-run spike this probe recommended; the
> verdict is CAPACITY-BOUND (negative).** The spike (§ "Smallest honest next step") was executed
> end-to-end: Q3 protocol dataset + frozen 48-case held-out eval, Unsloth QLoRA on
> **Qwen2.5-3B-Instruct (matched control)**, deployed on-prem via Ollama, measured with the same
> harness as the baseline. **specialized-3B = 77% overall / 76% reserved-band vs general-3B 77% /
> 78%** — level, marginally worse on the band; the fine-tune only *reshuffled* errors and still
> misread the sub-0.10 threshold. Specialization did **not** close the held-out gap → the ceiling is
> **capacity, not method**. Full details in `docs/paper/finetune_spike.md` and **ADR-0034**; the
> "either outcome is publishable" bet below landed on the honest negative.

**The question this answers.** OPT-A-01b showed a general 3B model (qwen2.5:3b) cannot reliably
reason Keystone's bounded triage decision: in-distribution it agreed with the policy 6/6, but on
a held-out anti-parrot probe it dropped to **4/6**, misreading the numeric `failure_rate` and
misapplying seam semantics (`OPEN_QUESTIONS.md:88-90`, `docs/exec-plans/completed/opt-a-01b-triage-prompt-rescue.md:30-48`).
The named frontier is a **purpose-fine-tuned small on-prem model** that does the reasoning the
general 3B could not (`OPEN_QUESTIONS.md:99-106`). Colab supplies the training hardware; weights
download and run on-prem, so data-residency holds (training data is synthetic). The make-or-break
is **DATA**: can we generate enough diverse, **contamination-free** labeled data to produce a
*credible* result — genuine generalization, not a memorized/leaked one? This probe assesses the
data, designs the train/test disjointness protocol, and gives an honest viability verdict.

**Scope.** Assessed **TRIAGE first** (it already has the held-out eval harness). Defense is noted
as a thinner extension, not the primary target.

---

## The one distinction the whole assessment turns on: RULE-COMPLEXITY vs DATA-VOLUME

A reviewer will collapse "can we make enough data?" into "can we make a lot of rows?" — those are
different questions and the gap between them is the whole finding. The triage labels come from a
**deterministic policy** (`route_for`, `src/keystone/agents/triage.py:161-194`). Row *volume* is
therefore unlimited (sample signals, call the policy, get a label — for free). What is bounded is
the **information content of the rule** the model must learn. If that rule is trivial, a model can
*memorize* it and "high accuracy" proves nothing; genuine generalization can only be demonstrated
on the *one axis* where the rule is actually non-trivial. The rest of this doc separates those two
and shows the credible claim lives entirely in the second.

---

## Q1 — The decision to learn: the exact input→output

The model would learn to replicate **`route_for`** (`triage.py:161-194`), the transparent triage
policy that is *already* the ground truth and the source of the few-shot examples.

**Input** — three already-computed signals (`TriageSignals`, `triage.py:145-158`), read as plain
values (the memo-blind boundary is sacred — SIGNALS ONLY, never the attack channel):

| Signal | Type / domain | Source of truth |
| --- | --- | --- |
| `failure_rate` | `float` ∈ [0, 1] — fraction of attacks that landed | `triage.py:156` |
| `seam_result` | `{clean, boundary, open}` | `SeamClassification`, `triage.py:73-75` |
| `severity` | `{LOW, MEDIUM, HIGH}` | `FindingSeverity`, `triage.py:86-88` |

**Output** — exactly one of three routes (`Route`, `triage.py:100-102`): `remediate` / `accept` /
`escalate`.

**The ground-truth rule** (`route_for`, `triage.py:185-194`), applied in order:

1. `severity is HIGH` → **escalate** (regardless of rate or seam)
2. else `failure_rate < 0.10` (`ACTION_FLOOR`, `triage.py:107`) → **accept**
3. else the seam decides: `open` → **escalate**, `boundary` → **accept**, `clean` → **remediate**

The interplay is real: the *same* `failure_rate` routes three different ways by seam (step 3) — the
property the honesty tests exercise.

**Defense (noted, not primary).** The second candidate is `choose_remediation`
(`src/keystone/agents/defense.py:98-110`): a **2-way** choice ((a) guardrail patch vs (c) financial
tightening) over `DefenseSignals` (`defense.py:77-80`) — `failure_rate`, a boolean `financial_gap`,
plus seam/severity for the rationale. Its rule is even simpler: `financial_gap and failure_rate <
0.10` → (c), else (a) — **effectively a 2-leaf rule with one boolean and one threshold**. It has no
held-out eval harness. Triage is the stronger first target; defense is a weaker demonstration
(binary, thinner rule) and should only follow if triage answers the question positively.

---

## Q2 — Data VOLUME + DIVERSITY: is the input space rich enough to force learning, not memorizing?

**Volume is a non-issue.** Labels are a pure function call; we can mint 1k, 100k, or 1M
`(signals → route)` pairs at zero marginal cost. Fine-tuning a small model on a 3-way classifier
needs *far* less than that. **Volume is not the constraint — do not frame it as one.**

**Diversity is the real question, and the honest answer is two-sided.** Decompose the rule's input
space by what actually changes the label:

- **`severity`**: only **HIGH vs not-HIGH** matters. LOW and MEDIUM are **routing-equivalent** (both
  fall through to steps 2–3). So 3 levels collapse to **2** decision-relevant classes.
- **`failure_rate`**: only the **single threshold at 0.10** matters. Every value in [0, 0.10) behaves
  identically; every value in [0.10, 1] behaves identically (given the other signals). The continuous
  axis collapses to **2** sides — *but the boundary itself is a real, learnable, continuous thing.*
- **`seam_result`**: 3 values, decisive only in step 3 (not-HIGH, above floor).

**Enumerating the distinct behaviours: the rule is a 5-leaf decision tree.**

| Region (severity, rate, seam) | Route | Raw cells covered |
| --- | --- | --- |
| HIGH, any, any | escalate | 6 |
| not-HIGH, < 0.10, any | accept | 6 |
| not-HIGH, ≥ 0.10, clean | remediate | 2 |
| not-HIGH, ≥ 0.10, boundary | accept | 2 |
| not-HIGH, ≥ 0.10, open | escalate | 2 |

Over the *categorical* grid (`{HIGH, not-HIGH}` × `{below, above}` × 3 seams = 12 cells, or 18 if
all three severities are kept), there are only **5 distinct rules** and **3 outputs**. **The
categorical structure is thin enough to be a lookup table** — a model that memorizes ~9–18 combos
"passes" without learning anything. Categorical accuracy alone would be **self-deceptive**.

**Where genuine generalization lives: the continuous `failure_rate` threshold.** This is the one
axis with real, non-memorizable content — and it is *exactly* the axis the general 3B failed on
(it called 0.06 "above 0.10", `opt-a-01b…md:46-48`). A model shown floats on both sides of 0.10 and
tested on **held-out float values it never saw** must have learned the *threshold* (and its
interaction with the HIGH-override and the seam map) to be right. That is real generalization over a
continuous variable, and it is the precise capability at issue.

**Verdict on data (Q2).** Volume: unlimited. Diversity: **adequate on the one axis that matters**
(the continuous rate threshold + the override/interplay precedence), **thin on the categoricals**
(a memorizable 5-leaf rule). This is neither "rich" nor "too thin to show anything" — it is *rich
enough for one narrow, well-defined generalization claim* and nothing broader. Two data-generation
requirements follow directly:

- **Stratify to balance the 3 routes.** Uniform sampling over (rate, seam, severity) is
  escalate-heavy (all HIGH + all open-above-floor collapse to escalate). Balance the label
  distribution so accuracy is not inflated by a majority class.
- **Over-sample the near-threshold band.** Concentrate `failure_rate` density around 0.10 (both
  sides) at fine granularity, across every seam×severity combo — that is where the learnable content
  and the 3B failures both live.

---

## Q3 — CONTAMINATION: the train/test disjointness protocol (the make-or-break deliverable)

A fine-tune result without **provable** train/test disjointness is worthless — it measures memory,
not generalization. The tabular, low-dimensional, structured input here is a **gift**: unlike text
fine-tuning (where contamination is fuzzy and needs embedding-similarity heuristics), disjointness
can be **guaranteed by construction** and **checked mechanically**. The protocol has four parts.

### Part 1 — Partition the CONTINUOUS axis (the primary generalization test)

The threshold at 0.10 is the real learnable boundary, so hold out a **band around it** plus specific
values, and never let training touch them:

- **Held-out threshold band.** Train `failure_rate` sampled only from `[0.00, 0.05] ∪ [0.20, 1.00]`.
  The band `(0.05, 0.20)` — which brackets the 0.10 decision boundary — is **reserved for test**. A
  model that learned the threshold classifies band points correctly; one that memorized training
  rates *cannot* (it never saw a rate in the band). This directly targets the OPT-A-01b numeric
  misread (0.06, 0.08, 0.12 all live in the reserved band).
- **Held-out exact values.** Additionally reserve a set of round values used by the existing eval
  (e.g. 0.25, 0.30, 0.45) so no exact-value memorization can pass, even outside the band.

### Part 2 — Partition the CATEGORICAL interactions (held-out precedence combos)

Because the categorical grid is memorizable, do not merely hold out *examples* — hold out **whole
interaction cells** the model must reach by applying the override *rules*, not by lookup. Reuse the
OPT-A-01b anti-parrot design (`scripts/triage_llm_eval.py:104-153`), which is already built exactly
this way — each case chosen so a pattern-matcher gets it wrong while a rule-applier gets it right:

- `clean, HIGH, 0.12` → escalate (HIGH overrides the clean→remediate map)
- `clean, LOW, 0.25` → remediate (the only clean+LOW example the prompt ever showed was 0.05→accept)
- `open, MED, 0.06` → accept (the floor beats open→escalate — requires reading 0.06 < 0.10)
- `boundary, HIGH, 0.08` → escalate (HIGH overrides floor + boundary)
- `boundary, LOW, 0.30` → accept
- `open, HIGH, 0.45` → escalate (no route-collapse)

### Part 3 — The frozen, EXTENDED held-out eval set

The 6 anti-parrot cases (`triage_llm_eval.py:104-153`) are the **existing** held-out set and the
apples-to-apples baseline (general 3B = **4/6**). Six points give a coarse fraction; **extend to
~40–60 held-out cases** — the 6 anti-parrot combos plus systematic threshold-band sweeps at each
seam×severity — so post-fine-tune accuracy is statistically meaningful and the baseline can be
re-measured on the same larger set. The held-out set is **frozen before any training data is
generated** and never contributes a label to training.

### Part 4 — Mechanical near-duplicate leakage filter (provable, not heuristic)

Because an input is a 3-tuple `(float, cat, cat)`, near-duplication has an exact definition:

> A training point *contaminates* a test point iff **same `seam_result` AND same `severity` AND
> `|Δfailure_rate| < ε`** (e.g. ε = 0.03), OR the training rate falls in the reserved threshold band
> `(0.05, 0.20)`, OR the training rate equals a reserved exact value.

Assert this over the full training × test product as a build-time check (cheap — thousands × dozens).
Disjointness is then **provable by construction** (region exclusion) *and* **verified mechanically**
(the filter) — a materially stronger contamination guarantee than any text-based fine-tune can offer.
State it that way in the paper: it is a genuine methodological strength of the bounded task.

---

## Q4 — The honest CLAIM ceiling

The labels come from `route_for`, so the model can at most **distill the policy**. Two claims are
honest and publishable; a third would be a lie.

**Honest positive claim (if it generalizes):** *"A small model, fine-tuned on synthetic
policy-labeled decisions, replicates Keystone's bounded triage policy on-prem — including reading the
continuous `failure_rate` threshold and the signal interplay — and generalizes to held-out
rate-regions and precedence combos that the general 3B (OPT-A-01b, 4/6) got wrong."* This is a real
result: specialization closing a measured capability gap on the exact task where the general model
failed.

**Honest negative outcome (if it does not — equally publishable):** *"Even fine-tuned, the small
model fails on the held-out threshold band → the gap is capacity/architecture-bound, not a data or
prompt artifact; the transparent deterministic policy remains the correct default."* OPT-A-01b already
established the honest-negative discipline; this would complete it.

**The claim that would be dishonest — do NOT make it:** *"the model reasons better than the policy."*
Impossible by construction — the policy is the label source, so its accuracy ceiling is **100% = the
policy itself**. The model can approach the policy; it can never beat it.

**A limitation the verdict must carry (intellectual honesty).** Distilling a deterministic **5-leaf
tree** into an LLM is *methodologically* valid but *motivationally* soft: on this task the policy is
strictly the better artifact — deterministic, auditable, free, already shipping. A skeptic's fair
question is "why learn an if-else an LLM will only ever approximate?" The honest answer is that the
value is a **proof-of-concept for on-prem specialization** — evidence that a small local model *can*
be made reliable on a bounded decision where the general model was not — pointing at future decisions
where a clean policy is *not* available. The fine-tune demonstrates the *method*; it does not claim to
improve *this* decision. Framed that way it is honest; framed as "the fine-tuned agent decides better"
it is not.

---

## Q5 — Mechanics: Colab train → on-prem inference, base model, data-residency

**Pipeline (honest, end-to-end):** generate synthetic `(signals → route)` data locally from
`route_for` → fine-tune a small base with **LoRA/QLoRA on Colab** (free T4/16 GB is ample) →
**download the adapter/merged weights** → run inference **on-prem** via the same Ollama seam that
serves `qwen2.5:3b` today (`src/keystone/llm/inference/ollama.py:21`, custom GGUF/adapter via a
Modelfile).

**Base-model candidates** (align with the current Qwen stack; the task is a 3-way classifier, so
*small is correct*):

| Base | Fit | Note |
| --- | --- | --- |
| **Qwen2.5-0.5B / 1.5B-Instruct** | primary | matches the deployed family; 0.5–1.5B is more than enough for a 5-leaf rule; QLoRA (or even full FT at 0.5B) fits Colab trivially |
| Qwen2.5-3B-Instruct | matched control | *same* size as the general baseline — the cleanest "specialized vs general at equal capacity" comparison |
| Llama-3.2-1B / 3B-Instruct | alternative | if a non-Qwen cross-check is wanted |

Recommend **QLoRA** (memory-cheap, adapters are small to move) with **Qwen2.5-3B as the matched
control** so the headline compares specialized-3B vs general-3B at equal capacity — the fairest test
of the OPEN_QUESTIONS thesis.

**Data-residency framing (honest, and it holds).** The training data is **synthetic** — generated
from the policy over sampled abstract signals, carrying no PII and no real data, the same posture as
the rest of Keystone (`ADR-0024`, data-residency-preserving). Therefore the **training venue is
immaterial**: nothing sensitive crosses the trust boundary because nothing sensitive exists in the
training set. The residency guarantee is about **inference over real data**, and that stays **on-prem**
(identical to `qwen2.5:3b` today). Frame it precisely as: *"training happens on synthetic data, so
where it runs does not matter; deployment inference is local, so real data never leaves."* Do not
overclaim it as "trained on-prem" — it is "trained on synthetic data, deployed on-prem," which is the
honest and sufficient statement.

**Volume/compute reality:** for a 5-leaf rule with one continuous threshold, a few thousand
stratified examples and a short LoRA run suffice; this is a *small* experiment, not a compute-heavy
one. The bottleneck is protocol rigor (Q3), not GPU.

---

## Q6 — The honest verdict + the smallest next step

**Verdict: VIABLE, but only for a NARROW claim — technically sound, motivationally modest.**

- **Data volume** — not a constraint (unlimited synthetic labels).
- **Data diversity** — adequate on the *one* axis that carries real content (the continuous rate
  threshold + interplay/override precedence — the exact 3B failure surface); **thin** on the
  categoricals (a memorizable 5-leaf rule). Enough for a single well-scoped generalization claim,
  not for a "rich reasoning" claim.
- **Contamination protocol** — **sound and provable by construction** (Q3): region-exclusion on the
  continuous axis + held-out precedence cells + a frozen extended eval + a mechanical near-duplicate
  filter. This is a genuine strength of the tabular task and stronger than any text fine-tune's
  contamination story.
- **Claim ceiling** — distillation of the policy: the honest positive ("specialized small model
  reliably replicates the bounded decision the general 3B failed, on held-out cases") is legitimate;
  "reasons better than the policy" is impossible and forbidden; and the demonstration's *punch* is
  limited because the deterministic policy is already the better artifact.

**This is NOT a clean "build it" and NOT a clean "data too thin."** It is "viable for a narrow,
honest, well-guarded claim." So do **not** force the full build.

**Smallest honest next step — a one-run decisive spike (recommended), NOT the full build:**

1. Generate the stratified synthetic dataset **with the Q3 protocol** (held-out band + frozen
   extended eval + mechanical filter).
2. QLoRA-fine-tune **one** small base (Qwen2.5-1.5B, and/or 3B as the matched control) on Colab.
3. Measure **only** held-out **threshold-band** accuracy vs the general-3B baseline (**4/6** →
   the extended set).

That single run is decisive both ways: if specialization closes the held-out gap, the full build is
justified and scoped (triage first, protocol in hand); if it does not, that is the honest
capacity-bound negative that completes OPT-A-01b — either outcome is publishable. **Defense** stays a
later extension, only if triage answers positively (its 2-leaf rule is a weaker demonstration and has
no eval harness yet).

**Do not** proceed to a full multi-model, multi-decision fine-tuning build on the strength of this
probe — the narrow claim ceiling (Q4) does not warrant it until the one-run spike shows the held-out
gap actually closes.

---

## Sources (all read-only, cited file:line)

- Triage policy / ground-truth labeler: `src/keystone/agents/triage.py` — `route_for` (161-194),
  `ACTION_FLOOR` (107), `TriageSignals` (145-158), `Route` (100-102), `SeamClassification` (73-75),
  `FindingSeverity` (86-88).
- Held-out anti-parrot eval + in-distribution set: `scripts/triage_llm_eval.py` (48-97, 104-153).
- OPT-A-01b measured result (in-dist 6/6, held-out 4/6; the two stable failures):
  `docs/exec-plans/completed/opt-a-01b-triage-prompt-rescue.md` (30-48); `OPEN_QUESTIONS.md` (88-90,
  111-115).
- Defense policy (extension target): `src/keystone/agents/defense.py` — `choose_remediation`
  (98-110), `DEFENSE_FLOOR` (48), `DefenseSignals` (77-80).
- Model stack / on-prem inference seam: `src/keystone/llm/inference/ollama.py` (17-21, `qwen2.5:3b`).
- The fine-tuning frontier (roadmap, not built): `OPEN_QUESTIONS.md` (99-106).
- Data-residency principle: `ADR-0024` (`DECISIONS.md:832`); `CLAUDE.md` non-negotiables.
