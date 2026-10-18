# Individual Viva Questions and Concise Answers

1. **What is congestion control?** — A transport-layer mechanism that limits the sender's rate to reduce network overload and packet loss.
2. **What is cwnd?** — The congestion window limits the amount of unacknowledged data the sender can have in flight.
3. **What is ssthresh?** — The threshold used by Tahoe and Reno to switch from slow start to congestion avoidance.
4. **What is slow start?** — In this model, cwnd approximately doubles after each successful RTT while below ssthresh.
5. **What is congestion avoidance?** — In this model, cwnd increases by one packet per successful RTT.
6. **How does Tahoe react to loss?** — It sets ssthresh to half the current cwnd and resets cwnd to 1.
7. **How does Reno differ?** — For a modeled triple-duplicate-ACK event, Reno sets ssthresh to half cwnd and keeps cwnd at that new ssthresh instead of resetting to 1.
8. **What is AIMD?** — Additive Increase, Multiplicative Decrease: increase by one on success and halve cwnd after loss.
9. **Why is Reno often faster after a single loss?** — Its fast-recovery behaviour keeps a larger congestion window in this simplified model.
10. **What is RTT?** — Round-trip time between sending data and receiving corresponding feedback.
11. **How is throughput calculated?** — Successful packets divided by total simulated time.
12. **How is packet-loss rate calculated?** — Lost packets divided by packets sent.
13. **Why use a random seed?** — It makes the same probabilistic experiment reproducible.
14. **Is this real TCP?** — No. It is a discrete, round-based model of congestion-control behaviour.
15. **Why not use real sockets?** — The project is designed for safe, deterministic, offline demonstrations rather than actual network traffic.
16. **Why can recovery time be N/A?** — If cwnd does not return to the pre-loss level before the experiment ends, recovery was not observed.
17. **What causes a timeout in this model?** — Two or more lost packets in the same round are mapped to timeout feedback.
18. **Why can results differ between algorithms with identical seeds?** — The random loss sequence is the same, but different cwnd values cause different numbers of packets to be exposed to the loss model in later rounds.
