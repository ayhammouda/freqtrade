# Independent Review Request — Research V3 Preflight Harness

## Scope

Review the research-v3 infrastructure only. It is deliberately strategy-neutral and non-executable:
there is no candidate, backtest, Hyperopt run, dry-run, live configuration, exchange, or credential.

## Evidence to inspect

1. `PROTOCOL.md` — scope and authorization boundary.
2. `configs/research_only_template.json` — safe configuration contract.
3. `engine/raw_data.py` — raw-only provenance, gap preservation, and contiguous-history logic.
4. `engine/risk.py` — pure conservative sizing arithmetic with explicit limits.
5. `scripts/run_preflight.py` and `scripts/verify_preflight_bundle.py` — deterministic artifact
   creation and validation.
6. `artifacts/RAW_SOURCE_MANIFEST.csv`, `artifacts/RAW_DAILY_CALENDAR.csv`, and
   `artifacts/PREFLIGHT_REPORT.json` — preserved output.
7. `ARTIFACT_HASHES.sha256` — bundle integrity manifest.

## Questions for the reviewer

1. Can any loader path silently create a timestamp or an OHLCV value absent from raw data?
2. Does every downstream eligibility decision have enough raw facts to enforce point-in-time
   listing age, continuity, completeness, zero-volume, liquidity, and indicator warm-up rules?
3. Can a configuration or command authorize a strategy, backtest, dry-run, live order, exchange, or
   credential use despite the stated controls?
4. Does position sizing use explicit effective loss and caps rather than an unstated fixed stake?
5. Are the files and outputs sufficient to reproduce and independently verify the preflight result?

## Required conclusion

State one of:

- `Infrastructure controls pass; research authorization still requires a new protocol review.`
- `Infrastructure controls require remediation before any research protocol can be proposed.`

Neither conclusion permits trading. A future strategy programme still requires genuinely unused data
and a separately reviewed, frozen protocol.
