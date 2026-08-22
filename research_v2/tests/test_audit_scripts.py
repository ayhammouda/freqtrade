# ruff: noqa: S101

from pathlib import Path

import numpy as np
import pandas as pd

from research_v2.scripts.audit_data_coverage import audit_file, largest_gap
from research_v2.scripts.audit_legacy_warmup import has_contiguous_prefix
from research_v2.scripts.freeze_hashes import manifest_lines, verify


def test_largest_gap_counts_missing_slots() -> None:
    dates = pd.Series(pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-05"], utc=True))

    gap = largest_gap(dates, pd.Timedelta(days=1))

    assert gap.missing_candles == 2
    assert gap.start == pd.Timestamp("2026-01-02", tz="UTC")
    assert gap.end == pd.Timestamp("2026-01-05", tz="UTC")


def test_raw_prefix_requires_exactly_contiguous_4h_rows() -> None:
    dates = pd.date_range("2025-01-01", periods=601, freq="4h", tz="UTC")
    entry = dates[-1]

    raw_ns = dates[:-1].as_unit("ns").asi8.copy()
    assert has_contiguous_prefix(raw_ns, entry)

    missing = np.delete(raw_ns, 300)
    assert not has_contiguous_prefix(missing, entry)


def test_daily_audit_records_raw_gap_and_consumed_status(tmp_path: Path) -> None:
    repository = tmp_path
    source = repository / "user_data" / "data" / "binance" / "BTC_USDC-1d.feather"
    source.parent.mkdir(parents=True)
    dates = pd.date_range("2025-01-01", periods=370, freq="1D", tz="UTC").delete(20)
    frame = pd.DataFrame(
        {
            "date": dates,
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 100_000.0,
        }
    )
    frame.to_feather(source)

    row = audit_file(source, repository)

    assert row["missing_slots_between_endpoints"] == 1
    assert row["largest_gap_missing_candles"] == 1
    assert row["duplicate_timestamps"] == 0
    assert row["consumption_status"] == "consumed_research_data"


def test_hash_manifest_excludes_itself_and_verifies(tmp_path: Path) -> None:
    research = tmp_path / "research_v2"
    research.mkdir()
    (research / "evidence.txt").write_text("preserved\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("invariants\n", encoding="utf-8")
    output = research / "ARTIFACT_HASHES.sha256"

    lines = manifest_lines(tmp_path, output)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert len(lines) == 2
    assert all("ARTIFACT_HASHES.sha256" not in line for line in lines)
    verify(tmp_path, output)
