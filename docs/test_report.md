# Test Report — Executed Build

## Automated test execution

Command executed in the build environment:

```text
python -m pytest -q
```

Actual result:

```text
17 passed in 0.09s
```

The core modules also passed Python bytecode compilation with `compileall`.

## Application smoke-test status

The Streamlit package was not installed in the build environment, so the browser UI could not be launched here. The `app.py` file was syntax-compiled successfully. The target Windows/macOS machine should install the pinned dependencies from `requirements.txt` and then perform the manual UI checks below.

## Manual application checks

| Test | Expected result | Actual result | Status |
|---|---|---|---|
| Dashboard opens | Interface loads without error | Not executed in build environment | Pending target-machine check |
| Zero-loss experiment | No loss events | Core simulation test passed | Pass |
| High-loss experiment | Loss events appear and cwnd reacts | Core simulation test passed | Pass |
| Tahoe comparison | Tahoe curve and metrics are displayed | UI not launched | Pending target-machine check |
| Reno comparison | Reno curve and metrics are displayed | UI not launched | Pending target-machine check |
| AIMD comparison | AIMD curve and metrics are displayed | UI not launched | Pending target-machine check |
| CSV download | Valid CSV downloads | Export functions compiled; browser download not exercised | Pending target-machine check |
| JSON download | Valid configuration downloads | Export functions compiled; browser download not exercised | Pending target-machine check |
| Fixed seed | Repeated run is identical | Automated test passed | Pass |
| Invalid input | Validation rejects invalid values | Automated validation tests passed | Pass |
