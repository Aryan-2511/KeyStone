# FINETUNE-SPIKE-01 — a decisive QLoRA specialization probe for triage routing

**Status:** Phase 1 complete (repo side built + frozen) · Phase 2 (Colab training) is the user's
step · Phase 3 (the decisive measurement) runs in-repo once the adapter returns.
**Mode of claim:** a narrow **distillation / capacity** probe — honest either way it lands.

**The question.** `docs/paper/finetune_feasibility.md` returned *VIABLE-but-NARROW*. This spike
runs the one decisive experiment it recommended: does task-**specialization** let a small on-prem
model make the bounded triage decision the **general 3B** failed on (OPT-A-01b held-out: **4/6**)?

**What this is — and is not.** The training labels come from the transparent policy
(`route_for`, `src/keystone/agents/triage.py:161-194`), so a fine-tuned model can at most
**distill** the policy — never "reason better than" it (the policy is the label ceiling). This is
**not** "a fine-tuned agent brain." It is a capacity/specialization probe, framed exactly that way.
The two honest outcomes are stated up front, before any number exists:

- **Specialized > general on held-out** → a narrow, honest *on-prem specialization proof-of-concept*
  (a small local model reaches the decision the general model missed).
- **Specialized ≈ general (still fails held-out)** → the *capacity-bound* finding is **completed**:
  even fine-tuned, small models can't — the gap is neither prompt nor specialization, it is capacity.

Both are valid and publishable. We go in indifferent to which lands.

---

## The credibility guarantee (why this result will be worth anything)

A fine-tune "accuracy" is meaningless unless the test set is provably disjoint from training. The
protocol (from `finetune_feasibility.md` Q3) is enforced mechanically, and the low-dimensional task
makes disjointness **provable by construction** — a genuine strength over text fine-tuning.

1. **Freeze-first ordering.** The held-out eval was generated and **committed before any training
   data existed** (git history: the "FREEZE the held-out eval" commit precedes the training commit).
   Nothing downstream can leak into it.
2. **Reserved threshold band.** `route_for`'s only learnable continuous boundary is the 0.10 action
   floor. The open band **(0.05, 0.20)** bracketing it is reserved **test-only**; training samples
   `failure_rate` only from `[0, 0.05] ∪ [0.20, 1.0]`. A memorizer cannot classify an in-band point
   it never saw — only threshold-learning can. **45 of 48** held-out cases sit in this band (the
   exact axis general 3B failed on — it read 0.06 as "above 0.10").
3. **Mechanical near-duplicate filter.** For held-out points outside the band (the OPT-A-01b
   anti-parrot exact values 0.25 / 0.30 / 0.45), a training row is contaminating iff **same
   `seam_result` ∧ same `severity` ∧ |Δrate| < 0.03**. Enforced by
   `keystone.finetune.protocol.contaminates_heldout`.
4. **Asserted, in a committed test.** `tests/test_finetune_disjointness.py` asserts **zero**
   training rows contaminate the frozen eval, every label equals `route_for`, and the committed
   artifacts reproduce the deterministic generator. If it ever fails, fix the generator — never the
   assertion or the protocol.

---

## Phase 1 — what is in the repo (built, frozen, green)

