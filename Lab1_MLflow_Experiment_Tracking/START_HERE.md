# Lab 1 — MLflow Experiment Tracking

This is a separate runnable package and report for Lab 1. Open only this lab's folder and notebook. Do not submit the combined four-lab archive. The package includes prerequisite dataset/model creation; you do not have to copy a SQLite registry from another lab. No measured result or screenshot is prefilled.

## Start here: Windows / Docker route

1. Extract `Lab1_MLflow_Experiment_Tracking.zip` into its own folder.
2. Open the extracted `Lab1_MLflow_Experiment_Tracking` folder. Type `powershell` into File Explorer's address bar and press Enter.
3. Start Docker Desktop and wait for its engine. If it remains stuck on Starting, resolve the WSL startup issue first. Check these commands:

```text
python --version
docker info
docker compose version
```

4. Set your name:

```powershell
$env:LAB_AUTHOR="Sai YourFullName"
```

5. Initialize this lab once, then run the lab experiments:

```text
python labctl.py init
python labctl.py lab1
```

This is the Lab 1 execution itself; do not run it twice merely because the detailed section repeats the command.

This lab uses Docker project `cartvista-lab1` and volume `cartvista_lab1_project`. Other labs use different volumes. Run one lab stack at a time because browser ports are shared. Run `python labctl.py stop` in the previous lab folder before starting another. Stopping preserves results. Do not add `-v` to Compose down unless you intend to delete data.

The detailed exercise commands follow. They run from this same folder.

## 3 Lab 1 Experiment tracking and registry

### 3.1 Execute all training and exercises

```text
python labctl.py lab1
```

The runner performs these steps:

1. Generates the exact 5,000-customer synthetic data from the brief with seed 42.
2. Trains the untracked baseline and prints AUC, accuracy and the always-no-churn baseline.
3. Trains the six required candidates: logistic regression C 0.1/1/10 and RF 50/4, 200/8, 400/12 trees/depth.
4. Logs model type, applicable hyperparameters, fingerprint, split details, AUC, accuracy, F1, precision, recall, author and purpose; saves each model with its schema.
5. Registers the best finished run on the current full dataset and sets `champion`.
6. Loads it through the registry and scores five customers.
7. Adds both gradient boosting challengers, then registers the best again, recording another version even if the winning weights do not change.
8. Removes exactly one data row, logs a comparison run, records both fingerprints, and restores the original bytes even if the run fails.
9. Runs sklearn autologging in a separate process and scores the final champion.

Repeated execution intentionally adds new runs. Start with a clean project for a simple screenshot. The altered-data run is excluded from automatic champion selection by its fingerprint. Autolog runs lack the manual comparison metric and fingerprint, so they are also excluded.

### 3.2 Open MLflow and collect evidence

```text
docker compose up -d mlflow
```

Open **http://localhost:5000**. Select `cartvista-churn`.

- Sort the table by `test_auc` descending. Show the parameter and precision/recall columns. Screenshot the table.
- Select the six main candidates and click Compare. Inspect the model-kind, depth, AUC and other metrics.
- Open an individual run → Artifacts → model to see `MLmodel`, the model file and environment information.
- Filter using `tags.author = 'Sai YourFullName'` (use the actual author value you set).
- Open Models → `cartvista-churn`. Screenshot the versions and `champion` alias after the gradient boosting runs.
- Open the E4 run and compare `data_fingerprint` with a full-data run. A fingerprint identifies data content, not the person or laptop; identical source CSV bytes legitimately yield identical fingerprints.
- Open the autolog run and compare its logged metadata with the manual run.

Capture the consumer again if you need a clean terminal output:

```text
docker compose run --rm tools python consume_model.py
python labctl.py collect
```

Look in `my_results/evidence/lab1_consume.json` and `lab1_fingerprints.json`. Use the actual winner and actual AUC in your report. The brief's example rates, model rankings and scores are illustrative: logistic regression can win because the data was generated from a logistic function. Never change a result to imitate the sample.

### 3.3 Complete your written section

Use the Lab 1 answers in `WRITTEN_ANSWERS.md`. Add your own winning run ID, metrics, model choice and explanation of the observed recall/precision trade-off. The scripts use the same held-out split for lab comparison; repeated model selection on that split makes it a validation set in practice, not an untouched final performance estimate.


## Complete this lab's separate submission

1. Run `python labctl.py collect` to copy generated evidence into `my_results`.
2. Open this folder's `SUBMISSION_TEMPLATE.html`. It contains ONLY Lab 1 sections. Fill your name, ID and actual observations; add your screenshots using the image controls.
3. Read `WRITTEN_ANSWERS.md` for this lab's explanations. Adapt them to your measured outputs; do not invent values or successful UI runs.
4. Print the completed template to PDF as `Lab1_YourStudentID_Report.pdf` before closing the browser. Browser edits are not automatically saved to the HTML file.
5. Submit that PDF and the requested code/evidence for Lab 1 in its own portal entry. The starter ZIP is source material, not an executed submission. The course portal's required format takes precedence.
6. Use `python labctl.py stop` before starting another lab. Keep `my_results` and your PDF.

## Colab route for this lab

Upload `Lab1_Colab.ipynb` to Google Colab. In its first upload cell choose this lab's ZIP. Set your name, then run cells in order on a CPU runtime. Each notebook performs its own prerequisite training. Save the executed notebook and download its evidence ZIP before disconnecting.

Lab 1 Python experiments and registry can run in Colab. If its MLflow UI proxy fails, capture UI evidence using the local route.

## What is included

- This lab's instructions, written answers, notebook and editable report template.
- The required source scripts and infrastructure configuration.
- Shared model-generation scripts copied into this package so it can run independently.
- `VALIDATION.md`: checks performed and remaining execution requirements.

