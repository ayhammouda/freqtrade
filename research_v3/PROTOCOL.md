# Research v3 infrastructure preflight protocol

Status: **DRAFT — INFRASTRUCTURE ONLY; NO STRATEGY, BACKTEST, HYPEROPT, DRY-RUN, OR LIVE TRADING**

## Purpose

Research v2 froze with historical evidence exhausted and a legacy nested-selection integrity defect.
This phase does not attempt to repair a historical result or search for a strategy. It automates the
data-provenance, point-in-time fact generation, risk-sizing, and research-only configuration checks
that a future prospective protocol must pass before an independent review.

All existing local OHLCV remains consumed research data. It is used here only to test data plumbing
and generate audit facts. No statistic emitted by this phase is strategy performance evidence.

## Fixed scope

- Input: raw, unfilled Binance USDC daily Feather files already recorded by research v2.
- Output: a raw-calendar fact table, source manifest, deterministic preflight report, and tests.
- No Freqtrade strategy class, candidate parameter, signal, trade, portfolio simulation, order,
  credential, exchange connection, dry-run, or live action is permitted.
- The research-only configuration has no exchange section or credential-like field and explicitly
  disables dry-run and live-trading authorization.
- Risk code is pure arithmetic. It has no default strategy parameters and cannot place an order.
- The preflight invokes Freqtrade's local history loader only to compare its filled and unfilled
  timestamp sets against raw files. It does not instantiate a strategy, backtest, exchange, or order.

## Preflight acceptance gates

The bundle is ready for independent infrastructure review only when all of the following pass:

1. Each requested raw source is hashed, timestamp-ordered, unique, and represented in a calendar
   that preserves missing slots as missing facts rather than synthesizing OHLCV candles.
2. The calendar exposes raw presence, zero-volume observations, contiguous raw-history run length,
   and trailing 90-calendar-day completeness/zero-volume/turnover facts without declaring a pair
   eligible.
3. Any timestamp present in a post-loader dataframe but absent from raw source timestamps is a hard
   failure. Each preflight records local Freqtrade loader checks in filled and unfilled modes; a gap
   resets contiguous history.
4. Position stake arithmetic includes stop distance, entry cost, exit cost, and adverse fill; it
   respects supplied risk, heat, gross, slot, minimum-stake, and maximum-stake constraints.
5. Pair selection ordering is deterministic and independent of whitelist input order.
6. Unit tests, Ruff, the preflight command, source manifest checks, and a local artifact manifest
   pass from a clean process. The manifest excludes bytecode, test reports, caches, and itself.
7. A trailing 90-day completeness, zero-volume, or turnover fact is usable only when its companion
   `trailing_90d_expected_slots` equals 90; this phase does not convert that rule into eligibility.

## Explicit non-goals

This protocol does not authorize selection of the reserved BTC/ETH daily trend family, define an
outer horizon, set a liquidity threshold, or open a new trial budget. Those require a separate,
complete prospective protocol and a fresh independent review after this infrastructure gate passes.

## Integrity limitation

The SHA-256 manifest is a local integrity check, not an immutable timestamp anchor. A future
prospective protocol must obtain an external timestamp before its first unseen candle.
