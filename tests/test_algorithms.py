from core.algorithms import AIMDController, RenoController, TahoeController


def test_tahoe_loss_resets_cwnd_and_halves_ssthresh():
    c = TahoeController(20, 16)
    c.on_loss("triple_duplicate_ack")
    assert c.cwnd == 1
    assert c.ssthresh == 10


def test_reno_fast_recovery_keeps_half_window():
    c = RenoController(20, 16)
    c.on_loss("triple_duplicate_ack")
    assert c.ssthresh == 10
    assert c.cwnd == 10


def test_reno_timeout_resets_to_one():
    c = RenoController(20, 16)
    c.on_loss("timeout")
    assert c.cwnd == 1
    assert c.ssthresh == 10


def test_aimd_success_and_loss():
    c = AIMDController(4, 16)
    c.on_success()
    assert c.cwnd == 5
    c.on_loss("triple_duplicate_ack")
    assert c.cwnd == 2.5


def test_slow_start_then_congestion_avoidance():
    c = TahoeController(1, 4)
    c.on_success()
    assert c.cwnd == 2
    c.on_success()
    assert c.cwnd == 4
    c.on_success()
    assert c.cwnd == 5
