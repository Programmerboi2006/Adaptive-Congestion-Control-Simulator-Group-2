# Adaptive Congestion-Control Simulator and Performance Analyzer

## Overview
A Python-based application that simulates and compares TCP Tahoe, TCP Reno, and AIMD congestion-control algorithms under different network conditions.

The application visualizes congestion-window behavior and evaluates performance using metrics such as throughput, packet loss rate, average congestion window, congestion events, and estimated recovery time.

## Features
- Simulates TCP Tahoe, TCP Reno, and AIMD.
- Configurable network conditions.
- Visualizes congestion-window behavior.
- Compares algorithm performance.
- Calculates performance metrics.
- Exports simulation results as CSV and JSON.
- Includes validation checks and automated tests.

## Technologies Used
- Python
- Streamlit
- Pandas
- Plotly
- Pytest

## Installation

1. Install Python.
2. Clone or download this repository.
3. Open a terminal in the project directory.
4. Install dependencies:

   `pip install -r requirements.txt`

## Run the Application

`python -m streamlit run app.py`

## Run Tests

`python -m pytest`

## Project Structure

- `app.py` — Application entry point.
- `core/` — Simulation algorithms, configuration, metrics, experiments, and export functionality.
- `ui/` — User-interface components.
- `tests/` — Automated tests.
- `docs/` — Project documentation.
- `requirements.txt` — Python dependencies.

## Limitations
This project is a simplified software simulation. It does not transmit real TCP packets or implement a complete TCP networking stack. Some loss classification and recovery measurements are heuristic approximations.