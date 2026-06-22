"""The canonical, REFERENCED Layer-2 assurance result (KS-0302 / KS-0304).

The Layer-1 milestone and the demo run-result REFERENCE the proven Layer-2 outcome by
identity rather than re-running Garak/Guardrails (the seam's "referenced, not re-run"
rule). This is the SINGLE SOURCE OF TRUTH for that referenced result: the
prompt-injection probe fired `before_fails`/`prompt_cap` unguarded and `after_fails`
once the NeMo Guardrails input rail was added.

The KS-0304 assurance loop produces this same outcome over its deterministic spine;
its tests assert the loop's `before_fails`/`after_fails` EQUAL this constant, so the
referenced numbers can't drift from what the loop actually does. Pure data — no LLM,
no network, no Garak run here.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ReferencedAssurance(BaseModel):
    """The referenced before/after of the Layer-2 find-and-patch (not re-run here)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    prompt_cap: int
    before_fails: int
    after_fails: int
    exploit_before: bool
    exploit_after: bool
    found_by: str
    patched_by: str

    @property
    def remediated(self) -> bool:
        """True iff the rail closed the hole: no fails and the exploit no longer fires."""
        return self.after_fails == 0 and not self.exploit_after


# The proven KS-0304 outcome: 10/12 prompt-injection probes exploited the unguarded
# agent (and the exploit fired); the NeMo Guardrails input rail took it to 0/12.
REFERENCED_ASSURANCE = ReferencedAssurance(
    prompt_cap=12,
    before_fails=10,
    after_fails=0,
    exploit_before=True,
    exploit_after=False,
    found_by="Garak (LLM01 prompt injection)",
    patched_by="NeMo Guardrails input rail",
)
