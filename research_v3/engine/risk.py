"""Pure stake-sizing primitives for a future conservative research protocol.

No values in this module are strategy defaults. Callers must explicitly provide every limit and
cost input, which keeps policy choices visible to a future protocol and independent reviewer.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


POLICY_MAX_INTENDED_RISK_FRACTION = 0.0025
POLICY_MAX_HEAT_FRACTION = 0.0075
POLICY_MAX_GROSS_EXPOSURE_FRACTION = 1.0


@dataclass(frozen=True)
class PositionRiskInputs:
    """Explicit inputs for one prospective stake decision.

    ``existing_heat_fraction`` is the sum of each open position's stake multiplied by its own
    effective-loss fraction, divided by account equity.  It is not gross notional exposure.
    ``effective_loss_fraction`` remains a modeled stop-fill loss, not a worst-case gap-loss bound.
    """

    equity: float
    intended_risk_fraction: float
    stop_distance_fraction: float
    entry_cost_fraction: float
    exit_cost_fraction: float
    adverse_fill_fraction: float
    existing_heat_fraction: float
    maximum_heat_fraction: float
    existing_gross: float
    maximum_gross_fraction: float
    open_positions: int
    maximum_positions: int
    minimum_stake: float
    maximum_stake: float


@dataclass(frozen=True)
class StakeDecision:
    status: str
    stake: float
    effective_loss_fraction: float
    intended_loss: float
    realized_intended_loss: float
    limiting_constraint: str


def _validate(inputs: PositionRiskInputs) -> None:
    values = (
        inputs.equity,
        inputs.intended_risk_fraction,
        inputs.stop_distance_fraction,
        inputs.entry_cost_fraction,
        inputs.exit_cost_fraction,
        inputs.adverse_fill_fraction,
        inputs.existing_heat_fraction,
        inputs.maximum_heat_fraction,
        inputs.existing_gross,
        inputs.maximum_gross_fraction,
        inputs.minimum_stake,
        inputs.maximum_stake,
    )
    if not all(isfinite(value) for value in values):
        raise ValueError("All risk inputs must be finite")
    if inputs.equity <= 0 or inputs.minimum_stake <= 0 or inputs.maximum_stake <= 0:
        raise ValueError("Equity and stake limits must be positive")
    if inputs.minimum_stake > inputs.maximum_stake:
        raise ValueError("minimum_stake cannot exceed maximum_stake")
    if not 0 < inputs.intended_risk_fraction <= POLICY_MAX_INTENDED_RISK_FRACTION:
        raise ValueError("intended_risk_fraction exceeds the frozen policy ceiling")
    if inputs.stop_distance_fraction <= 0:
        raise ValueError("stop_distance_fraction must be positive")
    if inputs.maximum_heat_fraction > POLICY_MAX_HEAT_FRACTION:
        raise ValueError("maximum_heat_fraction exceeds the frozen policy ceiling")
    if inputs.maximum_gross_fraction > POLICY_MAX_GROSS_EXPOSURE_FRACTION:
        raise ValueError("maximum_gross_fraction exceeds the frozen policy ceiling")
    if any(
        value < 0
        for value in (
            inputs.stop_distance_fraction,
            inputs.entry_cost_fraction,
            inputs.exit_cost_fraction,
            inputs.adverse_fill_fraction,
            inputs.existing_heat_fraction,
            inputs.maximum_heat_fraction,
            inputs.existing_gross,
            inputs.maximum_gross_fraction,
        )
    ):
        raise ValueError("Risk distances, exposure, and limits cannot be negative")
    if inputs.open_positions < 0 or inputs.maximum_positions <= 0:
        raise ValueError("Position counts are invalid")


def calculate_capped_stake(inputs: PositionRiskInputs) -> StakeDecision:
    """Size one potential position, reducing or skipping rather than oversizing it."""
    _validate(inputs)
    effective_loss = (
        inputs.stop_distance_fraction
        + inputs.entry_cost_fraction
        + inputs.exit_cost_fraction
        + inputs.adverse_fill_fraction
    )
    if effective_loss <= 0:
        raise ValueError("Effective loss distance must be positive")
    intended_loss = inputs.equity * inputs.intended_risk_fraction
    if inputs.open_positions >= inputs.maximum_positions:
        return StakeDecision("skip", 0.0, effective_loss, intended_loss, 0.0, "position_slots")

    risk_stake = intended_loss / effective_loss
    heat_capacity = max(0.0, inputs.maximum_heat_fraction - inputs.existing_heat_fraction)
    heat_stake = (inputs.equity * heat_capacity) / effective_loss
    gross_stake = max(0.0, inputs.equity * inputs.maximum_gross_fraction - inputs.existing_gross)
    candidates = (
        ("risk", risk_stake),
        ("heat", heat_stake),
        ("gross", gross_stake),
        ("exchange_maximum", inputs.maximum_stake),
    )
    limiting_constraint, stake = min(enumerate(candidates), key=lambda item: (item[1][1], item[0]))[
        1
    ]
    if stake < inputs.minimum_stake:
        return StakeDecision("skip", 0.0, effective_loss, intended_loss, 0.0, limiting_constraint)
    return StakeDecision(
        "accept",
        stake,
        effective_loss,
        intended_loss,
        stake * effective_loss,
        limiting_constraint,
    )


def deterministic_pair_order(pairs: list[str]) -> list[str]:
    """Return a duplicate-free lexical order independent of whitelist input order."""
    if any(not pair or not isinstance(pair, str) for pair in pairs):
        raise ValueError("Pairs must be non-empty strings")
    return sorted(set(pairs))
