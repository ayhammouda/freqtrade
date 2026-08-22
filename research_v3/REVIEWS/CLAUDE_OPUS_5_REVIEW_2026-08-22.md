# Claude Opus 5 Independent Re-Audit — 2026-08-22

## Method and scope

- Model: `claude-opus-5` (Claude Code CLI model alias `opus`).
- Mode: fresh, tool-free, read-only review at maximum effort.
- Reviewed commit: `fe2dc52fc` on `codex/research-v2-audit-stop`.
- Predecessors in scope: v2 freeze `975b7ef10`; initial v3 harness `ec0c4ea29`.
- Excluded: untracked `research_v2/data_rebuild/`, raw Feather files, and the large raw-calendar
  CSV. The reviewer was supplied the implementation, tests, protocols, manifests, curated command
  evidence, and source summaries instead.

## Verdict

**Infrastructure controls pass; research authorization still requires a new protocol review.**

The review found no remaining blocker or high-severity issue. It explicitly did not authorize a
strategy search, backtest optimisation, dry-run, exchange connection, credential use, or live
trading.

## Accepted remediation evidence

- `freeze_hashes.py` excludes runtime bytecode, caches, JUnit XML, and its own manifest; its
  regression test proves those exclusions. The post-test verification reports 27 artifacts.
- `run_preflight.py` invokes the local Freqtrade history loader in both modes. On the approved daily
  data, unfilled mode preserved all 17,851 raw timestamps and filled mode exposed 3,658 synthetic
  timestamps, equal to the recorded raw gaps.
- Position-risk and total-heat ceilings are executable and tested. Zero stop distance is rejected;
  tied constraints are deterministic.
- Calendar raw-presence counts reconcile per pair with the source manifest. The safe configuration
  contract now recurses through lists and rejects unknown keys.
- Commands, dependency snapshot, warm-up/ramp-in guidance, and local-manifest limitations are now
  recorded.

## Remaining follow-ups (not audit blockers)

1. Sort hash inputs by the rendered POSIX relative path to make manifest ordering cross-platform.
2. Assert filled synthetic timestamp counts per pair, not only in aggregate; add negative tests for
   every verifier rejection branch.
3. State and assert the source-discovery rule for the fixed 11-pair universe.
4. Before a future protocol, either wire `has_contiguous_raw_prefix` into an approved eligibility
   path or explicitly reserve it; document observed-slot requirements for liquidity facts and the
   conservative limits of aggregate heat/gap-risk arithmetic.

## Independent-review limitations

The reviewer could verify implementation logic and supplied arithmetic but not raw-file hashes,
large-calendar contents, or untracked material. The SHA-256 manifest remains a local integrity
check, not a trusted external timestamp.

## Reproduction evidence

At this reviewed commit, the recorded command sequence completed with:

- `14 passed` for `pytest research_v3/tests -q` (only PyArrow Feather deprecation warnings).
- Ruff check and format check passed.
- Preflight and bundle verification passed with 11 pairs and 21,509 daily fact rows.
- `freeze_hashes --verify` passed with 27 artifacts after tests ran.

This record preserves review evidence only. It does not change the consumed-data rule or permit any
form of trading.
