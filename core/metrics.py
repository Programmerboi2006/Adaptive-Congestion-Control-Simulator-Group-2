import math
from typing import Any

import pandas as pd


def calculate_metrics(df: pd.DataFrame, rtt_ms: float) -> dict[str, Any]:
    if df.empty:
        return {
            "throughput_packets_per_second": 0.0,
            "packet_loss_rate": 0.0,
            "average_cwnd": 0.0,
            "congestion_events": 0,
            "recovery_time_ms": None,
            "successful_packets": 0,
            "lost_packets": 0,
            "rounds": 0,
        }

    sent = int(df["packets_sent"].sum())
    lost = int(df["packets_lost"].sum())
    successful = int(df["packets_acked"].sum())
    total_time_s = len(df) * rtt_ms / 1000.0
    throughput = successful / total_time_s if total_time_s > 0 else 0.0
    loss_rate = lost / sent if sent else 0.0
    average_cwnd = float(df["cwnd_before"].mean())
    events = int(df["loss_occurred"].sum())
    recovery = recovery_time_ms(df, rtt_ms)

    return {
        "throughput_packets_per_second": throughput,
        "packet_loss_rate": loss_rate,
        "average_cwnd": average_cwnd,
        "congestion_events": events,
        "recovery_time_ms": recovery,
        "successful_packets": successful,
        "lost_packets": lost,
        "rounds": len(df),
    }


def recovery_time_ms(df: pd.DataFrame, rtt_ms: float) -> float | None:
    """Return mean RTT-based recovery time after losses.

    Recovery is defined as the number of subsequent rounds needed for cwnd_after
    to reach the cwnd_before of the loss round. If that level is not reached
    before the experiment ends, that event is excluded from the mean.
    """
    recovery_times: list[float] = []
    rows = df.reset_index(drop=True)
    for idx, row in rows.iterrows():
        if not row["loss_occurred"]:
            continue
        target = float(row["cwnd_before"])
        for next_idx in range(idx + 1, len(rows)):
            if float(rows.loc[next_idx, "cwnd_after"]) >= target:
                recovery_times.append((next_idx - idx) * rtt_ms)
                break
    if not recovery_times:
        return None
    return float(sum(recovery_times) / len(recovery_times))


def build_summary(name: str, df: pd.DataFrame, rtt_ms: float) -> dict[str, Any]:
    return {"algorithm": name, **calculate_metrics(df, rtt_ms)}


def format_metrics(metrics: dict[str, Any]) -> dict[str, str]:
    recovery = metrics["recovery_time_ms"]
    return {
        "Throughput": f"{metrics['throughput_packets_per_second']:.2f} pkt/s",
        "Packet loss": f"{metrics['packet_loss_rate'] * 100:.2f}%",
        "Average cwnd": f"{metrics['average_cwnd']:.2f} packets",
        "Congestion events": str(metrics["congestion_events"]),
        "Recovery time": "N/A" if recovery is None or math.isnan(recovery) else f"{recovery:.1f} ms",
    }
