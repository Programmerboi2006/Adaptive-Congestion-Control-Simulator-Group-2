from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class SimulationConfig:
    algorithm: str = "TCP Reno"
    loss_probability: float = 0.05
    rtt_ms: float = 100.0
    rounds: int = 100
    initial_cwnd: float = 1.0
    initial_ssthresh: float = 16.0
    seed: int = 42

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self.algorithm not in {"TCP Tahoe", "TCP Reno", "AIMD"}:
            raise ValueError("algorithm must be TCP Tahoe, TCP Reno, or AIMD")
        if not 0 <= self.loss_probability <= 1:
            raise ValueError("loss_probability must be between 0 and 1")
        if self.rtt_ms <= 0:
            raise ValueError("rtt_ms must be greater than 0")
        if self.rounds < 1:
            raise ValueError("rounds must be at least 1")
        if self.initial_cwnd <= 0:
            raise ValueError("initial_cwnd must be greater than 0")
        if self.initial_ssthresh <= 0:
            raise ValueError("initial_ssthresh must be greater than 0")
        if not isinstance(self.seed, int):
            raise ValueError("seed must be an integer")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SimulationConfig":
        return cls(**data)