| Artifact | Path | What it is |
| --- | --- | --- |
| Contamination protocol | `src/keystone/finetune/protocol.py` | reserved band, near-dup metric, `contaminates_heldout`, JSONL/chat serialization |
| Deterministic builders | `src/keystone/finetune/dataset.py` | `build_heldout` (48 cases), `build_training` (route-balanced, disjoint) |
| **Frozen held-out eval** | `src/keystone/finetune/data/heldout_eval.jsonl` | **48 cases**, 45 in the reserved band; each labeled by `route_for` |
| Training set (structured) | `src/keystone/finetune/data/train.jsonl` | **465 cases**, balanced 155 / 155 / 155 across the 3 routes, 0 in-band |
| Training set (chat) | `…/data/train_chat.jsonl` *(generated, gitignored)* | `make finetune-data` emits it from `train.jsonl`; chat format QLoRA consumes (system+user = the live eval's exact prompt). Not committed — it embeds the full system prompt ×465 (~1.3 MB); reproducible on demand. |
| Generator CLI | `scripts/finetune_gen_data.py` | `heldout` (freeze-once) / `train` (disjoint, asserts) |
| Eval harness | `scripts/finetune_eval.py` | runs the frozen eval vs any configured Ollama model |
| Disjointness test | `tests/test_finetune_disjointness.py` | the credibility assertions (9 tests) |
| Colab trainer | `colab/finetune_triage_qlora.py` | QLoRA on Colab (outside the gate-scanned dirs; its deps are not repo deps) |

**Regenerate (optional, deterministic — produces byte-identical files):**
```
uv run python scripts/finetune_gen_data.py heldout --force   # only to re-freeze (re-measure baseline!)
uv run python scripts/finetune_gen_data.py train             # asserts zero contamination
```

### The general-3B baseline (the number to beat)

Measured 2026-07-13 with the SAME harness Phase 3 uses, on the frozen 48-case held-out set,
against `qwen2.5:3b` (the OPT-A-01b model), 3 calls/case:

> **Overall: 37/48 = 77%.  Reserved-band: 35/45 = 78%.**
> Per route: **escalate 22/22 (100%)**, **accept 13/19 (68%)**, **remediate 2/7 (29%)**.

The OPT-A-01b 6-case held-out baseline was **4/6 (67%)**; this extends it to 48 band-concentrated
cases — a sharper, harder measure of the same capability. The **failure pattern is exactly the
OPT-A-01b capacity story, at higher resolution**, and it tells the fine-tune precisely what it must
fix:

- **`remediate` collapses (2/7).** `clean / LOW @ 0.12, 0.15, 0.18` are all called *accept* — the
  model applies "low rate ⇒ contained" even on a **clean** seam **above** the 0.10 floor (the
  OPT-A-01b "misapplied contained to a clean seam" error, reproduced).
- **Near-floor rates are misread.** `clean / MED @ 0.06, 0.08` → *remediate*, and `open / {LOW,MED}
  @ 0.06, 0.08` → *escalate*, when all four are **below** the floor and should be *accept*. The
  model reads 0.06 / 0.08 as if above 0.10 — the exact numeric misread OPT-A-01b flagged.
- **`escalate` is perfect (22/22)** because HIGH-severity and open-above-floor both escalate — the
  model over-escalates, which happens to be right for these cells.

So the specialized model must (a) learn the **clean-above-floor ⇒ remediate** distinction and
(b) read the **sub-0.10 threshold** correctly. That is the whole point of the held-out band.

---

## Phase 2 — Colab training (the user runs this)

Claude Code cannot run Colab; this phase is yours. It is a *small* experiment (465 examples, a
5-leaf rule) — minutes on a free T4, not hours.

1. **Open Colab** → new notebook → Runtime → Change runtime type → **T4 GPU**.
2. **Produce the chat dataset** locally with `make finetune-data` (writes the gitignored
   `src/keystone/finetune/data/train_chat.jsonl`), then **upload** it into the Colab session
   (Files pane) so it sits next to the notebook as `train_chat.jsonl`.
3. **Paste** `colab/finetune_triage_qlora.py` — either run it whole, or cell-by-cell using the
   `# --- Cell N` markers. Cell 1 installs deps; Cell 2 is config; `main()` trains.
   - **Base model:** default is **`Qwen/Qwen2.5-3B-Instruct`** — the **matched control** (specialized-3B
     vs general-3B at equal capacity, the cleanest claim). Optionally also run
     `Qwen2.5-1.5B-Instruct` / `-0.5B-Instruct` as a cheap cross-check (the task is tiny).
4. **Export for on-prem Ollama.** After `main()` finishes you have `keystone-triage-ft-merged/`.
   Convert to GGUF and make it an Ollama model:
   - convert with `llama.cpp`'s `convert_hf_to_gguf.py` (a Colab cell) → `keystone-triage-ft.gguf`;
   - download the `.gguf`;
   - on-prem, create a `Modelfile` (`FROM ./keystone-triage-ft.gguf`) and
     `ollama create keystone-triage-ft -f Modelfile`.
   (Any HF→GGUF→Ollama path is fine; the only requirement is that `ollama run keystone-triage-ft`
   works locally.)
5. **Return** the adapter/GGUF so Phase 3 can measure it. **Stop here and hand back.**

**Data-residency framing (keep it precise):** the uploaded data is **synthetic** (generated from
the policy over abstract signals — no PII), so training on Colab crosses no trust boundary; only
*inference over real data* must stay local, and it does (on-prem Ollama). Say "**trained on
synthetic data, deployed on-prem**," never "trained on-prem."

---

## Phase 3 — the decisive measurement (in-repo, after the adapter returns)

Serve the fine-tuned model under its Ollama name and run the **same frozen eval, same harness** as
the baseline:

```
KEYSTONE_OLLAMA_MODEL=keystone-triage-ft uv run python scripts/finetune_eval.py --repeats 3 --verbose
```

Report **specialized-3B held-out accuracy vs the general-3B baseline**, with special attention to
**reserved-band accuracy** (the threshold axis). Then record the honest verdict — specialization
proof-of-concept **or** capacity-bound completion — and update `DECISIONS.md`, `OPEN_QUESTIONS.md`,
`ROADMAP.md`, and `finetune_feasibility.md` with the outcome.

> **Result (measured 2026-07-18; Unsloth QLoRA, Qwen2.5-3B-Instruct matched control, 1 epoch,
> fp16/T4, q8_0 GGUF, on-prem Ollama; same frozen 48-case harness, 3 calls/case):**
>
> | | **specialized-3B** | general-3B baseline |
> | --- | --- | --- |
> | Overall | **37/48 = 77%** | 37/48 = 77% |
> | Reserved-band | **34/45 = 76%** | 35/45 = 78% |
> | route `remediate` | 4/7 (57%) | 2/7 (29%) |
> | route `accept` | 13/19 (68%) | 13/19 (68%) |
> | route `escalate` | 20/22 (91%) | 22/22 (100%) |
>
> **Verdict: CAPACITY-BOUND (the finding is completed, not a proof-of-concept).** Specialization
> did **not** close the gap: overall is identical (77%) and the reserved band is *marginally worse*
> (76% vs 78%). The fine-tune only **reshuffled** the errors — it learned the *clean-above-floor ⇒
> remediate* distinction for MEDIUM severity (`remediate` 4/7 vs 2/7) but **still misreads the
> sub-0.10 threshold** (`clean/LOW @ 0.12,0.15,0.18` → accept, wrong) and **newly regressed
> `escalate`** (`open/LOW @ 0.12,0.18` → accept; 20/22 vs a perfect 22/22). Both prompting (OPT-A-01b)
> **and** task-specialization now fail on the same held-out band → the ceiling is **capacity, not
> method**. Honest framing: *a specialized small on-prem 3B model does **not** reliably replicate the
> bounded routing decision general 3B got wrong on held-out cases.*
>
> **Inference conditions (matched to the baseline, not the Unsloth defaults).** Unsloth's exported
> Modelfile shipped `temperature 1.5` + `min_p 0.1` + a stock-Qwen `SYSTEM` prompt — all three would
> have corrupted the comparison. The eval harness supplies its **own** system prompt (`TRIAGE_SYSTEM`)
> and the baseline was measured against **stock `qwen2.5:3b`, which pins no sampling params** (Ollama
> defaults) via a `complete()` path that sends no `options.temperature`. So the committed Modelfile
> **removes** `SYSTEM` (harness wins) and **strips** `temperature`/`min_p` so the fine-tune samples
> under the **same Ollama defaults the baseline used** — only the *model* differs. (Setting
> `temperature 0` as first assumed would have been an *unmatched* comparison favoring the fine-tune;
> the baseline was never deterministic. See `DECISIONS.md`.) The eval is therefore mildly
> non-deterministic run-to-run, exactly as the baseline was; the ≈-parity conclusion is robust to
> that noise (the fine-tune is not *near* clearly beating 78%).

---

## Honesty guardrails (this defines a paper claim)

- The held-out set is **frozen before training data exists**; the disjointness assertion **passes**
  (zero contamination) — otherwise the result is worthless. Non-negotiable.
- Claim ceiling: honest = *"a specialized small on-prem model {does / does not} replicate the bounded
  decision general 3B failed on, on held-out cases."* **Forbidden:** "reasons better than the policy"
  (impossible — the policy is the label ceiling) and "a fine-tuned agent brain" (oversells a narrow
  distillation probe).
- Report the result **whichever way it lands** — a negative is a valid, valuable outcome. Do **not**
  tune the dataset or eval to flatter the model's number.
