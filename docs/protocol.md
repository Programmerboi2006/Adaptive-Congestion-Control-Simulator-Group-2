# Simulated Protocol and Message Format

This project does **not** send real network packets. The following logical records represent the information that a real transport protocol would reason about.

## Sender state

- `cwnd`: number of packets the sender is permitted to have in flight for the modeled round.
- `ssthresh`: threshold separating slow start from congestion avoidance for Tahoe and Reno.
- `RTT`: assumed round-trip delay for one simulation round.

## Data packet model

Each modeled packet has no payload or socket address. It is represented only by its position in the current round and by whether the network-event model marks it as lost.

## ACK model

A successful packet contributes one acknowledgement. For the simplified congestion-feedback model:

- exactly one lost packet in a round → `triple_duplicate_ack`
- two or more lost packets → `timeout`
- no lost packets → normal ACK feedback and a congestion-window increase

This abstraction is intentionally simpler than a production TCP implementation.

## Round record

Each output row contains:

`round, cwnd_before, ssthresh_before, packets_sent, packets_lost, packets_acked, loss_occurred, feedback, cwnd_after, ssthresh_after, time_ms`

The record is sufficient to reconstruct the experiment and calculate the displayed metrics.
