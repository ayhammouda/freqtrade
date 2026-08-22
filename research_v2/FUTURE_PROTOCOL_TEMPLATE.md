# Non-authorizing future research protocol template

Status: **INCOMPLETE TEMPLATE — MUST NOT BE USED TO RUN A STRATEGY**
Created: 2026-08-22 (Europe/Paris)

This file preserves safeguards identified during the research-v2 audit. It is not an amendment to
the zero trial budget in `PROTOCOL.md`, does not reserve future candles, and contains no executable
candidate. Every bracketed field must be fixed, independently reviewed, hash-frozen, and immutably
anchored before the first outer candle. Missing information is a hard stop, not analyst discretion.

## Activation prerequisites

- A genuinely future evidence horizon exists after the final implementation freeze.
- The full candidate and selection pipeline can be frozen before that horizon begins.
- Raw candles can be retained without synthetic gap filling and a dated point-in-time eligibility
  calendar can be constructed.
- The owner approves any required Git commit or external timestamp anchor. This does not authorize
  trading, credential use, or exchange orders.

## Required frozen decisions

### Evidence chronology

- Freeze timestamp and data cutoff: `[UTC timestamp]`.
- Consumed development interval, with every prior inspection disclosed: `[half-open UTC interval]`.
- Chronological inner-training and inner-validation windows: `[exact half-open UTC intervals]`.
- Exact deterministic inner score, tie order, missing-data behavior, and cash/no-qualifier branch:
  `[algorithm]`.
- Exactly one selected pipeline must be frozen before the outer horizon starts.
- Exact outer reporting partitions and final endpoint: `[fixed half-open UTC intervals]`. They are
  reporting partitions of one continuous mark-to-market simulation; positions are not force-exited
  at boundaries unless liquidation is itself a frozen strategy rule.
- If any outer result affects any decision, that period is consumed and cannot confirm the revision.
- An underpopulated required fold makes the programme insufficient; it is never removed from the
  denominator and the endpoint is never extended after performance is viewed.

### Family and variants

- Reserved starting family: one transparent 1d absolute-momentum or Donchian trend family with a
  USDC cash state and one explicit underreaction/trend-persistence hypothesis.
- BTC/USDC and ETH/USDC only are the mandatory first baseline.
- Timeframe is 1d and is not optimized.
- Entry, exit, stop, and every parameter/range: `[coarse values and rationale]`.
- No pair-specific exceptions, indicator grab bag, unsupported precision, DCA, leverage, margin,
  futures, shorts, or post-result protection tuning.
- Either freeze the identical broader-universe variant before the same outer horizon and include
  both variants in multiplicity correction, or defer it to an entirely later untouched horizon.
  It may not be designed after seeing the BTC/ETH outer result and reuse that period.
- Total family, variant, parameter-cell, loss-function, universe, and diagnostic budget:
  `[finite counts, including the no-qualifier outcome]`.

### Point-in-time data and warm-up

- Build a dated eligibility calendar from raw, unfilled candles using only lagged information.
- Mechanically define reliable listing start, active-market state, gap thresholds, liquidity/capacity
  rules, and exchange-minimum feasibility. Capacity must include frozen wallet and maximum order
  participation, not turnover alone.
- A blackout, delisting, or disqualifying gap immediately makes a pair ineligible, resets all
  indicators, and requires a complete contiguous re-warm.
- Derive startup history from per-pair indicator and signal convergence; record the chosen count and
  tolerance. Do not assume a row count proves contiguous exchange history.
- Disable loader gap synthesis for research input. Independently assert after loading that no
  synthetic row is eligible, every entry has the required raw contiguous prefix, timestamps are
  unique/monotonic, and all informative candles are completed and lagged.
- Warm-up, embargo, eligibility, benchmark, and trade intervals use exact half-open UTC semantics.

### Portfolio risk

- Planned loss includes stop distance, round-trip baseline costs, and frozen adverse-fill allowance.
- Intended loss per position may not exceed 0.25% of pre-entry equity; total correlated crypto heat
  may not exceed 0.75%. These ceilings may be tightened before evidence but never relaxed afterward.
- Freeze starting wallet, stop formula/range, gross and per-asset caps, maximum correlated positions,
  minimum/maximum stake, fee-currency handling, precision/rounding, pending-order treatment, and the
  safe callback failure branch: `[values and formulas]`.
- State whether caps are entry-only or continuous. If continuous, freeze rebalancing/exit behavior.
- Stake is always reduced or a signal is skipped; exchange minimums never justify oversizing.
- Assert every simulated entry and pending order against loss, heat, and gross caps. Any clamp,
  fallback, exception, or breach invalidates the run.
- Risk containment is never described as signal edge.

### Execution and costs

