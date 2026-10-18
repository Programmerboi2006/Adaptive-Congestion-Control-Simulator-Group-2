# Test Report

## Automated test execution

Run:

```bash
pytest -q
```

Record the actual output here after running the tests on the target machine:

```text
PASTE ACTUAL PYTEST OUTPUT HERE
```

## Manual application checks

| Test | Expected result | Actual result | Status |
|---|---|---|---|
| Dashboard opens | Interface loads without error |  |  |
| Zero-loss experiment | No loss events |  |  |
| High-loss experiment | Loss events appear and cwnd reacts |  |  |
| Tahoe comparison | Tahoe curve and metrics are displayed |  |  |
| Reno comparison | Reno curve and metrics are displayed |  |  |
| AIMD comparison | AIMD curve and metrics are displayed |  |  |
| CSV download | Valid CSV downloads |  |  |
| JSON download | Valid configuration downloads |  |  |
| Fixed seed | Repeated run is identical |  |  |
| Invalid input | Validation prevents invalid simulation |  |  |
