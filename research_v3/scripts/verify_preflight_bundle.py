"""Verify a research-v3 preflight bundle without executing a strategy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_v3.engine.preflight_verification import verify_preflight_bundle


def main() -> int:
    """Run verification and write a deterministic audit receipt."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    report = verify_preflight_bundle(args.repository.resolve(), args.output_dir, args.config)
    receipt = args.output_dir / "PREFLIGHT_VERIFICATION.json"
    receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
