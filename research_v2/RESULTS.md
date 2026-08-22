# Research v2 results

Status: audit complete and locally hash-frozen at 2026-08-22T13:39:45+02:00; no research-v2
strategy performance experiment has been run.

## Outcome so far

The raw evidence establishes that the available historical USDC data is consumed research data.
The later ReinforcedAverage reassessment used eight chronological outer folds through 2026-08-22,
while earlier data-quality work inspected the older Binance USDC coverage. There is no honest
historical holdout left to open.

It also confirms a material legacy implementation defect: Freqtrade backtesting synthesized
missing candles across long USDC delisting blackouts, contradicting the earlier frozen protocol and
invalidating the claim that row-count startup alone enforced contiguous point-in-time warm-up.

Research v2 therefore records an invalidity/stopping result, not a candidate backtest:

- historical family trials: 0 authorized, 0 run;
- Hyperopt epochs: 0 authorized, 0 run;
- outer-fold evaluations: 0 authorized, 0 run;
- dry-run: not authorized;
- live trading: prohibited.

## Blocking data/loader finding

- `freqtrade/optimize/backtesting.py:364-373` calls `history.load_data()` without overriding gap
  filling.
- `freqtrade/data/history/history_utils.py:85-95` sets `fill_up_missing=True` by default.
- `freqtrade/data/converter/converter.py:102-139` forward-fills OHLC from the previous close and
  sets volume to zero.
- `user_data/research/st_cci/reassess/logs/inner_F8.log:1638-1658` records 9.31%-57.88% synthetic
  4h fillups across nine pairs. The prior `user_data/research/PROTOCOL.md:20` says gaps were not
  synthesized.
- `RAvgOpt` blocks entries on zero-volume rows, but its EMAs and resampled two-day SMA consume the
  filled prices and do not reset after a blackout. Nine genuine raw zero-volume 4h rows also exist,
  so volume alone cannot recover candle provenance.
- The reproducible archive audit in `LEGACY_WARMUP_AUDIT.csv` checks the exact 600 raw 4h timestamps
  immediately before each executed entry. All 4,004 selected/reference outer entries and all
  34,804 48-arm outer-grid entries pass. In contrast, 19,880 of 177,235 inner-grid entries fail;
  every selected inner winner from F3 through F8 contains affected trades.

The correct scope is therefore selection contamination, not an outer-entry timing violation. The
outer parameters were chosen from affected inner runs, so the nested walk-forward is invalid as
clean selection-adjusted evidence. The direction and magnitude of bias are unknown. Re-running a
fixed implementation would expose only consumed folds and cannot become fresh confirmation.

## Legacy evidence that controls the decision

| Evidence | Raw path | Controlling finding |
|---|---|---|
| CombinedBinHAndCluc programme | `user_data/research/` | Nine validation candidates failed; the mean-reversion family did not produce credible OOS evidence |
| Supertrend/CCI programme | `user_data/research/st_cci/REPORT.md` and raw `results/` | Both frozen candidates failed validation/holdout expectancy gates |
| Repository screen/deep search | `user_data/research/st_cci/deep/` | Many families/configurations were screened; apparent trend profit depended on exceptional rally trades and/or invalid warm-up |
| ReinforcedAverage experiment | `user_data/research/st_cci/REPORT_E3.md` and raw archives | Validation and holdout failed; procedural slips were later disclosed |
| ReinforcedAverage reassessment | `user_data/research/st_cci/RAVG_REASSESSMENT_PROTOCOL.md`, `RAVG_REASSESSMENT_RESULTS.csv`, `RAVG_REASSESSMENT_REPORT.md`, and `reassess/` | Invalid due to gap-contaminated inner selection; descriptive outputs were PF 1.09, chained DD 10.9%, CI spanning zero, below exposure path, random-entry mean percentile 54, concentration and DSR failures |

## Raw-over-narrative corrections preserved

- The RAvg strategy file was frozen before its holdout run, but its freeze document was written
  after the holdout launch.
- The first reassessment report had the exposure-path comparison sign wrong, lagged exposure by
  one candle, confused maximum per-fold drawdown with chained drawdown, and used a hard-coded DSR
  dispersion assumption. The archived verifier corrections make the rejection stronger.
- Closed-trade daily P&L is not adequate for beta/drawdown inference; research-v2 requires daily
  mark-to-market portfolio returns.

The legacy performance values above are preserved to explain the safe decision, not treated as
valid proof of a negative edge. The implementation defect prevents both affirmative and negative
performance inference from the controlling reassessment.

## Verification results

- Independent fresh-context draft review returned BLOCK. After all blockers were disposed by
  narrowing this to a zero-trial stop protocol, the final scoped re-review returned PASS.
- `pytest research_v2/tests`: 4 passed. Two PyArrow deprecation warnings are recorded in
  `logs/pytest.xml`; they do not affect the audit values.
- Ruff check and format check: passed for all research-v2 Python files.
- Bundle verification: 66 unique source-data rows and hashes, five legacy strategy hashes, all
  warm-up totals, zero historical budget, safe configuration, verdict consistency, and disabled
  dry-run/live authorization passed. Raw output is `logs/bundle_verification.txt`.
- `ARTIFACT_HASHES.sha256` was generated after the final edits and verified byte-for-byte. It is a
  local integrity manifest, not an immutable timestamp anchor.

No Freqtrade strategy command, backtest, Hyperopt epoch, paper trade, live trade, or exchange order
was executed by research v2.

## Direct data audit

`research_v2/DATA_COVERAGE.csv` contains 66 pair/timeframe rows and SHA-256 hashes. It found the
raw delisting gaps explicitly (for example, 163 missing 1d BTC/ETH/BNB candles and 705 missing TRX
daily candles between endpoints). BTC, ETH, BNB, XRP, and SOL pass the illustrative endpoint screen.
That screen is neither a frozen rule nor a historical point-in-time calendar, strategy universe, or
authorization.
