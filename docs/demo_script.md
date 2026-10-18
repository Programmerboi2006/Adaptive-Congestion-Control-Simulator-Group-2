# Five-Minute Live Demonstration Script

## 0:00–0:40 — Introduce the problem

“TCP congestion control prevents a sender from overwhelming the network. Our project simulates how Tahoe, Reno, and AIMD change their congestion windows when packets are acknowledged or lost. It is a controlled round-based simulation, not real TCP traffic.”

## 0:40–1:30 — Show the Dashboard

Use the default Reno configuration. Explain `cwnd`, `ssthresh`, packet-loss probability, RTT, rounds, and random seed. Run the simulation and point out the cwnd curve and loss markers.

## 1:30–2:30 — Demonstrate congestion behaviour

Open Simulation Workspace. Increase loss probability to about 0.10 and run. Show a loss event. Explain that one lost packet is modeled as triple-duplicate-ACK feedback and two or more losses as a timeout. Point out that Tahoe resets cwnd to 1, while Reno can keep a larger cwnd after a triple-duplicate-ACK event.

## 2:30–3:30 — Compare algorithms

Open Algorithm Comparison and run the same conditions for all three algorithms. Explain that the same seed and network parameters are used, so differences come from the congestion-control rules.

## 3:30–4:20 — Show a predefined experiment

Open Network Conditions and select “High RTT + packet loss”. Run the scenario. Explain that RTT affects elapsed time and throughput calculations, while packet loss causes congestion responses.

## 4:20–5:00 — Validation and export

Open Test and Validation and run built-in checks. Then show the CSV and JSON download buttons. Finish by stating that the experiment is reproducible using the saved configuration and seed.
