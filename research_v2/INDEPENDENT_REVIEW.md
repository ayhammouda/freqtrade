# Independent protocol review and disposition

Review date: 2026-08-22
Context: fresh, read-only quantitative-methodology review before the local research-v2 freeze
Initial disposition: **BLOCK**

Final scoped re-review after dispositions: **PASS — no remaining BLOCK issue for the zero-trial
audit/stop bundle**. This PASS does not assess future-template executability or authorize a strategy
run; the local hash manifest was still pending when the reviewer returned PASS.

## Controlling review conclusion

No strategy is eligible for dry-run and no historical search should continue. The correct
evidentiary verdict is **Research invalid because implementation or data problems remain**, with
**Historical evidence exhausted** as an independent stop. “No credible strategy found” may describe
the practical outcome, but the invalid legacy reassessment cannot prove a negative edge.

## Blocking findings and maintainer dispositions

| Finding | Disposition in the final local stop bundle |
|---|---|
| Synthetic gap filling contaminated RAvg inner selection | Accepted. RAvg is `invalid_selection_integrity`; legacy metrics are descriptive only. A repair may diagnose bias but cannot recreate unseen OOS evidence. |
| Draft mixed a current zero-trial stop memo with an incomplete future experiment | Accepted. `PROTOCOL.md` now governs only the audit/stop. All future design ideas moved to explicitly incomplete, non-authorizing `FUTURE_PROTOCOL_TEMPLATE.md`. |
| BTC/ETH-first sequencing could contaminate a later broad-universe test | Accepted in the template. Both variants must be frozen before one common outer horizon and corrected jointly, or the broad variant must wait for an entirely later horizon. |
| Legacy randomized entries conditioned on future holding durations | Accepted in the template. Randomized signals must rerun the complete causal exit, stop/gap, eligibility, allocator, risk, and cost engines. |
| Selection-adjusted inference was not reproducibly specified | Removed from the current zero-trial protocol. A future protocol must freeze exact resampling, sidedness, seeds, CI, full multiplicity family, and selection pipeline before evidence. The known Hyperopt floor is 3,530 epochs. |
| Several fold, stress, regime, and acceptance predicates were discretionary | Removed from the current zero-trial protocol. The template requires exact endpoints and behavior for underpopulation, NaN/zero-trade/no-loss PF, missing stresses, grid edges, regimes, adverse seeds, and stopping. |

## Major findings and dispositions

| Finding | Disposition |
|---|---|
| Fold-by-fold force exits distort trend returns | Future outer folds are reporting partitions of one continuous marked-to-market simulation. |
| Endpoint coverage is not a point-in-time eligibility calendar | `DATA_COVERAGE.csv` is labeled audit-only. Future work requires a dated raw-candle mask, immediate gap/delisting removal, and post-loader assertions. |
| Eligibility thresholds and capacity were unsupported | Removed as frozen rules. Future wallet, participation, listing, liquidity, and convergence thresholds remain required unresolved fields. |
| Risk formula/callback/cap semantics were incomplete | Current operative risk is zero. Future planned loss must include costs/adverse fill and freeze wallet, rounding, pending orders, cap semantics, and failure assertions under the 0.25%/0.75% ceilings. |
| Fee bumps were not a feasible fill model | Future protocol must freeze order types, separate cost components, implement gap stops, label unmeasured costs hypothetical, and define missing-detail fallback. |
| Passive/factor benchmarks were underspecified | Future formulas must freeze rebalancing, costs, scaling lookback/cap, no-leverage handling, timestamp alignment, and regression specification. |
| Integrity tools do not validate deployed portfolio callbacks | Future checks must cover every pair, prefix/truncation equivalence, allocator order, simultaneous signals, callback errors, exchange minimums, and risk assertions. |
| Horizon/trade-count rules allowed optional stopping | No current horizon exists. Any future historical or paper endpoint must be fixed in calendar time; inadequate information is insufficient and never extends the clock. |
| Worst-day tolerance was loose relative to heat | Removed as a current threshold. Future stress loss must be explicitly tied to the frozen heat budget. |
| Freqtrade paper mode cannot measure real execution | Future paper evaluation must be described as simulated; execution claims require independent quote/order-book shadow logging. |
| Local hashes are not an immutable chronology anchor | Accepted. This bundle is a local audit/stop freeze only. No performance run is authorized until a separately complete bundle is committed with user approval or externally timestamped. |

## Raw-timestamp reconciliation

The reviewer correctly identified contamination but initially inferred too much about outer entry
eligibility. A second independent archive audit compared every executed entry with original Feather
timestamps under a strict rule: the 600 raw 4h candles immediately before entry must be exactly 4h
apart and end at entry minus 4h.

| Archive population | Entries | Violations |
|---|---:|---:|
| Selected/reference outer archives | 4,004 | 0 |
| All 48-arm outer-grid diagnostics | 34,804 | 0 |
| All 48-arm inner-selection archives | 177,235 | 19,880 |

The narrow outer result does not restore valid nested selection. Every selected inner winner from
F3 through F8 contains affected trades, so the parameters evaluated outside were chosen using
synthetic-contaminated histories. Bias direction and magnitude are unknown. The preserved
reproduction is `scripts/audit_legacy_warmup.py`, with CSV and log outputs.

## Final disposition

The reviewer considered a stop/invalidity protocol freeze-worthy only if it authorized no strategy
run. The final bundle follows that structure. It is not an execution protocol, dry-run permission,
or immutable chronology anchor. The research action is to stop.
