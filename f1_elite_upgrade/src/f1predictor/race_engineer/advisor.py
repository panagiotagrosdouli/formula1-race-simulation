"""Rule-based AI Race Engineer advisor.

This is intentionally transparent and deterministic: it explains the reasoning
rather than pretending to be an opaque oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from f1predictor.strategy.advanced_strategy import undercut_gain


@dataclass
class RaceContext:
    driver: str = "LEC"
    current_lap: int = 24
    total_laps: int = 53
    current_compound: str = "MEDIUM"
    tire_age: int = 20
    gap_ahead_s: float = 2.0
    gap_behind_s: float = 4.0
    target_compound: str = "HARD"
    safety_car_probability: float = 0.10
    rain_probability: float = 0.05


def advise_pit_stop(ctx: RaceContext) -> Dict[str, object]:
    gain = undercut_gain(ctx.current_compound, ctx.target_compound, ctx.tire_age)
    risk_penalty = 0.8 * ctx.safety_car_probability + 0.6 * ctx.rain_probability
    attack_window = ctx.gap_ahead_s < 3.0 and ctx.gap_behind_s > 2.0
    net_score = gain - risk_penalty + (0.35 if attack_window else -0.15)

    if net_score > 0.7:
        decision = "PIT NOW"
    elif net_score > 0.15:
        decision = "PIT SOON"
    else:
        decision = "STAY OUT"

    explanation = [
        f"Estimated undercut gain: {gain:.2f}s on the next lap.",
        f"Risk penalty from SC/rain uncertainty: {risk_penalty:.2f}s.",
        "Attack window is open." if attack_window else "Attack window is not ideal.",
        f"Decision score: {net_score:.2f}.",
    ]

    return {
        "driver": ctx.driver,
        "decision": decision,
        "score": round(net_score, 3),
        "undercut_gain_s": round(gain, 3),
        "attack_window": attack_window,
        "explanation": explanation,
    }
