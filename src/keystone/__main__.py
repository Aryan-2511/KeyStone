"""Console entry point stub.

Phase 0 placeholder so the `keystone` script resolves. Real CLI/demo wiring
lands in a later phase; for now this just reports the version.
"""

from keystone import __version__


def main() -> None:
    print(f"keystone {__version__}")


if __name__ == "__main__":
    main()
