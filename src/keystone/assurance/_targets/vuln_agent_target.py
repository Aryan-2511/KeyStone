"""Standalone Garak function target (KS-0303) — NOT imported by keystone.

Garak runs in its own ISOLATED venv (ADR-0003) and cannot import `keystone`, so
this target is intentionally stdlib-only and lives in its own directory (no
package `__init__`) that the scan runner puts on `PYTHONPATH`. Garak imports it as
the top-level module `vuln_agent_target` via its `function` generator.

It exposes the mock agent's instruction-in-data flaw to Garak: it sends Garak's
prompt to the configured Ollama model under a VULNERABLE system prompt (passed in
`KEYSTONE_GARAK_SYSTEM`) and returns the model's text, which Garak's latent-
injection detectors evaluate. This is the same architectural flaw as the KS-0301
agent (trusting instructions embedded in input data), generalized so Garak's
generic injection probes exercise it.
"""

from __future__ import annotations

import json
import os
import urllib.request

_TIMEOUT = 60.0


def generate(prompt: str, **kwargs: object) -> list[str]:
    """Garak `function` entry point: one prompt -> one model completion."""
    host = os.environ.get("KEYSTONE_OLLAMA_HOST", "http://localhost:11434")
    model = os.environ.get("KEYSTONE_OLLAMA_MODEL", "qwen2.5:3b")
    system = os.environ.get("KEYSTONE_GARAK_SYSTEM", "")
    if not host.startswith(("http://", "https://")):
        raise ValueError(f"refusing non-http Ollama host: {host!r}")

    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0},
        }
    ).encode("utf-8")
    request = urllib.request.Request(  # noqa: S310  # scheme-guarded local Ollama endpoint
        f"{host}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=_TIMEOUT) as response:  # noqa: S310  # scheme-guarded local Ollama endpoint
        payload = json.loads(response.read().decode("utf-8"))
    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    content = message.get("content", "") if isinstance(message, dict) else ""
    return [str(content)]
