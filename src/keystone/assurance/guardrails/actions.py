"""Custom NeMo Guardrails action shim (KS-0302).

Thin wrapper so the input rail can call the deterministic detector. The actual
logic (fully type-checked, unit-tested) lives in
`keystone.assurance.injection_patterns`; this file only adapts it to NeMo's
`@action` calling convention. The untyped third-party `@action` decorator is why
this one module carries a scoped mypy relaxation — the NeMo analog of ADR-0010.
"""

from __future__ import annotations

from typing import Any

from nemoguardrails.actions import action

from keystone.assurance.injection_patterns import is_data_field_injection


@action(name="check_data_field_injection")
async def check_data_field_injection(context: dict[str, Any] | None = None) -> bool:
    """Input-rail action: flag the user message as data-field injection."""
    user_message = (context or {}).get("user_message", "")
    return is_data_field_injection(str(user_message))
