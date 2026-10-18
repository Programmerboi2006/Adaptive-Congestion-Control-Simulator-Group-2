import pytest

from core.config import SimulationConfig


@pytest.mark.parametrize(
    "field,value",
    [
        ("loss_probability", -0.1),
        ("loss_probability", 1.1),
        ("rtt_ms", 0),
        ("rounds", 0),
        ("initial_cwnd", 0),
        ("initial_ssthresh", 0),
    ],
)
def test_invalid_values_are_rejected(field, value):
    data = SimulationConfig().to_dict()
    data[field] = value
    with pytest.raises(ValueError):
        SimulationConfig.from_dict(data)


def test_invalid_algorithm_is_rejected():
    data = SimulationConfig().to_dict()
    data["algorithm"] = "TCP Cubic"
    with pytest.raises(ValueError):
        SimulationConfig.from_dict(data)
