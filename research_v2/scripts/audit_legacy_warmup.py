"""Audit archived RAvg trade entries against raw contiguous 4h warm-up history."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from freqtrade.data.btanalysis import load_backtest_data, load_backtest_stats


WARMUP_CANDLES = 600
STEP = pd.Timedelta(hours=4)
GROUP_PATTERNS = {
    "inner_selection": re.compile(r"^inner_F[1-8]$"),
    "selected_outer_archives": re.compile(r"^outer_F[1-8]_[SR]$"),
    "grid_outer_diagnostic": re.compile(r"^grid_outer_F[1-8]$"),
}
EXPECTED_ARCHIVES = {
    "inner_selection": 8,
    "selected_outer_archives": 16,
    "grid_outer_diagnostic": 8,
}


def raw_date_index(path: Path) -> np.ndarray:
    """Return strictly ordered raw timestamps as integer nanoseconds."""
    frame = pd.read_feather(path, columns=["date"])
    dates = pd.to_datetime(frame["date"], utc=True)
    if dates.duplicated().any() or not dates.is_monotonic_increasing:
        raise ValueError(f"Raw timestamps are not unique and ordered: {path}")
    return pd.DatetimeIndex(dates).as_unit("ns").asi8.copy()


def has_contiguous_prefix(raw_ns: np.ndarray, entry: pd.Timestamp) -> bool:
    """Check that the 600 raw bars immediately before an entry are exactly 4h apart."""
    return bool(contiguous_entry_mask(raw_ns, pd.DatetimeIndex([entry]))[0])


def contiguous_entry_mask(raw_ns: np.ndarray, entries: pd.DatetimeIndex) -> np.ndarray:
    """Vectorize the strict raw-prefix rule for entry timestamps."""
    entry_ns = pd.DatetimeIndex(entries).tz_convert("UTC").as_unit("ns").asi8
    positions = np.searchsorted(raw_ns, entry_ns, side="left")
    enough_history = positions >= WARMUP_CANDLES
    step_ns = int(STEP.value)
    prior_position = np.maximum(0, np.minimum(positions - 1, len(raw_ns) - 1))
    prefix_ends_at_prior_candle = raw_ns[prior_position] == entry_ns - step_ns
    bad_steps = np.diff(raw_ns) != step_ns
    cumulative_bad = np.concatenate(([0], np.cumsum(bad_steps, dtype=np.int64)))
    safe_start = np.maximum(0, positions - WARMUP_CANDLES)
    safe_end = np.maximum(0, np.minimum(positions - 1, len(cumulative_bad) - 1))
    bad_in_prefix = cumulative_bad[safe_end] - cumulative_bad[safe_start]
    return enough_history & prefix_ends_at_prior_candle & (bad_in_prefix == 0)


def classify_archives(results_root: Path) -> dict[str, list[Path]]:
    """Find the three frozen archive populations used by the reconciliation."""
    groups = {name: [] for name in GROUP_PATTERNS}
    for directory in sorted(path for path in results_root.iterdir() if path.is_dir()):
        for name, pattern in GROUP_PATTERNS.items():
            if pattern.match(directory.name):
                archives = sorted(directory.glob("*.zip"))
                if len(archives) != 1:
                    raise RuntimeError(f"Expected one ZIP in {directory}, found {len(archives)}")
                groups[name].extend(archives)
    for name, archives in groups.items():
        if len(archives) != EXPECTED_ARCHIVES[name]:
            raise RuntimeError(
                f"Expected {EXPECTED_ARCHIVES[name]} {name} archives, found {len(archives)}"
            )
    return groups


def audit_archive(
    archive: Path,
    repository: Path,
    raw_dates: dict[str, np.ndarray],
    selected_strategy: str = "",
) -> tuple[dict[str, str | int], Counter[str]]:
    """Count strict raw-prefix violations for every strategy trade in one archive."""
    strategies = sorted(load_backtest_stats(archive)["strategy"])
    trades = 0
    violations = 0
    selected_trades = 0
    selected_violations = 0
    pair_violations: Counter[str] = Counter()
    for strategy in strategies:
        frame = load_backtest_data(archive, strategy=strategy)
        trades += len(frame)
        strategy_violations = 0
        for pair, pair_frame in frame.groupby("pair", sort=False):
            pair = str(pair)
            if pair not in raw_dates:
                raise KeyError(f"No raw 4h index for {pair}")
            valid = contiguous_entry_mask(
                raw_dates[pair], pd.DatetimeIndex(pair_frame["open_date"])
            )
            invalid_count = int((~valid).sum())
            strategy_violations += invalid_count
            if invalid_count:
                pair_violations[pair] += invalid_count
        violations += strategy_violations
        if strategy == selected_strategy:
            selected_trades = len(frame)
            selected_violations = strategy_violations
    if selected_strategy and selected_strategy not in strategies:
        raise RuntimeError(f"Selected strategy {selected_strategy} absent from {archive}")
    directory = archive.parent.name
    fold_match = re.search(r"F[1-8]", directory)
    return (
        {
            "fold": fold_match.group(0) if fold_match else "",
            "archive": archive.relative_to(repository).as_posix(),
            "strategy_count": len(strategies),
            "trade_entries": trades,
            "entries_with_600_contiguous_raw_4h_prefix": trades - violations,
            "entries_without_600_contiguous_raw_4h_prefix": violations,
            "selected_strategy": selected_strategy,
            "selected_trade_entries": selected_trades if selected_strategy else "",
            "selected_entries_without_600_contiguous_raw_4h_prefix": (
                selected_violations if selected_strategy else ""
            ),
        },
        pair_violations,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()

    repository = args.repository.resolve()
    results_root = repository / "user_data" / "research" / "st_cci" / "reassess" / "results"
    groups = classify_archives(results_root)
    selection_frame = pd.read_csv(
        repository / "user_data" / "research" / "st_cci" / "reassess" / "wf_selection.csv"
    )
    selected_by_fold = dict(zip(selection_frame["fold"], selection_frame["selected"], strict=True))
    raw_dates = {
        f"{base}/USDC": raw_date_index(
            repository / "user_data" / "data" / "binance" / f"{base}_USDC-4h.feather"
        )
        for base in ("BTC", "ETH", "TRX", "BNB", "LTC", "XRP", "SOL", "BCH", "XLM", "DOT", "ADA")
    }

    rows: list[dict[str, str | int]] = []
    group_pairs: dict[str, Counter[str]] = {}
    for group, archives in groups.items():
        pair_counts: Counter[str] = Counter()
        for archive in archives:
            fold_match = re.search(r"F[1-8]", archive.parent.name)
            fold = fold_match.group(0) if fold_match else ""
            selected_strategy = selected_by_fold[fold] if group == "inner_selection" else ""
            row, archive_pairs = audit_archive(
                archive, repository, raw_dates, selected_strategy=selected_strategy
            )
            row = {"archive_group": group, **row}
            rows.append(row)
            pair_counts.update(archive_pairs)
        group_pairs[group] = pair_counts

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "research_v2 legacy RAvg raw-warmup audit",
        f"warmup_candles={WARMUP_CANDLES}",
        "rule=the 600 raw 4h timestamps immediately preceding each entry must be exactly 4h apart",
    ]
    for group in GROUP_PATTERNS:
        selected = [row for row in rows if row["archive_group"] == group]
        trades = sum(int(row["trade_entries"]) for row in selected)
        violations = sum(
            int(row["entries_without_600_contiguous_raw_4h_prefix"]) for row in selected
        )
        lines.append(
            f"group={group} archives={len(selected)} trades={trades} violations={violations}"
        )
        pair_text = ",".join(
            f"{pair}:{count}" for pair, count in sorted(group_pairs[group].items())
        )
        lines.append(f"group={group} violation_pairs={pair_text or 'none'}")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
