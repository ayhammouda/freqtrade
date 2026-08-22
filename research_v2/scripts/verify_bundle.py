"""Verify internal consistency of the research-v2 local audit/stop bundle."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


EXPECTED_WARMUP = {
    "inner_selection": (177_235, 19_880),
    "selected_outer_archives": (4_004, 0),
    "grid_outer_diagnostic": (34_804, 0),
}
EXPECTED_SELECTED_INVALID = {
    "F1": 0,
    "F2": 0,
    "F3": 21,
    "F4": 23,
    "F5": 87,
    "F6": 88,
    "F7": 88,
    "F8": 88,
}
FORBIDDEN_CONFIG_KEY_PARTS = ("api_key", "apikey", "secret", "password", "token")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_data_coverage(repository: Path) -> list[str]:
    rows = read_csv(repository / "research_v2" / "DATA_COVERAGE.csv")
    if len(rows) != 66:
        raise RuntimeError(f"Expected 66 data rows, found {len(rows)}")
    keys = {(row["pair"], row["timeframe"]) for row in rows}
    if len(keys) != 66:
        raise RuntimeError("Pair/timeframe rows are not unique")
    if {row["consumption_status"] for row in rows} != {"consumed_research_data"}:
        raise RuntimeError("A data row is not marked consumed")
    for row in rows:
        source = repository / row["source_file"]
        actual = sha256_file(source)
        if actual != row["source_sha256"]:
            raise RuntimeError(f"Source hash mismatch: {source}")
    return ["data_coverage_rows=66", "data_source_hashes=66_ok"]


def check_warmup_audit(repository: Path) -> list[str]:
    rows = read_csv(repository / "research_v2" / "LEGACY_WARMUP_AUDIT.csv")
    for group, expected in EXPECTED_WARMUP.items():
        selected = [row for row in rows if row["archive_group"] == group]
        actual = (
            sum(int(row["trade_entries"]) for row in selected),
            sum(int(row["entries_without_600_contiguous_raw_4h_prefix"]) for row in selected),
        )
        if actual != expected:
            raise RuntimeError(f"Warm-up totals differ for {group}: {actual} != {expected}")
    inner = {row["fold"]: row for row in rows if row["archive_group"] == "inner_selection"}
    selected_invalid = {
        fold: int(row["selected_entries_without_600_contiguous_raw_4h_prefix"])
        for fold, row in inner.items()
    }
    if selected_invalid != EXPECTED_SELECTED_INVALID:
        raise RuntimeError(f"Selected inner violations differ: {selected_invalid}")
    return [
        "legacy_inner_entries=177235",
        "legacy_inner_warmup_violations=19880",
        "legacy_outer_entries_checked=38808",
        "legacy_outer_warmup_violations=0",
    ]


def check_strategy_hashes(repository: Path) -> list[str]:
    rows = read_csv(repository / "research_v2" / "STRATEGY_HASHES.csv")
    checked = 0
    for row in rows:
        if row["path"] == "N/A":
            continue
        path = repository / row["path"]
        if sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"Legacy strategy hash mismatch: {path}")
        checked += 1
    return [f"legacy_strategy_hashes={checked}_ok"]


def check_safe_config(repository: Path) -> list[str]:
    path = repository / "research_v2" / "configs" / "protocol_snapshot.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    for key in config:
        normalized = key.lower()
        if any(part in normalized for part in FORBIDDEN_CONFIG_KEY_PARTS):
            raise RuntimeError(f"Credential-like field in safe config: {key}")
    if config["live_trading_authorized"] or config["dry_run_authorized"]:
        raise RuntimeError("Trading or dry-run authorization unexpectedly enabled")
    if config["historical_trial_budget"] != 0:
        raise RuntimeError("Historical trial budget is not zero")
    return ["safe_config_credentials=none", "strategy_and_trading_authorization=false"]


def check_documents(repository: Path) -> list[str]:
    protocol = (repository / "research_v2" / "PROTOCOL.md").read_text(encoding="utf-8")
    report = (repository / "research_v2" / "FINAL_REPORT.md").read_text(encoding="utf-8")
    required_verdict = "Research invalid because implementation or data problems remain"
    if required_verdict not in protocol or not report.startswith(f"# {required_verdict}"):
        raise RuntimeError("Controlling verdict is absent or inconsistent")
    if "Historical strategy/parameter trial budget: **0**" not in protocol:
        raise RuntimeError("Zero historical budget is absent")
    return ["verdict_consistency=ok", "historical_trial_budget=0"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    repository = args.repository.resolve()

    lines = ["research_v2 bundle verification"]
    lines.extend(check_data_coverage(repository))
    lines.extend(check_warmup_audit(repository))
    lines.extend(check_strategy_hashes(repository))
    lines.extend(check_safe_config(repository))
    lines.extend(check_documents(repository))
    lines.append("status=pass")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
