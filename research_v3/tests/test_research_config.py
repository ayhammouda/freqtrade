import json
from pathlib import Path

import pytest

from research_v3.engine.research_config import validate_research_only_config


def valid_config() -> dict[str, object]:
    return {
        "schema": "research_v3_non_executable_contract_v1",
        "not_a_freqtrade_config": True,
        "status": "research_only_not_executable",
        "purpose": "infrastructure_preflight",
        "trading_mode": "spot",
        "stake_currency": "USDC",
        "margin_mode": None,
        "exchange": None,
        "candidate_strategy": None,
        "historical_strategy_trials_authorized": 0,
        "dry_run_authorized": False,
        "live_trading_authorized": False,
    }


def test_template_is_safe() -> None:
    template = Path("research_v3/configs/research_only_template.json")

    validate_research_only_config(json.loads(template.read_text(encoding="utf-8")))


def test_credential_like_key_is_rejected() -> None:
    config = valid_config() | {"api_key": "not-a-real-key"}

    with pytest.raises(ValueError, match="Credential-like"):
        validate_research_only_config(config)


def test_strategy_or_dry_run_authorization_is_rejected() -> None:
    config = valid_config() | {"candidate_strategy": "Unsafe", "dry_run_authorized": True}

    with pytest.raises(ValueError, match="not safe"):
        validate_research_only_config(config)


def test_nested_credentials_and_unknown_keys_are_rejected() -> None:
    with pytest.raises(ValueError, match="Credential-like"):
        validate_research_only_config(valid_config() | {"exchanges": [{"api_key": "x"}]})
    with pytest.raises(ValueError, match="unknown keys"):
        validate_research_only_config(valid_config() | {"ccxt_config": {}})
