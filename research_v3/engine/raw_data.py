"""Raw-candle provenance and point-in-time fact utilities.

These helpers deliberately never fill missing timestamps or OHLCV values. A future protocol may
apply policy thresholds to their outputs, but this module does not decide eligibility.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd


DAILY_STEP = pd.Timedelta(days=1)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one immutable input file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_index(values: Iterable[object]) -> pd.DatetimeIndex:
    """Normalize timestamps and reject duplicate or non-monotonic raw input."""
    index = pd.DatetimeIndex(pd.to_datetime(list(values), utc=True)).as_unit("ns")
    if index.has_duplicates:
        raise ValueError("Raw timestamps contain duplicates")
    if not index.is_monotonic_increasing:
        raise ValueError("Raw timestamps are not monotonic")
    return index


def assert_no_synthetic_timestamps(
    raw_dates: Iterable[object], post_loader_dates: Iterable[object]
) -> None:
    """Reject a loader output that contains timestamps not present in raw source data."""
    raw = utc_index(raw_dates)
    loaded = utc_index(post_loader_dates)
    synthetic = loaded[~loaded.isin(raw)]
    if len(synthetic):
        raise ValueError(
            "Post-loader data contains timestamps absent from raw source: "
            f"count={len(synthetic)}, first={synthetic[0].isoformat()}, "
            f"last={synthetic[-1].isoformat()}"
        )


def has_contiguous_raw_prefix(
    raw_dates: Iterable[object], decision_time: object, required_candles: int, step: pd.Timedelta
) -> bool:
    """Return whether a decision has the requested raw contiguous history immediately before it."""
    if required_candles <= 0:
        raise ValueError("required_candles must be positive")
    if step <= pd.Timedelta(0):
        raise ValueError("step must be positive")
    raw = utc_index(raw_dates)
    decision = pd.Timestamp(decision_time)
    if decision.tzinfo is None:
        decision = decision.tz_localize("UTC")
    else:
        decision = decision.tz_convert("UTC")
    position = int(raw.searchsorted(decision, side="left"))
    if position < required_candles:
        return False
    prefix = raw[position - required_candles : position]
    return bool(
        prefix[-1] == decision - step
        and len(prefix) == required_candles
        and (prefix[1:] - prefix[:-1] == step).all()
    )


def verify_freqtrade_loader_provenance(
    datadir: Path, pair: str, timeframe: str, raw_dates: Iterable[object]
) -> dict[str, int]:
    """Check local Freqtrade loader modes against raw timestamps without any strategy execution.

    The unfilled mode must preserve the raw timestamp set exactly.  Filled mode is expected to add
    timestamps for pairs with source gaps; those additions must be observable and rejected by the
    anti-synthesis primitive rather than silently accepted.
    """
    from freqtrade.data.history import load_pair_history
    from freqtrade.enums import CandleType

    raw = utc_index(raw_dates)
    expected_slots = int((raw[-1] - raw[0]) / pd.Timedelta(days=1)) + 1
    unfilled = load_pair_history(
        pair=pair,
        timeframe=timeframe,
        datadir=datadir,
        fill_up_missing=False,
        drop_incomplete=False,
        data_format="feather",
        candle_type=CandleType.SPOT,
    )
    assert_no_synthetic_timestamps(raw, unfilled["date"])
    filled = load_pair_history(
        pair=pair,
        timeframe=timeframe,
        datadir=datadir,
        fill_up_missing=True,
        drop_incomplete=False,
        data_format="feather",
        candle_type=CandleType.SPOT,
    )
    filled_dates = utc_index(filled["date"])
    synthetic_count = int((~filled_dates.isin(raw)).sum())
    if synthetic_count:
        try:
            assert_no_synthetic_timestamps(raw, filled_dates)
        except ValueError:
            pass
        else:
            raise AssertionError("Filled loader timestamps were not rejected as synthetic")
    return {
        "raw_rows": len(raw),
        "unfilled_rows": len(unfilled),
        "filled_rows": len(filled),
        "filled_synthetic_timestamps": synthetic_count,
        "raw_missing_slots_in_span": expected_slots - len(raw),
    }


def _contiguous_run(present: pd.Series) -> list[int]:
    run = 0
    values: list[int] = []
    for is_present in present:
        run = run + 1 if bool(is_present) else 0
        values.append(run)
    return values


def build_daily_raw_calendar(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a daily fact calendar while preserving all source gaps as absent rows.

    ``frame`` must contain raw ``date``, ``close``, and ``volume`` fields. Missing dates remain
    explicit ``False``/``NaN`` facts; no OHLCV value is copied across a gap.
    """
    required = {"date", "close", "volume"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Raw frame lacks columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Raw frame is empty")

    raw = frame.loc[:, ["date", "close", "volume"]].copy()
    raw["date"] = utc_index(raw["date"])
    if not (raw["date"].dt.normalize() == raw["date"]).all():
        raise ValueError("Daily raw timestamps must be midnight UTC")
    raw["quote_turnover_usdc"] = raw["close"] * raw["volume"]
    full_dates = pd.date_range(raw["date"].iloc[0], raw["date"].iloc[-1], freq="1D", tz="UTC")
    calendar = pd.DataFrame({"date": full_dates}).merge(
        raw, how="left", on="date", validate="one_to_one"
    )
    calendar["raw_candle_present"] = calendar["close"].notna()
    calendar["raw_zero_volume"] = calendar["raw_candle_present"] & (calendar["volume"] <= 0)
    calendar["contiguous_raw_candle_run"] = _contiguous_run(calendar["raw_candle_present"])

    observed = calendar["raw_candle_present"].astype(int)
    zero_volume = calendar["raw_zero_volume"].astype(int)
    expected = pd.Series(1, index=calendar.index, dtype=int).rolling(90, min_periods=1).sum()
    observed_window = observed.rolling(90, min_periods=1).sum()
    calendar["trailing_90d_expected_slots"] = expected.astype(int)
    calendar["trailing_90d_observed_slots"] = observed_window.astype(int)
    calendar["trailing_90d_completeness_pct"] = 100 * observed_window / expected
    calendar["trailing_90d_zero_volume_pct_of_observed"] = np.where(
        observed_window > 0,
        100 * zero_volume.rolling(90, min_periods=1).sum() / observed_window,
        np.nan,
    )
    calendar["trailing_90d_median_daily_quote_usdc"] = (
        calendar["quote_turnover_usdc"].rolling(90, min_periods=1).median()
    )
    return calendar.loc[
        :,
        [
            "date",
            "raw_candle_present",
            "raw_zero_volume",
            "contiguous_raw_candle_run",
            "trailing_90d_expected_slots",
            "trailing_90d_observed_slots",
            "trailing_90d_completeness_pct",
            "trailing_90d_zero_volume_pct_of_observed",
            "trailing_90d_median_daily_quote_usdc",
        ],
    ]