- Freeze market/limit order types and causal fill rules: `[rules]`.
- Record commission, spread, impact/slippage, latency, non-fill, and stop-gap loss separately.
- Label unmeasured costs as hypothetical sensitivities; do not call them realistic without captured
  evidence.
- Freeze normal, moderate, and severe per-side assumptions: `[values and evidence]`.
- Entry occurs no earlier than the next executable candle after a completed signal; freeze delayed
  entry stress.
- Implement pessimistic gap-stop fills in preserved code rather than relying on native optimistic
  stop semantics.
- Freeze the mandatory fallback when 1h/5m detail coverage is missing; an unavailable required
  stress cannot be silently skipped.
- Freeze allocator tie-breaking independent of whitelist order and test pair-order permutations,
  simultaneous signals, partial fills, and an explicitly adverse non-fill sensitivity.

### Benchmarks and controls

- USDC cash without yield; separately report USDC/USD purchasing-power sensitivity if reliable data
  is available.
- Unscaled passive BTC/ETH and eligible-basket opportunity cost, plus exposure-matched and
  volatility-matched versions. Freeze rebalance timing, costs, volatility lookback, scaling cap,
  no-leverage constraint, and fold-boundary handling.
- Freeze the causal exposure-path basket formula and timestamp alignment.
- Randomize or circularly shift eligible entry signals with a frozen exclusion radius and seeds,
  then rerun the identical exit, stop/gap, eligibility, allocator, heat/gross, and cost engines.
  Never assign future realized holding durations from actual trades.
- Freeze whether factor analysis uses separate BTC and basket regressions or a joint model, the
  risk-free convention, collinearity handling, and bootstrap/HAC inference.

### Integrity checks

- Freqtrade lookahead analysis with enough actual non-forced signals; cancellation for too few
  trades is insufficient.
- Recursive analysis separately for every eligible pair, direct prefix/truncation equivalence for
  signals and portfolio callbacks, and start-date shifts at predeclared phases.
- Exact entry/exit flag equality and a frozen numerical indicator tolerance.
- Manual completed-informative-candle check, post-loader raw-mask assertion, simultaneous allocator
  tests, callback exception/min-stake tests, and cap assertions.
- Clean-process reproduction with cache disabled, fixed seeds, resolved configuration, parameter
  precedence check, disabled parameter export, dependencies, commands, logs, raw exports, and
  SHA-256 manifests.

### Statistics and decision rules

- Primary series: full-calendar daily mark-to-market portfolio excess returns, including open
  positions.
- Freeze one exact resampling method, automatic block-length rule, fold-boundary handling, seed,
  resample count, interval construction, and one-sided family-wise alpha.
- Prefer max-stat/bootstrap evaluation of the complete search-and-select pipeline. Define the full
  multiplicity family, including all cells, variants, benchmarks, factors, costs, stability probes,
  and all historical work that influenced selection. The known historical Hyperopt floor is 3,530
  epochs before explicit configurations.
- Use Deflated Sharpe Ratio only as a sensitivity unless its trial-dispersion estimator and trial
  universe are frozen. Report trade PF/expectancy without treating trades as independent.
- Freeze parameter-neighborhood topology, grid-edge handling, equality/zero-trade/no-loss-PF/NaN
  behavior, missing benchmark/stress behavior, regime definitions, concentration thresholds,
  catastrophic-fold rule, and adverse-seed pass proportion.
- Minimum candidate gates may be tightened before outer data but not loosened: positive aggregate
  normal- and moderate-cost expectancy, normal-cost PF at least 1.15, chained drawdown at most 10%,
  positive performance in a majority of required populated folds, risk/benchmark/random-entry
  value-add, broad parameter stability, no dominant pair/month/mania/few-trade dependence, and
  selection-adjusted evidence.
- Absolute profit, low exposure, or small sizing alone cannot pass.

### Forward paper-evaluation gate

- Historical success authorizes only a hash-frozen Freqtrade paper evaluation, never live trading.
- Freeze one calendar endpoint, adequacy interpretation, monitoring metrics, passive/randomized
  comparisons, safety shutdowns, and final efficacy gates before it starts. Never extend the clock
  to reach a trade count or significance threshold.
- Freqtrade dry-run simulates fills. If execution realism is claimed, independently capture
  contemporaneous quote/order-book shadow data; do not treat paper fills as realized queue,
  slippage, impact, or missed-fill evidence.
- Any safety shutdown is failed evidence and does not restart the clock. The frozen strategy cannot
  change during measurement.

## Mandatory review and freeze record

An independent fresh-context reviewer must return no unresolved BLOCK finding. The final protocol,
strategy, selection runner, eligibility calendar, benchmark/control code, resolved configuration,
dependency lock, source-data manifest, commands, seeds, and acceptance rules must then be SHA-256
hashed and immutably anchored before the first outer candle. Until every field above is resolved,
the only authorized action is no strategy run.
