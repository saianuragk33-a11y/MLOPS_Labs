# Lab 2 validation

Repackaged from the previously supplied solution. The split package was checked for Python/notebook syntax, local script dependencies, Compose service/volume isolation and ZIP extraction integrity. Full Docker/Airflow/Grafana execution has not been rerun here. You must execute the lab and capture your own results.

Original combined-project verification record (context, not new test results):

# Validation of this solution package

Executed in a fresh Python 3.12 environment with the supplied ML requirements. These are developer verification results, not the student's submission evidence.

## Executed successfully

- Generated the exact 5,000-row Lab 1 synthetic dataset; untracked training; six primary candidates; gradient boosting challengers; manual tracking of all metrics/parameters/tags; model artifacts and schemas; model registration and alias loading.
- One-row fingerprint experiment and restoration of original data; sklearn autolog training.
- Exported champion and scored 5,000 rows with both MLflow and joblib. Also executed the final minimal CSV/NumPy scorer in a separate environment with no pandas or MLflow installed. Labels were exactly equal and probabilities matched numerically.
- Five automated tests passed: PSI edge cases; service/batch/validation; degraded startup and HTTP 503; monitoring metrics/window; shadow routing with both models evaluated.
- Started actual Uvicorn HTTP processes and ran valid/invalid API probes, 300-request latency measurement and 3×100-customer batch comparison.
- Moved the champion alias while the HTTP process was running; confirmed unchanged loaded metadata until restart, then confirmed the newly loaded version.
- Tested current-cycle candidate validation at a passing 0.72 threshold and a failing 0.95 threshold, with the champion unchanged by failure.
- Sent normal/drift requests to the monitored HTTP service and checked exported metrics; ran the numerical PSI script.
- Sent 300 A/B HTTP requests: both variants received traffic. Sent 30 shadow requests: only champion answered.
- Parsed YAML and dashboard/alert JSON; compiled notebook code cells and Python source, including the DAG.

## Observed results in this developer run

These demonstrate that the paths executed; do not copy these values as your results. Logistics, random A/B assignment and timing depend on the execution.

- Best full-data candidate was logistic regression with AUC approximately 0.7496; the brief's claim that RF must win was not true for the supplied generator in this run.
- AUC gate 0.72 passed; deliberately impossible 0.95 gate failed.
- Normal PSI: tenure 0.0238, support tickets 0.0043, monthly spend 0.0115.
- Drift PSI: tenure 6.8942, support tickets 3.1437, monthly spend 4.7926, using this package's documented smoothing/binning.
- The A/B request allocation in one 300-request test was 265 champion / 35 challenger, consistent with randomized approximately 90/10 routing.

## Not executed in this workspace

Docker CLI/daemon was unavailable. Docker image builds, actual image sizes, Airflow import/scheduler execution inside its container, the optional Docker-socket scoring task, Prometheus scraping and Grafana dashboard/alert runtime behavior have not been end-to-end verified here. Configurations and complete execution/check instructions are supplied; verify them locally and capture actual screenshots. The lean-image <450 MB target remains a measured local acceptance condition, not a verified claim.

The Colab notebook's cells were syntax-checked and its underlying Python scripts were executed here. A hosted Google Colab session and its browser port proxy were not available for verification. All-Docker execution uses Python 3.11; local executable verification used Python 3.12. The dependencies selected provide both versions' wheels, but the Docker build itself remains a local check.

## Re-run optional automated checks

After Lab 1 and create_challenger.py in a local activated environment:

```text
python -m pip install pytest==8.2.2
python -m pytest tests -q
```

Use START_HERE.md to validate the actual required containers, UIs and submission evidence. No model database, developer run IDs or developer screenshots are shipped as student evidence.
