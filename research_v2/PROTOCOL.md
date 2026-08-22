# Research v2 audit and stopping protocol — conservative long-only USDC spot

Status: **FROZEN LOCAL AUDIT/STOP PROTOCOL — NO STRATEGY RUNS AUTHORIZED**
Frozen: 2026-08-22T13:39:45+02:00 (Europe/Paris)
Repository: Freqtrade 2026.7, branch `stable`, commit `52bc96f4480b1a0da6a9b455bd00b17fbb6786a5`

This protocol is decision-first. It governs the repository audit and determines whether the
existing evidence can justify a frozen Freqtrade dry-run; it does not authorize a new strategy
experiment. Cash is an acceptable outcome.
Capital preservation, tail control, and selection-adjusted out-of-sample evidence outrank return
and trade count.

## 1. Immediate gate and authority

The repository audit found no genuinely untouched historical outer fold. The prior programme
inspected data-quality or strategy results across the locally available Binance USDC history,
including the eight-fold walk-forward through 2026-08-22. Under the governing rule that any
inspected period is consumed, **all local history is research-consumed**.

Consequences, frozen before any research-v2 result:

- Historical strategy/parameter trial budget: **0**.
- No Hyperopt, parameter grid, candidate backtest, pseudo-holdout, or repackaged walk-forward is
  authorized by research v2.
- No existing strategy qualifies for dry-run. The current programme-level stopping condition is
  **Research invalid because implementation or data problems remain**. Historical evidence
  exhausted is a second, independent stopping condition.
- Research v2 may run only non-strategy evidence audits, data-integrity checks, hash generation,
  and documentation verification. These do not create a new performance claim.
- A future candidate would require a new, complete protocol frozen before its first unseen outer
  candle. This file records only the current stop and durable invariants; the separate future
  template is explicitly incomplete and non-authorizing.
- Live trading, leverage, futures, margin, shorts, order placement, credential access, and real
  capital are outside scope.

This is not a claim that no strategy can work. It is a claim that the current evidence cannot
support a fresh confirmatory test or a dry-run authorization, and that the strongest prior
walk-forward cannot be accepted as implemented because its loader synthesized long blackout gaps.

## 2. Evidence precedence and consumed-data register

Precedence is: raw result archive and metadata > command log > generated CSV > frozen code/hash >
dated protocol amendment > narrative report. Contradictions remain recorded; later prose does not
erase earlier artifacts.

Authoritative legacy roots:

- `user_data/research/` — CombinedBinHAndCluc programme and raw artifacts.
- `user_data/research/st_cci/` — Supertrend, CCI, repository screen, ReinforcedAverage, and
  reassessment programmes.
- `user_data/backtest_results/` and `user_data/hyperopt_results/` — additional raw archives.
- `user_data/data/binance/` — locally available Binance spot OHLCV.

Conservative consumed classification:

| Half-open UTC interval | Why consumed | Permitted research-v2 use |
|---|---|---|
| [2018-12-15, 2021-01-01) | Coverage, liquidity, zero-volume, listing, and warm-up history were inspected; 2020 candles were also used by later implementations and factor/warm-up checks | Audit/context only |
| [2021-01-01, 2022-09-30) | Era A, regime slices, screens, Hyperopt diagnostics, robustness tests, and walk-forward F1–F2 | Audit/context only |
| [2022-09-30, 2024-03-01) | USDC delisting/relisting gaps and point-in-time availability inspected; walk-forward F3–F4 and warm-up data used | Audit/context only |
| [2024-03-01, 2025-04-01) | Main training/Hyperopt period, repository screen, deep-search probes, and walk-forward F4–F6 | Audit/context only |
| [2025-04-01, 2026-01-01) | Reused validation, candidate selection, stress runs, and walk-forward F6–F7 | Audit/context only |
| [2026-01-01, 2026-08-15) | Reused holdout for Supertrend, CCI, ReinforcedAverage, benchmarks, and stress runs | Audit/context only |
| [2026-08-15, 2026-08-23) | Recent-window inspection, refreshed 4h/1d data, and walk-forward F8 | Audit/context only |

Any candle at or before the latest timestamp in `research_v2/DATA_COVERAGE.csv` is presumed
consumed even if it is not named in a report. Downloading older data later does not make it an
untouched chronological holdout because family selection already used later outcomes.

### 2.1 Blocking loader contradiction

