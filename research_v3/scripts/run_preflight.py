"""Generate deterministic, strategy-neutral research-v3 preflight artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd

from research_v3.engine.raw_data import (
    build_daily_raw_calendar,
    sha256_file,
    utc_index,
    verify_freqtrade_loader_provenance,
)
from research_v3.engine.research_config import validate_research_only_config


PAIR_CODES = ("BTC", "ETH", "TRX", "BNB", "LTC", "XRP", "SOL", "BCH", "XLM", "DOT", "ADA")


def source_path(repository: Path, pair: str) -> Path:
    """Resolve one approved raw daily source path."""
    return repository / "user_data" / "data" / "binance" / f"{pair}_USDC-1d.feather"


def run(repository: Path, output_dir: Path, config_path: Path) -> dict[str, object]:
    """Build audit-only artifacts from raw daily candles and safe configuration."""
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate_research_only_config(config)
    calendars: list[pd.DataFrame] = []
    loader_checks: dict[str, dict[str, int]] = {}
    manifest: list[dict[str, object]] = []
    for pair in PAIR_CODES:
        path = source_path(repository, pair)
        if not path.is_file():
            raise FileNotFoundError(f"Missing approved source: {path}")
        frame = pd.read_feather(path, columns=["date", "close", "volume"])
        dates = utc_index(frame["date"])
        loader_checks[f"{pair}/USDC"] = verify_freqtrade_loader_provenance(
            path.parent, f"{pair}/USDC", "1d", dates
        )
        calendar = build_daily_raw_calendar(frame)
        calendar.insert(0, "pair", f"{pair}/USDC")
        calendars.append(calendar)
        manifest.append(
            {
                "pair": f"{pair}/USDC",
                "timeframe": "1d",
                "source_file": path.relative_to(repository).as_posix(),
                "source_sha256": sha256_file(path),
                "raw_start_utc": dates[0].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "raw_end_utc": dates[-1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "raw_observed_candles": len(frame),
                "consumption_status": "consumed_audit_only",
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    calendar_output = output_dir / "RAW_DAILY_CALENDAR.csv"
    manifest_output = output_dir / "RAW_SOURCE_MANIFEST.csv"
    report_output = output_dir / "PREFLIGHT_REPORT.json"
    full_calendar = pd.concat(calendars, ignore_index=True)
    full_calendar.to_csv(calendar_output, index=False)
    with manifest_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)
    report = {
        "candidate_strategy": None,
        "dry_run_authorized": False,
        "historical_strategy_trials_authorized": 0,
        "live_trading_authorized": False,
        "freqtrade_loader_provenance": loader_checks,
        "output_calendar_rows": len(full_calendar),
        "output_manifest_rows": len(manifest),
        "pair_count": len(PAIR_CODES),
        "status": "infrastructure_preflight_passed_not_strategy_evidence",
    }
    report_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.repository.resolve(), args.output_dir, args.config)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
