# Research v3 preflight automation

This directory contains only strategy-neutral research infrastructure. It does not run Freqtrade,
connect to an exchange, or evaluate performance.

Run the deterministic preflight from the repository root:

```powershell
.\.venv\Scripts\python.exe -m research_v3.scripts.run_preflight `
  --repository . `
  --output-dir research_v3\artifacts `
  --config research_v3\configs\research_only_template.json

.\.venv\Scripts\python.exe -m research_v3.scripts.verify_preflight_bundle `
  --repository . `
  --output-dir research_v3\artifacts `
  --config research_v3\configs\research_only_template.json

.\.venv\Scripts\python.exe -m research_v3.scripts.freeze_hashes --root research_v3
.\.venv\Scripts\python.exe -m research_v3.scripts.freeze_hashes --root research_v3 --verify
```

Then run tests and static checks before writing the final manifest (test output is deliberately not
part of the manifest):

```powershell
.\.venv\Scripts\python.exe -m pytest research_v3\tests -q
.\.venv\Scripts\ruff.exe check research_v3
.\.venv\Scripts\ruff.exe format --check research_v3
.\.venv\Scripts\python.exe -m research_v3.scripts.freeze_hashes --root research_v3
.\.venv\Scripts\python.exe -m research_v3.scripts.freeze_hashes --root research_v3 --verify
```

Generated artifacts describe raw data quality and configuration safety only. They cannot be used as
strategy validation, eligibility, dry-run authorization, or a substitute for a future protocol.
