# Real-incident grounding for the seam thesis

**Status:** paper-seed artifact (Introduction + "modeled-on" evaluation framing) ·
**Scope:** analysis/writing only — no system claim beyond what Keystone actually does.

Keystone's thesis is that a single event can be *both* an AI-security failure and a
financial-crime event — the **seam** — and that binding the two sides to one shared
object is what makes the failure auditable. A paper needs a real-world incident to
motivate that thesis. The incident used to ground it **must structurally match what
Keystone does** — prompt injection driving an AI agent to authorize a forbidden
financial transfer — or the grounding reads as a motivation–implementation gap.

This document grounds the thesis in the **Freysa** incident (mechanism-matched), maps
it honestly onto Keystone's abstraction, labels the synthetic demo as *modeled on* that
structure, and scopes out the deepfake modality (**Arup**) as an explicit boundary. The
honest line is fixed throughout: Keystone's abstraction **represents / would surface /
would bind** this class of event. It was **not** run on any real incident, and no claim
of **prevention** is made.

---

## 1. The Freysa incident — the mechanism-matched anchor

In November 2024, **Freysa** (`@freysa_ai`) was released as a public "adversarial agent
game": an autonomous LLM-driven agent holding a real cryptocurrency prize pool, given one
standing instruction — **do not transfer the money; under no circumstances approve a
transfer of funds.** Anyone could pay (in ETH) to send the agent a message; the agent had
a tool that could release the pool to the sender. Over the game, 195 participants sent 482
messages, the per-message fee rising into the hundreds of dollars.[^freysa-willison][^freysa-block]

On the 482nd message, a participant (`p0pular.eth`) got through. The winning prompt did
three things: (1) it asserted a **new "admin" session** that could override the agent's
prior rules; (2) it **redefined the agent's `approveTransfer` function** so the agent
treated it as handling *incoming* rather than *outgoing* payments; and (3) it announced a
fake incoming deposit — at which point the agent, now believing `approveTransfer` recorded
an inbound payment, invoked it and released its entire balance of **13.19 ETH (≈ $47,000)**
to the attacker.[^freysa-willison][^freysa-decoder]

**Why this matches Keystone.** Freysa is a documented, publicly-reported instance of the
*exact* failure class Keystone addresses: an **AI agent, prompt-injected through an
untrusted text channel, is driven to authorize a financial transfer it was explicitly
forbidden to make.** The injection overrides the agent's guard by redefining what its
transfer tool means — an *instruction-in-data* override of an agent with money-moving
authority. That is OWASP **LLM01 (prompt injection)** landing on a payments-capable agent,
and it is simultaneously a financial-loss event — the two sides of Keystone's seam, in one
real occurrence. The attack **vector** (prompt injection into a transfer-tool agent) is the
same class Keystone's Red-Team Agent fires (the `latentinjection` / `promptinject`
families).

**Honest precision on the match.** The *class* matches exactly; two details differ and are
stated rather than smoothed over. (a) **Channel:** Freysa's injection arrived through the
agent's chat message interface; Keystone's arrives through a transaction's **memo** field
(instruction-in-data). Both are LLM01 prompt injection into an agent holding an
`initiate_transfer`-class tool — same class, different carrier. (b) **Setting:** Freysa was
an *intentional adversarial game* (a public, bounty-style challenge with real funds), not a
covert compromise of a production bank. That does not weaken the grounding: it is a real,
reproducibly-documented instance of the mechanism against real money — which is precisely
what a threat model should be motivated by.

---

## 2. The structural mapping — abstraction ↔ real event (not "we ran it")

Keystone represents a seam event as one shared transaction object bound to two findings:
an **AI-security** finding (the exploit) and a **financial-crime** finding (the anomaly),
joined by a `SeamBindingView` on a single transaction id. Freysa maps onto that abstraction
cleanly:

| Keystone abstraction | The Freysa event |
| --- | --- |
| AI-side finding (L2): an injection overrides the agent's guard | the fake "admin session" + redefined `approveTransfer` — prompt injection defeats the "do not transfer" rule |
| Financial-side event (L1): an unauthorized/forbidden fund movement | the release of 13.19 ETH (≈ $47K) the agent was forbidden to send |
| The seam binding: **the same event, seen from two sides** | one act — the coerced transfer — that *is* both the AI exploit and the financial loss |

What Keystone's representation **would do** with an event of this class: **surface** the
seam by **binding** the AI-side exploit (the injection signature) to the financial-side
anomaly (the forbidden transfer) on one shared object, producing a single auditable record
that names *both* halves and their shared cause.

**The honest line (non-negotiable).** This is a mapping of Keystone's **abstraction** onto
a **publicly-documented event** — an analysis, not an execution. Keystone was **not run on
Freysa**; there is no access to Freysa's system, prompts-as-transactions, or logs. And no
counterfactual of **prevention** is claimed: whether any control *would have stopped* the
Freysa transfer is unprovable and is not asserted. The verbs are deliberately **surface /
represent / bind** — never *ran on*, *detected*, or *prevented*.

