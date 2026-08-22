# Research v2 command record

All commands below are read-only or generate new audit files under `research_v2/`. No strategy
backtest, Hyperopt, exchange order, credential change, commit, or push was run.

## Environment and repository

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
git describe --tags --always --dirty
.\.venv\Scripts\python.exe -m freqtrade --version
.\.venv\Scripts\python.exe --version
```

Package versions recorded in `DEPENDENCIES.txt` were obtained with Python
`importlib.metadata.version()`; no dependency was installed or changed.

## Local data inventory

```powershell
.\.venv\Scripts\python.exe -m freqtrade list-data `
  --config user_data\config.json --show-timerange
```

Only non-secret output fields were used. The local runtime configuration was not copied because it
contains populated credential fields.

## Deterministic data coverage audit

```powershell
.\.venv\Scripts\python.exe research_v2\scripts\audit_data_coverage.py `
  --repository . `
  --output research_v2\DATA_COVERAGE.csv `
  --log research_v2\logs\data_coverage_audit.txt
```

## Legacy warm-up reconciliation

```powershell
.\.venv\Scripts\python.exe research_v2\scripts\audit_legacy_warmup.py `
  --repository . `
  --output research_v2\LEGACY_WARMUP_AUDIT.csv `
  --log research_v2\logs\legacy_warmup_audit.txt
```

This parses preserved result ZIPs and original Feather timestamps. It does not execute a strategy
or recalculate a signal.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest research_v2\tests -q `
  --junitxml=research_v2\logs\pytest.xml
.\.venv\Scripts\ruff.exe check research_v2
.\.venv\Scripts\ruff.exe format --check research_v2
.\.venv\Scripts\python.exe research_v2\scripts\verify_bundle.py `
  --repository . --log research_v2\logs\bundle_verification.txt
git diff --check
```

## Local hash freeze

Run only after final review dispositions and verification are recorded:

```powershell
.\.venv\Scripts\python.exe research_v2\scripts\freeze_hashes.py `
  --repository . --output research_v2\ARTIFACT_HASHES.sha256
.\.venv\Scripts\python.exe research_v2\scripts\freeze_hashes.py `
  --repository . --output research_v2\ARTIFACT_HASHES.sha256 --verify
```

The manifest is a local integrity check, not an immutable timestamp or permission to run a
candidate.
