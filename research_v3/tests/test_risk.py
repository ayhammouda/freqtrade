# ruff: noqa: S101

import pytest

from research_v3.engine.risk import (
    PositionRiskInputs,
    calculate_capped_stake,
    deterministic_pair_order,
)


def inputs(**overrides: object) -> PositionRiskInputs:
    base: dict[str, object] = {
        "equity": 10_000.0,
        "intended_risk_fraction": 0.0025,
        "stop_distance_fraction": 0.10,
        "entry_cost_fraction": 0.0015,
        "exit_cost_fraction": 0.0015,
        "adverse_fill_fraction": 0.005,
        "existing_heat_fraction": 0.0,
        "maximum_heat_fraction": 0.0075,
        "existing_gross": 0.0,
        "maximum_gross_fraction": 0.10,
        "open_positions": 0,
        "maximum_positions": 3,
        "minimum_stake": 10.0,
        "maximum_stake": 1_000.0,
    }
    return PositionRiskInputs(**(base | overrides))


def test_stake_includes_costs_and_respects_intended_loss() -> None:
    decision = calculate_capped_stake(inputs())

    assert decision.status == "accept"
    assert decision.effective_loss_fraction == pytest.approx(0.108)
    assert decision.realized_intended_loss <= decision.intended_loss
    assert decision.stake == pytest.approx(25 / 0.108)


def test_heat_and_gross_limits_reduce_or_skip_stake() -> None:
    heat_limited = calculate_capped_stake(inputs(existing_heat_fraction=0.0065))
    gross_limited = calculate_capped_stake(inputs(existing_gross=950.0))
    skipped = calculate_capped_stake(inputs(existing_gross=999.0, minimum_stake=20.0))

    assert heat_limited.limiting_constraint == "heat"
    assert gross_limited.limiting_constraint == "gross"
    assert skipped.status == "skip"


def test_slots_and_pair_order_are_deterministic() -> None:
    decision = calculate_capped_stake(inputs(open_positions=3))

    assert decision.status == "skip"
    assert decision.limiting_constraint == "position_slots"
    assert deterministic_pair_order(["SOL/USDC", "BTC/USDC", "SOL/USDC"]) == [
        "BTC/USDC",
        "SOL/USDC",
    ]


def test_policy_ceilings_and_constraint_ties_are_conservative() -> None:
    with pytest.raises(ValueError, match="policy ceiling"):
        calculate_capped_stake(inputs(intended_risk_fraction=0.01))
    with pytest.raises(ValueError, match="policy ceiling"):
        calculate_capped_stake(inputs(maximum_heat_fraction=0.01))
    with pytest.raises(ValueError, match="positive"):
        calculate_capped_stake(inputs(stop_distance_fraction=0.0))

    tied = calculate_capped_stake(inputs(maximum_stake=25 / 0.108, maximum_gross_fraction=1.0))
    assert tied.limiting_constraint == "risk"
