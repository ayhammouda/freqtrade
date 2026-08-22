# Repository Guidelines

## Project Structure & Module Organization

Core Python code lives in `freqtrade/`, organized by domain: exchange integrations, configuration, persistence, RPC/API services, strategies, optimization, and FreqAI. The standalone REST client is packaged under `ft_client/freqtrade_client/`. Tests live in `tests/` and generally mirror the production modules; shared fixtures are in `tests/conftest*.py`, while sample candles, trades, and configurations are under `tests/testdata/`. Documentation is built from `docs/`, with images and other static files in `docs/assets/`. Use `config_examples/` and `user_data/` for example and local runtime content, and `docker/` for specialized Compose setups.

## Build, Test, and Development Commands

- `pip install -r requirements-dev.txt` installs test, lint, and typing tools.
- `pip install -e ".[all]"` installs Freqtrade and optional features in editable mode; use `pip install -e ./ft_client` when changing the REST client.
- `pytest` runs the full suite. Narrow runs with `pytest tests/test_wallets.py` or `pytest tests/test_wallets.py::test_name`.
- `pre-commit run -a` runs Ruff, Ruff formatting, mypy, codespell, and repository checks.
- `python -m build --sdist --wheel` creates release artifacts in `dist/`.
- `pip install -r docs/requirements-docs.txt && mkdocs serve` previews documentation locally.

## Coding Style & Naming Conventions

Target Python 3.11 or newer. Use four-space indentation, a 100-character line limit, and standard Python naming: `snake_case` for modules/functions, `PascalCase` for classes, and `UPPER_CASE` for constants. Ruff owns formatting, linting, and import order; mypy checks production code. Add reStructuredText-style docstrings to public methods, using double quotes.

## Testing Guidelines

Write pytest tests in `test_*.py` files with `test_*` functions. New features require unit tests, and bug fixes should include a regression test. Keep deterministic fixtures near the relevant test module or in existing `conftest.py` files. CI runs randomized, parallel, and coverage-enabled suites; run the focused test while developing, then the full suite before submission.

## Commit & Pull Request Guidelines

Recent commits use short imperative subjects with prefixes such as `feat:`, `fix:`, `test:`, and `chore:`. Keep commits focused and written in English. Open PRs against `develop`, not `stable`. Follow the PR template: summarize the goal, link the issue, list the changelog, and explain behavior changes; include visuals when UI output changes. Ensure tests, pre-commit checks, and relevant documentation pass. Disclose AI assistance in the PR description and personally review all generated changes.

## Security & Configuration

Never commit exchange keys, tokens, private configuration, databases, or generated trading data. Use dry-run mode for validation and keep machine-specific settings under ignored local files in `user_data/`.

## Quantitative Research Invariants

- Treat every period, pair/timeframe slice, result, diagnostic, and benchmark already inspected as consumed research data. Never relabel it as fresh validation or holdout evidence; raw archives and command logs override narrative summaries.
- Freeze the protocol, trial budget, strategy family, timeframe, parameter/search bounds, point-in-time eligibility, costs, benchmarks, statistics, acceptance rules, and failure branches before performance is opened. Do not expand the budget or loosen a gate after disappointment.
- Compare candidates on one declared equity-risk model. Position sizing may bound loss but never creates edge. Default ceilings are 0.25% pre-entry equity loss per position, 0.75% total/correlated heat, and the frozen gross-exposure cap.
- Audit raw and post-loader candles. Synthetic gap fills, incomplete informative candles, warm-up instability, survivorship, pair-order allocation, or any risk-cap breach are validity failures; a behavior-changing repair consumes revealed data.
- Historical evidence can authorize only a hash-frozen dry-run, never live trading. Do not enable live mode, place orders, use leverage/margin/futures/shorts, or claim future profitability. Do not change a frozen strategy during its measurement period.
