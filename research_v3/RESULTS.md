# Research V3 — Infrastructure Preflight Results

**Verdict: Remediation in progress after independent review; not ready for strategy evaluation or dry-run.**

The preflight workflow has produced raw-candle provenance and gap-preserving daily fact calendars
for the 11 approved USDC pairs. It contains no candidate strategy, does not authorize historical
strategy trials, and cannot authorize dry-run or live trading.

## Recorded result

- 11 approved daily raw sources were hashed into `artifacts/RAW_SOURCE_MANIFEST.csv`.
- The raw-fact calendar contains 21,509 pair-days in `artifacts/RAW_DAILY_CALENDAR.csv`.
- The report records zero historical strategy trials and false dry-run/live authorization.
- Freqtrade's local loader preserves all 17,851 raw timestamps when `fill_up_missing=False`; its
  filled mode exposes 3,658 synthetic timestamps, exactly matching raw calendar gaps. The preflight
  records both outcomes and rejects unfilled synthetic timestamps.
- Verification re-hashes every listed daily source, reconciles each manifest count with calendar raw
  presence, and rejects unsafe configuration, mismatched report counts, unexpected schema, and
  impossible raw-gap facts.
- The source manifest excludes runtime bytecode, caches, test reports, and itself so it can be
  verified after a clean test run.

These are infrastructure observations only. They make no claim about eligibility thresholds,
signal quality, return, expectancy, drawdown, or future performance.
