# Presentation Outline

1. **Title slide** — Adaptive Congestion-Control Simulator and Performance Analyzer.
2. **Problem statement** — congestion control is necessary because packet loss and limited capacity require senders to adapt transmission rate.
3. **Objectives** — simulate Tahoe, Reno, AIMD; compare performance; visualize cwnd; provide reproducible experiments.
4. **Background** — cwnd, ssthresh, RTT, ACKs, slow start, congestion avoidance, loss feedback.
5. **Algorithms** — Tahoe, Reno, AIMD and their differences.
6. **Architecture** — Streamlit UI → simulation controller → event model + algorithm modules → metrics → visualization/export.
7. **Experiment design** — packet loss is probabilistic, rounds represent RTT, seed controls reproducibility.
8. **Results** — cwnd graphs and metric comparison from actual runs.
9. **Validation** — automated tests and edge-case checks.
10. **Limitations** — no real sockets, no retransmission timers, no TCP headers, no bandwidth queue, no advanced TCP variants.
11. **Conclusion** — controlled simulation makes congestion-control behaviour observable and comparable.