The original `user_data/research/PROTOCOL.md` says backtesting used
`fill_up_missing=False`. Raw code and logs contradict it:

- `freqtrade/optimize/backtesting.py::load_bt_data()` calls `history.load_data()` without a
  `fill_up_missing` override.
- `freqtrade/data/history/history_utils.py::load_data()` defaults `fill_up_missing=True`.
- `user_data/research/st_cci/reassess/logs/inner_F8.log` records synthetic 4h fillups of 9.31%
  for BTC/ETH/BNB, 30.94% for XRP/ADA, 40.19% for LTC, 41.20% for SOL, 43.34% for BCH, and
  57.88% for TRX. Other logs record still larger cases.

Freqtrade fills each missing candle with the previous close and zero volume. `RAvgOpt` blocks an
entry on a zero-volume row, but its EMAs and resampled two-day SMA still consume those rows and do
not reset after a blackout. The expanding inner-selection runs F3-F8 span such filled gaps, while
`startup_candle_count` trims only the beginning of a run. A separate raw-data audit described
point-in-time eligibility, but no strategy assertion enforced that mask inside those inner runs.
Therefore the statement that a 600-row startup count itself enforces 600 gap-free candles is false.

An archive-level audit found no outer entry that clearly violated the stated post-relisting
600-raw-candle warm-up; that narrower fact does not repair the selection pipeline, because each
outer parameter choice came from an affected inner run. The direction and magnitude of bias are
unknown. This unresolved selection-integrity defect is material. Research v2 will not repair and
rerun the consumed folds: such a rerun would be retrospective and could not restore confirmation.

## 3. Audit of the starting architecture

The raw programme has already consumed at least these families:

- 5m CombinedBinHAndCluc dip mean-reversion;
- 1m CCI oversold mean-reversion;
- 1h Supertrend trend following;
- 4h Average/ReinforcedAverage EMA-cross trend following;
- 1d Donchian/Turtle and many 5m/15m/1h/4h/1d repository-screen arms;
- BTC daily trend gates, hardened stops, exposure caps, and numerous risk-layer variants.

None produced evidence that can support a dry-run. As descriptive legacy output only, the strongest
audited candidate, ReinforcedAverage, reported pooled PF 1.09, chained drawdown 10.9%, a confidence
interval spanning zero, weak randomized-entry and exposure-path comparisons, concentration, and a
failed Deflated Sharpe Ratio. Those metrics would reject it even if taken at face value, but the
synthetic-gap defect means they cannot support a valid affirmative or negative performance
inference.

There is no prior BTC/ETH-only strategy baseline on the required common risk budget. Nearby
BTC/ETH/BNB probes do not satisfy that requirement. Running one now could be retrospective
diagnostics only and is forbidden by the zero historical trial budget.

If a future programme becomes possible, the simplest defensible starting family is **daily
absolute momentum / Donchian trend following with a USDC cash state**, first on BTC/USDC and
ETH/USDC only. The single economic hypothesis is that slow-moving flows and investor underreaction
create persistent medium-term trends, while an absolute-trend exit avoids paying crypto beta in
prolonged downtrends. Timeframe would be **1d and not optimized**. This is a family reservation,
not an approved candidate: research v2 defines no entry/exit constants, creates no strategy code,
and authorizes no performance run because doing so without an untouched outer fold would only add
selection.

A broader-universe extension is not authorized here. A future protocol must either freeze the
identical BTC/ETH and broad variants before one common outer horizon and correct jointly for both,
or reserve the broad variant for an entirely later untouched horizon. It may never observe the
BTC/ETH result, modify the broad variant, and reuse that period. Pair-specific signal parameters
and exceptions are forbidden.

## 4. Chronology, outer folds, warm-up, and embargo

### 4.1 Historical inner data

All historical periods are retrospective development evidence. They may explain prior failures,
but no metric from them is confirmatory. Research v2 therefore has no historical inner/validation
split and no historical outer fold.

### 4.2 Untouched outer folds

**None exist at freeze time.** This is the triggered stopping condition, not a missing protocol
choice. Relabeling the old Validation, Holdout, eight walk-forward folds, pre-2021 data, a pair
subset, or a different timeframe would not restore blindness.

No future fold count, endpoint, or selection algorithm is frozen by this stop protocol. Those are
mandatory unresolved fields in `FUTURE_PROTOCOL_TEMPLATE.md`. If any eventual outer result
influences code, parameters, pair rules, risk, costs, statistics, or interpretation, that period is
consumed and can never confirm the revision.

