# ruff: noqa: S101

import pandas as pd
import pytest

from research_v3.engine.raw_data import (
    assert_no_synthetic_timestamps,
    build_daily_raw_calendar,
    has_contiguous_raw_prefix,
)


def test_raw_prefix_requires_continuous_history_before_decision() -> None:
    raw = pd.date_range("2026-01-01", periods=4, freq="1D", tz="UTC")

    assert has_contiguous_raw_prefix(
        raw, "2026-01-05", required_candles=4, step=pd.Timedelta(days=1)
    )
    assert not has_contiguous_raw_prefix(
        raw.delete(2), "2026-01-05", required_candles=3, step=pd.Timedelta(days=1)
    )


def test_post_loader_synthetic_timestamp_is_rejected() -> None:
    raw = pd.date_range("2026-01-01", periods=2, freq="1D", tz="UTC")
    loaded = pd.date_range("2026-01-01", periods=3, freq="12h", tz="UTC")

    with pytest.raises(ValueError, match="absent from raw source"):
        assert_no_synthetic_timestamps(raw, loaded)


def test_daily_calendar_preserves_gap_without_ohlcv_fill() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-03", "2026-01-04"], utc=True),
            "close": [100.0, 102.0, 103.0],
            "volume": [10.0, 0.0, 20.0],
        }
    )

    calendar = build_daily_raw_calendar(frame)

    assert len(calendar) == 4
    gap = calendar.loc[calendar["date"] == pd.Timestamp("2026-01-02", tz="UTC")].iloc[0]
    assert not gap["raw_candle_present"]
    assert gap["contiguous_raw_candle_run"] == 0
    assert calendar.iloc[-1]["contiguous_raw_candle_run"] == 2
    assert calendar.iloc[-1]["trailing_90d_observed_slots"] == 3
    assert calendar.iloc[-1]["trailing_90d_expected_slots"] == 4


def test_daily_calendar_rejects_non_midnight_timestamps() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01 12:00:00"], utc=True),
            "close": [100.0],
            "volume": [10.0],
        }
    )

    with pytest.raises(ValueError, match="midnight UTC"):
        build_daily_raw_calendar(frame)
