from pathlib import Path
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.config import SimulationConfig
from core.experiments import SCENARIOS, apply_scenario, compare_algorithms
from core.export import (
    dataframe_csv_bytes,
    json_bytes,
    ensure_output_dir,
    save_dataframe,
    save_json,
)
from core.metrics import calculate_metrics, format_metrics
from core.simulation import simulate

st.set_page_config(
    page_title="Adaptive Congestion-Control Simulator",
    page_icon="CN",
    layout="wide",
)

st.markdown("""
<style>
.block-container { max-width: 1400px; padding-top: 2rem; padding-bottom: 3rem; }
.metric-card { border: 1px solid #d9dee7; border-radius: 10px; padding: 14px 16px; background: #f8fafc; }
.small-muted { color: #64748b; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

ALGORITHMS = ["TCP Tahoe", "TCP Reno", "AIMD"]


def config_sidebar() -> SimulationConfig:
    st.sidebar.header("Simulation controls")
    loaded = st.session_state.get("loaded_config")
    if loaded:
        st.sidebar.success("Saved configuration loaded.")
    with st.sidebar.expander("Load saved configuration"):
        uploaded = st.file_uploader("Upload JSON configuration", type=["json"], key="config_upload")
        if uploaded is not None and st.button("Apply configuration", key="apply_config"):
            try:
                data = json.load(uploaded)
                cfg = SimulationConfig.from_dict(data)
                st.session_state["loaded_config"] = cfg.to_dict()
                st.rerun()
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                st.error(f"Invalid configuration: {exc}")
    defaults = st.session_state.get("loaded_config", SimulationConfig().to_dict())
    algorithm = st.sidebar.selectbox("Algorithm", ALGORITHMS, index=ALGORITHMS.index(defaults["algorithm"]), key="algorithm_control")
    loss = st.sidebar.slider("Packet-loss probability", 0.0, 1.0, float(defaults["loss_probability"]), 0.01, key="loss_control")
    rtt = st.sidebar.number_input("RTT (ms)", min_value=1.0, max_value=5000.0, value=float(defaults["rtt_ms"]), step=10.0, key="rtt_control")
    rounds = st.sidebar.number_input("Simulation rounds", min_value=1, max_value=5000, value=int(defaults["rounds"]), step=10, key="rounds_control")
    initial_cwnd = st.sidebar.number_input("Initial cwnd (packets)", min_value=0.1, max_value=1000.0, value=float(defaults["initial_cwnd"]), step=1.0, key="cwnd_control")
    ssthresh = st.sidebar.number_input("Initial ssthresh", min_value=1.0, max_value=10000.0, value=float(defaults["initial_ssthresh"]), step=1.0, key="ssthresh_control")
    seed = st.sidebar.number_input("Random seed", min_value=0, max_value=2_147_483_647, value=int(defaults["seed"]), step=1, key="seed_control")
    return SimulationConfig(algorithm, loss, rtt, int(rounds), initial_cwnd, ssthresh, int(seed))


def cwnd_chart(df: pd.DataFrame, title: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["round"], y=df["cwnd_before"], mode="lines", name="cwnd"))
    if df["ssthresh_before"].notna().any():
        fig.add_trace(go.Scatter(x=df["round"], y=df["ssthresh_before"], mode="lines", name="ssthresh", line=dict(dash="dash")))
    loss_rows = df[df["loss_occurred"]]
    if not loss_rows.empty:
        fig.add_trace(go.Scatter(x=loss_rows["round"], y=loss_rows["cwnd_before"], mode="markers", name="loss event", marker=dict(size=9, symbol="x")))
    fig.update_layout(title=title, xaxis_title="Round / RTT", yaxis_title="Congestion window (packets)", hovermode="x unified", height=440)
    return fig


def comparison_chart(frames: dict[str, pd.DataFrame]):
    fig = go.Figure()
    for name, df in frames.items():
        fig.add_trace(go.Scatter(x=df["round"], y=df["cwnd_before"], mode="lines", name=name))
    fig.update_layout(title="Congestion-window evolution under identical conditions", xaxis_title="Round / RTT", yaxis_title="Congestion window (packets)", hovermode="x unified", height=500)
    return fig


def metrics_cards(metrics: dict):
    cols = st.columns(5)
    formatted = format_metrics(metrics)
    for col, (label, value) in zip(cols, formatted.items()):
        with col:
            st.markdown(f'<div class="metric-card"><div class="small-muted">{label}</div><strong>{value}</strong></div>', unsafe_allow_html=True)


def interpretation(metrics: dict, algorithm: str) -> str:
    loss = metrics["packet_loss_rate"] * 100
    throughput = metrics["throughput_packets_per_second"]
    if metrics["congestion_events"] == 0:
        return f"{algorithm} experienced no congestion events in this run, so its congestion window kept increasing according to its control rule. Throughput was {throughput:.2f} packets/s."
    recovery = metrics["recovery_time_ms"]
    recovery_text = "recovery could not be observed for all loss events" if recovery is None else f"average observed recovery time was {recovery:.1f} ms"
    return f"{algorithm} observed a {loss:.2f}% packet-loss rate with {metrics['congestion_events']} congestion events. The run achieved {throughput:.2f} packets/s; {recovery_text}."


def dashboard(config: SimulationConfig):
    st.title("Adaptive Congestion-Control Simulator and Performance Analyzer")
    st.write("A controlled, round-based Computer Networks simulation of TCP Tahoe, TCP Reno, and AIMD.")
    st.info("This is not a real TCP implementation. Each round represents one RTT; packet loss and congestion feedback are simulated locally so experiments are reproducible and fast.")
    st.subheader("Quick-start run")
    if st.button("Run current configuration", type="primary"):
        st.session_state["last_df"] = simulate(config)
        st.session_state["last_config"] = config.to_dict()
        st.session_state["last_algorithm"] = config.algorithm
    if "last_df" in st.session_state:
        df = st.session_state["last_df"]
        last_config = SimulationConfig.from_dict(st.session_state["last_config"])
        metrics = calculate_metrics(df, last_config.rtt_ms)
        metrics_cards(metrics)
        st.plotly_chart(cwnd_chart(df, f"{last_config.algorithm}: congestion window"), use_container_width=True)
        st.caption(interpretation(metrics, last_config.algorithm))
    else:
        st.subheader("What the simulator demonstrates")
        st.markdown("- **Slow start:** Tahoe and Reno grow rapidly below ssthresh.\n- **Congestion avoidance:** Tahoe and Reno increase by roughly one packet per successful RTT after ssthresh.\n- **Congestion feedback:** loss is represented by duplicate ACK or timeout feedback.\n- **AIMD:** increases linearly and halves cwnd after loss.\n- **Reproducibility:** the same seed and configuration produce the same experiment.")


def workspace(config: SimulationConfig):
    st.header("Simulation workspace")
    st.write("Inspect one algorithm round by round, including packet outcomes and congestion feedback.")
    c1, c2 = st.columns(2)
    with c1:
        run = st.button("Run simulation", type="primary")
    with c2:
        reset = st.button("Reset latest run")
    if reset:
        st.session_state.pop("workspace_df", None)
        st.rerun()
    if run:
        try:
            st.session_state["workspace_df"] = simulate(config)
            st.session_state["workspace_config"] = config.to_dict()
        except ValueError as exc:
            st.error(str(exc))
    if "workspace_df" not in st.session_state:
        st.warning("Configure the parameters in the sidebar and run the simulation.")
        return
    df = st.session_state["workspace_df"]
    cfg = SimulationConfig.from_dict(st.session_state["workspace_config"])
    metrics = calculate_metrics(df, cfg.rtt_ms)
    metrics_cards(metrics)
    st.plotly_chart(cwnd_chart(df, f"{cfg.algorithm}: cwnd, ssthresh and loss events"), use_container_width=True)
    st.subheader("Round-by-round results")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download round results CSV", dataframe_csv_bytes(df), "simulation_results.csv", "text/csv")
    st.download_button("Download experiment configuration JSON", json_bytes(cfg.to_dict()), "experiment_config.json", "application/json")


def comparison(config: SimulationConfig):
    st.header("Algorithm comparison")
    st.write("All three algorithms use the same loss probability, RTT, number of rounds, initial cwnd, ssthresh, and seed.")
    if st.button("Run side-by-side comparison", type="primary"):
        frames, summaries = compare_algorithms(config)
        st.session_state["comparison_frames"] = frames
        st.session_state["comparison_summaries"] = summaries
        st.session_state["comparison_config"] = config.to_dict()
    if "comparison_frames" not in st.session_state:
        st.info("Run the comparison to generate synchronized results.")
        return
    frames = st.session_state["comparison_frames"]
    summaries = st.session_state["comparison_summaries"]
    st.plotly_chart(comparison_chart(frames), use_container_width=True)
    summary_df = pd.DataFrame(summaries.values()).set_index("algorithm")
    summary_display = summary_df.copy()
    summary_display["throughput_packets_per_second"] = summary_display["throughput_packets_per_second"].round(2)
    summary_display["packet_loss_rate"] = (summary_display["packet_loss_rate"] * 100).round(2)
    summary_display["average_cwnd"] = summary_display["average_cwnd"].round(2)
    summary_display["recovery_time_ms"] = summary_display["recovery_time_ms"].round(1)
    summary_display = summary_display.rename(columns={"throughput_packets_per_second": "Throughput (pkt/s)", "packet_loss_rate": "Packet loss (%)", "average_cwnd": "Average cwnd", "congestion_events": "Congestion events", "recovery_time_ms": "Recovery time (ms)"})[["Throughput (pkt/s)", "Packet loss (%)", "Average cwnd", "Congestion events", "Recovery time (ms)"]]
    st.dataframe(summary_display, use_container_width=True)
    st.download_button("Download comparison CSV", dataframe_csv_bytes(summary_display.reset_index()), "comparison_summary.csv", "text/csv")
    st.subheader("Why the curves differ")
    st.markdown("**Tahoe** returns cwnd to 1 after either modeled congestion feedback type. **Reno** keeps a larger cwnd after a triple-duplicate-ACK event, so it normally recovers faster from a single isolated loss. **AIMD** has no slow-start phase in this simplified model: it adds one packet per successful round and halves cwnd after loss.")


def experiments(config: SimulationConfig):
    st.header("Network conditions and experiments")
    scenario = st.selectbox("Predefined scenario", list(SCENARIOS))
    scenario_cfg = apply_scenario(config, scenario)
    st.write(f"**Scenario parameters:** loss probability = {scenario_cfg.loss_probability:.2f}, RTT = {scenario_cfg.rtt_ms:.0f} ms")
    if st.button("Run scenario comparison", type="primary"):
        frames, summaries = compare_algorithms(scenario_cfg)
        st.session_state["scenario_frames"] = frames
        st.session_state["scenario_summaries"] = summaries
        st.session_state["scenario_name"] = scenario
    if "scenario_frames" not in st.session_state:
        return
    frames = st.session_state["scenario_frames"]
    summaries = st.session_state["scenario_summaries"]
    st.plotly_chart(comparison_chart(frames), use_container_width=True)
    table = pd.DataFrame(summaries.values())
    table["packet_loss_rate"] *= 100
    table = table.rename(columns={"algorithm": "Algorithm", "throughput_packets_per_second": "Throughput (pkt/s)", "packet_loss_rate": "Packet loss (%)", "average_cwnd": "Average cwnd", "congestion_events": "Congestion events", "recovery_time_ms": "Recovery time (ms)"})
    st.dataframe(table[["Algorithm", "Throughput (pkt/s)", "Packet loss (%)", "Average cwnd", "Congestion events", "Recovery time (ms)"]].round(2), use_container_width=True, hide_index=True)


def performance(config: SimulationConfig):
    st.header("Performance analysis")
    st.write("Metrics are calculated from packets sent, packets acknowledged, loss events, cwnd samples, RTT, and observed recovery rounds.")
    if st.button("Generate performance analysis", type="primary"):
        frames, summaries = compare_algorithms(config)
        st.session_state["performance_summaries"] = summaries
        st.session_state["performance_frames"] = frames
    if "performance_summaries" not in st.session_state:
        st.info("Generate the analysis to populate the metrics.")
        return
    summaries = st.session_state["performance_summaries"]
    table = pd.DataFrame(summaries.values())
    st.dataframe(table, use_container_width=True, hide_index=True)
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure([go.Bar(x=table["algorithm"], y=table["throughput_packets_per_second"])])
        fig.update_layout(title="Throughput", xaxis_title="Algorithm", yaxis_title="Packets/s")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = go.Figure([go.Bar(x=table["algorithm"], y=table["average_cwnd"])])
        fig.update_layout(title="Average congestion window", xaxis_title="Algorithm", yaxis_title="Packets")
        st.plotly_chart(fig, use_container_width=True)
    best = max(summaries.values(), key=lambda x: x["throughput_packets_per_second"])
    st.success(f"Automatic interpretation: under this exact experiment, {best['algorithm']} achieved the highest measured throughput at {best['throughput_packets_per_second']:.2f} packets/s. This is an experiment-specific result, not a universal ranking.")


def validation():
    st.header("Test and validation")
    st.write(
        "These checks validate simulator behaviour. They are separate from the "
        "simulated network experiments shown elsewhere in the app."
    )

    test_items = [
        ("Zero-loss determinism", "Same seed and configuration produce identical round results."),
        ("Simulation shape", "Simulation produces the expected number of rounds and columns."),
        ("100% loss handled", "The simulator handles complete packet loss without crashing."),
        ("Tahoe loss response", "Loss reduces ssthresh and resets cwnd to 1."),
        ("Reno fast recovery", "Triple duplicate ACK reduces cwnd to the new ssthresh."),
        ("Reno timeout", "Timeout resets cwnd to 1."),
        ("AIMD decrease", "Loss halves cwnd but never below 1."),
        ("Input validation", "Invalid probability, RTT, rounds, and cwnd values are rejected."),
    ]

    for name, desc in test_items:
        st.markdown(f"**{name}** — {desc}")

    if st.button("Run built-in validation", type="primary"):
        results = []

        try:
            # 1. Zero-loss determinism
            cfg = SimulationConfig(loss_probability=0.0, rounds=20, seed=7)
            a = simulate(cfg)
            b = simulate(cfg)
            results.append(("Zero-loss determinism", a.equals(b)))

            # 2. Simulation shape
            results.append((
                "Simulation shape",
                len(a) == 20
                and {"cwnd_before", "cwnd_after", "packets_lost"}.issubset(a.columns)
            ))

            # 3. 100% loss handled
            high = simulate(
                SimulationConfig(
                    loss_probability=1.0,
                    rounds=5,
                    seed=1
                )
            )
            results.append((
                "100% loss handled",
                high["packets_lost"].sum() > 0
            ))

            # 4. All algorithms can run
            for alg in ALGORITHMS:
                test_cfg = SimulationConfig(
                    algorithm=alg,
                    loss_probability=0.0,
                    rounds=5,
                    seed=3
                )
                frame = simulate(test_cfg)
                results.append((
                    f"{alg} zero-loss run",
                    len(frame) == 5
                ))

            # 5. Tahoe loss response
            tahoe_cfg = SimulationConfig(
                algorithm="TCP Tahoe",
                loss_probability=1.0,
                rounds=1,
                initial_cwnd=10.0,
                initial_ssthresh=16.0,
                seed=1
            )
            tahoe = simulate(tahoe_cfg)

            results.append((
                "Tahoe loss response",
                tahoe.iloc[0]["cwnd_after"] == 1
                and tahoe.iloc[0]["ssthresh_after"] == 5
            ))

            # Reno fast recovery
            from core.algorithms import create_controller

            reno_controller = create_controller(
                "TCP Reno",
                initial_cwnd=10.0,
                initial_ssthresh=16.0
            )
            reno_controller.on_loss("triple_duplicate_ack")

            results.append((
                "Reno fast recovery",
                reno_controller.cwnd == 5.0
                and reno_controller.ssthresh == 5.0
            ))

            # 6. Reno timeout
            reno_cfg = SimulationConfig(
                algorithm="TCP Reno",
                loss_probability=1.0,
                rounds=1,
                initial_cwnd=10.0,
                initial_ssthresh=16.0,
                seed=1
            )
            reno = simulate(reno_cfg)

            results.append((
                "Reno timeout",
                reno.iloc[0]["cwnd_after"] == 1
            ))

            # 7. AIMD decrease
            aimd_cfg = SimulationConfig(
                algorithm="AIMD",
                loss_probability=1.0,
                rounds=1,
                initial_cwnd=10.0,
                initial_ssthresh=16.0,
                seed=1
            )
            aimd = simulate(aimd_cfg)

            results.append((
                "AIMD decrease",
                aimd.iloc[0]["cwnd_after"] == 5
            ))

            # 8. Input validation
            input_validation_passed = True

            invalid_configs = [
                {"loss_probability": -0.1},
                {"loss_probability": 1.1},
                {"rtt_ms": 0},
                {"rounds": 0},
                {"initial_cwnd": 0},
            ]

            # 9. CSV export
            sample_df = pd.DataFrame({
                "round": [1, 2],
                "packets_lost": [0, 1],
            })
            csv_data = dataframe_csv_bytes(sample_df)
            csv_check = pd.read_csv(
                __import__("io").BytesIO(csv_data)
            )
            results.append((
                "CSV export",
                len(csv_check) == 2
                and list(csv_check.columns) == ["round", "packets_lost"]
                and csv_check["packets_lost"].tolist() == [0, 1]
            ))

            # 10. JSON export
            sample_config = {"algorithm": "TCP Reno", "seed": 42}
            json_data = json_bytes(sample_config)
            json_check = json.loads(json_data.decode("utf-8"))
            results.append((
                "JSON export",
                json_check == sample_config
            ))

            # 11. Export directory and file saving
            import tempfile

            with tempfile.TemporaryDirectory() as temp_dir:
                test_dir = Path(temp_dir) / "new_outputs"
                output_dir = ensure_output_dir(test_dir)

                csv_path = save_dataframe(
                    sample_df, "test.csv", output_dir
                )
                json_path = save_json(
                    sample_config, "test.json", output_dir
                )

                results.append((
                    "Export directory and file saving",
                    output_dir.is_dir()
                    and csv_path.is_file()
                    and json_path.is_file()
                    and pd.read_csv(csv_path).equals(sample_df)
                    and json.loads(
                        json_path.read_text(encoding="utf-8")
                    ) == sample_config
                ))

            for values in invalid_configs:
                try:
                    SimulationConfig(**values)
                    input_validation_passed = False
                    break
                except (ValueError, TypeError):
                    pass

            results.append((
                "Input validation",
                input_validation_passed
            ))

            # 12. Metrics calculation
            from core.metrics import calculate_metrics

            metric_df = pd.DataFrame({
                "round": [1, 2, 3],
                "cwnd_before": [4.0, 5.0, 2.0],
                "cwnd_after": [5.0, 2.0, 3.0],
                "packets_sent": [4, 5, 2],
                "packets_lost": [0, 1, 0],
                "packets_acked": [4, 4, 2],
                "loss_occurred": [False, True, False],
            })

            metrics = calculate_metrics(metric_df, 100.0)

            results.append((
                "Throughput calculation",
                abs(metrics["throughput_packets_per_second"] - 33.3333333333) < 0.001
            ))

            results.append((
                "Packet-loss rate calculation",
                abs(metrics["packet_loss_rate"] - (1 / 11)) < 0.000001
            ))

            results.append((
                "Average cwnd calculation",
                abs(metrics["average_cwnd"] - (11 / 3)) < 0.000001
            ))

            results.append((
                "Congestion event count",
                metrics["congestion_events"] == 1
            ))

            results.append((
                "Recovery time calculation",
                metrics["recovery_time_ms"] is None
            ))

            # 13. Empty-data metrics
            empty_metrics = calculate_metrics(pd.DataFrame(), 100.0)

            results.append((
                "Empty-data metrics",
                empty_metrics["throughput_packets_per_second"] == 0.0
                and empty_metrics["packet_loss_rate"] == 0.0
                and empty_metrics["average_cwnd"] == 0.0
                and empty_metrics["congestion_events"] == 0
                and empty_metrics["recovery_time_ms"] is None
            ))

        except Exception as exc:
            results.append(("Unexpected exception", False))
            st.error(
                f"Unexpected exception: {type(exc).__name__}: {exc}"
            )

        st.subheader("Validation results")

        for name, passed in results:
            if passed:
                st.success(f"PASS — {name}")
            else:
                st.error(f"FAIL — {name}")


def main():
    config = config_sidebar()
    st.sidebar.caption("All simulation controls are local; no external API or database is used.")
    page = st.sidebar.radio("Section", ["Dashboard", "Simulation workspace", "Algorithm comparison", "Network conditions", "Performance analysis", "Test and validation"])
    if page == "Dashboard": dashboard(config)
    elif page == "Simulation workspace": workspace(config)
    elif page == "Algorithm comparison": comparison(config)
    elif page == "Network conditions": experiments(config)
    elif page == "Performance analysis": performance(config)
    else: validation()


if __name__ == "__main__":
    main()
