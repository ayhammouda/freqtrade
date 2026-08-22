# Research v3 Reproduction Commands

Run from the repository root in a clean process. These commands perform no strategy evaluation,
exchange access, dry-run, or live action.

```powershell
.\.venv\Scripts\python.exe -m pytest research_v3\tests -q
.\.venv\Scripts\ruff.exe check research_v3
.\.venv\Scripts\ruff.exe format --check research_v3
.\.venv\Scripts\python.exe -m research_v3.scripts.run_preflight --repository . --output-dir research_v3\artifacts --config research_v3\configs\research_only_template.json
.\.venv\Scripts\python.exe -m research_v3.scripts.verify_preflight_bundle --repository . --output-dir research_v3\artifacts --config research_v3\configs\research_only_template.json
.\.venv\Scripts\python.exe -m research_v3.scripts.freeze_hashes --root research_v3
.\.venv\Scripts\python.exe -m research_v3.scripts.freeze_hashes --root research_v3 --verify
```

The manifest intentionally excludes bytecode, caches, test reports, and itself so the final two
commands remain reproducible after tests run.
