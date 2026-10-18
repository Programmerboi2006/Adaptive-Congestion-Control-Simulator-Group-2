from dataclasses import dataclass


@dataclass
class CongestionState:
    cwnd: float
    ssthresh: float | None


class CongestionController:
    name = "Base"

    def __init__(self, initial_cwnd: float, initial_ssthresh: float):
        self.state = CongestionState(initial_cwnd, initial_ssthresh)

    def on_success(self) -> None:
        raise NotImplementedError

    def on_loss(self, event: str) -> None:
        raise NotImplementedError

    @property
    def cwnd(self) -> float:
        return self.state.cwnd

    @property
    def ssthresh(self) -> float | None:
        return self.state.ssthresh

    def _increase(self) -> None:
        if self.state.ssthresh is not None and self.state.cwnd < self.state.ssthresh:
            self.state.cwnd *= 2.0
        else:
            self.state.cwnd += 1.0


class TahoeController(CongestionController):
    name = "TCP Tahoe"

    def on_success(self) -> None:
        self._increase()

    def on_loss(self, event: str) -> None:
        self.state.ssthresh = max(self.state.cwnd / 2.0, 1.0)
        self.state.cwnd = 1.0


class RenoController(CongestionController):
    name = "TCP Reno"

    def on_success(self) -> None:
        self._increase()

    def on_loss(self, event: str) -> None:
        self.state.ssthresh = max(self.state.cwnd / 2.0, 1.0)
        if event == "triple_duplicate_ack":
            self.state.cwnd = self.state.ssthresh
        else:
            self.state.cwnd = 1.0


class AIMDController(CongestionController):
    name = "AIMD"

    def __init__(self, initial_cwnd: float, initial_ssthresh: float):
        super().__init__(initial_cwnd, None)

    def on_success(self) -> None:
        self.state.cwnd += 1.0

    def on_loss(self, event: str) -> None:
        self.state.cwnd = max(self.state.cwnd / 2.0, 1.0)


def create_controller(name: str, initial_cwnd: float, initial_ssthresh: float) -> CongestionController:
    controllers = {
        "TCP Tahoe": TahoeController,
        "TCP Reno": RenoController,
        "AIMD": AIMDController,
    }
    try:
        return controllers[name](initial_cwnd, initial_ssthresh)
    except KeyError as exc:
        raise ValueError(f"Unknown algorithm: {name}") from exc
