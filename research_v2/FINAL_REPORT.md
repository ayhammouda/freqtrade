# Research invalid because implementation or data problems remain

Status: final local audit/stop report, hash-frozen 2026-08-22T13:39:45+02:00; not an immutable
execution freeze.

## Decision

No strategy is eligible for Freqtrade dry-run. Take no trading action and do not run another
historical search. USDC cash remains the research comparator, not an allocation recommendation.

Taken at face value, the legacy ReinforcedAverageStrategy outputs were not dry-run quality: pooled
risk-model PF 1.09, chained drawdown 10.9%, a daily-return interval spanning zero, performance below
its exposure-path basket, mean randomized-entry percentile 54, negative profit after removing the
five largest trades, and DSR below the frozen threshold. Supertrend, CCI, and CombinedBinHAndCluc
had also failed their stated validation/holdout gates. These values are descriptive, not a valid
negative performance conclusion, because the controlling nested selection was contaminated.

The fresh-context review found that prior Freqtrade backtests filled long missing USDC periods with
synthetic flat, zero-volume candles even though an earlier protocol said gaps were not synthesized.
A raw-timestamp reconciliation narrows the defect: 0 of 4,004 selected/reference outer entries and
0 of 34,804 outer-grid entries violate the strict 600-candle raw warm-up, but 19,880 of 177,235
inner-grid entries do. The indicators consume those fills, and every selected inner winner from F3
through F8 includes affected trades. The outer parameters therefore came from an invalid clean-
selection process. Bias direction is unknown. Because every historical fold is already consumed,
a corrected rerun would be retrospective and cannot restore missing confirmation.

## Why research stops

All locally available historical periods have been inspected for coverage, design, validation,
holdout, recent-window behavior, or walk-forward results. Reusing a pair subset, timeframe, or old
period would not make it unseen. Research v2 freezes the new historical trial budget at zero instead
of manufacturing another holdout. The unresolved inner-selection defect independently triggers the
invalid-research stop.

## Limitations

- Failure to find evidence is not proof that all long-only crypto strategies have negative edge.
- Binance USDC history is discontinuous because of delistings/relistings and has limited independent
  regimes.
- Prior research tried a large and only partly reconstructable number of configurations, making
  marginal historical statistics especially untrustworthy.
- The strongest surviving evidence concerns conservative risk containment, not signal quality.
  Small sizing bounded losses but did not create expectancy.
- Prior candidates were not compared under the requested common 0.25% position-risk / 0.75% heat
  budget, and the mandatory BTC/ETH-only baseline was never performed.

## Next justified action

No dry-run is justified now. The next potentially valid evidence must be genuinely future and
governed by a new, complete protocol frozen and immutably anchored before its first outer candle.
`FUTURE_PROTOCOL_TEMPLATE.md` records the unresolved design fields; it is deliberately
non-authorizing. A future programme should begin from one transparent 1d absolute-momentum or
Donchian hypothesis on BTC/ETH only and keep the 0.25% position-risk / 0.75% heat ceilings, but no
entry, exit, parameter, data horizon, or experiment is approved by this report.

Historical evidence permits neither live trading nor a frozen dry-run in the current repository.
