"""Verification rules for deterministic research-v3 preflight artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

from research_v3.engine.raw_data import sha256_file
from research_v3.engine.research_config import validate_research_only_config


REQUIRED_REPORT = {
    "candidate_strategy": None,
    "dry_run_authorized": False,
    "historical_strategy_trials_authorized": 0,
    "live_trading_authorized": False,
    "output_manifest_rows": 11,
    "pair_count": 11,
    "status": "infrastructure_preflight_passed_not_strategy_evidence",
}

CALENDAR_COLUMNS = {
    "pair",
    "date",
    "raw_candle_present",
    "raw_zero_volume",
    "contiguous_raw_candle_run",
    "trailing_90d_expected_slots",
    "trailing_90d_observed_slots",
    "trailing_90d_completeness_pct",
    "trailing_90d_zero_volume_pct_of_observed",
    "trailing_90d_median_daily_quote_usdc",
}


def _verify_report(output_dir: Path) -> dict[str, object]:
    """Load and validate the non-execution report controls."""
    report = json.loads((output_dir / "PREFLIGHT_REPORT.json").read_text(encoding="utf-8"))
    failures = {
        key: {"expected": expected, "actual": report.get(key)}
        for key, expected in REQUIRED_REPORT.items()
        if report.get(key) != expected
    }
    if failures:
        raise ValueError(f"Preflight report violates non-execution controls: {failures}")
    return report


def _verify_manifest(repository: Path, output_dir: Path, report: dict[str, object]) -> int:
    """Verify source provenance against the raw files present now."""

    with (output_dir / "RAW_SOURCE_MANIFEST.csv").open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    if len(manifest) != report["output_manifest_rows"]:
        raise ValueError("Manifest row count differs from preflight report")
    if len({row["pair"] for row in manifest}) != report["pair_count"]:
        raise ValueError("Manifest does not contain one unique entry per approved pair")
    for row in manifest:
        source = repository / row["source_file"]
        if not source.is_file():
            raise FileNotFoundError(f"Manifest source is missing: {source}")
        if sha256_file(source) != row["source_sha256"]:
            raise ValueError(f"Raw source hash changed since preflight: {row['source_file']}")
        if row["consumption_status"] != "consumed_audit_only":
            raise ValueError(f"Unexpected consumption status for {row['pair']}")
    return len(manifest)


def _verify_calendar(output_dir: Path, report: dict[str, object]) -> int:
    """Verify the gap-preserving raw calendar schema and simple invariants."""

    calendar = pd.read_csv(output_dir / "RAW_DAILY_CALENDAR.csv")
    if len(calendar) != report["output_calendar_rows"]:
        raise ValueError("Calendar row count differs from preflight report")
    if set(calendar.columns) != CALENDAR_COLUMNS:
        raise ValueError("Calendar schema differs from the frozen raw-fact schema")
    if calendar["pair"].nunique() != report["pair_count"]:
        raise ValueError("Calendar pair count differs from preflight report")
    if (calendar.loc[~calendar["raw_candle_present"], "contiguous_raw_candle_run"] != 0).any():
        raise ValueError("A missing raw candle has nonzero contiguous history")
    if (calendar["trailing_90d_observed_slots"] > calendar["trailing_90d_expected_slots"]).any():
        raise ValueError("Observed raw candles exceed expected calendar slots")
    return len(calendar)


def verify_preflight_bundle(
    repository: Path, output_dir: Path, config_path: Path
) -> dict[str, object]:
    """Verify that a preflight bundle has safe settings and current raw source hashes."""
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate_research_only_config(config)
    report = _verify_report(output_dir)
    manifest_rows = _verify_manifest(repository, output_dir, report)
    calendar_rows = _verify_calendar(output_dir, report)

    return {
        "calendar_rows": calendar_rows,
        "manifest_rows": manifest_rows,
        "pair_count": report["pair_count"],
        "status": "preflight_bundle_verified_not_strategy_evidence",
    }
