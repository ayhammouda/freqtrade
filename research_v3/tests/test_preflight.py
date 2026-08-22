# ruff: noqa: S101

import json
from pathlib import Path

import pandas as pd

from research_v3.engine.preflight_verification import verify_preflight_bundle
from research_v3.scripts.run_preflight import PAIR_CODES, run


def test_preflight_generates_consumed_audit_artifacts(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    data_dir = repository / "user_data" / "data" / "binance"
    data_dir.mkdir(parents=True)
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=3, freq="1D", tz="UTC"),
            "close": [100.0, 101.0, 102.0],
            "volume": [10.0, 20.0, 30.0],
        }
    )
    for pair in PAIR_CODES:
        frame.to_feather(data_dir / f"{pair}_USDC-1d.feather")
    config = {
        "status": "research_only_not_executable",
        "purpose": "infrastructure_preflight",
        "trading_mode": "spot",
        "margin_mode": None,
        "exchange": None,
        "candidate_strategy": None,
        "historical_strategy_trials_authorized": 0,
        "dry_run_authorized": False,
        "live_trading_authorized": False,
    }
    config_path = repository / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    report = run(repository, repository / "artifacts", config_path)

    assert report["status"] == "infrastructure_preflight_passed_not_strategy_evidence"
    assert report["output_manifest_rows"] == len(PAIR_CODES)
    calendar = pd.read_csv(repository / "artifacts" / "RAW_DAILY_CALENDAR.csv")
    manifest = pd.read_csv(repository / "artifacts" / "RAW_SOURCE_MANIFEST.csv")
    assert len(calendar) == len(PAIR_CODES) * 3
    assert set(manifest["consumption_status"]) == {"consumed_audit_only"}
    verification = verify_preflight_bundle(repository, repository / "artifacts", config_path)
    assert verification["status"] == "preflight_bundle_verified_not_strategy_evidence"