### 4.3 Warm-up and embargo

Not applicable: no candidate, inner interval, validation interval, outer fold, or entry is
authorized. Research v2 therefore cannot create warm-up or embargo observations. A later programme
must derive warm-up from convergence tests, reset it after every blackout, and define exact
half-open UTC intervals before its first unseen candle.

## 5. Point-in-time eligibility audit

The initial audit universe is BTC, ETH, TRX, BNB, LTC, XRP, SOL, BCH, XLM, DOT, and ADA against
USDC on Binance spot. `DATA_COVERAGE.csv` is an endpoint coverage and liquidity screen only; it is
not a historical eligibility calendar and does not authorize a pair. The audit treats every source
candle as consumed.

The legacy reassessment's external `pit_universe.csv` did not enforce eligibility inside the
strategy pipeline. Future eligibility must use raw, unfilled candles, immediate active-market/gap
disqualification, a full contiguous post-relisting re-warm, lagged liquidity inputs, and a dated
mask asserted again after Freqtrade loads data. That work belongs to a separately frozen protocol.

## 6. Frozen search, risk, benchmark, cost, and statistical boundaries

Research-v2 historical budget is **0 families, 0 variants, 0 parameter evaluations, 0 Hyperopt
epochs, and 0 outer evaluations**. There is no candidate risk model, benchmark test, execution
model, or inferential test because there is no authorized performance experiment. Operative
portfolio risk and exposure are therefore zero.

The documented legacy Hyperopt floor is **3,530 epochs**: at least 1,748 CombinedBinH epochs plus
1,782 later ST/CCI/RAvg epochs, before explicit configurations, screens, stress runs, and the
384 RAvg fold-by-parameter inner evaluations. No exact global trial count can be reconstructed. All
historical nominal p-values and performance statistics are descriptive only.

For avoidance of doubt, a later protocol may tighten but may not exceed the user-specified ceilings
of 0.25% intended equity risk per position and 0.75% total crypto heat, and must prohibit leverage,
margin, futures, shorts, DCA, pyramiding, and live trading. The previously drafted 10% gross cap,
costs, benchmarks, statistical tests, and dry-run duration were reviewer-challenged design ideas,
not validated or executable research-v2 rules. They have been moved to
`FUTURE_PROTOCOL_TEMPLATE.md` as unresolved fields.

## 7. Pass/fail and stopping conditions

No research-v2 candidate can pass because none may be selected or evaluated. The programme has
triggered two independent stopping conditions:

1. **Invalid research**: the legacy inner-selection pipeline has an unresolved synthetic-gap and
   point-in-time warm-up defect.
2. **Historical evidence exhausted**: all locally available periods through the coverage cutoff are
   consumed, so a corrected historical rerun cannot become fresh confirmation.

The zero trial budget is also exhausted by construction. `FINAL_REPORT.md` must lead with
**Research invalid because implementation or data problems remain**, state that no strategy is
eligible for dry-run, and avoid treating the direction of the invalid legacy performance estimates
as established.

## 8. Dry-run and live-trading gate

Closed. Research v2 authorizes neither a Freqtrade dry-run nor live trading. It defines no dry-run
measurement clock because no candidate has passed historical evidence. Any future paper-evaluation
gate requires a new complete protocol, quote/order-book shadow logging if fill realism is claimed,
a fixed calendar endpoint, the same final statistical gates as its historical stage, and no
strategy change or efficacy-based extension during measurement.

## 9. Freeze and artifact requirements

The local audit/stop freeze set contains `PROTOCOL.md`, `TRIAL_LEDGER.csv`, `DATA_COVERAGE.csv`,
`RESULTS.md`, `FINAL_REPORT.md`, a safe configuration snapshot, dependency versions, commands,
review findings, source-data hashes, strategy hashes, verification logs, and a final SHA-256
manifest. No legacy evidence is overwritten or renamed.

This is a local hash freeze, not an immutable execution freeze. A Git commit or externally
timestamped digest would be required to anchor chronology, and a commit needs explicit user
confirmation. No commit or push is authorized in this session. Before any future performance run,
a complete candidate protocol and implementation bundle must be independently reviewed, hashed,
and immutably anchored. `FUTURE_PROTOCOL_TEMPLATE.md` is non-authorizing and incomplete by design.
