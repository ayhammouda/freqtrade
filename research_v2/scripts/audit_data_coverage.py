"""Audit local Binance USDC OHLCV coverage without altering source data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PAIRS = ("BTC", "ETH", "TRX", "BNB", "LTC", "XRP", "SOL", "BCH", "XLM", "DOT", "ADA")
TIMEFRAME_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
FILE_RE = re.compile(
    rf"^(?P<base>{'|'.join(PAIRS)})_USDC-(?P<timeframe>{'|'.join(TIMEFRAME_MINUTES)})\.feather$"
)


@dataclass(frozen=True)
class Gap:
    missing_candles: int
    start: pd.Timestamp | None
    end: pd.Timestamp | None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_utc(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return ""
    return value.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def largest_gap(dates: pd.Series, step: pd.Timedelta) -> Gap:
    if len(dates) < 2:
        return Gap(0, None, None)
    deltas = dates.diff()
    index = deltas.idxmax()
    delta = deltas.loc[index]
    missing = max(0, round(delta / step) - 1)
    if missing == 0:
        return Gap(0, None, None)
    current_position = dates.index.get_loc(index)
    return Gap(missing, dates.iloc[current_position - 1], dates.iloc[current_position])


def trailing_metrics(frame: pd.DataFrame, step: pd.Timedelta) -> tuple[float, float, float, int]:
    end = frame["date"].iloc[-1]
    start = end - pd.Timedelta(days=90) + step
    trailing = frame.loc[frame["date"] >= start].copy()
    expected = max(1, math.floor((end - start) / step) + 1)
    completeness = len(trailing) / expected
    zero_volume_pct = float((trailing["volume"] <= 0).mean() * 100) if len(trailing) else math.nan
    quote_turnover = (trailing["close"] * trailing["volume"]).set_axis(trailing["date"])
    daily_turnover = quote_turnover.resample("1D").sum(min_count=1)
    median_daily_quote = float(daily_turnover.median()) if len(daily_turnover) else math.nan
    max_gap = largest_gap(trailing["date"], step).missing_candles
    return completeness, zero_volume_pct, median_daily_quote, max_gap


def audit_file(path: Path, repository: Path) -> dict[str, str | int | float]:
    match = FILE_RE.match(path.name)
    if not match:
        raise ValueError(f"Unexpected file name: {path}")
    base = match.group("base")
    timeframe = match.group("timeframe")
    step = pd.Timedelta(minutes=TIMEFRAME_MINUTES[timeframe])
    frame = pd.read_feather(path, columns=["date", "open", "high", "low", "close", "volume"])
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    dates = frame["date"]
    duplicates = int(dates.duplicated().sum())
    non_monotonic = int(not dates.is_monotonic_increasing)
    start = dates.iloc[0] if len(frame) else None
    end = dates.iloc[-1] if len(frame) else None
    expected = math.floor((end - start) / step) + 1 if len(frame) else 0
    missing = max(0, expected - len(frame))
    gap = largest_gap(dates, step)
    zero_volume = int((frame["volume"] <= 0).sum())
    invalid_ohlc = int(
        (
            (frame[["open", "high", "low", "close"]] <= 0).any(axis=1)
            | (frame["high"] < frame[["open", "close", "low"]].max(axis=1))
            | (frame["low"] > frame[["open", "close", "high"]].min(axis=1))
        ).sum()
    )
    completeness, trailing_zero, median_daily_quote, trailing_max_gap = trailing_metrics(
        frame, step
    )

    endpoint_screen = "not_evaluated_non_daily"
    if timeframe == "1d":
        history_days = (end - start).days + 1 if start is not None and end is not None else 0
        eligible = (
            len(frame) >= 300
            and history_days >= 365
            and completeness >= 0.99
            and trailing_zero <= 1.0
            and median_daily_quote >= 5_000_000
            and trailing_max_gap <= 3
            and duplicates == 0
            and non_monotonic == 0
            and invalid_ohlc == 0
        )
        endpoint_screen = "passes_endpoint_screen" if eligible else "fails_endpoint_screen"

    return {
        "pair": f"{base}/USDC",
        "timeframe": timeframe,
        "market_type": "spot",
        "source_file": path.relative_to(repository).as_posix(),
        "source_sha256": sha256_file(path),
        "start_utc": iso_utc(start),
        "end_utc": iso_utc(end),
        "observed_candles": len(frame),
        "expected_slots_between_endpoints": expected,
        "missing_slots_between_endpoints": missing,
        "raw_completeness_pct": round(100 * len(frame) / expected, 6) if expected else 0,
        "gap_intervals": int((dates.diff() > step).sum()) if len(frame) else 0,
        "largest_gap_missing_candles": gap.missing_candles,
        "largest_gap_start_utc": iso_utc(gap.start),
        "largest_gap_end_utc": iso_utc(gap.end),
        "duplicate_timestamps": duplicates,
        "non_monotonic_dates": non_monotonic,
        "zero_volume_candles": zero_volume,
        "zero_volume_pct": round(100 * zero_volume / len(frame), 6) if len(frame) else 0,
        "invalid_ohlc_rows": invalid_ohlc,
        "trailing_90d_completeness_pct": round(100 * completeness, 6),
        "trailing_90d_zero_volume_pct": round(trailing_zero, 6),
        "trailing_90d_median_daily_quote_usdc": round(median_daily_quote, 2),
        "trailing_90d_largest_gap_missing_candles": trailing_max_gap,
        "endpoint_daily_screen": endpoint_screen,
        "consumption_status": "consumed_research_data",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()

    repository = args.repository.resolve()
    datadir = repository / "user_data" / "data" / "binance"
    paths = sorted(path for path in datadir.glob("*.feather") if FILE_RE.match(path.name))
    expected_files = len(PAIRS) * len(TIMEFRAME_MINUTES)
    if len(paths) != expected_files:
        raise RuntimeError(f"Expected {expected_files} files, found {len(paths)}")

    rows = [audit_file(path, repository) for path in paths]
    timeframe_order = {timeframe: index for index, timeframe in enumerate(TIMEFRAME_MINUTES)}
    pair_order = {pair: index for index, pair in enumerate(PAIRS)}
    rows.sort(
        key=lambda row: (
            pair_order[str(row["pair"]).split("/")[0]],
            timeframe_order[str(row["timeframe"])],
        )
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    daily = [row for row in rows if row["timeframe"] == "1d"]
    eligible = [
        row["pair"] for row in daily if row["endpoint_daily_screen"] == "passes_endpoint_screen"
    ]
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text(
        "\n".join(
            [
                "research_v2 data coverage audit",
                f"repository={repository}",
                f"files_scanned={len(rows)}",
                f"daily_pairs_passing_endpoint_screen={','.join(map(str, eligible))}",
                "all_rows_consumption_status=consumed_research_data",
                "note=endpoint screen is not a point-in-time calendar or strategy authorization",
                "note=Freqtrade backtesting default fill behavior is audited "
                "separately in RESULTS.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(rows)} rows to {args.output}")
    print(f"Daily pairs passing endpoint screen: {', '.join(map(str, eligible)) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
