# Adaptive Congestion-Control Simulator and Performance Analyzer

A Python + Streamlit Computer Networks mini-project that models TCP Tahoe, TCP Reno, and AIMD in a controlled, reproducible round-based simulation.

## Features

- TCP Tahoe, TCP Reno, and AIMD congestion-control models.
- Configurable packet-loss probability, RTT, rounds, initial cwnd, ssthresh, and random seed.
- Dashboard and single-algorithm workspace.
- Side-by-side algorithm comparison under identical conditions.
- Predefined network scenarios.
- Throughput, packet-loss rate, average cwnd, congestion-event count, and observed recovery time.
- CSV result export and JSON configuration export, with saved JSON configurations loadable through the sidebar.
- Built-in validation page and pytest suite.
- Windows/macOS compatible; no database, Docker, cloud service, external API, or real network traffic.

## Folder structure

```text
Adaptive-Congestion-Control-Simulator/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── algorithms.py
│   ├── config.py
│   ├── experiments.py
│   ├── export.py
│   ├── metrics.py
│   └── simulation.py
├── ui/
│   └── __init__.py
├── tests/
│   ├── test_algorithms.py
│   ├── test_simulation.py
│   └── test_validation.py
├── docs/
│   ├── architecture.md
│   ├── contribution_division.md
│   ├── demo_script.md
│   ├── presentation_outline.md
│   ├── protocol.md
│   ├── test_report_template.md
│   └── viva_questions.md
└── outputs/
```

## Simulation model

Each simulation round represents one RTT. The current cwnd determines how many modeled packets are sent. Every packet independently has the configured probability of being lost. Successful packets are treated as acknowledgements.

Feedback is intentionally simplified:

- no loss → normal ACK feedback;
- exactly one lost packet → triple duplicate ACK feedback;
- two or more lost packets → timeout feedback.

Tahoe and Reno use slow start below ssthresh and additive congestion avoidance at or above ssthresh. Tahoe resets cwnd to 1 after either modeled loss feedback. Reno resets to 1 after timeout but keeps cwnd at the new ssthresh after triple duplicate ACK. AIMD starts without a slow-start phase, increases cwnd by one after a successful round, and halves cwnd after loss.

This is a teaching model, not a complete TCP implementation. It does not implement real sockets, sequence numbers, retransmission timers, advertised receiver windows, TCP headers, packet queues, bandwidth constraints, or advanced TCP variants.

## Windows setup

1. Install Python 3.11–3.13 from the official Python distribution. During installation on Windows, enable “Add Python to PATH” if available.
2. Open PowerShell in the project folder.
3. Create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If `py` is unavailable but `python` works:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. Run tests:

```powershell
python -m pytest -q
```

6. Start the application:

```powershell
python -m streamlit run app.py
```

The browser should open automatically. If it does not, use the local URL shown by Streamlit.

## macOS setup

1. Install Python 3.11–3.13 from the official Python distribution or verify an existing installation:

```bash
python3 --version
```

2. Open Terminal and enter the project folder.
3. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. Run tests:

```bash
python -m pytest -q
```

6. Start the application:

```bash
python -m streamlit run app.py
```

## Offline use

After dependencies have been installed, the application itself does not need internet access. Streamlit runs locally and all simulation data is generated locally.

## Export

The interface offers direct browser downloads for CSV results and JSON configurations. A downloaded JSON configuration can be uploaded again from the sidebar and applied to restore the experiment controls. The `outputs/` directory is included so future code can save local files without assuming a pre-existing directory; it is created automatically when needed.

## Testing

The pytest suite checks algorithm responses, deterministic seeds, zero-loss and full-loss cases, output structure, sequential rounds, and invalid configuration values. Do not copy a test result into a report until the tests have actually been run on the demonstration machine.

## Five-minute demonstration

Use `docs/demo_script.md`.

## Academic documentation

- `docs/architecture.md` — system architecture and Mermaid diagram.
- `docs/protocol.md` — simulated packet/ACK and round record design.
- `docs/presentation_outline.md` — presentation structure.
- `docs/viva_questions.md` — concise viva preparation.
- `docs/contribution_division.md` — suggested four-member work split.
- `docs/test_report_template.md` — test-report template that intentionally leaves actual results blank until execution.

## Troubleshooting

**`python` or `python3` not found:** install Python and reopen the terminal.

**PowerShell blocks activation:** use the alternative command below and run Python through the environment directly, or change the PowerShell execution policy only if permitted by the machine administrator:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**Port already in use:** start Streamlit on another local port:

```bash
python -m streamlit run app.py --server.port 8502
```

**Blank or broken page:** stop Streamlit with Ctrl+C, reactivate the virtual environment, and rerun the command.

## ZIP transfer checklist

Do not include `.venv`, caches, `.pytest_cache`, or `__pycache__`. The project can be zipped directly from the folder after these generated directories are removed. The supplied project `.gitignore` excludes them if Git is used.
