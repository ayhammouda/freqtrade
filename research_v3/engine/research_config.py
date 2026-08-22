"""Validation for safe, non-executable research configuration snapshots."""

from __future__ import annotations

from typing import Any


FORBIDDEN_KEY_PARTS = ("api_key", "apikey", "secret", "password", "token")


def _walk_keys(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, list):
        return [
            key
            for index, item in enumerate(value)
            for key in _walk_keys(item, f"{prefix}[{index}]")
        ]
    if not isinstance(value, dict):
        return []
    keys: list[str] = []
    for key, child in value.items():
        location = f"{prefix}.{key}" if prefix else str(key)
        keys.append(location)
        keys.extend(_walk_keys(child, location))
    return keys


def validate_research_only_config(config: dict[str, Any]) -> None:
    """Reject configuration that could name an executable strategy or contain credentials."""
    credential_keys = [
        key
        for key in _walk_keys(config)
        if any(part in key.lower() for part in FORBIDDEN_KEY_PARTS)
    ]
    if credential_keys:
        raise ValueError(f"Credential-like configuration keys are forbidden: {credential_keys}")
    required = {
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
        "schema": "research_v3_non_executable_contract_v1",
        "not_a_freqtrade_config": True,
    }
    failures = {
        key: {"expected": expected, "actual": config.get(key)}
        for key, expected in required.items()
        if config.get(key) != expected
    }
    if failures:
        raise ValueError(f"Research-only configuration is not safe: {failures}")
    unknown = set(config).difference(required)
    if unknown:
        raise ValueError(f"Research-only configuration has unknown keys: {sorted(unknown)}")
