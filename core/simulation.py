from dataclasses import asdict, dataclass
import random
from typing import Any

import pandas as pd

from .algorithms import create_controller
from .config import SimulationConfig


@dataclass(frozen=True)
class RoundResult:
    round: int
    cwnd_before: float
    ssthresh_before: float | None
    packets_sent: int
    packets_lost: int
    packets_acked: int
    loss_occurred: bool
    feedback: str
    cwnd_after: float
    ssthresh_after: float | None
    time_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _feedback_for_loss(lost_packets: int, packets_sent: int) -> str:
    # Simplified approximation, not a packet-level TCP model.
    if packets_sent >= 4 and lost_packets == 1:
        return "triple_duplicate_ack"
    return "timeout"


def simulate(config: SimulationConfig) -> pd.DataFrame:
    config.validate()
    rng = random.Random(config.seed)
    controller = create_controller(
        config.algorithm, config.initial_cwnd, config.initial_ssthresh
    )
    results: list[RoundResult] = []

    for round_no in range(1, config.rounds + 1):
        cwnd_before = controller.cwnd
        ssthresh_before = controller.ssthresh
        packets_sent = max(1, int(round(cwnd_before)))
        packets_lost = sum(
            1 for _ in range(packets_sent) if rng.random() < config.loss_probability
        )
        packets_acked = packets_sent - packets_lost
        loss_occurred = packets_lost > 0
        feedback = "none"

        if loss_occurred:
            feedback = _feedback_for_loss(packets_lost, packets_sent)
            controller.on_loss(feedback)
        else:
            controller.on_success()

        results.append(
            RoundResult(
                round=round_no,
                cwnd_before=cwnd_before,
                ssthresh_before=ssthresh_before,
                packets_sent=packets_sent,
                packets_lost=packets_lost,
                packets_acked=packets_acked,
                loss_occurred=loss_occurred,
                feedback=feedback,
                cwnd_after=controller.cwnd,
                ssthresh_after=controller.ssthresh,
                time_ms=round_no * config.rtt_ms,
            )
        )

    return pd.DataFrame([r.to_dict() for r in results])
