"""Generate the FINETUNE-SPIKE-01 datasets — with the disjointness guarantee enforced.

Two subcommands, in the order the credibility depends on:

    uv run python scripts/finetune_gen_data.py heldout   # FREEZE the test set (run ONCE)
    uv run python scripts/finetune_gen_data.py train      # build training, disjoint from it

``heldout`` refuses to overwrite the committed frozen eval unless ``--force`` is passed — the
test set is immutable once frozen. ``train`` READS that committed file and asserts ZERO
contamination (:func:`keystone.finetune.protocol.contaminates_heldout`) before writing; if the
assertion fails the script exits non-zero and writes nothing — fix the generator, never the
protocol.

Outputs (committed, under ``src/keystone/finetune/data/``):
    heldout_eval.jsonl   structured eval cases (signals + policy label + in_band)
    train.jsonl          structured training cases (for inspection / the disjointness test)
    train_chat.jsonl     chat-format records the Colab QLoRA trainer consumes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from keystone.finetune.dataset import build_heldout, build_training, route_distribution
from keystone.finetune.protocol import (
    Case,
    contaminates_heldout,
    read_cases_jsonl,
    write_cases_jsonl,
    write_chat_jsonl,
)

DATA_DIR = (
    Path(__file__).resolve().parents[1] / "src" / "keystone" / "finetune" / "data"
)
HELDOUT_PATH = DATA_DIR / "heldout_eval.jsonl"
TRAIN_PATH = DATA_DIR / "train.jsonl"
TRAIN_CHAT_PATH = DATA_DIR / "train_chat.jsonl"


def _summary(label: str, cases: list[Case]) -> None:
    dist = route_distribution(cases)
    in_band = sum(1 for c in cases if c.in_band)
    print(f"{label}: {len(cases)} cases | routes {dist} | in reserved band: {in_band}")


def gen_heldout(force: bool) -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if HELDOUT_PATH.exists() and not force:
        print(
            f"REFUSING to overwrite the frozen held-out eval at {HELDOUT_PATH}.\n"
            "The test set is immutable once committed. Pass --force only if you truly intend "
            "to re-freeze it (and know the baseline must be re-measured)."
        )
        return 1
    cases = build_heldout()
    write_cases_jsonl(HELDOUT_PATH, cases)
    _summary("frozen held-out eval", cases)
    print(f"wrote {HELDOUT_PATH}")
    return 0


def gen_train() -> int:
    if not HELDOUT_PATH.exists():
        print(
            "No frozen held-out eval found — run `finetune_gen_data.py heldout` FIRST.\n"
            "Ordering is the credibility: the test set is frozen before training data exists."
        )
        return 1
    heldout = read_cases_jsonl(HELDOUT_PATH)
    train = build_training(heldout)

    # THE credibility assertion: not one training row may contaminate the held-out set.
    leaks = [c for c in train if contaminates_heldout(c.signals, heldout)]
    if leaks:
        print(
            f"CONTAMINATION: {len(leaks)} training rows leak the held-out set. Aborting."
        )
        for c in leaks[:5]:
            print(f"  {c.name}: {c.signals}")
        return 2

    write_cases_jsonl(TRAIN_PATH, train)
    write_chat_jsonl(TRAIN_CHAT_PATH, train)
    _summary("training set", train)
    print(
        f"disjointness OK: 0 of {len(train)} training rows contaminate the held-out set"
    )
    print(f"wrote {TRAIN_PATH}\nwrote {TRAIN_CHAT_PATH}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    hp = sub.add_parser("heldout", help="freeze the held-out eval (run once)")
    hp.add_argument(
        "--force", action="store_true", help="allow overwriting the frozen eval"
    )
    sub.add_parser("train", help="build training data disjoint from the frozen eval")
    args = parser.parse_args()

    if args.cmd == "heldout":
        return gen_heldout(force=bool(args.force))
    return gen_train()


if __name__ == "__main__":
    sys.exit(main())