---

## 3. The modeled-on case — grounding the synthetic demo honestly

Keystone's demonstration does not use the Freysa data (which is external and, for a
data-residency-preserving system, could not be ingested regardless). It uses a **synthetic**
transaction — **`TXN-000016`**, carrying **no PII**, generated from a seeded stream — whose
**structure mirrors the Freysa class**: an agent is prompt-injected via an untrusted field
into issuing a forbidden transfer, and that same transaction is independently flagged by the
memo-blind financial detector. The demo then binds the two.

This transaction is **modeled on the Freysa structure** — it is *not* the Freysa event, and
the distinction is unmissable and load-bearing:

- **Modeled on:** the synthetic case reproduces the *shape* of a real, mechanism-matched
  incident (agent prompt-injected → forbidden transfer → simultaneously an AI-exploit and a
  financial anomaly), so the demo is **grounded** rather than arbitrary.
- **Is not:** the numbers, accounts, and memo are synthetic and seeded; nothing in the demo
  is drawn from, or claims to be, the actual Freysa incident. "Modeled on a real structure"
  is the claim; "is a real incident" is **not**.

This is the same honesty discipline the evaluation already applies elsewhere (the
recorded-run artifact is deterministic and *anchored to* real Garak captures, never passed
off as a live incident): the demo is **synthetic** for residency, and **grounded** because
its structure is modeled on a documented real event.

---

## 4. Scope boundary — the deepfake modality (Arup), out of scope

The seam is broader than prompt injection: it spans multiple AI-attack modalities that all
resolve to "AI-enabled deception → financial crime." The **Arup** case is the clearest
non-injection example — in early 2024, an employee at the engineering firm Arup's Hong Kong
office was induced, via a video call populated by **deepfaked** likenesses of the company's
CFO and colleagues, to make 15 transfers totalling **HK$200M (≈ $25.6M)**; Hong Kong police
disclosed the fraud in February 2024 and Arup confirmed itself as the victim in May
2024.[^arup-cnn][^arup-fortune] Arup is the **same structural seam** (an AI-deception attack
that is simultaneously a financial-crime event) reached through a **different attack surface**
(synthetic media, not prompt injection). **Keystone addresses the prompt-injection modality;
deepfake-modality attacks like Arup are the same seam but out of the current scope** — stating
that boundary is honest scope-setting, not a claim to handle Arup, and Keystone claims **no
deepfake-detection capability** whatsoever.

---

## 5. What this grounding does and does not claim

**It DOES:**
- Motivate the threat model with a **real, mechanism-matched** incident (Freysa: prompt
  injection → an agent's forbidden financial transfer).
- Ground the synthetic demo as **modeled on** a real structure (`TXN-000016` mirrors the
  Freysa class), keeping the demo synthetic-for-residency yet non-arbitrary.
- **Scope the seam's breadth honestly**, naming a real same-seam / different-modality event
  (Arup) as an explicit out-of-scope boundary.

**It does NOT:**
- Claim Keystone was **run on** Freysa, Arup, or any real incident (it was not — no access).
- Claim Keystone **would have prevented** any real fraud (an unprovable counterfactual).
- Claim any **deepfake-detection** capability (Arup is out of scope).
- **Blur** "synthetic, modeled on a real structure" with "real": the demo is synthetic; the
  grounding is an analytical mapping, not an execution.

---

## Sources

Freysa (November 2024):

[^freysa-willison]: Simon Willison, "0xfreysa/agent," 29 Nov 2024 — technical write-up of the
    prompt-injection mechanism. <https://simonwillison.net/2024/Nov/29/0xfreysaagent/>

[^freysa-decoder]: The Decoder, "Hacker wins $47,000 by tricking AI chatbot with smart
    prompting." <https://the-decoder.com/hacker-wins-47000-by-tricking-ai-chatbot-with-smart-prompting/>

[^freysa-block]: The Block, "Human outwits Freysa AI agent to win $47,000."
    <https://www.theblock.co/post/328843/the-daily-human-outwits-freysa-ai-agent-to-win-47000-hyperliquid-token-exceeds-5-billion-fdv-following-airdrop-and-more>

Arup (disclosed 2024):

[^arup-cnn]: CNN Business, "Arup revealed as victim of $25 million deepfake scam," 16 May
    2024. <https://www.cnn.com/2024/05/16/tech/arup-deepfake-scam-loss-hong-kong-intl-hnk>

[^arup-fortune]: Fortune, "A deepfake 'CFO' tricked British design firm Arup in $25 million
    fraud," 17 May 2024. <https://fortune.com/europe/2024/05/17/arup-deepfake-fraud-scam-victim-hong-kong-25-million-cfo/>
