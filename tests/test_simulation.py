import pandas as pd

from core.config import SimulationConfig
from core.simulation import simulate


def test_fixed_seed_is_reproducible():
    cfg = SimulationConfig(algorithm="TCP Reno", loss_probability=0.1, rounds=50, seed=99)
    assert simulate(cfg).equals(simulate(cfg))


def test_zero_loss_has_no_loss_events():
    df = simulate(SimulationConfig(loss_probability=0, rounds=25, seed=1))
    assert df["packets_lost"].sum() == 0
    assert not df["loss_occurred"].any()


def test_full_loss_is_handled():
    df = simulate(SimulationConfig(loss_probability=1, rounds=10, seed=1))
    assert df["packets_lost"].sum() == df["packets_sent"].sum()
    assert df["loss_occurred"].all()


def test_simulation_has_expected_columns_and_rows():
    df = simulate(SimulationConfig(rounds=7))
    expected = {"round", "cwnd_before", "ssthresh_before", "packets_sent", "packets_lost", "packets_acked", "loss_occurred", "feedback", "cwnd_after", "ssthresh_after", "time_ms"}
    assert set(df.columns) == expected
    assert len(df) == 7


def test_round_numbers_are_sequential():
    df = simulate(SimulationConfig(rounds=10))
    assert df["round"].tolist() == list(range(1, 11))
