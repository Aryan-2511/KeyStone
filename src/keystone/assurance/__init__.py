"""Assurance / red-team — drives Garak as an external subprocess.

Garak itself is an isolated CLI tool, not a dependency (ADR-0003); this layer is
the in-repo driver that invokes it and collects reports. The core must not
depend on it. Empty until Phase 3.
"""
