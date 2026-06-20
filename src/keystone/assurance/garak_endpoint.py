"""Guarded-agent HTTP endpoint for the Garak re-scan (KS-0302).

Garak runs in its own isolated venv (ADR-0003) and cannot import keystone or
nemoguardrails, so the guarded re-scan can't use the KS-0303 `function` target.
Instead this serves the GUARDED brain over HTTP (in our venv, with the rail) and
Garak's `rest` generator probes it. Same vulnerable model brain as KS-0303, but
the NeMo Guardrails input rail vets each prompt first: injection prompts are
refused before the model sees them, so the probe that fired 10/12 unguarded now
comes back clean.

Pure scaffolding for the slow live test / fixture refresh; nothing here runs in
the fast gate.
"""

from __future__ import annotations

import json
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from keystone.llm.inference import OllamaBackend, ToolCallingBackend, complete

from .garak_probe import (
    CURATED_PROBES,
    GARAK_PROBE_SYSTEM_PROMPT,
    ScanConfig,
    run_scan,
)
from .guard import GUARD_REFUSAL, is_blocked


def guarded_brain(prompt: str, *, backend: Any = None) -> str:
    """The guarded vulnerable brain: rail-vet the prompt, then (maybe) the model.

    If the input rail flags the prompt as data-field injection it is REFUSED
    (the model is never called); otherwise the same vulnerable completion as
    KS-0303 runs — so on clean prompts behaviour is unchanged.
    """
    if is_blocked(prompt):
        return GUARD_REFUSAL
    return complete(
        prompt, system=GARAK_PROBE_SYSTEM_PROMPT, backend=backend or OllamaBackend()
    )


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802  # http.server's required method name
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        output = guarded_brain(str(body.get("prompt", "")), backend=self.server.backend)  # type: ignore[attr-defined]
        payload = json.dumps({"output": output}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args: Any) -> None:  # silence per-request logging
        return


@contextmanager
def guarded_agent_endpoint(backend: ToolCallingBackend | None = None) -> Iterator[str]:
    """Serve the guarded brain on a free localhost port; yield its URI."""
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    server.backend = backend  # type: ignore[attr-defined]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def scan_guarded_agent(
    *,
    report_prefix: str,
    probes: Any = CURATED_PROBES,
    prompt_cap: int | None = 12,
    backend: ToolCallingBackend | None = None,
) -> Path:
    """Run the curated probe subset against the GUARDED agent via Garak `rest`.

    Stands up the guarded HTTP endpoint, points Garak's REST generator at it, runs
    the same curated probe subset as the unguarded KS-0303 scan, and returns the
    JSONL report path. The rail should make this report clean.
    """
    with guarded_agent_endpoint(backend) as uri:
        rest_cfg = {
            "rest": {
                "RestGenerator": {
                    "name": "keystone-guarded-agent",
                    "uri": uri,
                    "method": "post",
                    "headers": {"Content-Type": "application/json"},
                    "req_template_json_object": {"prompt": "$INPUT"},
                    "response_json": True,
                    "response_json_field": "output",
                }
            }
        }
        cfg_file = Path(tempfile.mkdtemp()) / "rest_generator.json"
        cfg_file.write_text(json.dumps(rest_cfg), encoding="utf-8")
        config = ScanConfig(
            target_type="rest",
            target_name="",
            report_prefix=report_prefix,
            probes=probes,
            prompt_cap=prompt_cap,
            generator_option_file=str(cfg_file),
        )
        return run_scan(config)
