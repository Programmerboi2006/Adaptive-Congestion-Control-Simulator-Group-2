from .config import SimulationConfig
from .metrics import build_summary
from .simulation import simulate

SCENARIOS = {
    "Ideal / zero loss": {"loss_probability": 0.0, "rtt_ms": 40.0},
    "Low packet loss": {"loss_probability": 0.02, "rtt_ms": 80.0},
    "Moderate packet loss": {"loss_probability": 0.08, "rtt_ms": 100.0},
    "High packet loss": {"loss_probability": 0.20, "rtt_ms": 100.0},
    "High RTT": {"loss_probability": 0.05, "rtt_ms": 250.0},
    "High RTT + packet loss": {"loss_probability": 0.15, "rtt_ms": 250.0},
}


def apply_scenario(base: SimulationConfig, scenario_name: str) -> SimulationConfig:
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    values = base.to_dict()
    values.update(SCENARIOS[scenario_name])
    return SimulationConfig.from_dict(values)


def compare_algorithms(base: SimulationConfig) -> tuple[dict[str, object], dict[str, object]]:
    frames: dict[str, object] = {}
    summaries: dict[str, object] = {}
    for algorithm in ["TCP Tahoe", "TCP Reno", "AIMD"]:
        config = SimulationConfig.from_dict({**base.to_dict(), "algorithm": algorithm})
        frame = simulate(config)
        frames[algorithm] = frame
        summaries[algorithm] = build_summary(algorithm, frame, config.rtt_ms)
    return frames, summaries
